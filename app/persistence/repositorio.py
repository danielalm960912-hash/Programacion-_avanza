"""Capa de persistencia: lectura y escritura de versiones del modelo y predicciones."""

from datetime import datetime

from sqlalchemy import select

from app.persistence.db import db
from app.persistence.models import ModelVersion, Prediction


def version_del_modelo(meta: dict) -> ModelVersion:
    """Devuelve el registro de la versión del modelo; si todavía no existe, lo crea."""
    info = meta["modelo"]
    consulta = select(ModelVersion).where(
        ModelVersion.nombre == info["nombre"],
        ModelVersion.version == info["version"],
    )
    version = db.session.execute(consulta).scalar_one_or_none()
    if version is None:
        version = ModelVersion(
            nombre=info["nombre"],
            version=info["version"],
            archivo=info["archivo"],
            algoritmo=info["algoritmo"],
            rmse_prueba=meta["metricas"]["rmse_prueba"],
            entrenado_en=datetime.fromisoformat(info["entrenado_en"]),
        )
        db.session.add(version)
        db.session.flush()  # obtiene el id sin terminar la transacción
    return version


def guardar_prediccion(version: ModelVersion, entradas: dict, resultado: dict, origen: str) -> Prediction:
    """Guarda una predicción con sus entradas, su resultado y la versión del modelo."""
    prediccion = Prediction(
        model_version_id=version.id,
        origen=origen,
        entradas=entradas,
        puntaje_predicho=resultado["puntaje_predicho"],
        rango_inferior=resultado["rango"][0],
        rango_superior=resultado["rango"][1],
        etiqueta=resultado["etiqueta"],
        latencia_ms=resultado["latencia_ms"],
    )
    db.session.add(prediccion)
    db.session.commit()
    return prediccion


def ultimas_predicciones(limite: int = 50) -> list[Prediction]:
    """Devuelve las predicciones más recientes."""
    consulta = select(Prediction).order_by(Prediction.id.desc()).limit(limite)
    return list(db.session.execute(consulta).scalars())


def deshacer() -> None:
    """Deshace la transacción en curso (por ejemplo, si algo falló al guardar)."""
    db.session.rollback()