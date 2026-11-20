"""Pruebas de la transformación de la ingesta (sin internet ni base de datos)."""

import datetime

import pandas as pd

from app.services.ingesta import COLUMNAS_RESULTADO, transformar

COLUMNAS_COLEGIO = [
    "cole_cod_mcpio_ubicacion", "cole_mcpio_ubicacion", "cole_depto_ubicacion",
    "estu_mcpio_reside", "estu_depto_reside", "estu_mcpio_presentacion", "estu_depto_presentacion",
    "cole_cod_dane_establecimiento", "cole_nombre_establecimiento", "cole_naturaleza",
    "cole_calendario", "cole_caracter", "cole_bilingue", "cole_genero",
    "cole_cod_dane_sede", "cole_nombre_sede", "cole_area_ubicacion", "cole_sede_principal",
    "cole_jornada",
]


def fila(consecutivo: str, **cambios) -> dict:
    """Arma un registro de la fuente con valores de prueba; 'cambios' reemplaza los que se indiquen."""
    registro = {col: "valor" for col in list(COLUMNAS_RESULTADO) + COLUMNAS_COLEGIO}
    registro.update(
        estu_consecutivo=consecutivo,
        estu_fechanacimiento="01/02/2005",
        punt_global="250",
        cole_codigo_icfes="ICFES1",
        cole_cod_dane_sede="SEDE1",
        cole_jornada="MAÑANA",
        cole_cod_dane_establecimiento="COLEGIO1",
        cole_nombre_sede="Sede central",
        cole_cod_mcpio_ubicacion="05001",
        estu_cod_reside_mcpio="05001",
        estu_cod_mcpio_presentacion="05001",
    )
    registro.update(cambios)
    return registro


def test_quita_duplicados():
    raw = pd.DataFrame([fila("A"), fila("A"), fila("B")])
    datos = transformar(raw)
    assert datos["filas_unicas"] == 2
    assert len(datos["tablas"]["resultado"]) == 2


def test_normaliza_colegio_una_sola_vez():
    raw = pd.DataFrame([fila("A"), fila("B"), fila("C")])
    tablas = transformar(raw)["tablas"]
    assert len(tablas["resultado"]) == 3
    assert len(tablas["sede"]) == 1
    assert len(tablas["establecimiento"]) == 1
    assert len(tablas["municipio"]) == 1


def test_dos_jornadas_misma_sede():
    raw = pd.DataFrame([fila("A"), fila("B", cole_jornada="TARDE", cole_codigo_icfes="ICFES2")])
    tablas = transformar(raw)["tablas"]
    assert len(tablas["sede"]) == 1
    assert len(tablas["sede_jornada"]) == 2


def test_tipos_de_dato():
    resultado = transformar(pd.DataFrame([fila("A")]))["tablas"]["resultado"].iloc[0]
    assert resultado["punt_global"] == 250
    assert resultado["estu_fechanacimiento"] == datetime.date(2005, 2, 1)


def test_alerta_si_la_sede_es_inconsistente():
    raw = pd.DataFrame([fila("A"), fila("B", cole_nombre_sede="Otro nombre")])
    alertas = transformar(raw)["alertas"]
    assert alertas["sedes_inconsistentes"] == 1