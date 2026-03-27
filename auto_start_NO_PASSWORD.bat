@echo off
REM ============================================================================
REM AI Job Foundry - Auto-Start (Startup Folder Method)
REM No requiere contrasena
REM ============================================================================
REM
REM Este script debe colocarse en:
REM %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
REM
REM Lo que hace:
REM 1. Espera 2 minutos para que Windows cargue completamente
REM 2. Detecta la IP correcta de LM Studio
REM 3. Inicia todos los servicios (Docker, n8n, pipeline)
REM ============================================================================

echo.
echo ========================================
echo AI Job Foundry - Auto-Start
echo ========================================
echo.

REM Esperar 2 minutos (120 segundos) para que el sistema este listo
echo [1/3] Esperando 2 minutos para que el sistema este listo...
echo       - Windows cargando servicios
echo       - Red inicializando
echo       - LM Studio autostart (si configurado)
echo.
timeout /t 120 /nobreak

REM Cambiar al directorio del proyecto
echo.
echo [2/3] Cambiando al directorio del proyecto...
cd /d "C:\Users\MSI\Desktop\ai-job-foundry"

if not exist "C:\Users\MSI\Desktop\ai-job-foundry" (
    echo ERROR: Directorio del proyecto no encontrado!
    echo Ruta: C:\Users\MSI\Desktop\ai-job-foundry
    pause
    exit /b 1
)

echo       OK Directorio encontrado
echo.

REM Detectar IP de LM Studio
echo [3/3] Detectando IP de LM Studio...
echo.
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "detect_lm_studio_ip.ps1"

if errorlevel 1 (
    echo.
    echo WARNING: No se pudo detectar LM Studio
    echo El sistema continuara, pero las funciones de AI pueden fallar
    echo.
    timeout /t 5
)

REM Iniciar todos los servicios
echo.
echo ========================================
echo Iniciando AI Job Foundry...
echo ========================================
echo.

REM Iniciar Control Center
call START_CONTROL_CENTER.bat

REM Verificar si hubo errores
if errorlevel 1 (
    echo.
    echo ERROR: Fallo al iniciar AI Job Foundry
    echo Revisa que Python y los servicios esten disponibles
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo AI Job Foundry Iniciado Correctamente
echo ========================================
echo.
echo El sistema esta corriendo en segundo plano
echo Puedes cerrar esta ventana
echo.

REM Pausa de 10 segundos para ver el resultado
timeout /t 10

REM Cerrar ventana automaticamente (quitar REM si quieres que se cierre solo)
REM exit
