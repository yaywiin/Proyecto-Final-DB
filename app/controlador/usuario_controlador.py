"""Reglas de negocio para la gestión de usuarios (Issue #9)."""

from app.controlador.login_controlador import cifrar_password
from app.modelo import usuario_modelo as modelo

LONGITUD_NOMBRE = 100
LONGITUD_USUARIO = 30
MIN_PASSWORD = 4
ROLES_VALIDOS = ("admin", "cobrador")


class ErrorUsuario(Exception):
    """Error de regla de negocio con un mensaje listo para mostrar en la vista."""


def listar_usuarios(filtro=""):
    return modelo.listar_usuarios(filtro)


def _validar_datos_basicos(nombre, usuario, rol):
    nombre = (nombre or "").strip()
    usuario = (usuario or "").strip()
    rol = (rol or "").strip().lower()

    if not nombre:
        raise ErrorUsuario("Escribe el nombre completo del usuario.")
    if len(nombre) > LONGITUD_NOMBRE:
        raise ErrorUsuario(f"El nombre admite máximo {LONGITUD_NOMBRE} caracteres.")

    if not usuario:
        raise ErrorUsuario("Escribe el nombre de usuario para iniciar sesión.")
    if " " in usuario:
        raise ErrorUsuario("El nombre de usuario no puede contener espacios.")
    if len(usuario) > LONGITUD_USUARIO:
        raise ErrorUsuario(f"El usuario admite máximo {LONGITUD_USUARIO} caracteres.")

    if rol not in ROLES_VALIDOS:
        raise ErrorUsuario("Selecciona un rol válido (admin o cobrador).")

    return nombre, usuario, rol


def crear_usuario(nombre, usuario, password, rol):
    """Valida y registra un usuario nuevo en la base de datos."""
    nombre, usuario, rol = _validar_datos_basicos(nombre, usuario, rol)
    password = password or ""

    if len(password) < MIN_PASSWORD:
        raise ErrorUsuario(f"La contraseña debe tener al menos {MIN_PASSWORD} caracteres.")

    if modelo.buscar_por_usuario(usuario):
        raise ErrorUsuario(f"El usuario '{usuario}' ya existe. Elige otro.")

    password_hash = cifrar_password(password)
    return modelo.crear_usuario(nombre, usuario, password_hash, rol)


def actualizar_usuario(id_usuario, nombre, usuario, rol, password, id_admin_actual):
    """Valida y actualiza un usuario existente. La contraseña es opcional."""
    actual = modelo.buscar_por_id(id_usuario)
    if actual is None:
        raise ErrorUsuario("El usuario seleccionado ya no existe.")

    nombre, usuario, rol = _validar_datos_basicos(nombre, usuario, rol)

    existente = modelo.buscar_por_usuario(usuario)
    if existente and existente["id_usuario"] != id_usuario:
        raise ErrorUsuario(f"El usuario '{usuario}' ya está en uso por otra cuenta.")

    # Evitar que el administrador actual se quite el rol o deje el sistema sin admins
    if actual["rol"] == "admin" and rol != "admin":
        if id_usuario == id_admin_actual:
            raise ErrorUsuario("No puedes cambiar tu propio rol de administrador.")
        if actual["activo"] == 1 and modelo.contar_admins_activos() <= 1:
            raise ErrorUsuario("Debe quedar al menos un administrador activo en el sistema.")

    password_hash = None
    if password:
        if len(password) < MIN_PASSWORD:
            raise ErrorUsuario(f"La nueva contraseña debe tener al menos {MIN_PASSWORD} caracteres.")
        password_hash = cifrar_password(password)

    modelo.actualizar_usuario(id_usuario, nombre, usuario, rol, password_hash)


def cambiar_estado_usuario(id_usuario, activo, id_admin_actual):
    """Da de baja lógica (activo=0) o reactiva (activo=1) a un usuario."""
    actual = modelo.buscar_por_id(id_usuario)
    if actual is None:
        raise ErrorUsuario("El usuario seleccionado ya no existe.")

    if not activo:
        if id_usuario == id_admin_actual:
            raise ErrorUsuario("No puedes dar de baja tu propia cuenta mientras tienes sesión iniciada.")
        if actual["rol"] == "admin" and actual["activo"] == 1 and modelo.contar_admins_activos() <= 1:
            raise ErrorUsuario("No puedes desactivar al último administrador activo.")

    modelo.cambiar_estado(id_usuario, activo)