# ETAPA 1: Compilación
FROM maven:3-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn clean package -DskipTests

# ETAPA 2: Ejecución
FROM eclipse-temurin:17-jre
WORKDIR /app

# --- NUEVAS LÍNEAS CRÍTICAS ---
# Creamos la carpeta donde el código buscará el modelo
RUN mkdir -p /app/models/model-es
# Copiamos el modelo directamente desde tu carpeta src a la imagen final
COPY --from=build /app/src/main/resources/model-es /app/models/model-es
# ------------------------------

COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]