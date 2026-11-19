# Ferreycorp - Modelo de Propensión de Compra

Prueba técnica de Data Science: modelo de propensión de compra por cliente a partir
de datos de visitas y comportamiento, con clusterización de clientes, modelado
supervisado y traducción de resultados a valor de negocio.

## Entregables

| Archivo | Contenido |
|---|---|
| `FERREYCORP_Propension_Compra.ipynb` | Notebook completo: EDA, feature engineering, clustering, modelado, tuning, SHAP y captura de valor |
| `Codigo_Solucion.txt` | Exportación en texto plano del notebook (código + markdown) |
| `Documentacion_Solucion.pdf` | Documentación de la solución: objetivo, arquitectura, metodología, resultados, impacto de negocio, despliegue y arquitectura de producción propuesta |
| `Slides_Ferreycorp.pdf` | Presentación ejecutiva (7 slides) |
| `serving/` | API de scoring (FastAPI) usada para el despliegue demo |
| `infra/` | Infraestructura como código (Terraform) del despliegue demo en Cloud Run |
| `assets/` | Imágenes de resultados embebidas en la documentación |
| `Dataset/` | Dataset original provisto para la prueba |

## Cómo ejecutar el notebook

1. Crear y activar un entorno virtual (Python 3.12 recomendado):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Registrar el kernel de Jupyter (una sola vez):

   ```bash
   python -m ipykernel install --user --name ferreycorp --display-name "Python (ferreycorp)"
   ```

4. Abrir y ejecutar `FERREYCORP_Propension_Compra.ipynb` de principio a fin
   (Jupyter Notebook, JupyterLab o VS Code), seleccionando el kernel `ferreycorp`.
   El notebook asume que `Dataset/` está en la misma carpeta que el notebook.

## Demo en vivo

El modelo entrenado está desplegado como API pública en Cloud Run. Los detalles,
ejemplos de consulta (`curl`) y el diseño de una arquitectura de producción con
Vertex AI están documentados en la sección 6 y 7 de `Documentacion_Solucion.pdf`.
El código de esa API está en `serving/` y la infraestructura que lo despliega en
`infra/` (Terraform).
