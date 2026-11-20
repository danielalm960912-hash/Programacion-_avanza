"""Configuración de la app, leída de variables de entorno (con valores por defecto)."""

import os


class Config:
    MODELS_DIR = os.getenv("MODELS_DIR", "models")