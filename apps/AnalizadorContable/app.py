# app.py
import streamlit as st
import os
import pandas as pd
import requests
from database import SessionLocal, Engine, init_db
from process_pdfs import ejecutar_procesamiento
from sqlalchemy import text

# Asegurar directorios de carga física sin bloquear el renderizado
os.makedirs("./uploads", exist_ok=True)
OLLAMA_URL = "http://localhost:11434/api/generate"

st.set_page_config(page_title="Analizador Contable IA", layout="wide")
st.title("📊 Analizador Contable Inteligente - Servidor Local")

# Inicialización segura de la base de datos
try:
    init_db()
except Exception as e:
    st.error(f"Error inicializando el almacenamiento local: {e}")

# --- SIDEBAR: CONTROL DE ARCHIVOS ---
with st.sidebar:
    st.header("📁 Carga de Estados de Cuenta")
    uploaded_files = st.file_uploader("Subir archivos bancarios (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if st.button("🚀 Iniciar Procesamiento Contable"):
        if uploaded_files:
            for file in uploaded_files:
                ruta_destino = os.path.join("./uploads", file.name)
                with open(ruta_destino, "wb") as f:
                    f.write(file.getbuffer())
            
            with st.spinner("Ejecutando extracción semántica en la RTX 5070..."):
                ejecutar_procesamiento()
            st.success("¡Base de datos financiera sincronizada de forma limpia!")
            st.rerun()  # Forzar actualización de la pantalla para ver los datos nuevos
        else:
            st.warning("Por favor, introduce primero un archivo PDF.")

# --- SECCIÓN CENTRAL: MONITOREO DE DATOS DE FORMA SEGURA ---
st.subheader("📋 Últimos Registros Indexados en el Sistema")

@st.cache_data(ttl=5)  # Evita leer el disco duro constantemente en cada micro-renderizado de Streamlit
def cargar_datos_recientes():
    try:
        return pd.read_sql_query("SELECT fecha, descripcion, monto, tipo, categoria, nombre_archivo_pdf FROM transacciones ORDER BY fecha DESC LIMIT 10", Engine)
    except Exception:
        return pd.DataFrame()

df_recientes = cargar_datos_recientes()

if not df_recientes.empty:
    st.dataframe(df_recientes, use_container_width=True)
else:
    st.info("Servidor operativo. Cargue documentos en el panel lateral para poblar la base de datos.")

# --- MOTOR DE CONSULTAS SEMÁNTICAS (TEXT-TO-SQL) ---
st.subheader("🧠 Consultas Financieras en Lenguaje Natural")
pregunta = st.text_input("Haz una pregunta sobre tus finanzas (ej. '¿Cuánto gasté en Impuestos?'):")

if pregunta:
    esquema_bd = "Tabla: transacciones. Columnas: fecha (YYYY-MM-DD), descripcion (TEXT), monto (REAL), tipo (gasto o deposito), categoria (Comida, Supermercado, Gasolinas, Mantenimiento, Ingresos, Servicios, Impuestos, Otros)"
    
    if any(k in pregunta.lower() for k in ["pronostico", "proyeccion", "predecir", "tendencia"]):
        st.markdown("#### 📈 Generando Modelo Analítico Predictivo...")
        try:
            df_historico = pd.read_sql_query("SELECT fecha, monto FROM transacciones WHERE tipo='gasto'", Engine)
            if len(df_historico) >= 3:
                df_historico['fecha'] = pd.to_datetime(df_historico['fecha'])
                df_mensual = df_historico.groupby(df_historico['fecha'].dt.to_period('M'))['monto'].sum().reset_index()
                promedio_movil = df_mensual['monto'].mean()
                
                prompt_predictive = f"Actúas como un Director Financiero corporativo. El promedio exacto de egresos mensuales históricos es de: ${promedio_movil:.2f}. Los registros mensuales consolidados muestran la siguiente serie temporal:\n{df_mensual.to_string()}\nRedacta un reporte analítico predictivo para el próximo mes sobre el control de presupuesto y la tendencia."
                resp = requests.post(OLLAMA_URL, json={"model": "qwen2.5-coder:7b", "prompt": prompt_predictive, "stream": False}).json()
                st.markdown(resp.get("response", ""))
            else:
                st.warning("Se requieren registros de al menos 3 meses diferentes para estructurar una predicción matemática válida.")
        except Exception as e:
            st.error(f"Error al calcular la serie predictiva: {e}")
    else:
        esquema_bd = "Tabla: transacciones. Columnas: fecha (YYYY-MM-DD), descripcion (TEXT), monto (REAL), tipo (gasto o deposito), categoria (Comida, Supermercado, Gasolinas, Mantenimiento, Ingresos, Servicios, Impuestos, Otros)"
    
        prompt_sql = f"""Actúas como un traductor estricto de Lenguaje Natural a SQLite.
Basado estrictamente en este esquema de base de datos:
{esquema_bd}

MAPEO DE CATEGORÍAS OBLIGATORIO:
- Si el usuario habla de oxxo, restaurantes, vips, comida, subway -> categoria='Comida'
- Si habla de walmart, despensa, super, costco, soriana -> categoria='Supermercado'
- Si habla de pemex, gasolina, combustible -> categoria='Gasolinas'
- Si habla de luz, agua, internet, cfe, telmex, servicios -> categoria='Servicios'
- Si habla de sat, impuestos, iva, isr -> categoria='Impuestos'
- Si habla de nomina, sueldo, abono, ingresos -> tipo='deposito'

REGLAS INQUEBRANTABLES:
1. El nombre de la columna de dinero es estrictamente 'monto'. Jamás inventes variantes.
2. REGLA DE ORO CONTABLE: Si el usuario pide un total, cuánto gastó o sumas generales, usa ÚNICAMENTE SUM(monto). NO agregues la columna 'descripcion' en el SELECT de totales, ya que arruina el informe ejecutivo.
3. Si el usuario pide explícitamente una lista, un desglose o ver "en qué" gastó, entonces sí incluye la fecha, la descripción y el monto (SELECT fecha, descripcion, monto ...).
4. Si piden el balance neto o saldo actual, usa: SELECT (SUM(CASE WHEN tipo='deposito' THEN monto ELSE 0 END) - SUM(CASE WHEN tipo='gasto' THEN monto ELSE 0 END)) FROM transacciones;
5. Devuelve ÚNICAMENTE la sentencia SQL limpia, sin markdown (```sql), sin comentarios.

Pregunta de usuario actual: "{pregunta}"
SQL:"""
        
        try:
            resp_sql = requests.post(OLLAMA_URL, json={"model": "qwen2.5-coder:7b", "prompt": prompt_sql, "stream": False}).json().get("response", "").strip()
            
            # Limpieza absoluta por seguridad si el modelo se pone creativo
            resp_sql = resp_sql.replace("```sql", "").replace("```", "").replace(";", "").strip()
            if not resp_sql.endswith(";"):
                resp_sql += ";"
            
            # --- EJECUCIÓN DEL QUERY EN LA BASE DE DATOS ---
            with SessionLocal() as db_session:
                resultado_db = db_session.execute(text(resp_sql)).fetchall()
                columnas_db = db_session.execute(text(resp_sql)).keys()
                df_resultado = pd.DataFrame(resultado_db, columns=columnas_db)
                
            # Mostrar el SQL generado para auditoría del administrador
            st.code(f"SQL Generado automáticamente por Ollama: {resp_sql}", language="sql")
            
            # --- COMPORTAMIENTO INTELIGENTE DE VISUALIZACIÓN ---
            # Si el resultado tiene más de una fila y contiene columnas de detalle (como descripcion, fecha)
            if len(df_resultado) > 1 and "descripcion" in df_resultado.columns:
                st.markdown("### 📋 Detalle de Movimientos Encontrados:")
                # Pintamos la tabla nativa de Pandas en Streamlit, 100% exacta y sin alucinaciones de la IA
                st.dataframe(df_resultado, use_container_width=True)
                
                # Le pedimos a Ollama una síntesis ultra-breve explicándole que la tabla ya se mostró
                prompt_sintesis = f"El usuario pidió un desglose. Ya le mostré una tabla con estos datos:\n{df_resultado.to_string()}\nRedacta una sola frase cordial indicando que la lista detallada está arriba y menciona cuántos movimientos se encontraron en total."
            
            else:
                # Si es un solo número (un SUM o un COUNT), mostramos la respuesta directa
                prompt_sintesis = f"Pregunta original: '{pregunta}'. Resultado numérico directo de la base de datos:\n{df_resultado.to_string()}\nRedacta una respuesta interpretativa muy breve, exacta y clara sobre este monto total."

            # Llamada a Ollama para la síntesis final
            respuesta_final = requests.post(OLLAMA_URL, json={"model": "qwen2.5-coder:7b", "prompt": prompt_sintesis, "stream": False}).json().get("response", "")
            
            st.markdown(f"### 🤖 Resumen del Analizador:\n{respuesta_final}")
        except Exception as e:
            st.error(f"Fallo en la generación semántica del Query: {e}")