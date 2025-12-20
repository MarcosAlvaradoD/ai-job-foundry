# 🚀 Quick Start - Spotify YouTube Downloader

## Instalación Rápida (5 minutos)

### Windows

```bash
# 1. Instalar dependencias
INSTALL_SPOTIFY_YOUTUBE.bat

# 2. Ejecutar
python spotify_youtube_downloader.py
```

### Linux/Mac

```bash
# 1. Instalar dependencias
./install_spotify_youtube.sh

# 2. Ejecutar
python3 spotify_youtube_downloader.py
```

## Uso Rápido

### 📥 Opción 1: Descargar desde YouTube (Más fácil)

1. Ejecuta: `python spotify_youtube_downloader.py`
2. Selecciona opción `1`
3. Pega la URL de YouTube
4. ¡Listo! Tu MP3 estará en `./downloads`

**Ejemplo:**
```
URL de YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Carpeta: ./mis_canciones
```

### 🎵 Opción 2: Playlist de Spotify

1. Ve a https://developer.spotify.com/dashboard
2. Crea una app (toma 2 minutos)
3. Copia Client ID y Client Secret
4. Ejecuta: `python spotify_youtube_downloader.py`
5. Selecciona opción `2`
6. Pega tus credenciales
7. Pega URL de playlist de Spotify
8. ¡Listo!

**Ejemplo:**
```
Client ID: abc123...
Client Secret: xyz789...
Playlist URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
Carpeta: ./downloads
Máximo canciones: 10
```

## Ejemplos listos para usar

### Ejemplo 1: Script simple con URLs

```bash
# Edita el archivo
nano ejemplo_descarga_simple.py

# Agrega tus URLs de YouTube
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
]

# Ejecuta
python ejemplo_descarga_simple.py
```

### Ejemplo 2: Playlist de Spotify

```bash
# Edita el archivo
nano ejemplo_spotify_playlist.py

# Configura tus credenciales
SPOTIFY_CLIENT_ID = "tu_client_id"
SPOTIFY_CLIENT_SECRET = "tu_client_secret"
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/..."

# Ejecuta
python ejemplo_spotify_playlist.py
```

## ⚡ Comandos más usados

```bash
# Instalación completa
pip install yt-dlp spotipy playwright
playwright install chromium

# Solo lo esencial (YouTube)
pip install yt-dlp

# Verificar FFmpeg
ffmpeg -version

# Ejecutar modo interactivo
python spotify_youtube_downloader.py
```

## 🆘 Problemas comunes

| Problema | Solución |
|----------|----------|
| "FFmpeg not found" | Instala FFmpeg (ver README) |
| "No module named yt_dlp" | `pip install yt-dlp` |
| "Spotify error" | Verifica Client ID/Secret |
| Descarga lenta | Normal, YouTube limita velocidad |
| No encuentra canción | Prueba `use_playwright=True` |

## 📁 ¿Dónde están mis archivos?

Por defecto en: `./downloads/`

Cambiar carpeta:
```python
downloader = YouTubeDownloader(output_folder="./mi_musica")
```

## 🎯 Casos de uso

### Uso 1: Una canción específica
```bash
python spotify_youtube_downloader.py
→ Opción 1
→ Pega URL de YouTube
```

### Uso 2: Playlist de Spotify completa
```bash
python spotify_youtube_downloader.py
→ Opción 2
→ Configura Spotify
→ Pega URL de playlist
```

### Uso 3: Lista personalizada de YouTube
```bash
# Edita ejemplo_descarga_simple.py
# Agrega tus URLs
python ejemplo_descarga_simple.py
```

---

**¿Necesitas más ayuda?** Lee el README completo: `SPOTIFY_YOUTUBE_README.md`
