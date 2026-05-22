# process_pdfs.py
import os
import json
import asyncio
import aiohttp
import pdfplumber
from sqlalchemy import create_engine, Column, Integer, String, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURACIÓN DE BASE DE DATOS (RUTA ABSOLUTA PARA EVITAR ENTORNOS CRUZADOS) ---
RUTA_PROYECTO = "/home/admin-ia/02_Projects/Github/swworkplace/apps/AnalizadorContable"
DATABASE_URL = f"sqlite:///{RUTA_PROYECTO}/analizador_contable.db"

Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()

class Transaccion(Base):
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, index=True)
    descripcion = Column(String)
    monto = Column(Float)
    tipo = Column(String, index=True)       
    categoria = Column(String, index=True)  
    nombre_archivo_pdf = Column(String)

Index('idx_analisis_contable', Transaccion.fecha, Transaccion.tipo, Transaccion.categoria)

def init_db():
    Base.metadata.create_all(bind=Engine)

OLLAMA_URL = "http://localhost:11434/api/generate"
CACHE_CATEGORIAS = {}  

def extraer_texto_pdf(ruta_pdf):
    texto_completo = []
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in pdf.pages:
                texto_pag = pagina.extract_text()
                if texto_pag:
                    texto_completo.append(texto_pag)
        return "\n".join(texto_completo)
    except Exception as e:
        print(f"[-] Error crítico de lectura física en PDF {os.path.basename(ruta_pdf)}: {e}")
        return ""

def clasificar_por_reglas(descripcion: str) -> str:
    desc = descripcion.lower()
    if any(k in desc for k in ["uber", "didi", "oxxo", "restaurante", "vips", "subway", "7-eleven", "starbucks"]): return "Comida"
    if any(k in desc for k in ["walmart", "soriana", "chedraui", "costco", "heb", "super"]): return "Supermercado"
    if any(k in desc for k in ["pemex", "gasolin", "g500", "bp ", "combustible"]): return "Gasolinas"
    if any(k in desc for k in ["taller", "refaccionaria", "ferreteria", "autozone", "mantenimiento"]): return "Mantenimiento"
    if any(k in desc for k in ["nomina", "spei recibido", "transferencia recibida", "abono", "ingreso"]): return "Ingresos"
    if any(k in desc for k in ["cfe", "telmex", "izzi", "aws", "cloud", "google", "luz", "agua", "internet"]): return "Servicios"
    if any(k in desc for k in ["sat", "impuesto", "iva", "isr"]): return "Impuestos"
    return "Otros"

async def clasificar_con_ia(session: aiohttp.ClientSession, descripcion: str) -> str:
    # 1. Si la descripción ya fue clasificada antes, usamos la memoria caché (Ahorra VRAM)
    if descripcion in CACHE_CATEGORIAS:
        return CACHE_CATEGORIAS[descripcion]
    
    # 2. Intentamos primero con las reglas de texto duro
    categoria_regla = clasificar_por_reglas(descripcion)
    if categoria_regla != "Otros":
        return categoria_regla

    # --- [PUNTO C] PROMPT CON CONTEXTO EMPRESARIAL MEXICANO ---
    prompt = f"""Actúas como un experto auditor fiscal y contable mexicano.
Tu trabajo es clasificar la siguiente transacción bancaria en una sola categoría.

Contexto de las categorías comerciales en México:
- 'Comida': Restaurantes, cafeterías, tiendas de conveniencia (Oxxo, 7-Eleven, Starbucks, Vips).
- 'Supermercado': Despensa grande y canasta básica (Walmart, Costco, Soriana, Chedraui, HEB).
- 'Gasolinas': Combustible para vehículos (Pemex, BP , Shell, G500).
- 'Mantenimiento': Talleres mecánicos, refacciones, ferreterías y tiendas de pintura o construcción (Comex, Autozone, Truper, Home Depot).
- 'Servicios': Luz (CFE), agua, internet, telefonía, software (AWS, Google, Telmex, Izzi).
- 'Impuestos': Pagos al SAT, IVA, ISR.

Transacción a clasificar: "{descripcion}"

Devuelve ÚNICAMENTE la palabra de la categoría correspondiente de esta lista: [Comida, Supermercado, Gasolinas, Mantenimiento, Ingresos, Servicios, Impuestos, Otros]. No agregues notas, ni introducciones, ni puntos de la oración. Devuelve solo la palabra limpia."""

    # --- [PUNTO B] PARÁMETROS DE PRECISIÓN ABSOLUTA (OPTIONS) ---
    payload = {
        "model": "qwen2.5-coder:7b", 
        "prompt": prompt, 
        "stream": False, 
        "options": {
            "temperature": 0.0,  # Cero creatividad
            "top_k": 1,          # Solo la opción más probable
            "top_p": 0.1         # Filtro estricto de vocabulario
        }
    }
    
    try:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                res = data.get("response", "Otros").strip().replace(".", "").strip()
                # Guardamos en caché para no volver a preguntarle a la GPU si la descripción se repite
                CACHE_CATEGORIAS[descripcion] = res
                return res
    except Exception as e:
        print(f"[-] Error en micro-consulta de clasificación IA: {e}")
        
    return "Otros"

def buscar_lista_movimientos(objeto):
    """Busca de forma recursiva cualquier lista dentro del JSON devuelto por Ollama"""
    if isinstance(objeto, list):
        return objeto
    if isinstance(objeto, dict):
        if "movimientos" in objeto and isinstance(objeto["movimientos"], list):
            return objeto["movimientos"]
        if "transacciones" in objeto and isinstance(objeto["transacciones"], list):
            return objeto["transacciones"]
        # Buscar en cualquier otra clave que contenga una lista
        for v in objeto.values():
            if isinstance(v, list):
                return v
    return []

async def procesar_bloque_texto(session: aiohttp.ClientSession, texto: str, nombre_archivo: str):
    payload = {
        "model": "extractor-contable-ia",
        "prompt": f"Extrae los movimientos del siguiente extracto bancario de forma estructurada:\n\n{texto}",
        "stream": False,
        "format": "json"
    }
    
    try:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            if resp.status != 200:
                print(f"[-] Ollama respondió con código de error {resp.status} para un bloque de {nombre_archivo}")
                return
            
            raw_data = await resp.json()
            texto_respuesta = raw_data.get("response", "{}").strip()
            
            if not texto_respuesta or texto_respuesta == "{}":
                return
                
            estructura = json.loads(texto_respuesta)
            movimientos = buscar_lista_movimientos(estructura)
            
            if not movimientos:
                print(f"[-] Depuración: Ollama devolvió JSON pero no se detectaron listas de transacciones en este bloque de {nombre_archivo}. Respuesta IA: {texto_respuesta[:100]}...")
                return
                
            db = SessionLocal()
            contador_bloque = 0
            
            for m in movimientos:
                if not isinstance(m, dict):
                    continue
                    
                monto_raw = m.get("monto")
                desc_raw = m.get("descripcion") or m.get("concepto")
                
                if not monto_raw or not desc_raw:
                    continue
                
                # Clasificación inteligente híbrida (Reglas + IA)
                cat = await clasificar_con_ia(session, str(desc_raw))
                
                # Limpieza exhaustiva y robusta del monto numérico
                try:
                    monto_string = str(monto_raw).replace("$", "").replace(",", "").replace("MXN", "").strip()
                    monto_limpio = float(monto_string)
                except Exception:
                    print(f"[-] Omitida fila por monto inválido: {monto_raw}")
                    continue

                # Determinar el tipo de transacción de forma segura
                tipo_raw = str(m.get("tipo", "gasto")).lower()
                tipo_final = "deposito" if any(k in tipo_raw for k in ["deposito", "abono", "ingreso", "credit"]) else "gasto"

                transaccion = Transaccion(
                    fecha=m.get("fecha", "2026-01-01"),
                    descripcion=str(desc_raw),
                    monto=monto_limpio,
                    tipo=tipo_final,
                    categoria=cat,
                    nombre_archivo_pdf=nombre_archivo
                )
                db.add(transaccion)
                contador_bloque += 1
            
            if contador_bloque > 0:
                db.commit()
                print(f"[+++] ÉXITO REPOSITORIO: Insertados {contador_bloque} registros reales en SQLite desde {nombre_archivo}")
            db.close()
            
    except json.JSONDecodeError:
        print(f"[-] Error crítico: La respuesta de Ollama para {nombre_archivo} no es un JSON válido.")
    except Exception as e:
        print(f"[-] Error inesperado en el procesamiento de bloque: {e}")

async def pipeline_principal(rutas_pdfs):
    # Procesar máximo 2 archivos en paralelo
    sem = asyncio.Semaphore(2)
    async with aiohttp.ClientSession() as session:
        async def desencadenar(ruta):
            async with sem:
                nombre = os.path.basename(ruta)
                texto = extraer_texto_pdf(ruta)
                if texto.strip():
                    print(f"[*] Analizando texto extraído de: {nombre} ({len(texto)} caracteres)...")
                    
                    # CORRECCIÓN EN ESTA LÍNEA: Agrupamos el texto en bloques de 15 líneas
                    lineas = texto.split("\n")
                    bloques_lineas = ["\n".join(lineas[i:i+15]) for i in range(0, len(lineas), 15)]
                    
                    for bloque in bloques_lineas:
                        if len(bloque.strip()) > 30:
                            await procesar_bloque_texto(session, bloque, nombre)
                    print(f"[+] Archivo finalizado completamente: {nombre}")
                else:
                    print(f"[-] Omitido por falta de texto indexable: {nombre}")

        tareas = [desencadenar(r) for r in rutas_pdfs]
        await asyncio.gather(*tareas)

def ejecutar_procesamiento():
    init_db()
    # Forzamos la ruta exacta de la carpeta de subidas de tu usuario
    folder = "/home/admin-ia/02_Projects/Github/swworkplace/apps/AnalizadorContable/uploads"
    if not os.path.exists(folder):
        os.makedirs(folder)
    archivos = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    if archivos:
        print(f"[*] Iniciando carga masiva de {len(archivos)} estados de cuenta PDF en el sistema...")
        asyncio.run(pipeline_principal(archivos))
    else:
        print(f"[-] No se detectaron archivos PDF válidos en la ruta absoluta: {folder}")

# Esto nos permite ejecutar el script de forma aislada por consola
if __name__ == "__main__":
    ejecutar_procesamiento() 