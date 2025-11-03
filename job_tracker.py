"""
JOB TRACKER - Sistema de seguimiento de comunicaciones
Monitorea Gmail, LinkedIn y genera recordatorios automáticos
"""

import os
import json
from datetime import datetime, timedelta
import re
from pathlib import Path

# Configuración
CONFIG = {
    "gmail_keywords": ["interview", "entrevista", "reunión", "meeting", "zoom", "teams", "google meet"],
    "linkedin_keywords": ["interested", "interesado", "next steps", "siguientes pasos"],
    "check_interval_minutes": 30,
    "reminder_advance_hours": 2,  # Recordatorio 2 horas antes
    "data_file": "job_applications.json"
}

class JobTracker:
    def __init__(self):
        self.data_file = Path(CONFIG["data_file"])
        self.applications = self.load_applications()
    
    def load_applications(self):
        """Carga aplicaciones existentes"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_applications(self):
        """Guarda estado actual"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.applications, f, indent=2, ensure_ascii=False)
    
    def register_application(self, company, position, date_applied, contact_email=None, linkedin_url=None):
        """Registra una nueva aplicación"""
        app_id = f"{company}_{position}".replace(" ", "_").lower()
        
        self.applications[app_id] = {
            "company": company,
            "position": position,
            "date_applied": date_applied,
            "contact_email": contact_email,
            "linkedin_url": linkedin_url,
            "status": "applied",
            "communications": [],
            "interviews": [],
            "last_checked": None
        }
        
        self.save_applications()
        print(f"✅ Aplicación registrada: {company} - {position}")
        return app_id
    
    def check_gmail(self, app_id):
        """
        Revisa Gmail en busca de respuestas del reclutador
        TODO: Implementar con Gmail API
        """
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # Este es el esqueleto - necesitas credentials.json
        # Por ahora retorna estructura esperada
        
        new_messages = []
        # Aquí iría la lógica de Gmail API
        # service = build('gmail', 'v1', credentials=creds)
        # results = service.users().messages().list(userId='me', q=f'from:{email}').execute()
        
        return new_messages
    
    def extract_interview_details(self, message_body):
        """
        Extrae fecha/hora de entrevista del texto del mensaje
        Usa regex y NLP básico
        """
        interview_info = {
            "date": None,
            "time": None,
            "platform": None,
            "link": None
        }
        
        # Buscar plataformas
        platforms = {
            "zoom": r'zoom\.us/j/[\d]+',
            "teams": r'teams\.microsoft\.com',
            "meet": r'meet\.google\.com/[\w-]+'
        }
        
        for platform, pattern in platforms.items():
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                interview_info["platform"] = platform
                interview_info["link"] = match.group(0)
                break
        
        # Buscar fechas (formato: "15 de noviembre", "November 15", "2025-11-15")
        date_patterns = [
            r'\d{1,2}\s+de\s+\w+',  # 15 de noviembre
            r'\w+\s+\d{1,2}',       # November 15
            r'\d{4}-\d{2}-\d{2}'    # 2025-11-15
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message_body)
            if match:
                interview_info["date"] = match.group(0)
                break
        
        # Buscar horas (formato: "14:00", "2:00 PM", "14h00")
        time_pattern = r'\d{1,2}:\d{2}(?:\s*[AP]M)?|\d{1,2}h\d{2}'
        match = re.search(time_pattern, message_body, re.IGNORECASE)
        if match:
            interview_info["time"] = match.group(0)
        
        return interview_info
    
    def create_reminder(self, app_id, interview_date, interview_time):
        """
        Crea recordatorio para entrevista
        Opciones: WhatsApp, Telegram, notificación Windows
        """
        from datetime import datetime
        
        # Parsear fecha/hora
        # TODO: Mejorar parsing con dateutil o similar
        reminder_text = f"""
        🎯 ENTREVISTA PRÓXIMA
        
        Empresa: {self.applications[app_id]['company']}
        Posición: {self.applications[app_id]['position']}
        Fecha: {interview_date}
        Hora: {interview_time}
        
        Preparación sugerida:
        - Revisar descripción del puesto
        - Preparar preguntas para el entrevistador
        - Probar audio/video
        - Activar Interview Copilot
        """
        
        # Guardar recordatorio
        self.applications[app_id]["interviews"].append({
            "date": interview_date,
            "time": interview_time,
            "reminder_created": datetime.now().isoformat(),
            "status": "pending"
        })
        
        self.save_applications()
        
        # TODO: Enviar a WhatsApp/Telegram
        print(reminder_text)
        return reminder_text
    
    def generate_copilot_prompt(self, app_id):
        """
        Genera el prompt para Interview Copilot
        Incluye: CV, descripción del puesto, contexto
        """
        app = self.applications[app_id]
        
        # Leer CV
        cv_path = Path("cv_descriptor.txt")
        cv_content = cv_path.read_text(encoding='utf-8') if cv_path.exists() else "CV no encontrado"
        
        prompt = f"""
# CONTEXTO DE ENTREVISTA - INTERVIEW COPILOT

## Información de la Vacante
- **Empresa:** {app['company']}
- **Posición:** {app['position']}
- **Fecha de aplicación:** {app['date_applied']}

## Tu Perfil (CV)
{cv_content}

## Instrucciones para el Asistente
- Escucha las preguntas del entrevistador
- Genera respuestas sugeridas basadas en mi experiencia real
- Prioriza ejemplos concretos y métricas
- Mantén tono profesional pero cercano
- Si no tengo experiencia en algo, sugiere cómo responder honestamente

## Comunicaciones Previas
{json.dumps(app.get('communications', []), indent=2)}

---
**Modo:** Escucha activa. Genera sugerencias en tiempo real.
        """
        
        # Guardar prompt para uso del copilot
        prompt_file = Path(f"copilot_prompt_{app_id}.md")
        prompt_file.write_text(prompt, encoding='utf-8')
        
        print(f"✅ Prompt generado: {prompt_file}")
        return prompt
    
    def monitor_loop(self):
        """
        Loop principal de monitoreo
        Ejecutar cada X minutos
        """
        import time
        
        print(f"🔄 Iniciando monitoreo cada {CONFIG['check_interval_minutes']} minutos...")
        
        while True:
            for app_id, app in self.applications.items():
                if app["status"] not in ["rejected", "hired"]:
                    print(f"Revisando: {app['company']} - {app['position']}")
                    
                    # Revisar Gmail
                    new_messages = self.check_gmail(app_id)
                    
                    for msg in new_messages:
                        # Extraer info de entrevista
                        interview = self.extract_interview_details(msg["body"])
                        
                        if interview["date"] and interview["time"]:
                            print(f"🎯 Entrevista detectada!")
                            self.create_reminder(app_id, interview["date"], interview["time"])
                            self.generate_copilot_prompt(app_id)
                    
                    app["last_checked"] = datetime.now().isoformat()
            
            self.save_applications()
            time.sleep(CONFIG['check_interval_minutes'] * 60)


# EJEMPLO DE USO
if __name__ == "__main__":
    tracker = JobTracker()
    
    # Registrar una aplicación que acabas de hacer
    tracker.register_application(
        company="Ejemplo Corp",
        position="Senior Developer",
        date_applied="2025-11-03",
        contact_email="recruiter@ejemplo.com"
    )
    
    # Iniciar monitoreo (comentado para pruebas)
    # tracker.monitor_loop()
    
    print("\n✅ Sistema listo. Para producción:")
    print("1. Configura Gmail API (credentials.json)")
    print("2. Ejecuta: python job_tracker.py")
    print("3. Opcional: Configura como servicio de Windows")