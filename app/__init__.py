"""Fábrica de la aplicación: arma la app Flask y conecta sus capas."""

from flask import Flask

from app.config import Config
from app.persistence.db import db
from app.services.model_service import ModelService


def create_app() -> Flask:
    app = Flask("app")
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # tildes y eñes legibles en las respuestas JSON

    # capa de persistencia: conexión a PostgreSQL (local o Neon, según DATABASE_URL)
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("Falta la variable de entorno DATABASE_URL (revisa el archivo .env)")
    db.init_app(app)

    # capa de negocio: el modelo se carga UNA sola vez, al arrancar la app
    app.extensions["model_service"] = ModelService(app.config["MODELS_DIR"])

    # capa API: registra los endpoints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # comando de consola:  flask --app app crear-tablas
    @app.cli.command("crear-tablas")
    def crear_tablas():
        """Crea en la base de datos las tablas que aún no existen."""
        from app.persistence import models  # noqa: F401  (registra las tablas)

        db.create_all()
        print("Tablas creadas (o ya existían).")

    return app