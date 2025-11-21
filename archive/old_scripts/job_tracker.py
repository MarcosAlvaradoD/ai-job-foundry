"""
JOB TRACKER - Sistema de seguimiento de aplicaciones
Versión productiva con Gmail integrado
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Gmail API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class JobTracker:
    def __init__(self, data_file="data/applications/job_applications.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.applications = self.load_applications()
        self.gmail_service = None
        
        # Keywords para detectar correos de reclutadores
        self.recruiter_keywords = [
            "interview", "entrevista", "reunion", "meeting",
            "llamada", "call", "zoom", "teams", "meet",
            "siguiente paso", "next step", "disponibilidad",
            "availability", "horario", "schedule"
        ]
    
    def load_applications(self) -> Dict:
        """Carga aplicaciones existentes"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_applications(self):
        """Guarda estado actual"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.applications, f, indent=2, ensure_ascii=False)
        print(f"💾 Datos guardados: {self.data_file}")
    
    def connect_gmail(self):
        """Conecta con Gmail API"""
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.labels'
        ]
        
        creds_path = Path("data/credentials/credentials.json")
        token_path = Path("data/credentials/token.json")
        
        if not creds_path.exists():
            print("❌ No se encontró credentials.json")
            print("📋 Revisa GMAIL_SETUP.md para configurarlo")
            return False
        
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail conectado")
        return True
    
    def register_application(self, company: str, position: str, 
                           date_applied: str, contact_email: Optional[str] = None,
                           linkedin_url: Optional[str] = None, notes: Optional[str] = None):
        """Registra una nueva aplicación"""
        app_id = f"{company}_{position}".replace(" ", "_").lower()
        app_id = re.sub(r'[^a-z0-9_]', '', app_id)  # Limpiar caracteres especiales
        
        self.applications[app_id] = {
            "company": company,
            "position": position,
            "date_applied": date_applied,
            "contact_email": contact_email,
            "linkedin_url": linkedin_url,
            "notes": notes,
            "status": "applied",
            "communications": [],
            "interviews": [],
            "last_checked": None,
            "created_at": datetime.now().isoformat()
        }
        
        self.save_applications()
        print(f"✅ Aplicación registrada: {company} - {position} (ID: {app_id})")
        return app_id
    
    def check_gmail_for_responses(self, app_id: Optional[str] = None):
        """Revisa Gmail en busca de respuestas de reclutadores"""
        if not self.gmail_service:
            print("⚠️  Gmail no conectado. Ejecuta connect_gmail() primero")
            return
        
        print(f"\n🔍 Revisando correos...")
        
        # Si se especifica app_id, buscar solo ese
        if app_id and app_id in self.applications:
            apps_to_check = {app_id: self.applications[app_id]}
        else:
            # Buscar en todas las aplicaciones activas
            apps_to_check = {
                k: v for k, v in self.applications.items()
                if v["status"] not in ["rejected", "hired", "withdrawn"]
            }
        
        for app_id, app in apps_to_check.items():
            print(f"\n  📧 Revisando: {app['company']} - {app['position']}")
            
            # Construir query de búsqueda
            query_parts = [app['company']]
            if app['contact_email']:
                query_parts.append(f"from:{app['contact_email']}")
            
            # Buscar desde la fecha de aplicación
            try:
                date_applied = datetime.fromisoformat(app['date_applied'])
                after_date = date_applied.strftime('%Y/%m/%d')
                query_parts.append(f"after:{after_date}")
            except:
                pass
            
            query = " ".join(query_parts)
            
            try:
                results = self.gmail_service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=10
                ).execute()
                
                messages = results.get('messages', [])
                
                if not messages:
                    print(f"    ℹ️  Sin correos nuevos")
                    continue
                
                print(f"    📬 {len(messages)} correos encontrados")
                
                # Analizar cada correo
                for msg in messages:
                    message = self.gmail_service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    self.process_email(app_id, message)
            
            except HttpError as error:
                print(f"    ❌ Error: {error}")
            
            # Actualizar última revisión
            self.applications[app_id]['last_checked'] = datetime.now().isoformat()
        
        self.save_applications()
    
    def process_email(self, app_id: str, message: Dict):
        """Procesa un correo individual"""
        headers = {h['name']: h['value'] 
                  for h in message['payload']['headers']}
        
        from_email = headers.get('From', '')
        subject = headers.get('Subject', '')
        date = headers.get('Date', '')
        message_id = message['id']
        
        # Verificar si ya procesamos este correo
        existing_comms = self.applications[app_id]['communications']
        if any(c.get('message_id') == message_id for c in existing_comms):
            return  # Ya procesado
        
        # Extraer cuerpo del correo
        body = self.get_email_body(message)
        
        # Detectar si es relevante
        is_relevant = any(keyword.lower() in subject.lower() or 
                         keyword.lower() in body.lower()
                         for keyword in self.recruiter_keywords)
        
        if is_relevant:
            print(f"    ⭐ Correo relevante detectado:")
            print(f"       De: {from_email}")
            print(f"       Asunto: {subject}")
            
            # Guardar comunicación
            comm = {
                "message_id": message_id,
                "from": from_email,
                "subject": subject,
                "date": date,
                "body_preview": body[:200],
                "full_body": body,
                "detected_at": datetime.now().isoformat(),
                "type": "email"
            }
            
            self.applications[app_id]['communications'].append(comm)
            
            # Intentar extraer detalles de entrevista
            interview_info = self.extract_interview_details(body)
            if interview_info['date'] or interview_info['time']:
                print(f"    🎯 Entrevista detectada!")
                print(f"       Fecha: {interview_info.get('date', 'No especificada')}")
                print(f"       Hora: {interview_info.get('time', 'No especificada')}")
                
                self.applications[app_id]['interviews'].append({
                    **interview_info,
                    "detected_from_email": message_id,
                    "status": "pending"
                })
    
    def get_email_body(self, message: Dict) -> str:
        """Extrae el cuerpo del correo"""
        try:
            if 'data' in message['payload']['body']:
                import base64
                return base64.urlsafe_b64decode(
                    message['payload']['body']['data']
                ).decode('utf-8')
            
            # Si tiene partes
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        import base64
                        return base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
            
            return ""
        except:
            return ""
    
    def extract_interview_details(self, text: str) -> Dict:
        """Extrae fecha/hora de entrevista del texto"""
        info = {
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
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["platform"] = platform
                info["link"] = match.group(0)
                break
        
        # Buscar fechas (formatos comunes)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # 03/11/2025
            r'\d{4}-\d{2}-\d{2}',      # 2025-11-03
            r'\d{1,2}\s+de\s+\w+',     # 3 de noviembre
            r'\w+\s+\d{1,2}',          # November 3
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                info["date"] = match.group(0)
                break
        
        # Buscar horas
        time_pattern = r'\d{1,2}:\d{2}(?:\s*[AP]M)?'
        match = re.search(time_pattern, text, re.IGNORECASE)
        if match:
            info["time"] = match.group(0)
        
        return info
    
    def get_summary(self) -> Dict:
        """Genera resumen del estado actual"""
        total = len(self.applications)
        by_status = {}
        pending_interviews = []
        recent_comms = []
        
        for app_id, app in self.applications.items():
            status = app['status']
            by_status[status] = by_status.get(status, 0) + 1
            
            # Entrevistas pendientes
            for interview in app.get('interviews', []):
                if interview.get('status') == 'pending':
                    pending_interviews.append({
                        "company": app['company'],
                        "position": app['position'],
                        **interview
                    })
            
            # Comunicaciones recientes (últimos 7 días)
            for comm in app.get('communications', []):
                try:
                    detected = datetime.fromisoformat(comm['detected_at'])
                    if (datetime.now() - detected).days <= 7:
                        recent_comms.append({
                            "company": app['company'],
                            "position": app['position'],
                            **comm
                        })
                except:
                    pass
        
        return {
            "total_applications": total,
            "by_status": by_status,
            "pending_interviews": pending_interviews,
            "recent_communications": recent_comms,
            "last_updated": datetime.now().isoformat()
        }
    
    def print_summary(self):
        """Imprime resumen en consola"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("  📊 RESUMEN DE APLICACIONES")
        print("="*60 + "\n")
        
        print(f"Total de aplicaciones: {summary['total_applications']}")
        print("\nPor estado:")
        for status, count in summary['by_status'].items():
            print(f"  - {status}: {count}")
        
        if summary['pending_interviews']:
            print(f"\n🎯 Entrevistas pendientes: {len(summary['pending_interviews'])}")
            for iv in summary['pending_interviews']:
                print(f"\n  📅 {iv['company']} - {iv['position']}")
                print(f"     Fecha: {iv.get('date', 'Por confirmar')}")
                print(f"     Hora: {iv.get('time', 'Por confirmar')}")
                if iv.get('link'):
                    print(f"     Link: {iv['link']}")
        
        if summary['recent_communications']:
            print(f"\n📬 Comunicaciones recientes (7 días): {len(summary['recent_communications'])}")
            for comm in summary['recent_communications'][:5]:
                print(f"\n  ✉️  {comm['company']}")
                print(f"     Asunto: {comm['subject']}")
                print(f"     De: {comm['from']}")
        
        print("\n" + "="*60 + "\n")


# INTERFAZ DE COMANDOS
def main():
    import sys
    
    tracker = JobTracker()
    
    if len(sys.argv) < 2:
        print("""
🎯 JOB TRACKER - Sistema de Seguimiento

Comandos:
  register    - Registrar nueva aplicación
  check       - Revisar correos de Gmail
  summary     - Ver resumen de aplicaciones
  list        - Listar todas las aplicaciones
  
Ejemplos:
  python job_tracker.py register
  python job_tracker.py check
  python job_tracker.py summary
        """)
        return
    
    command = sys.argv[1]
    
    if command == "register":
        print("\n📝 REGISTRAR NUEVA APLICACIÓN\n")
        company = input("Empresa: ")
        position = input("Posición: ")
        date_applied = input("Fecha de aplicación (YYYY-MM-DD) [hoy]: ") or datetime.now().strftime('%Y-%m-%d')
        contact_email = input("Email del reclutador (opcional): ") or None
        linkedin_url = input("URL de LinkedIn (opcional): ") or None
        notes = input("Notas (opcional): ") or None
        
        tracker.register_application(
            company, position, date_applied,
            contact_email, linkedin_url, notes
        )
    
    elif command == "check":
        if not tracker.connect_gmail():
            return
        tracker.check_gmail_for_responses()
        tracker.print_summary()
    
    elif command == "summary":
        tracker.print_summary()
    
    elif command == "list":
        print("\n📋 TODAS LAS APLICACIONES:\n")
        for app_id, app in tracker.applications.items():
            print(f"{app_id}:")
            print(f"  {app['company']} - {app['position']}")
            print(f"  Estado: {app['status']}")
            print(f"  Aplicado: {app['date_applied']}\n")
    
    else:
        print(f"❌ Comando desconocido: {command}")


if __name__ == "__main__":
    main()