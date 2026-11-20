"""Capa de persistencia: conexión a la base de datos con SQLAlchemy."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def base_datos_disponible() -> bool:
    """Hace una consulta mínima para comprobar que la base de datos responde."""
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except Exception:
        db.session.rollback()
        return False