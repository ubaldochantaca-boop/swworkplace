import os
import torch
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

# --- 1. CONFIGURACIÓN DE HARDWARE ---
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"--- Ejecutando en: {device.upper()} (GPU NVIDIA Quadro T2000) ---")

# --- 2. CARGA DEL DOCUMENTO ---
# Asegúrate de que el nombre coincida con tu archivo PDF real
archivo_pdf = "fileRes.pdf" 

if not os.path.exists(archivo_pdf):
    print(f"❌ ERROR: No encuentro el archivo '{archivo_pdf}'.")
    exit()

print(f"Procesando: {archivo_pdf}...")
loader = PyPDFLoader(archivo_pdf)
documentos = loader.load()

# --- 3. DIVISIÓN DE TEXTO ---
# Usamos un tamaño de 1000 con solapamiento para no romper filas de tablas
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs_divididos = text_splitter.split_documents(documentos)
print(f"Documento fragmentado en {len(docs_divididos)} partes.")

# --- 4. EMBEDDINGS Y BASE DE DATOS ---
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': device}
)

# Creamos la base de datos (en memoria para esta sesión)
vector_db = Chroma.from_documents(documents=docs_divididos, embedding=embeddings)

# --- 5. LÓGICA DE CONSULTA BLINDADA ---
llm = Ollama(model="gemma:2b")

def consultar_finanzas_blindada(pregunta):
    # Recuperamos más fragmentos (k=10) para asegurar que saltamos el glosario legal
    docs_relevantes = vector_db.similarity_search(pregunta, k=10)
    contexto_completo = "\n".join([d.page_content for d in docs_relevantes])
    
    # DEBUG: Mostrar qué encontró el buscador
    print("\n[DEBUG] Fragmentos encontrados:")
    for i, d in enumerate(docs_relevantes[:3]): # Mostramos solo los 3 primeros en consola
        print(f"  - Fragmento {i+1}: {d.page_content[:150]}...")

    # FILTRO DE PRECISIÓN: Extraer líneas que mencionen palabras clave de la pregunta
    palabras_clave = ["SUPERCENTER", "SORIANA", "WALMART", "GAS", "FARM", "ESTETICA", "TOTAL", "ABONOS"]
    evidencia_directa = ""
    
    for palabra in palabras_clave:
        if palabra.lower() in pregunta.lower():
            lineas = [linea for linea in contexto_completo.split('\n') if palabra.upper() in linea.upper()]
            if lineas:
                evidencia_directa += "\n".join(lineas)

    # Si el filtro encontró algo, se lo damos prioritario a la IA
    contexto_final = evidencia_directa if evidencia_directa else contexto_completo

    prompt = f"""
    ERES UN CONTABLE QUE NO COMETE ERRORES.
    
    DATOS REALES DEL PDF:
    {contexto_final}
    
    PREGUNTA DEL USUARIO: {pregunta}
    
    REGLA: Responde SOLO con la información de los DATOS REALES. 
    Si hay montos con signo +$, lístalos exactamente como aparecen.
    No inventes números.
    """
    
    print("\n[Gemma analizando...]")
    respuesta = llm.invoke(prompt)
    print(f"\n--- RESPUESTA ---\n{respuesta}\n" + "-"*30)

# --- 6. BUCLE DE INTERACCIÓN (CHAT) ---
def iniciar_chat():
    print("\n" + "="*50)
    print("SISTEMA DE ANÁLISIS BANCARIO LISTO")
    print("Escribe tu pregunta o 'salir' para terminar.")
    print("="*50)

    while True:
        try:
            user_input = input("\nPregunta: ")
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("Saliendo...")
                break
                
            if not user_input.strip():
                continue
                
            consultar_finanzas_blindada(user_input)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    iniciar_chat()