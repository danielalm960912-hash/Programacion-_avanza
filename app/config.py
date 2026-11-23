"""Configuración de la app, leída de variables de entorno (con valores por defecto)."""

import os

from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env si existe (en Docker las variables llegan por el compose)


class Config:
    MODELS_DIR = os.getenv("MODELS_DIR", "models")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    # En el despliegue gratuito (512 MB de RAM) la ingesta se desactiva:
    # los datos se cargan a Neon desde el entorno local.
    INGESTA_HABILITADA = os.getenv("INGESTA_HABILITADA", "true").lower() == "true"