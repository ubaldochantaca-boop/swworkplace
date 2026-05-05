
"""
SISTEMA IA v4.4 - OPTIMIZACIÓN DE MANTENIMIENTO
"""

import pandas as pd
import time
import psutil
import os
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.llms import Ollama

def mostrar_dashboard(tiempo_inicio, cpu_inicio, ram_inicio):
    tiempo_total = time.time() - tiempo_inicio
    cpu_final = psutil.cpu_percent()
    ram_final = psutil.virtual_memory().used / (1024 * 1024)

    print("-" * 35)
    print("DASHBOARD DE DESEMPEÑO")
    print(f"Tiempo: {tiempo_total:.2f} seg")
    print(f"CPU: {cpu_final}% | RAM: {ram_final:.2f} MB")
    print("-" * 35)

def ejecutar_agente():

    archivo = "IW49UL.csv"

    if not os.path.exists(archivo):
        print(f"Error: No se encuentra el archivo {archivo}")
        return

    print(f"Cargando archivo: {archivo}")
    df = pd.read_csv(archivo)

    llm = Ollama(model="llama3:8b", temperature=0)

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        allow_dangerous_code=True,
        max_iterations=10,
        early_stopping_method="generate"
    )

    print("="*50)
    print("SISTEMA IA v4.4 - ANALIZADOR DE MANTENIMIENTO")
    print("="*50)

    pregunta = input("En qué te puedo apoyar > ")
    ver_kpis = input("¿Quieres visualizar KPIs? (si/no): ").lower() == "si"

    t_inicio = time.time()
    cpu_i = psutil.cpu_percent()
    ram_i = psutil.virtual_memory().used

    try:
        respuesta = agent.run(pregunta)
        print(f"Respuesta: {respuesta}")
    except Exception as e:
        print(f"Error del agente: {str(e)}")

    if ver_kpis:
        mostrar_dashboard(t_inicio, cpu_i, ram_i)

if __name__ == "__main__":
    ejecutar_agente()
