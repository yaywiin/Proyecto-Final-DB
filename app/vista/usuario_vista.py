"""Ventana de gestión de usuarios (Alta, baja, cambio y consulta).

Se abre desde el menú principal:

    from app.vista.usuario_vista import abrir_usuarios
    abrir_usuarios(root, usuario)
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.controlador import usuario_controlador as controlador
from app.controlador.usuario_controlador import ErrorUsuario
from app.modelo.conexion import ErrorBD

FONDO = "#0b0f19"
PANEL = "#111827"
CAMPO = "#1f2937"
DORADO = "#d4af37"
TEXTO = "#f3f4f6"
TEXTO_SUAVE = "#9ca3af"
PELIGRO = "#7f1d1d"
PELIGRO_HOVER = "#991b1b"


def abrir_usuarios(parent, usuario):
    """Abre la ventana de administración de usuarios."""
    return VentanaUsuarios(parent, usuario)


def _id_usuario(usuario):
    return usuario.get("id_usuario", usuario.get("usuario_id"))


class VentanaUsuarios:
    def __init__(self, parent, usuario):
        self.id_admin_actual = _id_usuario(usuario)
        self.usuario_seleccionado = None

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("CYC PARKING - Gestión de Usuarios")
        self.ventana.configure(bg=FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self._centrar(parent, 860, 560)

        self.var_nombre = tk.StringVar()
        self.var_usuario = tk.StringVar()
        self.var_password = tk.StringVar()
        self.var_rol = tk.StringVar(value="cobrador")
        self.var_buscar = tk.StringVar()
        self.var_modo = tk.StringVar(value="Nuevo usuario")
        self.var_ayuda_pass = tk.StringVar(value="Contraseña (mín. 4 caracteres)")

        self._usuarios_por_id = {}

        self._crear_widgets()
        self._actualizar_lista()
        self.entry_nombre.focus()

    # ------------------------------------------------------------------ vista
    def _centrar(self, parent, ancho, alto):
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    def _etiqueta(self, padre, texto=None, textvariable=None):
        opciones = {"textvariable": textvariable} if textvariable else {"text": texto}
        tk.Label(
            padre, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8), **opciones
        ).pack(anchor=tk.W)

    def _campo(self, padre, variable, limite=None, ocultar=False):
        opciones = {}
        if limite:
            opciones["validate"] = "key"
            opciones["validatecommand"] = (
                self.ventana.register(lambda texto: len(texto) <= limite),
                "%P",
            )
        if ocultar:
            opciones["show"] = "•"

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
        entry.pack(fill=tk.X, ipady=5, pady=(2, 10))
        return entry

    def _boton(self, padre, texto, comando, estilo="secundario"):
        """Botón hecho con Label para conservar colores también en macOS."""
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
            pady=8,
            cursor="hand2",
        )
        boton._fondo = fondo
        boton._hover = hover
        boton.bind("<Button-1>", lambda e: comando())
        boton.bind("<Enter>", lambda e: boton.config(bg=boton._hover))
        boton.bind("<Leave>", lambda e: boton.config(bg=boton._fondo))
        return boton

    def _crear_widgets(self):
        tk.Label(
            self.ventana,
            text="GESTIÓN DE USUARIOS",
            bg=FONDO,
            fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, padx=24, pady=(18, 8))

        cuerpo = tk.Frame(self.ventana, bg=FONDO)
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 18))

        # Panel izquierdo: formulario alta / edición
        form = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16, width=290)
        form.pack(side=tk.LEFT, fill=tk.Y)
        form.pack_propagate(False)

        tk.Label(
            form,
            textvariable=self.var_modo,
            bg=PANEL,
            fg=DORADO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 12))

        self._etiqueta(form, "Nombre completo")
        self.entry_nombre = self._campo(
            form, self.var_nombre, limite=controlador.LONGITUD_NOMBRE
        )

        self._etiqueta(form, "Usuario (acceso)")
        self.entry_usuario = self._campo(
            form, self.var_usuario, limite=controlador.LONGITUD_USUARIO
        )

        self._etiqueta(form, textvariable=self.var_ayuda_pass)
        self.entry_password = self._campo(form, self.var_password, ocultar=True)

        self._etiqueta(form, "Rol")
        self.combo_rol = ttk.Combobox(
            form,
            textvariable=self.var_rol,
            values=list(controlador.ROLES_VALIDOS),
            state="readonly",
        )
        self.combo_rol.pack(fill=tk.X, ipady=3, pady=(2, 16))

        self.btn_guardar = self._boton(
            form, "Guardar usuario", self._guardar, estilo="dorado"
        )
        self.btn_guardar.pack(fill=tk.X, pady=(0, 8))

        self.btn_estado = self._boton(
            form, "Dar de baja", self._alternar_estado, estilo="peligro"
        )
        self.btn_estado.pack(fill=tk.X, pady=(0, 8))

        self.btn_limpiar = self._boton(
            form, "Nuevo / Limpiar", self._limpiar_formulario, estilo="secundario"
        )
        self.btn_limpiar.pack(fill=tk.X)

        # Panel derecho: consulta y buscador
        lista = tk.Frame(cuerpo, bg=PANEL, padx=18, pady=16)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))

        encabezado = tk.Frame(lista, bg=PANEL)
        encabezado.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            encabezado,
            text="Usuarios registrados",
            bg=PANEL,
            fg=TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT)
        self.lbl_total = tk.Label(
            encabezado, text="", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)
        )
        self.lbl_total.pack(side=tk.RIGHT)

        buscador = tk.Frame(lista, bg=PANEL)
        buscador.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            buscador, text="Buscar:", bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(0, 8))
        entry_buscar = tk.Entry(
            buscador,
            textvariable=self.var_buscar,
            bg=CAMPO,
            fg=TEXTO,
            insertbackground=TEXTO,
            relief=tk.FLAT,
            font=("Segoe UI", 9),
        )
        entry_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        entry_buscar.bind("<KeyRelease>", lambda e: self._actualizar_lista())

        estilo = ttk.Style()
        estilo.theme_use("clam")
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

        self.tabla = ttk.Treeview(
            lista,
            columns=("id", "nombre", "usuario", "rol", "estado"),
            show="headings",
            style="Parking.Treeview",
            selectmode="browse",
            height=14,
        )
        for columna, titulo, ancho in (
            ("id", "ID", 45),
            ("nombre", "Nombre", 175),
            ("usuario", "Usuario", 110),
            ("rol", "Rol", 85),
            ("estado", "Estado", 75),
        ):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor=tk.W)

        self.tabla.pack(fill=tk.BOTH, expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # ----------------------------------------------------------------- lógica
    def _actualizar_lista(self):
        try:
            filas = controlador.listar_usuarios(self.var_buscar.get())
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._usuarios_por_id = {f["id_usuario"]: f for f in filas}
        self.tabla.delete(*self.tabla.get_children())
        for fila in filas:
            estado_txt = "Activo" if fila["activo"] else "Inactivo"
            self.tabla.insert(
                "",
                tk.END,
                iid=str(fila["id_usuario"]),
                values=(
                    fila["id_usuario"],
                    fila["nombre"],
                    fila["usuario"],
                    fila["rol"],
                    estado_txt,
                ),
            )
        self.lbl_total.config(text=f"{len(filas)} usuario(s)")

    def _al_seleccionar(self, _evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        id_usuario = int(seleccion[0])
        datos = self._usuarios_por_id.get(id_usuario)
        if not datos:
            return

        self.usuario_seleccionado = datos
        self.var_modo.set(f"Editando usuario #{id_usuario}")
        self.var_nombre.set(datos["nombre"])
        self.var_usuario.set(datos["usuario"])
        self.var_password.set("")
        self.var_rol.set(datos["rol"])
        self.var_ayuda_pass.set("Nueva contraseña (dejar vacío para no cambiar)")
        self.btn_guardar.config(text="Actualizar usuario")

        if datos["activo"]:
            self.btn_estado._fondo = PELIGRO
            self.btn_estado._hover = PELIGRO_HOVER
            self.btn_estado.config(text="Dar de baja", bg=PELIGRO)
        else:
            self.btn_estado._fondo = "#065f46"
            self.btn_estado._hover = "#047857"
            self.btn_estado.config(text="Reactivar usuario", bg="#065f46")

    def _limpiar_formulario(self):
        self.usuario_seleccionado = None
        self.tabla.selection_remove(self.tabla.selection())
        self.var_modo.set("Nuevo usuario")
        self.var_nombre.set("")
        self.var_usuario.set("")
        self.var_password.set("")
        self.var_rol.set("cobrador")
        self.var_ayuda_pass.set("Contraseña (mín. 4 caracteres)")
        self.btn_guardar.config(text="Guardar usuario")
        self.btn_estado._fondo = PELIGRO
        self.btn_estado._hover = PELIGRO_HOVER
        self.btn_estado.config(text="Dar de baja", bg=PELIGRO)
        self.entry_nombre.focus()

    def _guardar(self):
        try:
            if self.usuario_seleccionado is None:
                controlador.crear_usuario(
                    self.var_nombre.get(),
                    self.var_usuario.get(),
                    self.var_password.get(),
                    self.var_rol.get(),
                )
                mensaje = f"Usuario '{self.var_usuario.get().strip()}' creado correctamente."
            else:
                controlador.actualizar_usuario(
                    self.usuario_seleccionado["id_usuario"],
                    self.var_nombre.get(),
                    self.var_usuario.get(),
                    self.var_rol.get(),
                    self.var_password.get(),
                    self.id_admin_actual,
                )
                mensaje = f"Usuario '{self.var_usuario.get().strip()}' actualizado correctamente."
        except ErrorUsuario as error:
            messagebox.showwarning("Usuarios", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._actualizar_lista()
        self._limpiar_formulario()
        messagebox.showinfo("Usuarios", mensaje, parent=self.ventana)

    def _alternar_estado(self):
        if self.usuario_seleccionado is None:
            messagebox.showwarning(
                "Usuarios", "Selecciona primero un usuario de la tabla.", parent=self.ventana
            )
            return

        id_usuario = self.usuario_seleccionado["id_usuario"]
        nuevo_estado = 0 if self.usuario_seleccionado["activo"] else 1
        accion = "dar de baja" if nuevo_estado == 0 else "reactivar"

        if not messagebox.askyesno(
            "Confirmar acción",
            f"¿Seguro que deseas {accion} al usuario '{self.usuario_seleccionado['usuario']}'?",
            parent=self.ventana,
        ):
            return

        try:
            controlador.cambiar_estado_usuario(id_usuario, nuevo_estado, self.id_admin_actual)
        except ErrorUsuario as error:
            messagebox.showwarning("Usuarios", str(error), parent=self.ventana)
            return
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return

        self._actualizar_lista()
        self._limpiar_formulario()