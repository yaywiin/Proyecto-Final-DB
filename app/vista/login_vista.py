import tkinter as tk
from tkinter import messagebox, ttk

from app.controlador.login_controlador import autenticar_usuario
from app.vista.menu_vista import NOMBRE_SISTEMA, SUBTITULO_SISTEMA, VentanaMenu


class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.mostrar_login()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def centrar_ventana(self, ancho, alto):
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def mostrar_login(self):
        self.limpiar_ventana()
        self.root.title(f"{NOMBRE_SISTEMA} - Identificación")
        self.centrar_ventana(680, 420)
        self.root.configure(bg="#0b0f19")
        self.root.resizable(False, False)

        # Panel izquierdo estilo exclusivo (Inspirado en el branding CYC)
        panel_izq = tk.Frame(self.root, bg="#0b0f19", width=260)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y)
        panel_izq.pack_propagate(False)

        # Contenedor centrado para la marca
        marca_frame = tk.Frame(panel_izq, bg="#0b0f19")
        marca_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(
            marca_frame,
            text="CYC",
            font=("Segoe UI", 28, "bold"),
            bg="#0b0f19",
            fg="#d4af37",  # Dorado elegante
        ).pack()

        tk.Label(
            marca_frame,
            text="PARKING",
            font=("Segoe UI", 12, "bold"),
            bg="#0b0f19",
            fg="white",
        ).pack(pady=(0, 5))

        tk.Label(
            marca_frame,
            text=SUBTITULO_SISTEMA,
            font=("Segoe UI", 7),
            bg="#0b0f19",
            fg="#9ca3af",
        ).pack()

        # Panel derecho con formulario limpio
        panel_der = tk.Frame(self.root, bg="#111827", padx=40, pady=35)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            panel_der,
            text="Acceso al Sistema",
            font=("Segoe UI", 14, "bold"),
            bg="#111827",
            fg="white",
        ).pack(anchor=tk.W)

        tk.Label(
            panel_der,
            text="Ingrese sus credenciales operativas",
            font=("Segoe UI", 9),
            bg="#111827",
            fg="#9ca3af",
        ).pack(anchor=tk.W, pady=(2, 25))

        tk.Label(
            panel_der,
            text="Usuario",
            font=("Segoe UI", 9),
            bg="#111827",
            fg="#d1d5db",
        ).pack(anchor=tk.W)

        self.entry_usuario = ttk.Entry(panel_der, font=("Segoe UI", 10))
        self.entry_usuario.pack(fill=tk.X, ipady=5, pady=(4, 15))
        self.entry_usuario.focus()

        tk.Label(
            panel_der,
            text="Contraseña",
            font=("Segoe UI", 9),
            bg="#111827",
            fg="#d1d5db",
        ).pack(anchor=tk.W)

        self.entry_password = ttk.Entry(panel_der, show="•", font=("Segoe UI", 10))
        self.entry_password.pack(fill=tk.X, ipady=5, pady=(4, 8))

        self.ver_pass = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            panel_der,
            text="Mostrar contraseña",
            variable=self.ver_pass,
            command=self.alternar_password,
            bg="#111827",
            fg="#9ca3af",
            selectcolor="#1f2937",
            activebackground="#111827",
            activeforeground="white",
            font=("Segoe UI", 8),
        )
        chk.pack(anchor=tk.W, pady=(0, 20))

        btn_ingresar = tk.Button(
            panel_der,
            text="INGRESAR",
            command=self.validar_acceso,
            bg="#d4af37",
            fg="#0b0f19",
            activebackground="#c5a059",
            activeforeground="#0b0f19",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            pady=8,
            cursor="hand2",
        )
        btn_ingresar.pack(fill=tk.X)

        tk.Label(
            panel_der,
            text="Demo: admin / admin123  |  cobrador / cobrador123",
            font=("Segoe UI", 8),
            bg="#111827",
            fg="#6b7280",
        ).pack(pady=(20, 0))

        self.root.bind("<Return>", lambda e: self.validar_acceso())

    def alternar_password(self):
        self.entry_password.config(show="" if self.ver_pass.get() else "•")

    def validar_acceso(self):
        username = self.entry_usuario.get()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showwarning("Aviso", "Complete los campos obligatorios.")
            return

        usuario = autenticar_usuario(username, password)
        if not usuario:
            messagebox.showerror("Error", "Credenciales incorrectas.")
            return

        self.ir_al_menu(usuario)

    def ir_al_menu(self, usuario):
        self.root.unbind("<Return>")
        self.limpiar_ventana()
        VentanaMenu(self.root, usuario, al_cerrar_sesion=self.mostrar_login)


if __name__ == "__main__":
    root = tk.Tk()
    VentanaLogin(root)
    root.mainloop()