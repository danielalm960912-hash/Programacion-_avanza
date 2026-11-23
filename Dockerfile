# Imagen de la app: Python 3.12 (misma versión menor del entrenamiento) sobre un Linux liviano
FROM python:3.12-slim

# Python: no crear archivos .pyc y mostrar los logs al instante
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Primero solo las dependencias: Docker guarda este paso en caché
#    y no lo repite mientras requirements.txt no cambie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Luego el código de la app y el modelo entrenado
COPY app/ app/
COPY models/ models/

# Usuario sin privilegios de administrador (buena práctica de seguridad)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Al arrancar: crea las tablas que falten y levanta Gunicorn con la fábrica de la app
CMD ["sh", "-c", "flask --app app crear-tablas && exec gunicorn --bind 0.0.0.0:${PORT:-8000} --timeout 300 'app:create_app()'"]