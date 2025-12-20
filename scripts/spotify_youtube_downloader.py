"""
Script para descargar música de Spotify → YouTube
Autor: AI Job Foundry
Fecha: 2025-12-20

Funcionalidades:
1. Descargar MP3 desde URL de YouTube
2. Obtener playlist de Spotify y buscar/descargar desde YouTube
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
import subprocess

try:
    import yt_dlp
except ImportError:
    print("❌ yt-dlp no instalado. Ejecuta: pip install yt-dlp")
    sys.exit(1)

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print("⚠️  Spotipy no instalado. Para usar Spotify ejecuta: pip install spotipy")
    spotipy = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("⚠️  Playwright no instalado. Para buscar en YouTube ejecuta: pip install playwright")
    print("   Luego ejecuta: playwright install chromium")
    sync_playwright = None


class YouTubeDownloader:
    """Clase para descargar audio de YouTube como MP3"""

    def __init__(self, output_folder: str = "./downloads"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def download_mp3(self, youtube_url: str, custom_filename: Optional[str] = None) -> bool:
        """
        Descarga audio de YouTube como MP3

        Args:
            youtube_url: URL del video de YouTube
            custom_filename: Nombre personalizado para el archivo (opcional)

        Returns:
            True si la descarga fue exitosa, False en caso contrario
        """
        try:
            print(f"\n🎵 Descargando: {youtube_url}")

            # Configuración de yt-dlp para extraer solo audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.output_folder / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
            }

            # Si se proporciona un nombre personalizado
            if custom_filename:
                # Limpiar el nombre de archivo de caracteres no válidos
                safe_filename = re.sub(r'[<>:"/\\|?*]', '', custom_filename)
                ydl_opts['outtmpl'] = str(self.output_folder / f'{safe_filename}.%(ext)s')

            # Descargar
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info)
                # Cambiar extensión a .mp3
                mp3_file = Path(filename).with_suffix('.mp3')

                print(f"✅ Descargado exitosamente: {mp3_file.name}")
                print(f"📁 Ubicación: {mp3_file.absolute()}")
                return True

        except Exception as e:
            print(f"❌ Error al descargar: {str(e)}")
            return False

    def download_multiple(self, urls: List[str]) -> Dict[str, bool]:
        """
        Descarga múltiples URLs

        Args:
            urls: Lista de URLs de YouTube

        Returns:
            Diccionario con URL y estado de descarga
        """
        results = {}
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Procesando...")
            results[url] = self.download_mp3(url)
            time.sleep(1)  # Pausa entre descargas

        return results


class SpotifyYouTubeConverter:
    """Clase para obtener playlist de Spotify y buscar en YouTube"""

    def __init__(self, spotify_client_id: str = None, spotify_client_secret: str = None):
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.sp = None

        if spotify_client_id and spotify_client_secret and spotipy:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=spotify_client_id,
                    client_secret=spotify_client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                print("✅ Conectado a Spotify API")
            except Exception as e:
                print(f"⚠️  No se pudo conectar a Spotify: {e}")

    def get_playlist_tracks(self, playlist_url: str) -> List[Dict[str, str]]:
        """
        Obtiene todas las canciones de una playlist de Spotify

        Args:
            playlist_url: URL de la playlist de Spotify

        Returns:
            Lista de diccionarios con información de las canciones
        """
        if not self.sp:
            print("❌ No hay conexión con Spotify API")
            return []

        try:
            # Extraer ID de la playlist
            playlist_id = playlist_url.split('playlist/')[-1].split('?')[0]

            print(f"\n🎵 Obteniendo canciones de la playlist...")

            tracks = []
            results = self.sp.playlist_tracks(playlist_id)

            while results:
                for item in results['items']:
                    track = item['track']
                    if track:  # Algunas canciones pueden ser None
                        artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                        tracks.append({
                            'name': track['name'],
                            'artist': artist,
                            'search_query': f"{artist} - {track['name']}"
                        })

                # Siguiente página si existe
                results = self.sp.next(results) if results['next'] else None

            print(f"✅ Encontradas {len(tracks)} canciones")
            return tracks

        except Exception as e:
            print(f"❌ Error al obtener playlist: {str(e)}")
            return []

    def search_youtube_playwright(self, search_query: str) -> Optional[str]:
        """
        Busca en YouTube usando Playwright y obtiene la primera URL

        Args:
            search_query: Query de búsqueda

        Returns:
            URL del primer resultado de YouTube o None
        """
        if not sync_playwright:
            print("❌ Playwright no disponible")
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Buscar en YouTube
                search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                page.goto(search_url, wait_until='domcontentloaded')

                # Esperar a que cargue el primer resultado
                page.wait_for_selector('a#video-title', timeout=10000)

                # Obtener el primer resultado
                first_result = page.query_selector('a#video-title')
                if first_result:
                    href = first_result.get_attribute('href')
                    if href:
                        video_url = f"https://www.youtube.com{href}"
                        browser.close()
                        return video_url

                browser.close()
                return None

        except Exception as e:
            print(f"❌ Error buscando en YouTube: {str(e)}")
            return None

    def search_youtube_ytdlp(self, search_query: str) -> Optional[str]:
        """
        Busca en YouTube usando yt-dlp (método alternativo, más rápido)

        Args:
            search_query: Query de búsqueda

        Returns:
            URL del primer resultado de YouTube o None
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch1',  # Buscar 1 resultado
                'extract_flat': True,  # No descargar, solo obtener URL
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_query, download=False)
                if result and 'entries' in result and len(result['entries']) > 0:
                    video_url = f"https://www.youtube.com/watch?v={result['entries'][0]['id']}"
                    return video_url

            return None

        except Exception as e:
            print(f"❌ Error buscando con yt-dlp: {str(e)}")
            return None


class SpotifyToYouTubeDownloader:
    """Clase principal que combina Spotify + YouTube + Download"""

    def __init__(self, output_folder: str = "./downloads",
                 spotify_client_id: str = None,
                 spotify_client_secret: str = None,
                 use_playwright: bool = False):
        self.downloader = YouTubeDownloader(output_folder)
        self.converter = SpotifyYouTubeConverter(spotify_client_id, spotify_client_secret)
        self.use_playwright = use_playwright

    def download_from_spotify_playlist(self, playlist_url: str,
                                      max_songs: Optional[int] = None) -> Dict[str, any]:
        """
        Descarga todas las canciones de una playlist de Spotify desde YouTube

        Args:
            playlist_url: URL de la playlist de Spotify
            max_songs: Número máximo de canciones a descargar (None = todas)

        Returns:
            Diccionario con estadísticas de descarga
        """
        print(f"\n{'='*60}")
        print(f"🎵 SPOTIFY → YOUTUBE → MP3 DOWNLOADER")
        print(f"{'='*60}\n")

        # 1. Obtener canciones de Spotify
        tracks = self.converter.get_playlist_tracks(playlist_url)

        if not tracks:
            return {'success': 0, 'failed': 0, 'total': 0}

        # Limitar cantidad si se especifica
        if max_songs:
            tracks = tracks[:max_songs]

        # 2. Buscar y descargar cada canción
        stats = {'success': 0, 'failed': 0, 'total': len(tracks)}

        for i, track in enumerate(tracks, 1):
            print(f"\n[{i}/{len(tracks)}] 🎵 {track['search_query']}")

            # Buscar en YouTube
            if self.use_playwright:
                youtube_url = self.converter.search_youtube_playwright(track['search_query'])
            else:
                youtube_url = self.converter.search_youtube_ytdlp(track['search_query'])

            if not youtube_url:
                print(f"❌ No se encontró en YouTube")
                stats['failed'] += 1
                continue

            print(f"🔗 Encontrado: {youtube_url}")

            # Descargar
            success = self.downloader.download_mp3(youtube_url, custom_filename=track['search_query'])

            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1

            # Pausa entre descargas para no saturar
            if i < len(tracks):
                time.sleep(2)

        # Resumen
        print(f"\n{'='*60}")
        print(f"📊 RESUMEN DE DESCARGA")
        print(f"{'='*60}")
        print(f"✅ Exitosas: {stats['success']}")
        print(f"❌ Fallidas: {stats['failed']}")
        print(f"📦 Total: {stats['total']}")
        print(f"{'='*60}\n")

        return stats


def main():
    """Función principal con menú interactivo"""

    print("""
╔══════════════════════════════════════════════════════════╗
║     🎵 SPOTIFY → YOUTUBE MP3 DOWNLOADER 🎵               ║
╚══════════════════════════════════════════════════════════╝
    """)

    print("\n¿Qué deseas hacer?\n")
    print("1️⃣  Descargar MP3 desde URL de YouTube")
    print("2️⃣  Descargar playlist completa de Spotify → YouTube")
    print("3️⃣  Salir")

    choice = input("\n👉 Selecciona una opción (1-3): ").strip()

    if choice == "1":
        # Opción 1: Descargar desde YouTube directamente
        print("\n" + "="*60)
        youtube_url = input("🔗 Ingresa la URL de YouTube: ").strip()
        output_folder = input("📁 Carpeta de salida (Enter = ./downloads): ").strip() or "./downloads"

        downloader = YouTubeDownloader(output_folder)
        downloader.download_mp3(youtube_url)

    elif choice == "2":
        # Opción 2: Playlist de Spotify
        print("\n" + "="*60)
        print("📋 Para usar Spotify necesitas Client ID y Client Secret")
        print("   Obtenerlos en: https://developer.spotify.com/dashboard")
        print("="*60 + "\n")

        client_id = input("🔑 Spotify Client ID: ").strip()
        client_secret = input("🔑 Spotify Client Secret: ").strip()
        playlist_url = input("🔗 URL de la playlist de Spotify: ").strip()
        output_folder = input("📁 Carpeta de salida (Enter = ./downloads): ").strip() or "./downloads"

        max_songs_input = input("🔢 Máximo de canciones (Enter = todas): ").strip()
        max_songs = int(max_songs_input) if max_songs_input else None

        use_playwright_input = input("🌐 ¿Usar Playwright para búsqueda? (s/N): ").strip().lower()
        use_playwright = use_playwright_input == 's'

        app = SpotifyToYouTubeDownloader(
            output_folder=output_folder,
            spotify_client_id=client_id,
            spotify_client_secret=client_secret,
            use_playwright=use_playwright
        )

        app.download_from_spotify_playlist(playlist_url, max_songs)

    elif choice == "3":
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)

    else:
        print("\n❌ Opción no válida")


if __name__ == "__main__":
    main()
