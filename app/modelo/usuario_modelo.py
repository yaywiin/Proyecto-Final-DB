"""Acceso a la base de datos para la gestión de usuarios."""

from app.modelo.conexion import consultar, ejecutar, insertar


def listar_usuarios(filtro=""):
    """Devuelve todos los usuarios, filtrando opcionalmente por nombre o usuario."""
    filtro = (filtro or "").strip()
    if filtro:
        patron = f"%{filtro}%"
        return consultar(
            "SELECT id_usuario, nombre, usuario, rol, activo "
            "FROM usuarios "
            "WHERE nombre LIKE %s OR usuario LIKE %s "
            "ORDER BY activo DESC, id_usuario ASC",
            (patron, patron),
        )
    return consultar(
        "SELECT id_usuario, nombre, usuario, rol, activo "
        "FROM usuarios "
        "ORDER BY activo DESC, id_usuario ASC"
    )


def buscar_por_id(id_usuario):
    """Devuelve un usuario por su id, o None si no existe."""
    filas = consultar(
        "SELECT id_usuario, nombre, usuario, rol, activo "
        "FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
    )
    return filas[0] if filas else None


def buscar_por_usuario(username):
    """Devuelve un usuario por su nombre de acceso, o None si no existe."""
    filas = consultar(
        "SELECT id_usuario, nombre, usuario, rol, activo "
        "FROM usuarios WHERE usuario = %s",
        (username,),
    )
    return filas[0] if filas else None


def contar_admins_activos():
    """Cuenta cuántos administradores activos existen en el sistema."""
    filas = consultar(
        "SELECT COUNT(*) AS total FROM usuarios WHERE rol = 'admin' AND activo = 1"
    )
    return filas[0]["total"] if filas else 0


def crear_usuario(nombre, usuario, password_hash, rol):
    """Inserta un usuario nuevo y devuelve su id_usuario."""
    return insertar(
        "INSERT INTO usuarios (nombre, usuario, password, rol, activo) "
        "VALUES (%s, %s, %s, %s, 1)",
        (nombre, usuario, password_hash, rol),
    )


def actualizar_usuario(id_usuario, nombre, usuario, rol, password_hash=None):
    """Actualiza los datos de un usuario. Solo cambia la contraseña si se envía."""
    if password_hash:
        return ejecutar(
            "UPDATE usuarios SET nombre = %s, usuario = %s, rol = %s, password = %s "
            "WHERE id_usuario = %s",
            (nombre, usuario, rol, password_hash, id_usuario),
        )
    return ejecutar(
        "UPDATE usuarios SET nombre = %s, usuario = %s, rol = %s "
        "WHERE id_usuario = %s",
        (nombre, usuario, rol, id_usuario),
    )


def cambiar_estado(id_usuario, activo):
    """Activa (1) o da de baja lógica (0) a un usuario."""
    return ejecutar(
        "UPDATE usuarios SET activo = %s WHERE id_usuario = %s",
        (1 if activo else 0, id_usuario),
    )