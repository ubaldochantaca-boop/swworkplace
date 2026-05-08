package com.maintenance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
// Eliminamos @EntityScan y @EnableJpaRepositories temporalmente 
// porque Spring los detecta automáticamente si tus carpetas 
// cuelgan de "com.maintenance" (como 'com.maintenance.domain.modelo')
public class BackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);
    }
}