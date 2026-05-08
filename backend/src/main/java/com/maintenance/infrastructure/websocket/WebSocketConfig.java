// 1. Asegúrate de que el package coincida con la carpeta donde está el archivo
package com.maintenance.infrastructure.websocket; 

import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;
// 2. Si AudioWebSocketHandler está en la misma carpeta, no necesitas importarlo.
// Si está en OTRA carpeta (ej: api.websocket), añade el import aquí:
// import com.maintenance.api.websocket.AudioWebSocketHandler; 

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    private final AudioWebSocketHandler audioWebSocketHandler;

    public WebSocketConfig(AudioWebSocketHandler audioWebSocketHandler) {
        this.audioWebSocketHandler = audioWebSocketHandler;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(audioWebSocketHandler, "/audio-stream")
                .setAllowedOrigins("*");
    }
}