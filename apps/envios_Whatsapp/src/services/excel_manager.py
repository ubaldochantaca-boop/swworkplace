import os
import threading
import pandas as pd

COLUMNAS_OFICIALES = [
    "numero_destinatario",
    "nombre",
    "wa_destinatario",
    "numero_whatsapp",
    "tipo",
    "institucion",
    "cliente",
    "profesion",
    "clave_busqueda"
]

class DirectorioManager:
    def __init__(self, excel_path: str = "Directorio_Destinatarios.xlsx"):
        self.excel_path = excel_path
        self._lock = threading.Lock()
        self._verificar_y_asegurar()

    def _verificar_y_asegurar(self) -> None:
        """
        Verifica que el archivo contenga las columnas requeridas con wa_destinatario.
        Si la columna B no tiene encabezado (Unnamed: 1), le asigna 'nombre'.
        """
        with self._lock:
            if not os.path.exists(self.excel_path):
                df_vacio = pd.DataFrame(columns=COLUMNAS_OFICIALES)
                df_vacio.to_excel(self.excel_path, index=False)
                return

            try:
                df = pd.read_excel(self.excel_path)
                renombres = {}
                
                # Si la columna 1 no tiene nombre
                if len(df.columns) > 1 and ("Unnamed:" in str(df.columns[1]) or pd.isna(df.columns[1])):
                    renombres[df.columns[1]] = "nombre"
                
                # Si existe nombre_destinatario pero no wa_destinatario
                if "nombre_destinatario" in df.columns and "wa_destinatario" not in df.columns:
                    renombres["nombre_destinatario"] = "wa_destinatario"
                elif "wa-nombre" in df.columns and "wa_destinatario" not in df.columns:
                    renombres["wa-nombre"] = "wa_destinatario"

                if renombres:
                    df.rename(columns=renombres, inplace=True)
                    df.to_excel(self.excel_path, index=False)
                    print(f"[INFO] Columnas actualizadas con éxito en {self.excel_path}: {df.columns.tolist()}")

            except PermissionError:
                print(f"[ADVERTENCIA] {self.excel_path} está abierto en otra aplicación. Se leerá sin reescribir encabezados.")
            except Exception as e:
                print(f"[ERROR] Error al verificar columnas de {self.excel_path}: {e}")

    def obtener_todos(self) -> list[dict]:
        """
        Retorna la lista completa de destinatarios ordenados alfabéticamente (A-Z)
        por la Columna C ('wa_destinatario') del archivo Excel.
        """
        with self._lock:
            if not os.path.exists(self.excel_path):
                return []
            try:
                df = pd.read_excel(self.excel_path)
                df = df.fillna("")
                
                # La Columna C de Excel es el índice 2 (base 0)
                col_c_nombre = "wa_destinatario"
                if df.shape[1] > 2:
                    col_c_nombre = df.columns[2]
                elif "wa_destinatario" in df.columns:
                    col_c_nombre = "wa_destinatario"
                elif "nombre_destinatario" in df.columns:
                    col_c_nombre = "nombre_destinatario"

                # Ordenar alfabéticamente A-Z por la Columna C (wa_destinatario)
                if col_c_nombre in df.columns:
                    df = df.sort_values(by=col_c_nombre, key=lambda col: col.astype(str).str.lower(), ascending=True)
                
                registros = []
                for _, row in df.iterrows():
                    # Extraer valor exacto de la Columna C (índice 2)
                    if df.shape[1] > 2:
                        wa_dest_val = row.iloc[2]
                    else:
                        wa_dest_val = row.get("wa_destinatario") or row.get("nombre_destinatario") or ""

                    nombre_b_val = row.iloc[1] if df.shape[1] > 1 else ""

                    registro = {
                        "numero_destinatario": int(row.iloc[0]) if str(row.iloc[0]).isdigit() else row.iloc[0],
                        "nombre": str(nombre_b_val).strip(),
                        "wa_destinatario": str(wa_dest_val).strip(),
                        "nombre_destinatario": str(wa_dest_val).strip(),  # Alias de compatibilidad
                        "numero_whatsapp": str(row.get("numero_whatsapp") or (row.iloc[3] if df.shape[1] > 3 else "")).strip(),
                        "tipo": str(row.get("tipo") or (row.iloc[4] if df.shape[1] > 4 else "Persona")).strip(),
                        "institucion": str(row.get("institucion") or (row.iloc[5] if df.shape[1] > 5 else "")).strip(),
                        "cliente": str(row.get("cliente") or (row.iloc[6] if df.shape[1] > 6 else "")).strip(),
                        "profesion": str(row.get("profesion") or (row.iloc[7] if df.shape[1] > 7 else "")).strip(),
                        "clave_busqueda": str(row.get("clave_busqueda") or (row.iloc[8] if df.shape[1] > 8 else "")).strip()
                    }
                    # Incluir cualquier otra columna adicional existente en el archivo Excel
                    for c_name in df.columns:
                        c_str = str(c_name).strip()
                        if c_str not in registro:
                            val = row.get(c_name, "")
                            registro[c_str] = str(val).strip() if pd.notna(val) else ""

                    registros.append(registro)
                return registros
            except Exception as e:
                print(f"[ERROR] Error al leer destinatarios de Columna C: {e}")
                return []

    def obtener_valores_selectores(self) -> dict:
        """
        Obtiene los valores únicos para los 5 selectores independientes.
        """
        destinatarios = self.obtener_todos()
        
        tipos = sorted(list(set(d["tipo"] for d in destinatarios if d.get("tipo"))))
        instituciones = sorted(list(set(d["institucion"] for d in destinatarios if d.get("institucion"))))
        clientes = sorted(list(set(d["cliente"] for d in destinatarios if d.get("cliente"))))
        profesiones = sorted(list(set(d["profesion"] for d in destinatarios if d.get("profesion"))))
        claves = sorted(list(set(d["clave_busqueda"] for d in destinatarios if d.get("clave_busqueda"))))

        return {
            "tipos": tipos if tipos else ["Persona", "Grupo"],
            "instituciones": instituciones,
            "clientes": clientes,
            "profesiones": profesiones,
            "claves_busqueda": claves
        }

    def agregar_destinatario(self, datos: dict) -> dict:
        """
        Agrega un nuevo destinatario al archivo Excel atómicamente con wa_destinatario.
        """
        with self._lock:
            try:
                df = pd.read_excel(self.excel_path) if os.path.exists(self.excel_path) else pd.DataFrame(columns=COLUMNAS_OFICIALES)
            except Exception:
                df = pd.DataFrame(columns=COLUMNAS_OFICIALES)
            
            siguiente_numero = 1
            if not df.empty and 'numero_destinatario' in df.columns:
                try:
                    siguiente_numero = int(pd.to_numeric(df['numero_destinatario'], errors='coerce').max()) + 1
                except Exception:
                    siguiente_numero = len(df) + 1

            wa_num = str(datos.get("numero_whatsapp", "")).strip()
            tipo_propuesto = str(datos.get("tipo", "")).strip()
            if "@g.us" in wa_num:
                tipo = "Grupo"
            elif tipo_propuesto in ["Grupo", "Persona"]:
                tipo = tipo_propuesto
            else:
                tipo = "Persona"

            wa_dest = str(datos.get("wa_destinatario") or datos.get("nombre_destinatario") or "").strip()
            nombre = str(datos.get("nombre") or wa_dest).strip()

            nuevo_registro = {
                "numero_destinatario": siguiente_numero,
                "nombre": nombre,
                "wa_destinatario": wa_dest,
                "numero_whatsapp": wa_num,
                "tipo": tipo,
                "institucion": str(datos.get("institucion", "")).strip(),
                "cliente": str(datos.get("cliente", "")).strip(),
                "profesion": str(datos.get("profesion", "")).strip(),
                "clave_busqueda": str(datos.get("clave_busqueda", "")).strip()
            }

            df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
            col_orden = "wa_destinatario" if "wa_destinatario" in df.columns else (df.columns[2] if len(df.columns) > 2 else df.columns[0])
            df = df.sort_values(by=col_orden, key=lambda col: col.astype(str).str.strip().str.lower(), ascending=True)
            df.reset_index(drop=True, inplace=True)
            df['numero_destinatario'] = range(1, len(df) + 1)
            df.to_excel(self.excel_path, index=False)
            return nuevo_registro
