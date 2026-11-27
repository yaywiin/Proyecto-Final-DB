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
from app.vista.entrada_salida_vista import EntryConPlaceholder
from app.vista.estilo import CAMPO, DORADO, FONDO, PANEL, PLACEHOLDER, TEXTO, TEXTO_SUAVE
from app.vista.selector_cajon import SelectorCajon


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
        self._centrar(parent, 940, 580)

        self.var_matricula = tk.StringVar()
        self.var_fecha = tk.StringVar(value=date.today().strftime(controlador.FORMATO_FECHA))
        self.var_meses = tk.StringVar(value="1")
        self.var_cajon = tk.StringVar()
        self.var_estado = tk.StringVar(value="Escribe la matrícula del vehículo.")

        self._crear_widgets()
        for variable in (self.var_matricula, self.var_fecha, self.var_meses):
            variable.trace_add("write", lambda *_: self._revisar_cajon())
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
        self.entry_matricula.bind("<Return>", lambda e: self._al_confirmar_matricula())

        self._etiqueta(form, "Fecha de inicio (AAAA-MM-DD)")
        self._campo(form, self.var_fecha, "Ej. 2026-11-23")

        self._etiqueta(form, "Meses")
        self._campo(form, self.var_meses, "Ej. 1", limite=2)

        self._etiqueta(form, "Cajón")
        self.selector = SelectorCajon(form, self.var_cajon, self._cajones_libres)
        self.selector.pack(fill=tk.X, pady=(2, 8))
        self.selector.al_confirmar(self._contratar)

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
            ("cajon", "Cajón", 50), ("matricula", "Matrícula", 75), ("cliente", "Cliente", 105),
            ("inicio", "Inicio", 80), ("fin", "Fin", 80), ("monto", "Monto", 75), ("estado", "Estado", 75),
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
                    fila["numero_cajon"] or "—", fila["matricula"], fila["cliente"], _fecha(fila["fecha_inicio"]),
                    _fecha(fila["fecha_fin"]), f"${fila['monto']:,.2f}", fila["estado"],
                ),
            )
        self.lbl_total.config(text=f"{len(filas)} pensión(es)")

    def _cajones_libres(self):
        return controlador.cajones_disponibles(
            self.var_matricula.get(), self.var_fecha.get(), self.var_meses.get()
        )

    def _revisar_cajon(self, proponer=True):
        """Ajusta el selector según si el vehículo está dentro.

        Dentro y con la pensión desde hoy: su cajón queda puesto y bloqueado. Dentro y con
        la pensión para después: solo se propone. En otro caso se deja elegir.
        """
        datos = (self.var_matricula.get(), self.var_fecha.get(), self.var_meses.get())
        try:
            numero = controlador.cajon_obligado(*datos)
            if numero is not None:
                if numero in self._cajones_libres():
                    nota = f"Está dentro: su pensión va en el cajón {numero}."
                else:
                    nota = f"Está en el cajón {numero}, no disponible en esas fechas. Registra su salida."
                self.selector.fijar(numero, nota)
                return
            self.selector.liberar()
            if proponer:
                self._sugerir_cajon()
        except ErrorServicio:
            self.selector.liberar()  # Datos incompletos: se avisará al contratar
        except ErrorBD as error:
            self.selector.liberar()
            self.selector.pista.config(text=str(error))

    def _sugerir_cajon(self):
        """Si el vehículo ya está dentro y no se ha elegido cajón, propone el suyo."""
        if self.var_cajon.get():
            return
        numero = controlador.cajon_sugerido(self.var_matricula.get())
        if numero is not None and numero in self._cajones_libres():
            self.var_cajon.set(str(numero))
            self.selector.pista.config(text=f"El vehículo está en el cajón {numero}.")

    def _al_confirmar_matricula(self):
        self._revisar_cajon()
        if not self.selector.fijo:
            self.selector.enfocar()

    def _contratar(self):
        self._revisar_cajon(proponer=False)  # Pudo entrar o salir desde que se escribió
        try:
            pension = controlador.previsualizar_pension(
                self.var_matricula.get(), self.var_fecha.get(), self.var_meses.get(), self.var_cajon.get()
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
        self.selector.limpiar()
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
            ("Cajón", str(pension["cajon"])),
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
