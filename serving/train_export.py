"""Re-fits the final tuned pipeline (same feature engineering + hyperparameters
as the notebook) on the full dataset and pickles it for serving.

Not re-running RandomizedSearchCV: the winning hyperparameters are already known
(n_estimators=400, max_depth=None, min_samples_leaf=2, max_features=None) from
the notebook's search. Fitting on the full dataset (not just the 70% train split)
because this is for deployment, not evaluation - more data, better model.
"""
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = "../Dataset/compras_data.csv"
df = pd.read_csv(DATA_PATH).drop(columns=["tamanio_ciudad"])
df = df.sort_values(["id", "dia_visita"]).reset_index(drop=True)

g = df.groupby("id")
df["n_visita"] = g.cumcount() + 1
df["dias_desde_ultima_visita"] = g["dia_visita"].diff()
df["dias_desde_ultima_visita"] = df["dias_desde_ultima_visita"].fillna(
    df["dias_desde_ultima_visita"].median())
tasa_compra_global = df["incidencia_compra"].mean()
df["tasa_compra_historica"] = g["incidencia_compra"].transform(
    lambda s: s.shift(1).expanding().mean())
df["tasa_compra_historica"] = df["tasa_compra_historica"].fillna(tasa_compra_global)

price_cols = [f"precio_marca_{i}" for i in range(1, 6)]
promo_cols = [f"promo_marca_{i}" for i in range(1, 6)]
df["precio_min"] = df[price_cols].min(axis=1)
df["precio_max"] = df[price_cols].max(axis=1)
df["precio_promedio"] = df[price_cols].mean(axis=1)
df["alguna_promo_activa"] = df[promo_cols].max(axis=1).astype(int)

price_matrix = df[price_cols].to_numpy()
promo_matrix = df[promo_cols].to_numpy()
marca_idx = df["ultima_marca_comprada"].astype(int).to_numpy()
has_history = marca_idx > 0
col_idx = np.clip(marca_idx - 1, 0, 4)
df["precio_ultima_marca"] = np.where(has_history, price_matrix[np.arange(len(df)), col_idx], np.nan)
df["gap_precio_vs_min"] = (df["precio_ultima_marca"] - df["precio_min"]).fillna(0)
df["promo_ultima_marca"] = np.where(has_history, promo_matrix[np.arange(len(df)), col_idx], 0).astype(int)
df["tiene_historial_marca"] = has_history.astype(int)

cust = df.groupby("id").agg(
    n_visitas=("dia_visita", "count"),
    tasa_compra=("incidencia_compra", "mean"),
    cantidad_media=("cantidad", lambda s: s[s > 0].mean() if (s > 0).any() else 0),
    edad=("edad", "first"),
    ingreso_anual=("ingreso_anual", "first"),
).reset_index()
sensibilidad = df.loc[df["alguna_promo_activa"] == 1].groupby("id")["incidencia_compra"].mean()
cust["sensibilidad_promo"] = cust["id"].map(sensibilidad).fillna(0)

feat_cols_cluster = ["n_visitas", "tasa_compra", "cantidad_media", "edad", "ingreso_anual", "sensibilidad_promo"]
scaler_cluster = StandardScaler().fit(cust[feat_cols_cluster])
X_cl = scaler_cluster.transform(cust[feat_cols_cluster])
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X_cl)
cust["segmento"] = kmeans.labels_.astype(str)
df = df.merge(cust[["id", "segmento"]], on="id", how="left")

target = "incidencia_compra"
cat_cols = ["genero", "estado_civil", "nivel_educacion", "ocupacion", "segmento"]
num_cols = ["edad", "ingreso_anual", "n_visita", "dias_desde_ultima_visita",
            "tasa_compra_historica", "precio_min", "precio_max", "precio_promedio",
            "gap_precio_vs_min"]
bin_cols = ["alguna_promo_activa", "promo_ultima_marca", "tiene_historial_marca"]
feature_cols = cat_cols + num_cols + bin_cols

X, y = df[feature_cols], df[target]
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ("num", StandardScaler(), num_cols),
], remainder="passthrough")
clf = RandomForestClassifier(n_estimators=400, max_depth=None, min_samples_leaf=2,
                              max_features=None, class_weight="balanced", random_state=42, n_jobs=-1)
pipe = Pipeline([("pre", preprocessor), ("clf", clf)]).fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump(pipe, f)

schema = {
    "feature_cols": feature_cols, "cat_cols": cat_cols, "num_cols": num_cols,
    "bin_cols": bin_cols, "n_segmentos": 4,
    "example": {c: (str(X[c].mode()[0]) if c in cat_cols
                     else int(X[c].mode()[0]) if c in bin_cols
                     else round(float(X[c].median()), 2))
                for c in feature_cols},
}
with open("schema.json", "w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

print("model.pkl + schema.json written. train AUC sanity check:")
from sklearn.metrics import roc_auc_score
print(roc_auc_score(y, pipe.predict_proba(X)[:, 1]))
