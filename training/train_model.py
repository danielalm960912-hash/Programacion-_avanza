"""Entrena el modelo ganador (Hist Gradient Boosting) y lo exporta para la app.

Reproduce el notebook Trabajo_Final_Módulo_Inteligencia_Artificial.ipynb
con los hiperparámetros ganadores de Optuna, sin repetir la búsqueda.
"""

from pathlib import Path
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version

import joblib
import numpy as np
import pandas as pd
import requests
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

RANDOM_STATE = 42

# Carpeta donde se guarda la copia local de los datos (ignorada por Git)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_CACHE = DATA_DIR / "saber11_antioquia_20224.pkl"
MODELS_DIR = DATA_DIR.parent / "models"
MODEL_NAME = "saber11_hgb"
MODEL_VERSION = "v1"

# ---------------------------------------------------------------
# Constantes de los datos (notebook, sección 1)
# ---------------------------------------------------------------
BASE_URL = "https://www.datos.gov.co/resource/kgxf-xxbe.json"
FILTRO = "periodo = '20224' AND cole_depto_ubicacion = 'ANTIOQUIA'"
TARGET = "punt_global"

DROPPED_COLS = [
    # fuga: se conocen con los resultados del examen
    "punt_lectura_critica", "punt_matematicas", "punt_c_naturales",
    "punt_sociales_ciudadanas", "punt_ingles", "desemp_ingles",
    "estu_estadoinvestigacion",
    # un solo valor por los filtros de descarga
    "periodo", "cole_depto_ubicacion", "cole_cod_depto_ubicacion", "estu_estudiante",
    # identificadores
    "estu_consecutivo", "cole_codigo_icfes", "cole_cod_dane_establecimiento",
    "cole_cod_dane_sede",
    # demasiadas categorías
    "cole_nombre_establecimiento", "cole_nombre_sede",
    # códigos que repiten un nombre
    "cole_cod_mcpio_ubicacion", "estu_cod_reside_depto", "estu_cod_reside_mcpio",
    "estu_cod_depto_presentacion", "estu_cod_mcpio_presentacion",
    # repiten otra columna
    "estu_depto_reside", "estu_mcpio_reside", "estu_depto_presentacion",
    "estu_mcpio_presentacion", "estu_pais_reside",
    # casi siempre el mismo valor
    "estu_nacionalidad", "estu_privado_libertad",
    # se reemplaza por edad
    "estu_fechanacimiento",
]

# Transformaciones previas al pipeline (la app tendrá que aplicar las mismas)
FECHA_EXAMEN = pd.Timestamp("2022-08-01")
CUARTOS = {"Uno": 1, "Dos": 2, "Tres": 3, "Cuatro": 4, "Cinco": 5, "Seis o mas": 6}
PERSONAS = {"1 a 2": 1.5, "3 a 4": 3.5, "5 a 6": 5.5, "7 a 8": 7.5, "9 o más": 9}

# ---------------------------------------------------------------
# Constantes del preprocesamiento (notebook, sección 4)
# ---------------------------------------------------------------
NUMERIC_COLS = ["edad", "fami_cuartoshogar", "fami_personashogar"]
EDUCACION = [
    "Ninguno",
    "Primaria incompleta",
    "Primaria completa",
    "Secundaria (Bachillerato) incompleta",
    "Secundaria (Bachillerato) completa",
    "Técnica o tecnológica incompleta",
    "Técnica o tecnológica completa",
    "Educación profesional incompleta",
    "Educación profesional completa",
    "Postgrado",
]
ESTRATOS = ["Estrato 1", "Estrato 2", "Estrato 3", "Estrato 4", "Estrato 5", "Estrato 6"]
ORDINAL_LEVELS = {
    "fami_estratovivienda": ESTRATOS,
    "fami_educacionpadre": EDUCACION,
    "fami_educacionmadre": EDUCACION,
}
ORDINAL_COLS = list(ORDINAL_LEVELS)

# ---------------------------------------------------------------
# Modelo ganador: hiperparámetros del trial 12 de Optuna (notebook, sección 6)
# ---------------------------------------------------------------
TEST_SIZE = 0.20
BEST_PARAMS = {
    "learning_rate": 0.10616525141677582,
    "max_iter": 367,
    "max_depth": 7,
    "min_samples_leaf": 88,
    "l2_regularization": 0.0011367627929023169,
}


def descargar_datos() -> pd.DataFrame:
    """Lee los datos de la copia local; si no existe, los descarga de la API."""
    if RAW_CACHE.exists():
        print(f"Leyendo datos desde la copia local: {RAW_CACHE.name}")
        raw = pd.read_pickle(RAW_CACHE)
    else:
        print("Descargando datos de datos.gov.co (puede tardar unos minutos)...")
        resp = requests.get(
            BASE_URL,
            params={"$where": FILTRO, "$limit": 200_000, "$order": "estu_consecutivo"},
            timeout=300,
        )
        resp.raise_for_status()
        raw = pd.DataFrame(resp.json())
        DATA_DIR.mkdir(exist_ok=True)
        raw.to_pickle(RAW_CACHE)
        print(f"copia local guardada en: {RAW_CACHE}")
    print(f"descargadas: {raw.shape[0]:,} filas x {raw.shape[1]} columnas")
    return raw


def limpiar_datos(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Quita duplicados y aplica los arreglos de estructura del notebook.

    Devuelve (raw_sin_duplicados, data_limpia). raw se conserva porque
    más adelante sacaremos de ahí los ejemplos con sus valores originales.
    """
    raw = raw.drop_duplicates().reset_index(drop=True)
    print(f"sin duplicados: {len(raw):,} filas")

    data = raw.copy()
    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")

    nacimiento = pd.to_datetime(data["estu_fechanacimiento"], format="%d/%m/%Y", errors="coerce")
    data["edad"] = np.floor((FECHA_EXAMEN - nacimiento).dt.days / 365.25)
    data.loc[~data["edad"].between(10, 80), "edad"] = np.nan

    data["fami_cuartoshogar"] = data["fami_cuartoshogar"].map(CUARTOS)
    data["fami_personashogar"] = data["fami_personashogar"].map(PERSONAS)

    for col in ["fami_educacionpadre", "fami_educacionmadre"]:
        data[col] = data[col].replace("No sabe", np.nan)

    data = data.drop(columns=DROPPED_COLS)
    print(f"datos limpios: {data.shape[0]:,} filas x {data.shape[1]} columnas")
    return raw, data


def construir_pipeline(categorical_cols: list[str]) -> Pipeline:
    """Arma el preprocesador del notebook + el modelo con los mejores hiperparámetros."""
    numeric_steps = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    ordinal_steps = Pipeline([
        ("encode", OrdinalEncoder(
            categories=list(ORDINAL_LEVELS.values()),
            handle_unknown="use_encoded_value",
            unknown_value=np.nan,
        )),
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    categorical_steps = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Sin dato")),
        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric_steps, NUMERIC_COLS),
            ("ordinal", ordinal_steps, ORDINAL_COLS),
            ("categorical", categorical_steps, categorical_cols),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")

    return Pipeline([
        ("prepare", preprocessor),
        ("model", HistGradientBoostingRegressor(**BEST_PARAMS, random_state=RANDOM_STATE)),
    ])


def entrenar_y_evaluar(data: pd.DataFrame):
    """Hace la misma partición del notebook, entrena y mide el RMSE en prueba."""
    X = data.drop(columns=TARGET)
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"entrenamiento: {len(X_train):,} filas | prueba: {len(X_test):,} filas")

    categorical_cols = [c for c in X_train.columns if c not in NUMERIC_COLS + ORDINAL_COLS]
    print(f"columnas: {len(NUMERIC_COLS)} numéricas, {len(ORDINAL_COLS)} ordinales, "
          f"{len(categorical_cols)} nominales")

    print("Entrenando el modelo (puede tardar uno o dos minutos)...")
    modelo = construir_pipeline(categorical_cols).fit(X_train, y_train)

    rmse_test = root_mean_squared_error(y_test, modelo.predict(X_test))
    print(f"RMSE en el conjunto de prueba: {rmse_test:.2f}")
    return modelo, X_train, X_test, y_test, rmse_test, categorical_cols

def a_json(valor):
    """Convierte números de numpy a números normales de Python para guardarlos en JSON."""
    return valor.item() if hasattr(valor, "item") else str(valor)


def exportar(modelo, raw, data, X_train, X_test, rmse_test):
    """Guarda el modelo (.joblib) y su ficha técnica (metadata.json) en models/."""
    MODELS_DIR.mkdir(exist_ok=True)

    # 1. El modelo: el Pipeline completo (preprocesamiento + Hist Gradient Boosting)
    ruta_modelo = MODELS_DIR / f"{MODEL_NAME}_{MODEL_VERSION}.joblib"
    joblib.dump(modelo, ruta_modelo)
    tamano_mb = ruta_modelo.stat().st_size / 1_048_576
    print(f"modelo guardado: {ruta_modelo.name} ({tamano_mb:.1f} MB)")

    columnas = list(X_train.columns)
    columnas_texto = [c for c in columnas if c != "edad"]

    # 2. Opciones válidas de cada campo, tomadas del entrenamiento (para las listas desplegables)
    raw_train = raw.loc[X_train.index]
    opciones = {col: sorted(raw_train[col].dropna().unique().tolist()) for col in columnas_texto}

    # 3. Cuartiles del puntaje en entrenamiento (para la etiqueta del resultado)
    y_train = data.loc[X_train.index, TARGET]
    q1, q2, q3 = (float(v) for v in y_train.quantile([0.25, 0.50, 0.75]))

    # 4. Cinco estudiantes reales del conjunto de prueba, con sus valores originales
    idx = X_test.sample(n=5, random_state=RANDOM_STATE).index
    entradas = raw.loc[idx, columnas_texto].copy()
    entradas.insert(0, "edad", data.loc[idx, "edad"])
    entradas = entradas.astype(object).where(entradas.notna(), None)
    predichos = modelo.predict(X_test.loc[idx])
    ejemplos = [
        {
            "entradas": fila,
            "puntaje_real": float(data.loc[i, TARGET]),
            "puntaje_predicho": round(float(p), 2),
        }
        for i, fila, p in zip(idx, entradas.to_dict(orient="records"), predichos)
    ]

    metadata = {
        "modelo": {
            "nombre": MODEL_NAME,
            "version": MODEL_VERSION,
            "archivo": ruta_modelo.name,
            "algoritmo": "HistGradientBoostingRegressor",
            "hiperparametros": BEST_PARAMS,
            "entrenado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "entorno": {
            "python": platform.python_version(),
            **{lib: version(lib) for lib in ["scikit-learn", "pandas", "numpy", "joblib"]},
        },
        "metricas": {
            "rmse_prueba": round(rmse_test, 2),
            "rmse_validacion_cruzada": {"media": 40.55, "desviacion": 0.17,
                                        "fuente": "notebook, sección 6 (5 folds)"},
            "filas_entrenamiento": len(X_train),
            "filas_prueba": len(X_test),
        },
        "datos": {"fuente": BASE_URL, "filtro": FILTRO, "objetivo": TARGET},
        "entradas": {
            "columnas": columnas,
            "numericas": NUMERIC_COLS,
            "ordinales": ORDINAL_LEVELS,
            "opciones": opciones,
        },
        "transformaciones": {
            "edad_rango_valido": [10, 80],
            "cuartos": CUARTOS,
            "personas": PERSONAS,
            "a_faltante": {"fami_educacionpadre": ["No sabe"], "fami_educacionmadre": ["No sabe"]},
        },
        "etiquetas": {"cuartiles_puntaje": {"q1": q1, "q2": q2, "q3": q3}},
        "ejemplos": ejemplos,
    }

    ruta_meta = MODELS_DIR / "metadata.json"
    with open(ruta_meta, "w", encoding="utf-8") as archivo:
        json.dump(metadata, archivo, ensure_ascii=False, indent=2, default=a_json)
    print(f"metadata guardada: {ruta_meta.name}")



if __name__ == "__main__":
    raw = descargar_datos()
    raw, data = limpiar_datos(raw)
    modelo, X_train, X_test, y_test, rmse_test, categorical_cols = entrenar_y_evaluar(data)
    exportar(modelo, raw, data, X_train, X_test, rmse_test)