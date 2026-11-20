"""Capa de negocio: ingesta (ETL) desde datos.gov.co hacia PostgreSQL.

Extraer  -> descarga los resultados Saber 11 de la API de datos abiertos.
Transformar -> quita duplicados y separa los datos en las tablas normalizadas.
Cargar   -> inserta en PostgreSQL sin duplicar (ON CONFLICT DO NOTHING).
"""

import time

import pandas as pd
import requests
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.persistence.db import db
from app.persistence.models import Ingesta

BASE_URL = "https://www.datos.gov.co/resource/kgxf-xxbe.json"
FILTRO = "periodo = '20224' AND cole_depto_ubicacion = 'ANTIOQUIA'"
TAMANO_LOTE = 5_000

# columna de la fuente -> columna de la tabla resultado
COLUMNAS_RESULTADO = {
    "estu_consecutivo": "estu_consecutivo",
    "cole_codigo_icfes": "codigo_icfes",
    "periodo": "periodo",
    "estu_tipodocumento": "estu_tipodocumento",
    "estu_genero": "estu_genero",
    "estu_fechanacimiento": "estu_fechanacimiento",
    "estu_nacionalidad": "estu_nacionalidad",
    "estu_pais_reside": "estu_pais_reside",
    "estu_privado_libertad": "estu_privado_libertad",
    "estu_estudiante": "estu_estudiante",
    "estu_estadoinvestigacion": "estu_estadoinvestigacion",
    "estu_cod_reside_mcpio": "cod_mcpio_reside",
    "estu_cod_mcpio_presentacion": "cod_mcpio_presentacion",
    "fami_estratovivienda": "fami_estratovivienda",
    "fami_educacionpadre": "fami_educacionpadre",
    "fami_educacionmadre": "fami_educacionmadre",
    "fami_cuartoshogar": "fami_cuartoshogar",
    "fami_personashogar": "fami_personashogar",
    "fami_tieneinternet": "fami_tieneinternet",
    "fami_tieneautomovil": "fami_tieneautomovil",
    "fami_tienecomputador": "fami_tienecomputador",
    "fami_tienelavadora": "fami_tienelavadora",
    "punt_global": "punt_global",
    "punt_lectura_critica": "punt_lectura_critica",
    "punt_matematicas": "punt_matematicas",
    "punt_c_naturales": "punt_c_naturales",
    "punt_sociales_ciudadanas": "punt_sociales_ciudadanas",
    "punt_ingles": "punt_ingles",
    "desemp_ingles": "desemp_ingles",
}
PUNTAJES = [c for c in COLUMNAS_RESULTADO if c.startswith("punt_")]


# ------------------------------------------------------------------ extraer
def extraer() -> pd.DataFrame:
    """Descarga de la API los resultados de Antioquia del periodo 2022-2."""
    resp = requests.get(
        BASE_URL,
        params={"$where": FILTRO, "$limit": 200_000, "$order": "estu_consecutivo"},
        timeout=600,
    )
    resp.raise_for_status()
    return pd.DataFrame(resp.json())


# ------------------------------------------------------------- transformar
def _tabla(raw: pd.DataFrame, columnas: dict, llave: str) -> pd.DataFrame:
    """Toma las columnas indicadas, las renombra y deja una fila por llave."""
    tabla = raw[list(columnas)].rename(columns=columnas)
    tabla = tabla.dropna(subset=[llave])
    return tabla.drop_duplicates(subset=[llave])


def _inconsistencias(raw: pd.DataFrame, llave: str, columnas: list[str]) -> int:
    """Cuenta las llaves que aparecen con más de un valor en alguna columna (violan la 3FN)."""
    por_llave = raw.groupby(llave)[columnas].nunique(dropna=False)
    return int(por_llave.gt(1).any(axis=1).sum())


def transformar(raw: pd.DataFrame) -> dict:
    """Separa los datos de la fuente en las tablas normalizadas."""
    raw = raw.drop_duplicates()
    raw = raw.drop_duplicates(subset=["estu_consecutivo"], keep="last")

    # municipios: de ubicación del colegio, de residencia y de presentación del examen
    partes = []
    for cod, nombre, depto in [
        ("cole_cod_mcpio_ubicacion", "cole_mcpio_ubicacion", "cole_depto_ubicacion"),
        ("estu_cod_reside_mcpio", "estu_mcpio_reside", "estu_depto_reside"),
        ("estu_cod_mcpio_presentacion", "estu_mcpio_presentacion", "estu_depto_presentacion"),
    ]:
        partes.append(_tabla(raw, {cod: "cod_mcpio", nombre: "nombre", depto: "departamento"}, "cod_mcpio"))
    municipios = pd.concat(partes).drop_duplicates(subset=["cod_mcpio"])
    municipios["nombre"] = municipios["nombre"].fillna("Sin nombre")

    establecimientos = _tabla(raw, {
        "cole_cod_dane_establecimiento": "cod_dane_establecimiento",
        "cole_nombre_establecimiento": "nombre",
        "cole_naturaleza": "naturaleza",
        "cole_calendario": "calendario",
        "cole_caracter": "caracter",
        "cole_bilingue": "bilingue",
        "cole_genero": "genero",
    }, "cod_dane_establecimiento")
    establecimientos["nombre"] = establecimientos["nombre"].fillna("Sin nombre")

    sedes = _tabla(raw, {
        "cole_cod_dane_sede": "cod_dane_sede",
        "cole_cod_dane_establecimiento": "cod_dane_establecimiento",
        "cole_cod_mcpio_ubicacion": "cod_mcpio",
        "cole_nombre_sede": "nombre",
        "cole_area_ubicacion": "area_ubicacion",
        "cole_sede_principal": "sede_principal",
    }, "cod_dane_sede")
    sedes["nombre"] = sedes["nombre"].fillna("Sin nombre")

    sede_jornadas = _tabla(raw, {
        "cole_codigo_icfes": "codigo_icfes",
        "cole_cod_dane_sede": "cod_dane_sede",
        "cole_jornada": "jornada",
    }, "codigo_icfes")

    resultados = raw[list(COLUMNAS_RESULTADO)].rename(columns=COLUMNAS_RESULTADO)
    resultados["estu_fechanacimiento"] = pd.to_datetime(
        resultados["estu_fechanacimiento"], format="%d/%m/%Y", errors="coerce"
    ).dt.date
    for col in PUNTAJES:
        resultados[col] = pd.to_numeric(resultados[col], errors="coerce").astype("Int64")

    # control de calidad: ¿se siguen cumpliendo las dependencias del diseño?
    alertas = {
        "sedes_inconsistentes": _inconsistencias(raw, "cole_cod_dane_sede", [
            "cole_nombre_sede", "cole_cod_dane_establecimiento", "cole_cod_mcpio_ubicacion",
            "cole_area_ubicacion", "cole_sede_principal"]),
        "establecimientos_inconsistentes": _inconsistencias(raw, "cole_cod_dane_establecimiento", [
            "cole_nombre_establecimiento", "cole_naturaleza", "cole_calendario",
            "cole_caracter", "cole_bilingue", "cole_genero"]),
        "codigos_icfes_inconsistentes": _inconsistencias(raw, "cole_codigo_icfes", [
            "cole_cod_dane_sede", "cole_jornada"]),
    }

    return {
        "filas_unicas": len(raw),
        "alertas": alertas,
        "tablas": {
            "municipio": municipios,
            "establecimiento": establecimientos,
            "sede": sedes,
            "sede_jornada": sede_jornadas,
            "resultado": resultados,
        },
    }


# ------------------------------------------------------------------ cargar
def _a_python(valor):
    """Convierte vacíos de pandas en None y números de numpy en números de Python."""
    if valor is None or (not isinstance(valor, str) and pd.isna(valor)):
        return None
    return valor.item() if hasattr(valor, "item") else valor


def _contar(nombre_tabla: str) -> int:
    tabla = db.metadata.tables[nombre_tabla]
    return db.session.execute(select(func.count()).select_from(tabla)).scalar_one()


def _insertar(nombre_tabla: str, df: pd.DataFrame) -> int:
    """Inserta las filas que no existan (por llave primaria) y devuelve cuántas eran nuevas."""
    tabla = db.metadata.tables[nombre_tabla]
    antes = _contar(nombre_tabla)
    registros = [{k: _a_python(v) for k, v in fila.items()} for fila in df.to_dict(orient="records")]
    sentencia = pg_insert(tabla).on_conflict_do_nothing()
    for inicio in range(0, len(registros), TAMANO_LOTE):
        db.session.execute(sentencia, registros[inicio:inicio + TAMANO_LOTE])
    return _contar(nombre_tabla) - antes


def ejecutar_ingesta() -> dict:
    """Ejecuta el ETL completo y deja registro en la tabla ingesta. Devuelve un resumen."""
    inicio = time.perf_counter()
    try:
        raw = extraer()
        datos = transformar(raw)

        ingesta = Ingesta(fuente=BASE_URL, filtro=FILTRO, estado="en_proceso",
                          filas_recibidas=len(raw), filas_unicas=datos["filas_unicas"])
        db.session.add(ingesta)
        db.session.flush()  # obtiene el id de la ingesta sin terminar la transacción

        tablas = datos["tablas"]
        tablas["resultado"]["ingesta_id"] = ingesta.id
        nuevas = {nombre: _insertar(nombre, df) for nombre, df in tablas.items()}

        ingesta.filas_nuevas = nuevas["resultado"]
        ingesta.estado = "exitosa"
        ingesta.mensaje = f"nuevas por tabla: {nuevas}; alertas: {datos['alertas']}"
        ingesta.duracion_s = round(time.perf_counter() - inicio, 1)
        db.session.commit()  # todo o nada: si algo falló antes, no se guarda nada

        return {
            "ingesta_id": ingesta.id,
            "estado": ingesta.estado,
            "filas_recibidas": ingesta.filas_recibidas,
            "filas_unicas": ingesta.filas_unicas,
            "filas_nuevas_por_tabla": nuevas,
            "alertas": datos["alertas"],
            "duracion_s": ingesta.duracion_s,
        }
    except Exception as error:
        db.session.rollback()
        fallida = Ingesta(fuente=BASE_URL, filtro=FILTRO, estado="fallida",
                          mensaje=str(error)[:2000],
                          duracion_s=round(time.perf_counter() - inicio, 1))
        db.session.add(fallida)
        db.session.commit()
        raise