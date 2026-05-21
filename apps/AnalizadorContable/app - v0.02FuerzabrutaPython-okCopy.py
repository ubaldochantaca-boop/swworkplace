import os
import torch
import pandas as pd

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.documents import Document

# --- 1. CONFIGURACIÓN DE HARDWARE ---
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"--- Ejecutando en: {device.upper()} (GPU NVIDIA Quadro T2000) ---")

# --- 2. CARGA DE DATOS ---
archivo_csv = "file.csv"

try:
    # Usamos utf-8-sig para evitar errores de caracteres raros al inicio
    df = pd.read_csv(archivo_csv, sep=None, engine='python', encoding='utf-8-sig')
    df.columns = [c.strip() for c in df.columns]
    
    # Identificar columnas clave
    col_desc = next((c for c in df.columns if "desc" in c.lower() or "concep" in c.lower()), df.columns[2])
    col_monto = next((c for c in df.columns if "monto" in c.lower() or "importe" in c.lower()), df.columns[-1])
    col_fecha = next((c for c in df.columns if "fecha" in c.lower()), df.columns[0])

    # Limpiar montos para que sean números
    df['Monto_Num'] = df[col_monto].replace(r'[\$,+]', '', regex=True).astype(float)
    print(f"✅ CSV cargado. Columnas: {col_fecha}, {col_desc}, {col_monto}")

except Exception as e:
    print(f"❌ Error crítico: {e}")
    exit()

# --- 3. PREPARAR BÚSQUEDA ---
documentos = [
    Document(page_content=f"Fecha: {r[col_fecha]}, Desc: {r[col_desc]}, Monto: {r[col_monto]}") 
    for _, r in df.iterrows()
]
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': device})
vector_db = Chroma.from_documents(documents=documentos, embedding=embeddings)

# --- 4. LÓGICA DE CONSULTA CON FILTRO DIRECTO ---
llm = Ollama(model="gemma:2b")

def consultar(pregunta):
    # Paso 1: Filtro de palabras clave en Pandas (Fuerza Bruta)
    # Buscamos palabras de más de 3 letras de la pregunta dentro del CSV
    palabras = [p.upper() for p in pregunta.split() if len(p) > 3]
    evidencia = ""
    total_calculado = 0
    
    for p in palabras:
        coincidencias = df[df[col_desc].str.contains(p, case=False, na=False)]
        if not coincidencias.empty:
            for _, r in coincidencias.iterrows():
                evidencia += f"- Fecha: {r[col_fecha]}, {r[col_desc]}, Monto: {r[col_monto]}\n"
            total_calculado += coincidencias['Monto_Num'].sum()

    # Paso 2: Búsqueda semántica (por si el filtro falla)
    docs = vector_db.similarity_search(pregunta, k=5)
    contexto_extra = "\n".join([d.page_content for d in docs])

    # Paso 3: Construir Prompt
    prompt = f"""
    ERES UN ANALISTA CONTABLE.
    
    DATOS ENCONTRADOS:
    {evidencia if evidencia else contexto_extra}
    
    PREGUNTA: {pregunta}
    
    INSTRUCCIONES:
    - Si hay datos arriba, lístalos.
    - El total calculado por el sistema es: ${total_calculado:,.2f}
    - Responde de forma clara y directa.
    """
    
    print("\n[Analizando...]")
    print(f"DEBUG: Palabras buscadas: {palabras}")
    
    respuesta = llm.invoke(prompt)
    print(f"\n--- RESPUESTA ---\n{respuesta}\n" + "="*40)

# --- 5. CHAT ---
if __name__ == "__main__":
    print("\nSISTEMA LISTO. Pregunta por 'Supermercado', 'Izzi', etc.")
    while True:
        q = input("\nPregunta: ")
        if q.lower() in ['salir', 'exit']: break
        consultar(q)