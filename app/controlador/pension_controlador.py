"""Reglas de las pensiones.

El precio por mes y el % de descuento salen de la tabla `parametros`
(`precio_pension_mensual` y `descuento_pension_2anios`), no del código.

Descuento: se aplica si el cliente tiene más de 2 años desde su primera pensión.
"""

import calendar
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from app.controlador.servicio_controlador import ErrorServicio, normalizar_matricula
from app.modelo import pension_modelo as modelo
from app.modelo import servicio_modelo

ID_PUBLICO_GENERAL = 1
MESES_MAXIMOS = 36
FORMATO_FECHA = "%Y-%m-%d"


def id_usuario(usuario):
    """El id puede venir como `id_usuario` (base de datos) o `usuario_id`."""
    return usuario.get("id_usuario", usuario.get("usuario_id"))


def sumar_meses(fecha, meses):
    """Misma fecha `meses` meses después (si el día no existe, el último del mes)."""
    indice = fecha.month - 1 + meses
    anio, mes = fecha.year + indice // 12, indice % 12 + 1
    return date(anio, mes, min(fecha.day, calendar.monthrange(anio, mes)[1]))


def fecha_fin(fecha_inicio, meses):
    """La pensión de N meses termina el día anterior al mismo día N meses después."""
    return sumar_meses(fecha_inicio, meses) - timedelta(days=1)


def _leer_numero(clave, descripcion):
    valor = modelo.leer_parametro(clave)
    if valor is None:
        raise ErrorServicio(f"Falta configurar {descripcion} (parámetro '{clave}').")
    try:
        return Decimal(valor)
    except ArithmeticError:
        raise ErrorServicio(f"El parámetro '{clave}' no es un número válido.")


def previsualizar_pension(matricula, texto_fecha, texto_meses):
    """Valida los datos y calcula la pensión, sin guardar nada."""
    matricula = normalizar_matricula(matricula)

    vehiculo = servicio_modelo.buscar_vehiculo(matricula)
    if vehiculo is None:
        raise ErrorServicio(f"El vehículo {matricula} no está registrado.")
    if vehiculo["id_cliente"] == ID_PUBLICO_GENERAL:
        raise ErrorServicio(
            "Las pensiones son solo para clientes registrados. "
            "Registra al cliente y asígnale el vehículo primero."
        )

    try:
        inicio = datetime.strptime((texto_fecha or "").strip(), FORMATO_FECHA).date()
    except ValueError:
        raise ErrorServicio("Escribe la fecha de inicio como AAAA-MM-DD, por ejemplo 2026-11-23.")

    try:
        meses = int((texto_meses or "").strip())
    except ValueError:
        raise ErrorServicio("Los meses deben ser un número entero.")
    if not 1 <= meses <= MESES_MAXIMOS:
        raise ErrorServicio(f"Los meses deben estar entre 1 y {MESES_MAXIMOS}.")

    fin = fecha_fin(inicio, meses)
    if modelo.hay_traslape(matricula, inicio, fin):
        raise ErrorServicio(f"El vehículo {matricula} ya tiene una pensión en esas fechas.")

    precio = _leer_numero("precio_pension_mensual", "el precio mensual de la pensión")
    descuento = _leer_numero("descuento_pension_2anios", "el descuento de la pensión")

    primera = modelo.primera_pension(vehiculo["id_cliente"])
    con_descuento = primera is not None and inicio > sumar_meses(primera, 24)
    porcentaje = descuento if con_descuento else Decimal(0)

    bruto = precio * meses
    monto = (bruto * (Decimal(100) - porcentaje) / Decimal(100)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return {
        "matricula": matricula,
        "id_cliente": vehiculo["id_cliente"],
        "cliente": vehiculo["cliente"],
        "fecha_inicio": inicio,
        "fecha_fin": fin,
        "meses": meses,
        "precio_mensual": precio,
        "descuento": porcentaje,
        "monto": monto,
    }


def confirmar_pension(pension, id_cobrador):
    """Guarda la pensión calculada en `previsualizar_pension`. Devuelve su id."""
    if modelo.hay_traslape(pension["matricula"], pension["fecha_inicio"], pension["fecha_fin"]):
        raise ErrorServicio(f"El vehículo {pension['matricula']} ya tiene una pensión en esas fechas.")
    id_pension, _id_cobro = modelo.contratar_pension(
        pension["id_cliente"],
        pension["matricula"],
        id_cobrador,
        pension["fecha_inicio"],
        pension["fecha_fin"],
        pension["monto"],
    )
    return id_pension


def listar_pensiones():
    return modelo.listar_pensiones()
