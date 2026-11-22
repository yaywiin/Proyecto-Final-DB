"""Acceso a la base de datos para clientes y vehículos (Issue #12)."""

from app.modelo.conexion import consultar, ejecutar, insertar, transaccion

ID_PUBLICO_GENERAL = 1


# ------------------------------------------------------------------ clientes
def listar_clientes(filtro=""):
    """Devuelve clientes con su conteo de vehículos, filtrando por nombre o teléfono."""
    filtro = (filtro or "").strip()
    if filtro:
        patron = f"%{filtro}%"
        return consultar(
            "SELECT c.id_cliente, c.nombre, c.telefono, c.tipo_cliente, c.fecha_registro, "
            "COUNT(v.matricula) AS total_vehiculos "
            "FROM clientes c "
            "LEFT JOIN vehiculos v ON v.id_cliente = c.id_cliente "
            "WHERE c.nombre LIKE %s OR IFNULL(c.telefono, '') LIKE %s "
            "GROUP BY c.id_cliente, c.nombre, c.telefono, c.tipo_cliente, c.fecha_registro "
            "ORDER BY c.id_cliente ASC",
            (patron, patron),
        )
    return consultar(
        "SELECT c.id_cliente, c.nombre, c.telefono, c.tipo_cliente, c.fecha_registro, "
        "COUNT(v.matricula) AS total_vehiculos "
        "FROM clientes c "
        "LEFT JOIN vehiculos v ON v.id_cliente = c.id_cliente "
        "GROUP BY c.id_cliente, c.nombre, c.telefono, c.tipo_cliente, c.fecha_registro "
        "ORDER BY c.id_cliente ASC"
    )


def buscar_cliente_por_id(id_cliente):
    filas = consultar(
        "SELECT id_cliente, nombre, telefono, tipo_cliente, fecha_registro "
        "FROM clientes WHERE id_cliente = %s",
        (id_cliente,),
    )
    return filas[0] if filas else None


def crear_cliente(nombre, telefono, tipo_cliente, matricula_publico=None):
    """Crea un cliente y opcionalmente le reasigna un vehículo que era de Público general."""
    with transaccion() as cursor:
        cursor.execute(
            "INSERT INTO clientes (nombre, telefono, tipo_cliente) VALUES (%s, %s, %s)",
            (nombre, telefono, tipo_cliente),
        )
        id_cliente = cursor.lastrowid
        if matricula_publico:
            cursor.execute(
                "UPDATE vehiculos SET id_cliente = %s "
                "WHERE matricula = %s AND id_cliente = %s",
                (id_cliente, matricula_publico, ID_PUBLICO_GENERAL),
            )
        return id_cliente


def actualizar_cliente(id_cliente, nombre, telefono, tipo_cliente):
    return ejecutar(
        "UPDATE clientes SET nombre = %s, telefono = %s, tipo_cliente = %s "
        "WHERE id_cliente = %s",
        (nombre, telefono, tipo_cliente, id_cliente),
    )


def cliente_tiene_relaciones(id_cliente):
    """Indica si el cliente tiene vehículos o pensiones registradas."""
    filas = consultar(
        "SELECT "
        "(SELECT COUNT(*) FROM vehiculos WHERE id_cliente = %s) AS vehiculos, "
        "(SELECT COUNT(*) FROM pensiones WHERE id_cliente = %s) AS pensiones",
        (id_cliente, id_cliente),
    )
    datos = filas[0]
    return datos["vehiculos"] > 0 or datos["pensiones"] > 0


def eliminar_cliente(id_cliente):
    return ejecutar("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))


# ----------------------------------------------------------------- vehículos
def listar_vehiculos(filtro="", solo_publico=False):
    """Lista vehículos con el nombre de su cliente."""
    condiciones = []
    parametros = []

    if solo_publico:
        condiciones.append("v.id_cliente = %s")
        parametros.append(ID_PUBLICO_GENERAL)

    filtro = (filtro or "").strip()
    if filtro:
        patron = f"%{filtro}%"
        condiciones.append(
            "(v.matricula LIKE %s OR c.nombre LIKE %s OR IFNULL(v.marca, '') LIKE %s "
            "OR IFNULL(v.modelo, '') LIKE %s)"
        )
        parametros.extend([patron, patron, patron, patron])

    where = f"WHERE {' AND '.join(condiciones)} " if condiciones else ""
    return consultar(
        "SELECT v.matricula, v.id_cliente, c.nombre AS cliente, v.marca, v.modelo, v.color "
        "FROM vehiculos v "
        "JOIN clientes c ON c.id_cliente = v.id_cliente "
        f"{where}"
        "ORDER BY v.matricula ASC",
        tuple(parametros) if parametros else None,
    )


def listar_vehiculos_publico_general():
    """Devuelve los vehículos asignados actualmente a Público general."""
    return consultar(
        "SELECT matricula, marca, modelo, color "
        "FROM vehiculos WHERE id_cliente = %s ORDER BY matricula ASC",
        (ID_PUBLICO_GENERAL,),
    )


def buscar_vehiculo(matricula):
    filas = consultar(
        "SELECT matricula, id_cliente, marca, modelo, color "
        "FROM vehiculos WHERE matricula = %s",
        (matricula,),
    )
    return filas[0] if filas else None


def crear_vehiculo(matricula, id_cliente, marca, modelo, color):
    return insertar(
        "INSERT INTO vehiculos (matricula, id_cliente, marca, modelo, color) "
        "VALUES (%s, %s, %s, %s, %s)",
        (matricula, id_cliente, marca, modelo, color),
    )


def actualizar_vehiculo(matricula_original, matricula_nueva, id_cliente, marca, modelo, color):
    return ejecutar(
        "UPDATE vehiculos "
        "SET matricula = %s, id_cliente = %s, marca = %s, modelo = %s, color = %s "
        "WHERE matricula = %s",
        (matricula_nueva, id_cliente, marca, modelo, color, matricula_original),
    )


def vehiculo_tiene_historial(matricula):
    """Indica si el vehículo tiene estancias, pensiones o cobros asociados."""
    filas = consultar(
        "SELECT "
        "(SELECT COUNT(*) FROM detalle_servicios WHERE matricula = %s) AS servicios, "
        "(SELECT COUNT(*) FROM pensiones WHERE matricula = %s) AS pensiones, "
        "(SELECT COUNT(*) FROM detalle_cobros WHERE matricula = %s) AS cobros",
        (matricula, matricula, matricula),
    )
    datos = filas[0]
    return datos["servicios"] > 0 or datos["pensiones"] > 0 or datos["cobros"] > 0


def eliminar_vehiculo(matricula):
    return ejecutar("DELETE FROM vehiculos WHERE matricula = %s", (matricula,))