"""Ventana de entradas y salidas de vehículos.

Se abre desde el menú principal:

    from app.vista.entrada_salida_vista import abrir_entrada_salida
    abrir_entrada_salida(root, usuario)
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.controlador import servicio_controlador as controlador
from app.controlador.servicio_controlador import ErrorServicio
from app.modelo.conexion import ErrorBD

FONDO = "#0b0f19"
PANEL = "#111827"
CAMPO = "#1f2937"
DORADO = "#d4af37"
TEXTO = "#f3f4f6"
TEXTO_SUAVE = "#9ca3af"


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
        self._centrar(parent, 820, 600)

        self.var_matricula = tk.StringVar()
        self.var_cliente = tk.StringVar()
        self.var_marca = tk.StringVar()
        self.var_modelo = tk.StringVar()
        self.var_color = tk.StringVar()
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

    def _campo(self, padre, variable):
        entry = tk.Entry(
            padre, textvariable=variable, bg=CAMPO, fg=TEXTO, insertbackground=TEXTO,
            relief=tk.FLAT, font=("Segoe UI", 10),
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
        self.entry_matricula = self._campo(form, self.var_matricula)
        self.entry_matricula.bind("<Return>", lambda e: self._verificar_vehiculo())
        self.entry_matricula.bind("<FocusOut>", lambda e: self._verificar_vehiculo())
        self.entry_matricula.bind("<KeyRelease>", self._al_escribir_matricula)

        tk.Label(
            form, textvariable=self.var_estado, bg=PANEL, fg=DORADO, justify=tk.LEFT,
            wraplength=240, font=("Segoe UI", 8),
        ).pack(anchor=tk.W, pady=(0, 10))

        self._etiqueta(form, "Cliente (solo si el vehículo es nuevo)")
        self.combo_cliente = ttk.Combobox(form, textvariable=self.var_cliente, state="readonly")
        self.combo_cliente.pack(fill=tk.X, ipady=3, pady=(2, 10))

        self._etiqueta(form, "Marca")
        self.entry_marca = self._campo(form, self.var_marca)
        self._etiqueta(form, "Modelo")
        self.entry_modelo = self._campo(form, self.var_modelo)
        self._etiqueta(form, "Color")
        self.entry_color = self._campo(form, self.var_color)

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
            lista, columns=("matricula", "cliente", "entrada"), show="headings",
            style="Parking.Treeview", selectmode="browse", height=14,
        )
        for columna, titulo, ancho in (
            ("matricula", "Matrícula", 100), ("cliente", "Cliente", 140), ("entrada", "Entrada", 140),
        ):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor=tk.W)
        self.tabla.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # ----------------------------------------------------------------- lógica
    def _habilitar_datos_nuevo(self, activo):
        estado = "normal" if activo else "disabled"
        self.combo_cliente.config(state="readonly" if activo else "disabled")
        for entry in (self.entry_marca, self.entry_modelo, self.entry_color):
            entry.config(state=estado)

    def _cargar_clientes(self):
        try:
            filas = controlador.clientes_disponibles()
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return
        self.clientes = {f"{f['nombre']} (#{f['id_cliente']})": f["id_cliente"] for f in filas}
        self.combo_cliente["values"] = list(self.clientes)
        if self.clientes:
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
                values=(fila["matricula"], fila["cliente"], fila["fecha_entrada"].strftime("%d/%m/%Y %H:%M")),
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
            return None
        try:
            vehiculo = controlador.consultar_vehiculo(self.var_matricula.get())
        except ErrorServicio as error:
            self.var_estado.set(str(error))
            self._habilitar_datos_nuevo(True)
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
        return vehiculo

    def _limpiar_formulario(self):
        for variable in (self.var_matricula, self.var_marca, self.var_modelo, self.var_color):
            variable.set("")
        self._habilitar_datos_nuevo(True)
        self.var_estado.set("Escribe una matrícula y presiona Enter.")
        self.entry_matricula.focus()

    def _registrar_entrada(self):
        self._verificar_vehiculo()
        try:
            resultado = controlador.registrar_entrada(
                self.var_matricula.get(),
                self.id_usuario,
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
        self.var_estado.set(f"Entrada registrada: {resultado['matricula']}.")

    def _registrar_salida(self):
        try:
            resultado = controlador.registrar_salida(self.var_matricula.get())
        except ErrorServicio as error:
            messagebox.showwarning("Salida", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._actualizar_lista()
        self._limpiar_formulario()
        self.var_estado.set(
            f"Salida registrada: {resultado['matricula']} a las "
            f"{resultado['fecha_salida'].strftime('%H:%M')}."
        )
