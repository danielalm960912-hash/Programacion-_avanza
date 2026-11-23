"""Capa API: endpoints que reciben peticiones HTTP y responden en JSON."""

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select

from app.persistence.db import base_datos_disponible, db
from app.persistence.models import Ingesta
from app.services.ingesta import ejecutar_ingesta
from app.services.model_service import EntradaInvalida
from app.persistence.repositorio import (
    consultar_estudiantes,
    opciones_filtros,
    resumen_datos,
    ultimas_predicciones,
)
from app.services.prediction_services import predecir_y_registrar

api_bp = Blueprint("api", "app.api.routes", url_prefix="/api")


def servicio():
    """Devuelve el ModelService que se cargó al arrancar la app."""
    return current_app.extensions["model_service"]


@api_bp.get("/health")
def health():
    """Responde si la app está viva, qué modelo tiene cargado y si llega a la base de datos."""
    bd_ok = base_datos_disponible()
    cuerpo = {
        "status": "ok" if bd_ok else "degradado",
        "modelo_version": servicio().version,
        "base_datos": "ok" if bd_ok else "sin conexión",
    }
    return jsonify(cuerpo), 200 if bd_ok else 503


@api_bp.get("/opciones")
def opciones():
    """Entrega los campos y sus valores válidos (para armar el formulario)."""
    meta = servicio().meta
    return jsonify(
        columnas=meta["entradas"]["columnas"],
        numericas=meta["entradas"]["numericas"],
        opciones=meta["entradas"]["opciones"],
        edad_rango_valido=meta["transformaciones"]["edad_rango_valido"],
    )


@api_bp.get("/ejemplos")
def ejemplos():
    """Entrega los estudiantes de ejemplo (para el botón 'Cargar ejemplo')."""
    return jsonify(servicio().meta["ejemplos"])


@api_bp.post("/predict")
def predict():
    """Recibe los datos de un estudiante en JSON y devuelve la predicción."""
    entradas = request.get_json(silent=True)
    if not isinstance(entradas, dict):
        return jsonify(errores=["el cuerpo debe ser un objeto JSON con los datos del estudiante"]), 400
    
    origen = "web" if request.args.get("origen") == "web" else "api"

    try:
        resultado = predecir_y_registrar(entradas, origen=origen)
    except EntradaInvalida as error:
        return jsonify(errores=error.errores), 400

    return jsonify(resultado), 200


@api_bp.post("/ingesta")
def ingesta():
    """Ejecuta la ingesta (ETL) desde datos.gov.co y devuelve el resumen."""
    if not current_app.config["INGESTA_HABILITADA"]:
        return jsonify(
            estado="deshabilitada",
            error="La ingesta está deshabilitada en este despliegue. Los datos se cargan desde el entorno local.",
        ), 403
    try:
        resumen = ejecutar_ingesta()
    except Exception as error:
        return jsonify(estado="fallida", error=str(error)), 500
    return jsonify(resumen), 201


@api_bp.get("/ingestas")
def ingestas():
    """Historial de las últimas 20 ingestas (trazabilidad)."""
    consulta = select(Ingesta).order_by(Ingesta.id.desc()).limit(20)
    filas = db.session.execute(consulta).scalars()
    return jsonify([
        {
            "id": i.id,
            "fecha": i.fecha.isoformat(),
            "estado": i.estado,
            "filas_recibidas": i.filas_recibidas,
            "filas_unicas": i.filas_unicas,
            "filas_nuevas": i.filas_nuevas,
            "duracion_s": i.duracion_s,
            "mensaje": i.mensaje,
        }
        for i in filas
    ])
    
    
@api_bp.get("/predicciones")
def predicciones():
    """Historial de las últimas 50 predicciones (trazabilidad de la inferencia)."""
    return jsonify([
        {
            "id": p.id,
            "creado_en": p.creado_en.isoformat(),
            "model_version_id": p.model_version_id,
            "origen": p.origen,
            "puntaje_predicho": p.puntaje_predicho,
            "rango": [p.rango_inferior, p.rango_superior],
            "etiqueta": p.etiqueta,
            "latencia_ms": p.latencia_ms,
            "entradas": p.entradas,
        }
        for p in ultimas_predicciones()
    ])
    

@api_bp.get("/resumen-datos")
def resumen():
    """Cuántos datos de la fuente hay guardados y las opciones para filtrarlos."""
    return jsonify(resumen=resumen_datos(), filtros=opciones_filtros())


@api_bp.get("/estudiantes")
def estudiantes():
    """Estudiantes guardados, paginados de 25 en 25 y con filtros opcionales."""
    pagina = max(request.args.get("pagina", 1, type=int), 1)
    municipio = request.args.get("municipio") or None
    naturaleza = request.args.get("naturaleza") or None
    return jsonify(consultar_estudiantes(pagina, 25, municipio, naturaleza))