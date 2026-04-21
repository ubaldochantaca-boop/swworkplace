# 🎥 SegmentadorVideoDocker (Versión Híbrida Pro)

Este proyecto implementa un sistema de segmentación de video de alta eficiencia diseñado para ser ejecutado tanto en entornos de **contenedores (Docker)** como de forma **standalone (Portable .exe)** en Windows. La arquitectura garantiza que el programa sea "estupida y sensualmente rápido" al evitar re-codificaciones innecesarias mediante el motor FFmpeg.

## 🎯 Objetivos de la Arquitectura
*   **Portabilidad Extrema:** Funciona igual en la Lenovo Ideapad que en la ThinkPad.
*   **Higiene del Host:** El Drive C: se mantiene limpio de dependencias; todo el trabajo pesado ocurre en el Drive D: o dentro de contenedores.
*   **Independencia del PATH:** No requiere configurar variables de entorno manuales en Windows gracias al uso de rutas relativas para el motor de video.
*   **Híbrido por Diseño:** Un mismo código fuente (`main.py`) detecta si está en Docker o en modo portable.

---

## 📂 Estructura del Ecosistema
El proyecto sigue la jerarquía de directorios profesional en `D:\Github\swworkplace\apps\SegmentadorVideoDocker`:

```text
SegmentadorVideoDocker/
├── bin/                    # Binarios críticos (ffmpeg.exe para modo portable)
├── src/
│   └── main.py             # Código fuente híbrido y optimizado
├── output/                 # Resultados de segmentación y LOG.txt
├── Dockerfile              # Receta de imagen basada en Python 3.12-slim
├── docker-compose.yml      # Orquestador de desarrollo
├── requirements.txt        # Placeholder obligatorio para el Build
└── main.exe                # Artefacto final compilado
```

---

## 🚀 Guías de Operación

### 1. Desarrollo y Ejecución con Docker
Ideal para procesar videos de forma aislada y limpia.
*   **Requisito:** Tener Docker Desktop y WSL2 operativos.
*   **Comando Maestro:**
    ```bash
    docker compose up --build
    ```
*   **Nota Técnica:** El contenedor instala FFmpeg internamente y mapea las carpetas `src/` y `output/` de tu Drive D: para persistencia inmediata de datos.

### 2. Uso Portable (Standalone .exe)
Para ejecutar la aplicación sin depender de Docker ni instalar Python.
*   **Requisito:** El video debe llamarse `video_prueba.mp4` (o según se configure en el entorno) y estar en la raíz junto al `.exe`.
*   **Estructura Requerida:** El archivo `ffmpeg.exe` **debe** existir dentro de la subcarpeta `bin/`.
*   **Resultado:** Al ejecutar `main.exe`, el sistema detectará el motor local y generará los fragmentos en `output/`.

---

## 🛠 Compilación (Higiene de Compiladores)
Para no instalar PyInstaller o compiladores en Windows, generamos el `.exe` usando un contenedor efímero:

```bash
docker run --rm -v "D:\Github\swworkplace\apps\SegmentadorVideoDocker:/src" cdrx/pyinstaller-windows "pyinstaller --onefile src/main.py"
```

---

## 📝 Consideraciones DevOps (#ucz_update)
*   **Variables de Entorno:** El script prioriza `VIDEO_INPUT`, `SEGMENT_TIME` y `OUTPUT_FOLDER` si están definidas en el sistema/contenedor.
*   **Persistencia de Logs:** Todas las acciones se registran en `output/LOG.txt` para trazabilidad de errores.
*   **Build Failure:** El archivo `requirements.txt` es **obligatorio** en la raíz; aunque esté vacío, su ausencia detendrá la construcción de la imagen de Docker.
*   **Higiene Final:** Tras usar Docker, se recomienda ejecutar `docker compose down` para liberar recursos y redes virtuales.

---
**Desarrollado bajo principios de consistencia y despliegue simple.** 🚀