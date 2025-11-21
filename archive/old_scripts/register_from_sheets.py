"""
REGISTER FROM SHEETS - Importar aplicaciones desde Google Sheets
Para que puedas dar de alta en Excel/Sheets en lugar de PowerShell
"""

import json
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def connect_sheets():
    """Conecta con Google Sheets"""
    creds_path = Path("data/credentials/credentials.json")
    token_path = Path("data/credentials/token_sheets.json")
    
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
    
    return build('sheets', 'v4', credentials=creds)

def import_from_sheet(spreadsheet_id):
    """Importa aplicaciones desde Google Sheets"""
    
    service = connect_sheets()
    
    print(f"\n📥 Importando desde Google Sheets...")
    print(f"🔗 https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n")
    
    # Leer datos
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Applications!A2:H100'  # Ajusta el rango según necesites
        ).execute()
        
        rows = result.get('values', [])
        
        if not rows:
            print("⚠️  No hay datos en la hoja")
            return {}
        
        # Estructura esperada:
        # A: ID, B: Company, C: Position, D: Date Applied, E: Status, 
        # F: Contact Email, G: LinkedIn URL, H: Notes
        
        applications = {}
        imported_count = 0
        
        for row in rows:
            if len(row) < 3:  # Mínimo necesitamos: Company, Position
                continue
            
            # Generar ID si no existe
            if len(row) > 0 and row[0]:
                app_id = row[0]
            else:
                company = row[1] if len(row) > 1 else "Unknown"
                position = row[2] if len(row) > 2 else "Unknown"
                app_id = f"{company}_{position}".replace(" ", "_").lower()
            
            # Limpiar ID
            import re
            app_id = re.sub(r'[^a-z0-9_]', '', app_id)
            
            applications[app_id] = {
                "company": row[1] if len(row) > 1 else "",
                "position": row[2] if len(row) > 2 else "",
                "date_applied": row[3] if len(row) > 3 else datetime.now().strftime('%Y-%m-%d'),
                "status": row[4] if len(row) > 4 else "applied",
                "contact_email": row[5] if len(row) > 5 else None,
                "linkedin_url": row[6] if len(row) > 6 else None,
                "notes": row[7] if len(row) > 7 else None,
                "communications": [],
                "interviews": [],
                "last_checked": None,
                "created_at": datetime.now().isoformat()
            }
            
            imported_count += 1
            print(f"  ✅ {applications[app_id]['company']} - {applications[app_id]['position']}")
        
        print(f"\n📊 Total importadas: {imported_count}")
        return applications
    
    except HttpError as error:
        print(f"❌ Error: {error}")
        return {}

def merge_with_existing(new_apps):
    """Combina con aplicaciones existentes"""
    
    data_file = Path("data/applications/job_applications.json")
    
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        # Combinar (nuevas sobrescriben existentes)
        merged = {**existing, **new_apps}
        
        print(f"\n🔄 Combinando:")
        print(f"  Existentes: {len(existing)}")
        print(f"  Nuevas: {len(new_apps)}")
        print(f"  Total: {len(merged)}")
        
        return merged
    else:
        return new_apps

def save_applications(applications):
    """Guarda aplicaciones al JSON"""
    
    data_file = Path("data/applications/job_applications.json")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(applications, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Guardado en: {data_file}")

if __name__ == "__main__":
    import sys
    
    print("""
    📊 IMPORTAR DESDE GOOGLE SHEETS
    ================================
    
    Formato esperado en la hoja 'Applications':
    
    Columna A: ID (opcional, se genera automáticamente)
    Columna B: Company (REQUERIDO)
    Columna C: Position (REQUERIDO)
    Columna D: Date Applied (YYYY-MM-DD, opcional)
    Columna E: Status (applied/interview/offer/rejected/hired)
    Columna F: Contact Email (opcional)
    Columna G: LinkedIn URL (opcional)
    Columna H: Notes (opcional)
    
    """)
    
    # Cargar configuración
    config_file = Path("data/sheets_config.json")
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            spreadsheet_id = config.get('spreadsheet_id')
    else:
        spreadsheet_id = input("ID del Google Sheet: ").strip()
        
        if not spreadsheet_id:
            print("❌ ID requerido")
            sys.exit(1)
    
    # Importar
    new_apps = import_from_sheet(spreadsheet_id)
    
    if not new_apps:
        print("⚠️  No se importó nada")
        sys.exit(0)
    
    # Combinar con existentes
    all_apps = merge_with_existing(new_apps)
    
    # Guardar
    save_applications(all_apps)
    
    print("\n✅ Importación completada")
    print("\nAhora puedes:")
    print("  - Ver resumen: py job_tracker.py summary")
    print("  - Ver dashboard: py run_dashboard.py")
    print("  - Revisar correos: py job_tracker.py check")