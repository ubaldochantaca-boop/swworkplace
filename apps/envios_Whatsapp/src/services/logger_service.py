import os
from datetime import datetime
import threading

class WhatsAppLogger:
    def __init__(self, log_path: str = "log_envio_whatsapp.txt"):
        self.log_path = log_path
        self._lock = threading.Lock()

    def registrar_evento(
        self,
        numero_destinatario: int | str,
        wa_destinatario: str,
        numero_whatsapp: str,
        estado: str,
        detalle: str = ""
    ) -> str:
        """
        Registra una línea con formato estricto en el archivo plano log_envio_whatsapp.txt:
        Timestamp | ID | Destinatario: {wa_destinatario} | WhatsApp | Estado | Detalle
        Estados válidos: 'ENVIADO', 'ERROR', 'ANOMALÍA'
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estado_clean = str(estado).strip().upper()
        if estado_clean not in ["ENVIADO", "ERROR", "ANOMALÍA"]:
            if "FALL" in estado_clean or "ERR" in estado_clean:
                estado_clean = "ERROR"
            elif "INV" in estado_clean or "OMIT" in estado_clean or "VAC" in estado_clean:
                estado_clean = "ANOMALÍA"
            else:
                estado_clean = "ENVIADO"

        id_str = str(numero_destinatario).strip() if numero_destinatario is not None else "S/N"
        dest_str = str(wa_destinatario).strip() if wa_destinatario else "Desconocido"
        wa_str = str(numero_whatsapp).strip() if numero_whatsapp else "Sin WhatsApp"
        detalle_str = str(detalle).strip() if detalle else "Operación completada"

        linea = f"[{timestamp}] | ID: {id_str} | Destinatario: {dest_str} | WhatsApp: {wa_str} | Estado: {estado_clean} | Detalle: {detalle_str}\n"

        with self._lock:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(linea)

        return linea.strip()

    def obtener_ultimas_lineas(self, limite: int = 150) -> list[str]:
        """Obtiene las líneas más recientes del log."""
        if not os.path.exists(self.log_path):
            return []
        try:
            with self._lock:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    lineas = f.readlines()
                return [l.strip() for l in lineas[-limite:] if l.strip()]
        except Exception:
            return []

    def limpiar_log(self) -> None:
        """Limpia el archivo de log para una nueva corrida si es requerido."""
        with self._lock:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(f"=== INICIO DE BITÁCORA DE ENVÍOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
