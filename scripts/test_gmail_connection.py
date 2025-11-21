"""
TEST GMAIL CONNECTION - Verificar que Gmail API funciona
Ejecutar DESPUÉS de configurar credentials.json
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def test_gmail_connection():
    """Prueba la conexión con Gmail API"""
    
    print("\n" + "="*50)
    print("  🧪 PRUEBA DE CONEXIÓN GMAIL API")
    print("="*50 + "\n")
    
    # Verificar estructura de carpetas
    credentials_path = Path("data/credentials/credentials.json")
    token_path = Path("data/credentials/token.json")
    
    print("[1/5] Verificando estructura de carpetas...")
    if not credentials_path.parent.exists():
        print("  ❌ Carpeta data/credentials/ no existe")
        print("  📝 Creándola...")
        credentials_path.parent.mkdir(parents=True, exist_ok=True)
    print("  ✅ Estructura OK\n")
    
    print("[2/5] Verificando credentials.json...")
    if not credentials_path.exists():
        print("  ❌ No se encontró credentials.json")
        print("\n  📋 PASOS PARA OBTENERLO:")
        print("  1. Ve a: https://console.cloud.google.com")
        print("  2. APIs & Services > Credentials")
        print("  3. CREATE CREDENTIALS > OAuth client ID")
        print("  4. Application type: Desktop app")
        print("  5. Descarga el JSON y guárdalo en:")
        print(f"     {credentials_path.absolute()}\n")
        return False
    print("  ✅ credentials.json encontrado\n")
    
    print("[3/5] Importando librerías de Google...")
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        print("  ✅ Librerías importadas\n")
    except ImportError as e:
        print(f"  ❌ Error: {e}")
        print("\n  📦 Instala las dependencias:")
        print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client\n")
        return False
    
    print("[4/5] Autenticando con Google...")
    
    # Scopes necesarios
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.labels'
    ]
    
    creds = None
    
    # Cargar token existente
    if token_path.exists():
        print("  📄 Token existente encontrado")
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # Si no hay credenciales válidas, obtener nuevas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  🔄 Refrescando token expirado...")
            creds.refresh(Request())
        else:
            print("  🌐 Iniciando flujo OAuth (se abrirá tu navegador)...")
            print("\n  ⚠️  IMPORTANTE:")
            print("  - Selecciona tu cuenta: markalvati@gmail.com")
            print("  - Si ves 'App no verificada', click en 'Avanzado'")
            print("  - Luego 'Ir a AI Job Foundry (no seguro)'")
            print("  - Acepta los permisos\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Guardar token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("  ✅ Token guardado\n")
    
    print("[5/5] Probando lectura de correos...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Obtener últimos 5 correos
        results = service.users().messages().list(
            userId='me',
            maxResults=5,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("  ℹ️  No se encontraron correos en INBOX\n")
        else:
            print(f"  ✅ Se encontraron {len(messages)} correos\n")
            print("  📧 Últimos correos:")
            
            for i, msg in enumerate(messages, 1):
                # Obtener detalles del correo
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                
                from_addr = headers.get('From', 'Desconocido')
                subject = headers.get('Subject', '(Sin asunto)')
                date = headers.get('Date', '')
                
                print(f"\n  [{i}] De: {from_addr}")
                print(f"      Asunto: {subject}")
                print(f"      Fecha: {date}")
        
        print("\n" + "="*50)
        print("  ✅ CONEXIÓN EXITOSA")
        print("="*50 + "\n")
        print("  Siguiente paso: Ejecutar job_tracker.py\n")
        return True
    
    except HttpError as error:
        print(f"  ❌ Error HTTP: {error}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = test_gmail_connection()
    
    if not success:
        print("  ⚠️  Revisa los pasos en GMAIL_SETUP.md\n")
        sys.exit(1)