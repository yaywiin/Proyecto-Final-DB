"""Control centralizado de permisos por perfil (Issue #13)."""

MODULOS_ADMIN = (
    "Entradas y Salidas",
    "Cobros",
    "Estacionamiento",
    "Pensiones",
    "Clientes",
    "Vehículos",
    "Usuarios",
    "Reportes",
)

MODULOS_COBRADOR = (
    "Entradas y Salidas",
    "Cobros",
    "Estacionamiento",
    "Clientes",
    "Vehículos",
)

PERMISOS_POR_ROL = {
    "admin": MODULOS_ADMIN,
    "cobrador": MODULOS_COBRADOR,
}


def obtener_rol(usuario):
    """Devuelve el rol normalizado ('admin' o 'cobrador') del usuario en sesión."""
    if not isinstance(usuario, dict):
        return "cobrador"
    rol = usuario.get("rol") or usuario.get("perfil") or "cobrador"
    return str(rol).strip().lower()


def es_admin(usuario):
    """Indica si el usuario en sesión tiene perfil de administrador."""
    return obtener_rol(usuario) == "admin"


def tiene_permiso(usuario, modulo):
    """Verifica si el rol del usuario puede acceder al módulo indicado."""
    permitidos = PERMISOS_POR_ROL.get(obtener_rol(usuario), ())
    return modulo in permitidos


def filtrar_modulos(usuario, modulos):
    """Filtra la lista de (titulo, descripcion) dejando solo los permitidos al rol."""
    return [item for item in modulos if tiene_permiso(usuario, item[0])]