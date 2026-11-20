"""Pruebas de la capa API. Se ejecutan con:  python -m pytest -v"""

import pytest

from app import create_app


@pytest.fixture
def cliente():
    app = create_app()
    return app.test_client()


def test_health(cliente):
    respuesta = cliente.get("/api/health")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["status"] == "ok"


def test_opciones(cliente):
    datos = cliente.get("/api/opciones").get_json()
    assert "edad" in datos["columnas"]
    assert len(datos["opciones"]) > 0


def test_predict_con_un_ejemplo(cliente):
    ejemplo = cliente.get("/api/ejemplos").get_json()[0]
    respuesta = cliente.post("/api/predict", json=ejemplo["entradas"])
    assert respuesta.status_code == 200
    assert abs(respuesta.get_json()["puntaje_predicho"] - ejemplo["puntaje_predicho"]) < 0.1


def test_predict_rechaza_datos_invalidos(cliente):
    respuesta = cliente.post("/api/predict", json={"edad": 5})
    assert respuesta.status_code == 400
    assert "errores" in respuesta.get_json()


def test_predict_rechaza_cuerpo_que_no_es_json(cliente):
    respuesta = cliente.post("/api/predict", data="hola")
    assert respuesta.status_code == 400