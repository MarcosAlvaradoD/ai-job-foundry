"""
INTERVIEW COPILOT - Versión con Escucha Automática
Presiona Page Down para capturar audio y traducir/responder
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import keyboard  # Para hotkeys globales
import pyaudio
import wave
import tempfile

class InterviewCopilot:
    def __init__(self):
        self.cv_path = Path("data/cv_descriptor.txt")
        self.cv_content = self.load_cv()
        self.llm_endpoint = "http://172.23.0.1:11434/v1/chat/completions"
        self.current_model = "qwen2.5-14b-instruct"
        
        # Audio settings
        self.is_recording = False
        self.audio_frames = []
        self.audio = pyaudio.PyAudio()
        
        # Context de la vacante actual
        self.job_context = {
            "company": "Zemsania",
            "position": "BI & Power Platform Consultant",
            "key_skills": ["Power Apps", "Power BI", "Azure", "SharePoint", "Project Leadership"]
        }
        
        # UI
        self.window = None
        self.question_input = None
        self.answer_output = None
        self.status_label = None
        
    def load_cv(self):
        """Carga tu CV"""
        if self.cv_path.exists():
            with open(self.cv_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "CV no encontrado"
    
    def start_recording(self):
        """Inicia grabación de audio"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.audio_frames = []
        
        self.status_label.config(text="🔴 GRABANDO... (Page Down para detener)", fg="#ff0000")
        
        def record_thread():
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            while self.is_recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_frames.append(data)
                except:
                    break
            
            stream.stop_stream()
            stream.close()
        
        threading.Thread(target=record_thread, daemon=True).start()
    
    def stop_recording_and_process(self):
        """Detiene grabación y procesa"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        time.sleep(0.5)  # Esperar a que termine
        
        self.status_label.config(text="⏳ Procesando audio...", fg="#ffaa00")
        
        # Guardar audio temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()
        
        # Transcribir con Whisper
        threading.Thread(
            target=self.transcribe_and_answer,
            args=(temp_file.name,),
            daemon=True
        ).start()
    
    def transcribe_and_answer(self, audio_file):
        """Transcribe audio y genera respuesta"""
        try:
            # Transcribir con Whisper local
            transcription = self.transcribe_audio(audio_file)
            
            if not transcription:
                self.status_label.config(text="❌ No se pudo transcribir", fg="#ff0000")
                return
            
            # Mostrar pregunta detectada
            self.question_input.delete("1.0", tk.END)
            self.question_input.insert(tk.END, f"[EN] {transcription}")
            
            # Traducir y responder
            self.status_label.config(text="🤖 Generando respuesta...", fg="#00aaff")
            
            answer = self.generate_bilingual_answer(transcription)
            
            # Mostrar respuesta
            self.answer_output.delete("1.0", tk.END)
            self.answer_output.insert(tk.END, answer)
            
            self.status_label.config(text="✅ Listo (Page Down para próxima pregunta)", fg="#00ff00")
            
            # Log
            self.log_interaction(transcription, answer)
        
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {e}", fg="#ff0000")
        
        finally:
            # Limpiar archivo temporal
            try:
                Path(audio_file).unlink()
            except:
                pass
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio usando Whisper local"""
        try:
            # Opción 1: Whisper local (si lo tienes instalado)
            import whisper
            
            model = whisper.load_model("base")
            result = model.transcribe(audio_file, language="en")
            
            return result["text"].strip()
        
        except ImportError:
            # Opción 2: API de Whisper (requiere OpenAI key)
            # O retornar None para indicar que no está disponible
            return None
    
    def generate_bilingual_answer(self, english_question):
        """Genera respuesta bilingüe (traducción + sugerencia)"""
        
        prompt = f"""Eres un asistente de entrevistas bilingüe (EN/ES).

Contexto de la entrevista:
- Empresa: {self.job_context['company']}
- Posición: {self.job_context['position']}
- Skills clave: {', '.join(self.job_context['key_skills'])}

Perfil del candidato (CV resumido):
{self.cv_content[:1500]}

PREGUNTA DEL ENTREVISTADOR (en inglés):
"{english_question}"

Tu tarea:
1. TRADUCIR la pregunta al español
2. GENERAR una respuesta sugerida EN ESPAÑOL basada en el CV
3. La respuesta debe ser CORTA (2-3 frases)
4. Incluir un ejemplo concreto si es posible

FORMATO DE SALIDA:
📝 PREGUNTA (ES):
[traducción al español de la pregunta]

💡 RESPUESTA SUGERIDA:
[tu respuesta en español, 2-3 frases]

🎯 PUNTOS CLAVE:
- [punto 1]
- [punto 2]
- [punto 3]

💬 TIP DE COMUNICACIÓN:
[consejo rápido para responder mejor]
"""
        
        try:
            response = requests.post(
                self.llm_endpoint,
                json={
                    "model": self.current_model,
                    "messages": [
                        {"role": "system", "content": "Eres un experto asistente de entrevistas bilingüe."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code}"
        
        except Exception as e:
            return f"""Error conectando con IA: {e}

📝 PREGUNTA (ES):
[Error en traducción automática]

💡 RESPUESTA DE RESPALDO:
- Menciona tu experiencia en {self.job_context['key_skills'][0]}
- Usa el método STAR
- Da un ejemplo concreto de tu CV
"""
    
    def generate_answer(self, question):
        """Genera respuesta (versión manual/texto)"""
        
        prompt = f"""Eres un asistente de entrevistas. El candidato está en una entrevista para:
- Empresa: {self.job_context['company']}
- Posición: {self.job_context['position']}

Perfil del candidato:
{self.cv_content[:2000]}

Pregunta:
"{question}"

Genera una respuesta CORTA (2-3 frases) basada en experiencia REAL del CV.

FORMATO:
RESPUESTA: [tu respuesta]
PUNTOS CLAVE: [bullets]
"""
        
        try:
            response = requests.post(
                self.llm_endpoint,
                json={
                    "model": self.current_model,
                    "messages": [
                        {"role": "system", "content": "Eres un asistente experto en preparación de entrevistas."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code}"
        
        except Exception as e:
            return f"Error: {e}"
    
    def create_ui(self):
        """Crea ventana overlay"""
        self.window = tk.Tk()
        self.window.title("Interview Copilot 🎯")
        
        # Configuración de ventana
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.95)
        self.window.geometry("500x700+10+50")
        self.window.configure(bg='#1e1e1e')
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#1e1e1e', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Label(
            main_frame,
            text=f"🎯 {self.job_context['company']} - {self.job_context['position'][:30]}...",
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Arial', 10, 'bold')
        )
        header.pack(pady=(0, 10))
        
        # Status con instrucciones
        self.status_label = tk.Label(
            main_frame,
            text="🎙️ Presiona PAGE DOWN para grabar pregunta",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Arial', 9, 'bold')
        )
        self.status_label.pack(pady=(0, 10))
        
        # Label pregunta
        tk.Label(
            main_frame,
            text="Pregunta del entrevistador:",
            bg='#1e1e1e',
            fg='#aaaaaa',
            font=('Arial', 9)
        ).pack(anchor='w')
        
        # Input pregunta
        self.question_input = scrolledtext.ScrolledText(
            main_frame,
            height=3,
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.question_input.pack(fill=tk.X, pady=(5, 10))
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='#1e1e1e')
        btn_frame.pack(pady=(0, 10))
        
        btn_record = tk.Button(
            btn_frame,
            text="🎙️ Grabar",
            command=self.start_recording,
            bg='#cc0000',
            fg='#ffffff',
            font=('Arial', 9, 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_record.pack(side=tk.LEFT, padx=5)
        
        btn_stop = tk.Button(
            btn_frame,
            text="⏹️ Detener",
            command=self.stop_recording_and_process,
            bg='#666666',
            fg='#ffffff',
            font=('Arial', 9, 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_stop.pack(side=tk.LEFT, padx=5)
        
        btn_generate = tk.Button(
            btn_frame,
            text="🤖 Generar (texto)",
            command=self.on_generate,
            bg='#0066cc',
            fg='#ffffff',
            font=('Arial', 9, 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_generate.pack(side=tk.LEFT, padx=5)
        
        # Label respuesta
        tk.Label(
            main_frame,
            text="💡 Sugerencia:",
            bg='#1e1e1e',
            fg='#aaaaaa',
            font=('Arial', 9)
        ).pack(anchor='w')
        
        # Output respuesta
        self.answer_output = scrolledtext.ScrolledText(
            main_frame,
            height=18,
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.answer_output.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Instrucciones
        instructions = tk.Label(
            main_frame,
            text="⚠️ INVISIBLE para videollamada | ESC=minimizar | Ctrl+C=copiar",
            bg='#1e1e1e',
            fg='#666666',
            font=('Arial', 8)
        )
        instructions.pack()
        
        # Hotkeys
        self.window.bind('<Escape>', lambda e: self.window.iconify())
        
        # Registrar hotkey global (Page Down)
        keyboard.on_press_key('page down', self.on_page_down_press)
        keyboard.on_release_key('page down', self.on_page_down_release)
    
    def on_page_down_press(self, event):
        """Handler cuando se presiona Page Down"""
        if not self.is_recording:
            self.start_recording()
    
    def on_page_down_release(self, event):
        """Handler cuando se suelta Page Down"""
        if self.is_recording:
            self.stop_recording_and_process()
    
    def on_generate(self):
        """Handler del botón generar (modo manual)"""
        question = self.question_input.get("1.0", tk.END).strip()
        
        if not question:
            self.answer_output.delete("1.0", tk.END)
            self.answer_output.insert(tk.END, "⚠️ Escribe la pregunta primero")
            return
        
        self.answer_output.delete("1.0", tk.END)
        self.answer_output.insert(tk.END, "🔄 Generando...\n\n")
        self.window.update()
        
        def generate_thread():
            answer = self.generate_answer(question)
            self.answer_output.delete("1.0", tk.END)
            self.answer_output.insert(tk.END, answer)
            self.log_interaction(question, answer)
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def log_interaction(self, question, answer):
        """Guarda log de la entrevista"""
        log_dir = Path("data/interviews")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"interview_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Empresa: {self.job_context['company']}\n")
            f.write(f"\nPREGUNTA:\n{question}\n")
            f.write(f"\nRESPUESTA:\n{answer}\n")
    
    def run(self):
        """Inicia la aplicación"""
        print("\n" + "="*60)
        print("  🎯 INTERVIEW COPILOT - Con Escucha Automática")
        print("="*60)
        print(f"\n  Empresa: {self.job_context['company']}")
        print(f"  Posición: {self.job_context['position']}")
        print(f"\n  💡 USO:")
        print(f"  1. Mantén esta ventana VISIBLE (segunda pantalla o esquina)")
        print(f"  2. Durante entrevista:")
        print(f"     - Presiona y MANTÉN PAGE DOWN mientras habla el entrevistador")
        print(f"     - Suelta PAGE DOWN cuando termine")
        print(f"     - El sistema transcribe, traduce y genera respuesta")
        print(f"  3. Lee la respuesta NATURALMENTE")
        print(f"\n  🎙️ IMPORTANTE:")
        print(f"  - Usa audífonos para evitar que capture tu voz")
        print(f"  - La ventana es LOCAL (no se ve en Zoom/Teams)")
        print(f"  - Presiona ESC para minimizar")
        print("\n" + "="*60 + "\n")
        
        self.create_ui()
        self.window.mainloop()

if __name__ == "__main__":
    import sys
    
    print("""
    🎯 INTERVIEW COPILOT - Setup
    =============================
    
    Dependencias necesarias:
    pip install keyboard pyaudio whisper
    
    (whisper es opcional, usa Whisper local para transcripción)
    
    Presiona Enter para continuar...
    """)
    
    input()
    
    # Verificar IA
    print("🔍 Verificando IA...")
    try:
        response = requests.get("http://172.23.0.1:11434/v1/models", timeout=5)
        if response.status_code == 200:
            print("✅ IA disponible")
        else:
            print("⚠️ IA con problemas")
    except:
        print("❌ No se puede conectar con IA")
        print("   Verifica que esté corriendo")
        sys.exit(1)
    
    copilot = InterviewCopilot()
    
    # Personalizar
    print("\n📝 Personalización:")
    company = input("Empresa (Enter = Zemsania): ").strip() or "Zemsania"
    position = input("Posición (Enter = BI Consultant): ").strip() or "BI & Power Platform Consultant"
    
    copilot.job_context['company'] = company
    copilot.job_context['position'] = position
    
    print(f"\n✅ Configurado para: {company} - {position}")
    print("🚀 Iniciando...\n")
    
    time.sleep(2)
    copilot.run()