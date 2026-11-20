"""Pruebas de la capa de negocio. Se ejecutan con:  python -m pytest -v"""

import pytest

from app.services.model_service import EntradaInvalida, ModelService

servicio = ModelService("models")
EJEMPLOS = servicio.meta["ejemplos"]


def test_predice_igual_que_al_entrenar():
    for ejemplo in EJEMPLOS:
        resultado = servicio.predecir(ejemplo["entradas"])
        assert abs(resultado["puntaje_predicho"] - ejemplo["puntaje_predicho"]) < 0.1


def test_respuesta_tiene_los_campos_esperados():
    resultado = servicio.predecir(EJEMPLOS[0]["entradas"])
    assert set(resultado) == {"puntaje_predicho", "rango", "etiqueta", "modelo_version", "latencia_ms"}
    assert resultado["rango"][0] <= resultado["puntaje_predicho"] <= resultado["rango"][1]


def test_campos_vacios_se_permiten():
    entradas = dict(EJEMPLOS[0]["entradas"])
    entradas["fami_educacionpadre"] = None
    entradas["edad"] = ""
    resultado = servicio.predecir(entradas)
    assert 0 <= resultado["puntaje_predicho"] <= 500


def test_valor_desconocido_se_rechaza():
    entradas = dict(EJEMPLOS[0]["entradas"])
    entradas["fami_estratovivienda"] = "Estrato 99"
    with pytest.raises(EntradaInvalida):
        servicio.predecir(entradas)


def test_edad_fuera_de_rango_se_rechaza():
    entradas = dict(EJEMPLOS[0]["entradas"])
    entradas["edad"] = 5
    with pytest.raises(EntradaInvalida):
        servicio.predecir(entradas)