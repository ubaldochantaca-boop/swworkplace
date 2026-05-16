# API Prueba Técnica - Spring Boot

## Descripción
Este proyecto es una API desarrollada con **Spring Boot** que implementa una arquitectura backend sencilla orientada a servicios.  
El objetivo del proyecto es demostrar la creación de servicios, manejo de dependencias con **Maven** y ejecución de una aplicación Java moderna basada en **Spring Boot**.
El proyecto forma parte de un ejercicio técnico para validar habilidades en:
- Desarrollo Backend con Java
- Spring Boot
- Maven- Git / GitHub
- Ejecución en entornos Linux 

# Tecnologías utilizadas
- Java 21
- Spring Boot- Maven
- Git- GitHub
- Linux / Ubuntu

# Arquitectura del proyecto
El proyecto sigue una estructura típica de aplicaciones Spring Boot.

spring-boot-tutorial  
│  
├── src  
│ ├── main  
│ │ ├── java  
│ │ │ └── com.codewithmosh.store  
│ │ │ ├── StoreApplication.java  
│ │ │ ├── OrderService.java  
│ │ │ └── Otros componentes  
│ │ │  
│ │ └── resources  
│ │ └── application.properties  
│ │  
│ └── test  
│  
├── pom.xml  
└── README.md

### Componentes principales
| Componente | Descripción |
|------------|-------------|
| StoreApplication | Clase principal que inicia la aplicación Spring Boot |
| Services | Lógica de negocio |
| Resources | Configuración del sistema |

# Requisitos del sistema
Para ejecutar el proyecto se requiere:

| Software | Versión recomendada |
|--------|----------------|
| Java | 21 |
| Maven | 3.9+ || Git | 2.x || Sistema operativo | Linux / Windows / Mac |

Verificar versiones:
java -version
mvn -version
git --version

# Instalación del proyecto
## 1 Clonar el repositorio
git clone https://github.com/nygma2004/km.git

## 2 Entrar al directorio del proyecto
cd km

## 3 Navegar al módulo backend
cd sap_gui_scripting

o dependiendo de la estructura:

cd apps/backend/spring-boot-tutorial

# Compilación del proyecto
Para compilar el proyecto ejecutar:

mvn clean install

Esto realizará:

- limpieza del proyecto
- descarga de dependencias
- compilación
- ejecución de pruebas
- generación del artefacto

# Ejecución de la aplicación
Existen dos formas de ejecutar la aplicación.

## Método 1 (recomendado)
mvn spring-boot:run

## Método 2
Compilar primero:

mvn clean package

Luego ejecutar:

java -jar target/api-prueba-tecnica.jar

# Puertos y acceso
Por defecto Spring Boot ejecuta la aplicación en:

http://localhost:8080


# Buenas prácticas aplicadas
Este proyecto sigue varias buenas prácticas de desarrollo profesional:

### Uso de Spring Boot
- Auto configuración
- Inyección de dependencias
- Gestión de Beans

### Uso de Maven
- Gestión centralizada de dependencias
- Reproducibilidad de builds

### Control de versiones
- Uso de Git
- Uso de ramas para desarrollo
- Pull Requests para integración

### Organización del código
Separación de responsabilidades:

- Controllers
- Services
- Configuración


# Troubleshooting
## Error común: ApplicationContext
Si aparece un error como:

ConfigurableApplicationContext cannot be converted to ApplicationContext

Verificar que el import correcto sea:

org.springframework.context.ApplicationContext
y no:
org.apache.catalina.core.ApplicationContext

# Buen flujo de trabajo con Git
Se recomienda no trabajar directamente en `main`.

Crear siempre una rama:

git checkout -b fix/nombre-del-cambio

Luego:
git add .git commit -m "Descripción del cambio"git push origin fix/nombre-del-cambio

Posteriormente crear un **Pull Request** hacia `main`.

# Resumen rápido para recrear el proyecto
Paso a paso mínimo para descargar y ejecutar el proyecto desde cero.

### 1 Clonar repositorio
git clone https://github.com/nygma2004/km.git

### 2 Entrar al proyecto
cd km/apps/backend/spring-boot-tutorial

### 3 Compilar
mvn clean install

### 4 Ejecutar aplicación
mvn spring-boot:run
o
java -jar target/api-prueba-tecnica.jar

### 5 Abrir en navegador
http://localhost:8080

# Autor/Referencia
- Proyecto desarrollado como parte de una prueba técnica de backend utilizando **Spring Boot**.
- https://www.youtube.com/watch?v=gJrjgg1KVL4&t=4065s