import re
import httpx

class EvolutionClient:
    def __init__(self, api_url: str, instance: str, api_key: str):
        self.api_url = str(api_url).rstrip('/')
        self.instance = str(instance).strip()
        self.api_key = str(api_key).strip()
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def normalizar_destino(self, valor: str) -> tuple[str, str, str | None]:
        """
        Normaliza el destino.
        Retorna una tupla: (destino_normalizado, tipo_detectado, error_o_anomalia)
        Si error_o_anomalia no es None, se considera una 'ANOMALÍA'.
        """
        if not valor:
            return "", "Desconocido", "Número o ID de WhatsApp vacío o ausente"

        destino = str(valor).strip()

        # Identificar grupo de WhatsApp (@g.us)
        if "@g.us" in destino:
            # Validar formato mínimo de JID de grupo
            if len(destino) < 15:
                return destino, "Grupo", "JID de grupo WhatsApp incompleto o inválido"
            return destino, "Grupo", None

        # Identificar persona individual
        destino_limpio = destino.replace("@s.whatsapp.net", "")
        destino_digitos = re.sub(r"\D", "", destino_limpio)

        if not destino_digitos:
            return "", "Persona", f"Destino sin dígitos válidos: '{valor}'"

        if len(destino_digitos) < 8:
            return destino_digitos, "Persona", f"Número telefónico demasiado corto ({len(destino_digitos)} dígitos): '{destino_digitos}'"

        return destino_digitos, "Persona", None

    async def verificar_estado_instancia(self) -> dict:
        """
        Consulta a Evolution API para comprobar si el servidor está online
        y si la instancia de WhatsApp está conectada.
        """
        url = f"{self.api_url}/instance/connectionState/{self.instance}"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    # Evolution API devuelve comúnmente { "instance": { "state": "open" } } o similar
                    state = "open"
                    if isinstance(data, dict):
                        state = data.get("instance", {}).get("state") or data.get("state") or "online"
                    return {
                        "online": True,
                        "state": state,
                        "instance": self.instance,
                        "mensaje": f"Instancia activa ({state})"
                    }
                else:
                    return {
                        "online": False,
                        "state": "error",
                        "instance": self.instance,
                        "mensaje": f"API respondió código {resp.status_code}"
                    }
        except httpx.ConnectError:
            return {
                "online": False,
                "state": "unreachable",
                "instance": self.instance,
                "mensaje": f"No se puede conectar a {self.api_url} (¿Contenedor Docker apagado?)"
            }
        except Exception as e:
            return {
                "online": False,
                "state": "error",
                "instance": self.instance,
                "mensaje": f"Error de verificación: {str(e)}"
            }

    async def enviar_mensaje_texto(self, destino: str, texto: str, delay_ms: int = 1200) -> tuple[bool, str, str]:
        """
        Envía un mensaje de texto a través del endpoint /message/sendText/{instance}.
        Retorna: (exito: bool, estado: str ['ENVIADO'|'ERROR'|'ANOMALÍA'], detalle_tecnico: str)
        """
        destino_valido, _, anomalia = self.normalizar_destino(destino)
        if anomalia:
            return False, "ANOMALÍA", anomalia

        if not str(texto).strip():
            return False, "ANOMALÍA", "El texto del mensaje está vacío"

        url = f"{self.api_url}/message/sendText/{self.instance}"
        payload = {
            "number": destino_valido,
            "text": str(texto).strip(),
            "options": {
                "delay": delay_ms,
                "presence": "composing"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                
                if response.status_code in [200, 201]:
                    return True, "ENVIADO", "Mensaje despachado y aceptado por Evolution API"
                else:
                    detalle = f"Rechazo de API (HTTP {response.status_code}): {response.text[:200]}"
                    return False, "ERROR", detalle

        except httpx.TimeoutException:
            return False, "ERROR", "Timeout: La API de WhatsApp no respondió en 15 segundos"
        except httpx.ConnectError:
            return False, "ERROR", f"Fallo de conexión: Servidor {self.api_url} inaccesible"
        except Exception as e:
            return False, "ERROR", f"Fallo técnico de comunicación: {str(e)}"
