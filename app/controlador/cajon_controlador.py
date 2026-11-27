"""Reglas de los cajones: cuáles se pueden elegir en una entrada o en una pensión."""

from app.controlador.errores import ErrorServicio
from app.modelo import cajon_modelo as modelo


def total_cajones():
    total = modelo.total_cajones()
    if total is None:
        raise ErrorServicio("Falta configurar la cantidad de cajones (parámetro 'total_cajones').")
    return total


def libres_para_entrada(matricula=None):
    """Cajones sin vehículo dentro y sin pensión vigente de otro vehículo."""
    hoy = modelo.fecha_actual()
    no_disponibles = set(modelo.ocupados())
    no_disponibles.update(
        p["numero_cajon"] for p in modelo.apartados(hoy, hoy) if p["matricula"] != matricula
    )
    return [n for n in range(1, total_cajones() + 1) if n not in no_disponibles]


def cajon_fijo(matricula):
    """Cajón de la pensión vigente del vehículo.

    Devuelve (numero, ocupado_por): `numero` es None si no tiene pensión con cajón,
    y `ocupado_por` es la matrícula de otro vehículo que está en ese cajón, o None.
    """
    numero = modelo.cajon_de_pension_vigente(matricula)
    if numero is None:
        return None, None
    ocupante = modelo.ocupados().get(numero)
    return numero, ocupante if ocupante != matricula else None


def libres_para_pension(matricula, fecha_inicio, fecha_fin):
    """Cajones sin otra pensión en el periodo; si empieza ya, sin otro vehículo dentro."""
    no_disponibles = {p["numero_cajon"] for p in modelo.apartados(fecha_inicio, fecha_fin)}
    if fecha_inicio <= modelo.fecha_actual() <= fecha_fin:
        no_disponibles.update(n for n, ocupante in modelo.ocupados().items() if ocupante != matricula)
    return [n for n in range(1, total_cajones() + 1) if n not in no_disponibles]


def cajon_actual(matricula):
    """Cajón en el que está el vehículo ahora, o None."""
    return next((n for n, ocupante in modelo.ocupados().items() if ocupante == matricula), None)


def validar_cajon(texto, libres):
    """Convierte lo capturado en un número de cajón disponible."""
    texto = str(texto if texto is not None else "").strip()
    if not texto:
        raise ErrorServicio("Elige el cajón.")
    if not texto.isdecimal():
        raise ErrorServicio("El cajón debe ser un número.")
    numero = int(texto)
    total = total_cajones()
    if not 1 <= numero <= total:
        raise ErrorServicio(f"El cajón debe estar entre 1 y {total}.")
    if numero not in libres:
        raise ErrorServicio(f"El cajón {numero} no está disponible.")
    return numero
