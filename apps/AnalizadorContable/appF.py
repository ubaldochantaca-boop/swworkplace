import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. CONFIGURAR LA RUTA DE LOS PDFS
ruta_cuentas = "./mis_cuentas"

print(f"Buscando PDFs en {ruta_cuentas}...")

# 2. CARGADOR MULTI-ARCHIVO
# Esto busca todos los archivos que terminen en .pdf dentro de la carpeta
loader = DirectoryLoader(ruta_cuentas, glob="./*.pdf", loader_cls=PyPDFLoader)
documentos_crudos = loader.load()

# 3. DIVIDIR TEXTO (Crucial para no agotar la VRAM de la T2000)
# Dividimos los PDFs en pedazos de 1000 caracteres con un pequeño solapamiento
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs_divididos = text_splitter.split_documents(documentos_crudos)

print(f"Se han procesado {len(documentos_crudos)} archivos y dividido en {len(docs_divididos)} fragmentos.")

# 4. CREAR/ACTUALIZAR BASE DE DATOS
device = "cuda" if torch.cuda.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': device})

# Esto creará una base de datos local que contiene TODOS tus estados de cuenta
vector_db = Chroma.from_documents(
    documents=docs_divididos, 
    embedding=embeddings, 
    persist_directory="./db_cuentas"
)

print("Base de datos actualizada con éxito.")