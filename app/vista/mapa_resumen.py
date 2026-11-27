"""Piezas para la ventana del croquis: leyenda con conteo, botón y recuadro.

Uso dentro de la ventana del croquis (`canvas` es donde se dibuja):

    from app.controlador.mapa_controlador import estado_del_mapa
    from app.vista.mapa_resumen import COLORES, RecuadroCajon, ResumenCajones

    self.resumen = ResumenCajones(self.ventana, al_actualizar=self.dibujar)
    self.resumen.pack(fill=tk.X)
    self.recuadro = RecuadroCajon(canvas)

    def dibujar(self):
        mapa = estado_del_mapa()
        canvas.delete("all")
        for cajon in mapa["cajones"]:
            etiqueta = f"cajon{cajon['numero']}"
            # dibujar el rectángulo y los textos con tags=(etiqueta,)
            # y fill=COLORES[cajon["estado"]]
            self.recuadro.conectar(etiqueta, cajon)
        self.resumen.mostrar(mapa)
"""

import tkinter as tk

from app.vista.estilo import CAMPO, DORADO, FONDO, PANEL, TEXTO, TEXTO_SUAVE

COLORES = {"libre": "#16a34a", "ocupado": "#ef4444", "pension": "#a855f7"}
NOMBRES = (("libre", "libres"), ("ocupado", "ocupados"), ("pension", "de pensión"))


class ResumenCajones(tk.Frame):
    """Leyenda de colores con el conteo de cada estado y el botón "Actualizar"."""

    def __init__(self, padre, al_actualizar):
        super().__init__(padre, bg=PANEL, padx=18, pady=10)
        self.conteos = {}
        for estado, nombre in NOMBRES:
            tk.Frame(self, bg=COLORES[estado], width=14, height=14).pack(side=tk.LEFT, padx=(0, 8))
            numero = tk.Label(self, text="0", bg=PANEL, fg=TEXTO, font=("Segoe UI", 16, "bold"))
            numero.pack(side=tk.LEFT)
            tk.Label(self, text=nombre, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(
                side=tk.LEFT, padx=(6, 24),
            )
            self.conteos[estado] = numero
        tk.Button(
            self, text="Actualizar", command=al_actualizar, relief=tk.FLAT, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=14, pady=4, bg=DORADO, fg=FONDO,
            activebackground="#e5c158", activeforeground=FONDO,
        ).pack(side=tk.RIGHT)

    def mostrar(self, mapa):
        for estado, etiqueta in self.conteos.items():
            etiqueta.config(text=str(mapa["conteo"][estado]))


def texto_recuadro(cajon):
    """Lo que dice el recuadro de un cajón."""
    titulos = {"libre": "Libre", "ocupado": "Ocupado", "pension": "Pensión"}
    lineas = [f"Cajón {cajon['numero']}  •  {titulos[cajon['estado']]}"]
    if cajon["matricula"]:
        lineas.append(f"{cajon['matricula']}  •  {cajon['cliente']}")
    if cajon["hora_entrada"]:
        lineas.append(f"Entrada: {cajon['hora_entrada']:%d/%m/%Y %H:%M}")
    if cajon["estado"] == "pension":
        lineas.append(f"Pensión hasta: {cajon['pension_hasta']:%d/%m/%Y}")
        lineas.append("Vehículo dentro" if cajon["dentro"] else "Vehículo fuera")
    if cajon["apartado_para"]:
        lineas.append(f"Apartado para {cajon['apartado_para']}")
    return "\n".join(lineas)


class RecuadroCajon:
    """Recuadro con los datos del cajón mientras el cursor está encima."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.etiqueta = tk.Label(
            canvas, bg=CAMPO, fg=TEXTO, justify=tk.LEFT, font=("Segoe UI", 9), padx=10, pady=6,
            highlightbackground=DORADO, highlightthickness=1,
        )

    def conectar(self, tag, cajon):
        """Muestra los datos de `cajon` sobre los dibujos del canvas con ese `tag`."""
        texto = texto_recuadro(cajon)
        self.canvas.tag_bind(tag, "<Enter>", lambda e: self._mostrar(texto, e))
        self.canvas.tag_bind(tag, "<Motion>", lambda e: self._mostrar(texto, e))
        self.canvas.tag_bind(tag, "<Leave>", lambda e: self.ocultar())

    def _mostrar(self, texto, evento):
        self.etiqueta.config(text=texto)
        self.etiqueta.update_idletasks()
        ancho, alto = self.etiqueta.winfo_reqwidth(), self.etiqueta.winfo_reqheight()
        x, y = evento.x + 16, evento.y + 16
        # Si no cabe a la derecha o abajo, se pone del otro lado del cursor.
        if x + ancho > self.canvas.winfo_width():
            x = evento.x - ancho - 12
        if y + alto > self.canvas.winfo_height():
            y = evento.y - alto - 12
        self.etiqueta.place(x=max(x, 0), y=max(y, 0))

    def ocultar(self):
        self.etiqueta.place_forget()
