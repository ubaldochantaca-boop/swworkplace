# Usamos la versión de Python solicitada (3.12) en formato slim para que pese poco [9]
FROM python:3.12-slim

# Instalamos FFmpeg y dependencias del sistema [8]
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Definimos el directorio de trabajo interno [10, 11]
WORKDIR /app

# Instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de la carpeta src local a /app en el contenedor [12]
COPY src/ .

# Comando para ejecutar el segmentador al iniciar el contenedor [13]
CMD ["python", "main.py"]