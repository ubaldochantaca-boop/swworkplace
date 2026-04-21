import subprocess
import os
import logging
import sys

try:
    from tkinter import Tk, filedialog
    TK_AVAILABLE = True
except:
    TK_AVAILABLE = False


LOGFILE = "LOG.txt"

logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("==============================================")
print("  SISTEMA INTELIGENTE DE SEGMENTACION VIDEO")
print("==============================================\n")

logging.info("Inicio del proceso")


# -------------------------------------------------
# Solicitar tamaño segmento
# -------------------------------------------------

entrada = input("Tamaño deseado de cada segmento en MB (default 190): ")

if entrada.strip() == "":
    target_size_mb = 190
else:
    target_size_mb = float(entrada)

logging.info(f"Tamaño objetivo de segmento: {target_size_mb} MB")


# -------------------------------------------------
# Verificar FFmpeg
# -------------------------------------------------

try:

    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["ffprobe", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    logging.info("FFmpeg y ffprobe encontrados")

except:

    print("ERROR: FFmpeg no está instalado o no está en PATH.")
    logging.error("FFmpeg no encontrado")
    sys.exit(1)


# -------------------------------------------------
# Selección archivo
# -------------------------------------------------

videoin = None

if TK_AVAILABLE:

    try:

        print("\nIntentando abrir explorador de archivos...\n")

        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        videoin = filedialog.askopenfilename(
            title="Seleccione el archivo de video",
            filetypes=[("Videos", "*.mp4 *.mkv *.avi *.mov")]
        )

        root.destroy()

    except Exception as e:

        logging.error(f"Error usando selector gráfico: {str(e)}")
        videoin = None


# -------------------------------------------------
# Fallback manual
# -------------------------------------------------

while not videoin:

    videoin = input("\nIngrese la ruta completa del archivo de video: ")

    videoin = videoin.strip('"')

    if os.path.isdir(videoin):

        print("\nERROR: Ingresaste una carpeta, no un archivo.")
        videoin = None
        continue

    if not os.path.exists(videoin):

        print("\nERROR: El archivo no existe.")
        videoin = None
        continue


logging.info(f"Archivo seleccionado: {videoin}")


# -------------------------------------------------
# Obtener info video
# -------------------------------------------------

try:

    duracion_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        videoin
    ]

    duracion = float(subprocess.check_output(duracion_cmd).decode().strip())

    size_bytes = os.path.getsize(videoin)

    size_mb = size_bytes / (1024 * 1024)

    bitrate_total = size_mb / duracion

    logging.info(f"Duración video: {duracion}")
    logging.info(f"Tamaño video: {size_mb}")

except Exception as e:

    logging.error("Error obteniendo información del video")
    print("\nERROR: No se pudo leer información del video.")
    sys.exit(2)


# -------------------------------------------------
# Calcular duración segmentos
# -------------------------------------------------

segment_time = int(target_size_mb / bitrate_total)

logging.info(f"Segment time: {segment_time}")


# -------------------------------------------------
# Nombres salida
# -------------------------------------------------

directorio = os.path.dirname(videoin)

nombre_base = os.path.splitext(os.path.basename(videoin))[0]

videoout = os.path.join(directorio, nombre_base + "_part%03d.mp4")


# -------------------------------------------------
# Mostrar resumen
# -------------------------------------------------

print("\nResumen del video")
print("-----------------------------")

print("Archivo:", nombre_base)
print("Duración:", round(duracion/60,2), "minutos")
print("Tamaño:", round(size_mb,2), "MB")
print("Duración segmento:", segment_time, "segundos")

print()


# -------------------------------------------------
# Ejecutar FFmpeg
# -------------------------------------------------

cmd = [
    "ffmpeg",
    "-i", videoin,
    "-c", "copy",
    "-map", "0",
    "-segment_time", str(segment_time),
    "-f", "segment",
    videoout
]

print("Procesando video...\n")

logging.info("Ejecutando FFmpeg")

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

for line in process.stdout:

    if "time=" in line:

        try:

            tiempo = line.split("time=")[1].split(" ")[0]

            h, m, s = tiempo.split(":")
            segundos = float(h)*3600 + float(m)*60 + float(s)

            progreso = (segundos / duracion) * 100

            print(f"\rProgreso: {progreso:5.2f}%", end="")

        except:
            pass

    logging.info(line.strip())


process.wait()


# -------------------------------------------------
# Verificar salida
# -------------------------------------------------

archivos = [
    f for f in os.listdir(directorio)
    if f.startswith(nombre_base + "_part")
]

total = len(archivos)


if total == 0:

    print("\nERROR: No se generaron archivos.")
    logging.error("No se generaron archivos")
    sys.exit(3)


print("\n\n====================================")
print("PROCESO FINALIZADO SIN ERRORES")
print("Segmentos generados:", total)
print("====================================\n")

logging.info(f"Archivos generados: {total}")
logging.info("Proceso finalizado")