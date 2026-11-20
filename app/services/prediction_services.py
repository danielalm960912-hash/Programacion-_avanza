"""Capa de negocio: predice y deja registro persistente de cada inferencia."""

from flask import current_app

from app.persistence import repositorio


def predecir_y_registrar(entradas: dict, origen: str = "api") -> dict:
    """Pide la predicción al modelo y la guarda en la base de datos (trazabilidad)."""
    servicio = current_app.extensions["model_service"]
    resultado = servicio.predecir(entradas)  # si los datos son inválidos, lanza EntradaInvalida

    try:
        version = repositorio.version_del_modelo(servicio.meta)
        registro = repositorio.guardar_prediccion(version, entradas, resultado, origen)
        resultado["prediccion_id"] = registro.id
    except Exception:
        repositorio.deshacer()
        current_app.logger.exception("No se pudo guardar la predicción en la base de datos")
        resultado["prediccion_id"] = None
    return resultado