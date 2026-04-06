
"""
SegmentadorVideo.py
-------------------------------------------------------------
Sistema Inteligente de Segmentación de Video usando FFmpeg.

Autor: Proyecto educativo
Descripción:
Este script permite dividir un archivo de video en múltiples
segmentos de tamaño aproximado definido por el usuario (en MB).

Características principales:
- Selección de archivo mediante ventana gráfica (Tkinter).
- Cálculo automático del tiempo de segmento basado en tamaño.
- Uso de FFmpeg sin recodificación (copia de streams).
- Generación de logs para auditoría del proceso.
- Compatibilidad con ejecución como script Python o ejecutable (.EXE).
- Búsqueda automática de ffmpeg y ffprobe:
    1) En la carpeta del programa
    2) En el PATH del sistema

Requerimientos:
- Python 3.9+ (si se ejecuta como script)
- FFmpeg y FFprobe
"""

import subprocess
import os
import logging
import shutil
import sys

# ======================================================
# CONFIGURACIÓN DE LOG
# ======================================================

logging.basicConfig(
    filename="Log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("==============================================")
print("  SISTEMA INTELIGENTE DE SEGMENTACION VIDEO")
print("==============================================\n")

logging.info("Inicio del programa")

# ======================================================
# DETECTAR RUTA DEL PROGRAMA
# ======================================================

if getattr(sys, 'frozen', False):
    ruta_programa = os.path.dirname(sys.executable)
else:
    ruta_programa = os.path.dirname(os.path.abspath(__file__))

# ======================================================
# LOCALIZAR FFMPEG
# ======================================================

def localizar_ffmpeg():
    """Busca ffmpeg y ffprobe primero localmente y luego en PATH."""

    ffmpeg_local = os.path.join(ruta_programa, "ffmpeg.exe")
    ffprobe_local = os.path.join(ruta_programa, "ffprobe.exe")

    if os.path.exists(ffmpeg_local) and os.path.exists(ffprobe_local):
        logging.info("Usando FFmpeg local")
        return ffmpeg_local, ffprobe_local

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        logging.info("Usando FFmpeg del sistema")
        return "ffmpeg", "ffprobe"

    print("ERROR: FFmpeg no está disponible.")
    print("Coloque ffmpeg.exe y ffprobe.exe junto al programa.")
    logging.error("FFmpeg no encontrado")
    sys.exit()

ffmpeg_cmd, ffprobe_cmd = localizar_ffmpeg()

# ======================================================
# SOLICITAR TAMAÑO DE SEGMENTO
# ======================================================

entrada = input("Tamaño deseado de cada segmento en MB (default 190): ").strip()

if entrada == "":
    tamaño_segmento_MB = 190
else:
    try:
        tamaño_segmento_MB = float(entrada)
    except:
        print("Valor inválido. Se usará 190 MB.")
        tamaño_segmento_MB = 190

logging.info(f"Tamaño objetivo: {tamaño_segmento_MB} MB")

# ======================================================
# SELECCIONAR VIDEO
# ======================================================

archivo_video = None

print("\nSe abrirá el explorador de archivos...\n")

try:
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    archivo_video = askopenfilename(
        title="Seleccionar video",
        filetypes=[("Videos", "*.mp4 *.mkv *.mov *.avi")]
    )

    root.destroy()

except Exception as e:
    logging.error(f"Error usando selector gráfico: {e}")
    print("No se pudo usar el selector gráfico.")

if not archivo_video:
    archivo_video = input("Ingrese la ruta completa del archivo de video: ").strip()

# ======================================================
# VALIDAR ARCHIVO
# ======================================================

if not os.path.isfile(archivo_video):
    print("ERROR: archivo inválido.")
    logging.error("Archivo no existe")
    sys.exit()

logging.info(f"Archivo seleccionado: {archivo_video}")

# ======================================================
# OBTENER DURACIÓN DEL VIDEO
# ======================================================

def obtener_duracion(video):

    comando = [
        ffprobe_cmd,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video
    ]

    resultado = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if resultado.returncode != 0:
        logging.error("Error leyendo duración del video")
        print("No se pudo obtener información del video.")
        sys.exit()

    return float(resultado.stdout.strip())

duracion = obtener_duracion(archivo_video)
logging.info(f"Duración video: {duracion} segundos")

# ======================================================
# CALCULAR SEGMENTO
# ======================================================

tamano_bytes = os.path.getsize(archivo_video)
tamano_MB = tamano_bytes / (1024 * 1024)

segundos_por_segmento = duracion * (tamaño_segmento_MB / tamano_MB)

logging.info(f"Segmento estimado: {segundos_por_segmento} segundos")

# ======================================================
# DEFINIR SALIDA
# ======================================================

directorio_video = os.path.dirname(os.path.abspath(archivo_video))
nombre_base = os.path.splitext(os.path.basename(archivo_video))[0]

salida = os.path.join(directorio_video, nombre_base + "_%03d.mp4")

# ======================================================
# EJECUTAR FFMPEG
# ======================================================

print("\nProcesando video...\n")

comando = [
    ffmpeg_cmd,
    "-i",
    archivo_video,
    "-c",
    "copy",
    "-map",
    "0",
    "-segment_time",
    str(segundos_por_segmento),
    "-f",
    "segment",
    salida
]

proceso = subprocess.run(comando)

if proceso.returncode != 0:
    print("ERROR durante el procesamiento.")
    logging.error("Error ejecutando ffmpeg")
else:
    print("\nProceso completado correctamente.")
    print("Segmentos generados en:")
    print(directorio_video)
    logging.info("Segmentación completada")

print("\nRevise Log.txt para más detalles.")
