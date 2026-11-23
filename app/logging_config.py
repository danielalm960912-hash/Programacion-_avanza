import json
import logging
import sys
from datetime import datetime, timezone

# Atributos que todo LogRecord trae por defecto. Lo que NO esté aquí
# son campos extra que nosotros agregamos (puntaje, latencia, etc.).
CAMPOS_ESTANDAR = set(vars(logging.LogRecord("", 0, "", 0, "", None, None)))
CAMPOS_ESTANDAR.update({"message", "asctime"})


class FormatoJSON(logging.Formatter):
    """Convierte cada registro de log en una línea JSON."""

    def format(self, record):
        datos = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "status": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
            "service": "saber11-app",
        }
        # Campos extra enviados con extra={...}
        for clave, valor in vars(record).items():
            if clave not in CAMPOS_ESTANDAR and clave not in datos:
                datos[clave] = valor
        # Si hay una excepción, se agrega el detalle del error
        if record.exc_info:
            datos["error.stack"] = self.formatException(record.exc_info)
        return json.dumps(datos, ensure_ascii=False, default=str)


def configurar_logs(nivel="INFO"):
    """Todos los logs de la app salen en JSON por stdout."""
    manejador = logging.StreamHandler(sys.stdout)
    manejador.setFormatter(FormatoJSON())
    raiz = logging.getLogger()
    raiz.handlers.clear()
    raiz.addHandler(manejador)
    raiz.setLevel(nivel)