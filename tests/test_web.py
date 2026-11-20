"""Pruebas de la capa de presentación (páginas web)."""

import pytest

from app import create_app


@pytest.fixture
def cliente():
    return create_app().test_client()


def test_pagina_prediccion(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)
    assert 'id="formulario"' in html
    assert html.count("<select") == 20


def test_pagina_historial(cliente):
    respuesta = cliente.get("/historial")
    assert respuesta.status_code == 200
    assert "Historial de predicciones" in respuesta.get_data(as_text=True)


def test_pagina_datos(cliente):
    respuesta = cliente.get("/datos")
    assert respuesta.status_code == 200
    assert "boton-ingesta" in respuesta.get_data(as_text=True)


def test_prediccion_desde_web_queda_con_origen_web(cliente):
    ejemplo = cliente.get("/api/ejemplos").get_json()[0]
    respuesta = cliente.post("/api/predict?origen=web", json=ejemplo["entradas"])
    prediccion_id = respuesta.get_json()["prediccion_id"]
    historial = cliente.get("/api/predicciones").get_json()
    registro = next(p for p in historial if p["id"] == prediccion_id)
    assert registro["origen"] == "web"