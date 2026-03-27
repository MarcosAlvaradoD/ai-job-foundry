@echo off
REM ===========================================================================
REM AI JOB FOUNDRY - Auto Start Services
REM Inicia Docker, LM Studio y Control Center automáticamente
REM ===========================================================================

echo.
echo ========================================================================
echo   AI JOB FOUNDRY - AUTO START
echo ========================================================================
echo.

REM 1. Check Docker
echo [1/3] Checking Docker...
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo   Docker: RUNNING
) else (
    echo   Docker: Starting...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 10 /nobreak >nul
)

REM 2. Check LM Studio
echo.
echo [2/3] Checking LM Studio...
curl -s http://127.0.0.1:11434/v1/models >nul 2>&1
if %errorlevel% equ 0 (
    echo   LM Studio: RUNNING
) else (
    echo   LM Studio: Starting...
    start "" "C:\Users\%USERNAME%\AppData\Local\LM Studio\LM Studio.exe"
    timeout /t 5 /nobreak >nul
)

REM 3. Start Control Center
echo.
echo [3/3] Starting Control Center...
echo.

py control_center.py

echo.
echo ========================================================================
echo   Services stopped
echo ========================================================================
echo.
pause
