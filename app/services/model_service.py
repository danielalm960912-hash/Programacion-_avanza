"""Capa de negocio: carga el modelo una sola vez y hace las predicciones."""

import json
import time
from pathlib import Path

import joblib

from app.services.features import preparar_entradas, validar_entradas


class EntradaInvalida(Exception):
    """Se lanza cuando los datos recibidos no pasan la validación."""

    @property
    def errores(self) -> list[str]:
        return self.args[0]


class ModelService:
    """Envuelve el modelo entrenado y su ficha técnica (metadata.json)."""

    def __init__(self, models_dir: str | Path = "models"):
        models_dir = Path(models_dir)
        self.meta = json.loads((models_dir / "metadata.json").read_text(encoding="utf-8"))
        self.modelo = joblib.load(models_dir / self.meta["modelo"]["archivo"])
        self.rmse = self.meta["metricas"]["rmse_prueba"]

    @property
    def version(self) -> str:
        return f"{self.meta['modelo']['nombre']}_{self.meta['modelo']['version']}"

    def etiqueta(self, puntaje: float) -> str:
        """Ubica el puntaje en los cuartiles del entrenamiento."""
        q = self.meta["etiquetas"]["cuartiles_puntaje"]
        if puntaje < q["q1"]:
            return "Bajo"
        if puntaje < q["q2"]:
            return "Medio-bajo"
        if puntaje < q["q3"]:
            return "Medio-alto"
        return "Alto"

    def predecir(self, entradas: dict) -> dict:
        """Valida, prepara y predice. Devuelve el resultado listo para responder."""
        errores = validar_entradas(entradas, self.meta)
        if errores:
            raise EntradaInvalida(errores)

        inicio = time.perf_counter()
        fila = preparar_entradas(entradas, self.meta)
        puntaje = float(self.modelo.predict(fila)[0])
        latencia_ms = round((time.perf_counter() - inicio) * 1000, 1)

        return {
            "puntaje_predicho": round(puntaje, 1),
            "rango": [round(max(puntaje - self.rmse, 0), 1), round(min(puntaje + self.rmse, 500), 1)],
            "etiqueta": self.etiqueta(puntaje),
            "modelo_version": self.version,
            "latencia_ms": latencia_ms,
        }