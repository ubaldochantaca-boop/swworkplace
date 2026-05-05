# ==========================================================
# 1.- Nombre del programa:     Renombrador PRO
#
# 2.- Autor:     Ubaldo Chantaca Zeron ©ucz
#
# 3.- Versión:     V0.00
#
# 4.- Fecha de creación:     16-Apr-2026
#
# 5.- Fecha de modificación:     16-Apr-2026
#
# 6.- Resumen de funcionalidad:
#     Aplicación gráfica desarrollada en Python/Tkinter para
#     renombrar archivos de forma masiva dentro de un
#     subdirectorio seleccionado por el usuario.
#
#     Funciones principales:
#     - Selección de carpeta mediante explorador Windows
#     - Prefijo y/o sufijo configurable
#     - Vista previa antes de ejecutar
#     - Checkbox para elegir archivos individuales
#     - Exclusión de carpetas y subdirectorios
#     - Log de éxitos y errores
#     - Panel lateral de ayuda
#     - Nueva ejecución sin cerrar la aplicación
#
# 7.- Ejemplo de ejecución:
#
#     Carpeta seleccionada:  C:\Reportes
#
#     Archivos originales:
#     ventas.xlsx
#     clientes.txt
#
#     Prefijo:  REP_
#
#     Sufijo:   _2026
#
#     Resultado:
#     REP_ventas_2026.xlsx
#     REP_clientes_2026.txt
#
# ==========================================================
#
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

APP_NAME = "Renombrador de Archivos"
CURRENT_DIR = Path.cwd()


class RenombradorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("980x700")

        self.prefijo = tk.StringVar()
        self.sufijo = tk.StringVar()

        self.crear_ui()
        self.cargar_archivos()

    def crear_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Carpeta actual:").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text=str(CURRENT_DIR)).grid(row=0, column=1, columnspan=4, sticky="w")

        ttk.Label(top, text="Prefijo:").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(top, textvariable=self.prefijo, width=25).grid(row=1, column=1, sticky="w")

        ttk.Label(top, text="Sufijo:").grid(row=1, column=2, sticky="w", padx=(20, 0))
        ttk.Entry(top, textvariable=self.sufijo, width=25).grid(row=1, column=3, sticky="w")

        ttk.Button(top, text="Vista previa", command=self.cargar_archivos).grid(row=1, column=4, padx=10)
        ttk.Button(top, text="Renombrar", command=self.renombrar).grid(row=1, column=5, padx=5)

        mid = ttk.LabelFrame(self.root, text="Vista previa (Antes -> Después)", padding=10)
        mid.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview = scrolledtext.ScrolledText(mid, height=20)
        self.preview.pack(fill="both", expand=True)

        low = ttk.LabelFrame(self.root, text="Log de ejecución", padding=10)
        low.pack(fill="both", expand=True, padx=10, pady=5)

        self.log = scrolledtext.ScrolledText(low, height=12)
        self.log.pack(fill="both", expand=True)

    def obtener_archivos(self):
        exe_name = Path(__file__).name if "__file__" in globals() else ""
        archivos = []

        for item in CURRENT_DIR.iterdir():
            if item.is_file():
                if item.name.lower() != exe_name.lower():
                    archivos.append(item)

        return archivos

    def nuevo_nombre(self, archivo):
        return f"{self.prefijo.get()}{archivo.stem}{self.sufijo.get()}{archivo.suffix}"

    def cargar_archivos(self):
        self.preview.delete("1.0", tk.END)

        archivos = self.obtener_archivos()

        if not archivos:
            self.preview.insert(tk.END, "No hay archivos para procesar.\n")
            return

        for archivo in archivos:
            nuevo = self.nuevo_nombre(archivo)
            self.preview.insert(tk.END, f"{archivo.name}  ->  {nuevo}\n")

    def renombrar(self):
        archivos = self.obtener_archivos()

        if not archivos:
            messagebox.showinfo(APP_NAME, "No hay archivos para renombrar.")
            return

        resp = messagebox.askyesno(
            APP_NAME,
            "¿Confirmas que deseas renombrar los archivos mostrados?"
        )

        if not resp:
            return

        self.log.delete("1.0", tk.END)

        exitosos = 0
        errores = 0

        for archivo in archivos:
            nuevo = self.nuevo_nombre(archivo)
            destino = archivo.parent / nuevo

            try:
                if destino.exists():
                    raise FileExistsError("Ya existe archivo destino")

                archivo.rename(destino)
                self.log.insert(tk.END, f"OK   | {archivo.name} -> {nuevo}\n")
                exitosos += 1

            except PermissionError:
                self.log.insert(tk.END, f"ERROR| {archivo.name} | Archivo en uso / bloqueado\n")
                errores += 1

            except FileExistsError:
                self.log.insert(tk.END, f"ERROR| {archivo.name} | Ya existe destino: {nuevo}\n")
                errores += 1

            except Exception as e:
                self.log.insert(tk.END, f"ERROR| {archivo.name} | {str(e)}\n")
                errores += 1

        self.log.insert(tk.END, "\n")
        self.log.insert(tk.END, f"Resumen: {exitosos} renombrados, {errores} errores.\n")

        self.cargar_archivos()


if __name__ == "__main__":
    root = tk.Tk()
    app = RenombradorApp(root)
    root.mainloop()