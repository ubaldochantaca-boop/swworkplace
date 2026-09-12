import asyncio
from typing import List, Dict, Any
from .evolution_client import EvolutionClient
from .logger_service import WhatsAppLogger

class DispatchEngine:
    def __init__(self, evolution_client: EvolutionClient, logger: WhatsAppLogger, send_delay: float = 1.5):
        self.client = evolution_client
        self.logger = logger
        self.send_delay = send_delay
        
        self.is_running = False
        self._stop_requested = False
        self.total = 0
        self.current = 0
        self.enviados = 0
        self.errores = 0
        self.anomalias = 0
        self.active_subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.active_subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self.active_subscribers:
            self.active_subscribers.remove(queue)

    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        payload = {"type": event_type, "data": data}
        for q in list(self.active_subscribers):
            try:
                await q.put(payload)
            except Exception:
                pass

    def stop(self) -> None:
        if self.is_running:
            self._stop_requested = True

    async def iniciar_despacho(self, destinatarios: List[Dict[str, Any]], mensaje_texto: str) -> None:
        if self.is_running:
            return

        self.is_running = True
        self._stop_requested = False
        self.total = len(destinatarios)
        self.current = 0
        self.enviados = 0
        self.errores = 0
        self.anomalias = 0

        await self.broadcast("status", {
            "is_running": True,
            "total": self.total,
            "current": 0,
            "enviados": 0,
            "errores": 0,
            "anomalias": 0,
            "porcentaje": 0,
            "mensaje": f"Iniciando despacho a {self.total} destinatarios seleccionados..."
        })

        for index, item in enumerate(destinatarios):
            if self._stop_requested:
                linea_cancel = self.logger.registrar_evento(
                    "S/N", "SISTEMA", "", "ANOMALÍA", "Despacho cancelado por el usuario"
                )
                await self.broadcast("log", {"linea": linea_cancel, "estado": "ANOMALÍA"})
                break

            self.current = index + 1
            num_id = item.get("numero_destinatario", index + 1)
            col_b_nombre = str(item.get("nombre") or item.get("wa_destinatario") or "").strip() or "Destinatario"
            col_c_wa_dest = str(item.get("wa_destinatario") or item.get("nombre") or "").strip() or "Destinatario"
            dest_nombre = col_c_wa_dest
            wa_num = str(item.get("numero_whatsapp", "")).strip()

            # Determinar texto base para el destinatario:
            # Si el destinatario tiene su propio mensaje individualizado (Modo 2), se usa prioritariamente.
            # En caso contrario, se utiliza el mensaje general de la plantilla (Modo 1).
            texto_base = str(item.get("mensaje_personalizado") or "").strip()
            if not texto_base:
                texto_base = str(mensaje_texto or "").strip()

            if not texto_base:
                # Si no hay texto para este contacto, registrar anomalía y continuar
                linea_vacia = self.logger.registrar_evento(
                    numero_destinatario=num_id,
                    wa_destinatario=dest_nombre,
                    numero_whatsapp=wa_num,
                    estado="ANOMALÍA",
                    detalle="Destinatario omitido: mensaje individual vacío"
                )
                self.anomalias += 1
                await self.broadcast("log", {"linea": linea_vacia, "estado": "ANOMALÍA"})
                continue

            # Anteponer prefijo "NOMBRE: " si está activado para este contacto
            if item.get("anteponer_nombre", False):
                prefijo = f"{col_b_nombre}: "
                if not texto_base.startswith(prefijo):
                    texto_base = f"{prefijo}{texto_base}"

            # Personalización de variables dinámicas:
            nombre_para_mensaje = col_b_nombre if col_b_nombre != "Destinatario" else col_c_wa_dest
            mensaje_final = (
                texto_base
                .replace("{nombre}", col_b_nombre)
                .replace("{nombre_destinatario}", col_b_nombre)
                .replace("{wa_destinatario}", nombre_para_mensaje)
            )

            # Envío a la API
            exito, estado, detalle = await self.client.enviar_mensaje_texto(wa_num, mensaje_final)

            if estado == "ENVIADO":
                self.enviados += 1
            elif estado == "ERROR":
                self.errores += 1
            else:
                self.anomalias += 1

            # Registrar en archivo plano log_envio_whatsapp.txt
            linea_log = self.logger.registrar_evento(
                numero_destinatario=num_id,
                wa_destinatario=dest_nombre,
                numero_whatsapp=wa_num,
                estado=estado,
                detalle=detalle
            )

            porcentaje = int((self.current / self.total) * 100) if self.total > 0 else 100

            # Emitir evento en vivo al frontend
            await self.broadcast("item_processed", {
                "current": self.current,
                "total": self.total,
                "porcentaje": porcentaje,
                "enviados": self.enviados,
                "errores": self.errores,
                "anomalias": self.anomalias,
                "item": {
                    "id": num_id,
                    "wa_destinatario": dest_nombre,
                    "whatsapp": wa_num,
                    "estado": estado,
                    "detalle": detalle
                },
                "log_line": linea_log
            })

            # Pausa defensiva entre envíos si no es el último elemento
            if self.current < self.total and not self._stop_requested:
                await asyncio.sleep(self.send_delay)

        self.is_running = False
        estado_final = "CANCELADO" if self._stop_requested else "COMPLETADO"
        
        await self.broadcast("completed", {
            "is_running": False,
            "estado_final": estado_final,
            "total": self.total,
            "procesados": self.current,
            "enviados": self.enviados,
            "errores": self.errores,
            "anomalias": self.anomalias,
            "mensaje": f"Proceso {estado_final.lower()}: {self.enviados} enviados, {self.errores} errores, {self.anomalias} anomalías."
        })
