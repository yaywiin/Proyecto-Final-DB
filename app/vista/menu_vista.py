import tkinter as tk
from tkinter import messagebox

from app.controlador.permisos import filtrar_modulos, obtener_rol, tiene_permiso
from app.vista.entrada_salida_vista import abrir_entrada_salida
from app.vista.reportes_vista import abrir_reportes
from app.vista.usuario_vista import abrir_usuarios
from app.vista.cliente_vehiculo_vista import abrir_clientes_vehiculos

NOMBRE_SISTEMA = "CYC PARKING"
SUBTITULO_SISTEMA = "Sistema de Gestión de Estacionamiento"


class VentanaMenu:
    def __init__(self, root, usuario, al_cerrar_sesion=None):
        self.root = root
        self.usuario = usuario
        self.al_cerrar_sesion = al_cerrar_sesion

        self.configurar_ventana(920, 640)
        self.crear_widgets()

    def configurar_ventana(self, ancho, alto):
        self.root.title(f"{NOMBRE_SISTEMA} - Menú Principal")
        x = max(0, (self.root.winfo_screenwidth() // 2) - (ancho // 2))
        y = max(0, (self.root.winfo_screenheight() // 2) - (alto // 2))
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.configure(bg="#0b0f19")  # Fondo negro azulado de alta gama
        self.root.resizable(False, False)

    def crear_widgets(self):
        # Barra superior minimalista
        barra = tk.Frame(self.root, bg="#111827", padx=24, pady=14)
        barra.pack(fill=tk.X)

        # Monograma de las iniciales CYC
        lbl_logo = tk.Label(
            barra,
            text="CYC",
            font=("Segoe UI", 14, "bold"),
            bg="#111827",
            fg="#d4af37",  # Tono dorado elegante
        )
        lbl_logo.pack(side=tk.LEFT)

        tk.Label(
            barra,
            text=" |  PARKING",
            font=("Segoe UI", 11),
            bg="#111827",
            fg="#9ca3af",
        ).pack(side=tk.LEFT)

        btn_salir = tk.Button(
            barra,
            text="Cerrar sesión",
            command=self.cerrar_sesion,
            bg="#1f2937",
            fg="#f87171",
            activebackground="#374151",
            activeforeground="#f87171",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        btn_salir.pack(side=tk.RIGHT)

        nombre = self.usuario.get("nombre", "Usuario")
        perfil = obtener_rol(self.usuario).upper()

        tk.Label(
            barra,
            text=f"{nombre}  •  {perfil}",
            fg="#d1d5db",
            bg="#111827",
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT, padx=15)

        # Cuerpo principal con tarjetas limpias
        cuerpo = tk.Frame(self.root, bg="#0b0f19", padx=30, pady=25)
        cuerpo.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            cuerpo,
            text="CONTROL OPERATIVO",
            font=("Segoe UI", 10, "bold"),
            bg="#0b0f19",
            fg="#d4af37",
        ).pack(anchor=tk.W, pady=(0, 15))

        rejilla = tk.Frame(cuerpo, bg="#0b0f19")
        rejilla.pack(fill=tk.BOTH, expand=True)

        modulos = [
            ("Entradas y Salidas", "Registro de acceso vehicular"),
            ("Cobros", "Tarifa proporcional y liquidación"),
            ("Pensiones", "Gestión de espacios exclusivos"),
            ("Clientes", "Directorio y estatus VIP"),
            ("Vehículos", "Control por matrícula y gama"),
            ("Usuarios", "Control de accesos al sistema"),
            ("Reportes", "Métricas de ocupación e ingresos"),
        ]

        modulos_visibles = filtrar_modulos(self.usuario, modulos)

        for i, (titulo, desc) in enumerate(modulos_visibles):
            fila = i // 2
            col = i % 2

            tarjeta = tk.Frame(
                rejilla,
                bg="#111827",
                padx=16,
                pady=14,
            )
            tarjeta.grid(row=fila, column=col, padx=8, pady=8, sticky="nsew")

            btn = tk.Button(
                tarjeta,
                text=titulo,
                font=("Segoe UI", 10, "bold"),
                bg="#1f2937",
                fg="#f3f4f6",
                activebackground="#d4af37",
                activeforeground="#0b0f19",
                relief=tk.FLAT,
                anchor="w",
                padx=10,
                pady=6,
                cursor="hand2",
                command=lambda m=titulo: self.abrir_modulo(m),
            )
            btn.pack(fill=tk.X)

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#d4af37", fg="#0b0f19"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1f2937", fg="#f3f4f6"))

            tk.Label(
                tarjeta,
                text=desc,
                font=("Segoe UI", 8),
                bg="#111827",
                fg="#9ca3af",
                anchor="w",
            ).pack(fill=tk.X, pady=(5, 0))

        rejilla.columnconfigure(0, weight=1, uniform="col")
        rejilla.columnconfigure(1, weight=1, uniform="col")

    def abrir_modulo(self, modulo):
        if not tiene_permiso(self.usuario, modulo):
            messagebox.showwarning(
                "Acceso restringido",
                f"Tu perfil no tiene permiso para acceder a {modulo}.",
                parent=self.root,
            )
            return
        if modulo == "Entradas y Salidas":
            abrir_entrada_salida(self.root, self.usuario)
            return
        if modulo == "Clientes":
            abrir_clientes_vehiculos(self.root, self.usuario, pestana="clientes")
            return
        if modulo == "Vehículos":
            abrir_clientes_vehiculos(self.root, self.usuario, pestana="vehiculos")
            return
        if modulo == "Reportes":
            abrir_reportes(self.root, self.usuario)
            return
        if modulo == "Usuarios":
            rol = str(self.usuario.get("rol", self.usuario.get("perfil", "cobrador"))).lower()
            if rol != "admin":
                messagebox.showwarning(
                    "Acceso restringido",
                    "Solo el administrador puede gestionar usuarios.",
                    parent=self.root,
                )
                return
            abrir_usuarios(self.root, self.usuario)
            return
        messagebox.showinfo(modulo, f"Módulo seleccionado: {modulo}")

    def cerrar_sesion(self):
        if self.al_cerrar_sesion:
            self.al_cerrar_sesion()