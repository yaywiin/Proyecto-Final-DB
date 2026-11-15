"""Reglas de las entradas y salidas de vehículos.

La vista llama a estas funciones; si algo no se puede hacer lanzan ErrorServicio
con un mensaje listo para mostrar.
"""

from app.modelo import servicio_modelo as modelo

LONGITUD_MATRICULA = 15


class ErrorServicio(Exception):
    """Error de regla de negocio con un mensaje para el usuario."""


def normalizar_matricula(texto):
    matricula = "".join((texto or "").split()).upper()
    if not matricula:
        raise ErrorServicio("Escribe la matrícula del vehículo.")
    if len(matricula) > LONGITUD_MATRICULA:
        raise ErrorServicio(f"La matrícula admite máximo {LONGITUD_MATRICULA} caracteres.")
    if not matricula.isalnum():
        raise ErrorServicio("La matrícula solo puede llevar letras y números.")
    return matricula


def _limpiar(texto):
    texto = (texto or "").strip()
    return texto or None


def clientes_disponibles():
    return modelo.listar_clientes()


def vehiculos_dentro():
    return modelo.listar_dentro()


def consultar_vehiculo(matricula):
    """Devuelve el vehículo registrado o None, para que la vista sepa si pedir datos."""
    return modelo.buscar_vehiculo(normalizar_matricula(matricula))


def registrar_entrada(matricula, id_usuario, id_cliente=None, marca=None, modelo_veh=None, color=None):
    """Registra la entrada. Devuelve un resumen para mostrar al cobrador."""
    matricula = normalizar_matricula(matricula)

    if modelo.buscar_entrada_abierta(matricula):
        raise ErrorServicio(f"El vehículo {matricula} ya está dentro del estacionamiento.")

    vehiculo = modelo.buscar_vehiculo(matricula)
    vehiculo_nuevo = None
    if vehiculo is None:
        if id_cliente is None:
            raise ErrorServicio("Elige el cliente del vehículo nuevo.")
        vehiculo_nuevo = {
            "id_cliente": id_cliente,
            "marca": _limpiar(marca),
            "modelo": _limpiar(modelo_veh),
            "color": _limpiar(color),
        }

    modelo.registrar_entrada(matricula, id_usuario, vehiculo_nuevo)
    return {"matricula": matricula, "vehiculo_nuevo": vehiculo_nuevo is not None}


def registrar_salida(matricula):
    """Registra la salida del vehículo. Devuelve matrícula y fecha de salida."""
    matricula = normalizar_matricula(matricula)

    entrada = modelo.buscar_entrada_abierta(matricula)
    if entrada is None:
        raise ErrorServicio(f"El vehículo {matricula} no tiene una entrada abierta.")

    fecha_salida = modelo.registrar_salida(entrada["id_detalle_servicio"])
    return {
        "matricula": matricula,
        "fecha_entrada": entrada["fecha_entrada"],
        "fecha_salida": fecha_salida,
    }
