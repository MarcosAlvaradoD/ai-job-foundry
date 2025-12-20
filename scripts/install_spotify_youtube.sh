#!/bin/bash

echo "============================================"
echo "  INSTALADOR SPOTIFY-YOUTUBE DOWNLOADER"
echo "============================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# [1/5] Verificar Python
echo "[1/5] Verificando Python..."
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python instalado:${NC} $(python3 --version)"
else
    echo -e "${RED}✗ ERROR: Python no está instalado${NC}"
    echo "Instálalo según tu sistema:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi
echo ""

# [2/5] Verificar FFmpeg
echo "[2/5] Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓ FFmpeg instalado:${NC} $(ffmpeg -version | head -n1)"
else
    echo -e "${YELLOW}⚠ ADVERTENCIA: FFmpeg no encontrado${NC}"
    echo ""
    echo "FFmpeg es OBLIGATORIO para convertir a MP3"
    echo ""
    echo "Opciones de instalación:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo ""
    read -p "¿Continuar de todas formas? (s/N): " continue
    if [[ ! $continue =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi
echo ""

# [3/5] Instalar yt-dlp
echo "[3/5] Instalando yt-dlp (obligatorio)..."
pip3 install yt-dlp
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ yt-dlp instalado${NC}"
else
    echo -e "${RED}✗ ERROR: No se pudo instalar yt-dlp${NC}"
    exit 1
fi
echo ""

# [4/5] Instalar Spotify
echo "[4/5] ¿Deseas instalar soporte para Spotify? (s/N)"
read -p "> " install_spotify
if [[ $install_spotify =~ ^[Ss]$ ]]; then
    echo "Instalando spotipy..."
    pip3 install spotipy
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Spotipy instalado${NC}"
    else
        echo -e "${YELLOW}⚠ No se pudo instalar spotipy${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Omitido - Solo podrás descargar desde YouTube directamente${NC}"
fi
echo ""

# [5/5] Instalar Playwright
echo "[5/5] ¿Deseas instalar Playwright para búsqueda robusta? (s/N)"
read -p "> " install_playwright
if [[ $install_playwright =~ ^[Ss]$ ]]; then
    echo "Instalando playwright..."
    pip3 install playwright
    echo "Instalando navegador Chromium..."
    playwright install chromium
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Playwright instalado${NC}"
    else
        echo -e "${YELLOW}⚠ No se pudo instalar Playwright${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Omitido - Usarás yt-dlp para búsqueda (más rápido)${NC}"
fi
echo ""

# Resumen
echo "============================================"
echo "  ✓ INSTALACIÓN COMPLETADA"
echo "============================================"
echo ""
echo "Ahora puedes usar:"
echo "  - python3 spotify_youtube_downloader.py"
echo "  - python3 ejemplo_descarga_simple.py"
echo "  - python3 ejemplo_spotify_playlist.py"
echo ""
echo "Para más información lee: SPOTIFY_YOUTUBE_README.md"
echo ""
