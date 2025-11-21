@echo off
REM AI Job Foundry - Web Application Launcher
REM Quick start script for Windows

echo ================================================================================
echo AI JOB FOUNDRY - WEB APPLICATION
echo ================================================================================
echo.

REM Check if Flask is installed
py -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Flask not installed
    echo [INFO] Installing Flask...
    py -m pip install flask --break-system-packages
)

REM Check if BeautifulSoup4 is installed
py -c "import bs4" 2>nul
if %errorlevel% neq 0 (
    echo [WARN] BeautifulSoup4 not installed
    echo [INFO] Installing BeautifulSoup4...
    py -m pip install beautifulsoup4 --break-system-packages
)

echo.
echo [INFO] Starting web server...
echo [INFO] Open: http://localhost:5000
echo.
echo Press Ctrl+C to stop
echo ================================================================================
echo.

REM Start Flask app
cd /d "%~dp0"
py web_app\app.py

pause
