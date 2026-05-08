package com.maintenance.domain.modelo;

import jakarta.persistence.*; // Importante: usar jakarta para Spring Boot 3
import lombok.Data;

@Entity
@Table(name = "avisos_mantenimiento") // Forzamos el nombre de la tabla
@Data
public class AvisoMantenimiento {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String descripcion;
    // ... otros campos
}