"""Validaciones de captura que comparten los formularios."""

SIGNOS_PERMITIDOS = " .-'’"  # "Ma. José", "Mercedes-Benz", "O'Brien"


def es_solo_texto(texto):
    """True si está vacío o empieza con letra y solo lleva letras, espacios, puntos, guiones o apóstrofos."""
    inicio = texto.lstrip()[:1]
    if inicio and not inicio.isalpha():
        return False
    return all(c.isalpha() or c in SIGNOS_PERMITIDOS for c in texto)
