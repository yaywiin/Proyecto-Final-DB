"""Reglas de negocio para la gestión de clientes y vehículos (Issue #12)."""

from app.modelo import cliente_vehiculo_modelo as modelo
from app.modelo.cliente_vehiculo_modelo import ID_PUBLICO_GENERAL

LONGITUD_NOMBRE = 100
LONGITUD_TELEFONO = 20
LONGITUD_MATRICULA = 15
LONGITUD_MARCA = 40
LONGITUD_MODELO = 40
LONGITUD_COLOR = 30
TIPOS_CLIENTE = ("paso", "frecuente")


class ErrorClienteVehiculo(Exception):
    """Error de regla de negocio con mensaje listo para mostrar en la vista."""


def _limpiar(texto):
    texto = (texto or "").strip()
    return texto or None


def normalizar_matricula(texto):
    matricula = "".join((texto or "").split()).upper()
    if not matricula:
        raise ErrorClienteVehiculo("Escribe la matrícula del vehículo.")
    if len(matricula) > LONGITUD_MATRICULA:
        raise ErrorClienteVehiculo(f"La matrícula admite máximo {LONGITUD_MATRICULA} caracteres.")
    if not matricula.isalnum():
        raise ErrorClienteVehiculo("La matrícula solo puede llevar letras y números.")
    return matricula


# ------------------------------------------------------------------ clientes
def listar_clientes(filtro=""):
    return modelo.listar_clientes(filtro)


def vehiculos_publico_general():
    return modelo.listar_vehiculos_publico_general()


def _validar_cliente(nombre, telefono, tipo_cliente):
    nombre = (nombre or "").strip()
    telefono = _limpiar(telefono)
    tipo_cliente = (tipo_cliente or "").strip().lower()

    if not nombre:
        raise ErrorClienteVehiculo("Escribe el nombre del cliente.")
    if len(nombre) > LONGITUD_NOMBRE:
        raise ErrorClienteVehiculo(f"El nombre admite máximo {LONGITUD_NOMBRE} caracteres.")
    if telefono and len(telefono) > LONGITUD_TELEFONO:
        raise ErrorClienteVehiculo(f"El teléfono admite máximo {LONGITUD_TELEFONO} caracteres.")
    if tipo_cliente not in TIPOS_CLIENTE:
        raise ErrorClienteVehiculo("Selecciona un tipo de cliente válido (paso o frecuente).")

    return nombre, telefono, tipo_cliente


def crear_cliente(nombre, telefono, tipo_cliente, matricula_publico=None):
    nombre, telefono, tipo_cliente = _validar_cliente(nombre, telefono, tipo_cliente)
    return modelo.crear_cliente(nombre, telefono, tipo_cliente, matricula_publico)


def actualizar_cliente(id_cliente, nombre, telefono, tipo_cliente):
    actual = modelo.buscar_cliente_por_id(id_cliente)
    if actual is None:
        raise ErrorClienteVehiculo("El cliente seleccionado ya no existe.")
    if id_cliente == ID_PUBLICO_GENERAL:
        raise ErrorClienteVehiculo("El registro base 'Público general' no se puede modificar.")

    nombre, telefono, tipo_cliente = _validar_cliente(nombre, telefono, tipo_cliente)
    modelo.actualizar_cliente(id_cliente, nombre, telefono, tipo_cliente)


def eliminar_cliente(id_cliente):
    if id_cliente == ID_PUBLICO_GENERAL:
        raise ErrorClienteVehiculo("No se puede eliminar el registro base 'Público general'.")
    if modelo.buscar_cliente_por_id(id_cliente) is None:
        raise ErrorClienteVehiculo("El cliente seleccionado ya no existe.")
    if modelo.cliente_tiene_relaciones(id_cliente):
        raise ErrorClienteVehiculo(
            "No se puede eliminar este cliente porque tiene vehículos o pensiones registradas. "
            "Reasigna o elimina primero sus vehículos."
        )
    modelo.eliminar_cliente(id_cliente)


# ----------------------------------------------------------------- vehículos
def listar_vehiculos(filtro="", solo_publico=False):
    return modelo.listar_vehiculos(filtro, solo_publico=solo_publico)


def _validar_vehiculo(matricula, id_cliente, marca, modelo_veh, color):
    matricula = normalizar_matricula(matricula)
    if id_cliente is None or modelo.buscar_cliente_por_id(id_cliente) is None:
        raise ErrorClienteVehiculo("Selecciona un cliente válido para el vehículo.")

    marca = _limpiar(marca)
    modelo_veh = _limpiar(modelo_veh)
    color = _limpiar(color)

    if marca and len(marca) > LONGITUD_MARCA:
        raise ErrorClienteVehiculo(f"La marca admite máximo {LONGITUD_MARCA} caracteres.")
    if modelo_veh and len(modelo_veh) > LONGITUD_MODELO:
        raise ErrorClienteVehiculo(f"El modelo admite máximo {LONGITUD_MODELO} caracteres.")
    if color and len(color) > LONGITUD_COLOR:
        raise ErrorClienteVehiculo(f"El color admite máximo {LONGITUD_COLOR} caracteres.")

    return matricula, id_cliente, marca, modelo_veh, color


def crear_vehiculo(matricula, id_cliente, marca, modelo_veh, color):
    matricula, id_cliente, marca, modelo_veh, color = _validar_vehiculo(
        matricula, id_cliente, marca, modelo_veh, color
    )
    if modelo.buscar_vehiculo(matricula):
        raise ErrorClienteVehiculo(f"La matrícula {matricula} ya está registrada.")
    modelo.crear_vehiculo(matricula, id_cliente, marca, modelo_veh, color)


def actualizar_vehiculo(matricula_original, matricula_nueva, id_cliente, marca, modelo_veh, color):
    if modelo.buscar_vehiculo(matricula_original) is None:
        raise ErrorClienteVehiculo("El vehículo seleccionado ya no existe.")

    matricula_nueva, id_cliente, marca, modelo_veh, color = _validar_vehiculo(
        matricula_nueva, id_cliente, marca, modelo_veh, color
    )
    if matricula_nueva != matricula_original and modelo.buscar_vehiculo(matricula_nueva):
        raise ErrorClienteVehiculo(f"La matrícula {matricula_nueva} ya pertenece a otro vehículo.")

    modelo.actualizar_vehiculo(
        matricula_original, matricula_nueva, id_cliente, marca, modelo_veh, color
    )


def eliminar_vehiculo(matricula):
    if modelo.buscar_vehiculo(matricula) is None:
        raise ErrorClienteVehiculo("El vehículo seleccionado ya no existe.")
    if modelo.vehiculo_tiene_historial(matricula):
        raise ErrorClienteVehiculo(
            f"No se puede eliminar {matricula} porque tiene estancias, pensiones o cobros registrados."
        )
    modelo.eliminar_vehiculo(matricula)