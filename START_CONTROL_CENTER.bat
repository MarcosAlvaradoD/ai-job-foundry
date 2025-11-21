@echo off
REM AI JOB FOUNDRY - CONTROL CENTER LAUNCHER
REM Verifies services and launches control center

echo.
echo ================================================
echo   AI JOB FOUNDRY - STARTING CONTROL CENTER
echo ================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Por favor instala Python 3.13+
    pause
    exit /b 1
)

echo Python: OK
echo.

REM Run Control Center (now includes startup check)
py control_center.py

REM If control_center exits with error
if errorlevel 1 (
    echo.
    echo ================================================
    echo   CONTROL CENTER TERMINATED WITH ERROR
    echo ================================================
    echo.
    echo TIP: Si hubo error de OAuth, ejecuta:
    echo      py reauthenticate_gmail.py
    echo.
    pause
)

echo.
