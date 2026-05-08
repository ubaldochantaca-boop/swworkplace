package com.maintenance.infrastructure.websocket;

import com.maintenance.domain.modelo.AvisoMantenimiento;
import com.maintenance.domain.repositorio.AvisoMantenimientoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.BinaryMessage;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.BinaryWebSocketHandler;
import org.springframework.web.socket.CloseStatus;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Component
public class AudioWebSocketHandler extends BinaryWebSocketHandler {

    @Autowired
    private VoskService voskService;

    @Autowired
    private AvisoMantenimientoRepository avisoRepository;

    @Override
    protected void handleBinaryMessage(WebSocketSession session, BinaryMessage message) throws Exception {
        try {
            byte[] audioData = new byte[message.getPayload().remaining()];
            message.getPayload().get(audioData);
            
            // 1. Transcribir (VoskService ahora es persistente, gracias al cambio anterior)
            String jsonTexto = voskService.transcribeAudio(audioData);
            
            if (jsonTexto != null && !jsonTexto.trim().isEmpty()) {
                System.out.println("Texto reconocido: " + jsonTexto);
                
                // 2. LA CLAVE: Detectar si es un resultado final para guardarlo en DB
                if (jsonTexto.contains("\"text\"")) {
                    String textoLimpio = extraerTextoJson(jsonTexto);
                    
                    if (!textoLimpio.isEmpty()) {
                        AvisoMantenimiento aviso = new AvisoMantenimiento();
                        aviso.setDescripcion(textoLimpio);
                        
                        // Guardar en PostgreSQL
                        avisoRepository.save(aviso);
                        System.out.println("✅ REGISTRO GUARDADO EN POSTGRES: " + textoLimpio);
                    }
                }
                
                // Enviar respuesta al cliente (Python/Frontend)
                session.sendMessage(new TextMessage(jsonTexto));
            }
        } catch (Exception e) {
            System.err.println("Error procesando audio: " + e.getMessage());
        }
    }

    /**
     * Utilidad para limpiar el JSON de Vosk {"text": "..."} y obtener solo el string
     */
    private String extraerTextoJson(String json) {
        Pattern pattern = Pattern.compile("\"text\"\\s*:\\s*\"([^\"]+)\"");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return "";
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        System.out.println("Cliente conectado: " + session.getId());
        // Limpiamos el contexto de Vosk para una nueva sesión
        voskService.reset(); 
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        System.out.println("Cliente desconectado: " + session.getId());
    }
}