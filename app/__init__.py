"""Fábrica de la aplicación: arma la app Flask y conecta sus capas."""

from flask import Flask

from app.config import Config
from app.services.model_service import ModelService


def create_app() -> Flask:
    app = Flask("app")
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # tildes y eñes legibles en las respuestas JSON

    # capa de negocio: el modelo se carga UNA sola vez, al arrancar la app
    app.extensions["model_service"] = ModelService(app.config["MODELS_DIR"])

    # capa API: registra los endpoints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)

    return app