"""Capa API: endpoints que reciben peticiones HTTP y responden en JSON."""

from flask import Blueprint, current_app, jsonify, request

from app.services.model_service import EntradaInvalida

api_bp = Blueprint("api", "app.api.routes", url_prefix="/api")


def servicio():
    """Devuelve el ModelService que se cargó al arrancar la app."""
    return current_app.extensions["model_service"]


@api_bp.get("/health")
def health():
    """Responde si la app está viva y qué modelo tiene cargado."""
    return jsonify(status="ok", modelo_version=servicio().version)


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

    try:
        resultado = servicio().predecir(entradas)
    except EntradaInvalida as error:
        return jsonify(errores=error.errores), 400

    return jsonify(resultado), 200