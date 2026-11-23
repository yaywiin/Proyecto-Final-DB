"""Ventana de pensiones (solo para el administrador).

Se abre desde el menú principal:

    from app.vista.pensiones_vista import abrir_pensiones
    abrir_pensiones(root, usuario)
"""

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from app.controlador import pension_controlador as controlador
from app.controlador.permisos import es_admin
from app.controlador.servicio_controlador import LONGITUD_MATRICULA, ErrorServicio
from app.modelo.conexion import ErrorBD
from app.vista.entrada_salida_vista import (
    CAMPO, DORADO, FONDO, PANEL, PLACEHOLDER, TEXTO, TEXTO_SUAVE, EntryConPlaceholder,
)


def abrir_pensiones(parent, usuario):
    """Abre la ventana si el usuario es admin; si no, avisa y no abre nada."""
    if not es_admin(usuario):
        messagebox.showwarning("Pensiones", "Esta sección es solo para el administrador.", parent=parent)
        return None
    return VentanaPensiones(parent, usuario)


def _boton(padre, texto, comando, dorado=False):
    return tk.Button(
        padre, text=texto, command=comando, relief=tk.FLAT, cursor="hand2",
        font=("Segoe UI", 10, "bold"), padx=14, pady=6,
        bg=DORADO if dorado else CAMPO, fg=FONDO if dorado else TEXTO,
        activebackground="#e5c158" if dorado else "#374151",
        activeforeground=FONDO if dorado else TEXTO,
    )


def _fecha(valor):
    return valor.strftime("%d/%m/%Y")


class VentanaPensiones:
    def __init__(self, parent, usuario):
        self.id_usuario = controlador.id_usuario(usuario)
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("CYC PARKING - Pensiones")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self._centrar(parent, 900, 560)

        self.var_matricula = tk.StringVar()
        self.var_fecha = tk.StringVar(value=date.today().strftime(controlador.FORMATO_FECHA))
        self.var_meses = tk.StringVar(value="1")
        self.var_estado = tk.StringVar(value="Escribe la matrícula del vehículo.")

        self._crear_widgets()
        self._actualizar_lista()
        self.entry_matricula.focus()

    # ------------------------------------------------------------------ vista
    def _centrar(self, parent, ancho, alto):
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    def _etiqueta(self, padre, texto):
        tk.Label(padre, text=texto, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(anchor=tk.W)

    def _campo(self, padre, variable, ejemplo, limite=None):
        opciones = {}
        if limite:
            opciones = {
                "validate": "key",
                "validatecommand": (self.ventana.register(lambda texto: len(texto) <= limite), "%P"),
            }
        entry = EntryConPlaceholder(
            padre, variable, ejemplo, bg=CAMPO, fg=TEXTO, insertbackground=TEXTO,
            relief=tk.FLAT, font=("Segoe UI", 10), **opciones,
        )
        entry.pack(fill=tk.X, ipady=4, pady=(2, 10))
        return entry

    def _crear_widgets(self):
        tk.Label(
            self.ventana, text="PENSIONES", bg=FONDO, fg=DORADO, font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, padx=24, pady=(18, 8))

        cuerpo = tk.Frame(self.ventana, bg=FONDO)
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 18))

        form = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16, width=270)
        form.pack(side=tk.LEFT, fill=tk.Y)
        form.pack_propagate(False)

        self._etiqueta(form, "Matrícula")
        self.entry_matricula = self._campo(form, self.var_matricula, "Ej. ABC1234", limite=LONGITUD_MATRICULA)
        self.entry_matricula.bind("<Return>", lambda e: self._contratar())

        self._etiqueta(form, "Fecha de inicio (AAAA-MM-DD)")
        self._campo(form, self.var_fecha, "Ej. 2026-11-23")

        self._etiqueta(form, "Meses")
        self._campo(form, self.var_meses, "Ej. 1", limite=2)

        tk.Label(
            form, textvariable=self.var_estado, bg=PANEL, fg=DORADO, justify=tk.LEFT,
            wraplength=230, font=("Segoe UI", 8),
        ).pack(anchor=tk.W, pady=(0, 12))

        _boton(form, "Contratar pensión", self._contratar, dorado=True).pack(fill=tk.X)

        lista = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))
        encabezado = tk.Frame(lista, bg=PANEL)
        encabezado.pack(fill=tk.X)
        tk.Label(
            encabezado, text="Pensiones registradas", bg=PANEL, fg=TEXTO, font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT)
        self.lbl_total = tk.Label(encabezado, text="", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9))
        self.lbl_total.pack(side=tk.RIGHT)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Parking.Treeview", background=CAMPO, fieldbackground=CAMPO, foreground=TEXTO,
            rowheight=26, borderwidth=0,
        )
        estilo.configure(
            "Parking.Treeview.Heading", background=PANEL, foreground=DORADO,
            font=("Segoe UI", 9, "bold"), borderwidth=0,
        )
        estilo.map("Parking.Treeview", background=[("selected", DORADO)], foreground=[("selected", FONDO)])

        columnas = (
            ("matricula", "Matrícula", 80), ("cliente", "Cliente", 120), ("inicio", "Inicio", 85),
            ("fin", "Fin", 85), ("monto", "Monto", 80), ("estado", "Estado", 80),
        )
        self.tabla = ttk.Treeview(
            lista, columns=[c[0] for c in columnas], show="headings", style="Parking.Treeview",
            selectmode="browse", height=14,
        )
        for clave, titulo, ancho in columnas:
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, anchor="center")
        self.tabla.tag_configure("Vencida", foreground=PLACEHOLDER)
        self.tabla.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    # ----------------------------------------------------------------- lógica
    def _actualizar_lista(self):
        try:
            filas = controlador.listar_pensiones()
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return
        self.tabla.delete(*self.tabla.get_children())
        for fila in filas:
            self.tabla.insert(
                "", tk.END, tags=(fila["estado"],),
                values=(
                    fila["matricula"], fila["cliente"], _fecha(fila["fecha_inicio"]),
                    _fecha(fila["fecha_fin"]), f"${fila['monto']:,.2f}", fila["estado"],
                ),
            )
        self.lbl_total.config(text=f"{len(filas)} pensión(es)")

    def _contratar(self):
        try:
            pension = controlador.previsualizar_pension(
                self.var_matricula.get(), self.var_fecha.get(), self.var_meses.get()
            )
        except ErrorServicio as error:
            messagebox.showwarning("Pensión", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        if not CuadroPension(self.ventana, pension).confirmado:
            self.var_estado.set(f"Pensión de {pension['matricula']} cancelada.")
            return

        try:
            controlador.confirmar_pension(pension, self.id_usuario)
        except ErrorServicio as error:
            messagebox.showwarning("Pensión", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._actualizar_lista()
        self.var_matricula.set("")
        self.var_meses.set("1")
        self.var_estado.set(f"Pensión registrada: {pension['matricula']}, ${pension['monto']:,.2f}.")
        self.entry_matricula.focus()


class CuadroPension:
    """Ventana modal con el detalle de la pensión. `confirmado` dice si se presionó Cobrar."""

    def __init__(self, parent, pension):
        self.confirmado = False
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Cobro de pensión")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)

        panel = tk.Frame(self.ventana, bg=PANEL, padx=28, pady=22)
        panel.pack(padx=24, pady=24)

        tk.Label(
            panel, text=pension["matricula"], bg=PANEL, fg=TEXTO, font=("Segoe UI", 16, "bold"),
        ).pack(anchor=tk.W)
        tk.Label(
            panel, text=f"{pension['cliente']}  •  Pensión mensual", bg=PANEL, fg=TEXTO_SUAVE,
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, pady=(0, 14))

        filas = [
            ("Inicio", _fecha(pension["fecha_inicio"])),
            ("Fin", _fecha(pension["fecha_fin"])),
            ("Meses", str(pension["meses"])),
            ("Precio por mes", f"${pension['precio_mensual']:,.2f}"),
        ]
        if pension["descuento"] > 0:
            filas.append(("Descuento (más de 2 años)", f"{pension['descuento'].normalize():f}%"))
        for titulo, valor in filas:
            fila = tk.Frame(panel, bg=PANEL)
            fila.pack(fill=tk.X, pady=2)
            tk.Label(fila, text=titulo, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            tk.Label(fila, text=valor, bg=PANEL, fg=TEXTO, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=(24, 0))

        tk.Label(
            panel, text="TOTAL A COBRAR", bg=PANEL, fg=DORADO, font=("Segoe UI", 8, "bold"),
        ).pack(anchor=tk.W, pady=(18, 0))
        tk.Label(
            panel, text=f"${pension['monto']:,.2f}", bg=PANEL, fg=DORADO, font=("Segoe UI", 30, "bold"),
        ).pack(anchor=tk.W, pady=(0, 16))

        botones = tk.Frame(panel, bg=PANEL)
        botones.pack(fill=tk.X)
        _boton(botones, "Cobrar", self._cobrar, dorado=True).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        _boton(botones, "Cancelar", self._cancelar).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.ventana.bind("<Return>", lambda e: self._cobrar())
        self.ventana.bind("<Escape>", lambda e: self._cancelar())
        self.ventana.protocol("WM_DELETE_WINDOW", self._cancelar)

        self.ventana.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.ventana.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.ventana.winfo_height()) // 2
        self.ventana.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        self.ventana.grab_set()
        self.ventana.focus_force()
        self.ventana.wait_window()

    def _cobrar(self):
        self.confirmado = True
        self.ventana.destroy()

    def _cancelar(self):
        self.ventana.destroy()
