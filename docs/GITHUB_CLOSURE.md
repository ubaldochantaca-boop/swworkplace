# Cierre de Actividades y Control de Versiones: Maintenance Platform
**Tags:** #GITHUB #DEVOPS #VERSIONAMIENTO #V1-00

## 1. Versión Actual: v1.0.0
Se declara este hito como la **Versión 1.0.0 (Gold Master)**. 
**Alcance:** Ingesta de audio PCM vía WebSockets, transcripción offline con Vosk y persistencia en PostgreSQL mediante JPA.

## 2. Archivo README.md (Propuesta Profesional)

Crea un archivo llamado `README.md` en la raíz de tu proyecto y pega lo siguiente:

---
# Maintenance Platform - Módulo de Voz v1.0.0

Sistema de registro de avisos de mantenimiento industrial mediante reconocimiento de voz offline, diseñado para entornos de baja conectividad y alta privacidad.

## 🛠️ Tecnologías
- **Backend:** Spring Boot 3.x, Java 17.
- **IA:** Vosk SDK (Modelos Small-ES).
- **Base de Datos:** PostgreSQL 15.
- **Contenedores:** Docker & Docker Compose.
- **Cliente de Prueba:** Python 3.12.

## 🚀 Instalación Rápida
1. Descargue el modelo Vosk en `backend/src/main/resources/model-es/`.
2. Ejecute `docker-compose up --build -d`.
3. Procese su audio con FFmpeg: `ffmpeg -i input.wav -ar 16000 -ac 1 output.wav`.
4. Ejecute el test: `python test_voz.py`.

## 📂 Estructura
- `/backend`: Lógica Hexagonal y motor IA.
- `docker-compose.yml`: Orquestación de servicios.
- `test_voz.py`: Cliente WebSocket de validación.

---

## 3. Mejores Prácticas para Recuperar Versiones
Para recuperar una versión específica (como la v1.0.0) en el futuro, GitHub y Git ofrecen mecanismos robustos:

- **Tags (Etiquetas):** Es la mejor práctica. Permite marcar puntos específicos en la historia como "Versiones".
- **Comando de recuperación:** `git checkout v1.0.0` (Esto pone tu código exactamente como estaba al momento de crear el tag).
- **Releases en GitHub:** Al subir un tag, puedes ir a la sección "Releases" en la web de GitHub y adjuntar el archivo binario o documentación extra.

## 4. Próximos Pasos y Sugerencias

### A. Uso de Branches (Ramas)
**¿Qué es?** Es una línea de tiempo paralela para desarrollar mejoras sin romper lo que ya funciona (v1.0.0).
**¿Por qué y para qué?**
- **Por qué:** Si intentas agregar Llama 3 y algo falla, la v1.0.0 sigue intacta.
- **Para qué:** Para experimentar, corregir errores (bugs) o desarrollar el Frontend por separado.
- **Comando:** `git checkout -b feature/llama3-integration`.

### B. Recomendaciones de Control de Versiones
Para no perder el control, sigue esta tabla de comandos esenciales:

| Comando | Dónde se ejecuta | Nombre | Por qué y Para qué |
| :--- | :--- | :--- | :--- |
| `git status` | Terminal Raíz | Estado | **Por qué:** Ver qué archivos cambiaron. **Para qué:** No subir basura o archivos temporales. |
| `git diff` | Terminal Raíz | Diferencia | **Por qué:** Comparar líneas de código. **Para qué:** Revisar qué editaste antes de confirmar. |
| `git commit -m "..."` | Terminal Raíz | Confirmación | **Por qué:** Guardar un hito. **Para qué:** Crear un punto de restauración con un mensaje explicativo. |
| `git log --oneline` | Terminal Raíz | Historial | **Por qué:** Ver la cronología. **Para qué:** Entender cómo evolucionó el proyecto y buscar IDs de versiones previas. |
| `git pull origin main` | Terminal Raíz | Actualización | **Por qué:** Sincronizar. **Para qué:** Traer cambios si trabajas en más de una computadora (Casa vs. Oficina). |
| `git stash` | Terminal Raíz | Reserva | **Por qué:** Tienes cambios incompletos. **Para qué:** Guardarlos temporalmente para limpiar la rama sin perder el trabajo. |

## 5. Sugerencias de Mejora Técnica
1. **Frontend:** Crear una carpeta `/frontend` con Angular para visualizar los registros de la DB en tiempo real.
2. **Clasificador IA:** Implementar un servicio que tome el texto de la v1.0.0 y lo envíe a un SLM (Llama 3.2) para extraer la criticidad del aviso.
3. **Seguridad:** Implementar un JWT (JSON Web Token) para que el WebSocket no sea abierto a cualquier persona.