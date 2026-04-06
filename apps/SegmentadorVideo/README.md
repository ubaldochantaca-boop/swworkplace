# Segmentador de Video con FFmpeg

## Objetivo

Este proyecto proporciona una herramienta sencilla para dividir archivos
de video en múltiples segmentos de tamaño aproximado definido por el
usuario.

El sistema utiliza FFmpeg para realizar la segmentación sin recodificar
el video, lo que permite que el proceso sea rápido y conserve la calidad
original.

## Sistema objetivo

El software fue diseñado principalmente para:

-   Windows 10 / Windows 11
-   Python 3.9 o superior

También puede ejecutarse como ejecutable `.exe` sin necesidad de tener
Python instalado.

------------------------------------------------------------------------

# Arquitectura del sistema

Arquitectura simplificada:

Usuario\
↓\
Script Python\
↓\
Cálculo de duración y tamaño del video\
↓\
Generación del comando FFmpeg\
↓\
Ejecución de FFmpeg\
↓\
Segmentación del video

Componentes principales:

-   Python (control del flujo)
-   Tkinter (selector de archivos)
-   FFprobe (obtención de metadatos)
-   FFmpeg (segmentación)

------------------------------------------------------------------------

# Requerimientos

## Requerimientos mínimos

-   Windows 10 o superior
-   FFmpeg
-   FFprobe

## Si se ejecuta como script

-   Python 3.9+

## Si se ejecuta como EXE

-   No requiere Python
-   Solo FFmpeg

------------------------------------------------------------------------

# Ventajas

-   No recodifica el video
-   Muy rápido
-   Portable
-   Fácil de usar

------------------------------------------------------------------------

# Desventajas

-   Tamaño de segmento aproximado
-   Depende de FFmpeg
-   Interfaz gráfica mínima

------------------------------------------------------------------------

# Crear el ejecutable

Instalar PyInstaller:

    pip install pyinstaller

Luego ejecutar:

    pyinstaller --onefile SegmentadorVideo.py

El ejecutable aparecerá en:

    dist/SegmentadorVideo.exe

------------------------------------------------------------------------

# Opciones de transportabilidad

## Con Python

    python SegmentadorVideo.py

## Sin Python

    SegmentadorVideo.exe

## Portable completo

Colocar en la misma carpeta:

    SegmentadorVideo.exe
    ffmpeg.exe
    ffprobe.exe
