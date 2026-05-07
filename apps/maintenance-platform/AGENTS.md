# Codex Review Instructions

## Contexto del Proyecto
- **Arquitectura**: Hexagonal (Puertos y Adaptadores)
- **Stack**: Spring Boot 4.0.6, Java 17, Maven
- **Componente crítico**: Vosk 0.3.45 para Speech-to-Text

## Error Específico a Corregir

### Ubicación del error
- Archivo: `backend/src/main/java/com/maintenance/infrastructure/websocket/VoskService.java`
- Línea: 30
- Código actual: `recognizer.acceptWaveform(audioBytes, audioBytes.length);`

### Mensaje de error
cannot find symbol: method acceptWaveform(byte[],int)
location: variable recognizer of type org.vosk.Recognizer


### Instrucciones para Codex

1. **Analiza la API real de Vosk 0.3.45**
   - La versión es 0.3.45
   - Investiga qué métodos tiene la clase `org.vosk.Recognizer`
   - Busca cualquier método que procese audio: `acceptWaveform`, `write`, `process`, `feed`, `accept`

2. **Posibles correcciones (investiga cuál es la correcta):**
   - Opción A: `recognizer.acceptWaveform(audioBytes)` - solo un parámetro
   - Opción B: `recognizer.write(audioBytes)` - método write
   - Opción C: `recognizer.process(audioBytes)` - método process
   - Opción D: Convertir a short[]: `recognizer.acceptWaveform(shortArray, length)`

3. **Aplica el cambio mínimo**
   - SOLO modifica la línea 30 del archivo
   - NO cambies imports, NO refactorices otras partes
   - Asegura que el código compile después del cambio

4. **Verificación**
   - El método debe existir en Vosk 0.3.45
   - Debe mantener la funcionalidad de procesar audio en tiempo real
   - El parámetro `audioBytes` es de tipo `byte[]`

## Restricciones IMPORTANTES
- No modifiques ningún otro archivo
- No cambies la arquitectura hexagonal
- No muevas Vosk a otra capa
- Solo corrige el error de compilación

## Salida esperada
El código compila exitosamente y el WebSocket puede procesar audio.

