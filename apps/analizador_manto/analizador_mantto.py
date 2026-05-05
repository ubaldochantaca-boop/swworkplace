"""
MÓDULO: Analizador de Mantenimiento (Edición Ingeniería ThinkPad)
VERSION: 6.0.0 (GPU Monitoring & SAP Data Fix)
DESCRIPCIÓN: Optimizado para procesar costos de SAP y monitorear GPU NVIDIA.
"""

import pandas as pd
import time
import psutil
import os
import re
import GPUtil
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_pandas_dataframe_agent

# --- 1. MONITOR DE DESEMPEÑO (CPU + RAM + GPU) ---
class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = 0
        
    def iniciar_conteo(self):
        self.start_time = time.time()
        psutil.cpu_percent(interval=None)

    def obtener_metricas(self):
        # Monitoreo de GPU Quadro
        try:
            gpus = GPUtil.getGPUs()
            gpu_uso = f"{gpus[0].load * 100:.1f}%" if gpus else "No Detectada"
        except:
            gpu_uso = "Error de lectura"
            
        return {
            "tiempo": time.time() - self.start_time,
            "ram": self.process.memory_info().rss / (1024 * 1024),
            "cpu": psutil.cpu_percent(interval=None),
            "gpu": gpu_uso
        }

# --- 2. CARGA Y CURACIÓN DE DATOS (Vital para evitar Alucinaciones) ---
def cargar_y_curar_datos(nombre_archivo):
    print(f"[*] Procesando archivo SAP: {nombre_archivo}...")
    try:
        # Cargamos el archivo (el motor python detecta sep automáticamente)
        df = pd.read_csv(nombre_archivo, sep=None, engine='python', header=0)
        
        # A. Normalizar nombres de columnas (SAP usa puntos y espacios que rompen el código)
        # Ejemplo: 'Coste plan. tot.' -> 'Coste_plan_tot'
        df.columns = [re.sub(r'[.\s]+', '_', col).strip('_') for col in df.columns]
        
        # B. Limpieza de Monedas (Remover comas de miles para que sean números reales)
        # Buscamos columnas que contengan 'Coste' o 'acumulado'
        for col in df.columns:
            if any(key in col.lower() for key in ['coste', 'acumulado', 'planificado']):
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        print(f"[!] ERROR en carga: {e}"); exit()

# --- 3. BUCLE PRINCIPAL ---
def ejecutar_analizador():
    monitor = PerformanceMonitor()
    df = cargar_y_curar_datos('IW49UL.csv') 
    
    # Usamos Llama 3 8B (Asegúrate de haber hecho 'ollama pull llama3:8b')
    llm = OllamaLLM(model="llama3:8b", temperature=0)

    print("\n" + "="*55)
    print("  ANALIZADOR DE MANTENIMIENTO v6.0 (THINKPAD EDITION)")
    print("="*55)
    print(f"Columnas Listas: {', '.join(df.columns[:4])}...")

    while True:
        pregunta = input("\nEn que te puedo apoyar > ").strip()
        if pregunta.lower() in ["salir", "exit"]: break
        if not pregunta: continue

        ver_pasos = input("¿Ver razonamiento? (si/no): ").lower() == 'si'
        ver_kpis = input("¿Ver KPIs? (si/no): ").lower() == 'si'

        # El agente ahora recibe instrucciones sobre cómo listar datos
        agente = create_pandas_dataframe_agent(
            llm, df, verbose=ver_pasos, 
            allow_dangerous_code=True,
            agent_executor_kwargs={"handle_parsing_errors": True, "max_iterations": 10}
        )

        try:
            print(f"\n[IA Pensando con GPU...]")
            monitor.iniciar_conteo()
            
            # El prompt incluye los nombres de columnas ya limpios para que la IA no falle
            prompt_contexto = (
                f"Dataframe: 'df'. Columnas disponibles: {', '.join(df.columns)}\n"
                f"Tarea: {pregunta}\n"
                "Nota: Si pides una lista, muestra solo las columnas relevantes. "
                "Para totales, usa .sum(). Responde en español."
            )
            
            resultado = agente.invoke(prompt_contexto)
            
            if not ver_pasos:
                print(f"\nRespuesta Final:\n{resultado['output']}")
                
        except Exception as e:
            print(f"\n[!] El agente se detuvo: {e}")
        
        if ver_kpis:
            m = monitor.obtener_metricas()
            print("\n" + "📊 KPI DASHBOARD " + "-"*20)
            print(f"⏱️  Tiempo de Respuesta: {m['tiempo']:.2f} seg")
            print(f"⚙️  Carga CPU: {m['cpu']}%")
            print(f"🎮  Carga GPU NVIDIA: {m['gpu']}") # Aquí verás tu Quadro T2000
            print(f"💾  RAM Usada: {m['ram']:.2f} MB")
            print("-" * 37)

if __name__ == "__main__":
    ejecutar_analizador()