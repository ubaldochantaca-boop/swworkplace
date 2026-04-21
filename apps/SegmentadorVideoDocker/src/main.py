import os
import subprocess
import logging
import sys

# ==========================================================
# ARQUITECTURA DEVOPS - SEGMENTADOR PROFESIONAL PORTABLE
# Proyecto: SegmentadorVideoDocker
# ==========================================================

# #ucz: Update - Configuración dinámica mediante variables de entorno
# Prioriza la inyección de Docker; fallback automático para ejecución local (.exe)
LOGFILE = os.getenv("LOGFILE", os.path.join("output", "LOG.txt"))
VIDEO_IN = os.getenv("VIDEO_INPUT", "video_prueba.mp4")
SEGMENT_TIME = os.getenv("SEGMENT_TIME", "60")
OUTPUT_DIR = os.getenv("OUTPUT_FOLDER", "output")

# #ucz: Update - Asegurar persistencia y existencia de rutas
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Configuración técnica de logs
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def ejecutar_segmentacion():
    print("==============================================")
    print("  SISTEMA INTELIGENTE DE SEGMENTACION VIDEO")
    print("==============================================\n")
    logging.info("Inicio del proceso de segmentación.")

    # #ucz: Update - Lógica de detección de motor FFmpeg (Evita dependencia de PATH)
    # 1. Intenta usar el binario local del paquete portable
    ffmpeg_path = os.path.join("bin", "ffmpeg.exe")
    
    # 2. Si no existe localmente, asume que está en el sistema (Entorno Docker)
    if not os.path.exists(ffmpeg_path):
        ffmpeg_path = "ffmpeg"

    # Verificación de integridad del motor
    try:
        subprocess.run([ffmpeg_path, "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info(f"Motor FFmpeg validado en ruta: {ffmpeg_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("FFmpeg no detectado. Verifique la carpeta 'bin/' o la instalación del contenedor.")
        print("ERROR CRÍTICO: FFmpeg no encontrado.")
        sys.exit(1)

    # Verificación de archivo de entrada
    if not os.path.exists(VIDEO_IN):
        logging.error(f"Archivo de entrada ausente: {VIDEO_IN}")
        print(f"ERROR: No se encontró el video '{VIDEO_IN}' en la raíz.")
        sys.exit(1)

    # Construcción de rutas de salida
    nombre_base = os.path.splitext(os.path.basename(VIDEO_IN))
    videoout = os.path.join(OUTPUT_DIR, f"{nombre_base}_part%03d.mp4")

    print(f"➤ Procesando: {VIDEO_IN}")
    print(f"➤ Tiempo por segmento: {SEGMENT_TIME}s")
    print(f"➤ Directorio de salida: {OUTPUT_DIR}/")
    print("\n[Tratando datos sensual y rápidamente...]\n")

    # Comando FFmpeg optimizado con '-c copy' para velocidad instantánea
    cmd = [
        ffmpeg_path,
        "-i", VIDEO_IN,
        "-c", "copy",
        "-map", "0",
        "-segment_time", str(SEGMENT_TIME),
        "-f", "segment",
        videoout
    ]

    try:
        logging.info(f"Ejecutando comando FFmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Conteo de archivos para reporte final
        archivos_creados = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(nombre_base) and f.endswith(".mp4")]
        
        print("\n====================================")
        print("      PROCESO FINALIZADO CON ÉXITO")
        print(f"  Segmentos generados: {len(archivos_creados)}")
        print("====================================\n")
        logging.info(f"Segmentación completada. Archivos generados: {len(archivos_creados)}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error en ejecución de motor FFmpeg: {e}")
        print("\n[!] Fallo crítico durante la segmentación. Revise LOG.txt.")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_segmentacion()