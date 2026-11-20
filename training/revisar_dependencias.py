"""Revisa qué columnas dependen de qué llave, para diseñar las tablas normalizadas.

Para cada llave candidata (por ejemplo, el código DANE de la sede) cuenta en
cuántos casos una misma llave aparece con MÁS DE UN valor en otra columna.
0 casos = la columna depende de esa llave y puede ir en su tabla.
"""

import pandas as pd

raw = pd.read_pickle("data/saber11_antioquia_20224.pkl").drop_duplicates()
print(f"filas únicas: {len(raw):,}\n")

LLAVES = {
    "estu_consecutivo": [],
    "cole_cod_dane_sede": [
        "cole_nombre_sede", "cole_cod_dane_establecimiento", "cole_codigo_icfes",
        "cole_mcpio_ubicacion", "cole_area_ubicacion", "cole_naturaleza",
        "cole_calendario", "cole_caracter", "cole_bilingue", "cole_genero",
        "cole_jornada", "cole_sede_principal",
    ],
    "cole_cod_dane_establecimiento": [
        "cole_nombre_establecimiento", "cole_naturaleza", "cole_mcpio_ubicacion",
    ],
    "cole_cod_mcpio_ubicacion": ["cole_mcpio_ubicacion"],
}

for llave, columnas in LLAVES.items():
    print(f"=== {llave}: {raw[llave].nunique():,} valores distintos, "
          f"{raw[llave].isna().sum():,} vacíos ===")
    if llave == "estu_consecutivo":
        print(f"  ¿es única por fila?: {raw[llave].is_unique}\n")
        continue
    for col in columnas:
        varias = raw.groupby(llave)[col].nunique(dropna=False).gt(1).sum()
        estado = "depende ✅" if varias == 0 else f"NO depende ❌ ({varias:,} llaves con varios valores)"
        print(f"  {col:32s} {estado}")
    print()
    
    PRUEBAS = [
    (["cole_cod_dane_sede", "cole_jornada"], "cole_codigo_icfes"),
    (["cole_codigo_icfes"], "cole_cod_dane_sede"),
    (["cole_codigo_icfes"], "cole_jornada"),
    (["cole_cod_dane_establecimiento"], "cole_calendario"),
    (["cole_cod_dane_establecimiento"], "cole_caracter"),
    (["cole_cod_dane_establecimiento"], "cole_bilingue"),
    (["cole_cod_dane_establecimiento"], "cole_genero"),
    (["cole_cod_dane_establecimiento"], "cole_area_ubicacion"),
]

print("=== pruebas adicionales ===")
for llave, col in PRUEBAS:
    varias = raw.groupby(llave)[col].nunique(dropna=False).gt(1).sum()
    estado = "depende ✅" if varias == 0 else f"NO depende ❌ ({varias:,} casos)"
    print(f"  {' + '.join(llave):45s} → {col:28s} {estado}")