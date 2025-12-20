"""
Ejemplo simple de uso del downloader
Copia este archivo y modifícalo según tus necesidades
"""

from spotify_youtube_downloader import YouTubeDownloader

# ====================================
# CONFIGURACIÓN
# ====================================

# Carpeta donde se guardarán los MP3
OUTPUT_FOLDER = "./mis_descargas"

# Lista de URLs de YouTube para descargar
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    # Agrega más URLs aquí
]

# ====================================
# DESCARGA
# ====================================

def main():
    print("\n🎵 Iniciando descarga de canciones...\n")

    # Crear downloader
    downloader = YouTubeDownloader(output_folder=OUTPUT_FOLDER)

    # Descargar cada URL
    for i, url in enumerate(YOUTUBE_URLS, 1):
        print(f"\n[{i}/{len(YOUTUBE_URLS)}] Descargando...")
        downloader.download_mp3(url)

    print("\n✅ ¡Descarga completada!")
    print(f"📁 Archivos guardados en: {OUTPUT_FOLDER}\n")

if __name__ == "__main__":
    main()
