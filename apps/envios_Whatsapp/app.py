import os
import sys
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from dotenv import load_dotenv

from src.services.excel_manager import DirectorioManager
from src.services.evolution_client import EvolutionClient
from src.services.logger_service import WhatsAppLogger
from src.services.dispatch_engine import DispatchEngine

# Detección de entorno normal vs empaquetado (PyInstaller .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

# Cargar variables de entorno desde config.env junto al ejecutable
env_file_path = os.path.join(EXE_DIR, 'config.env')
if not os.path.exists(env_file_path):
    env_file_path = os.path.join(BASE_DIR, 'config.env')
load_dotenv(env_file_path)

EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://localhost:8080")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "ubaldon8n")
EVOLUTION_APIKEY = os.getenv("EVOLUTION_APIKEY", "")

excel_name = os.getenv("EXCEL_FILE", "Directorio_Destinatarios.xlsx")
EXCEL_FILE = excel_name if os.path.isabs(excel_name) else os.path.join(EXE_DIR, excel_name)

log_name = os.getenv("LOG_FILE", "log_envio_whatsapp.txt")
LOG_FILE = log_name if os.path.isabs(log_name) else os.path.join(EXE_DIR, log_name)

SEND_DELAY = float(os.getenv("SEND_DELAY", "1.5"))

# Instanciar servicios
excel_manager = DirectorioManager(excel_path=EXCEL_FILE)
evolution_client = EvolutionClient(api_url=EVOLUTION_URL, instance=EVOLUTION_INSTANCE, api_key=EVOLUTION_APIKEY)
logger_service = WhatsAppLogger(log_path=LOG_FILE)
dispatch_engine = DispatchEngine(evolution_client=evolution_client, logger=logger_service, send_delay=SEND_DELAY)

# Aplicación FastAPI
app = FastAPI(title="Despacho WhatsApp Web", version="2.0.0")

# Plantillas HTML (dentro del paquete o directorio del proyecto)
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Modelos Pydantic
class NuevoDestinatarioPayload(BaseModel):
    wa_destinatario: str
    nombre: Optional[str] = ""
    numero_whatsapp: str
    tipo: Optional[str] = "Persona"
    institucion: Optional[str] = ""
    cliente: Optional[str] = ""
    profesion: Optional[str] = ""
    clave_busqueda: Optional[str] = ""

class IniciarEnvioPayload(BaseModel):
    mensaje: Optional[str] = ""
    destinatarios: List[Dict[str, Any]]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "instance_name": EVOLUTION_INSTANCE,
            "excel_file": EXCEL_FILE,
            "log_file": LOG_FILE
        }
    )

@app.get("/api/config")
async def get_config():
    return {
        "evolution_url": EVOLUTION_URL,
        "evolution_instance": EVOLUTION_INSTANCE,
        "excel_file": EXCEL_FILE,
        "log_file": LOG_FILE,
        "send_delay": SEND_DELAY
    }

@app.get("/api/health")
async def health_check():
    """Verifica estado de salud de la instancia Evolution API."""
    estado = await evolution_client.verificar_estado_instancia()
    return estado

@app.get("/api/destinatarios")
async def get_destinatarios():
    """Obtiene el catálogo de destinatarios y los valores únicos para los 5 selectores."""
    contactos = excel_manager.obtener_todos()
    selectores = excel_manager.obtener_valores_selectores()
    return {
        "total": len(contactos),
        "contactos": contactos,
        "selectores": selectores
    }

@app.post("/api/destinatarios")
async def create_destinatario(payload: NuevoDestinatarioPayload):
    """Da de alta un nuevo destinatario en Directorio_Destinatarios.xlsx."""
    if not payload.wa_destinatario.strip():
        raise HTTPException(status_code=400, detail="El nombre del destinatario (wa_destinatario) es obligatorio.")
    if not payload.numero_whatsapp.strip():
        raise HTTPException(status_code=400, detail="El número o JID de WhatsApp es obligatorio.")
    
    nuevo = excel_manager.agregar_destinatario(payload.model_dump())
    return {"status": "ok", "destinatario": nuevo}

@app.post("/api/envio/iniciar")
async def iniciar_envio(payload: IniciarEnvioPayload, background_tasks: BackgroundTasks):
    """Inicia el despacho en segundo plano a los destinatarios seleccionados."""
    if dispatch_engine.is_running:
        raise HTTPException(status_code=409, detail="Ya hay un envío en curso.")
    
    if not payload.destinatarios:
        raise HTTPException(status_code=400, detail="No se seleccionó ningún destinatario.")
        
    tiene_mensaje_comun = bool(payload.mensaje and payload.mensaje.strip())
    tiene_mensajes_individuales = any(
        bool(d.get("mensaje_personalizado") and str(d.get("mensaje_personalizado")).strip())
        for d in payload.destinatarios
    )

    if not tiene_mensaje_comun and not tiene_mensajes_individuales:
        raise HTTPException(status_code=400, detail="Debe ingresar un mensaje común o asignar mensajes individuales a los destinatarios.")

    # Lanzar tarea en segundo plano
    background_tasks.add_task(
        dispatch_engine.iniciar_despacho,
        destinatarios=payload.destinatarios,
        mensaje_texto=payload.mensaje or ""
    )

    return {
        "status": "iniciado",
        "total": len(payload.destinatarios),
        "mensaje": f"Despacho iniciado para {len(payload.destinatarios)} destinatarios."
    }

@app.post("/api/envio/detener")
async def detener_envio():
    """Detiene el envío en curso."""
    if not dispatch_engine.is_running:
        return {"status": "no_activo", "mensaje": "No hay ningún envío en ejecución."}
    dispatch_engine.stop()
    return {"status": "deteniendo", "mensaje": "Solicitud de detención enviada."}

@app.get("/api/envio/estado")
async def obtener_estado():
    """Consulta el estado del motor de despacho."""
    porcentaje = int((dispatch_engine.current / dispatch_engine.total) * 100) if dispatch_engine.total > 0 else 0
    return {
        "is_running": dispatch_engine.is_running,
        "total": dispatch_engine.total,
        "current": dispatch_engine.current,
        "porcentaje": porcentaje,
        "enviados": dispatch_engine.enviados,
        "errores": dispatch_engine.errores,
        "anomalias": dispatch_engine.anomalias
    }

@app.get("/api/log/texto")
async def obtener_log_texto():
    """Obtiene las líneas recientes de la bitácora plana."""
    lineas = logger_service.obtener_ultimas_lineas(100)
    return {"lineas": lineas}

@app.get("/api/log/descargar")
async def descargar_log():
    """Descarga el archivo plano log_envio_whatsapp.txt."""
    if not os.path.exists(LOG_FILE):
        # Crear archivo vacío si no existe
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
    return FileResponse(
        path=LOG_FILE,
        filename="log_envio_whatsapp.txt",
        media_type="text/plain"
    )

@app.websocket("/ws/progreso")
async def websocket_progreso(websocket: WebSocket):
    """Canal WebSocket para streaming en tiempo real de logs y progreso."""
    await websocket.accept()
    queue = dispatch_engine.subscribe()
    try:
        # Enviar estado actual de inmediato
        porcentaje = int((dispatch_engine.current / dispatch_engine.total) * 100) if dispatch_engine.total > 0 else 0
        await websocket.send_json({
            "type": "init",
            "data": {
                "is_running": dispatch_engine.is_running,
                "total": dispatch_engine.total,
                "current": dispatch_engine.current,
                "porcentaje": porcentaje,
                "enviados": dispatch_engine.enviados,
                "errores": dispatch_engine.errores,
                "anomalias": dispatch_engine.anomalias
            }
        })

        while True:
            try:
                # Esperar evento de la cola con timeout para mantener vivo el socket
                msg = await asyncio.wait_for(queue.get(), timeout=20.0)
                await websocket.send_json(msg)
            except asyncio.TimeoutError:
                # Heartbeat ping
                await websocket.send_json({"type": "ping", "data": {}})
    except (WebSocketDisconnect, ConnectionResetError):
        pass
    except Exception:
        pass
    finally:
        dispatch_engine.unsubscribe(queue)

if __name__ == "__main__":
    import multiprocessing
    import webbrowser
    import threading
    import time
    import uvicorn

    multiprocessing.freeze_support()

    def _abrir_navegador():
        time.sleep(1.2)
        try:
            webbrowser.open("http://localhost:8000")
        except Exception:
            pass

    threading.Thread(target=_abrir_navegador, daemon=True).start()

    print("=======================================================================")
    print("      SISTEMA DE DESPACHO WHATSAPP (CATÁLOGO EXCEL Y WEB)")
    print("=======================================================================")
    print(" [OK] Servidor iniciado correctamente.")
    print(" [OK] Abriendo navegador en: http://localhost:8000")
    print(f" [OK] Conectando con WhatsApp Engine: {EVOLUTION_URL} ({EVOLUTION_INSTANCE})")
    print(" [INFO] Para cerrar la aplicación, cierra esta ventana.")
    print("=======================================================================\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
