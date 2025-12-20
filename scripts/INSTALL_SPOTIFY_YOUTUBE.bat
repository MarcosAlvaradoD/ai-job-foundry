@echo off
echo ============================================
echo   INSTALADOR SPOTIFY-YOUTUBE DOWNLOADER
echo ============================================
echo.

echo [1/5] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Descargalo desde https://www.python.org/downloads/
    pause
    exit /b 1
)
echo OK - Python instalado
echo.

echo [2/5] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: FFmpeg no encontrado
    echo.
    echo FFmpeg es OBLIGATORIO para convertir a MP3
    echo.
    echo Opciones de instalacion:
    echo   1. Con Chocolatey: choco install ffmpeg
    echo   2. Manual: https://ffmpeg.org/download.html
    echo.
    echo Continuar de todas formas? (S/N)
    set /p continue=
    if /i not "%continue%"=="S" exit /b 1
) else (
    echo OK - FFmpeg instalado
)
echo.

echo [3/5] Instalando yt-dlp (obligatorio)...
pip install yt-dlp
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar yt-dlp
    pause
    exit /b 1
)
echo OK
echo.

echo [4/5] Deseas instalar soporte para Spotify? (S/N)
set /p install_spotify=
if /i "%install_spotify%"=="S" (
    echo Instalando spotipy...
    pip install spotipy
    echo OK
) else (
    echo Omitido - Solo podras descargar desde YouTube directamente
)
echo.

echo [5/5] Deseas instalar Playwright para busqueda robusta? (S/N)
set /p install_playwright=
if /i "%install_playwright%"=="S" (
    echo Instalando playwright...
    pip install playwright
    echo Instalando navegador Chromium...
    playwright install chromium
    echo OK
) else (
    echo Omitido - Usaras yt-dlp para busqueda (mas rapido)
)
echo.

echo ============================================
echo   INSTALACION COMPLETADA
echo ============================================
echo.
echo Ahora puedes usar:
echo   - python spotify_youtube_downloader.py
echo   - python ejemplo_descarga_simple.py
echo   - python ejemplo_spotify_playlist.py
echo.
echo Para mas informacion lee: SPOTIFY_YOUTUBE_README.md
echo.
pause
