"""Minimal public demo API for the propensity model, served on Cloud Run.

Not the recommended production architecture (see Documentacion_Solucion.pdf's
Vertex AI batch-scoring design) - this is a lightweight live endpoint for
demoing the trained pipeline in an interview, nothing more.
"""
import json
import pickle
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, create_model

HERE = Path(__file__).parent
with open(HERE / "model.pkl", "rb") as f:
    MODEL = pickle.load(f)
with open(HERE / "schema.json", encoding="utf-8") as f:
    SCHEMA = json.load(f)

FEATURE_COLS = SCHEMA["feature_cols"]
EXAMPLE = SCHEMA["example"]

# Build a pydantic model from the schema so FastAPI validates the request body
# and generates /docs automatically, instead of hand-typing 17 fields.
_fields = {c: ((str if c in SCHEMA["cat_cols"] else int if c in SCHEMA["bin_cols"] else float),
               EXAMPLE[c]) for c in FEATURE_COLS}
Visita = create_model("Visita", **_fields)

app = FastAPI(title="Ferreycorp - Propension de Compra (demo)",
              description="Endpoint publico de demo. No es la arquitectura de produccion "
                           "recomendada (ver documentacion: batch scoring en Vertex AI).")


@app.get("/")
def root():
    return {"status": "ok", "model": "RandomForest propension de compra", "fields": FEATURE_COLS}


@app.get("/example")
def example():
    return EXAMPLE


@app.post("/predict")
def predict(visita: Visita):
    row = visita.model_dump()
    missing = [c for c in FEATURE_COLS if c not in row]
    if missing:
        raise HTTPException(400, f"faltan campos: {missing}")
    X = pd.DataFrame([{c: row[c] for c in FEATURE_COLS}])
    proba = float(MODEL.predict_proba(X)[0, 1])
    return {"propension_compra": round(proba, 4), "prediccion": int(proba >= 0.5)}
