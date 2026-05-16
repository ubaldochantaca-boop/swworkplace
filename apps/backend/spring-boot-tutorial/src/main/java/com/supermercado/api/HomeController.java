package com.supermercado.api;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class HomeController {
    @Value("${spring.application.name}")
    private String appName;

    @RequestMapping("/")
    public String index() {
        System.out.println("Bienvenido a " + appName); // Imprime el nombre de la aplicación en la consola
        return "index.html"; // Mosh indica que este es el nombre de la vista [3]
    }
}