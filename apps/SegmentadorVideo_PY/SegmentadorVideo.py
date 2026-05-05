import subprocess
import os
import logging
import shutil
import sys

# ==============================
# CONFIGURAR LOG
# ==============================

logging.basicConfig(
    filename="Log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("==============================================")
print("  SISTEMA INTELIGENTE DE SEGMENTACION VIDEO")
print("==============================================\n")

# ==============================
# PEDIR TAMAÑO DE SEGMENTO
# ==============================

entrada = input("Tamaño deseado de cada segmento en MB (default 190): ").strip()

if entrada == "":
    tamaño_segmento_MB = 190
else:
    try:
        tamaño_segmento_MB = float(entrada)
    except:
        print("Valor inválido. Se usará 190 MB.")
        tamaño_segmento_MB = 190

logging.info(f"Tamaño objetivo de segmento: {tamaño_segmento_MB} MB")

# ==============================
# VERIFICAR FFMPEG
# ==============================

def verificar_ffmpeg():

    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg no está instalado o no está en el PATH")
        logging.error("ffmpeg no encontrado")
        sys.exit()

    if shutil.which("ffprobe") is None:
        print("ERROR: ffprobe no está instalado o no está en el PATH")
        logging.error("ffprobe no encontrado")
        sys.exit()

    logging.info("FFmpeg y FFprobe encontrados")

verificar_ffmpeg()

# ==============================
# SELECCIONAR VIDEO
# ==============================

archivo_video = None

print("\nSe abrirá el explorador de archivos de Windows...\n")

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

# ==============================
# VALIDAR ARCHIVO
# ==============================

if not os.path.isfile(archivo_video):

    print("ERROR: el archivo no existe.")
    logging.error("Archivo inválido")
    sys.exit()

logging.info(f"Archivo seleccionado: {archivo_video}")

# ==============================
# OBTENER DURACION
# ==============================

def obtener_duracion(video):

    comando = [
        "ffprobe",
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

        logging.error("Error obteniendo información del video")
        print("No se pudo leer información del video.")
        sys.exit()

    return float(resultado.stdout.strip())

duracion = obtener_duracion(archivo_video)

logging.info(f"Duración del video: {duracion} segundos")

# ==============================
# OBTENER TAMAÑO DEL ARCHIVO
# ==============================

tamano_bytes = os.path.getsize(archivo_video)

tamano_MB = tamano_bytes / (1024 * 1024)

logging.info(f"Tamaño archivo: {tamano_MB:.2f} MB")

# ==============================
# CALCULAR SEGMENTO
# ==============================

segundos_por_segmento = duracion * (tamaño_segmento_MB / tamano_MB)

logging.info(f"Segmento estimado en segundos: {segundos_por_segmento}")

# ==============================
# GENERAR RUTA DE SALIDA
# ==============================

directorio_video = os.path.dirname(os.path.abspath(archivo_video))

nombre_base = os.path.splitext(os.path.basename(archivo_video))[0]

salida = os.path.join(directorio_video, nombre_base + "_%03d.mp4")

logging.info(f"Archivos de salida: {salida}")

# ==============================
# EJECUTAR FFMPEG
# ==============================

print("\nProcesando video...\n")

comando = [
    "ffmpeg",
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

    print("Ocurrió un error durante el procesamiento.")
    logging.error("Error ejecutando ffmpeg")

else:

    print("\nProceso completado sin errores.")
    print("Los segmentos se encuentran en:\n")
    print(directorio_video)

    logging.info("Proceso completado correctamente")

print("\nRevise Log.txt para más detalles.")