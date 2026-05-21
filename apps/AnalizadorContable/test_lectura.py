from langchain_community.document_loaders import PyPDFLoader
import os

# Cambia esto por el nombre de uno de tus archivos en la carpeta
archivo = "./file.pdf" 

if os.path.exists(archivo):
    loader = PyPDFLoader(archivo)
    paginas = loader.load()
    print(f"Número de páginas leídas: {len(paginas)}")
    print("--- Contenido de la primera página (primeros 500 caracteres) ---")
    print(paginas[0].page_content[:500])
else:
    print("Archivo no encontrado.")