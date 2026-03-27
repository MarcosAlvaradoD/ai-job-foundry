"""
INTERVIEW COPILOT OVERLAY - INVISIBLE DURANTE SCREEN SHARE
===========================================================
Ventana flotante que NO aparece en grabaciones/Zoom/Teams/Meet.
Funciona como APUNTADOR INVISIBLE durante videollamadas de trabajo.

CARACTERÍSTICAS:
  ✅ INVISIBLE en Zoom, Teams, Google Meet, OBS (WDA_EXCLUDEFROMCAPTURE)
  ✅ Siempre encima de todas las ventanas
  ✅ Semi-transparente, no molesta visualmente
  ✅ Ctrl+Shift+H → Mostrar / Ocultar instantáneo
  ✅ Escribe la pregunta → AI sugiere respuesta basada en TU CV
  ✅ Botones de preguntas frecuentes (STAR, "cuéntame de ti", etc.)
  ✅ Conecta a LM Studio local (Qwen2.5 14B) — sin enviar datos a internet
  ✅ Carga CV automáticamente desde data/cv_descriptor.txt

INSTALACIÓN (solo si falta algo):
  pip install keyboard requests

USO:
  py core/copilot/interview_copilot_overlay.py

HOTKEYS:
  Ctrl+Shift+H   → Mostrar / Ocultar ventana completa
  Enter          → Enviar pregunta al AI
  Escape         → Limpiar / Cancelar
  Ctrl+Q         → Cerrar copilot

Autor: AI Job Foundry — Marcos Alberto Alvarado
Fecha: 2026-03-26
"""

import sys
import os
import json
import threading
import ctypes
import tkinter as tk
from tkinter import scrolledtext, font as tkfont
from pathlib import Path
from datetime import datetime

# ─── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
CV_PATH = PROJECT_ROOT / "data" / "cv_descriptor.txt"
LOG_PATH = PROJECT_ROOT / "logs" / "copilot_sessions"

# ─── LM Studio config (detecta IP automáticamente) ──────────────────────────
LM_STUDIO_HOSTS = [
    "http://192.168.100.39:11434",   # IP actual del screenshot
    "http://192.168.100.28:11434",   # IP del .env
    "http://172.17.32.1:11434",      # Docker gateway
    "http://127.0.0.1:11434",        # localhost
    "http://localhost:11434",
    "http://192.168.100.39:1234",    # Puerto alternativo LM Studio
    "http://127.0.0.1:1234",
]
LM_STUDIO_MODEL = "qwen2.5-14b-instruct"

# ─── Colores del tema (oscuro, discreto) ────────────────────────────────────
BG_DARK     = "#0d1117"   # fondo principal
BG_CARD     = "#161b22"   # fondo de tarjetas
BG_INPUT    = "#21262d"   # fondo inputs
FG_TEXT     = "#e6edf3"   # texto principal
FG_MUTED    = "#8b949e"   # texto secundario
ACCENT_BLUE = "#58a6ff"   # azul GitHub
ACCENT_GRN  = "#3fb950"   # verde éxito
ACCENT_YLW  = "#d29922"   # amarillo advertencia
ACCENT_RED  = "#f85149"   # rojo error
BORDER      = "#30363d"   # bordes

# ─── Preguntas frecuentes de entrevista ─────────────────────────────────────
QUICK_QUESTIONS = [
    ("👤 Háblame de ti",           "Cuéntame de ti, tu background y experiencia"),
    ("💪 Mayor fortaleza",          "¿Cuál es tu mayor fortaleza profesional?"),
    ("📉 Mayor debilidad",          "¿Cuál es tu mayor debilidad y cómo la manejas?"),
    ("🏆 Logro más importante",     "¿Cuál es tu logro profesional más importante?"),
    ("⚔️ Manejo de conflictos",     "Cuéntame de una vez que manejaste un conflicto en el equipo"),
    ("📊 Gestión de proyectos",     "¿Cómo manejas múltiples proyectos simultáneamente?"),
    ("🔄 Cambio / adaptación",      "¿Puedes darme un ejemplo de adaptación a un cambio importante?"),
    ("💰 Expectativa salarial",     "¿Cuál es tu expectativa de compensación?"),
    ("🎯 Por qué este rol",         "¿Por qué quieres este puesto específico?"),
    ("🚀 Dónde te ves en 5 años",  "¿Dónde te ves en 5 años?"),
    ("❓ Preguntas al entrevistador","¿Tienes alguna pregunta para nosotros?"),
]


# ══════════════════════════════════════════════════════════════════════════════
#   CLASE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class InterviewCopilotOverlay:
    """
    Copilot invisible para entrevistas.
    La ventana NO aparece en captura de pantalla gracias a WDA_EXCLUDEFROMCAPTURE.
    """

    def __init__(self):
        self.cv_content = self._load_cv()
        self.lm_url = None
        self.job_context = None
        self.session_log = []
        self.is_thinking = False
        self.hidden = False

        # Crear ventana ANTES de aplicar el flag de invisibilidad
        self._build_ui()
        self._apply_capture_exclusion()
        self._detect_lm_studio()

    # ─── Carga del CV ────────────────────────────────────────────────────────
    def _load_cv(self) -> str:
        if CV_PATH.exists():
            text = CV_PATH.read_text(encoding="utf-8", errors="ignore")
            return text[:3000]  # Limitar contexto
        return ""

    # ─── Detección de LM Studio ──────────────────────────────────────────────
    def _detect_lm_studio(self):
        """Detecta qué IP tiene LM Studio corriendo (en background)."""
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
                self._status(f"✅ LM Studio: {host}", ACCENT_GRN)
                return
            except Exception:
                continue
        self._status("⚠️  LM Studio no encontrado — revisa que esté corriendo", ACCENT_YLW)

    # ─── Windows: excluir de captura de pantalla ─────────────────────────────
    def _apply_capture_exclusion(self):
        """
        Usa SetWindowDisplayAffinity con WDA_EXCLUDEFROMCAPTURE (0x11).
        La ventana es VISIBLE para el usuario pero INVISIBLE en:
          - Zoom (compartir pantalla)
          - Teams
          - Google Meet
          - OBS / Streamlabs
          - Windows Game Bar / Xbox Capture
        Requiere Windows 10 version 2004 (build 19041) o superior.
        """
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            if result:
                self._status("🔒 INVISIBLE en screen capture activo", ACCENT_GRN)
            else:
                # Retry con HWND directo
                hwnd2 = ctypes.windll.user32.FindWindowW(None, "AI Copilot")
                if hwnd2:
                    ctypes.windll.user32.SetWindowDisplayAffinity(hwnd2, WDA_EXCLUDEFROMCAPTURE)
        except Exception as e:
            self._status(f"⚠️  Capture exclusion no aplicada: {e}", ACCENT_YLW)

    # ─── Construcción de la UI ────────────────────────────────────────────────
    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("AI Copilot")
        self.root.configure(bg=BG_DARK)

        # Posición: esquina superior derecha (puede arrastrarse)
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"420x620+{screen_w - 440}+20")

        # Siempre encima + semi-transparente
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.92)

        # Sin barra de título estándar (más discreto)
        self.root.overrideredirect(True)

        # Permitir arrastrar la ventana
        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._do_drag)
        self._drag_x = 0
        self._drag_y = 0

        # Hotkeys globales (keyboard lib si está, sino tkinter)
        self._setup_hotkeys()

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG_CARD, pady=6, cursor="fleur")
        header.pack(fill="x")
        header.bind("<ButtonPress-1>", self._start_drag)
        header.bind("<B1-Motion>", self._do_drag)

        tk.Label(
            header, text="🎯 AI Interview Copilot",
            bg=BG_CARD, fg=FG_TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=10)

        # Botones de cabecera
        btn_frame = tk.Frame(header, bg=BG_CARD)
        btn_frame.pack(side="right", padx=6)

        self._btn(btn_frame, "─", self._minimize, BG_CARD, FG_MUTED, 2).pack(side="left")
        self._btn(btn_frame, "✕", self._quit, BG_CARD, ACCENT_RED, 2).pack(side="left")

        # ── Status bar ──────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="⏳ Iniciando...")
        self.status_lbl = tk.Label(
            self.root, textvariable=self.status_var,
            bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 8), anchor="w", padx=8
        )
        self.status_lbl.pack(fill="x")

        # ── Job context pill ────────────────────────────────────────────────
        self.job_lbl = tk.Label(
            self.root, text="📋 Sin job context — escribe el puesto abajo",
            bg=BG_DARK, fg=ACCENT_YLW,
            font=("Segoe UI", 8, "italic"), anchor="w", padx=8
        )
        self.job_lbl.pack(fill="x")

        # ── Respuesta del AI ─────────────────────────────────────────────────
        resp_frame = tk.Frame(self.root, bg=BG_CARD, padx=6, pady=6)
        resp_frame.pack(fill="both", expand=True, padx=6, pady=(4, 2))

        tk.Label(
            resp_frame, text="💡 Sugerencia",
            bg=BG_CARD, fg=ACCENT_BLUE,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x")

        self.response_text = scrolledtext.ScrolledText(
            resp_frame,
            bg=BG_CARD, fg=FG_TEXT,
            font=("Segoe UI", 9),
            wrap=tk.WORD,
            relief="flat",
            state="disabled",
            height=12,
            cursor="arrow",
            insertbackground=FG_TEXT
        )
        self.response_text.pack(fill="both", expand=True, pady=(4, 0))

        # ── Botones rápidos ──────────────────────────────────────────────────
        quick_frame = tk.LabelFrame(
            self.root, text=" ⚡ Preguntas frecuentes ",
            bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 8), bd=1, relief="flat",
            padx=4, pady=4
        )
        quick_frame.pack(fill="x", padx=6, pady=(2, 2))

        # Grid de botones 2 columnas
        for i, (label, question) in enumerate(QUICK_QUESTIONS):
            row, col = divmod(i, 2)
            btn = tk.Button(
                quick_frame,
                text=label,
                bg=BG_INPUT, fg=FG_TEXT,
                font=("Segoe UI", 7),
                relief="flat", bd=0,
                padx=4, pady=2,
                cursor="hand2",
                activebackground=BORDER, activeforeground=FG_TEXT,
                command=lambda q=question: self._ask(q)
            )
            btn.grid(row=row, column=col, sticky="ew", padx=2, pady=1)
        quick_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(1, weight=1)

        # ── Input de pregunta ────────────────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=BG_DARK, padx=6, pady=4)
        input_frame.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            bg=BG_INPUT, fg=FG_TEXT,
            font=("Segoe UI", 9),
            relief="flat", bd=4,
            insertbackground=FG_TEXT
        )
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<Return>", lambda e: self._ask_from_input())
        self.input_entry.bind("<Escape>", lambda e: self._clear())
        self.input_entry.insert(0, "Escribe la pregunta del entrevistador...")
        self.input_entry.config(fg=FG_MUTED)
        self.input_entry.bind("<FocusIn>", self._clear_placeholder)
        self.input_entry.bind("<FocusOut>", self._restore_placeholder)

        send_btn = tk.Button(
            input_frame,
            text="➤",
            bg=ACCENT_BLUE, fg=BG_DARK,
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0,
            padx=8, pady=0,
            cursor="hand2",
            activebackground=FG_TEXT,
            command=self._ask_from_input
        )
        send_btn.pack(side="left", padx=(4, 0))

        # ── Job context input ────────────────────────────────────────────────
        # FIX: pady tuple no es válido en Frame constructor — moverlo a pack()
        job_input_frame = tk.Frame(self.root, bg=BG_DARK, padx=6)
        job_input_frame.pack(fill="x", pady=(0, 6))

        self.job_input_var = tk.StringVar()
        job_entry = tk.Entry(
            job_input_frame,
            textvariable=self.job_input_var,
            bg=BG_INPUT, fg=FG_MUTED,
            font=("Segoe UI", 8),
            relief="flat", bd=4,
            insertbackground=FG_TEXT
        )
        job_entry.pack(side="left", fill="x", expand=True)
        job_entry.insert(0, "Empresa / Puesto (ej: TCS — Project Manager)")
        job_entry.bind("<FocusIn>", lambda e: (job_entry.delete(0, "end"), job_entry.config(fg=FG_TEXT)))
        job_entry.bind("<Return>", lambda e: self._set_job_context())

        tk.Button(
            job_input_frame,
            text="Set",
            bg=BORDER, fg=FG_TEXT,
            font=("Segoe UI", 8),
            relief="flat", bd=0,
            padx=6, pady=0,
            cursor="hand2",
            command=self._set_job_context
        ).pack(side="left", padx=(4, 0))

        # ── Hotkey hint ──────────────────────────────────────────────────────
        tk.Label(
            self.root,
            text="Ctrl+Shift+H = Ocultar/Mostrar  |  Invisible en Zoom/Teams/Meet",
            bg=BG_DARK, fg=BORDER,
            font=("Segoe UI", 7)
        ).pack(pady=(0, 4))

    # ─── Hotkeys ─────────────────────────────────────────────────────────────
    def _setup_hotkeys(self):
        """Configura hotkeys globales."""
        try:
            import keyboard
            keyboard.add_hotkey("ctrl+shift+h", self._toggle_visibility, suppress=False)
            keyboard.add_hotkey("ctrl+q", self._quit, suppress=False)
        except ImportError:
            # Fallback: solo hotkeys dentro de la ventana
            self.root.bind("<Control-h>", lambda e: self._toggle_visibility())
            self.root.bind("<Control-q>", lambda e: self._quit())

    def _toggle_visibility(self):
        """Alterna visibilidad — funciona incluso desde otra app."""
        if self.hidden:
            self.root.after(0, self.root.deiconify)
            self.root.after(0, lambda: self.root.wm_attributes("-topmost", True))
            self.hidden = False
        else:
            self.root.after(0, self.root.withdraw)
            self.hidden = True

    # ─── Drag ────────────────────────────────────────────────────────────────
    def _start_drag(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_drag(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    # ─── Helpers UI ──────────────────────────────────────────────────────────
    def _btn(self, parent, text, command, bg, fg, padx=6):
        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg,
            font=("Segoe UI", 9),
            relief="flat", bd=0,
            padx=padx, pady=2,
            cursor="hand2",
            activebackground=BORDER, activeforeground=FG_TEXT
        )

    def _status(self, msg: str, color: str = FG_MUTED):
        self.root.after(0, lambda: (
            self.status_var.set(msg),
            self.status_lbl.config(fg=color)
        ))

    def _set_response(self, text: str):
        self.response_text.config(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", text)
        self.response_text.config(state="disabled")

    def _append_response(self, chunk: str):
        self.response_text.config(state="normal")
        self.response_text.insert("end", chunk)
        self.response_text.see("end")
        self.response_text.config(state="disabled")

    def _clear(self):
        self._set_response("")
        self.input_var.set("")

    def _minimize(self):
        self.root.iconify()

    def _quit(self):
        self._save_session_log()
        self.root.destroy()

    def _clear_placeholder(self, event):
        if self.input_entry.get() == "Escribe la pregunta del entrevistador...":
            self.input_entry.delete(0, "end")
            self.input_entry.config(fg=FG_TEXT)

    def _restore_placeholder(self, event):
        if not self.input_entry.get():
            self.input_entry.insert(0, "Escribe la pregunta del entrevistador...")
            self.input_entry.config(fg=FG_MUTED)

    # ─── Job context ─────────────────────────────────────────────────────────
    def _set_job_context(self):
        value = self.job_input_var.get().strip()
        if value and value != "Empresa / Puesto (ej: TCS — Project Manager)":
            self.job_context = value
            self.job_lbl.config(
                text=f"📋 Job: {value[:60]}",
                fg=ACCENT_GRN
            )
            self._status(f"✅ Contexto: {value[:40]}", ACCENT_GRN)

    # ─── Lógica AI ───────────────────────────────────────────────────────────
    def _ask_from_input(self):
        question = self.input_var.get().strip()
        if not question or question == "Escribe la pregunta del entrevistador...":
            return
        self.input_var.set("")
        self.input_entry.config(fg=FG_TEXT)
        self._ask(question)

    def _ask(self, question: str):
        """Envía pregunta al AI y muestra respuesta en streaming."""
        if self.is_thinking:
            return
        if not self.lm_url:
            self._set_response("⚠️  LM Studio no disponible.\n\nAsegúrate de que LM Studio esté corriendo con el modelo cargado.")
            return

        self.is_thinking = True
        self._set_response("⏳ Pensando...")
        self._status("🤔 Consultando AI...", ACCENT_BLUE)

        # Log
        self.session_log.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": ""
        })

        threading.Thread(
            target=self._call_lm_studio,
            args=(question,),
            daemon=True
        ).start()

    def _build_system_prompt(self) -> str:
        prompt = """Eres un asistente experto para entrevistas de trabajo.
Tu rol es ayudar al candidato a responder preguntas de entrevista de forma clara y persuasiva.

INSTRUCCIONES CRÍTICAS:
- Respuesta CORTA y DIRECTA (máx 5-6 oraciones)
- Usa ejemplos concretos del CV del candidato cuando sea posible
- Formato: primero la idea central, luego el ejemplo/evidencia
- Enfoque en logros cuantificables (números, porcentajes, impacto)
- Lenguaje natural, no robótico
- Si es pregunta STAR (situación/comportamental), usa ese formato brevemente
- NO digas "Como PM..." o "Como candidato..." — responde EN VOZ del candidato
"""
        if self.cv_content:
            prompt += f"\n\nCV / PERFIL DEL CANDIDATO:\n{self.cv_content[:2500]}"

        if self.job_context:
            prompt += f"\n\nPUESTO AL QUE APLICA: {self.job_context}"

        return prompt

    def _call_lm_studio(self, question: str):
        """Llama a LM Studio API con streaming."""
        import urllib.request, urllib.error
        import json as _json

        system_prompt = self._build_system_prompt()
        payload = _json.dumps({
            "model": LM_STUDIO_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.5,
            "max_tokens": 350,
            "stream": True
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"{self.lm_url}/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                method="POST"
            )

            # Limpiar y empezar streaming
            self.root.after(0, lambda: self._set_response(""))
            full_response = ""

            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    line = line.decode("utf-8").strip()
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = _json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_response += content
                            chunk = content
                            self.root.after(0, lambda c=chunk: self._append_response(c))
                    except Exception:
                        continue

            # Actualizar log
            if self.session_log:
                self.session_log[-1]["response"] = full_response

            self.root.after(0, lambda: self._status("✅ Listo — Enter para nueva pregunta", ACCENT_GRN))

        except urllib.error.URLError as e:
            err = f"❌ Error de conexión con LM Studio:\n{e}\n\nVerifica que LM Studio esté corriendo."
            self.root.after(0, lambda: self._set_response(err))
            self.root.after(0, lambda: self._status("❌ Error LM Studio", ACCENT_RED))
            # Reintentar detección de IP
            self.lm_url = None
            threading.Thread(target=self._find_lm_studio, daemon=True).start()

        except Exception as e:
            err = f"❌ Error inesperado:\n{e}"
            self.root.after(0, lambda: self._set_response(err))
            self.root.after(0, lambda: self._status("❌ Error", ACCENT_RED))

        finally:
            self.is_thinking = False

    # ─── Guardar sesión ──────────────────────────────────────────────────────
    def _save_session_log(self):
        if not self.session_log:
            return
        try:
            LOG_PATH.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = LOG_PATH / f"session_{ts}.json"
            log_file.write_text(
                json.dumps(self.session_log, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    # ─── Run ─────────────────────────────────────────────────────────────────
    def run(self):
        """Inicia el overlay."""
        # Aplicar capture exclusion después de que la ventana sea visible
        self.root.after(500, self._reapply_capture_exclusion)
        self.root.mainloop()

    def _reapply_capture_exclusion(self):
        """
        Re-aplica WDA_EXCLUDEFROMCAPTURE después de que la ventana esté
        completamente inicializada. Este segundo intento es más confiable.
        """
        try:
            # Obtener HWND real de la ventana tkinter
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()

            # También buscar por título
            hwnd2 = ctypes.windll.user32.FindWindowW(None, "AI Copilot")
            target_hwnd = hwnd2 if hwnd2 else hwnd

            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            result = ctypes.windll.user32.SetWindowDisplayAffinity(target_hwnd, WDA_EXCLUDEFROMCAPTURE)

            if result:
                self._status("🔒 INVISIBLE en screen share ✓", ACCENT_GRN)
            else:
                error = ctypes.get_last_error()
                self._status(f"⚠️  Capture exclusion: error {error}", ACCENT_YLW)
        except Exception as e:
            self._status(f"⚠️  Windows API: {e}", ACCENT_YLW)


# ══════════════════════════════════════════════════════════════════════════════
#   ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("🎯 AI INTERVIEW COPILOT OVERLAY")
    print("=" * 60)
    print(f"📂 Proyecto: {PROJECT_ROOT}")
    print(f"📄 CV: {'✅ Cargado' if CV_PATH.exists() else '❌ No encontrado'}")
    print()
    print("⚡ HOTKEYS:")
    print("   Ctrl+Shift+H  → Mostrar / Ocultar")
    print("   Enter         → Enviar pregunta")
    print("   Escape        → Limpiar")
    print("   Ctrl+Q        → Cerrar")
    print()
    print("🔒 La ventana es INVISIBLE en Zoom/Teams/Meet/OBS")
    print("   (requiere Windows 10 build 19041+)")
    print()
    print("Iniciando overlay... (puedes minimizar esta terminal)")
    print("=" * 60)

    app = InterviewCopilotOverlay()
    app.run()


if __name__ == "__main__":
    main()
