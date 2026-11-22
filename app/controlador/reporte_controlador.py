"""Reglas de la pantalla de reportes.

Describe los 4 reportes (columnas y totales) para que la vista solo tenga que
dibujarlos, y decide quién puede verlos.
"""

from app.modelo import reporte_modelo as modelo

TODOS_LOS_ANIOS = "Todos"


def es_admin(usuario):
    """El usuario puede traer el perfil como `rol` (base de datos) o `perfil`."""
    return (usuario.get("rol") or usuario.get("perfil")) == "admin"


def anios_disponibles():
    """Opciones del filtro: 'Todos' y cada año con datos, del más reciente al más antiguo."""
    return [TODOS_LOS_ANIOS] + [str(anio) for anio in modelo.listar_anios()]


def anio_inicial():
    """El año más reciente con datos, o 'Todos' si aún no hay ninguno."""
    opciones = anios_disponibles()
    return opciones[1] if len(opciones) > 1 else TODOS_LOS_ANIOS


def _dinero(valor):
    return f"${valor:,.2f}"


# Cada columna: (clave de la fila, título, ancho, alineación, formato)
REPORTES = [
    {
        "titulo": "Entradas y salidas por mes",
        "leer": modelo.entradas_salidas_por_mes,
        "columnas": [
            ("anio", "Año", 70, "center", str),
            ("nombre_mes", "Mes", 150, "center", str),
            ("total_entradas", "Entradas", 110, "center", str),
            ("total_salidas", "Salidas", 110, "center", str),
        ],
        "totales": {"total_entradas": str, "total_salidas": str},
    },
    {
        "titulo": "Meses con mayor demanda",
        "leer": modelo.meses_mayor_demanda,
        "columnas": [
            ("anio", "Año", 70, "center", str),
            ("nombre_mes", "Mes", 150, "center", str),
            ("total_vehiculos", "Vehículos", 110, "center", str),
        ],
        "totales": {"total_vehiculos": str},
    },
    {
        "titulo": "Horarios con mayor demanda",
        "leer": modelo.horarios_mayor_demanda,
        "columnas": [
            ("anio", "Año", 70, "center", str),
            ("franja_horaria", "Horario", 150, "center", str),
            ("total_entradas", "Entradas", 110, "center", str),
        ],
        "totales": {"total_entradas": str},
    },
    {
        "titulo": "Ingresos por servicio",
        "leer": modelo.ingresos_por_servicio,
        "columnas": [
            ("anio", "Año", 70, "center", str),
            ("servicio", "Servicio", 170, "center", str),
            ("total_operaciones", "Operaciones", 110, "center", str),
            ("total_ingresos", "Ingresos", 130, "center", _dinero),
        ],
        "totales": {"total_operaciones": str, "total_ingresos": _dinero},
    },
]


def armar_reporte(numero, opcion_anio):
    """Devuelve las filas ya formateadas y la fila de totales de un reporte.

    numero: posición en REPORTES (0 a 3). opcion_anio: 'Todos' o un año como texto.
    """
    reporte = REPORTES[numero]
    anio = None if opcion_anio == TODOS_LOS_ANIOS else int(opcion_anio)
    filas = reporte["leer"](anio)

    tabla = [
        tuple(formato(fila[clave]) for clave, _titulo, _ancho, _alin, formato in reporte["columnas"])
        for fila in filas
    ]

    totales = None
    if filas:
        suma = {clave: sum(fila[clave] for fila in filas) for clave in reporte["totales"]}
        totales = tuple(
            reporte["totales"][clave](suma[clave]) if clave in reporte["totales"] else ""
            for clave, *_ in reporte["columnas"]
        )
        totales = ("Total",) + totales[1:] if totales[0] == "" else totales
    return {"columnas": reporte["columnas"], "filas": tabla, "totales": totales}
