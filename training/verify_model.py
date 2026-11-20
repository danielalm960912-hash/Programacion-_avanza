"""Verifica que el modelo guardado carga y predice igual que al entrenarlo.

Simula lo que hará la app: recibe los datos de un estudiante con sus valores
originales (como vendrían del formulario), aplica las transformaciones
guardadas en metadata.json y le pide la predicción al modelo.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODELS_DIR = Path("models")

meta = json.loads((MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))
modelo = joblib.load(MODELS_DIR / meta["modelo"]["archivo"])
print(f"modelo cargado: {meta['modelo']['archivo']} | RMSE de prueba: {meta['metricas']['rmse_prueba']}")

T = meta["transformaciones"]
COLUMNAS = meta["entradas"]["columnas"]
NUMERICAS = meta["entradas"]["numericas"]


def preparar(entradas: dict) -> pd.DataFrame:
    """Convierte los datos de un estudiante en la fila que espera el modelo."""
    fila = pd.DataFrame([entradas], columns=COLUMNAS)

    # transformaciones previas, con las mismas reglas del entrenamiento
    fila["fami_cuartoshogar"] = fila["fami_cuartoshogar"].map(T["cuartos"])
    fila["fami_personashogar"] = fila["fami_personashogar"].map(T["personas"])
    for col, valores in T["a_faltante"].items():
        fila[col] = fila[col].replace(valores, np.nan)

    # mismos tipos de dato que en el entrenamiento: números y texto ("str" de pandas 3)
    for col in COLUMNAS:
        if col in NUMERICAS:
            fila[col] = pd.to_numeric(fila[col], errors="coerce")
        else:
            fila[col] = fila[col].astype("str")

    minimo, maximo = T["edad_rango_valido"]
    fila["edad"] = fila["edad"].where(fila["edad"].between(minimo, maximo))
    return fila


todo_bien = True
for n, ejemplo in enumerate(meta["ejemplos"], start=1):
    predicho = float(modelo.predict(preparar(ejemplo["entradas"]))[0])
    esperado = ejemplo["puntaje_predicho"]
    coincide = abs(predicho - esperado) < 0.01
    todo_bien = todo_bien and coincide
    print(f"ejemplo {n}: real {ejemplo['puntaje_real']:.0f} | "
          f"guardado {esperado:.2f} | ahora {predicho:.2f} | {'OK' if coincide else 'DIFERENTE'}")

print("✅ El modelo guardado predice igual que al entrenarlo." if todo_bien
      else "❌ Hay diferencias: revisar las transformaciones.")