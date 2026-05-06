"""
INTERVIEW COPILOT OVERLAY - INVISIBLE DURANTE SCREEN SHARE
===========================================================
Ventana flotante que NO aparece en grabaciones/Zoom/Teams/Meet.
Funciona como APUNTADOR INVISIBLE durante videollamadas de trabajo.

CARACTERISTICAS:
  INVISIBLE en Zoom, Teams, Google Meet, OBS (WDA_EXCLUDEFROMCAPTURE)
  Siempre encima de todas las ventanas
  Semi-transparente, no molesta visualmente
  VOZ: Ctrl+L mantener presionado para escuchar, soltar para procesar
       SIN sonido de salida - solo texto en pantalla
  Cargar perfil/job desde Google Sheets con boton dedicado
  Botones de preguntas frecuentes (STAR, cuéntame de ti, etc.)
  Conecta a LM Studio local (Qwen2.5 14B)
  Carga CV automaticamente desde data/cv_descriptor.txt

INSTALACION:
  pip install SpeechRecognition sounddevice scipy keyboard

USO:
  py core/copilot/interview_copilot_overlay.py

HOTKEYS:
  Ctrl+L         -> MANTENER para escuchar / soltar para procesar
  Ctrl+Shift+H   -> Mostrar / Ocultar ventana completa
  Enter          -> Enviar texto al AI
  Escape         -> Limpiar
  Ctrl+Q         -> Cerrar

Autor: AI Job Foundry - Marcos Alberto Alvarado
Fecha: 2026-03-27
"""

import sys
import os
import json
import threading
import ctypes
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path
from datetime import datetime

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
CV_PATH      = PROJECT_ROOT / "data" / "cv_descriptor.txt"
LOG_PATH     = PROJECT_ROOT / "logs" / "copilot_sessions"

# ─── LM Studio (detecta IP automaticamente) ──────────────────────────────────
# Lee del .env si está disponible; si no, prueba la lista de hosts
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

_env_url   = os.getenv("LM_STUDIO_URL", "").strip()
_env_model = os.getenv("LM_STUDIO_MODEL", "").strip()

# El host del .env va primero en la lista de candidatos
LM_STUDIO_HOSTS = list(dict.fromkeys(filter(None, [
    _env_url,
    "http://127.0.0.1:11434",
    "http://localhost:11434",
    "http://127.0.0.1:1234",
    "http://192.168.100.39:11434",
    "http://192.168.100.28:11434",
    "http://172.17.32.1:11434",
    "http://192.168.100.39:1234",
])))

# Modelo del .env; fallback al modelo anterior si no está configurado
LM_STUDIO_MODEL = _env_model or "qwen2.5-14b-instruct"

# ─── Intentar importar librerias de voz ──────────────────────────────────────
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wavfile
    HAS_SD = True
except ImportError:
    HAS_SD = False

# Whisper local (openai-whisper) — prioridad sobre Google SR
# Modelos disponibles: tiny(~75MB) base(~145MB) small(~465MB) medium(~1.5GB) large(~3GB)
# Con RTX 4090 usa GPU automaticamente (10x mas rapido que CPU)
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")   # configurable via .env
_whisper_model = None   # cargado lazy al primer uso

def _load_whisper():
    """Carga el modelo Whisper la primera vez que se necesita (lazy load)."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        print(f"[Whisper] Cargando modelo '{WHISPER_MODEL_SIZE}'... (puede tomar 5-10s la primera vez)")
        _whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
        print(f"[Whisper] ✓ Modelo '{WHISPER_MODEL_SIZE}' listo")
        return _whisper_model
    except ImportError:
        return None
    except Exception as e:
        print(f"[Whisper] Error cargando modelo: {e}")
        return None

try:
    import whisper as _whisper_test
    HAS_WHISPER = True
    del _whisper_test
except ImportError:
    HAS_WHISPER = False

# ─── Colores ─────────────────────────────────────────────────────────────────
BG_DARK     = "#0d1117"
BG_CARD     = "#161b22"
BG_INPUT    = "#21262d"
FG_TEXT     = "#e6edf3"
FG_MUTED    = "#8b949e"
ACCENT_BLUE = "#58a6ff"
ACCENT_GRN  = "#3fb950"
ACCENT_YLW  = "#d29922"
ACCENT_RED  = "#f85149"
BORDER      = "#30363d"
ACCENT_VOICE = "#ff7b54"   # Naranja para indicador de voz

# ─── Preguntas rapidas ────────────────────────────────────────────────────────
QUICK_QUESTIONS = [
    ("Háblame de ti",        "Cuéntame de ti, tu background y experiencia profesional"),
    ("Mayor fortaleza",      "Cuál es tu mayor fortaleza profesional?"),
    ("Mayor debilidad",      "Cuál es tu mayor debilidad y cómo la manejas?"),
    ("Logro importante",     "Cuál es tu logro profesional más importante?"),
    ("Conflictos",           "Cuéntame de una vez que manejaste un conflicto en el equipo"),
    ("Gestión proyectos",    "Cómo manejas múltiples proyectos simultáneamente?"),
    ("Cambio/adaptación",    "Ejemplo de adaptación a un cambio importante?"),
    ("Salario esperado",     "Cuál es tu expectativa de compensación?"),
    ("Por qué este rol",     "Por qué quieres este puesto específico?"),
    ("5 años",               "Dónde te ves en 5 años?"),
    ("Preguntas para ellos", "Qué preguntas tienes para nosotros?"),
]


# ═════════════════════════════════════════════════════════════════════════════
class InterviewCopilotOverlay:

    def __init__(self):
        self.cv_content   = self._load_cv()
        self.lm_url       = None
        self.job_context  = None
        self.session_log  = []
        self.is_thinking  = False
        self.is_listening = False
        self._listen_thread = None
        self._audio_frames  = []

        # Speech recognition
        self.recognizer  = sr.Recognizer() if HAS_SR else None
        self.microphone  = None   # Inicializar lazy para no bloquear el arranque

        self._build_ui()
        self._apply_capture_exclusion()
        self._detect_lm_studio()

    # ─── CV ──────────────────────────────────────────────────────────────────
    def _load_cv(self) -> str:
        if CV_PATH.exists():
            return CV_PATH.read_text(encoding="utf-8", errors="ignore")[:3000]
        return ""

    # ─── LM Studio ───────────────────────────────────────────────────────────
    def _detect_lm_studio(self):
        threading.Thread(target=self._find_lm_studio, daemon=True).start()

    def _find_lm_studio(self):
        import urllib.request, urllib.error
        for host in LM_STUDIO_HOSTS:
            try:
                req = urllib.request.Request(
                    f"{host}/v1/models",
                    headers={"Content-Type": "application/json"},
                    method="GET"
                )
                urllib.request.urlopen(req, timeout=2)
                self.lm_url = host
                self._status(f"LM Studio: {host}", ACCENT_GRN)
                return
            except Exception:
                continue
        self._status("LM Studio no encontrado — verifica que este corriendo", ACCENT_YLW)

    # ─── Windows capture exclusion ───────────────────────────────────────────
    def _apply_capture_exclusion(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        except Exception:
            pass

    def _reapply_capture_exclusion(self):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "AI Copilot")
            if not hwnd:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            if result:
                self._status("INVISIBLE en screen share activo", ACCENT_GRN)
        except Exception:
            pass

    # ─── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("AI Copilot")
        self.root.configure(bg=BG_DARK)

        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"430x680+{screen_w - 450}+10")
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.93)
        self.root.overrideredirect(True)

        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>",     self._do_drag)
        self._drag_x = self._drag_y = 0

        self._setup_hotkeys()

        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG_CARD, pady=5, cursor="fleur")
        hdr.pack(fill="x")
        hdr.bind("<ButtonPress-1>", self._start_drag)
        hdr.bind("<B1-Motion>",     self._do_drag)

        tk.Label(hdr, text="AI Interview Copilot",
                 bg=BG_CARD, fg=FG_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

        # Indicador de voz (siempre visible, cambia color)
        self.voice_indicator = tk.Label(
            hdr, text="MIC OFF",
            bg=BORDER, fg=FG_MUTED,
            font=("Segoe UI", 7, "bold"),
            padx=6, pady=2, relief="flat"
        )
        self.voice_indicator.pack(side="left", padx=4)

        btns = tk.Frame(hdr, bg=BG_CARD)
        btns.pack(side="right", padx=6)
        self._btn(btns, "─", self.root.iconify, BG_CARD, FG_MUTED).pack(side="left")
        self._btn(btns, "x", self._quit, BG_CARD, ACCENT_RED).pack(side="left")

        # ── Status ──────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Iniciando...")
        self.status_lbl = tk.Label(
            self.root, textvariable=self.status_var,
            bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 7), anchor="w", padx=8
        )
        self.status_lbl.pack(fill="x")

        # ── Job context badge ────────────────────────────────────────────────
        self.job_lbl = tk.Label(
            self.root, text="Sin job context — carga uno abajo",
            bg=BG_DARK, fg=ACCENT_YLW,
            font=("Segoe UI", 7, "italic"), anchor="w", padx=8
        )
        self.job_lbl.pack(fill="x")

        # ── Respuesta AI ─────────────────────────────────────────────────────
        resp_frame = tk.Frame(self.root, bg=BG_CARD, padx=6, pady=4)
        resp_frame.pack(fill="both", expand=True, padx=6, pady=(4, 2))

        tk.Label(resp_frame, text="Sugerencia AI",
                 bg=BG_CARD, fg=ACCENT_BLUE,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x")

        self.response_text = scrolledtext.ScrolledText(
            resp_frame,
            bg=BG_CARD, fg=FG_TEXT,
            font=("Segoe UI", 9),
            wrap=tk.WORD, relief="flat",
            state="disabled", height=11,
            cursor="arrow",
            insertbackground=FG_TEXT
        )
        self.response_text.pack(fill="both", expand=True, pady=(3, 0))

        # ── Preguntas rapidas ─────────────────────────────────────────────────
        qf = tk.LabelFrame(
            self.root, text=" Preguntas frecuentes ",
            bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 7), bd=1, relief="flat",
            padx=3, pady=3
        )
        qf.pack(fill="x", padx=6, pady=(2, 2))

        for i, (label, question) in enumerate(QUICK_QUESTIONS):
            row, col = divmod(i, 2)
            tk.Button(
                qf, text=label,
                bg=BG_INPUT, fg=FG_TEXT,
                font=("Segoe UI", 7),
                relief="flat", bd=0, padx=3, pady=1,
                cursor="hand2",
                activebackground=BORDER, activeforeground=FG_TEXT,
                command=lambda q=question: self._ask(q)
            ).grid(row=row, column=col, sticky="ew", padx=1, pady=1)
        qf.columnconfigure(0, weight=1)
        qf.columnconfigure(1, weight=1)

        # ── Panel de voz + texto ─────────────────────────────────────────────
        voice_frame = tk.Frame(self.root, bg=BG_DARK, padx=6, pady=2)
        voice_frame.pack(fill="x")

        # Boton de VOZ (mantener presionado)
        voice_state = {"active": False}

        # Label del motor de voz activo
        engine_label = "🤖 Whisper local" if HAS_WHISPER else ("🌐 Google SR" if HAS_SR else "❌ Sin voz")
        btn_text = f"MANTENER = ESCUCHAR  (Ctrl+L / Ctrl+Shift+R toggle)\n{engine_label} · modelo {WHISPER_MODEL_SIZE}" if HAS_WHISPER or HAS_SR \
                   else "Voz no disponible — pip install openai-whisper sounddevice scipy"

        self.voice_btn = tk.Button(
            voice_frame,
            text=btn_text,
            bg=BG_INPUT if (HAS_WHISPER or HAS_SR) else ACCENT_RED,
            fg=FG_MUTED if (HAS_WHISPER or HAS_SR) else "#fff",
            font=("Segoe UI", 8, "bold"),
            relief="flat", bd=0,
            padx=8, pady=5,
            cursor="hand2",
            justify="center",
            activebackground=ACCENT_VOICE, activeforeground="#000"
        )
        self.voice_btn.pack(fill="x")

        # Bind press/release del boton (mantener = push-to-talk)
        self.voice_btn.bind("<ButtonPress-1>",   lambda e: self._start_listening())
        self.voice_btn.bind("<ButtonRelease-1>", lambda e: self._stop_listening())

        # ── Input de texto ───────────────────────────────────────────────────
        inp_frame = tk.Frame(self.root, bg=BG_DARK, padx=6, pady=2)
        inp_frame.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            inp_frame,
            textvariable=self.input_var,
            bg=BG_INPUT, fg=FG_MUTED,
            font=("Segoe UI", 9),
            relief="flat", bd=4,
            insertbackground=FG_TEXT
        )
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<Return>",  lambda e: self._ask_from_input())
        self.input_entry.bind("<Escape>",  lambda e: self._clear())
        self.input_entry.bind("<FocusIn>", self._ph_clear)
        self.input_entry.bind("<FocusOut>",self._ph_restore)
        self._placeholder = "Escribe la pregunta..."
        self.input_entry.insert(0, self._placeholder)

        self._btn(inp_frame, "->", self._ask_from_input, ACCENT_BLUE, BG_DARK, 8).pack(side="left", padx=(3,0))

        # ── Job context / perfil ─────────────────────────────────────────────
        job_frame = tk.Frame(self.root, bg=BG_DARK, padx=6)
        job_frame.pack(fill="x", pady=(0, 4))

        self.job_input_var = tk.StringVar()
        job_entry = tk.Entry(
            job_frame,
            textvariable=self.job_input_var,
            bg=BG_INPUT, fg=FG_MUTED,
            font=("Segoe UI", 8),
            relief="flat", bd=4,
            insertbackground=FG_TEXT
        )
        job_entry.pack(side="left", fill="x", expand=True)
        job_entry.insert(0, "Empresa / Puesto  (ej: TCS — PM)")
        job_entry.bind("<FocusIn>",  lambda e: (job_entry.delete(0,"end"), job_entry.config(fg=FG_TEXT)))
        job_entry.bind("<Return>",   lambda e: self._set_job_context())

        self._btn(job_frame, "Set",
                  self._set_job_context, BORDER, FG_TEXT, 5).pack(side="left", padx=(2,0))
        self._btn(job_frame, "Sheets",
                  self._load_job_from_sheets_async, ACCENT_BLUE, BG_DARK, 5).pack(side="left", padx=(2,0))

        # ── Hint ─────────────────────────────────────────────────────────────
        whisper_hint = f"Whisper:{WHISPER_MODEL_SIZE}(GPU)" if HAS_WHISPER else ("GoogleSR" if HAS_SR else "SinVoz")
        tk.Label(
            self.root,
            text=f"Ctrl+L=Mantener  Ctrl+Shift+R=Toggle  Ctrl+Shift+H=Ocultar  [{whisper_hint}]  Invisible en Zoom/Teams",
            bg=BG_DARK, fg=BORDER, font=("Segoe UI", 6)
        ).pack(pady=(0, 3))

    # ─── Hotkeys ─────────────────────────────────────────────────────────────
    def _setup_hotkeys(self):
        try:
            import keyboard
            # Ctrl+L (original) — mantener presionado
            keyboard.add_hotkey("ctrl+l",           self._hotkey_voice_start, suppress=False)
            keyboard.on_release_key("l",            self._hotkey_voice_stop)
            # Ctrl+Shift+R (nuevo) — toggle push-to-talk
            keyboard.add_hotkey("ctrl+shift+r",     self._hotkey_voice_toggle, suppress=False)
            keyboard.add_hotkey("ctrl+shift+h",     self._toggle_visibility,  suppress=False)
            keyboard.add_hotkey("ctrl+q",           self._quit,               suppress=False)
        except ImportError:
            self.root.bind("<Control-l>",       lambda e: self._toggle_listening())
            self.root.bind("<Control-R>",       lambda e: self._toggle_listening())
            self.root.bind("<Control-h>",       lambda e: self._toggle_visibility())
            self.root.bind("<Control-q>",       lambda e: self._quit())

    def _hotkey_voice_toggle(self):
        """Ctrl+Shift+R — toggle: inicia o detiene la grabación."""
        if self.is_listening:
            self.root.after(0, self._stop_listening)
        else:
            self.root.after(0, self._start_listening)

    def _hotkey_voice_start(self):
        if not self.is_listening:
            self.root.after(0, self._start_listening)

    def _hotkey_voice_stop(self, event=None):
        if self.is_listening:
            self.root.after(0, self._stop_listening)

    def _toggle_visibility(self):
        if self.root.state() == 'withdrawn':
            self.root.after(0, self.root.deiconify)
            self.root.after(0, lambda: self.root.wm_attributes("-topmost", True))
        else:
            self.root.after(0, self.root.withdraw)

    # ─── VOZ: Grabar con sounddevice (mas confiable en Windows) ──────────────
    def _start_listening(self):
        # Para grabar audio necesitamos sounddevice (HAS_SD).
        # Para transcribir: Whisper O SpeechRecognition (cualquiera sirve).
        can_transcribe = HAS_WHISPER or HAS_SR
        if self.is_listening:
            return
        if not HAS_SD:
            self._status("Instala sounddevice: pip install sounddevice scipy", ACCENT_RED)
            return
        if not can_transcribe:
            self._status("Instala Whisper: pip install openai-whisper", ACCENT_RED)
            return
        self.is_listening = True
        self._audio_frames = []

        # UI feedback
        self.voice_btn.config(bg=ACCENT_VOICE, fg="#000",
                              text="ESCUCHANDO... (suelta para procesar)")
        self.voice_indicator.config(bg=ACCENT_VOICE, fg="#000", text="MIC ON")
        self._status("Escuchando... habla ahora", ACCENT_VOICE)

        # Iniciar grabacion en thread
        self._listen_thread = threading.Thread(target=self._record_audio, daemon=True)
        self._listen_thread.start()

    def _record_audio(self):
        """Graba audio con sounddevice mientras is_listening sea True."""
        SAMPLE_RATE = 16000
        CHANNELS = 1
        frames = []
        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                                dtype="int16") as stream:
                while self.is_listening:
                    data, _ = stream.read(1024)
                    frames.append(data.copy())
            self._audio_frames = frames
        except Exception as e:
            self.root.after(0, lambda: self._status(f"Error mic: {e}", ACCENT_RED))
            self.is_listening = False
            self._reset_voice_ui()

    def _stop_listening(self):
        if not self.is_listening:
            return
        self.is_listening = False

        self.voice_btn.config(bg=BG_INPUT, fg=FG_MUTED,
                              text="MANTENER = ESCUCHAR  (Ctrl+L)")
        self.voice_indicator.config(bg=BORDER, fg=FG_MUTED, text="MIC OFF")
        self._status("Procesando audio...", ACCENT_BLUE)

        threading.Thread(target=self._transcribe_and_ask, daemon=True).start()

    def _transcribe_and_ask(self):
        """
        Transcribe el audio grabado y lo envía al AI.
        Prioridad: Whisper local (GPU) → Google Web Speech → error
        """
        import tempfile
        if not self._audio_frames:
            self.root.after(0, lambda: self._status("Sin audio grabado", ACCENT_YLW))
            return

        SAMPLE_RATE = 16000
        tmp_path = None
        try:
            # ── Guardar audio WAV temporal ──────────────────────────────
            frames_np = np.concatenate(self._audio_frames, axis=0)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            wavfile.write(tmp_path, SAMPLE_RATE, frames_np)

            text = None

            # ── OPCION 1: Whisper local (sin internet, GPU, offline) ────
            if HAS_WHISPER:
                self.root.after(0, lambda: self._status("Transcribiendo con Whisper (local)...", ACCENT_BLUE))
                try:
                    model = _load_whisper()
                    if model:
                        # fp16=True aprovecha la RTX 4090 (o cualquier CUDA GPU)
                        result = model.transcribe(
                            tmp_path,
                            language=None,       # auto-detecta español/inglés
                            fp16=True,           # GPU half-precision (más rápido)
                            condition_on_previous_text=False,
                        )
                        text = result.get("text", "").strip()
                        detected_lang = result.get("language", "?")
                        if text:
                            self.root.after(0, lambda: self._status(
                                f"Whisper [{detected_lang}]: {text[:50]}", ACCENT_GRN))
                except Exception as e:
                    self.root.after(0, lambda: self._status(
                        f"Whisper error — usando Google SR: {e}", ACCENT_YLW))

            # ── OPCION 2: Google Web Speech (requiere internet) ─────────
            if not text and HAS_SR and self.recognizer:
                self.root.after(0, lambda: self._status("Transcribiendo con Google SR...", ACCENT_BLUE))
                try:
                    with sr.AudioFile(tmp_path) as source:
                        audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data, language="es-MX")
                    except sr.UnknownValueError:
                        text = self.recognizer.recognize_google(audio_data, language="en-US")
                except sr.UnknownValueError:
                    self.root.after(0, lambda: self._status(
                        "Audio no reconocido — habla más claro o escribe", ACCENT_YLW))
                    return
                except sr.RequestError:
                    self.root.after(0, lambda: self._status(
                        "Sin internet para Google SR — instala Whisper: pip install openai-whisper", ACCENT_YLW))
                    return

            if not text:
                if not HAS_WHISPER and not HAS_SR:
                    self.root.after(0, lambda: self._status(
                        "Instala Whisper: pip install openai-whisper sounddevice scipy", ACCENT_RED))
                else:
                    self.root.after(0, lambda: self._status("No se detectó voz — intenta de nuevo", ACCENT_YLW))
                return

            # ── Mostrar transcripción y enviar al AI ───────────────────
            self.root.after(0, lambda t=text: (
                self.input_var.set(t),
                self.input_entry.config(fg=FG_TEXT)
            ))
            self.root.after(200, lambda t=text: self._ask(t))

        except Exception as e:
            self.root.after(0, lambda: self._status(f"Error transcripcion: {e}", ACCENT_RED))
        finally:
            if tmp_path:
                try: os.unlink(tmp_path)
                except Exception: pass

    def _reset_voice_ui(self):
        self.voice_btn.config(bg=BG_INPUT, fg=FG_MUTED,
                              text="MANTENER = ESCUCHAR  (Ctrl+L)")
        self.voice_indicator.config(bg=BORDER, fg=FG_MUTED, text="MIC OFF")

    def _toggle_listening(self):
        if self.is_listening:
            self._stop_listening()
        else:
            self._start_listening()

    # ─── Cargar job desde Sheets ──────────────────────────────────────────────
    def _load_job_from_sheets_async(self):
        """Inicia carga de jobs desde Google Sheets en background."""
        self._status("Cargando jobs del Sheet...", ACCENT_BLUE)
        threading.Thread(target=self._fetch_top_jobs, daemon=True).start()

    def _fetch_top_jobs(self):
        """Lee jobs FIT>=7 del Sheet y los muestra para seleccionar."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from dotenv import load_dotenv
            load_dotenv(PROJECT_ROOT / ".env")
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            token_path = PROJECT_ROOT / "data" / "credentials" / "token.json"
            if not token_path.exists():
                self.root.after(0, lambda: self._status("No hay token OAuth — regenera credenciales (opcion 21)", ACCENT_RED))
                return

            creds = Credentials.from_authorized_user_file(str(token_path))
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())

            service = build("sheets", "v4", credentials=creds)
            sheet_id = os.getenv("GOOGLE_SHEETS_ID", "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg")

            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="LinkedIn!A1:R200"
            ).execute()
            values = result.get("values", [])
            if not values:
                self.root.after(0, lambda: self._status("Sheet vacio", ACCENT_YLW))
                return

            headers = values[0]
            col_role    = headers.index("Role")      if "Role"      in headers else 2
            col_company = headers.index("Company")   if "Company"   in headers else 1
            col_fit     = next((i for i,h in enumerate(headers) if "fit" in h.lower()), 17)
            col_url     = headers.index("ApplyURL")  if "ApplyURL"  in headers else 5

            def safe_fit(v):
                try:
                    s = str(v).strip()
                    return int(s.split("/")[0]) if "/" in s else int(float(s))
                except Exception: return 0

            jobs = []
            for row in values[1:]:
                if len(row) <= col_fit: continue
                fit = safe_fit(row[col_fit] if col_fit < len(row) else 0)
                if fit >= 7:
                    jobs.append({
                        "role":    row[col_role]    if col_role    < len(row) else "?",
                        "company": row[col_company] if col_company < len(row) else "?",
                        "fit":     fit,
                        "url":     row[col_url]     if col_url     < len(row) else "",
                    })

            jobs.sort(key=lambda j: j["fit"], reverse=True)
            top = jobs[:12]

            if not top:
                self.root.after(0, lambda: self._status("Sin jobs FIT>=7 en LinkedIn tab", ACCENT_YLW))
                return

            self.root.after(0, lambda: self._show_job_selector(top))

        except Exception as e:
            self.root.after(0, lambda: self._status(f"Error Sheets: {e}", ACCENT_RED))

    def _show_job_selector(self, jobs: list):
        """Ventana emergente para elegir job de la lista."""
        popup = tk.Toplevel(self.root)
        popup.title("Seleccionar Job")
        popup.configure(bg=BG_DARK)
        popup.wm_attributes("-topmost", True)
        popup.geometry("420x360")

        tk.Label(popup, text="Selecciona el job para esta entrevista:",
                 bg=BG_DARK, fg=FG_TEXT,
                 font=("Segoe UI", 9, "bold")).pack(padx=10, pady=(10,4))

        lb_frame = tk.Frame(popup, bg=BG_DARK)
        lb_frame.pack(fill="both", expand=True, padx=10, pady=4)

        scrollbar = tk.Scrollbar(lb_frame, bg=BORDER)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(
            lb_frame,
            bg=BG_CARD, fg=FG_TEXT,
            font=("Segoe UI", 9),
            selectbackground=ACCENT_BLUE, selectforeground=BG_DARK,
            relief="flat", bd=0,
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        for j in jobs:
            listbox.insert("end", f"[{j['fit']}/10]  {j['company'][:20]} - {j['role'][:35]}")

        def confirm():
            sel = listbox.curselection()
            if sel:
                j = jobs[sel[0]]
                context = f"{j['company']} — {j['role']}"
                self.job_context = context
                self.job_lbl.config(text=f"Job: {context[:65]}", fg=ACCENT_GRN)
                self.job_input_var.set(context)
                self._status(f"Contexto: {context[:45]}", ACCENT_GRN)
            popup.destroy()

        btn_frame = tk.Frame(popup, bg=BG_DARK)
        btn_frame.pack(fill="x", padx=10, pady=8)
        self._btn(btn_frame, "Seleccionar", confirm, ACCENT_BLUE, BG_DARK, 12).pack(side="left")
        self._btn(btn_frame, "Cancelar",    popup.destroy, BORDER,      FG_TEXT, 8).pack(side="left", padx=4)
        listbox.bind("<Double-Button-1>", lambda e: confirm())

    # ─── Job context manual ───────────────────────────────────────────────────
    def _set_job_context(self):
        v = self.job_input_var.get().strip()
        if v and v != "Empresa / Puesto  (ej: TCS — PM)":
            self.job_context = v
            self.job_lbl.config(text=f"Job: {v[:65]}", fg=ACCENT_GRN)
            self._status(f"Contexto: {v[:40]}", ACCENT_GRN)

    # ─── Drag ────────────────────────────────────────────────────────────────
    def _start_drag(self, e):
        self._drag_x = e.x_root - self.root.winfo_x()
        self._drag_y = e.y_root - self.root.winfo_y()

    def _do_drag(self, e):
        self.root.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    # ─── Helpers UI ──────────────────────────────────────────────────────────
    def _btn(self, parent, text, command, bg, fg, padx=6):
        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg,
            font=("Segoe UI", 8), relief="flat", bd=0,
            padx=padx, pady=2, cursor="hand2",
            activebackground=BORDER, activeforeground=FG_TEXT
        )

    def _status(self, msg, color=FG_MUTED):
        self.root.after(0, lambda: (
            self.status_var.set(msg),
            self.status_lbl.config(fg=color)
        ))

    def _set_response(self, text):
        self.response_text.config(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", text)
        self.response_text.config(state="disabled")

    def _append_response(self, chunk):
        self.response_text.config(state="normal")
        self.response_text.insert("end", chunk)
        self.response_text.see("end")
        self.response_text.config(state="disabled")

    def _clear(self):
        self._set_response("")
        self.input_var.set("")

    def _ph_clear(self, e):
        if self.input_entry.get() == self._placeholder:
            self.input_entry.delete(0, "end")
            self.input_entry.config(fg=FG_TEXT)

    def _ph_restore(self, e):
        if not self.input_entry.get():
            self.input_entry.insert(0, self._placeholder)
            self.input_entry.config(fg=FG_MUTED)

    def _quit(self):
        self._save_session_log()
        self.root.destroy()

    # ─── AI ──────────────────────────────────────────────────────────────────
    def _ask_from_input(self):
        q = self.input_var.get().strip()
        if not q or q == self._placeholder:
            return
        self.input_var.set("")
        self.input_entry.config(fg=FG_TEXT)
        self._ask(q)

    def _ask(self, question: str):
        if self.is_thinking:
            return
        if not self.lm_url:
            self._set_response("LM Studio no disponible.\n\nAsegurate de que este corriendo con el modelo cargado.")
            return
        self.is_thinking = True
        self._set_response("Pensando...")
        self._status("Consultando AI...", ACCENT_BLUE)
        self.session_log.append({"timestamp": datetime.now().isoformat(),
                                  "question": question, "response": ""})
        threading.Thread(target=self._call_lm_studio, args=(question,), daemon=True).start()

    def _build_system_prompt(self) -> str:
        prompt = """Eres un asistente experto para entrevistas de trabajo.
Tu rol: ayudar al candidato a responder preguntas de forma clara y persuasiva.

INSTRUCCIONES:
- Respuesta CORTA (max 5 oraciones)
- Usa ejemplos concretos del CV del candidato
- Logros con numeros cuando sea posible
- STAR method para preguntas comportamentales
- Responde en primera persona, como si fueras el candidato hablando
- No digas "Como candidato..." — habla directamente
"""
        if self.cv_content:
            prompt += f"\n\nCV / PERFIL:\n{self.cv_content[:2500]}"
        if self.job_context:
            prompt += f"\n\nPUESTO AL QUE APLICA: {self.job_context}"
        return prompt

    def _call_lm_studio(self, question: str):
        import urllib.request, urllib.error
        import json as _json

        payload = _json.dumps({
            "model": LM_STUDIO_MODEL,
            "messages": [
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user",   "content": question}
            ],
            "temperature": 0.45,
            "max_tokens": 320,
            "stream": True
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{self.lm_url}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
                method="POST"
            )
            self.root.after(0, lambda: self._set_response(""))
            full = ""

            with urllib.request.urlopen(req, timeout=60) as resp:
                for line in resp:
                    line = line.decode("utf-8").strip()
                    if not line.startswith("data: "): continue
                    data_str = line[6:]
                    if data_str == "[DONE]": break
                    try:
                        content = _json.loads(data_str)["choices"][0]["delta"].get("content","")
                        if content:
                            full += content
                            self.root.after(0, lambda c=content: self._append_response(c))
                    except Exception:
                        continue

            if self.session_log:
                self.session_log[-1]["response"] = full
            self.root.after(0, lambda: self._status("Listo — Enter o Ctrl+L para siguiente", ACCENT_GRN))

        except urllib.error.URLError as e:
            self.root.after(0, lambda: self._set_response(f"Error de conexion con LM Studio:\n{e}"))
            self.root.after(0, lambda: self._status("Error LM Studio", ACCENT_RED))
            self.lm_url = None
            threading.Thread(target=self._find_lm_studio, daemon=True).start()
        except Exception as e:
            self.root.after(0, lambda: self._set_response(f"Error: {e}"))
            self.root.after(0, lambda: self._status("Error", ACCENT_RED))
        finally:
            self.is_thinking = False

    # ─── Session log ─────────────────────────────────────────────────────────
    def _save_session_log(self):
        if not self.session_log:
            return
        try:
            LOG_PATH.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            (LOG_PATH / f"session_{ts}.json").write_text(
                json.dumps(self.session_log, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    # ─── Run ─────────────────────────────────────────────────────────────────
    def run(self):
        self.root.after(600, self._reapply_capture_exclusion)
        self.root.mainloop()


# ═════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 55)
    print("AI INTERVIEW COPILOT OVERLAY")
    print("=" * 55)
    print(f"CV: {'Cargado' if CV_PATH.exists() else 'No encontrado'}")
    if HAS_WHISPER and HAS_SD:
        print(f"Voz: ✅ Whisper local ({WHISPER_MODEL_SIZE}) + sounddevice — LISTO (sin internet)")
    elif HAS_SR and HAS_SD:
        print(f"Voz: ✅ SpeechRecognition + sounddevice — LISTO (requiere internet)")
    elif HAS_WHISPER and not HAS_SD:
        print(f"Voz: ⚠️  Whisper OK pero falta sounddevice → pip install sounddevice scipy")
    else:
        print(f"Voz: ❌ No disponible → pip install sounddevice scipy")
    print()
    print("HOTKEYS:")
    print("  Ctrl+L (mantener) = Escuchar / soltar = Procesar")
    print("  Ctrl+Shift+H      = Ocultar/Mostrar")
    print("  Enter             = Enviar texto")
    print("  Ctrl+Q            = Cerrar")
    print()
    print("INVISIBLE en Zoom / Teams / Google Meet / OBS")
    print("=" * 55)

    app = InterviewCopilotOverlay()
    app.run()


if __name__ == "__main__":
    main()
