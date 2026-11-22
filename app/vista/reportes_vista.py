"""Ventana de reportes (solo para el administrador).

Se abre desde el menú principal:

    from app.vista.reportes_vista import abrir_reportes
    abrir_reportes(root, usuario)
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.controlador import reporte_controlador as controlador
from app.modelo.conexion import ErrorBD
from app.vista.entrada_salida_vista import CAMPO, DORADO, FONDO, PANEL, TEXTO, TEXTO_SUAVE


def abrir_reportes(parent, usuario):
    """Abre la ventana si el usuario es admin; si no, avisa y no abre nada."""
    if not controlador.es_admin(usuario):
        messagebox.showwarning(
            "Reportes", "Esta sección es solo para el administrador.", parent=parent
        )
        return None
    return VentanaReportes(parent)


class VentanaReportes:
    def __init__(self, parent):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("CYC PARKING - Reportes")
        self.ventana.configure(bg=FONDO)
        self.ventana.minsize(760, 520)
        self.ventana.transient(parent)
        self._centrar(parent, 860, 600)

        self.var_anio = tk.StringVar()
        self.tablas = []
        self.totales = []

        self._estilos()
        self._crear_widgets()
        self._cargar_anios()
        self._actualizar()

    # ------------------------------------------------------------------ vista
    def _centrar(self, parent, ancho, alto):
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    def _estilos(self):
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
        estilo.configure("Parking.TNotebook", background=FONDO, borderwidth=0)
        estilo.configure(
            "Parking.TNotebook.Tab", background=PANEL, foreground=TEXTO_SUAVE,
            padding=(14, 7), font=("Segoe UI", 9, "bold"), borderwidth=0,
        )
        estilo.map(
            "Parking.TNotebook.Tab",
            background=[("selected", CAMPO)], foreground=[("selected", DORADO)],
        )

    def _crear_widgets(self):
        encabezado = tk.Frame(self.ventana, bg=FONDO)
        encabezado.pack(fill=tk.X, padx=24, pady=(18, 10))
        tk.Label(
            encabezado, text="REPORTES", bg=FONDO, fg=DORADO, font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT)

        self.combo_anio = ttk.Combobox(
            encabezado, textvariable=self.var_anio, state="readonly", width=10,
            postcommand=self._cargar_anios,
        )
        self.combo_anio.pack(side=tk.RIGHT)
        self.combo_anio.bind("<<ComboboxSelected>>", lambda e: self._actualizar())
        tk.Label(
            encabezado, text="Año", bg=FONDO, fg=TEXTO_SUAVE, font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT, padx=(0, 8))

        self.pestanas = ttk.Notebook(self.ventana, style="Parking.TNotebook")
        self.pestanas.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 20))

        for reporte in controlador.REPORTES:
            marco = tk.Frame(self.pestanas, bg=PANEL, padx=16, pady=14)
            self.pestanas.add(marco, text=reporte["titulo"])

            claves = [c[0] for c in reporte["columnas"]]
            tabla = ttk.Treeview(
                marco, columns=claves, show="headings", style="Parking.Treeview", selectmode="browse",
            )
            for clave, titulo, ancho, alineacion, _formato in reporte["columnas"]:
                tabla.heading(clave, text=titulo)
                tabla.column(clave, width=ancho, anchor=alineacion)
            tabla.pack(fill=tk.BOTH, expand=True)

            total = tk.Label(
                marco, text="", bg=PANEL, fg=DORADO, font=("Segoe UI", 10, "bold"), anchor="e",
            )
            total.pack(fill=tk.X, pady=(10, 0))

            self.tablas.append(tabla)
            self.totales.append(total)

    # ----------------------------------------------------------------- lógica
    def _cargar_anios(self):
        """Lee los años con datos. También se llama al desplegar la lista."""
        elegido = self.var_anio.get()
        try:
            opciones = controlador.anios_disponibles()
        except ErrorBD as error:
            messagebox.showerror("Base de datos", str(error), parent=self.ventana)
            return
        self.combo_anio["values"] = opciones
        if elegido in opciones:
            self.var_anio.set(elegido)
        else:
            self.var_anio.set(controlador.anio_inicial())

    def _actualizar(self):
        for numero, (tabla, total) in enumerate(zip(self.tablas, self.totales)):
            try:
                reporte = controlador.armar_reporte(numero, self.var_anio.get())
            except ErrorBD as error:
                messagebox.showerror("Base de datos", str(error), parent=self.ventana)
                return

            tabla.delete(*tabla.get_children())
            for fila in reporte["filas"]:
                tabla.insert("", tk.END, values=fila)

            if reporte["totales"] is None:
                total.config(text="Sin datos para este año.")
            else:
                partes = [
                    f"{titulo}: {valor}"
                    for (_c, titulo, *_resto), valor in zip(reporte["columnas"], reporte["totales"])
                    if valor and valor != "Total"
                ]
                total.config(text="Total   " + "   ".join(partes))
