package com.maintenance.infrastructure.websocket;

import org.vosk.Model;
import org.vosk.Recognizer;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;
import java.io.IOException;

@Service
public class VoskService {

    private Model model;
    private Recognizer globalRecognizer;

    @PostConstruct
    public void init() throws IOException {
        // Usamos la ruta absoluta configurada en el Dockerfile
        String modelPath = "/app/models/model-es"; 
        this.model = new Model(modelPath);
        // Inicializamos el recognizer a 16kHz
        this.globalRecognizer = new Recognizer(model, 16000.0f);
        System.out.println("Vosk: Modelo y Recognizer cargados correctamente.");
    }

    /**
     * Procesa los bytes de audio. 
     * Al usar el mismo recognizer, permitimos que Vosk acumule el contexto.
     */
    public synchronized String transcribeAudio(byte[] audioData) {
        try {
            // El método acceptWaveForm con F mayúscula es correcto para la versión Java
            if (globalRecognizer.acceptWaveForm(audioData, audioData.length)) {
                String result = globalRecognizer.getResult();
                System.out.println("Vosk: [Resultado Final] " + result);
                return result;
            } else {
                String partial = globalRecognizer.getPartialResult();
                // Opcional: imprimir solo si hay contenido para no saturar el log
                return partial;
            }
        } catch (Exception e) {
            System.err.println("Error en Vosk durante la transcripción: " + e.getMessage());
            return "{\"error\":\"fallo en procesamiento\"}";
        }
    }

    /**
     * Método para resetear el recognizer si es necesario (limpiar contexto)
     */
    public void reset() {
        if (globalRecognizer != null) {
            globalRecognizer.reset();
        }
    }

    @PreDestroy
    public void cleanup() {
        if (globalRecognizer != null) {
            globalRecognizer.close();
        }
        if (model != null) {
            model.close();
        }
        System.out.println("Vosk: Recursos liberados.");
    }
}