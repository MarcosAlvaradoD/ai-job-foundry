"""
INTERVIEW COPILOT - Asistente invisible para entrevistas
Escucha preguntas y genera sugerencias en tiempo real basadas en tu CV
"""

import os
import json
import threading
from pathlib import Path
from datetime import datetime

class InterviewCopilot:
    def __init__(self, cv_path="cv_descriptor.txt", context_file=None):
        self.cv_path = Path(cv_path)
        self.context_file = Path(context_file) if context_file else None
        self.cv_content = self.load_cv()
        self.context = self.load_context()
        self.transcription_buffer = []
        self.is_listening = False
        
    def load_cv(self):
        """Carga tu CV/perfil profesional"""
        if self.cv_path.exists():
            return self.cv_path.read_text(encoding='utf-8')
        return "CV no encontrado. Por favor crea cv_descriptor.txt"
    
    def load_context(self):
        """Carga contexto específico de la entrevista"""
        if self.context_file and self.context_file.exists():
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def start_audio_capture(self):
        """
        Captura audio del sistema (micrófono + altavoz)
        Usa PyAudio o sounddevice
        """
        try:
            import sounddevice as sd
            import numpy as np
            
            print("🎙️ Iniciando captura de audio...")
            self.is_listening = True
            
            # Configuración
            sample_rate = 16000  # 16kHz es suficiente para voz
            channels = 1  # Mono
            
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"⚠️ Audio status: {status}")
                
                # Aquí procesarías el audio
                # Por ahora solo lo guardamos en buffer
                if self.is_listening:
                    audio_chunk = indata.copy()
                    # Enviar a transcripción
                    threading.Thread(
                        target=self.transcribe_chunk,
                        args=(audio_chunk,)
                    ).start()
            
            # Iniciar stream
            with sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                callback=audio_callback
            ):
                print("✅ Captura activa. Presiona Ctrl+C para detener.")
                while self.is_listening:
                    sd.sleep(1000)
        
        except ImportError:
            print("❌ sounddevice no instalado. Instala con: pip install sounddevice")
            print("Alternativa: Usa transcripción manual")
    
    def transcribe_chunk(self, audio_data):
        """
        Transcribe fragmento de audio a texto
        Opciones: Whisper local, Whisper API, Google Speech-to-Text
        """
        try:
            # Opción 1: Whisper local (requiere OpenAI Whisper)
            import whisper
            
            model = whisper.load_model("base")  # tiny, base, small, medium, large
            result = model.transcribe(audio_data)
            
            text = result["text"].strip()
            if text:
                self.process_transcription(text)
        
        except ImportError:
            # Opción 2: Whisper API (usa créditos)
            pass
    
    def process_transcription(self, text):
        """
        Procesa el texto transcrito
        Detecta si es pregunta o respuesta tuya
        """
        self.transcription_buffer.append({
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "is_question": self.is_likely_question(text)
        })
        
        # Si detectamos una pregunta, generar sugerencia
        if self.is_likely_question(text):
            print(f"\n❓ Pregunta detectada: {text}")
            suggestion = self.generate_suggestion(text)
            self.display_suggestion(suggestion)
    
    def is_likely_question(self, text):
        """
        Determina si el texto es una pregunta
        Usa heurísticas simples
        """
        question_indicators = [
            "?",
            "cuéntame",
            "explícame",
            "cómo",
            "qué",
            "por qué",
            "cuándo",
            "dónde",
            "tell me",
            "explain",
            "how",
            "what",
            "why",
            "when",
            "where"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in question_indicators)
    
    def generate_suggestion(self, question):
        """
        Genera sugerencia de respuesta basada en:
        - Tu CV
        - Contexto de la entrevista
        - La pregunta específica
        """
        # Aquí usarías LM Studio (local) o API
        prompt = f"""
Eres un asistente de entrevistas. El candidato está siendo entrevistado y necesita ayuda.

# Su CV/Perfil:
{self.cv_content}

# Contexto de la entrevista:
{self.context}

# Pregunta del entrevistador:
"{question}"

# Tu tarea:
Genera una respuesta sugerida de 2-3 frases que:
1. Sea honesta y basada en la experiencia real del CV
2. Incluya ejemplos concretos o métricas si es posible
3. Sea natural y conversacional
4. Si no tiene experiencia directa, sugiere cómo responder positivamente

FORMATO DE SALIDA:
SUGERENCIA: [tu respuesta sugerida]
PUNTOS CLAVE: [bullet points para recordar]
EJEMPLOS: [si aplica, ejemplos específicos del CV]
"""
        
        # Llamar a LM Studio o modelo local
        suggestion = self.call_ai_model(prompt)
        
        return suggestion
    
    def call_ai_model(self, prompt):
        """
        Llama a tu AI Router o directamente a LM Studio
        """
        try:
            import requests
            
            # LM Studio endpoint local
            url = "http://localhost:1234/v1/chat/completions"
            
            payload = {
                "model": "local-model",  # El modelo que tengas cargado
                "messages": [
                    {"role": "system", "content": "Eres un asistente de entrevistas experto."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            response = requests.post(url, json=payload)
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            return f"Error al generar sugerencia: {e}"
    
    def display_suggestion(self, suggestion):
        """
        Muestra la sugerencia en pantalla
        Opciones:
        - Ventana flotante (tkinter)
        - Overlay transparente
        - Segunda pantalla
        - Terminal siempre visible
        """
        print("\n" + "="*60)
        print("💡 SUGERENCIA DE RESPUESTA")
        print("="*60)
        print(suggestion)
        print("="*60 + "\n")
        
        # TODO: Implementar ventana flotante discreta
        # self.show_overlay_window(suggestion)
    
    def show_overlay_window(self, text):
        """
        Crea ventana flotante siempre visible
        Transparente, pequeña, en esquina de pantalla
        """
        import tkinter as tk
        
        # Crear ventana
        window = tk.Tk()
        window.title("Interview Copilot")
        
        # Configurar como siempre visible
        window.attributes('-topmost', True)
        window.attributes('-alpha', 0.9)  # Semi-transparente
        
        # Posicionar en esquina
        window.geometry("400x200+10+10")
        
        # Agregar texto
        label = tk.Label(window, text=text, wraplength=380, justify="left")
        label.pack(padx=10, pady=10)
        
        # Auto-cerrar después de 30 segundos
        window.after(30000, window.destroy)
        
        window.mainloop()
    
    def save_session_log(self, filename=None):
        """
        Guarda transcripción completa de la entrevista
        Útil para análisis posterior
        """
        if not filename:
            filename = f"interview_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "date": datetime.now().isoformat(),
                "cv_used": str(self.cv_path),
                "context": self.context,
                "transcription": self.transcription_buffer
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Log guardado: {filename}")


# MODO DE USO
if __name__ == "__main__":
    import sys
    
    print("""
    🎯 INTERVIEW COPILOT
    ====================
    
    Antes de tu entrevista:
    1. Asegúrate de tener cv_descriptor.txt actualizado
    2. Si tienes contexto específico de la vacante, pásalo como argumento
    3. Inicia este script ANTES de la videollamada
    4. Mantén esta ventana visible en segunda pantalla o minimizada
    
    Comandos:
    - python interview_copilot.py                    # Modo básico
    - python interview_copilot.py copilot_prompt_ejemplo_corp_senior_developer.md
    
    Presiona Ctrl+C para detener y guardar log.
    """)
    
    # Obtener archivo de contexto si se proporciona
    context_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Iniciar copilot
    copilot = InterviewCopilot(context_file=context_file)
    
    try:
        # Iniciar captura de audio
        copilot.start_audio_capture()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo copilot...")
        copilot.is_listening = False
        copilot.save_session_log()
        print("✅ Sesión guardada. ¡Buena suerte!")