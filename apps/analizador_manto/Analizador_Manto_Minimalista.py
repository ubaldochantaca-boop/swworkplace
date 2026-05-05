
"""
NOMBRE: Analizador_Manto_Minimalista.py
VERSION: 3.00
DESCRIPCIÓN: Agente de IA local minimalista para análisis de CSV.
"""

import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_pandas_dataframe_agent

df = pd.read_csv('IW49UL.csv', sep=None, engine='python', header=0)

llm = OllamaLLM(model="llama3:8b", temperature=0)

agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    allow_dangerous_code=True,
    agent_executor_kwargs={"handle_parsing_errors": True}
)

def consultar_reporte(pregunta):
    print(f"Pregunta: {pregunta}")
    resultado = agent.invoke(pregunta)
    print(f"IA: {resultado['output']}")

if __name__ == "__main__":
    consultar_reporte("¿Cuál es el costo real acumulado total de todas las órdenes?")
#    consultar_reporte("¿Cuál es el costo planificado acumulado total de todas las órdenes?")
#    consultar_reporte("Listame el numero de orden que tiene monto planeado, enlista solo el numero de orden y el monto planeado")
#    consultar_reporte("Listame el numero de orden que tiene monto real diferente de cero, enlista solo el numero de orden y el monto real")
