"""
INTERVIEW COPILOT - SESSION RECORDER
Graba sesiones completas de entrevistas con push-to-talk

CARACTERÍSTICAS:
✅ Push-to-talk: Mantén Ctrl+Shift+R presionado para grabar
✅ Grabación continua: Graba mientras mantienes la tecla
✅ Transcripción automática con Whisper
✅ Resumen final con AI (transcripción + hitos + puntos clave)
✅ Log completo en JSON

USO:
1. Inicia el copilot
2. Presiona y MANTÉN Ctrl+Shift+R
3. Habla mientras mantienes presionado
4. Suelta cuando termines de hablar
5. Al final escribe 'summary' para obtener resumen completo
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import threading
import time

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.utils.llm_client import LLMClient
    HAS_LLM_CLIENT = True
except ImportError:
    print("[WARNING] No se pudo importar LLMClient")
    HAS_LLM_CLIENT = False

# Audio imports
try:
    import whisper
    import pyaudio
    import numpy as np
    import wave
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    print("[ERROR] Whisper/PyAudio no disponibles")
    print("[INSTALL] pip install openai-whisper pyaudio numpy")

# Keyboard para hotkey
try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False
    print("[ERROR] keyboard no disponible")
    print("[INSTALL] pip install keyboard")


class InterviewSessionRecorder:
    """
    Grabadora de sesiones de entrevista con push-to-talk
    """
    
    def __init__(self, cv_path: str = "data/cv_descriptor.txt"):
        self.cv_path = Path(cv_path)
        self.cv_content = self._load_cv()
        self.llm = LLMClient() if HAS_LLM_CLIENT else None
        
        # Audio config
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        
        # Whisper
        self.whisper_model = None
        if HAS_AUDIO:
            print("[LOAD] Cargando Whisper (puede tardar)...")
            self.whisper_model = whisper.load_model("base")
            print("[OK] Whisper listo")
        
        # Session data
        self.session_transcript = []
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        
        # Logs
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        print("[OK] Session Recorder inicializado")
    
    def _load_cv(self) -> str:
        """Carga CV descriptor"""
        if self.cv_path.exists():
            with open(self.cv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[OK] CV cargado: {len(content)} caracteres")
                return content
        return ""
    
    def _record_audio_continuous(self):
        """
        Graba audio CONTINUAMENTE mientras is_recording=True
        """
        if not HAS_AUDIO:
            return
        
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print("🎤 GRABANDO... (suelta Ctrl+Shift+R para parar)")
        
        self.audio_data = []
        
        while self.is_recording:
            try:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
            except Exception as e:
                print(f"[ERROR] Error grabando: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        print("⏹️ Grabación detenida")
    
    def start_recording(self):
        """Inicia grabación en thread separado"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_audio_continuous)
        self.recording_thread.start()
    
    def stop_recording(self) -> str:
        """
        Detiene grabación y transcribe
        
        Returns:
            Texto transcrito
        """
        if not self.is_recording:
            return ""
        
        self.is_recording = False
        
        # Esperar a que termine el thread
        if self.recording_thread:
            self.recording_thread.join()
        
        # Transcribir
        if not self.audio_data:
            print("[WARNING] No hay audio grabado")
            return ""
        
        return self._transcribe_audio()
    
    def _transcribe_audio(self) -> str:
        """Transcribe audio grabado con Whisper"""
        if not HAS_AUDIO or not self.whisper_model:
            return ""
        
        try:
            print("[AI] Transcribiendo...")
            
            # Convertir bytes a numpy array
            audio_bytes = b''.join(self.audio_data)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Transcribir con Whisper
            result = self.whisper_model.transcribe(audio_np, language='en')
            
            text = result['text'].strip()
            print(f"[TRANSCRIBED] {text}")
            
            return text
            
        except Exception as e:
            print(f"[ERROR] Error transcribiendo: {e}")
            return ""
    
    def _analyze_with_ai(self, question: str) -> str:
        """
        Analiza pregunta y genera sugerencia de respuesta
        
        Args:
            question: Pregunta transcrita
        
        Returns:
            Sugerencia de respuesta
        """
        if not self.llm or not question:
            return ""
        
        prompt = f"""You are an interview coach helping a candidate respond to interview questions.

CANDIDATE PROFILE:
{self.cv_content}

INTERVIEW QUESTION:
{question}

Provide a concise, professional response suggestion (2-3 sentences max) and 3 key points.

Format:
SUGGESTION: [Your suggestion here]
KEY POINTS:
- [Point 1]
- [Point 2]
- [Point 3]
"""
        
        try:
            response = self.llm.complete(prompt)
            # Extract text content if it's an LLMResponse object
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            print(f"[ERROR] Error generando sugerencia: {e}")
            return ""
    
    def add_to_transcript(self, question: str, suggestion: str = ""):
        """Agrega interacción al transcript de la sesión"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'suggestion': suggestion,
            'type': 'audio_interaction'
        }
        self.session_transcript.append(entry)
    
    def generate_session_summary(self) -> dict:
        """
        Genera resumen completo de la sesión con AI
        
        Returns:
            Dict con transcripción, resumen y hitos
        """
        if not self.session_transcript:
            return {
                'error': 'No hay datos en la sesión',
                'transcript': [],
                'summary': '',
                'key_points': []
            }
        
        # Extraer todas las preguntas y respuestas
        full_transcript = []
        for entry in self.session_transcript:
            full_transcript.append(f"Q: {entry.get('question', 'N/A')}")
            if entry.get('suggestion'):
                full_transcript.append(f"A: {entry.get('suggestion', 'N/A')}")
        
        transcript_text = "\n\n".join(full_transcript)
        
        # Generar resumen con AI
        if self.llm:
            summary_prompt = f"""You are an interview coach. Analyze this interview session transcript and provide:

1. EXECUTIVE SUMMARY (2-3 sentences about the interview performance)
2. KEY HIGHLIGHTS (3-5 important moments/questions)
3. AREAS COVERED (main topics discussed)
4. RECOMMENDATIONS (2-3 suggestions for improvement)

TRANSCRIPT:
{transcript_text}

Format your response clearly with headers.
"""
            
            try:
                print("\n[AI] Generando resumen de la sesión...")
                ai_summary = self.llm.complete(summary_prompt)
                # Extract text content if it's an LLMResponse object
                if hasattr(ai_summary, 'content'):
                    ai_summary = ai_summary.content
                else:
                    ai_summary = str(ai_summary)
            except Exception as e:
                print(f"[ERROR] Error generando resumen: {e}")
                ai_summary = "Error generating AI summary"
        else:
            ai_summary = "AI summary not available (LLM not loaded)"
        
        return {
            'session_date': datetime.now().isoformat(),
            'total_interactions': len(self.session_transcript),
            'full_transcript': transcript_text,
            'ai_summary': ai_summary,
            'raw_data': self.session_transcript
        }
    
    def save_session_log(self):
        """Guarda log completo de la sesión"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"interview_session_{timestamp}.json"
        
        session_data = self.generate_session_summary()
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Sesión guardada: {log_file}")
        return log_file
    
    def run(self):
        """
        Loop principal del copilot con push-to-talk
        """
        if not HAS_AUDIO:
            print("[ERROR] Audio no disponible. Instala: pip install openai-whisper pyaudio")
            return
        
        if not HAS_KEYBOARD:
            print("[ERROR] keyboard no disponible. Instala: pip install keyboard")
            return
        
        print("\n" + "="*70)
        print("  💬 INTERVIEW SESSION RECORDER")
        print("="*70)
        
        print("\n[MODO] Push-to-Talk con Hotkey")
        print("\n🎤 PUSH-TO-TALK: Mantén presionado Ctrl+Shift+R para grabar")
        print("📝 TEXTO: Escribe preguntas manualmente")
        print("📊 RESUMEN: Escribe 'summary' para obtener resumen de la sesión")
        print("🚪 SALIR: Escribe 'exit'")
        
        # Setup hotkey con callbacks para press y release
        keyboard.on_press_key('r', self._on_hotkey_press, suppress=True)
        keyboard.on_release_key('r', self._on_hotkey_release, suppress=True)
        
        print("\n[OK] Hotkey configurado: Ctrl+Shift+R")
        print("[TIP] MANTÉN PRESIONADAS las teclas mientras hablas")
        
        # Main loop
        while True:
            try:
                # Si no está grabando, esperar input de texto
                if not self.is_recording:
                    user_input = input("\n❓ Pregunta (o mantén Ctrl+Shift+R): ").strip()
                    
                    if user_input.lower() in ['exit', 'salir', 'quit']:
                        print("\n[INFO] Saliendo...")
                        break
                    
                    if user_input.lower() == 'summary':
                        self._show_session_summary()
                        continue
                    
                    if user_input:
                        # Pregunta escrita manualmente
                        print(f"\n💡 Analizando pregunta...")
                        suggestion = self._analyze_with_ai(user_input)
                        
                        if suggestion:
                            print("\n" + "="*70)
                            print("  💡 SUGERENCIA DE RESPUESTA")
                            print("="*70)
                            print(f"\n{suggestion}")
                            print("\n" + "="*70)
                        
                        self.add_to_transcript(user_input, suggestion)
                
                else:
                    # Está grabando, esperar a que suelte la tecla
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\n\n[INFO] Interrumpido por usuario")
                break
            except Exception as e:
                print(f"\n[ERROR] Error en loop: {e}")
        
        # Al salir, guardar sesión
        print("\n[INFO] Guardando sesión...")
        self.save_session_log()
        print("\n✅ Sesión finalizada")
    
    def _on_hotkey_press(self, event):
        """Callback cuando presiona Ctrl+Shift+R"""
        # Verificar que Ctrl y Shift estén presionados
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift'):
            if not self.is_recording:
                self.start_recording()
    
    def _on_hotkey_release(self, event):
        """Callback cuando suelta R (termina grabación)"""
        if self.is_recording:
            # Detener grabación y transcribir
            transcribed_text = self.stop_recording()
            
            if transcribed_text:
                print(f"\n💡 Analizando pregunta...")
                suggestion = self._analyze_with_ai(transcribed_text)
                
                if suggestion:
                    print("\n" + "="*70)
                    print("  💡 SUGERENCIA DE RESPUESTA")
                    print("="*70)
                    print(f"\n{suggestion}")
                    print("\n" + "="*70)
                
                self.add_to_transcript(transcribed_text, suggestion)
                print("\n" + "-"*70)
    
    def _show_session_summary(self):
        """Muestra resumen de la sesión actual"""
        print("\n" + "="*70)
        print("  📊 RESUMEN DE LA SESIÓN")
        print("="*70)
        
        summary = self.generate_session_summary()
        
        print(f"\n[INFO] Total de interacciones: {summary.get('total_interactions', 0)}")
        print("\n" + "="*70)
        print("  📝 TRANSCRIPCIÓN COMPLETA")
        print("="*70)
        print(f"\n{summary.get('full_transcript', 'N/A')}")
        
        print("\n" + "="*70)
        print("  🎯 RESUMEN CON AI")
        print("="*70)
        print(f"\n{summary.get('ai_summary', 'N/A')}")
        
        print("\n" + "="*70)


def main():
    """Main entry point"""
    print("\n")
    print("    ╔══════════════════════════════════════════════════════════════╗")
    print("    ║     INTERVIEW COPILOT - SESSION RECORDER (Push-to-Talk)    ║")
    print("    ╚══════════════════════════════════════════════════════════════╝")
    
    print("\n    🎤 PUSH-TO-TALK: Mantén Ctrl+Shift+R para grabar")
    print("    📝 TEXTO: Escribe preguntas manualmente")
    print("    📊 RESUMEN: Escribe 'summary' para resumen completo")
    print("    🚪 SALIR: Escribe 'exit'")
    
    print("\n    📋 REQUISITOS:")
    print("    1. LM Studio corriendo")
    print("    2. CV en data/cv_descriptor.txt")
    print("    3. Whisper instalado: pip install openai-whisper")
    print("    4. PyAudio instalado: pip install pyaudio")
    print("    5. Keyboard instalado: pip install keyboard")
    print("\n    ⌨️ NOTA: Debes ejecutar como administrador para usar hotkeys")
    print()
    
    try:
        recorder = InterviewSessionRecorder()
        recorder.run()
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
