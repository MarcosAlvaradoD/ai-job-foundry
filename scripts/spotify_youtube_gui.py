"""
Spotify → YouTube MP3 Downloader - Interfaz Gráfica
Versión GUI con tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import sys
from pathlib import Path
import re

try:
    import yt_dlp
except ImportError:
    print("❌ yt-dlp no instalado. Ejecuta: pip install yt-dlp")
    sys.exit(1)

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False


class SpotifyYouTubeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Spotify → YouTube MP3 Downloader")
        self.root.geometry("700x600")

        # Variables
        self.output_folder = tk.StringVar(value="./downloads")
        self.download_running = False

        self.create_widgets()

    def create_widgets(self):
        # Título
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="🎵 Spotify → YouTube MP3 Downloader",
            font=("Arial", 16, "bold")
        )
        title_label.pack()

        # Notebook (pestañas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: YouTube Download
        youtube_tab = ttk.Frame(notebook, padding="10")
        notebook.add(youtube_tab, text="📥 Descargar desde YouTube")
        self.create_youtube_tab(youtube_tab)

        # Tab 2: Spotify Playlist
        spotify_tab = ttk.Frame(notebook, padding="10")
        notebook.add(spotify_tab, text="🎵 Playlist de Spotify")
        self.create_spotify_tab(spotify_tab)

        # Tab 3: Configuración
        config_tab = ttk.Frame(notebook, padding="10")
        notebook.add(config_tab, text="⚙️ Configuración")
        self.create_config_tab(config_tab)

        # Log panel (inferior)
        log_frame = ttk.LabelFrame(self.root, text="📋 Log de descargas", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            width=80,
            state='disabled',
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_youtube_tab(self, parent):
        # URL Input
        url_frame = ttk.LabelFrame(parent, text="🔗 URL de YouTube", padding="10")
        url_frame.pack(fill=tk.X, pady=5)

        self.youtube_url = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.youtube_url, width=60)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón de descarga
        download_btn = ttk.Button(
            parent,
            text="⬇️ Descargar MP3",
            command=self.download_youtube,
            style="Accent.TButton"
        )
        download_btn.pack(pady=10)

        # Instrucciones
        instructions = """
📌 Instrucciones:
1. Copia la URL del video de YouTube
2. Pégala en el campo de arriba
3. Haz clic en "Descargar MP3"
4. El archivo se guardará en la carpeta seleccionada

⚠️ Notas:
- Solo se descargará el audio (no el video)
- Si la URL contiene una playlist, solo se descargará el primer video
- Videos con restricción de edad pueden fallar
        """

        instructions_label = ttk.Label(
            parent,
            text=instructions,
            justify=tk.LEFT,
            foreground="gray"
        )
        instructions_label.pack(pady=5, anchor=tk.W)

    def create_spotify_tab(self, parent):
        if not SPOTIFY_AVAILABLE:
            warning = ttk.Label(
                parent,
                text="⚠️ Spotipy no instalado. Ejecuta: pip install spotipy",
                foreground="orange"
            )
            warning.pack(pady=10)

        # Credenciales
        cred_frame = ttk.LabelFrame(parent, text="🔑 Credenciales de Spotify", padding="10")
        cred_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cred_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.spotify_client_id = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.spotify_client_id, width=50).grid(row=0, column=1, pady=2)

        ttk.Label(cred_frame, text="Client Secret:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.spotify_client_secret = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.spotify_client_secret, width=50, show="*").grid(row=1, column=1, pady=2)

        # URL de playlist
        playlist_frame = ttk.LabelFrame(parent, text="🎵 Playlist URL", padding="10")
        playlist_frame.pack(fill=tk.X, pady=5)

        self.spotify_playlist_url = tk.StringVar()
        ttk.Entry(playlist_frame, textvariable=self.spotify_playlist_url, width=60).pack()

        # Opciones
        options_frame = ttk.LabelFrame(parent, text="⚙️ Opciones", padding="10")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="Máximo de canciones:").grid(row=0, column=0, sticky=tk.W)
        self.max_songs = tk.StringVar(value="10")
        ttk.Entry(options_frame, textvariable=self.max_songs, width=10).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(options_frame, text="(vacío = todas)").grid(row=0, column=2, sticky=tk.W)

        # Botón
        download_btn = ttk.Button(
            parent,
            text="⬇️ Descargar Playlist",
            command=self.download_spotify_playlist,
            style="Accent.TButton"
        )
        download_btn.pack(pady=10)

        # Link
        help_label = ttk.Label(
            parent,
            text="💡 Obtén tus credenciales en: https://developer.spotify.com/dashboard",
            foreground="blue",
            cursor="hand2"
        )
        help_label.pack(pady=5)
        help_label.bind("<Button-1>", lambda e: self.open_url("https://developer.spotify.com/dashboard"))

    def create_config_tab(self, parent):
        # Carpeta de salida
        folder_frame = ttk.LabelFrame(parent, text="📁 Carpeta de salida", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(folder_frame, textvariable=self.output_folder, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="📂 Buscar", command=self.select_folder).pack(side=tk.LEFT)

        # Calidad de audio
        quality_frame = ttk.LabelFrame(parent, text="🎵 Calidad de audio", padding="10")
        quality_frame.pack(fill=tk.X, pady=5)

        self.audio_quality = tk.StringVar(value="192")
        ttk.Radiobutton(quality_frame, text="128 kbps (Buena)", variable=self.audio_quality, value="128").pack(anchor=tk.W)
        ttk.Radiobutton(quality_frame, text="192 kbps (Muy buena)", variable=self.audio_quality, value="192").pack(anchor=tk.W)
        ttk.Radiobutton(quality_frame, text="320 kbps (Excelente)", variable=self.audio_quality, value="320").pack(anchor=tk.W)

        # Opciones avanzadas
        advanced_frame = ttk.LabelFrame(parent, text="🔧 Opciones avanzadas", padding="10")
        advanced_frame.pack(fill=tk.X, pady=5)

        self.no_playlist = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame,
            text="Descargar solo el video (ignorar playlist si la URL la contiene)",
            variable=self.no_playlist
        ).pack(anchor=tk.W)

        self.cookies_browser = tk.StringVar(value="none")
        ttk.Label(advanced_frame, text="Usar cookies del navegador (para videos con restricción):").pack(anchor=tk.W, pady=(10,0))
        ttk.Radiobutton(advanced_frame, text="Ninguno", variable=self.cookies_browser, value="none").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(advanced_frame, text="Chrome", variable=self.cookies_browser, value="chrome").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(advanced_frame, text="Firefox", variable=self.cookies_browser, value="firefox").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(advanced_frame, text="Edge", variable=self.cookies_browser, value="edge").pack(anchor=tk.W, padx=20)

    def log(self, message):
        """Agregar mensaje al log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def select_folder(self):
        """Seleccionar carpeta de salida"""
        folder = filedialog.askdirectory(initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)

    def open_url(self, url):
        """Abrir URL en navegador"""
        import webbrowser
        webbrowser.open(url)

    def download_youtube(self):
        """Descargar desde YouTube"""
        url = self.youtube_url.get().strip()

        if not url:
            messagebox.showwarning("⚠️ URL vacía", "Por favor ingresa una URL de YouTube")
            return

        if self.download_running:
            messagebox.showwarning("⚠️ Descarga en curso", "Espera a que termine la descarga actual")
            return

        # Ejecutar en thread separado
        thread = threading.Thread(target=self._download_youtube_thread, args=(url,))
        thread.daemon = True
        thread.start()

    def _download_youtube_thread(self, url):
        """Thread de descarga de YouTube"""
        self.download_running = True

        try:
            self.log(f"🎵 Descargando: {url}")

            # Configuración de yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.audio_quality.get(),
                }],
                'outtmpl': str(Path(self.output_folder.get()) / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
            }

            # No descargar playlist completa
            if self.no_playlist.get():
                ydl_opts['noplaylist'] = True

            # Cookies del navegador
            if self.cookies_browser.get() != "none":
                ydl_opts['cookiesfrombrowser'] = (self.cookies_browser.get(),)

            # Descargar
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')

                self.log(f"✅ Descargado exitosamente: {title}")
                self.log(f"📁 Ubicación: {self.output_folder.get()}\n")

                messagebox.showinfo("✅ Descarga completada", f"Descargado: {title}")

        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ Error: {error_msg}\n")

            # Sugerencia para restricción de edad
            if "age" in error_msg.lower() or "sign in" in error_msg.lower():
                messagebox.showerror(
                    "❌ Error de restricción",
                    "Este video tiene restricción de edad.\n\n"
                    "Solución: Ve a Configuración y selecciona un navegador "
                    "en 'Usar cookies del navegador'."
                )
            else:
                messagebox.showerror("❌ Error", f"Error al descargar:\n{error_msg}")

        finally:
            self.download_running = False

    def progress_hook(self, d):
        """Hook de progreso de descarga"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            self.log(f"⬇️  {percent} - {speed} - ETA: {eta}")
        elif d['status'] == 'finished':
            self.log("🔄 Convirtiendo a MP3...")

    def download_spotify_playlist(self):
        """Descargar playlist de Spotify"""
        if not SPOTIFY_AVAILABLE:
            messagebox.showerror("❌ Error", "Spotipy no instalado.\nEjecuta: pip install spotipy")
            return

        client_id = self.spotify_client_id.get().strip()
        client_secret = self.spotify_client_secret.get().strip()
        playlist_url = self.spotify_playlist_url.get().strip()

        if not client_id or not client_secret:
            messagebox.showwarning("⚠️ Credenciales faltantes", "Por favor ingresa tu Client ID y Client Secret")
            return

        if not playlist_url:
            messagebox.showwarning("⚠️ URL faltante", "Por favor ingresa la URL de la playlist")
            return

        messagebox.showinfo(
            "🚧 En desarrollo",
            "Esta funcionalidad estará disponible próximamente.\n\n"
            "Por ahora usa la versión de línea de comandos:\n"
            "python spotify_youtube_downloader.py"
        )


def main():
    root = tk.Tk()
    app = SpotifyYouTubeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
