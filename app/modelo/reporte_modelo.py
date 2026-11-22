"""Acceso a la base para los reportes.

Cada reporte sale de una vista de `database/04_vistas.sql`. Los nombres de las
vistas son constantes de este módulo; el año siempre viaja como parámetro (%s).
"""

from app.modelo.conexion import consultar

_ENTRADAS_SALIDAS_MES = "vista_rep_7_entradas_salidas_mes"
_MESES_DEMANDA = "vista_rep_8_meses_mayor_demanda"
_HORARIOS_DEMANDA = "vista_rep_9_horarios_mayor_demanda"
_INGRESOS_SERVICIO = "vista_rep_10_ingresos_por_servicio"


def _leer(vista, orden, anio):
    """Lee una vista completa o filtrada por año, con el orden indicado."""
    if anio is None:
        return consultar(f"SELECT * FROM {vista} ORDER BY {orden}")
    return consultar(f"SELECT * FROM {vista} WHERE anio = %s ORDER BY {orden}", (anio,))


def listar_anios():
    """Años con datos, del más reciente al más antiguo."""
    filas = consultar(
        f"SELECT anio FROM {_ENTRADAS_SALIDAS_MES} "
        f"UNION SELECT anio FROM {_INGRESOS_SERVICIO} ORDER BY anio DESC"
    )
    return [fila["anio"] for fila in filas]


def entradas_salidas_por_mes(anio=None):
    return _leer(_ENTRADAS_SALIDAS_MES, "anio, mes", anio)


def meses_mayor_demanda(anio=None):
    return _leer(_MESES_DEMANDA, "anio, total_vehiculos DESC, mes", anio)


def horarios_mayor_demanda(anio=None):
    return _leer(_HORARIOS_DEMANDA, "anio, total_entradas DESC, hora", anio)


def ingresos_por_servicio(anio=None):
    return _leer(_INGRESOS_SERVICIO, "anio, total_ingresos DESC", anio)
