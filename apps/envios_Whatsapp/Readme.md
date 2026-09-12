# 🚀 WhatsApp Enterprise Dispatch Engine (FastAPI + Evolution API)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3.x-77C1D2.svg?logo=alpinedotjs&logoColor=white)](https://alpinejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-black.svg?logo=socketdotio&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Evolution API](https://img.shields.io/badge/Evolution_API-v2.x-25D366.svg?logo=whatsapp&logoColor=white)](https://github.com/EvolutionAPI/evolution-api)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-0078D6.svg?logo=windows&logoColor=white)](https://www.microsoft.com/windows/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

Sistema full-stack de grado industrial y ejecución local diseñado para la automatización, gestión y despacho masivo o personalizado de mensajería WhatsApp a través de **Evolution API**. Utiliza hojas de cálculo **Microsoft Excel (`.xlsx`)** como base de datos maestra persistente, incorpora telemetría en vivo vía **WebSockets**, mitigación defensiva contra bloqueos y empaquetado autónomo para despliegue **cero instalación** en cualquier estación de trabajo Windows.

---

## 📑 Tabla de Contenidos

- [1. Arquitectura de Software y Diagramas](#1-arquitectura-de-software-y-diagramas)
  - [1.1. Diagrama de Arquitectura de Capas](#11-diagrama-de-arquitectura-de-capas)
  - [1.2. Diagrama de Flujo de Datos y Secuencia](#12-diagrama-de-flujo-de-datos-y-secuencia)
- [2. Principios de Ingeniería y Características Core](#2-principios-de-ingeniería-y-características-core)
  - [2.1. Paradigma Dual de Despacho](#21-paradigma-dual-de-despacho)
  - [2.2. Parser RFC 4180 / TSV de Portapapeles de Excel](#22-parser-rfc-4180--tsv-de-portapapeles-de-excel)
  - [2.3. Búsqueda Abierta Multidimensional](#23-búsqueda-abierta-multidimensional)
  - [2.4. Telemetría en Tiempo Real y Pausa Defensiva](#24-telemetría-en-tiempo-real-y-pausa-defensiva)
- [3. Estructura del Catálogo Maestro (`Directorio_Destinatarios.xlsx`)](#3-estructura-del-catálogo-maestro-directorio_destinatariosxlsx)
- [4. Estructura del Proyecto](#4-estructura-del-proyecto)
- [5. Configuración de Entorno (`config.env`)](#5-configuración-de-entorno-configenv)
- [6. Opciones de Implementación y Puesta en Marcha](#6-opciones-de-implementación-y-puesta-en-marcha)
  - [Opción 1: Entorno de Desarrollo (Código Fuente Python)](#opción-1-entorno-de-desarrollo-código-fuente-python)
  - [Opción 2: Paquete Portable Autónomo (Cero Instalación - Windows)](#opción-2-paquete-portable-autónomo-cero-instalación---windows)
- [7. Manual Operativo de Uso](#7-manual-operativo-de-uso)

---

## 1. Arquitectura de Software y Diagramas

El sistema sigue una arquitectura desacoplada y orientada a eventos, organizada en 4 capas de responsabilidad:

### 1.1. Diagrama de Arquitectura de Capas

```mermaid
flowchart TB
    subgraph UI ["Capa de Presentación (Frontend)"]
        A1["Interfaz Web SPA (Tailwind CSS + Alpine.js)"]
        A2["Parser de Portapapeles RFC 4180 (Excel TSV)"]
        A3["Telemetría WebSocket (Consola y Métricas)"]
    end

    subgraph API ["Capa de Aplicación y Servicios (Backend FastAPI)"]
        B1["FastAPI Router (Endpoints REST)"]
        B2["WebSocket Connection Manager"]
        B3["DispatchEngine (Gestor Asíncrono de Envíos)"]
        B4["DirectorioManager (Gestor Atómico de Excel)"]
        B5["WhatsAppLogger (Auditoría en Archivo Plano)"]
    end

    subgraph DATA ["Capa de Datos y Persistencia"]
        C1[("Directorio_Destinatarios.xlsx")]
        C2[("log_envio_whatsapp.txt")]
        C3["config.env"]
    end

    subgraph GATEWAY ["Capa de Mensajería Externa"]
        D1["Evolution API (Docker / Node.js)"]
        D2["WhatsApp Web Engine (Baileys / Chromium)"]
        D3["Red WhatsApp"]
    end

    A1 <-->|HTTP REST| B1
    A3 <-->|Eventos Bidireccionales WS| B2
    B1 --> B3
    B1 --> B4
    B3 --> B5
    B4 <--> C1
    B5 --> C2
    B1 --> C3
    B3 -->|Peticiones Async HTTP / JSON| D1
    D1 --> D2
    D2 --> D3
```

### 1.2. Diagrama de Flujo de Datos y Secuencia

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Operador
    participant UI as Navegador Web (Alpine.js)
    participant Backend as Servidor FastAPI (app.py)
    participant Engine as DispatchEngine
    participant Excel as ExcelManager (.xlsx)
    participant Evo as Evolution API (WhatsApp)

    Usuario->>UI: Abre la aplicación web
    UI->>Backend: GET /api/destinatarios
    Backend->>Excel: Leer directorio ordenado A-Z
    Excel-->>Backend: Dataset (Contactos y Selectores)
    Backend-->>UI: JSON (Contactos disponibles)
    UI-->>Usuario: Despliegue de catálogo ordenado

    alt Modo 2: Mensajes Personalizados desde Excel
        Usuario->>UI: Copia celdas multilínea en Excel (Ctrl + C) y pega en Web (Ctrl + V)
        UI->>UI: parsearCeldasExcel() preserva \n, *negritas*, viñetas y comillas
        UI-->>Usuario: Vista previa de correspondencia Contacto -> Mensaje
    end

    Usuario->>UI: Clic en "Enviar a Seleccionados"
    UI->>Backend: POST /api/envio/iniciar (Payload con destinatarios y mensajes)
    Backend->>Engine: Iniciar bucle de despacho en segundo plano
    Backend-->>UI: 200 OK (Despacho en ejecución)

    loop Para cada destinatario
        Engine->>Engine: Aplicar prefijo 'NOMBRE: ' o comodines {nombre}
        Engine->>Evo: POST /message/sendText/{instance} (JSON payload)
        Evo-->>Engine: Respuesta de estado (ENVIADO / ERROR / ANOMALÍA)
        Engine->>Backend: Registrar en log_envio_whatsapp.txt
        Engine-->>UI: WebSocket Broadcast (Progreso %, log line, contadores)
        UI-->>Usuario: Actualización visual en vivo de consola y barra
        Engine->>Engine: Pausa defensiva (1.5 segundos anti-bloqueo)
    end

    Engine-->>UI: WebSocket Broadcast (Proceso completado)
    UI-->>Usuario: Notificación de finalización exitosa
```

---

## 2. Principios de Ingeniería y Características Core

### 2.1. Paradigma Dual de Despacho
El sistema provee dos modos de operación mutuamente excluyentes en la interfaz:
1. **Modo 1 ("Un mensaje a varios")**: Mensaje broadcast masivo con inyección de variables contextuales:
   - `{nombre}`: Sustitución en tiempo de ejecución por el nombre del contacto (Columna B de Excel).
2. **Modo 2 ("Mensajes personalizados por destinatario")**: Mensaje independiente por cada contacto:
   - Casilla de verificación individual o maestra (`NOMBRE: a todos`) para anteponer automáticamente `NOMBRE: <mensaje>`.
   - Soporte para copiar columnas completas desde Microsoft Excel / Google Sheets con preservación estricta de saltos de página.

### 2.2. Parser RFC 4180 / TSV de Portapapeles de Excel
Cuando una celda de Excel contiene saltos de línea internos (`Alt + Enter`, viñetas, párrafos), el portapapeles del sistema operativo encapsula la celda entre comillas dobles: `"Línea 1\r\nLínea 2"`.
- Se implementó un analizador de estados finitos (`parsearCeldasExcel`) en JavaScript que:
  - **No fragmenta** celdas multilínea: mantiene el mensaje íntegro para ese único contacto.
  - Elimina las comillas envolventes de transporte de Excel sin afectar comillas legítimas de redacción.
  - Asigna las celdas copiadas verticalmente hacia abajo en orden estricto A-Z.
  - Soporta pegado de múltiples columnas extrayendo la columna que contiene el mensaje.

### 2.3. Búsqueda Abierta Multidimensional
- Motor de búsqueda libre que opera sobre cualquier columna o renglón en tiempo real.
- **Normalización canónica**: Remueve acentos (`normalize('NFD')`), convierte a minúsculas e ignora signos diacríticos, garantizando coincidencia sin importar errores tipográficos.
- Coexistencia con 5 selectores independientes: *Tipo*, *Institución*, *Cliente*, *Profesión* y *Clave Tag*.

### 2.4. Telemetría en Tiempo Real y Pausa Defensiva
- Canal de **WebSockets nativo** para comunicación asíncrona dúplex.
- **Rate-Limiting Defensivo**: Intervalo parametrizable (por defecto `1.5s`) entre cada mensaje saliente para evitar detección por comportamiento anómalo o ráfagas masivas de WhatsApp.
- **Auditoría Estandarizada**: Salida concurrente a archivo plano `log_envio_whatsapp.txt` con marcas temporales ISO y clasificación de anomalías.

---

## 3. Estructura del Catálogo Maestro (`Directorio_Destinatarios.xlsx`)

El archivo Excel funge como el almacén maestro estructurado. Las columnas están tipificadas de la siguiente manera:

| Columna | Nombre de Campo | Tipo | Obligatorio | Descripción / Ejemplo |
|:---:|---|:---:|:---:|---|
| **A** | `numero_destinatario` | Entero / Cadena | Sí | Folio identificador único de control (`1`, `2`, `105`). |
| **B** | `nombre` | Cadena | Opcional | Nombre o alias descriptivo (usado para `{nombre}`). |
| **C** | `wa_destinatario` | Cadena | **Sí** | Nombre de ordenamiento principal en WhatsApp (`Ing. Juan Pérez`). |
| **D** | `numero_whatsapp` | Cadena | **Sí** | Número internacional con código de país o JID de grupo (`******` o `120363******@g.us`). |
| **E** | `tipo` | Cadena | Sí | Tipo de entidad: `Persona` o `Grupo`. |
| **F** | `institucion` | Cadena | Opcional | Empresa, dependencia o institución (`UCZ`, `Hospital`). |
| **G** | `cliente` | Cadena | Opcional | Clasificación comercial o etiqueta de cliente. |
| **H** | `profesion` | Cadena | Opcional | Cargo o profesión (`Médico`, `Director`, `Docente`). |
| **I** | `clave_busqueda` | Cadena | Opcional | Código de indexación o tag rápido (`VIP`, `ZONA-NORTE`). |

---

## 4. Estructura del Proyecto

```text
envios_Whatsapp/
├── app.py                             # Núcleo del Servidor FastAPI (REST + WebSockets)
├── config.env                         # Variables de entorno y configuración de conexión
├── Directorio_Destinatarios.xlsx      # Catálogo maestro de destinatarios
├── iniciar.bat                        # Script lanzador con enlace de red local (0.0.0.0)
├── requirements.txt                   # Manifiesto de dependencias Python
├── DespachoWhatsApp.spec              # Especificación de compilación con PyInstaller
├── src/
│   ├── services/
│   │   ├── dispatch_engine.py         # Motor de despacho, sustitución y rate-limiting
│   │   ├── evolution_client.py        # Cliente HTTP asíncrono hacia Evolution API
│   │   ├── excel_manager.py           # Gestor de I/O de Excel con bloqueo de hilos
│   │   └── logger_service.py          # Logger de eventos en log_envio_whatsapp.txt
├── templates/
│   └── index.html                     # Frontend SPA interactivo (Alpine.js + Tailwind)
└── dist/
    ├── DespachoWhatsApp.exe           # Binario ejecutable autónomo (38.7 MB)
    ├── Despacho_WhatsApp_Portable.zip # Paquete portable comprimido listo para transferir
    └── Despacho_WhatsApp_Portable/    # Carpeta distribuible con ejecutable y config.env
```

---

## 5. Configuración de Entorno (`config.env`)

El archivo `config.env` controla los parámetros de ejecución:

```ini
# Dirección de la Evolution API
EVOLUTION_URL=http://localhost:8080

# Instancia activa de WhatsApp vinculada en Evolution API
EVOLUTION_INSTANCE=******

# API Key configurada al desplegar Evolution API
EVOLUTION_APIKEY=******

# Ruta o nombre del archivo Excel de destinatarios
EXCEL_FILE=Directorio_Destinatarios.xlsx

# Archivo plano de bitácora y auditoría
LOG_FILE=log_envio_whatsapp.txt

# Pausa defensiva entre mensajes en segundos (recomendado: 1.5 a 3.0)
SEND_DELAY=1.5
```

---

## 6. Opciones de Implementación y Puesta en Marcha

El sistema está diseñado para implementarse bajo dos modalidades según las necesidades operativas:

```mermaid
graph LR
    subgraph OPC1 ["Opción 1: Entorno de Desarrollo (Código Fuente)"]
        O1A["Máquina con Python 3.10+"] --> O1B["iniciar.bat"] --> O1C["Acceso Local y en Red LAN (0.0.0.0:8000)"]
    end

    subgraph OPC2 ["Opción 2: Paquete Portable Autónomo (Cero Instalación)"]
        O2A["Cualquier PC Windows x64"] --> O2B["DespachoWhatsApp.exe"] --> O2C["Doble Clic -> Abre Navegador Localmente"]
    end
```

---

### Opción 1: Entorno de Desarrollo (Código Fuente Python)
*Recomendada para la máquina principal de desarrollo o administradores del sistema.*

#### Requisitos Previos:
- Windows 10/11 con Python 3.10 o superior instalado.
- Instancia activa de **Evolution API** corriendo localmente en Docker (`http://localhost:8080`).

#### 1. Instalación y Configuración:
Clonar el repositorio y preparar el entorno virtual:
```powershell
# Clonar o ubicarse en el directorio del proyecto
cd D:\******\envios_Whatsapp

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Inicio del Sistema:
Existen dos formas de iniciarlo:
- **Forma Automática:** Hacer doble clic en el archivo `iniciar.bat`.
- **Forma Manual por Consola:**
  ```powershell
  python app.py
  ```

#### 3. Modo de Uso y Acceso:
- **Acceso Local:** Abre automáticamente tu navegador en `http://localhost:8000`.
- **Acceso desde otra PC en la misma red Wi-Fi/LAN:**
  Cualquier otra computadora conectada a la misma red puede ingresar directamente desde su navegador (Edge, Chrome) a:
  ```text
  http://<IP_DE_TU_MAQUINA>:8000
  (Ejemplo: http://******:8000)
  ```
  *(No requiere instalar nada en las otras computadoras).*

---

### Opción 2: Paquete Portable Autónomo (Cero Instalación - Windows)
*Recomendada para operadores finales o para trasladar la solución a cualquier computadora de oficina sin instalar Python, Git, Docker ni dependencias.*

#### Requisitos Previos:
- Computadora con Windows 10, 11 o Windows Server (64 bits).
- Que la máquina de desarrollo (donde corre Evolution API) esté encendida en la misma red local o accesible vía IP.

#### 1. Implementación (Traslado a otra PC):
1. Copia el archivo comprimido `dist/Despacho_WhatsApp_Portable.zip` o la carpeta `dist/Despacho_WhatsApp_Portable/` a una memoria USB o compártela por red.
2. Pégala y descomprímela en la máquina de destino (por ejemplo, en el *Escritorio* o *Documentos*).
3. Abre el archivo `config.env` con el Bloc de Notas y confirma la IP de la máquina de desarrollo:
   ```ini
   EVOLUTION_URL=http://******:8080
   EVOLUTION_INSTANCE=******
   EVOLUTION_APIKEY=******
   EXCEL_FILE=Directorio_Destinatarios.xlsx
   LOG_FILE=log_envio_whatsapp.txt
   SEND_DELAY=1.5
   ```

#### 2. Inicio del Sistema:
1. Haz **doble clic en `DespachoWhatsApp.exe`**.
2. Se abrirá una ventana de terminal informando el inicio del servicio.
3. El sistema **abrirá automáticamente tu navegador web** predeterminado en `http://localhost:8000`.

#### 3. Modo de Uso:
- La aplicación leerá el archivo `Directorio_Destinatarios.xlsx` local de esa computadora.
- Todos los envíos se tramitarán a través de la Evolution API central sin que esa PC requiera Docker.
- Para cerrar el sistema, simplemente cierra la ventana de la terminal.

---

## 7. Manual Operativo de Uso

```mermaid
stateDiagram-v2
    [*] --> Filtrar_Contactos
    Filtrar_Contactos --> Seleccionar_Destinatarios: Clic en casillas o "Seleccionar Filtrados"
    Seleccionar_Destinatarios --> Eleccion_Modalidad

    state Eleccion_Modalidad {
        [*] --> Modo_1_Comun
        [*] --> Modo_2_Individual
        Modo_1_Comun: Redactar mensaje común + botón {nombre}
        Modo_2_Individual: Pegar desde Excel o escribir por fila
    }

    Eleccion_Modalidad --> Iniciar_Despacho: Clic en "Enviar a Seleccionados"
    Iniciar_Despacho --> Monitoreo_Consola: Telemetría en tiempo real por WebSockets
    Monitoreo_Consola --> [*]: Descarga de auditoría (log_envio_whatsapp.txt)
```

1. **Filtros y Búsqueda:** Utiliza los 5 selectores superiores o escribe en la barra de **Búsqueda Abierta** cualquier palabra o frase para filtrar el catálogo en vivo.
2. **Selección:** Marca individualmente los contactos deseados o presiona **`+ Seleccionar Filtrados`** para agregarlos a la tabla superior fijada en orden A-Z.
3. **Redacción / Pegado:**
   - **En Modo 1:** Escribe el texto en el área de redacción. Puedes usar el botón `+ Personalizar: {nombre}` para insertar el comodín.
   - **En Modo 2:** Haz clic en **`📋 Pegar desde Excel`**, pega la columna de mensajes copiada de tu hoja de cálculo y haz clic en **`✅ Aplicar Mensajes`**, o escribe/pega directamente en la celda de cada contacto.
4. **Despacho y Monitoreo:** Haz clic en **`Enviar a Seleccionados`**. Se desplegará la consola con la barra de progreso y el detalle de cada mensaje despachado.
5. **Auditoría:** Al concluir el despacho, presiona **`Descargar log`** para obtener el reporte plano de auditoría.

---

## 📄 Licencia y Mantenimiento

Desarrollado bajo arquitectura modular para máxima portabilidad y resiliencia en entornos corporativos de mensajería empresarial.