# 🎵 Spotify → YouTube MP3 Downloader

Script completo para descargar música de playlists de Spotify buscando en YouTube y descargando como MP3.

## 📋 Características

✅ **Descargar MP3 desde YouTube** - Simplemente pega una URL de YouTube
✅ **Playlist de Spotify → MP3** - Obtiene todas las canciones de una playlist de Spotify y las descarga desde YouTube
✅ **Dos métodos de búsqueda** - yt-dlp (rápido) o Playwright (más robusto)
✅ **Calidad de audio** - MP3 a 192kbps
✅ **Nombres personalizados** - Los archivos se guardan con el nombre de la canción

## 🔧 Instalación

### 1. Instalar FFmpeg (Requerido)

**Windows:**
```bash
# Opción 1: Con Chocolatey
choco install ffmpeg

# Opción 2: Manual
# Descargar desde https://ffmpeg.org/download.html
# Agregar a PATH
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Instalar dependencias de Python

```bash
# Navegar a la carpeta scripts
cd scripts

# Instalar dependencias obligatorias
pip install yt-dlp

# Instalar dependencias opcionales (Spotify)
pip install spotipy

# Instalar Playwright (opcional, para búsqueda más robusta)
pip install playwright
playwright install chromium
```

O instalar todo desde el archivo requirements:
```bash
pip install -r spotify_youtube_requirements.txt
playwright install chromium
```

## 🎯 Uso

### Modo Interactivo

```bash
python spotify_youtube_downloader.py
```

El script te presentará un menú con opciones:
1. Descargar MP3 desde URL de YouTube
2. Descargar playlist completa de Spotify → YouTube
3. Salir

### Opción 1: Descargar desde YouTube

```python
from spotify_youtube_downloader import YouTubeDownloader

# Crear downloader
downloader = YouTubeDownloader(output_folder="./mis_canciones")

# Descargar una canción
downloader.download_mp3("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Descargar con nombre personalizado
downloader.download_mp3(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    custom_filename="Rick Astley - Never Gonna Give You Up"
)

# Descargar múltiples
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk"
]
results = downloader.download_multiple(urls)
```

### Opción 2: Playlist de Spotify

Primero necesitas credenciales de Spotify API:

1. Ve a https://developer.spotify.com/dashboard
2. Crea una aplicación
3. Obtén tu **Client ID** y **Client Secret**

```python
from spotify_youtube_downloader import SpotifyToYouTubeDownloader

# Configurar
app = SpotifyToYouTubeDownloader(
    output_folder="./mis_canciones",
    spotify_client_id="TU_CLIENT_ID",
    spotify_client_secret="TU_CLIENT_SECRET",
    use_playwright=False  # True para usar Playwright
)

# Descargar playlist completa
app.download_from_spotify_playlist(
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
)

# Descargar solo las primeras 10 canciones
app.download_from_spotify_playlist(
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
    max_songs=10
)
```

## 📁 Estructura de archivos

```
scripts/
├── spotify_youtube_downloader.py      # Script principal
├── spotify_youtube_requirements.txt   # Dependencias
└── SPOTIFY_YOUTUBE_README.md         # Esta documentación

downloads/                             # Carpeta por defecto de descargas
└── *.mp3                             # Tus canciones descargadas
```

## 🔍 Métodos de búsqueda

### yt-dlp (Por defecto - Recomendado)
- ✅ Más rápido
- ✅ No requiere navegador
- ✅ Menos uso de recursos
- ❌ A veces puede fallar en búsquedas complejas

```python
use_playwright=False
```

### Playwright (Alternativa)
- ✅ Más robusto
- ✅ Mejor para búsquedas complejas
- ❌ Más lento
- ❌ Requiere navegador Chromium

```python
use_playwright=True
```

## 💡 Ejemplos de uso avanzado

### Ejemplo 1: Descargar una lista de YouTube URLs

```python
from spotify_youtube_downloader import YouTubeDownloader

urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    "https://www.youtube.com/watch?v=9bZkp7q19f0"
]

downloader = YouTubeDownloader("./rock_classics")
results = downloader.download_multiple(urls)

# Ver resultados
for url, success in results.items():
    status = "✅" if success else "❌"
    print(f"{status} {url}")
```

### Ejemplo 2: Buscar y descargar manualmente

```python
from spotify_youtube_downloader import SpotifyYouTubeConverter, YouTubeDownloader

# Inicializar
converter = SpotifyYouTubeConverter()
downloader = YouTubeDownloader("./mis_canciones")

# Buscar en YouTube
query = "The Beatles - Hey Jude"
youtube_url = converter.search_youtube_ytdlp(query)

if youtube_url:
    print(f"Encontrado: {youtube_url}")
    downloader.download_mp3(youtube_url, custom_filename=query)
```

### Ejemplo 3: Solo obtener lista de Spotify (sin descargar)

```python
from spotify_youtube_downloader import SpotifyYouTubeConverter

converter = SpotifyYouTubeConverter(
    spotify_client_id="TU_CLIENT_ID",
    spotify_client_secret="TU_CLIENT_SECRET"
)

# Obtener canciones
tracks = converter.get_playlist_tracks(
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
)

# Imprimir lista
for i, track in enumerate(tracks, 1):
    print(f"{i}. {track['artist']} - {track['name']}")
```

## ⚠️ Notas importantes

1. **Legalidad**: Este script es solo para uso educativo. Asegúrate de tener permiso para descargar el contenido.

2. **FFmpeg**: Es OBLIGATORIO tener FFmpeg instalado en el sistema para convertir a MP3.

3. **Límite de descargas**: YouTube puede bloquear si descargas demasiadas canciones muy rápido. El script incluye pausas automáticas.

4. **Calidad de audio**: El script descarga la mejor calidad disponible y la convierte a MP3 a 192kbps.

5. **Nombres de archivo**: Los caracteres especiales en nombres de archivo se eliminan automáticamente.

## 🐛 Solución de problemas

### Error: "FFmpeg not found"
```bash
# Verificar instalación de FFmpeg
ffmpeg -version

# Si no está instalado, ver sección de instalación arriba
```

### Error: "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### Error: "No se puede conectar a Spotify"
- Verifica que tu Client ID y Client Secret sean correctos
- Asegúrate de que tu aplicación en Spotify Dashboard esté activa

### Las búsquedas no encuentran resultados
- Prueba cambiar de `use_playwright=False` a `use_playwright=True` o viceversa
- Verifica que el nombre de la canción sea correcto

## 📊 Ejemplo de salida

```
╔══════════════════════════════════════════════════════════╗
║     🎵 SPOTIFY → YOUTUBE MP3 DOWNLOADER 🎵               ║
╚══════════════════════════════════════════════════════════╝

✅ Conectado a Spotify API

🎵 Obteniendo canciones de la playlist...
✅ Encontradas 50 canciones

[1/50] 🎵 The Beatles - Hey Jude
🔗 Encontrado: https://www.youtube.com/watch?v=A_MjCqQoLLA
🎵 Descargando: https://www.youtube.com/watch?v=A_MjCqQoLLA
✅ Descargado exitosamente: The Beatles - Hey Jude.mp3
📁 Ubicación: /home/user/downloads/The Beatles - Hey Jude.mp3

[2/50] 🎵 Queen - Bohemian Rhapsody
...

════════════════════════════════════════════════════════════
📊 RESUMEN DE DESCARGA
════════════════════════════════════════════════════════════
✅ Exitosas: 48
❌ Fallidas: 2
📦 Total: 50
════════════════════════════════════════════════════════════
```

## 🚀 Roadmap futuro

- [ ] Soporte para Apple Music
- [ ] Interfaz gráfica (GUI)
- [ ] Descarga en diferentes formatos (FLAC, WAV, etc.)
- [ ] Organización automática por carpetas (artista/álbum)
- [ ] Descarga de metadata (carátula, letras, etc.)
- [ ] Soporte para SoundCloud, Bandcamp, etc.

## 📝 Licencia

Este script es para uso educativo. Respeta los derechos de autor y las políticas de uso de Spotify y YouTube.

## 🤝 Contribuciones

Si encuentras bugs o tienes sugerencias, por favor:
1. Abre un issue
2. Envía un pull request
3. Contacta al desarrollador

---

**Desarrollado con ❤️ por AI Job Foundry**
