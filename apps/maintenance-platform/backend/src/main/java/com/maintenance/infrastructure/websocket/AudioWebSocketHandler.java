package com.maintenance.infrastructure.websocket;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.BinaryMessage;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.BinaryWebSocketHandler;
import com.maintenance.infrastructure.websocket.VoskService; // Asegúrate que este sea el path real

@Component
public class AudioWebSocketHandler extends BinaryWebSocketHandler {

    @Autowired
    private VoskService voskService;

    @Override
    protected void handleBinaryMessage(WebSocketSession session, BinaryMessage message) throws Exception {
        try {
            // Mejora: Usamos un buffer intermedio para asegurar que leemos todos los bytes correctamente
            byte[] audioData = new byte[message.getPayload().remaining()];
            message.getPayload().get(audioData);
            
            // Transcribir usando Vosk
            String texto = voskService.transcribeAudio(audioData);
            
            // Si reconoció algo, enviarlo al cliente y mostrarlo en consola
            if (texto != null && !texto.trim().isEmpty()) {
                System.out.println("Texto reconocido: " + texto);
                session.sendMessage(new TextMessage(texto));
            }
        } catch (Exception e) {
            System.err.println("Error procesando audio: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        System.out.println("Cliente conectado: " + session.getId());
        super.afterConnectionEstablished(session);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, org.springframework.web.socket.CloseStatus status) throws Exception {
        System.out.println("Cliente desconectado: " + session.getId());
        super.afterConnectionClosed(session, status);
    }
} // <--- ESTA ES LA LLAVE QUE FALTABA Y CAUSABA EL ERROR