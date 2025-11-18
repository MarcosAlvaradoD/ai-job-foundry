"""
SYNC WITH SHEETS - Sincronizar Job Tracker con Google Sheets
Permite editar aplicaciones desde Sheets y sincronizar cambios
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsSync:
    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self.applications_file = Path("data/applications/job_applications.json")
        self.config_file = Path("data/sheets_config.json")
        
        # Scopes necesarios
        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
    
    def connect_sheets(self):
        """Conecta con Google Sheets API"""
        creds_path = Path("data/credentials/credentials.json")
        token_path = Path("data/credentials/token_sheets.json")
        
        if not creds_path.exists():
            print("❌ No se encontró credentials.json")
            print("📋 Usa las mismas credenciales de Gmail")
            return False
        
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
        print("✅ Google Sheets conectado")
        return True
    
    def create_spreadsheet(self, title="Job Applications Tracker"):
        """Crea una nueva hoja de cálculo"""
        if not self.service:
            print("❌ Primero conecta con connect_sheets()")
            return None
        
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Applications',
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Interviews',
                        }
                    },
                    {
                        'properties': {
                            'title': 'Communications',
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl'
            ).execute()
            
            self.spreadsheet_id = spreadsheet.get('spreadsheetId')
            url = spreadsheet.get('spreadsheetUrl')
            
            # Guardar ID
            self.save_config()
            
            print(f"✅ Hoja creada: {url}")
            print(f"📋 ID: {self.spreadsheet_id}")
            
            # Configurar encabezados
            self.setup_headers()
            
            return self.spreadsheet_id
        
        except HttpError as error:
            print(f"❌ Error: {error}")
            return None
    
    def setup_headers(self):
        """Configura los encabezados de las hojas"""
        # Encabezados de Applications
        headers_applications = [
            'ID', 'Company', 'Position', 'Date Applied', 
            'Status', 'Contact Email', 'LinkedIn URL', 
            'Notes', 'Last Checked', 'Interviews Count', 
            'Communications Count'
        ]
        
        # Encabezados de Interviews
        headers_interviews = [
            'Application ID', 'Company', 'Position',
            'Date', 'Time', 'Platform', 'Link', 'Status'
        ]
        
        # Encabezados de Communications
        headers_communications = [
            'Application ID', 'Company', 'From', 
            'Subject', 'Date', 'Type', 'Preview'
        ]
        
        try:
            # Escribir encabezados
            requests = [
                {
                    'updateCells': {
                        'range': {
                            'sheetId': 0,  # Applications
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'rows': [{
                            'values': [
                                {'userEnteredValue': {'stringValue': h},
                                 'userEnteredFormat': {'textFormat': {'bold': True}}}
                                for h in headers_applications
                            ]
                        }],
                        'fields': 'userEnteredValue,userEnteredFormat.textFormat.bold'
                    }
                },
                {
                    'updateCells': {
                        'range': {
                            'sheetId': 1,  # Interviews
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'rows': [{
                            'values': [
                                {'userEnteredValue': {'stringValue': h},
                                 'userEnteredFormat': {'textFormat': {'bold': True}}}
                                for h in headers_interviews
                            ]
                        }],
                        'fields': 'userEnteredValue,userEnteredFormat.textFormat.bold'
                    }
                },
                {
                    'updateCells': {
                        'range': {
                            'sheetId': 2,  # Communications
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'rows': [{
                            'values': [
                                {'userEnteredValue': {'stringValue': h},
                                 'userEnteredFormat': {'textFormat': {'bold': True}}}
                                for h in headers_communications
                            ]
                        }],
                        'fields': 'userEnteredValue,userEnteredFormat.textFormat.bold'
                    }
                }
            ]
            
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            print("✅ Encabezados configurados")
        
        except HttpError as error:
            print(f"❌ Error configurando encabezados: {error}")
    
    def ensure_sheets_exist(self):
        """Verifica que las hojas existan, si no las crea"""
        try:
            # Obtener hojas existentes
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            existing_sheets = {sheet['properties']['title']: sheet['properties']['sheetId'] 
                             for sheet in spreadsheet['sheets']}
            
            # Hojas requeridas
            required_sheets = ['Applications', 'Interviews', 'Communications']
            
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    print(f"  ℹ️  Creando hoja: {sheet_name}")
                    request = {
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    }
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body={'requests': [request]}
                    ).execute()
            
            return True
        except HttpError as error:
            print(f"❌ Error verificando hojas: {error}")
            return False
    
    def push_to_sheets(self):
        """Envía datos del JSON a Google Sheets"""
        if not self.spreadsheet_id:
            print("❌ No hay spreadsheet configurado")
            return False
        
        # Verificar que las hojas existan
        if not self.ensure_sheets_exist():
            return False
        
        # Configurar encabezados si es necesario
        self.setup_headers()
        
        # Cargar aplicaciones
        if not self.applications_file.exists():
            print("❌ No hay aplicaciones registradas")
            return False
        
        with open(self.applications_file, 'r', encoding='utf-8') as f:
            applications = json.load(f)
        
        # Preparar datos
        rows_applications = []
        rows_interviews = []
        rows_communications = []
        
        for app_id, app in applications.items():
            # Fila de Applications
            row_app = [
                app_id,
                app.get('company', ''),
                app.get('position', ''),
                app.get('date_applied', ''),
                app.get('status', 'applied'),
                app.get('contact_email', ''),
                app.get('linkedin_url', ''),
                app.get('notes', ''),
                app.get('last_checked', ''),
                len(app.get('interviews', [])),
                len(app.get('communications', []))
            ]
            rows_applications.append(row_app)
            
            # Filas de Interviews
            for interview in app.get('interviews', []):
                row_iv = [
                    app_id,
                    app['company'],
                    app['position'],
                    interview.get('date', ''),
                    interview.get('time', ''),
                    interview.get('platform', ''),
                    interview.get('link', ''),
                    interview.get('status', 'pending')
                ]
                rows_interviews.append(row_iv)
            
            # Filas de Communications
            for comm in app.get('communications', []):
                row_comm = [
                    app_id,
                    app['company'],
                    comm.get('from', ''),
                    comm.get('subject', ''),
                    comm.get('date', ''),
                    comm.get('type', 'email'),
                    comm.get('body_preview', '')[:100]
                ]
                rows_communications.append(row_comm)
        
        # Escribir a Sheets
        try:
            # Limpiar hojas primero
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range='Applications!A2:K'
            ).execute()
            
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range='Interviews!A2:H'
            ).execute()
            
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range='Communications!A2:G'
            ).execute()
            
            # Escribir nuevos datos
            if rows_applications:
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Applications!A2',
                    valueInputOption='RAW',
                    body={'values': rows_applications}
                ).execute()
                print(f"✅ {len(rows_applications)} aplicaciones actualizadas")
            
            if rows_interviews:
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Interviews!A2',
                    valueInputOption='RAW',
                    body={'values': rows_interviews}
                ).execute()
                print(f"✅ {len(rows_interviews)} entrevistas actualizadas")
            
            if rows_communications:
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Communications!A2',
                    valueInputOption='RAW',
                    body={'values': rows_communications}
                ).execute()
                print(f"✅ {len(rows_communications)} comunicaciones actualizadas")
            
            return True
        
        except HttpError as error:
            print(f"❌ Error: {error}")
            return False
    
    def pull_from_sheets(self):
        """Sincroniza cambios desde Google Sheets al JSON"""
        if not self.spreadsheet_id:
            print("❌ No hay spreadsheet configurado")
            return False
        
        try:
            # Leer datos de Applications
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Applications!A2:K'
            ).execute()
            
            rows = result.get('values', [])
            
            if not rows:
                print("ℹ️  No hay datos en Sheets")
                return False
            
            # Cargar JSON existente
            with open(self.applications_file, 'r', encoding='utf-8') as f:
                applications = json.load(f)
            
            # Actualizar desde Sheets
            updated_count = 0
            for row in rows:
                if len(row) < 5:
                    continue
                
                app_id = row[0]
                
                if app_id in applications:
                    # Actualizar campos editables
                    if len(row) > 4:
                        applications[app_id]['status'] = row[4]
                    if len(row) > 5 and row[5]:
                        applications[app_id]['contact_email'] = row[5]
                    if len(row) > 6 and row[6]:
                        applications[app_id]['linkedin_url'] = row[6]
                    if len(row) > 7 and row[7]:
                        applications[app_id]['notes'] = row[7]
                    
                    updated_count += 1
            
            # Guardar JSON actualizado
            with open(self.applications_file, 'w', encoding='utf-8') as f:
                json.dump(applications, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {updated_count} aplicaciones sincronizadas desde Sheets")
            return True
        
        except HttpError as error:
            print(f"❌ Error: {error}")
            return False
    
    def save_config(self):
        """Guarda configuración del spreadsheet"""
        config = {
            'spreadsheet_id': self.spreadsheet_id,
            'last_sync': datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        """Carga configuración guardada"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.spreadsheet_id = config.get('spreadsheet_id')
                return True
        return False


# INTERFAZ DE COMANDOS
def main():
    import sys
    
    sync = SheetsSync()
    
    if len(sys.argv) < 2:
        print("""
📊 SYNC WITH SHEETS - Sincronización con Google Sheets

Comandos:
  init     - Crear nueva hoja de cálculo
  push     - Enviar datos a Sheets (JSON → Sheets)
  pull     - Traer cambios desde Sheets (Sheets → JSON)
  sync     - Sincronización bidireccional (push + pull)
  
Ejemplos:
  python sync_with_sheets.py init
  python sync_with_sheets.py push
  python sync_with_sheets.py pull
  python sync_with_sheets.py sync
        """)
        return
    
    command = sys.argv[1]
    
    if command == "init":
        print("\n📋 CREAR NUEVA HOJA DE CÁLCULO\n")
        
        if not sync.connect_sheets():
            return
        
        title = input("Nombre de la hoja [Job Applications Tracker]: ") or "Job Applications Tracker"
        
        spreadsheet_id = sync.create_spreadsheet(title)
        
        if spreadsheet_id:
            print(f"\n✅ Hoja creada exitosamente")
            print(f"🔗 Abre: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            print(f"\nAhora ejecuta: python sync_with_sheets.py push")
    
    elif command == "push":
        if not sync.load_config():
            print("❌ No hay hoja configurada. Ejecuta: python sync_with_sheets.py init")
            return
        
        if not sync.connect_sheets():
            return
        
        print("\n📤 Enviando datos a Google Sheets...\n")
        sync.push_to_sheets()
        print(f"\n🔗 Ver hoja: https://docs.google.com/spreadsheets/d/{sync.spreadsheet_id}")
    
    elif command == "pull":
        if not sync.load_config():
            print("❌ No hay hoja configurada. Ejecuta: python sync_with_sheets.py init")
            return
        
        if not sync.connect_sheets():
            return
        
        print("\n📥 Sincronizando cambios desde Google Sheets...\n")
        sync.pull_from_sheets()
    
    elif command == "sync":
        if not sync.load_config():
            print("❌ No hay hoja configurada. Ejecuta: python sync_with_sheets.py init")
            return
        
        if not sync.connect_sheets():
            return
        
        print("\n🔄 Sincronización bidireccional...\n")
        print("[1/2] Trayendo cambios desde Sheets...")
        sync.pull_from_sheets()
        
        print("\n[2/2] Enviando actualizaciones a Sheets...")
        sync.push_to_sheets()
        
        print(f"\n✅ Sincronización completada")
        print(f"🔗 Ver hoja: https://docs.google.com/spreadsheets/d/{sync.spreadsheet_id}")
    
    else:
        print(f"❌ Comando desconocido: {command}")


if __name__ == "__main__":
    main()