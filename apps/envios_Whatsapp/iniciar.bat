@echo off
chcp 65001 > nul
title Despacho WhatsApp - Servidor Web Local
echo ======================================================================
echo       INICIANDO SISTEMA DE DESPACHO WHATSAPP (CATÁLOGO EXCEL)
echo ======================================================================
echo.

cd /d "%~dp0"

IF EXIST "%~dp0venv\Scripts\python.exe" (
    echo [OK] Usando entorno virtual del proyecto (venv)...
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
) ELSE (
    echo [ADVERTENCIA] No se encontró venv. Usando Python del sistema...
    set "PYTHON_EXE=python"
)

%PYTHON_EXE% -c "import websockets" 2>nul
IF ERRORLEVEL 1 (
    echo [INFO] Instalando librería websockets requerida...
    %PYTHON_EXE% -m pip install websockets
)

echo.
echo [INFO] Abriendo navegador web en http://localhost:8000 ...
start "" "http://localhost:8000"

echo [INFO] Iniciando servidor FastAPI con Uvicorn en http://0.0.0.0:8000 ...
echo [INFO] Acceso local:     http://localhost:8000
echo [INFO] Acceso desde red:  http://192.168.1.110:8000
%PYTHON_EXE% -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause
