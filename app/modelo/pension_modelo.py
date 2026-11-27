"""Acceso a la base para las pensiones.

Una pensión es un registro de `pensiones`; al contratarla se cobra con un recibo en
`cobros` y su desglose en `detalle_cobros` (con `id_pension`).
"""

from app.modelo import cajon_modelo
from app.modelo.conexion import consultar, transaccion


def leer_parametro(clave):
    """Valor de un parámetro de la tabla `parametros`, o None si no existe."""
    filas = consultar("SELECT valor FROM parametros WHERE clave = %s", (clave,))
    return filas[0]["valor"] if filas else None


def primera_pension(id_cliente):
    """Fecha de inicio de la primera pensión del cliente, o None si nunca ha tenido."""
    filas = consultar(
        "SELECT MIN(fecha_inicio) AS primera FROM pensiones WHERE id_cliente = %s",
        (id_cliente,),
    )
    return filas[0]["primera"]


def hay_traslape(matricula, fecha_inicio, fecha_fin):
    """True si el vehículo ya tiene una pensión que cubre alguna de esas fechas."""
    filas = consultar(
        "SELECT COUNT(*) AS total FROM pensiones "
        "WHERE matricula = %s AND fecha_inicio <= %s AND fecha_fin >= %s",
        (matricula, fecha_fin, fecha_inicio),
    )
    return filas[0]["total"] > 0


def listar_pensiones():
    """Todas las pensiones, las más recientes primero, con su estado de hoy."""
    return consultar(
        "SELECT p.id_pension, p.matricula, c.nombre AS cliente, p.fecha_inicio, p.fecha_fin, p.monto, "
        "p.numero_cajon, "
        "CASE WHEN CURDATE() BETWEEN p.fecha_inicio AND p.fecha_fin THEN 'Vigente' "
        "     WHEN CURDATE() < p.fecha_inicio THEN 'Por iniciar' "
        "     ELSE 'Vencida' END AS estado "
        "FROM pensiones p JOIN clientes c ON c.id_cliente = p.id_cliente "
        "ORDER BY p.fecha_inicio DESC, p.id_pension DESC"
    )


def contratar_pension(id_cliente, matricula, id_usuario, fecha_inicio, fecha_fin, monto, numero_cajon):
    """Guarda la pensión, el recibo y su desglose en una sola transacción.

    Devuelve (id_pension, id_cobro).
    """
    with transaccion() as cursor:
        cajon_modelo.bloquear(cursor)
        cursor.execute(
            "INSERT INTO pensiones "
            "(id_cliente, matricula, id_usuario, fecha_inicio, fecha_fin, monto, numero_cajon) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (id_cliente, matricula, id_usuario, fecha_inicio, fecha_fin, monto, numero_cajon),
        )
        id_pension = cursor.lastrowid
        cursor.execute(
            "INSERT INTO cobros (id_usuario, monto_total) VALUES (%s, %s)",
            (id_usuario, monto),
        )
        id_cobro = cursor.lastrowid
        cursor.execute(
            "INSERT INTO detalle_cobros (id_cobro, matricula, id_pension, monto) VALUES (%s, %s, %s, %s)",
            (id_cobro, matricula, id_pension, monto),
        )
        return id_pension, id_cobro
