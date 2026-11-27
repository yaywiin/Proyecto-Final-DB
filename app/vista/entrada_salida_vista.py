"""Ventana de entradas y salidas de vehículos.

Se abre desde el menú principal:

    from app.vista.entrada_salida_vista import abrir_entrada_salida
    abrir_entrada_salida(root, usuario)
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.controlador import cajon_controlador as cajones
from app.controlador import servicio_controlador as controlador
from app.controlador.servicio_controlador import ErrorServicio
from app.modelo.conexion import ErrorBD
from app.vista.estilo import CAMPO, DORADO, FONDO, PANEL, PLACEHOLDER, TEXTO, TEXTO_SUAVE
from app.vista.selector_cajon import SelectorCajon
from app.vista.validaciones import es_solo_texto

COLORES_VEHICULO = (
    "Blanco", "Negro", "Gris", "Plata", "Rojo",
    "Azul", "Verde", "Amarillo", "Café", "Beige",
    "Naranja", "Vino", "Dorado", "Otro",
)


class EntryConPlaceholder(tk.Entry):
    """Entry con un texto de ejemplo en gris.

    El ejemplo es una etiqueta encima del campo, así que nunca entra en la
    variable: un campo vacío sigue valiendo "".
    """

    def __init__(self, padre, variable, ejemplo, **opciones):
        super().__init__(padre, textvariable=variable, **opciones)
        self._variable = variable
        self._ejemplo = tk.Label(
            self, text=ejemplo, bg=CAMPO, fg=PLACEHOLDER, font=opciones.get("font"), cursor="xterm",
        )
        self._ejemplo.place(x=2, rely=0.5, anchor=tk.W)
        self._ejemplo.bind("<Button-1>", lambda e: self.focus_set())
        self._variable.trace_add("write", lambda *_: self._actualizar())
        self.bind("<FocusIn>", lambda e: self._actualizar(enfocado=True), add="+")
        self.bind("<FocusOut>", lambda e: self._actualizar(enfocado=False), add="+")
        self._actualizar()

    def configure(self, cnf=None, **opciones):
        resultado = super().configure(cnf, **opciones)
        if hasattr(self, "_ejemplo"):
            self._actualizar()
        return resultado

    config = configure

    def _actualizar(self, enfocado=None):
        if enfocado is None:
            enfocado = self.focus_get() is self
        visible = not self._variable.get() and not enfocado and str(self.cget("state")) == "normal"
        if visible:
            self._ejemplo.place(x=2, rely=0.5, anchor=tk.W)
        else:
            self._ejemplo.place_forget()


def abrir_entrada_salida(parent, usuario):
    """Abre la ventana. `usuario` es el diccionario del usuario con sesión iniciada."""
    return VentanaEntradaSalida(parent, usuario)


def _id_usuario(usuario):
    return usuario.get("usuario_id", usuario.get("id_usuario"))


class VentanaEntradaSalida:
    def __init__(self, parent, usuario):
        self.id_usuario = _id_usuario(usuario)
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("CYC PARKING - Entradas y Salidas")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self._centrar(parent, 860, 660)

        self.var_matricula = tk.StringVar()
        self.var_cliente = tk.StringVar()
        self.var_marca = tk.StringVar()
        self.var_modelo = tk.StringVar()
        self.var_color = tk.StringVar()
        self.var_cajon = tk.StringVar()
        self.var_estado = tk.StringVar(value="Escribe una matrícula y presiona Enter.")
        self.clientes = {}
        self._pendiente = None

        self._crear_widgets()
        self._cargar_clientes()
        self._actualizar_lista()
        self.entry_matricula.focus()

    # ------------------------------------------------------------------ vista
    def _centrar(self, parent, ancho, alto):
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    def _etiqueta(self, padre, texto):
        tk.Label(padre, text=texto, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(anchor=tk.W)

    def _campo(self, padre, variable, ejemplo, limite=None, solo_letras=False):
        opciones = {}
        if limite or solo_letras:
            def _validar(texto):
                if limite and len(texto) > limite:
                    return False
                if solo_letras and not es_solo_texto(texto):
                    return False
                return True

            opciones = {
                "validate": "key",
                "validatecommand": (self.ventana.register(_validar), "%P"),
            }
        entry = EntryConPlaceholder(
            padre, variable, ejemplo, bg=CAMPO, fg=TEXTO, insertbackground=TEXTO,
            relief=tk.FLAT, font=("Segoe UI", 10), **opciones,
        )
        entry.pack(fill=tk.X, ipady=4, pady=(2, 10))
        return entry

    def _boton(self, padre, texto, comando, dorado=False):
        return tk.Button(
            padre, text=texto, command=comando, relief=tk.FLAT, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=12, pady=6,
            bg=DORADO if dorado else CAMPO, fg=FONDO if dorado else TEXTO,
            activebackground="#e5c158" if dorado else "#374151",
            activeforeground=FONDO if dorado else TEXTO,
        )

    def _crear_widgets(self):
        tk.Label(
            self.ventana, text="ENTRADAS Y SALIDAS", bg=FONDO, fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, padx=24, pady=(18, 8))

        cuerpo = tk.Frame(self.ventana, bg=FONDO)
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 18))

        # Panel izquierdo: formulario
        form = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16, width=280)
        form.pack(side=tk.LEFT, fill=tk.Y)
        form.pack_propagate(False)

        self._etiqueta(form, "Matrícula")
        self.entry_matricula = self._campo(form, self.var_matricula, "Ej. ABC1234", limite=controlador.LONGITUD_MATRICULA)
        self.entry_matricula.bind("<Return>", lambda e: self._al_confirmar_matricula())
        self.entry_matricula.bind("<FocusOut>", lambda e: self._verificar_vehiculo())
        self.entry_matricula.bind("<KeyRelease>", self._al_escribir_matricula)

        tk.Label(
            form, textvariable=self.var_estado, bg=PANEL, fg=DORADO, justify=tk.LEFT,
            wraplength=240, font=("Segoe UI", 8),
        ).pack(anchor=tk.W, pady=(0, 10))

        self._etiqueta(form, "Cajón")
        self.selector = SelectorCajon(form, self.var_cajon, self._cajones_libres)
        self.selector.pack(fill=tk.X, pady=(2, 6))
        self.selector.al_confirmar(self._al_confirmar_cajon)

        self._etiqueta(form, "Cliente (solo si el vehículo es nuevo)")
        self.combo_cliente = ttk.Combobox(
            form, textvariable=self.var_cliente, state="readonly", postcommand=self._cargar_clientes,
        )
        self.combo_cliente.pack(fill=tk.X, ipady=3, pady=(2, 10))

        self._etiqueta(form, "Marca")
        self.entry_marca = self._campo(form, self.var_marca, "Ej. Nissan")
        self._etiqueta(form, "Modelo")
        self.entry_modelo = self._campo(form, self.var_modelo, "Ej. Versa")

        self._etiqueta(form, "Color")
        self.combo_color = ttk.Combobox(
            form,
            textvariable=self.var_color,
            values=COLORES_VEHICULO,
            state="readonly",
        )
        self.combo_color.pack(fill=tk.X, ipady=3, pady=(2, 10))

        self._boton(form, "Registrar entrada", self._registrar_entrada, dorado=True).pack(fill=tk.X, pady=(4, 6))
        self._boton(form, "Registrar salida", self._registrar_salida).pack(fill=tk.X)
        self._habilitar_datos_nuevo(True)

        # Panel derecho: vehículos dentro
        lista = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))

        encabezado = tk.Frame(lista, bg=PANEL)
        encabezado.pack(fill=tk.X)
        tk.Label(
            encabezado, text="Dentro ahora", bg=PANEL, fg=TEXTO, font=("Segoe UI", 10, "bold"),
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

        self.tabla = ttk.Treeview(
            lista, columns=("cajon", "matricula", "cliente", "entrada"), show="headings",
            style="Parking.Treeview", selectmode="browse", height=14,
        )
        for columna, titulo, ancho in (
            ("cajon", "Cajón", 60), ("matricula", "Matrícula", 90),
            ("cliente", "Cliente", 130), ("entrada", "Entrada", 130),
        ):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor="center")
        self.tabla.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # ----------------------------------------------------------------- lógica
    def _habilitar_datos_nuevo(self, activo):
        estado = "normal" if activo else "disabled"
        estado_combo = "readonly" if activo else "disabled"
        self.combo_cliente.config(state=estado_combo)
        self.combo_color.config(state=estado_combo)
        for entry in (self.entry_marca, self.entry_modelo):
            entry.config(state=estado)

    def _cargar_clientes(self):
        """Lee los clientes de la base. También se llama al desplegar la lista."""
        elegido = self.var_cliente.get()
        try:
            filas = controlador.clientes_disponibles()
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return
        self.clientes = {f"{f['nombre']} (#{f['id_cliente']})": f["id_cliente"] for f in filas}
        self.combo_cliente["values"] = list(self.clientes)
        if elegido in self.clientes:
            self.var_cliente.set(elegido)
        elif self.clientes:
            self.var_cliente.set(next(iter(self.clientes)))

    def _actualizar_lista(self):
        try:
            filas = controlador.vehiculos_dentro()
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return
        self.tabla.delete(*self.tabla.get_children())
        for fila in filas:
            self.tabla.insert(
                "", tk.END, iid=fila["matricula"],
                values=(
                    fila["numero_cajon"] or "—", fila["matricula"], fila["cliente"],
                    fila["fecha_entrada"].strftime("%d/%m/%Y %H:%M"),
                ),
            )
        self.lbl_total.config(text=f"{len(filas)} vehículo(s)")

    def _al_escribir_matricula(self, _evento):
        """Comprueba la matrícula poco después de dejar de escribir."""
        if self._pendiente:
            self.ventana.after_cancel(self._pendiente)
        self._pendiente = self.ventana.after(400, self._verificar_vehiculo)

    def _al_seleccionar(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion:
            self.var_matricula.set(seleccion[0])
            self._verificar_vehiculo()

    def _verificar_vehiculo(self):
        """Dice si la matrícula ya está registrada y pide datos solo si es nueva."""
        self._pendiente = None
        if not self.var_matricula.get().strip():
            self.var_estado.set("Escribe una matrícula y presiona Enter.")
            self._habilitar_datos_nuevo(True)
            self.selector.liberar()
            return None
        try:
            vehiculo = controlador.consultar_vehiculo(self.var_matricula.get())
        except ErrorServicio as error:
            self.var_estado.set(str(error))
            self._habilitar_datos_nuevo(True)
            self.selector.liberar()
            return None
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return None

        if vehiculo:
            self.var_estado.set(f"Vehículo registrado. Cliente: {vehiculo['cliente']}.")
            self._habilitar_datos_nuevo(False)
        else:
            self.var_estado.set("Vehículo nuevo: elige el cliente y captura sus datos.")
            self._habilitar_datos_nuevo(True)
        self._preparar_cajon()
        return vehiculo

    def _matricula_capturada(self):
        return controlador.normalizar_matricula(self.var_matricula.get())

    def _cajones_libres(self):
        try:
            matricula = self._matricula_capturada()
        except ErrorServicio:
            matricula = None
        return cajones.libres_para_entrada(matricula)

    def _preparar_cajon(self):
        """Si el vehículo tiene pensión, pone su cajón; si no, deja elegirlo."""
        try:
            numero, ocupado_por = cajones.cajon_fijo(self._matricula_capturada())
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return
        if numero is not None and ocupado_por is None:
            self.selector.fijar(numero, f"Pensión vigente: cajón {numero}.")
            return
        self.selector.liberar()
        if numero is not None:
            self.selector.pista.config(text=f"Su cajón {numero} lo ocupa {ocupado_por}. Elige otro.")

    def _al_confirmar_matricula(self):
        """Enter en la matrícula: revisa el vehículo y pasa al cajón si hay que elegirlo."""
        self._verificar_vehiculo()
        if not self.selector.fijo:
            self.selector.enfocar()

    def _al_confirmar_cajon(self):
        """Enter en el cajón: registra; si el vehículo es nuevo, pasa a sus datos."""
        vehiculo = self._verificar_vehiculo()
        if vehiculo:
            self._registrar_entrada()
        else:
            self.entry_marca.focus_set()

    def _limpiar_formulario(self):
        for variable in (self.var_matricula, self.var_marca, self.var_modelo, self.var_color):
            variable.set("")
        self.selector.limpiar()
        self._habilitar_datos_nuevo(True)
        self.var_estado.set("Escribe una matrícula y presiona Enter.")
        self.entry_matricula.focus()

    def _registrar_entrada(self):
        if not self.var_matricula.get().strip():
            messagebox.showwarning("Entrada", "Ingresa la matrícula del vehículo.", parent=self.ventana)
            return

        mat = "".join(self.var_matricula.get().split())
        if len(mat) < 5 or not mat.isalnum() or not (any(c.isalpha() for c in mat) and any(c.isdigit() for c in mat)):
            messagebox.showwarning(
                "Entrada",
                "Ingresa una matrícula válida (mínimo 5 caracteres con letras y números, ej. ABC1234).",
                parent=self.ventana,
            )
            return

        vehiculo = self._verificar_vehiculo()
        if vehiculo is None:
            if (
                not self.clientes.get(self.var_cliente.get())
                or not self.var_marca.get().strip()
                or not self.var_modelo.get().strip()
                or not self.var_color.get().strip()
            ):
                messagebox.showwarning(
                    "Entrada",
                    "Para un vehículo nuevo debes llenar cliente, marca, modelo y color.",
                    parent=self.ventana,
                )
                return

            marca = self.var_marca.get().strip()
            if not es_solo_texto(marca):
                messagebox.showwarning(
                    "Entrada",
                    "La marca no puede llevar números ni otros símbolos.",
                    parent=self.ventana,
                )
                return

        try:
            resultado = controlador.registrar_entrada(
                self.var_matricula.get(),
                self.id_usuario,
                cajon=self.var_cajon.get(),
                id_cliente=self.clientes.get(self.var_cliente.get()),
                marca=self.var_marca.get(),
                modelo_veh=self.var_modelo.get(),
                color=self.var_color.get(),
            )
        except ErrorServicio as error:
            messagebox.showwarning("Entrada", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._actualizar_lista()
        self._limpiar_formulario()
        self.var_estado.set(f"Entrada registrada: {resultado['matricula']}, cajón {resultado['cajon']}.")

    def _registrar_salida(self):
        try:
            cobro = controlador.previsualizar_salida(self.var_matricula.get())
        except ErrorServicio as error:
            messagebox.showwarning("Salida", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        if not CuadroCobro(self.ventana, cobro).confirmado:
            self.var_estado.set(f"Salida de {cobro['matricula']} cancelada.")
            return

        try:
            controlador.confirmar_salida(cobro, self.id_usuario)
        except ErrorServicio as error:
            messagebox.showwarning("Salida", str(error), parent=self.ventana)
            self._actualizar_lista()
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._actualizar_lista()
        self._limpiar_formulario()
        self.var_estado.set(
            f"Cobro registrado: {cobro['matricula']}, ${cobro['monto']:,.2f}."
        )


class CuadroCobro:
    """Ventana modal con el detalle del cobro. `confirmado` dice si se presionó Cobrar."""

    def __init__(self, parent, cobro):
        self.confirmado = False
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Cobro")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)

        panel = tk.Frame(self.ventana, bg=PANEL, padx=28, pady=22)
        panel.pack(padx=24, pady=24)

        tk.Label(
            panel, text=cobro["matricula"], bg=PANEL, fg=TEXTO, font=("Segoe UI", 16, "bold"),
        ).pack(anchor=tk.W)
        tk.Label(
            panel, text=f"{cobro['cliente']}  •  {cobro['motivo']}", bg=PANEL, fg=TEXTO_SUAVE,
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, pady=(0, 14))

        for titulo, valor in (
            ("Cajón", str(cobro["numero_cajon"] or "—")),
            ("Entrada", cobro["fecha_entrada"].strftime("%d/%m/%Y %H:%M")),
            ("Salida", cobro["fecha_salida"].strftime("%d/%m/%Y %H:%M")),
            ("Tiempo", controlador.formatear_tiempo(cobro["minutos_estancia"])),
        ):
            fila = tk.Frame(panel, bg=PANEL)
            fila.pack(fill=tk.X, pady=2)
            tk.Label(fila, text=titulo, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            tk.Label(fila, text=valor, bg=PANEL, fg=TEXTO, font=("Segoe UI", 9)).pack(side=tk.RIGHT)

        tk.Label(
            panel, text="TOTAL A COBRAR", bg=PANEL, fg=DORADO, font=("Segoe UI", 8, "bold"),
        ).pack(anchor=tk.W, pady=(18, 0))
        tk.Label(
            panel, text=f"${cobro['monto']:,.2f}", bg=PANEL, fg=DORADO, font=("Segoe UI", 30, "bold"),
        ).pack(anchor=tk.W, pady=(0, 16))

        botones = tk.Frame(panel, bg=PANEL)
        botones.pack(fill=tk.X)
        for texto, comando, dorado in (("Cobrar", self._cobrar, True), ("Cancelar", self._cancelar, False)):
            tk.Button(
                botones, text=texto, command=comando, relief=tk.FLAT, cursor="hand2",
                font=("Segoe UI", 10, "bold"), padx=14, pady=6,
                bg=DORADO if dorado else CAMPO, fg=FONDO if dorado else TEXTO,
                activebackground="#e5c158" if dorado else "#374151",
                activeforeground=FONDO if dorado else TEXTO,
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8) if dorado else 0)

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