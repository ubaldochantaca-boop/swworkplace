package com.maintenance.infrastructure.websocket;

import org.vosk.Model;
import org.vosk.Recognizer;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;
import java.io.IOException;
import java.io.ByteArrayInputStream;

@Service
public class VoskService {

    private Model model;

    @PostConstruct
    public void init() throws IOException {
        String modelPath = "/app/src/main/resources/model-es";
        this.model = new Model(modelPath);
        System.out.println("Vosk: Modelo cargado correctamente.");
    }

    public String transcribeAudio(byte[] audioData) {
        try (Recognizer recognizer = new Recognizer(model, 16000.0f)) {
            
            // LA CORRECCIÓN ESTÁ AQUÍ:
            // Solo pasamos el Stream. NO pasamos el entero con la longitud.
            if (recognizer.acceptWaveform(new ByteArrayInputStream(audioData))) {
                return recognizer.getResult();
            } else {
                return recognizer.getPartialResult();
            }
            
        } catch (Exception e) {
            System.err.println("Error en Vosk: " + e.getMessage());
            return "";
        }
    }

    @PreDestroy
    public void cleanup() {
        if (model != null) {
            model.close();
        }
    }
}