"""Ventana de gestión de clientes y vehículos (Issue #12).

Se abre desde el menú principal:

    from app.vista.cliente_vehiculo_vista import abrir_clientes_vehiculos
    abrir_clientes_vehiculos(root, usuario, pestana="clientes")
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.controlador import cliente_vehiculo_controlador as controlador
from app.controlador.cliente_vehiculo_controlador import ErrorClienteVehiculo
from app.modelo.conexion import ErrorBD
from app.vista.validaciones import es_solo_texto

FONDO = "#0b0f19"
PANEL = "#111827"
CAMPO = "#1f2937"
DORADO = "#d4af37"
TEXTO = "#f3f4f6"
TEXTO_SUAVE = "#9ca3af"
PELIGRO = "#7f1d1d"
PELIGRO_HOVER = "#991b1b"
COLORES_VEHICULO = (
    "Blanco", "Negro", "Gris", "Plata", "Rojo",
    "Azul", "Verde", "Amarillo", "Café", "Beige",
    "Naranja", "Vino", "Dorado", "Otro",
)


def abrir_clientes_vehiculos(parent, usuario=None, pestana="clientes"):
    """Abre la ventana en la pestaña 'clientes' o 'vehiculos'."""
    return VentanaClientesVehiculos(parent, usuario, pestana=pestana)


class VentanaClientesVehiculos:
    def __init__(self, parent, usuario=None, pestana="clientes"):
        self.usuario = usuario
        self.cliente_seleccionado = None
        self.vehiculo_seleccionado = None

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("CYC PARKING - Clientes y Vehículos")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self._centrar(parent, 920, 640)

        # Variables pestaña Clientes
        self.var_cli_modo = tk.StringVar(value="Nuevo cliente")
        self.var_cli_nombre = tk.StringVar()
        self.var_cli_telefono = tk.StringVar()
        self.var_cli_tipo = tk.StringVar(value="paso")
        self.var_cli_vehiculo_pg = tk.StringVar(value="Ninguno")
        self.var_cli_buscar = tk.StringVar()

        # Variables pestaña Vehículos
        self.var_veh_modo = tk.StringVar(value="Nuevo vehículo")
        self.var_veh_matricula = tk.StringVar()
        self.var_veh_cliente = tk.StringVar()
        self.var_veh_marca = tk.StringVar()
        self.var_veh_modelo = tk.StringVar()
        self.var_veh_color = tk.StringVar()
        self.var_veh_buscar = tk.StringVar()
        self.var_solo_publico = tk.BooleanVar(value=False)

        self._clientes_por_id = {}
        self._clientes_combo = {}
        self._vehiculos_pg_combo = {}
        self._vehiculos_por_mat = {}

        self._configurar_estilos()
        self._crear_widgets()
        self._refrescar_todo()

        if pestana == "vehiculos":
            self.notebook.select(self.tab_vehiculos)

    # ------------------------------------------------------------------ vista
    def _centrar(self, parent, ancho, alto):
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Parking.TNotebook", background=FONDO, borderwidth=0)
        estilo.configure(
            "Parking.TNotebook.Tab",
            background=PANEL,
            foreground=TEXTO_SUAVE,
            padding=(16, 8),
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        estilo.map(
            "Parking.TNotebook.Tab",
            background=[("selected", DORADO)],
            foreground=[("selected", FONDO)],
        )
        estilo.configure(
            "Parking.Treeview",
            background=CAMPO,
            fieldbackground=CAMPO,
            foreground=TEXTO,
            rowheight=26,
            borderwidth=0,
        )
        estilo.configure(
            "Parking.Treeview.Heading",
            background=PANEL,
            foreground=DORADO,
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        estilo.map(
            "Parking.Treeview",
            background=[("selected", DORADO)],
            foreground=[("selected", FONDO)],
        )

    def _etiqueta(self, padre, texto):
        tk.Label(padre, text=texto, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(
            anchor=tk.W
        )

    def _campo(self, padre, variable, limite=None, solo_digitos=False, solo_letras=False):
        opciones = {}
        if limite or solo_digitos or solo_letras:
            def _validar(texto):
                if limite and len(texto) > limite:
                    return False
                if solo_digitos and texto and not texto.isdigit():
                    return False
                if solo_letras and not es_solo_texto(texto):
                    return False
                return True

            opciones["validate"] = "key"
            opciones["validatecommand"] = (self.ventana.register(_validar), "%P")
        entry = tk.Entry(
            padre,
            textvariable=variable,
            bg=CAMPO,
            fg=TEXTO,
            insertbackground=TEXTO,
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            **opciones,
        )
        entry.pack(fill=tk.X, ipady=4, pady=(2, 10))
        return entry

    def _boton(self, padre, texto, comando, estilo="secundario"):
        paletas = {
            "dorado": (DORADO, "#e5c158", FONDO),
            "secundario": (CAMPO, "#374151", TEXTO),
            "peligro": (PELIGRO, PELIGRO_HOVER, TEXTO),
        }
        fondo, hover, color = paletas[estilo]
        boton = tk.Label(
            padre,
            text=texto,
            bg=fondo,
            fg=color,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=7,
            cursor="hand2",
        )
        boton.bind("<Button-1>", lambda e: comando())
        boton.bind("<Enter>", lambda e: boton.config(bg=hover))
        boton.bind("<Leave>", lambda e: boton.config(bg=fondo))
        return boton

    def _crear_widgets(self):
        tk.Label(
            self.ventana,
            text="CLIENTES Y VEHÍCULOS",
            bg=FONDO,
            fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, padx=24, pady=(16, 8))

        self.notebook = ttk.Notebook(self.ventana, style="Parking.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 18))

        self.tab_clientes = tk.Frame(self.notebook, bg=FONDO)
        self.tab_vehiculos = tk.Frame(self.notebook, bg=FONDO)
        self.notebook.add(self.tab_clientes, text="Clientes")
        self.notebook.add(self.tab_vehiculos, text="Vehículos")

        self._construir_tab_clientes()
        self._construir_tab_vehiculos()

    # ------------------------------------------------------- pestaña clientes
    def _construir_tab_clientes(self):
        cuerpo = tk.Frame(self.tab_clientes, bg=FONDO, pady=12)
        cuerpo.pack(fill=tk.BOTH, expand=True)

        form = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16, width=290)
        form.pack(side=tk.LEFT, fill=tk.Y)
        form.pack_propagate(False)

        tk.Label(
            form, textvariable=self.var_cli_modo, bg=PANEL, fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        self._etiqueta(form, "Nombre completo")
        self.entry_cli_nombre = self._campo(
            form, self.var_cli_nombre, limite=controlador.LONGITUD_NOMBRE, solo_letras=True,
        )

        self._etiqueta(form, "Teléfono")
        self._campo(
            form,
            self.var_cli_telefono,
            limite=controlador.LONGITUD_TELEFONO,
            solo_digitos=True,
        )

        self._etiqueta(form, "Tipo de cliente")
        ttk.Combobox(
            form,
            textvariable=self.var_cli_tipo,
            values=list(controlador.TIPOS_CLIENTE),
            state="readonly",
        ).pack(fill=tk.X, ipady=3, pady=(2, 10))

        self._etiqueta(form, "Asignar vehículo de 'Público general' (opcional)")
        self.combo_veh_pg = ttk.Combobox(
            form, textvariable=self.var_cli_vehiculo_pg, state="readonly"
        )
        self.combo_veh_pg.pack(fill=tk.X, ipady=3, pady=(2, 14))

        self.btn_cli_guardar = self._boton(
            form, "Guardar cliente", self._guardar_cliente, estilo="dorado"
        )
        self.btn_cli_guardar.pack(fill=tk.X, pady=(0, 8))

        self._boton(
            form, "Eliminar cliente", self._eliminar_cliente, estilo="peligro"
        ).pack(fill=tk.X, pady=(0, 8))

        self._boton(
            form, "Nuevo / Limpiar", self._limpiar_cliente, estilo="secundario"
        ).pack(fill=tk.X)

        # Panel derecho: tabla de clientes
        lista = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))

        enc = tk.Frame(lista, bg=PANEL)
        enc.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            enc, text="Directorio de clientes", bg=PANEL, fg=TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT)
        self.lbl_total_clientes = tk.Label(
            enc, text="", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)
        )
        self.lbl_total_clientes.pack(side=tk.RIGHT)

        busc = tk.Frame(lista, bg=PANEL)
        busc.pack(fill=tk.X, pady=(0, 10))
        tk.Label(busc, text="Buscar:", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        e_buscar = tk.Entry(
            busc, textvariable=self.var_cli_buscar, bg=CAMPO, fg=TEXTO,
            insertbackground=TEXTO, relief=tk.FLAT, font=("Segoe UI", 9),
        )
        e_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        e_buscar.bind("<KeyRelease>", lambda e: self._cargar_tabla_clientes())

        self.tabla_clientes = ttk.Treeview(
            lista,
            columns=("id", "nombre", "telefono", "tipo", "vehiculos"),
            show="headings",
            style="Parking.Treeview",
            selectmode="browse",
            height=13,
        )
        for col, titulo, ancho in (
            ("id", "ID", 40),
            ("nombre", "Nombre", 185),
            ("telefono", "Teléfono", 110),
            ("tipo", "Tipo", 80),
            ("vehiculos", "Vehículos", 75),
        ):
            self.tabla_clientes.heading(col, text=titulo)
            self.tabla_clientes.column(col, width=ancho, anchor=tk.W)
        self.tabla_clientes.pack(fill=tk.BOTH, expand=True)
        self.tabla_clientes.bind("<<TreeviewSelect>>", self._al_seleccionar_cliente)

    # ------------------------------------------------------ pestaña vehículos
    def _construir_tab_vehiculos(self):
        cuerpo = tk.Frame(self.tab_vehiculos, bg=FONDO, pady=12)
        cuerpo.pack(fill=tk.BOTH, expand=True)

        form = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16, width=290)
        form.pack(side=tk.LEFT, fill=tk.Y)
        form.pack_propagate(False)

        tk.Label(
            form, textvariable=self.var_veh_modo, bg=PANEL, fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        self._etiqueta(form, "Matrícula")
        self.entry_veh_matricula = self._campo(
            form, self.var_veh_matricula, limite=controlador.LONGITUD_MATRICULA
        )

        self._etiqueta(form, "Cliente asignado")
        self.combo_veh_cliente = ttk.Combobox(
            form, textvariable=self.var_veh_cliente, state="readonly"
        )
        self.combo_veh_cliente.pack(fill=tk.X, ipady=3, pady=(2, 10))

        self._etiqueta(form, "Marca")
        self._campo(form, self.var_veh_marca, limite=controlador.LONGITUD_MARCA, solo_letras=True,)

        self._etiqueta(form, "Modelo")
        self._campo(form, self.var_veh_modelo, limite=controlador.LONGITUD_MODELO)

        self._etiqueta(form, "Color")
        self.combo_veh_color = ttk.Combobox(
          form,
          textvariable=self.var_veh_color,
          values=COLORES_VEHICULO,
          state="readonly",
        )
        self.combo_veh_color.pack(fill=tk.X, ipady=3, pady=(2, 10))

        self.btn_veh_guardar = self._boton(
            form, "Guardar vehículo", self._guardar_vehiculo, estilo="dorado"
        )
        self.btn_veh_guardar.pack(fill=tk.X, pady=(4, 8))

        self._boton(
            form, "Eliminar vehículo", self._eliminar_vehiculo, estilo="peligro"
        ).pack(fill=tk.X, pady=(0, 8))

        self._boton(
            form, "Nuevo / Limpiar", self._limpiar_vehiculo, estilo="secundario"
        ).pack(fill=tk.X)

        # Panel derecho: tabla de vehículos
        lista = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))

        enc = tk.Frame(lista, bg=PANEL)
        enc.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            enc, text="Vehículos registrados", bg=PANEL, fg=TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT)
        self.lbl_total_vehiculos = tk.Label(
            enc, text="", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)
        )
        self.lbl_total_vehiculos.pack(side=tk.RIGHT)

        busc = tk.Frame(lista, bg=PANEL)
        busc.pack(fill=tk.X, pady=(0, 10))
        tk.Label(busc, text="Buscar:", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        e_buscar = tk.Entry(
            busc, textvariable=self.var_veh_buscar, bg=CAMPO, fg=TEXTO,
            insertbackground=TEXTO, relief=tk.FLAT, font=("Segoe UI", 9),
        )
        e_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 10))
        e_buscar.bind("<KeyRelease>", lambda e: self._cargar_tabla_vehiculos())

        tk.Checkbutton(
            busc,
            text="Solo Público general",
            variable=self.var_solo_publico,
            command=self._cargar_tabla_vehiculos,
            bg=PANEL,
            fg=DORADO,
            selectcolor=CAMPO,
            activebackground=PANEL,
            activeforeground=DORADO,
            font=("Segoe UI", 8, "bold"),
        ).pack(side=tk.RIGHT)

        self.tabla_vehiculos = ttk.Treeview(
            lista,
            columns=("matricula", "cliente", "marca", "modelo", "color"),
            show="headings",
            style="Parking.Treeview",
            selectmode="browse",
            height=13,
        )
        for col, titulo, ancho in (
            ("matricula", "Matrícula", 95),
            ("cliente", "Cliente", 155),
            ("marca", "Marca", 95),
            ("modelo", "Modelo", 95),
            ("color", "Color", 75),
        ):
            self.tabla_vehiculos.heading(col, text=titulo)
            self.tabla_vehiculos.column(col, width=ancho, anchor=tk.W)
        self.tabla_vehiculos.pack(fill=tk.BOTH, expand=True)
        self.tabla_vehiculos.bind("<<TreeviewSelect>>", self._al_seleccionar_vehiculo)

    # ----------------------------------------------------------------- lógica
    def _refrescar_todo(self):
        self._cargar_tabla_clientes()
        self._cargar_combos()
        self._cargar_tabla_vehiculos()

    def _cargar_combos(self):
        try:
            clientes = controlador.listar_clientes()
            veh_pg = controlador.vehiculos_publico_general()
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._clientes_combo = {
            f"{c['nombre']} (#{c['id_cliente']})": c["id_cliente"] for c in clientes
        }
        elegido = self.var_veh_cliente.get()
        self.combo_veh_cliente["values"] = list(self._clientes_combo)
        if elegido in self._clientes_combo:
            self.var_veh_cliente.set(elegido)
        elif self._clientes_combo:
            self.var_veh_cliente.set(next(iter(self._clientes_combo)))

        self._vehiculos_pg_combo = {"Ninguno": None}
        for v in veh_pg:
            desc = " ".join(x for x in (v["marca"], v["modelo"]) if x) or "Sin datos"
            self._vehiculos_pg_combo[f"{v['matricula']} ({desc})"] = v["matricula"]
        self.combo_veh_pg["values"] = list(self._vehiculos_pg_combo)
        self.var_cli_vehiculo_pg.set("Ninguno")

    def _cargar_tabla_clientes(self):
        try:
            filas = controlador.listar_clientes(self.var_cli_buscar.get())
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._clientes_por_id = {f["id_cliente"]: f for f in filas}
        self.tabla_clientes.delete(*self.tabla_clientes.get_children())
        for f in filas:
            self.tabla_clientes.insert(
                "",
                tk.END,
                iid=str(f["id_cliente"]),
                values=(
                    f["id_cliente"],
                    f["nombre"],
                    f["telefono"] or "—",
                    f["tipo_cliente"],
                    f["total_vehiculos"],
                ),
            )
        self.lbl_total_clientes.config(text=f"{len(filas)} cliente(s)")

    def _al_seleccionar_cliente(self, _evento):
        sel = self.tabla_clientes.selection()
        if not sel:
            return
        datos = self._clientes_por_id.get(int(sel[0]))
        if not datos:
            return
        self.cliente_seleccionado = datos
        self.var_cli_modo.set(f"Editando cliente #{datos['id_cliente']}")
        self.var_cli_nombre.set(datos["nombre"])
        self.var_cli_telefono.set(datos["telefono"] or "")
        self.var_cli_tipo.set(datos["tipo_cliente"])
        self.combo_veh_pg.config(state="disabled")
        self.btn_cli_guardar.config(text="Actualizar cliente")

    def _limpiar_cliente(self):
        self.cliente_seleccionado = None
        self.tabla_clientes.selection_remove(self.tabla_clientes.selection())
        self.var_cli_modo.set("Nuevo cliente")
        self.var_cli_nombre.set("")
        self.var_cli_telefono.set("")
        self.var_cli_tipo.set("paso")
        self.var_cli_vehiculo_pg.set("Ninguno")
        self.combo_veh_pg.config(state="readonly")
        self.btn_cli_guardar.config(text="Guardar cliente")
        self.entry_cli_nombre.focus()

    def _guardar_cliente(self):
        if not self.var_cli_nombre.get().strip() or not self.var_cli_telefono.get().strip() or not self.var_cli_tipo.get().strip():
            messagebox.showwarning(
                "Clientes",
                "Todos los campos del cliente son obligatorios.",
                parent=self.ventana,
            )
            return
        try:
            if self.cliente_seleccionado is None:
                matricula_pg = self._vehiculos_pg_combo.get(self.var_cli_vehiculo_pg.get())
                controlador.crear_cliente(
                    self.var_cli_nombre.get(),
                    self.var_cli_telefono.get(),
                    self.var_cli_tipo.get(),
                    matricula_publico=matricula_pg,
                )
                extra = f" y se le asignó {matricula_pg}" if matricula_pg else ""
                mensaje = f"Cliente registrado correctamente{extra}."
            else:
                controlador.actualizar_cliente(
                    self.cliente_seleccionado["id_cliente"],
                    self.var_cli_nombre.get(),
                    self.var_cli_telefono.get(),
                    self.var_cli_tipo.get(),
                )
                mensaje = "Cliente actualizado correctamente."
        except ErrorClienteVehiculo as error:
            messagebox.showwarning("Clientes", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._refrescar_todo()
        self._limpiar_cliente()
        messagebox.showinfo("Clientes", mensaje, parent=self.ventana)

    def _eliminar_cliente(self):
        if self.cliente_seleccionado is None:
            messagebox.showwarning("Clientes", "Selecciona un cliente de la tabla.", parent=self.ventana)
            return
        if not messagebox.askyesno(
            "Confirmar baja",
            f"¿Eliminar al cliente '{self.cliente_seleccionado['nombre']}'?",
            parent=self.ventana,
        ):
            return
        try:
            controlador.eliminar_cliente(self.cliente_seleccionado["id_cliente"])
        except ErrorClienteVehiculo as error:
            messagebox.showwarning("Clientes", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._refrescar_todo()
        self._limpiar_cliente()

    def _cargar_tabla_vehiculos(self):
        try:
            filas = controlador.listar_vehiculos(
                self.var_veh_buscar.get(), solo_publico=self.var_solo_publico.get()
            )
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._vehiculos_por_mat = {f["matricula"]: f for f in filas}
        self.tabla_vehiculos.delete(*self.tabla_vehiculos.get_children())
        for f in filas:
            self.tabla_vehiculos.insert(
                "",
                tk.END,
                iid=f["matricula"],
                values=(
                    f["matricula"],
                    f["cliente"],
                    f["marca"] or "—",
                    f["modelo"] or "—",
                    f["color"] or "—",
                ),
            )
        self.lbl_total_vehiculos.config(text=f"{len(filas)} vehículo(s)")

    def _al_seleccionar_vehiculo(self, _evento):
        sel = self.tabla_vehiculos.selection()
        if not sel:
            return
        datos = self._vehiculos_por_mat.get(sel[0])
        if not datos:
            return
        self.vehiculo_seleccionado = datos
        self.var_veh_modo.set(f"Editando {datos['matricula']}")
        self.var_veh_matricula.set(datos["matricula"])
        etiqueta_cli = f"{datos['cliente']} (#{datos['id_cliente']})"
        if etiqueta_cli in self._clientes_combo:
            self.var_veh_cliente.set(etiqueta_cli)
        self.var_veh_marca.set(datos["marca"] or "")
        self.var_veh_modelo.set(datos["modelo"] or "")
        self.var_veh_color.set(datos["color"] or "")
        self.btn_veh_guardar.config(text="Actualizar vehículo")

    def _limpiar_vehiculo(self):
        self.vehiculo_seleccionado = None
        self.tabla_vehiculos.selection_remove(self.tabla_vehiculos.selection())
        self.var_veh_modo.set("Nuevo vehículo")
        self.var_veh_matricula.set("")
        self.var_veh_marca.set("")
        self.var_veh_modelo.set("")
        self.var_veh_color.set("")
        self.btn_veh_guardar.config(text="Guardar vehículo")
        self.entry_veh_matricula.focus()

   
    def _guardar_vehiculo(self):
        id_cliente = self._clientes_combo.get(self.var_veh_cliente.get())
        if (
            not self.var_veh_matricula.get().strip()
            or not id_cliente
            or not self.var_veh_marca.get().strip()
            or not self.var_veh_modelo.get().strip()
            or not self.var_veh_color.get().strip()
        ):
            messagebox.showwarning(
                "Vehículos",
                "Todos los campos del vehículo son obligatorios.",
                parent=self.ventana,
            )
            return

        mat = "".join(self.var_veh_matricula.get().split())
        if len(mat) < 5 or not mat.isalnum() or not (any(c.isalpha() for c in mat) and any(c.isdigit() for c in mat)):
            messagebox.showwarning(
                "Vehículos",
                "Ingresa una matrícula válida (mínimo 5 caracteres con letras y números, ej. ABC1234).",
                parent=self.ventana,
            )
            return
        
        try:
            if self.vehiculo_seleccionado is None:
                controlador.crear_vehiculo(
                    self.var_veh_matricula.get(),
                    id_cliente,
                    self.var_veh_marca.get(),
                    self.var_veh_modelo.get(),
                    self.var_veh_color.get(),
                )
                mensaje = "Vehículo registrado correctamente."
            else:
                controlador.actualizar_vehiculo(
                    self.vehiculo_seleccionado["matricula"],
                    self.var_veh_matricula.get(),
                    id_cliente,
                    self.var_veh_marca.get(),
                    self.var_veh_modelo.get(),
                    self.var_veh_color.get(),
                )
                mensaje = "Vehículo actualizado correctamente."
        except ErrorClienteVehiculo as error:
            messagebox.showwarning("Vehículos", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._refrescar_todo()
        self._limpiar_vehiculo()
        messagebox.showinfo("Vehículos", mensaje, parent=self.ventana)

    def _eliminar_vehiculo(self):
        if self.vehiculo_seleccionado is None:
            messagebox.showwarning("Vehículos", "Selecciona un vehículo de la tabla.", parent=self.ventana)
            return
        mat = self.vehiculo_seleccionado["matricula"]
        if not messagebox.askyesno(
            "Confirmar baja", f"¿Eliminar el vehículo '{mat}'?", parent=self.ventana
        ):
            return
        try:
            controlador.eliminar_vehiculo(mat)
        except ErrorClienteVehiculo as error:
            messagebox.showwarning("Vehículos", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._refrescar_todo()
        self._limpiar_vehiculo()