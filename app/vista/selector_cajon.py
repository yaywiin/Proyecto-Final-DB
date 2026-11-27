"""Selector de cajón: se puede escribir y filtra los cajones libres."""

import tkinter as tk
from tkinter import ttk

from app.controlador.errores import ErrorServicio
from app.modelo.conexion import ErrorBD
from app.vista.estilo import PANEL, TEXTO_SUAVE

MAXIMO_EN_PISTA = 8


class SelectorCajon(tk.Frame):
    """Lista desplegable con escritura y una línea con los cajones que coinciden.

    `obtener_libres` es una función sin argumentos que devuelve los números libres.
    Se llama al desplegar la lista y al escribir.
    """

    def __init__(self, padre, variable, obtener_libres):
        super().__init__(padre, bg=PANEL)
        self.variable = variable
        self.obtener_libres = obtener_libres
        self.fijo = False
        self.combo = ttk.Combobox(
            self, textvariable=variable, postcommand=self.recargar,
            validate="key", validatecommand=(self.register(self._validar), "%P"),
        )
        self.combo.pack(fill=tk.X, ipady=3)
        self.pista = tk.Label(self, text="", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8), anchor=tk.W)
        self.pista.pack(fill=tk.X)
        self.combo.bind("<KeyRelease>", self._al_escribir)

    @staticmethod
    def _validar(texto):
        return texto == "" or (texto.isdecimal() and len(texto) <= 3)

    def _al_escribir(self, evento):
        if evento.keysym not in ("Return", "Tab", "Escape"):
            self.recargar()

    def recargar(self):
        """Vuelve a leer los cajones libres y filtra según lo escrito."""
        if self.fijo:
            return
        try:
            libres = [str(numero) for numero in self.obtener_libres()]
        except (ErrorServicio, ErrorBD) as error:
            self.combo["values"] = []
            self.pista.config(text=str(error), wraplength=230, justify=tk.LEFT)
            return
        escrito = self.variable.get()
        # Con un cajón ya elegido se muestran todos, para poder cambiarlo.
        coinciden = libres if escrito in libres else [n for n in libres if n.startswith(escrito)]
        self.combo["values"] = coinciden
        self.pista.config(text=self._describir(escrito, libres, coinciden))

    @staticmethod
    def _describir(escrito, libres, coinciden):
        if not libres:
            return "No hay cajones libres."
        if escrito in libres:
            return f"Cajón {escrito} libre."
        if not coinciden:
            return f"El cajón {escrito} no está disponible."
        texto = ", ".join(coinciden[:MAXIMO_EN_PISTA])
        resto = "…" if len(coinciden) > MAXIMO_EN_PISTA else ""
        return f"Libres: {texto}{resto}"

    def fijar(self, numero, nota):
        """Deja el cajón puesto y bloqueado (vehículos con pensión)."""
        self.fijo = True
        self.variable.set(str(numero))
        self.combo.config(state="disabled")
        self.pista.config(text=nota)

    def liberar(self):
        """Vuelve a dejar elegir; borra el cajón que estaba fijo."""
        if self.fijo:
            self.fijo = False
            self.variable.set("")
            self.combo.config(state="normal")
            self.pista.config(text="")

    def limpiar(self):
        self.liberar()
        self.variable.set("")
        self.pista.config(text="")

    def enfocar(self):
        self.combo.focus_set()

    def al_confirmar(self, funcion):
        self.combo.bind("<Return>", lambda e: funcion())
