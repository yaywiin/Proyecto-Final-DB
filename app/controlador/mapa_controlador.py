"""Datos del mapa del estacionamiento (croquis de cajones).

    from app.controlador.mapa_controlador import estado_del_mapa

    mapa = estado_del_mapa()
    mapa["total_cajones"], mapa["cajones_por_fila"]
    mapa["conteo"]    # {"libre": 17, "ocupado": 2, "pension": 1}
    mapa["cajones"]   # un diccionario por cajón, del 1 al total

Cada cajón trae:
    numero         número del cajón
    estado         "libre", "ocupado" o "pension"
    matricula      del vehículo que lo ocupa o del pensionado; None si está libre
    cliente        nombre del cliente; None si está libre
    hora_entrada   datetime en que entró el vehículo que está ahí, o None
    pension_hasta  fecha en que termina la pensión que lo aparta, o None
    dentro         True si el vehículo de `matricula` está en el cajón
    apartado_para  matrícula del pensionado cuando otro vehículo ocupa su cajón, o None
"""

from app.controlador import cajon_controlador
from app.modelo import cajon_modelo as modelo

ESTADOS = ("libre", "ocupado", "pension")
POR_FILA_PREDETERMINADO = 5


def _cajon(numero, estancia, pension):
    """Decide cómo se ve un cajón según quién está y quién lo tiene apartado."""
    cajon = {
        "numero": numero, "estado": "libre", "matricula": None, "cliente": None,
        "hora_entrada": None, "pension_hasta": None, "dentro": False, "apartado_para": None,
    }
    if pension:
        cajon["pension_hasta"] = pension["fecha_fin"]
    if estancia:
        cajon.update(
            matricula=estancia["matricula"], cliente=estancia["cliente"],
            hora_entrada=estancia["fecha_entrada"], dentro=True,
        )
        if pension and pension["matricula"] == estancia["matricula"]:
            cajon["estado"] = "pension"
        else:
            # Físicamente no hay lugar, aunque esté apartado para alguien más.
            cajon["estado"] = "ocupado"
            if pension:
                cajon["apartado_para"] = pension["matricula"]
    elif pension:
        cajon.update(estado="pension", matricula=pension["matricula"], cliente=pension["cliente"])
    return cajon


def estado_del_mapa():
    """Estado de todos los cajones en este momento."""
    total = cajon_controlador.total_cajones()
    estancias = {e["numero_cajon"]: e for e in modelo.estancias_abiertas()}
    pensiones = {p["numero_cajon"]: p for p in modelo.pensiones_vigentes()}
    cajones = [_cajon(n, estancias.get(n), pensiones.get(n)) for n in range(1, total + 1)]
    return {
        "total_cajones": total,
        "cajones_por_fila": modelo.parametro_cajones_por_fila() or POR_FILA_PREDETERMINADO,
        "conteo": {estado: sum(c["estado"] == estado for c in cajones) for estado in ESTADOS},
        "cajones": cajones,
    }
