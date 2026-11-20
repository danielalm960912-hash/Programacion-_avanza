"""Capa de presentación: páginas web de la aplicación (plantillas Jinja2)."""

from flask import Blueprint, current_app, render_template

web_bp = Blueprint("web", "app.web.routes")

# Los 21 campos del formulario, agrupados y con un nombre legible
GRUPOS = [
    ("Estudiante", [
        ("edad", "Edad"),
        ("estu_genero", "Género"),
        ("estu_tipodocumento", "Tipo de documento"),
    ]),
    ("Familia", [
        ("fami_estratovivienda", "Estrato de la vivienda"),
        ("fami_educacionpadre", "Educación del padre"),
        ("fami_educacionmadre", "Educación de la madre"),
        ("fami_cuartoshogar", "Cuartos en el hogar"),
        ("fami_personashogar", "Personas en el hogar"),
        ("fami_tieneinternet", "¿Tiene internet?"),
        ("fami_tienecomputador", "¿Tiene computador?"),
        ("fami_tieneautomovil", "¿Tiene automóvil?"),
        ("fami_tienelavadora", "¿Tiene lavadora?"),
    ]),
    ("Colegio", [
        ("cole_mcpio_ubicacion", "Municipio del colegio"),
        ("cole_naturaleza", "Naturaleza"),
        ("cole_area_ubicacion", "Área"),
        ("cole_jornada", "Jornada"),
        ("cole_calendario", "Calendario"),
        ("cole_caracter", "Carácter"),
        ("cole_bilingue", "¿Bilingüe?"),
        ("cole_genero", "Género del colegio"),
        ("cole_sede_principal", "¿Sede principal?"),
    ]),
]

# Campos cuyo orden natural está en las reglas de transformación del metadata
ORDEN_TRANSFORMACION = {"fami_cuartoshogar": "cuartos", "fami_personashogar": "personas"}


def opciones_ordenadas(meta: dict, col: str) -> list[str]:
    """Opciones de un campo en su orden natural (estratos, educación, cuartos...)."""
    valores = meta["entradas"]["opciones"][col]
    if col in meta["entradas"]["ordinales"]:
        orden = meta["entradas"]["ordinales"][col]
    elif col in ORDEN_TRANSFORMACION:
        orden = list(meta["transformaciones"][ORDEN_TRANSFORMACION[col]])
    else:
        return valores
    return [v for v in orden if v in valores] + [v for v in valores if v not in orden]


@web_bp.get("/")
def prediccion():
    """Página principal: formulario de predicción."""
    meta = current_app.extensions["model_service"].meta
    columnas = meta["entradas"]["columnas"]
    grupos = [
        (titulo, [
            {
                "nombre": col,
                "etiqueta": etiqueta,
                "opciones": None if col == "edad" else opciones_ordenadas(meta, col),
            }
            for col, etiqueta in campos if col in columnas
        ])
        for titulo, campos in GRUPOS
    ]
    edad_min, edad_max = meta["transformaciones"]["edad_rango_valido"]
    rmse = meta["metricas"]["rmse_prueba"]
    cuartiles = meta["etiquetas"]["cuartiles_puntaje"]
    return render_template(
        "prediccion.html",
        activa="prediccion",
        grupos=grupos,
        edad_min=edad_min,
        edad_max=edad_max,
        rmse=rmse,
        cuartiles=cuartiles,
        rmse_porcentaje=round(rmse / cuartiles["q2"] * 100),
    )


@web_bp.get("/historial")
def historial():
    """Historial de predicciones guardadas."""
    return render_template("historial.html", activa="historial")


@web_bp.get("/datos")
def datos():
    """Ingesta de datos desde datos.gov.co y su historial."""
    return render_template("datos.html", activa="datos")