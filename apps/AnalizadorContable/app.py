import os
import torch
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.documents import Document

# --- 1. CONFIGURACIÓN DE HARDWARE ---
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"--- Ejecutando en: {device.upper()} ---")

# --- 2. CONFIGURACIÓN DE CATEGORÍAS (Mapeo) ---
# Aquí puedes agregar todas las palabras clave que quieras agrupar
CATEGORIAS = {
    "DESPENSA": ["WALMART", "SUPERCENTER", "SORIANA", "SUPER RIVERA", "ABTS", "MDO DE LOS MARES"],
    "SERVICIOS": ["IZZI", "CFE", "TELMEX", "AGUA"],
    "SALUD": ["FARM", "SIMILARES", "HOSPITAL", "DR "],
    "TRANSPORTE": ["GAS", "ESTACION", "UBER", "DID"],
    "CUIDADO PERSONAL": ["ESTETICA", "BARBERIA", "SALON"]
}

# --- 3. CARGA Y CATEGORIZACIÓN DE DATOS ---
archivo_csv = "file.csv"

def categorizar_descripcion(descripcion):
    desc = str(descripcion).upper()
    for categoria, palabras in CATEGORIAS.items():
        if any(p in desc for p in palabras):
            return categoria
    return "OTROS"

try:
    df = pd.read_csv(archivo_csv, sep=None, engine='python', encoding='utf-8-sig')
    df.columns = [c.strip() for c in df.columns]
    
    # Identificar columnas
    col_desc = next((c for c in df.columns if "desc" in c.lower() or "concep" in c.lower()), df.columns[2])
    col_monto = next((c for c in df.columns if "monto" in c.lower() or "importe" in c.lower()), df.columns[-1])
    col_fecha = next((c for c in df.columns if "fecha" in c.lower()), df.columns[0])

    # Limpiar montos y agregar CATEGORÍA
    df['Monto_Num'] = df[col_monto].replace(r'[\$,+]', '', regex=True).astype(float)
    df['Categoria'] = df[col_desc].apply(categorizar_descripcion)
    
    print(f"✅ CSV cargado y categorizado.")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# --- 4. PREPARAR BÚSQUEDA ---
documentos = [
    Document(page_content=f"Fecha: {r[col_fecha]}, Cat: {r['Categoria']}, Desc: {r[col_desc]}, Monto: {r[col_monto]}") 
    for _, r in df.iterrows()
]
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': device})
vector_db = Chroma.from_documents(documents=documentos, embedding=embeddings)

# --- 5. LÓGICA DE CONSULTA ---
llm = Ollama(model="gemma:2b")

def consultar(pregunta):
    pregunta_up = pregunta.upper()
    evidencia = ""
    total_calculado = 0
    categoria_detectada = None

    # Paso 1: ¿La pregunta menciona una categoría directamente?
    for cat in CATEGORIAS.keys():
        if cat in pregunta_up:
            categoria_detectada = cat
            break

    if categoria_detectada:
        coincidencias = df[df['Categoria'] == categoria_detectada]
        total_calculado = coincidencias['Monto_Num'].sum()
        for _, r in coincidencias.iterrows():
            evidencia += f"- {r[col_fecha]}: {r[col_desc]} (${r[col_monto]})\n"
    else:
        # Si no es categoría, buscamos por palabra clave (como antes)
        palabras = [p for p in pregunta_up.split() if len(p) > 3]
        for p in palabras:
            coincidencias = df[df[col_desc].str.contains(p, case=False, na=False)]
            if not coincidencias.empty:
                total_calculado += coincidencias['Monto_Num'].sum()
                for _, r in coincidencias.iterrows():
                    evidencia += f"- {r[col_fecha]}: {r[col_desc]} (${r[col_monto]})\n"

    # Paso 2: Búsqueda semántica (respaldo)
    docs = vector_db.similarity_search(pregunta, k=5)
    contexto_extra = "\n".join([d.page_content for d in docs])

    # Paso 3: Prompt
    prompt = f"""
    ERES UN ANALISTA FINANCIERO.
    
    DATOS DETECTADOS:
    {evidencia if evidencia else contexto_extra}
    
    PREGUNTA: {pregunta}
    
    TOTAL CALCULADO: ${total_calculado:,.2f}
    
    INSTRUCCIONES:
    - Si se detectó una categoría, enumera los gastos.
    - Menciona siempre el TOTAL CALCULADO.
    - Si no hay datos, sugiere revisar el diccionario de categorías.
    """
    
    print("\n[Analizando...]")
    respuesta = llm.invoke(prompt)
    print(f"\n--- RESPUESTA ---\n{respuesta}\n" + "="*40)

if __name__ == "__main__":
    print("\nSISTEMA LISTO. Puedes preguntar por categorías (DESPENSA, SERVICIOS) o comercios.")
    while True:
        q = input("\nPregunta: ")
        if q.lower() in ['salir', 'exit']: break
        consultar(q)