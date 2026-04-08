
# Analizador Manto v4.4 (IA Local con Ollama)

Sistema de análisis de órdenes de mantenimiento exportadas desde SAP utilizando
un agente de IA local basado en LangChain y Ollama.

## Arquitectura
- **Capa de Datos**: CSV exportado desde SAP (ej. IW49UL.csv)
- **Capa de IA**: LangChain + modelo local en Ollama
- **Capa de Control**: límites de iteraciones y monitoreo de recursos

## Requisitos
- Python 3.10+
- Ollama instalado
- Modelo: `llama3.2:3b`

## Instalación

```bash
pip install -r requirements.txt
```

Descargar modelo:

```bash
ollama pull llama3.2:3b
```

## Uso

Colocar el archivo `IW49UL.csv` en la misma carpeta del script.

```bash
python analizador_manto_ul.py
```

Ejemplo de consulta:

```
Dime el número total de filas donde la columna 'Tipo de orden' es igual a 'PM01'
```

## Estructura del repositorio

```
analizador-manto/
│
├── analizador_manto_ul.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── docs/
    └── SRS_Analizador_Manto_v4_4.md
```
