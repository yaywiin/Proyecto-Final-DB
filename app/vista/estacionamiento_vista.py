"""Ventana del croquis del estacionamiento (Issue #45).

Se abre desde el menú principal:

    from app.vista.estacionamiento_vista import abrir_estacionamiento
    abrir_estacionamiento(root, usuario)
"""

import math
import tkinter as tk

FONDO = "#0b0f19"
PANEL = "#111827"
CAMPO = "#1f2937"
ASFALTO = "#161e2e"
LINEA_CARRIL = "#374151"
DORADO = "#d4af37"
TEXTO = "#f3f4f6"
TEXTO_SUAVE = "#9ca3af"

# Colores por estado del cajón: (fondo, borde, texto)
COLORES_ESTADO = {
    "libre": ("#14532d", "#22c55e", "#dcfce7"),
    "ocupado": ("#7f1d1d", "#ef4444", "#fee2e2"),
    "pension": ("#4c1d95", "#a855f7", "#f3e8ff"),
}

# Datos provisionales mientras se integra Issue #44 (consulta real a BD)
TOTAL_CAJONES_DEMO = 20
CAJONES_POR_FILA_DEMO = 5


def _datos_demo(total_cajones=TOTAL_CAJONES_DEMO):
    """Genera datos de prueba con el formato acordado para Issue #44."""
    muestras = {
        2: ("ocupado", "ABC1234"),
        5: ("ocupado", "JKL4567"),
        7: ("pension", "MNP2345"),
        8: ("pension", "QRS8901"),
        12: ("ocupado", "XYZ7890"),
        15: ("pension", "K7P06V"),
        18: ("ocupado", "DEF3456"),
    }
    cajones = []
    for num in range(1, total_cajones + 1):
        estado, matricula = muestras.get(num, ("libre", None))
        cajones.append(
            {
                "numero": num,
                "estado": estado,
                "matricula": matricula,
            }
        )
    return cajones


def abrir_estacionamiento(parent, usuario=None):
    """Abre la ventana del croquis del estacionamiento."""
    return VentanaEstacionamiento(parent, usuario)


class VentanaEstacionamiento:
    def __init__(self, parent, usuario=None):
        self.usuario = usuario
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("CYC PARKING - Estacionamiento")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self._centrar(parent, 860, 660)

        self._crear_widgets()
        self.dibujar_croquis(
            cajones=_datos_demo(TOTAL_CAJONES_DEMO),
            total_cajones=TOTAL_CAJONES_DEMO,
            cajones_por_fila=CAJONES_POR_FILA_DEMO,
        )

    # ------------------------------------------------------------------ vista
    def _centrar(self, parent, ancho, alto):
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    def _crear_widgets(self):
        tk.Label(
            self.ventana,
            text="CROQUIS DEL ESTACIONAMIENTO",
            bg=FONDO,
            fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, padx=24, pady=(16, 8))

        # Espacio reservado arriba para la leyenda, el conteo y el botón "Actualizar" (Issue #44)
        self.barra_info = tk.Frame(self.ventana, bg=PANEL, height=48, padx=16, pady=10)
        self.barra_info.pack(fill=tk.X, padx=24, pady=(0, 12))
        self.barra_info.pack_propagate(False)

        # Contenedor del croquis
        contenedor = tk.Frame(self.ventana, bg=PANEL, padx=14, pady=14)
        contenedor.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 20))

        self.canvas = tk.Canvas(
            contenedor,
            width=784,
            height=504,
            bg=ASFALTO,
            highlightthickness=1,
            highlightbackground=LINEA_CARRIL,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------------------- croquis
    def dibujar_croquis(self, cajones, total_cajones, cajones_por_fila):
        """Dibuja el croquis en el Canvas con filas, pasillos, carril de vuelta y acceso.

        Parámetros:
            cajones: lista de dicts {"numero": int, "estado": str, "matricula": str | None}
            total_cajones: cantidad total de cajones del estacionamiento
            cajones_por_fila: cuántos cajones caben en cada fila
        """
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()
        if ancho_canvas < 100:
            ancho_canvas = 784
        if alto_canvas < 100:
            alto_canvas = 504

        cajones_por_fila = max(1, int(cajones_por_fila))
        total_cajones = max(len(cajones), int(total_cajones))
        num_filas = max(1, math.ceil(total_cajones / cajones_por_fila))

        # Indexar cajones por número (si falta alguno, se asume libre)
        mapa = {c["numero"]: c for c in cajones}

        # Márgenes y zonas del croquis
        margen_izq = 24
        margen_sup = 20
        margen_der = 22
        ancho_carril_vuelta = 86
        alto_acceso = 58
        alto_pasillo = 34
        separacion_cajon = 10

        zona_cajones_ancho = ancho_canvas - margen_izq - margen_der - ancho_carril_vuelta - 14
        zona_cajones_alto = alto_canvas - margen_sup - alto_acceso - 16

        ancho_cajon = (zona_cajones_ancho - separacion_cajon * (cajones_por_fila - 1)) / cajones_por_fila
        alto_cajon = (zona_cajones_alto - alto_pasillo * (num_filas - 1)) / num_filas
        alto_cajon = min(alto_cajon, 84)

        # Centrar el bloque de filas verticalmente sobre la zona de acceso
        altura_bloques = num_filas * alto_cajon + (num_filas - 1) * alto_pasillo
        inicio_y = margen_sup + max(0, (zona_cajones_alto - altura_bloques) / 2)

        # Carril de vuelta a la derecha
        carril_x1 = margen_izq + zona_cajones_ancho + 14
        carril_x2 = ancho_canvas - margen_der
        carril_y1 = inicio_y
        carril_y2 = alto_canvas - 16
        self.canvas.create_rectangle(
            carril_x1, carril_y1, carril_x2, carril_y2,
            fill="#111827", outline=LINEA_CARRIL, width=1,
        )
        carril_cx = (carril_x1 + carril_x2) / 2
        self.canvas.create_line(
            carril_cx, carril_y1 + 16, carril_cx, carril_y2 - 20,
            fill=LINEA_CARRIL, dash=(6, 6), width=2,
        )
        self.canvas.create_text(
            carril_cx,
            (carril_y1 + carril_y2) / 2,
            text="CARRIL\nDE\nVUELTA\n↓",
            fill=TEXTO_SUAVE,
            font=("Segoe UI", 8, "bold"),
            justify=tk.CENTER,
        )

        # Dibujar filas de cajones y pasillos entre ellas
        for fila in range(num_filas):
            y1 = inicio_y + fila * (alto_cajon + alto_pasillo)
            y2 = y1 + alto_cajon

            for col in range(cajones_por_fila):
                numero = fila * cajones_por_fila + col + 1
                if numero > total_cajones:
                    break

                datos = mapa.get(numero, {"numero": numero, "estado": "libre", "matricula": None})
                estado = str(datos.get("estado", "libre")).lower()
                matricula = datos.get("matricula") or ""
                fondo_c, borde_c, texto_c = COLORES_ESTADO.get(estado, COLORES_ESTADO["libre"])

                x1 = margen_izq + col * (ancho_cajon + separacion_cajon)
                x2 = x1 + ancho_cajon
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fondo_c, outline=borde_c, width=2,
                )

                if estado in ("ocupado", "pension") and matricula:
                    self.canvas.create_text(
                        cx, cy - 11,
                        text=f"C-{numero:02d}",
                        fill=texto_c,
                        font=("Segoe UI", 10, "bold"),
                    )
                    self.canvas.create_text(
                        cx, cy + 12,
                        text=matricula,
                        fill=TEXTO,
                        font=("Segoe UI", 9, "bold"),
                    )
                else:
                    self.canvas.create_text(
                        cx, cy,
                        text=f"C-{numero:02d}",
                        fill=texto_c,
                        font=("Segoe UI", 11, "bold"),
                    )

            # Pasillo entre filas
            if fila < num_filas - 1:
                py = y2 + alto_pasillo / 2
                self.canvas.create_line(
                    margen_izq, py, carril_x1 - 4, py,
                    fill=LINEA_CARRIL, dash=(8, 6), width=1,
                )
                self.canvas.create_text(
                    margen_izq + zona_cajones_ancho / 2,
                    py,
                    text=f"PASILLO {fila + 1}  →",
                    fill=TEXTO_SUAVE,
                    font=("Segoe UI", 7, "bold"),
                )

        # Zona de acceso abajo
        acceso_y1 = alto_canvas - alto_acceso
        acceso_y2 = alto_canvas - 16
        acceso_x1 = margen_izq
        acceso_x2 = carril_x1 - 8
        self.canvas.create_rectangle(
            acceso_x1, acceso_y1, acceso_x2, acceso_y2,
            fill="#111827", outline=DORADO, width=1,
        )
        self.canvas.create_text(
            (acceso_x1 + acceso_x2) / 2,
            (acceso_y1 + acceso_y2) / 2,
            text="▲   ACCESO / SALIDA   ▼",
            fill=DORADO,
            font=("Segoe UI", 9, "bold"),
        )