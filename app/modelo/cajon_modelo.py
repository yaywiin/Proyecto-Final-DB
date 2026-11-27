"""Acceso a la base para los cajones del estacionamiento.

Un cajón está ocupado si tiene una estancia sin salida, y apartado si tiene una
pensión que cubre las fechas consultadas. No hay una tabla aparte: el total sale
del parámetro `total_cajones`.
"""

from app.modelo.conexion import consultar


def total_cajones():
    """Cantidad de cajones, o None si falta el parámetro."""
    filas = consultar("SELECT valor FROM parametros WHERE clave = 'total_cajones'")
    return int(filas[0]["valor"]) if filas else None


def bloquear(cursor):
    """Hace que los guardados con cajón pasen de uno en uno.

    Debe ser lo primero de la transacción. Sin esto, dos cobradores que guardan el
    mismo cajón al mismo tiempo pasan los dos la revisión de los triggers.
    """
    cursor.execute("SELECT valor FROM parametros WHERE clave = 'total_cajones' FOR UPDATE")


def fecha_actual():
    """Fecha del servidor de base de datos."""
    return consultar("SELECT CURDATE() AS hoy")[0]["hoy"]


def ocupados():
    """{numero_cajon: matricula} de los vehículos que están dentro."""
    filas = consultar(
        "SELECT numero_cajon, matricula FROM detalle_servicios "
        "WHERE fecha_salida IS NULL AND numero_cajon IS NOT NULL"
    )
    return {fila["numero_cajon"]: fila["matricula"] for fila in filas}


def apartados(fecha_inicio, fecha_fin):
    """Pensiones con cajón que cubren alguna fecha del periodo."""
    return consultar(
        "SELECT numero_cajon, matricula, fecha_inicio, fecha_fin FROM pensiones "
        "WHERE numero_cajon IS NOT NULL AND fecha_inicio <= %s AND fecha_fin >= %s",
        (fecha_fin, fecha_inicio),
    )


def cajon_de_pension_vigente(matricula):
    """Cajón de la pensión que el vehículo tiene hoy, o None."""
    filas = consultar(
        "SELECT numero_cajon FROM pensiones "
        "WHERE matricula = %s AND numero_cajon IS NOT NULL "
        "AND CURDATE() BETWEEN fecha_inicio AND fecha_fin",
        (matricula,),
    )
    return filas[0]["numero_cajon"] if filas else None
