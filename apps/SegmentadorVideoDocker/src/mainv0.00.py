import subprocess
import os
import logging
import sys

# #ucz_update - El log y parámetros se obtienen del entorno Docker [16]
LOGFILE = os.getenv("LOGFILE", "output/LOG.txt")
videoin = os.getenv("VIDEO_INPUT", "video.mp4")
segment_time = os.getenv("SEGMENT_TIME", "60")
# #ucz_update - Definir la ruta del binario FFmpeg para modo portable
# Buscamos primero en la carpeta bin/ relativa al ejecutable
ffmpeg_path = os.path.join("bin", "ffmpeg.exe")

# Si no existe en bin/ (por ejemplo, cuando corre en Docker), usamos el comando global
if not os.path.exists(ffmpeg_path):
    ffmpeg_path = "ffmpeg"

logging.basicConfig(filename=LOGFILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# #ucz_update - Verificación de FFmpeg dentro del contenedor [8]
try:
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL)
    logging.info("FFmpeg detectado con éxito")
except:
    logging.error("FFmpeg no encontrado")
    sys.exit(1)

# Lógica de segmentación usando FFmpeg [8]
videoout = os.path.join("/app/output", "segmento_%03d.mp4")
#cmd = ["ffmpeg", "-i", videoin, "-c", "copy", "-map", "0", "-segment_time", str(segment_time), "-f", "segment", videoout]
cmd = [
    ffmpeg_path,  # #ucz_update - Usamos la ruta detectada arriba
    "-i", videoin,
    "-c", "copy",
    "-map", "0",
    "-segment_time", str(segment_time),
    "-f", "segment",
    videoout
]

print(f"Procesando {videoin} en segmentos de {segment_time}s...")
subprocess.run(cmd)
print("¡Proceso finalizado en Docker!")
