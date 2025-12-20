"""
Ejemplo para descargar playlist de Spotify
Edita este archivo con tus credenciales y URL de playlist
"""

from spotify_youtube_downloader import SpotifyToYouTubeDownloader

# ====================================
# CONFIGURACIÓN - EDITA ESTO
# ====================================

# Credenciales de Spotify (obtenerlas en https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID = "TU_CLIENT_ID_AQUI"
SPOTIFY_CLIENT_SECRET = "TU_CLIENT_SECRET_AQUI"

# URL de la playlist de Spotify
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Carpeta donde se guardarán los MP3
OUTPUT_FOLDER = "./spotify_descargas"

# Máximo de canciones a descargar (None = todas)
MAX_SONGS = None  # Cambia a 10 para descargar solo las primeras 10

# Usar Playwright para búsqueda (más robusto pero más lento)
USE_PLAYWRIGHT = False

# ====================================
# DESCARGA
# ====================================

def main():
    print("\n🎵 Descargando playlist de Spotify → YouTube → MP3\n")

    # Validar credenciales
    if "TU_CLIENT_ID_AQUI" in SPOTIFY_CLIENT_ID:
        print("❌ ERROR: Debes configurar tus credenciales de Spotify")
        print("   1. Ve a https://developer.spotify.com/dashboard")
        print("   2. Crea una aplicación")
        print("   3. Copia el Client ID y Client Secret")
        print("   4. Edita este archivo y pega tus credenciales")
        return

    # Crear downloader
    app = SpotifyToYouTubeDownloader(
        output_folder=OUTPUT_FOLDER,
        spotify_client_id=SPOTIFY_CLIENT_ID,
        spotify_client_secret=SPOTIFY_CLIENT_SECRET,
        use_playwright=USE_PLAYWRIGHT
    )

    # Descargar playlist
    stats = app.download_from_spotify_playlist(
        SPOTIFY_PLAYLIST_URL,
        max_songs=MAX_SONGS
    )

    print(f"\n✅ ¡Descarga completada!")
    print(f"📁 Archivos guardados en: {OUTPUT_FOLDER}")
    print(f"📊 Exitosas: {stats['success']} | Fallidas: {stats['failed']}\n")

if __name__ == "__main__":
    main()
