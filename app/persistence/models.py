"""Capa de persistencia: tablas de la base de datos (modelo entidad-relación).

Grupo 1: datos de la fuente (datos.gov.co), normalizados en 3FN según el
análisis de dependencias de training/revisar_dependencias.py.
Cada clase es una tabla; Flask-SQLAlchemy la nombra en minúscula y singular
(Municipio -> municipio, SedeJornada -> sede_jornada).
"""

from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB

from app.persistence.db import db


def ahora() -> datetime:
    return datetime.now(timezone.utc)


class Municipio(db.Model):
    """Municipios de Colombia (ubicación de sedes, residencia y presentación)."""

    cod_mcpio = db.Column(db.Text, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    departamento = db.Column(db.Text)


class Establecimiento(db.Model):
    """Colegio (establecimiento educativo). Sus atributos dependen de su código DANE."""

    cod_dane_establecimiento = db.Column(db.Text, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    naturaleza = db.Column(db.Text)
    calendario = db.Column(db.Text)
    caracter = db.Column(db.Text)
    bilingue = db.Column(db.Text)
    genero = db.Column(db.Text)


class Sede(db.Model):
    """Sede de un establecimiento. El municipio y el área son de la sede, no del colegio."""

    cod_dane_sede = db.Column(db.Text, primary_key=True)
    cod_dane_establecimiento = db.Column(
        db.Text, db.ForeignKey("establecimiento.cod_dane_establecimiento"), nullable=False
    )
    cod_mcpio = db.Column(db.Text, db.ForeignKey("municipio.cod_mcpio"), nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    area_ubicacion = db.Column(db.Text)
    sede_principal = db.Column(db.Text)


class SedeJornada(db.Model):
    """Una sede en una jornada. El código ICFES identifica exactamente esa combinación."""

    codigo_icfes = db.Column(db.Text, primary_key=True)
    cod_dane_sede = db.Column(db.Text, db.ForeignKey("sede.cod_dane_sede"), nullable=False)
    jornada = db.Column(db.Text, nullable=False)


db.Index("ux_sede_jornada", SedeJornada.cod_dane_sede, SedeJornada.jornada, unique=True)


class Ingesta(db.Model):
    """Registro de cada carga desde datos.gov.co (trazabilidad del ETL)."""

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora)
    fuente = db.Column(db.Text, nullable=False)
    filtro = db.Column(db.Text)
    filas_recibidas = db.Column(db.Integer)
    filas_unicas = db.Column(db.Integer)
    filas_nuevas = db.Column(db.Integer)
    estado = db.Column(db.Text, nullable=False)
    mensaje = db.Column(db.Text)
    duracion_s = db.Column(db.Float)


class Resultado(db.Model):
    """Un estudiante y sus resultados en la prueba Saber 11."""

    estu_consecutivo = db.Column(db.Text, primary_key=True)
    codigo_icfes = db.Column(db.Text, db.ForeignKey("sede_jornada.codigo_icfes"), nullable=False)
    ingesta_id = db.Column(db.Integer, db.ForeignKey("ingesta.id"), nullable=False)
    periodo = db.Column(db.Text, nullable=False)

    # datos del estudiante
    estu_tipodocumento = db.Column(db.Text)
    estu_genero = db.Column(db.Text)
    estu_fechanacimiento = db.Column(db.Date)
    estu_nacionalidad = db.Column(db.Text)
    estu_pais_reside = db.Column(db.Text)
    estu_privado_libertad = db.Column(db.Text)
    estu_estudiante = db.Column(db.Text)
    estu_estadoinvestigacion = db.Column(db.Text)
    cod_mcpio_reside = db.Column(db.Text, db.ForeignKey("municipio.cod_mcpio"))
    cod_mcpio_presentacion = db.Column(db.Text, db.ForeignKey("municipio.cod_mcpio"))

    # datos de la familia (valores originales de la fuente)
    fami_estratovivienda = db.Column(db.Text)
    fami_educacionpadre = db.Column(db.Text)
    fami_educacionmadre = db.Column(db.Text)
    fami_cuartoshogar = db.Column(db.Text)
    fami_personashogar = db.Column(db.Text)
    fami_tieneinternet = db.Column(db.Text)
    fami_tieneautomovil = db.Column(db.Text)
    fami_tienecomputador = db.Column(db.Text)
    fami_tienelavadora = db.Column(db.Text)

    # puntajes
    punt_global = db.Column(db.Integer)
    punt_lectura_critica = db.Column(db.Integer)
    punt_matematicas = db.Column(db.Integer)
    punt_c_naturales = db.Column(db.Integer)
    punt_sociales_ciudadanas = db.Column(db.Integer)
    punt_ingles = db.Column(db.Integer)
    desemp_ingles = db.Column(db.Text)
    
# ---------------------------------------------------------------------------
# Grupo 2: modelo y predicciones (los llena la app al predecir)
# ---------------------------------------------------------------------------


class ModelVersion(db.Model):
    """Cada versión del modelo que ha hecho predicciones (trazabilidad)."""

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    version = db.Column(db.Text, nullable=False)
    archivo = db.Column(db.Text, nullable=False)
    algoritmo = db.Column(db.Text)
    rmse_prueba = db.Column(db.Float)
    entrenado_en = db.Column(db.DateTime(timezone=True))
    registrado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora)


db.Index("ux_model_version", ModelVersion.nombre, ModelVersion.version, unique=True)


class Prediction(db.Model):
    """Registro persistente de cada inferencia: entradas, resultado, versión y fecha."""

    id = db.Column(db.Integer, primary_key=True)
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_version.id"), nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora)
    origen = db.Column(db.Text, nullable=False)
    entradas = db.Column(JSONB, nullable=False)
    puntaje_predicho = db.Column(db.Float, nullable=False)
    rango_inferior = db.Column(db.Float)
    rango_superior = db.Column(db.Float)
    etiqueta = db.Column(db.Text)
    latencia_ms = db.Column(db.Float)