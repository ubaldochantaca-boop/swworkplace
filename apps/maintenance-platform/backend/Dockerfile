# ETAPA 1: Compilación (Usamos una imagen estándar de Maven con Java 17)
FROM maven:3-eclipse-temurin-17 AS build
WORKDIR /app

# Copiamos solo el archivo de configuración primero
COPY pom.xml .
# Descargamos las librerías necesarias
RUN mvn dependency:go-offline -B

# Copiamos el código fuente y fabricamos el ejecutable
# Cambio para forzar recompilacion 2026
COPY src ./src
RUN mvn clean package -DskipTests

# ETAPA 2: Ejecución (Imagen oficial de Java 17)
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
# Bandera de seguridad para acelerar el arranque
ENTRYPOINT ["java", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]