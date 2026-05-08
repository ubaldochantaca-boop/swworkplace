package com.maintenance.domain.repositorio;

import com.maintenance.domain.modelo.AvisoMantenimiento;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AvisoMantenimientoRepository extends JpaRepository<AvisoMantenimiento, Long> {
    // JpaRepository ya incluye métodos como .save(), .findAll(), .delete()
}