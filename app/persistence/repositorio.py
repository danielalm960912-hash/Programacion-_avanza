"""Capa de persistencia: consultas y escrituras de la aplicación (predicciones y datos de la fuente)."""

from datetime import datetime

from sqlalchemy import func, select

from app.persistence.db import db
from app.persistence.models import (
    Establecimiento,
    ModelVersion,
    Municipio,
    Prediction,
    Resultado,
    Sede,
    SedeJornada,
)


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


# ---------------------------------------------------------------------------
# Datos de la fuente (datos.gov.co): consultas para explorarlos en la app
# ---------------------------------------------------------------------------


def _contar(modelo) -> int:
    return db.session.execute(select(func.count()).select_from(modelo)).scalar_one()


def resumen_datos() -> dict:
    """Cuántos registros hay en cada tabla normalizada y el puntaje promedio."""
    promedio = db.session.execute(select(func.avg(Resultado.punt_global))).scalar_one()
    return {
        "estudiantes": _contar(Resultado),
        "sedes": _contar(Sede),
        "establecimientos": _contar(Establecimiento),
        "municipios": _contar(Municipio),
        "puntaje_promedio": round(float(promedio), 1) if promedio is not None else None,
    }


def opciones_filtros() -> dict:
    """Valores disponibles para filtrar la tabla de estudiantes."""
    municipios = db.session.execute(
        select(Municipio.nombre)
        .join(Sede, Sede.cod_mcpio == Municipio.cod_mcpio)
        .distinct()
        .order_by(Municipio.nombre)
    ).scalars().all()
    naturalezas = db.session.execute(
        select(Establecimiento.naturaleza)
        .where(Establecimiento.naturaleza.is_not(None))
        .distinct()
        .order_by(Establecimiento.naturaleza)
    ).scalars().all()
    return {"municipios": list(municipios), "naturalezas": list(naturalezas)}


def consultar_estudiantes(pagina: int, por_pagina: int, municipio: str | None, naturaleza: str | None) -> dict:
    """Una página de estudiantes, reconstruida uniendo las tablas normalizadas (JOIN)."""
    consulta = (
        select(
            Resultado.estu_consecutivo,
            Municipio.nombre.label("municipio"),
            Sede.nombre.label("sede"),
            Establecimiento.naturaleza,
            SedeJornada.jornada,
            Resultado.fami_estratovivienda.label("estrato"),
            Resultado.punt_global,
        )
        .join(SedeJornada, Resultado.codigo_icfes == SedeJornada.codigo_icfes)
        .join(Sede, SedeJornada.cod_dane_sede == Sede.cod_dane_sede)
        .join(Establecimiento, Sede.cod_dane_establecimiento == Establecimiento.cod_dane_establecimiento)
        .join(Municipio, Sede.cod_mcpio == Municipio.cod_mcpio)
    )
    if municipio:
        consulta = consulta.where(Municipio.nombre == municipio)
    if naturaleza:
        consulta = consulta.where(Establecimiento.naturaleza == naturaleza)

    total = db.session.execute(select(func.count()).select_from(consulta.subquery())).scalar_one()
    filas = db.session.execute(
        consulta.order_by(Resultado.estu_consecutivo)
        .limit(por_pagina)
        .offset((pagina - 1) * por_pagina)
    ).mappings().all()
    return {
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "estudiantes": [dict(fila) for fila in filas],
    }