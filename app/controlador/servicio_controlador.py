"""Reglas de las entradas y salidas de vehículos.

La vista llama a estas funciones; si algo no se puede hacer lanzan ErrorServicio
con un mensaje listo para mostrar.
"""

from app.controlador import cajon_controlador as cajones
from app.controlador.errores import ErrorServicio
from app.modelo import servicio_modelo as modelo

LONGITUD_MATRICULA = 7


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


def registrar_entrada(matricula, id_usuario, cajon=None, id_cliente=None, marca=None, modelo_veh=None, color=None):
    """Registra la entrada. Devuelve un resumen para mostrar al cobrador.

    Un vehículo con pensión vigente entra a su cajón, sin importar `cajon`, salvo
    que otro vehículo lo esté ocupando.
    """
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

    fijo, ocupado_por = cajones.cajon_fijo(matricula)
    if fijo is not None and ocupado_por is None:
        numero = fijo
    else:
        numero = cajones.validar_cajon(cajon, cajones.libres_para_entrada(matricula))

    modelo.registrar_entrada(matricula, id_usuario, numero, vehiculo_nuevo)
    return {"matricula": matricula, "cajon": numero, "vehiculo_nuevo": vehiculo_nuevo is not None}


def previsualizar_salida(matricula):
    """Calcula lo que se va a cobrar, sin guardar nada.

    La hora de salida queda fijada aquí: es la misma que se guarda al confirmar,
    así el monto no cambia aunque el cobrador tarde en cobrar.
    """
    matricula = normalizar_matricula(matricula)

    entrada = modelo.buscar_entrada_abierta(matricula)
    if entrada is None:
        raise ErrorServicio(f"El vehículo {matricula} no tiene una entrada abierta.")

    fecha_salida = modelo.hora_actual()
    cobro = modelo.calcular_cobro(entrada["id_detalle_servicio"], fecha_salida)
    cobro["fecha_salida"] = fecha_salida
    cobro["numero_cajon"] = entrada["numero_cajon"]
    return cobro


def confirmar_salida(cobro, id_usuario):
    """Guarda la salida y el cobro calculados en `previsualizar_salida`. Devuelve el id del cobro."""
    id_cobro = modelo.guardar_salida_con_cobro(
        cobro["id_detalle_servicio"],
        cobro["matricula"],
        id_usuario,
        cobro["fecha_salida"],
        cobro["horas_cobradas"],
        cobro["monto"],
    )
    if id_cobro is None:
        raise ErrorServicio(f"La salida de {cobro['matricula']} ya estaba registrada.")
    return id_cobro


def formatear_tiempo(minutos):
    horas, resto = divmod(int(minutos), 60)
    return f"{horas} h {resto:02d} min" if horas else f"{resto} min"
