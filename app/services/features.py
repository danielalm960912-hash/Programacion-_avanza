"""Capa de negocio: valida y prepara los datos de un estudiante para el modelo.

Aplica exactamente las mismas reglas que se usaron al entrenar, leyéndolas
del metadata.json (una sola fuente de verdad).
"""

import numpy as np
import pandas as pd


def validar_entradas(entradas: dict, meta: dict) -> list[str]:
    """Revisa los datos recibidos y devuelve la lista de errores (vacía si todo está bien).

    Los campos vacíos (None o "") se permiten: el modelo los rellena como en el
    entrenamiento. Lo que no se permite son campos desconocidos o valores que el
    modelo nunca vio.
    """
    errores = []
    columnas = meta["entradas"]["columnas"]
    opciones = meta["entradas"]["opciones"]

    desconocidos = set(entradas) - set(columnas)
    if desconocidos:
        errores.append(f"campos desconocidos: {sorted(desconocidos)}")

    edad = entradas.get("edad")
    if edad not in (None, ""):
        try:
            edad = float(edad)
        except (TypeError, ValueError):
            errores.append("edad: debe ser un número")
        else:
            minimo, maximo = meta["transformaciones"]["edad_rango_valido"]
            if not minimo <= edad <= maximo:
                errores.append(f"edad: debe estar entre {minimo} y {maximo}")

    for col, validos in opciones.items():
        valor = entradas.get(col)
        if valor not in (None, "") and valor not in validos:
            errores.append(f"{col}: valor no válido '{valor}'")

    return errores


def preparar_entradas(entradas: dict, meta: dict) -> pd.DataFrame:
    """Convierte los datos de un estudiante en la fila (DataFrame) que espera el modelo."""
    t = meta["transformaciones"]
    columnas = meta["entradas"]["columnas"]
    numericas = meta["entradas"]["numericas"]

    limpias = {col: (None if entradas.get(col) == "" else entradas.get(col)) for col in columnas}
    fila = pd.DataFrame([limpias], columns=columnas)

    # transformaciones previas, con las mismas reglas del entrenamiento
    fila["fami_cuartoshogar"] = fila["fami_cuartoshogar"].map(t["cuartos"])
    fila["fami_personashogar"] = fila["fami_personashogar"].map(t["personas"])
    for col, valores in t["a_faltante"].items():
        fila[col] = fila[col].replace(valores, np.nan)

    # mismos tipos de dato que en el entrenamiento: números y texto ("str" de pandas 3)
    for col in columnas:
        if col in numericas:
            fila[col] = pd.to_numeric(fila[col], errors="coerce")
        else:
            fila[col] = fila[col].astype("str")

    minimo, maximo = t["edad_rango_valido"]
    fila["edad"] = fila["edad"].where(fila["edad"].between(minimo, maximo))
    return fila