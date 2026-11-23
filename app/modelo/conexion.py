"""Conexión a la base de datos (MariaDB / XAMPP).

Es el único módulo que abre conexiones. El resto del modelo usa estas funciones:

    from app.modelo.conexion import consultar, ejecutar, insertar, transaccion

    filas = consultar("SELECT * FROM clientes WHERE id_cliente = %s", (1,))
    nuevo_id = insertar("INSERT INTO clientes (nombre) VALUES (%s)", ("Ana",))
    filas_afectadas = ejecutar("UPDATE clientes SET telefono = %s WHERE id_cliente = %s", ("555", 2))

    # Varias sentencias que deben guardarse todas o ninguna:
    with transaccion() as cur:
        cur.execute("UPDATE servicios SET fecha_salida = NOW() WHERE id_servicio = %s", (5,))
        cur.execute("INSERT INTO cobros (id_servicio, id_usuario, monto) VALUES (%s, %s, %s)", (5, 1, 90))

Siempre se pasan los valores como parámetros (%s), nunca pegados al texto del SQL.
"""

from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor

try:
    from app import config
except ImportError as error:  # pragma: no cover
    raise ImportError(
        "Falta app/config.py. Cópialo de la plantilla: cp app/config.example.py app/config.py"
    ) from error


class ErrorBD(Exception):
    """Error de base de datos con un mensaje que dice qué hacer."""


# Códigos de error de MySQL/MariaDB que conviene explicar mejor.
_NO_SE_PUDO_CONECTAR = 2003
_BASE_NO_EXISTE = 1049
_ACCESO_DENEGADO = 1045

# Errores que ocurren al ejecutar una sentencia (no al conectar).
_TABLA_NO_EXISTE = 1146
_RUTINA_NO_EXISTE = 1305
_ERROR_DE_REGLA = 1644  # SIGNAL de un trigger o procedimiento: el mensaje ya está en español
_LLAVE_DUPLICADA = 1062
_CONEXION_PERDIDA = (2006, 2013)
_RELACION_LLAVE_FORANEA = (1451, 1452)


def _explicar(error):
    """Convierte un error de MySQL/MariaDB en un mensaje que dice qué hacer."""
    codigo = error.args[0] if error.args else None
    detalle = error.args[1] if len(error.args) > 1 else str(error)
    if codigo == _ERROR_DE_REGLA:
        return detalle
    if codigo in (_RUTINA_NO_EXISTE, _TABLA_NO_EXISTE):
        return (
            "A la base de datos le falta una parte. Vuelve a correr los scripts de database/ "
            f"en orden (01 al 05). Detalle: {detalle}"
        )
    if codigo == _LLAVE_DUPLICADA:
        return "Ese registro ya existe."
    if codigo in _RELACION_LLAVE_FORANEA:
        return "El registro está relacionado con otros datos y no se puede guardar o eliminar así."
    if codigo in _CONEXION_PERDIDA:
        return "Se perdió la conexión con MySQL. Revisa que siga encendido en XAMPP."
    return f"Error de la base de datos ({codigo}): {detalle}"


def obtener_conexion():
    """Abre una conexión nueva. Quien la pide es responsable de cerrarla."""
    try:
        return pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
        )
    except pymysql.err.OperationalError as error:
        codigo = error.args[0] if error.args else None
        if codigo == _NO_SE_PUDO_CONECTAR:
            raise ErrorBD(
                f"No se pudo conectar a MySQL en {config.DB_HOST}:{config.DB_PORT}. "
                "Enciende MySQL en XAMPP (botón Start)."
            ) from error
        if codigo == _BASE_NO_EXISTE:
            raise ErrorBD(
                f"La base '{config.DB_NAME}' no existe. "
                "Créala corriendo los scripts de database/ (ver docs/Guia_Inicio.md)."
            ) from error
        if codigo == _ACCESO_DENEGADO:
            raise ErrorBD(
                f"MySQL rechazó el usuario '{config.DB_USER}'. "
                "Revisa DB_USER y DB_PASSWORD en app/config.py."
            ) from error
        raise ErrorBD(f"Error al conectar con la base de datos: {error}") from error


@contextmanager
def transaccion():
    """Entrega un cursor. Si todo sale bien confirma; si algo falla, deshace todo."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            yield cursor
        conexion.commit()
    except pymysql.err.MySQLError as error:
        conexion.rollback()
        raise ErrorBD(_explicar(error)) from error
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def consultar(sql, parametros=None):
    """Ejecuta un SELECT y devuelve una lista de diccionarios (una por fila)."""
    with transaccion() as cursor:
        cursor.execute(sql, parametros)
        return list(cursor.fetchall())


def ejecutar(sql, parametros=None):
    """Ejecuta un INSERT/UPDATE/DELETE y devuelve cuántas filas afectó."""
    with transaccion() as cursor:
        return cursor.execute(sql, parametros)


def insertar(sql, parametros=None):
    """Ejecuta un INSERT y devuelve el id autogenerado de la fila nueva."""
    with transaccion() as cursor:
        cursor.execute(sql, parametros)
        return cursor.lastrowid
