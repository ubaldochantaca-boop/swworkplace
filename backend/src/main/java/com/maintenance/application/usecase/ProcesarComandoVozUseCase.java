package com.maintenance.application.usecase;

import org.springframework.stereotype.Service;

@Service
public class ProcesarComandoVozUseCase {

    public String ejecutar(String comando) {
        return "Procesado: " + comando;
    }
}