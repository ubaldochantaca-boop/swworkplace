
# SRS - Analizador Minimalista de Mantenimiento con IA Local

## Palabras clave
Arquitectura-ReAct, Inferencia-Local, Agentes-Autónomos

## Objetivo
Definir los requisitos funcionales y técnicos para un agente de IA minimalista
capaz de analizar datos tabulares provenientes de SAP.

## Introducción
La solución utiliza el modelo Llama 3.2 (3B) ejecutado localmente mediante Ollama
para analizar reportes de mantenimiento IW49 exportados en formato CSV.

## Arquitectura

1. Abstracción de datos mediante Pandas.
2. Agente LangChain que implementa el ciclo ReAct:
   Thought -> Action -> Observation.
3. Ejecución local sin dependencia de servicios cloud.

## Inputs
Archivo CSV de reporte IW49.

## Outputs
Respuesta textual generada por el agente basada en el análisis del dataset.

## Requisitos

Hardware recomendado:
- CPU moderna
- 8GB RAM mínimo

Software:
- Python 3.10+
- Ollama
- Modelo llama3.2:3b

## Implementación

Instalar dependencias:

pip install pandas langchain-ollama langchain-experimental tabulate

Descargar modelo:

ollama pull llama3.2:3b

Ejecutar:

python Analizador_Manto_Minimalista.py

## Conclusión

La versión minimalista demuestra que es posible integrar IA local en el análisis
de datos industriales con una arquitectura ligera y sin dependencia de nube.
