"""Acceso a la base para las entradas y salidas de vehículos.

Una entrada es un registro de `detalle_servicios` con `fecha_salida` en NULL.
Al registrar la salida se llena `fecha_salida`. El servicio 1 del catálogo es
"Estancia por hora".
"""

from app.modelo import cajon_modelo
from app.modelo.conexion import consultar, transaccion

ID_SERVICIO_ESTANCIA = 1


def buscar_vehiculo(matricula):
    """Devuelve el vehículo con su cliente, o None si no existe."""
    filas = consultar(
        "SELECT v.matricula, v.marca, v.modelo, v.color, c.id_cliente, c.nombre AS cliente "
        "FROM vehiculos v JOIN clientes c ON c.id_cliente = v.id_cliente "
        "WHERE v.matricula = %s",
        (matricula,),
    )
    return filas[0] if filas else None


def buscar_entrada_abierta(matricula):
    """Devuelve la estancia sin salida del vehículo, o None."""
    filas = consultar(
        "SELECT id_detalle_servicio, fecha_entrada, numero_cajon FROM detalle_servicios "
        "WHERE matricula = %s AND fecha_salida IS NULL",
        (matricula,),
    )
    return filas[0] if filas else None


def listar_clientes():
    return consultar("SELECT id_cliente, nombre FROM clientes ORDER BY id_cliente")


def listar_dentro():
    """Vehículos que siguen dentro, del que lleva más tiempo al más reciente."""
    return consultar(
        "SELECT ds.id_detalle_servicio, ds.matricula, c.nombre AS cliente, "
        "ds.fecha_entrada, ds.numero_cajon, u.nombre AS cobrador "
        "FROM detalle_servicios ds "
        "JOIN vehiculos v ON v.matricula = ds.matricula "
        "JOIN clientes c ON c.id_cliente = v.id_cliente "
        "JOIN usuarios u ON u.id_usuario = ds.id_usuario "
        "WHERE ds.fecha_salida IS NULL ORDER BY ds.fecha_entrada"
    )


def registrar_entrada(matricula, id_usuario, numero_cajon, vehiculo_nuevo=None):
    """Guarda la entrada. Si el vehículo es nuevo lo crea en la misma transacción.

    vehiculo_nuevo: dict con id_cliente, marca, modelo y color (o None si ya existe).
    Devuelve el id del registro de la estancia.
    """
    with transaccion() as cursor:
        cajon_modelo.bloquear(cursor)
        if vehiculo_nuevo is not None:
            cursor.execute(
                "INSERT INTO vehiculos (matricula, id_cliente, marca, modelo, color) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    matricula,
                    vehiculo_nuevo["id_cliente"],
                    vehiculo_nuevo.get("marca"),
                    vehiculo_nuevo.get("modelo"),
                    vehiculo_nuevo.get("color"),
                ),
            )
        cursor.execute(
            "INSERT INTO detalle_servicios (matricula, id_servicio, id_usuario, fecha_entrada, numero_cajon) "
            "VALUES (%s, %s, %s, NOW(), %s)",
            (matricula, ID_SERVICIO_ESTANCIA, id_usuario, numero_cajon),
        )
        return cursor.lastrowid


def hora_actual():
    """Hora del servidor de base de datos, la misma que usan las entradas."""
    return consultar("SELECT NOW() AS ahora")[0]["ahora"]


def calcular_cobro(id_detalle_servicio, fecha_salida):
    """Calcula el cobro con el procedimiento de la base, sin guardar nada.

    Devuelve minutos, horas cobradas, tipo de cliente, si tiene pensión vigente,
    el monto y el motivo.
    """
    with transaccion() as cursor:
        cursor.callproc("sp_calcular_cobro_servicio", (id_detalle_servicio, fecha_salida))
        return cursor.fetchone()


def guardar_salida_con_cobro(id_detalle_servicio, matricula, id_usuario, fecha_salida, horas, monto):
    """Guarda la salida, el recibo y su desglose en una sola transacción.

    Devuelve el id del cobro, o None si la estancia ya tenía salida.
    """
    with transaccion() as cursor:
        cerradas = cursor.execute(
            "UPDATE detalle_servicios SET fecha_salida = %s "
            "WHERE id_detalle_servicio = %s AND fecha_salida IS NULL",
            (fecha_salida, id_detalle_servicio),
        )
        if cerradas == 0:
            return None
        cursor.execute(
            "INSERT INTO cobros (id_usuario, monto_total, fecha_cobro) VALUES (%s, %s, %s)",
            (id_usuario, monto, fecha_salida),
        )
        id_cobro = cursor.lastrowid
        cursor.execute(
            "INSERT INTO detalle_cobros (id_cobro, matricula, id_detalle_servicio, horas_cobradas, monto) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_cobro, matricula, id_detalle_servicio, horas, monto),
        )
        return id_cobro
