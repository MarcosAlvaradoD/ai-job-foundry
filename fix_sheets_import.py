"""
FIX SHEETS IMPORT - Script para arreglar la importación desde cualquier Sheet
Detecta automáticamente las pestañas disponibles
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

def detect_sheets_structure(service, spreadsheet_id):
    """Detecta la estructura del Sheet"""
    print(f"\n🔍 Analizando Google Sheet...")
    print(f"🔗 https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n")
    
    try:
        # Obtener metadata
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        print(f"📊 Título: {spreadsheet['properties']['title']}")
        print(f"\n📑 Pestañas disponibles:")
        
        sheets_info = []
        for sheet in spreadsheet['sheets']:
            sheet_title = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            
            # Intentar leer datos
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_title}'!A1:Z100"
                ).execute()
                
                rows = result.get('values', [])
                row_count = len(rows)
                col_count = len(rows[0]) if rows else 0
                
                sheets_info.append({
                    'title': sheet_title,
                    'id': sheet_id,
                    'rows': row_count,
                    'cols': col_count,
                    'headers': rows[0] if rows else []
                })
                
                print(f"  ✅ {sheet_title}")
                print(f"     Filas: {row_count}, Columnas: {col_count}")
                if rows and len(rows) > 0:
                    print(f"     Encabezados: {', '.join(rows[0][:5])}")
            
            except Exception as e:
                print(f"  ⚠️  {sheet_title} (vacía o sin acceso)")
        
        return sheets_info
    
    except HttpError as error:
        print(f"❌ Error: {error}")
        return []

def find_applications_sheet(sheets_info):
    """Encuentra la pestaña con datos de aplicaciones"""
    
    # Buscar por nombre
    for sheet in sheets_info:
        title_lower = sheet['title'].lower()
        if 'application' in title_lower or 'vacante' in title_lower or 'job' in title_lower:
            if sheet['rows'] > 1:  # Tiene datos
                return sheet
    
    # Si no encuentra por nombre, tomar la primera con datos
    for sheet in sheets_info:
        if sheet['rows'] > 1:
            return sheet
    
    return None

def import_from_detected_sheet(service, spreadsheet_id, sheet_info):
    """Importa desde la pestaña detectada"""
    
    sheet_title = sheet_info['title']
    headers = sheet_info['headers']
    
    print(f"\n📥 Importando desde: '{sheet_title}'")
    print(f"🔍 Encabezados detectados: {headers}\n")
    
    # Mapeo flexible de columnas
    column_map = {}
    
    for i, header in enumerate(headers):
        header_lower = header.lower()
        
        if 'company' in header_lower or 'empresa' in header_lower:
            column_map['company'] = i
        elif 'position' in header_lower or 'puesto' in header_lower or 'vacante' in header_lower:
            column_map['position'] = i
        elif 'date' in header_lower or 'fecha' in header_lower:
            column_map['date'] = i
        elif 'status' in header_lower or 'estado' in header_lower:
            column_map['status'] = i
        elif 'email' in header_lower or 'correo' in header_lower or 'contact' in header_lower:
            column_map['email'] = i
        elif 'linkedin' in header_lower or 'url' in header_lower or 'link' in header_lower:
            column_map['linkedin'] = i
        elif 'note' in header_lower or 'nota' in header_lower:
            column_map['notes'] = i
    
    print(f"🗺️  Mapeo de columnas:")
    for field, idx in column_map.items():
        print(f"  {field}: columna {idx} ({headers[idx]})")
    
    # Leer datos
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_title}'!A2:Z100"
        ).execute()
        
        rows = result.get('values', [])
        
        if not rows:
            print("\n⚠️  No hay datos para importar")
            return {}
        
        applications = {}
        imported_count = 0
        
        for row in rows:
            if len(row) < 2:  # Muy poca data
                continue
            
            # Extraer datos según mapeo
            company = row[column_map['company']] if 'company' in column_map and len(row) > column_map['company'] else "Unknown"
            position = row[column_map['position']] if 'position' in column_map and len(row) > column_map['position'] else "Unknown"
            
            if company == "Unknown" and position == "Unknown":
                continue
            
            # Generar ID
            import re
            app_id = f"{company}_{position}".replace(" ", "_").lower()
            app_id = re.sub(r'[^a-z0-9_]', '', app_id)
            
            applications[app_id] = {
                "company": company,
                "position": position,
                "date_applied": row[column_map['date']] if 'date' in column_map and len(row) > column_map['date'] else datetime.now().strftime('%Y-%m-%d'),
                "status": row[column_map['status']] if 'status' in column_map and len(row) > column_map['status'] else "applied",
                "contact_email": row[column_map['email']] if 'email' in column_map and len(row) > column_map['email'] else None,
                "linkedin_url": row[column_map['linkedin']] if 'linkedin' in column_map and len(row) > column_map['linkedin'] else None,
                "notes": row[column_map['notes']] if 'notes' in column_map and len(row) > column_map['notes'] else None,
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

def save_applications(applications):
    """Guarda aplicaciones al JSON"""
    
    data_file = Path("data/applications/job_applications.json")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Combinar con existentes si hay
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        merged = {**existing, **applications}
        
        print(f"\n🔄 Combinando:")
        print(f"  Existentes: {len(existing)}")
        print(f"  Nuevas: {len(applications)}")
        print(f"  Total: {len(merged)}")
        
        applications = merged
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(applications, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Guardado en: {data_file}")

if __name__ == "__main__":
    import sys
    
    print("""
    🔧 FIX SHEETS IMPORT
    ====================
    
    Este script detecta automáticamente la estructura de tu Google Sheet
    e importa los datos sin importar cómo estén organizados.
    
    """)
    
    # Cargar configuración
    config_file = Path("data/sheets_config.json")
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            spreadsheet_id = config.get('spreadsheet_id')
            print(f"📋 Usando Sheet configurado: {spreadsheet_id[:20]}...")
    else:
        print("⚠️  No hay Sheet configurado")
        spreadsheet_id = input("\nPega el ID del Google Sheet (o URL completa): ").strip()
        
        # Extraer ID de URL si es necesario
        if 'docs.google.com' in spreadsheet_id:
            import re
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', spreadsheet_id)
            if match:
                spreadsheet_id = match.group(1)
        
        if not spreadsheet_id:
            print("❌ ID requerido")
            sys.exit(1)
        
        # Guardar configuración
        config = {
            "spreadsheet_id": spreadsheet_id,
            "last_sync": datetime.now().isoformat()
        }
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Conectar
    service = connect_sheets()
    
    # Detectar estructura
    sheets_info = detect_sheets_structure(service, spreadsheet_id)
    
    if not sheets_info:
        print("\n❌ No se pudo analizar el Sheet")
        sys.exit(1)
    
    # Encontrar pestaña con aplicaciones
    target_sheet = find_applications_sheet(sheets_info)
    
    if not target_sheet:
        print("\n⚠️  No se encontró una pestaña con datos de aplicaciones")
        print("\nPestañas disponibles:")
        for i, sheet in enumerate(sheets_info, 1):
            print(f"  {i}. {sheet['title']} ({sheet['rows']} filas)")
        
        choice = input("\n¿Cuál quieres usar? (número): ").strip()
        try:
            target_sheet = sheets_info[int(choice) - 1]
        except:
            print("❌ Opción inválida")
            sys.exit(1)
    
    print(f"\n🎯 Usando pestaña: '{target_sheet['title']}'")
    
    # Importar
    applications = import_from_detected_sheet(service, spreadsheet_id, target_sheet)
    
    if not applications:
        print("\n⚠️  No se importó nada")
        sys.exit(0)
    
    # Guardar
    save_applications(applications)
    
    print("\n✅ Importación completada")
    print("\nAhora puedes:")
    print("  - Ver resumen: py job_tracker.py summary")
    print("  - Ver dashboard: py run_dashboard.py")