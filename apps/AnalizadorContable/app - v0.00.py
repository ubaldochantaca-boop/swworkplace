import os
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama

# 1. CARGAR TUS ESTADOS DE CUENTA
loader = PyPDFLoader("file.pdf")
paginas = loader.load_and_split()

# 2. CREAR BASE DE DATOS LOCAL (VECTORIAL)
# Esto guarda la información de tus cuentas en tu disco duro, cifrada por el modelo
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma.from_documents(paginas, embeddings, persist_directory="./db_cuentas")

# --- SISTEMA DE CHAT INTERACTIVO ---
print("\n" + "="*50)
print("SISTEMA LISTO. Escribe 'salir' para terminar.")
print("="*50)

llm = Ollama(model="gemma:2b")

while True:
    pregunta = input("\nPregunta sobre tus cuentas: ")
    
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        break

    # 1. Buscar contexto
    docs = vector_db.similarity_search(pregunta, k=3)
    contexto = "\n".join([d.page_content for d in docs])
    
    # 2. Generar respuesta
    prompt = f"Contexto: {contexto}\n\nPregunta: {pregunta}\n\nRespuesta detallada:"
    
    print("\n[Gemma está analizando...]")
    respuesta = llm.invoke(prompt)
    print(f"\nRESPUESTA:\n{respuesta}")

""""
 print("Documentos procesados y guardados localmente.")
# 3. FUNCIÓN DE CONSULTA
def preguntar_a_mis_cuentas(pregunta):
    # Busca en los PDFs solo lo relevante a la pregunta
    docs = vector_db.similarity_search(pregunta, k=2)
    contexto = "\n".join([d.page_content for d in docs])
    
    # Aquí es donde Gemma 2B analiza los datos encontrados
    print(f"\nAnalizando datos para: {pregunta}...")
    # (El proceso de inferencia se conecta aquí con el modelo local)
    # """