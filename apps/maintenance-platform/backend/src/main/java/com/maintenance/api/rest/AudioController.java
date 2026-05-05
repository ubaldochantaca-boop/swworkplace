package com.maintenance.api.rest;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class AudioController {

    @GetMapping("/test")
    public String test() {
        return "Conexión exitosa al Backend";
    }
    @GetMapping("/procesar")
    public String procesarOrden() {
        // Aquí es donde en el futuro conectarás tu lógica de IA
        return "Orden recibida. Iniciando análisis de mantenimiento con el agente SLM...";
    }
}