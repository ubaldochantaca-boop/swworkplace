import os
import torch
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

# --- CONFIGURACIÓN DE HARDWARE ---
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"--- Ejecutando en: {device.upper()} (GPU NVIDIA Quadro T2000) ---")

# --- 1. CARGA DEL DOCUMENTO ---
# Reemplaza 'tu_estado_de_cuenta.pdf' por el nombre real de tu archivo
archivo_pdf = "file.pdf" 

if not os.path.exists(archivo_pdf):
    print(f"❌ ERROR: No encuentro el archivo '{archivo_pdf}' en la carpeta.")
    exit()

print(f"Leendo documento: {archivo_pdf}...")
loader = PyPDFLoader(archivo_pdf)
documentos = loader.load()

# --- 2. DIVISIÓN DE TEXTO ---
# Chunks más pequeños (500) ayudan a que la búsqueda sea más precisa en tablas
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
docs_divididos = text_splitter.split_documents(documentos)
print(f"Documento fragmentado en {len(docs_divididos)} partes.")

# --- 3. CREACIÓN DE EMBEDDINGS Y BASE DE DATOS ---
# Forzamos a que el modelo de búsqueda use la GPU
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': device}
)

# Creamos la base de datos en memoria para esta prueba de depuración
vector_db = Chroma.from_documents(documents=docs_divididos, embedding=embeddings)

# --- 4. FUNCIÓN DE CHAT CON DEBUG ---
llm = Ollama(model="gemma:2b")

def chat_con_diagnostico():
    print("\n" + "="*50)
    print("SISTEMA DE DIAGNÓSTICO FINANCIERO LISTO")
    print("="*50)
    
    while True:
        pregunta = input("\nPregunta (o 'salir'): ")
        if pregunta.lower() in ['salir', 'exit']: break

        # PASO A: Búsqueda de fragmentos
        docs_relevantes = vector_db.similarity_search(pregunta, k=10)
        
        print("\n[DEBUG] Fragmentos encontrados en el PDF para esta pregunta:")
        if not docs_relevantes:
            print("  ⚠️ No se encontró NADA relevante en el PDF.")
        else:
            for i, d in enumerate(docs_relevantes):
                print(f"  --- Fragmento {i+1} ---\n  {d.page_content[:300]}...\n")

        # PASO B: Generación de respuesta optimizada
        contexto = "\n".join([d.page_content for d in docs_relevantes])
        
        # Un prompt mucho más directo y "valiente" para un modelo de 2B parámetros
        prompt = f"""
        ERES UN ANALISTA FINANCIERO. TU MISIÓN ES BUSCAR MONTOS Y FECHAS.
        
        DATOS EXTRAÍDOS DEL PDF:
        {contexto}
        
        PREGUNTA DEL USUARIO: {pregunta}
        
        REGLAS DE ORO:
        1. Busca líneas que tengan fechas (ej: 16-ene-2026) y montos con signo $ (ej: +$535.70).
        2. Si ves nombres como 'SUPERCENTER', 'SORIANA' o 'SUPER RIVERA', sumalos o lístalos.
        3. No me hables del glosario ni de las leyes. Ve directo a los números.
        4. Si encuentras la respuesta, responde de forma breve y clara.
        """
        
        print("[Gemma analizando con nuevas instrucciones...]")
        # Añadimos parámetros para que sea más preciso
        respuesta = llm.invoke(prompt)
        print(f"\nRESPUESTA DE LA IA:\n{respuesta}")

if __name__ == "__main__":
    chat_con_diagnostico()