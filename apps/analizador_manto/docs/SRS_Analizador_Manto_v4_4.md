---
title: 2026-04-07 - SRS_Analizador_Manto_v4_4_Final_Implementation IA-Local Ollama Ordenes de Mantto
sponsor: UCZ
Topic:
due: 2026-04-07 17:06
created: 2026-04-07 17:06
tags:
priority: "3"
status: backlog
qualification:
Ayuno_Intermitente:
Ingles_10min:
SAP_capacitación:
Leer_30min:
Typing_5min:
Meditación_10mins:
Ejercicio_Mins: 0
---

# Nombre: 2026-04-07 - SRS_Analizador_Manto_v4_4_Final_Implementation IA-Local Ollama Ordenes de Mantto
Creada: 2026-04-07 17:06

Aquí tienes la nota completa en formato Markdown, estructurada bajo el estándar **IEEE 830-1998** y lista para ser copiada o descargada para tu bóveda de Obsidian.

---
# **0. Palabras Clave**
Agentes ReAct, Inferencia Local, Robustez de Software.

---
# **1. Nombre de la Nota**
`SRS_Analizador_Manto_v4_4_Final_Implementation`

---
# **2. Objetivo de la Nota**
Proveer la especificación técnica y el código fuente final del "Analizador Manto v4.4", optimizando el manejo de excepciones por límites de iteración y asegurando la compatibilidad con modelos de lenguaje de parámetros reducidos (3B) en un entorno local.

---
# **3. Introducción**
Este documento define los requisitos y la implementación de un agente de IA para el análisis de órdenes de mantenimiento. Se enfoca en la transición hacia la estabilidad operativa mediante el control de ciclos de razonamiento en hardware local.

---
# **4. Estructura Lógica de Metaconceptos**
* **Capa de Datos:** Abstracción de archivos CSV mediante Pandas.
* **Capa de Razonamiento:** Lógica ReAct (Reason + Act) para la generación dinámica de consultas.
* **Capa de Control:** Gestión de límites críticos (`max_iterations`, `max_execution_time`) para evitar el bloqueo del sistema.

---
# **5. Índice**
1.  **Especificación de Requerimientos (SRS)**
2.  **Configuración de Versiones (v4.3 vs v4.4)**
3.  **Código Fuente Final (Documentado)**
4.  **Manual de Implementación**
5.  **Manual Operativo**
6.  **Conclusiones**
7.  **Referencias**

---
# **6. Inputs, Outputs y Restricciones**

| Componente | Descripción |
| :--- | :--- |
| **Inputs** | Archivo `IW49UL.csv`, comandos de texto (Ej: "Contar PM01"). |
| **Outputs** | Respuesta procesada, Dashboard de rendimiento (CPU/RAM/Tiempo). |
| **Consideraciones** | El modelo debe soportar la generación de código Python válido. |
| **Restricciones** | Tiempo máximo de ejecución: 500s. Límite de iteraciones: 5-10. |

---
# **7. Contenido Desarrollo**

#### **v4.30 - Optimización de Formato**
En esta etapa se implementó el dashboard de desempeño. Se detectó que el agente fallaba al intentar resolver consultas de conteo simples debido a una mala interpretación de los nombres de las columnas en el CSV.

## **v4.40 - Versión Final: El Punto de Equilibrio (3B)**
Se integra el modelo Llama 3.2 3B. Se ajustan los parámetros del agente para manejar el error de "Iteration Limit", permitiendo que el sistema devuelva un estado de error controlado en lugar de un colapso del proceso.

**Input Final:** Pregunta directa sobre órdenes tipo PM01.
**Output Final:** Conteo exacto o diagnóstico de error por límite de tiempo.

## **Código Fuente Documentado (Python)**

```python
"""
SISTEMA IA v4.4 - OPTIMIZACIÓN DE MANTENIMIENTO
Estándar de Documentación: Ingeniería de Software (Clean Code)
"""

import pandas as pd
import time
import psutil
import os
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.llms import Ollama # O el proveedor de modelo que utilices

def mostrar_dashboard(tiempo_inicio, cpu_inicio, ram_inicio):
    """Calcula y despliega métricas de desempeño del sistema."""
    tiempo_total = time.time() - tiempo_inicio
    cpu_final = psutil.cpu_percent()
    ram_final = psutil.virtual_memory().used / (1024 * 1024) # MB

    print("-" * 35)
    print("📊 DASHBOARD DE DESEMPEÑO (MODELO 3B)")
    print(f"⏱️ Tiempo: {tiempo_total:.2f} seg")
    print(f"⚙️ CPU: {cpu_final}% | 💾 RAM: {ram_final:.2f} MB")
    print("-" * 35)

def ejecutar_agente():
    # 1. Configuración de Archivo
    archivo = "IW49UL.csv"
    if not os.path.exists(archivo):
        print(f"[!] Error: No se encuentra el archivo {archivo}")
        return

    print(f"[*] Cargando archivo: {archivo}...")
    df = pd.read_csv(archivo)

    # 2. Inicialización del Modelo Local (Ajustar según tu configuración)
    llm = Ollama(model="llama3.2:3b", temperature=0)

    # 3. Creación del Agente con límites de seguridad
    # max_iterations: Evita bucles infinitos si el modelo alucina código
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=False, 
        allow_dangerous_code=True,
        max_iterations=10, 
        early_stopping_method="generate"
    )

    # 4. Interfaz de Usuario
    print("\n" + "="*50)
    print("  SISTEMA IA v4.4 - EL PUNTO DE EQUILIBRIO (3B)")
    print("="*50)

    pregunta = input("\nEn qué te puedo apoyar > ")
    ver_kpis = input("¿Quieres visualizar los KPIs? (si/no): ").lower() == "si"

    # 5. Ejecución y Monitoreo
    t_inicio = time.time()
    cpu_i = psutil.cpu_percent()
    ram_i = psutil.virtual_memory().used

    print("\n[Analizando con Llama 3.2 3B...]")

    try:
        respuesta = agent.run(pregunta)
        print(f"\nRespuesta: {respuesta}")
    except Exception as e:
        # Captura el error de límite de iteraciones o tiempo
        print(f"\nRespuesta: Error del Agente ({str(e)})")

    if ver_kpis:
        mostrar_dashboard(t_inicio, cpu_i, ram_i)

if __name__ == "__main__":
    ejecutar_agente()
```

---
# **8. Manual de Implementación**
1.  **Dependencias:** Ejecutar `pip install pandas langchain-experimental psutil langchain-community`.
2.  **Servidor de Inferencia:** Asegurarse de que Ollama (o el backend local) esté corriendo con el modelo `llama3.2:3b`.
3.  **Preparación de Datos:** Colocar el archivo `IW49UL.csv` en la misma carpeta que el script.

---
# **9. Manual Operativo**
1.  Iniciar el script desde la terminal: `python analizador_manto_ul.py`.
2.  Para consultas de conteo, ser específico: *"Dime el número total de filas donde la columna 'Tipo de orden' es igual a 'PM01'"*.
3.  Si el sistema arroja "Iteration Limit", simplificar la pregunta o verificar que los nombres de las columnas no contengan caracteres especiales.

---
# **10. Conclusiones**
El sistema v4.4 logra integrar un modelo de parámetros reducidos bajo un esquema de control estricto. La falla por límite de iteraciones es una medida de seguridad necesaria; su resolución definitiva depende de la capacidad del modelo para corregir errores de sintaxis en el primer intento.

---
# **11. Referencias**
1.  **IEEE Standard 830-1998**: [SRS Guidelines](https://standards.ieee.org/standard/830-1998.html).
2.  **Documentación LangChain**: [Security & Code Execution](https://python.langchain.com/docs/security/).
3.  **Chat de Referencia**: *Optimización de Agentes Locales*, Usuario: Gemini / uchantaca@gmail.com.