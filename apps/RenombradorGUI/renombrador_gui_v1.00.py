# ==========================================================
# 1.- Nombre del programa:     Renombrador PRO
#
# 2.- Autor:     Ubaldo Chantaca Zeron ©ucz
#
# 3.- Versión:     V-1.00
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
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

APP = "Renombrador PRO"


class AppRenombrador:

    def __init__(self, root):

        self.root = root
        self.root.title(APP)
        self.root.geometry("1100x720")

        self.prefijo = tk.StringVar()
        self.sufijo = tk.StringVar()

        self.directorio = Path.cwd()

        self.archivos = []
        self.checks = {}
        self.panel_ayuda = None  # Panel de ayuda no implementado en esta versión
        self.ayuda_visible = False  # Variable para controlar la visibilidad del panel de ayuda

        self.ui()
        self.cargar()

    # -------------------------------------------------
    def ui(self):

        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Carpeta:").grid(row=0, column=0)

        self.lbl = ttk.Label(top, text=str(self.directorio))
        self.lbl.grid(row=0, column=1, columnspan=4, sticky="w")
        
        ttk.Button(top, text="Seleccionar Carpeta",
           command=self.seleccionar).grid(row=0, column=5, padx=5)
        
        ttk.Button(
            self.root,
            text="❓ Ayuda",
            command=self.toggle_ayuda
        ).place(relx=0.98, y=10, anchor="ne")

    #    ttk.Button(top, text="❓ Ayuda",
    #            command=self.toggle_ayuda).grid(row=0, column=6, padx=5)

        ttk.Label(top, text="Prefijo").grid(row=1, column=2)
        ttk.Entry(top, textvariable=self.prefijo, width=20).grid(row=1, column=1)

        ttk.Label(top, text="Sufijo").grid(row=1, column=2)
        ttk.Entry(top, textvariable=self.sufijo, width=20).grid(row=1, column=3)

        ttk.Button(top, text="Vista previa",
                   command=self.cargar).grid(row=1, column=4)

        ttk.Button(top, text="Renombrar",
                   command=self.renombrar).grid(row=1, column=5)

        ttk.Button(top, text="Nueva ejecución",
                   command=self.reset).grid(row=1, column=6)

        # Tabla
        frame = ttk.LabelFrame(self.root, text="Archivos")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(frame)
        self.scroll = ttk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)

        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        # LOG
        self.log = tk.Text(self.root, height=12)
        self.log.pack(fill="both", padx=10, pady=5)

    # -------------------------------------------------
    def seleccionar(self):

        folder = filedialog.askdirectory(initialdir=self.directorio)

        if folder:
            self.directorio = Path(folder)
            self.lbl.config(text=str(self.directorio))
            self.reset()

    # -------------------------------------------------
    def reset(self):

        self.prefijo.set("")
        self.sufijo.set("")
        self.log.delete("1.0", tk.END)
        self.cargar()

    # -------------------------------------------------
    def obtener(self):

        exe = Path(__file__).name

        lista = []

        for x in self.directorio.iterdir():

            if x.is_file() and x.name.lower() != exe.lower():
                lista.append(x)

        return lista

    # -------------------------------------------------
    def nuevo(self, archivo):

        return f"{self.prefijo.get()}{archivo.stem}{self.sufijo.get()}{archivo.suffix}"

    # -------------------------------------------------
    def limpiar_tabla(self):

        for w in self.inner.winfo_children():
            w.destroy()

    # -------------------------------------------------
    def cargar(self):

        self.limpiar_tabla()

        self.archivos = self.obtener()
        self.checks = {}

        if not self.archivos:
            ttk.Label(self.inner, text="No hay archivos").pack()
            return

        for archivo in self.archivos:

            fila = ttk.Frame(self.inner)
            fila.pack(fill="x", padx=5, pady=2)

            var = tk.BooleanVar(value=True)

            self.checks[archivo] = var

            ttk.Checkbutton(fila, variable=var).pack(side="left")

            ttk.Label(
                fila,
                text=f"{archivo.name}   --->   {self.nuevo(archivo)}",
                width=120,
                anchor="w"
            ).pack(side="left")

    # ------------------------------------------------
    def toggle_ayuda(self):

        if self.ayuda_visible:
            self.cerrar_ayuda()
        else:
            self.mostrar_ayuda()


    def mostrar_ayuda(self):

        if self.panel_ayuda:
            return

        self.ayuda_visible = True

        self.panel_ayuda = tk.Frame(
            self.root,
            bg="#f0f0f0",
            width=220
        )

        self.panel_ayuda.place(
            relx=1.0,
            rely=0,
            relheight=1.0,
            relwidth=0.20,
            anchor="ne"
        )

        topbar = tk.Frame(self.panel_ayuda, bg="#d9d9d9")
        topbar.pack(fill="x")

        tk.Label(
            topbar,
            text="AYUDA",
            bg="#d9d9d9",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=8, pady=5)

        tk.Button(
            topbar,
            text="X",
            command=self.cerrar_ayuda
        ).pack(side="right", padx=5, pady=3)

        texto = tk.Text(
            self.panel_ayuda,
            wrap="word",
            bg="#f8f8f8"
        )

        texto.pack(fill="both", expand=True, padx=5, pady=5)

        ayuda = """
    OBJETIVO

    Renombrar archivos del subdirectorio seleccionado.

    RIESGOS

    • Cambia nombres de archivos reales.
    • Ejecutables también pueden cambiar.
    • Archivos bloqueados no podrán cambiarse.

    PASOS

    1. Seleccionar carpeta
    2. Capturar prefijo/sufijo
    3. Vista previa
    4. Desmarcar archivos
    5. Renombrar

    BOTÓN NUEVA EJECUCIÓN

    Reinicia el proceso.

    RECOMENDACIÓN

    Siempre revisar antes de ejecutar.

    ©ucz
    """

        texto.insert("1.0", ayuda)
        texto.config(state="disabled")


    def cerrar_ayuda(self):

        if self.panel_ayuda:
            self.panel_ayuda.destroy()
            self.panel_ayuda = None

        self.ayuda_visible = False

    # -------------------------------------------------
    def renombrar(self):

        self.log.delete("1.0", tk.END)

        seleccionados = [
            x for x in self.archivos if self.checks[x].get()
        ]

        if not seleccionados:
            messagebox.showwarning(APP, "No seleccionaste archivos.")
            return

        ok = 0
        err = 0

        confirmar = messagebox.askyesno(
            APP,
            f"¿Renombrar {len(seleccionados)} archivos seleccionados?"
        )

        if not confirmar:
            return

        for archivo in seleccionados:

            destino = archivo.parent / self.nuevo(archivo)

            try:

                if destino.exists():
                    raise FileExistsError

                archivo.rename(destino)

                self.log.insert(
                    tk.END,
                    f"OK     | {archivo.name} -> {destino.name}\n"
                )

                ok += 1

            except PermissionError:

                self.log.insert(
                    tk.END,
                    f"ERROR | {archivo.name} | Bloqueado/en uso\n"
                )

                err += 1

            except FileExistsError:

                self.log.insert(
                    tk.END,
                    f"ERROR | {archivo.name} | Ya existe destino\n"
                )

                err += 1

            except Exception as e:

                self.log.insert(
                    tk.END,
                    f"ERROR | {archivo.name} | {str(e)}\n"
                )

                err += 1

        self.log.insert(
            tk.END,
            f"\nResumen: {ok} OK / {err} errores"
        )

        self.cargar()


# ---------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AppRenombrador(root)
    root.mainloop()