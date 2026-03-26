"""
Fix OAuth Scopes - Regenera token con TODOS los scopes necesarios
Ejecutar: py fix_oauth_complete.py
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# SCOPES COMPLETOS - Incluye todo lo que necesita el proyecto
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

CREDENTIALS_FILE = 'data/credentials/credentials.json'
TOKEN_FILE = 'data/credentials/token.json'  # Ubicación correcta que usan todos los scripts

def main():
    print("\n🔐 REGENERANDO TOKEN CON SCOPES COMPLETOS\n")
    
    # 1. Verificar credentials.json
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ ERROR: No se encuentra {CREDENTIALS_FILE}")
        return
    
    print(f"✅ Credentials encontrados: {CREDENTIALS_FILE}")
    
    # 2. Eliminar token viejo si existe
    if os.path.exists(TOKEN_FILE):
        print(f"🗑️  Eliminando token viejo: {TOKEN_FILE}")
        os.remove(TOKEN_FILE)
    
    # 3. Crear nuevo token con TODOS los scopes
    print(f"\n🔄 Creando nuevo token con {len(SCOPES)} scopes:")
    for scope in SCOPES:
        print(f"   - {scope.split('/')[-1]}")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES
        )
        
        # Esto abrirá el navegador para autorizar
        print("\n🌐 Abriendo navegador para autorización...")
        print("   1. Selecciona tu cuenta de Google")
        print("   2. Acepta TODOS los permisos")
        print("   3. Cierra el navegador cuando termine\n")
        
        creds = flow.run_local_server(port=0)
        
        # 4. Guardar nuevo token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ TOKEN REGENERADO EXITOSAMENTE")
        print(f"   📁 Guardado en: {TOKEN_FILE}")
        
        # 5. Verificar scopes guardados
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            saved_scopes = token_data.get('scopes', [])
        
        print(f"\n📋 Scopes en nuevo token:")
        for scope in saved_scopes:
            print(f"   ✅ {scope.split('/')[-1]}")
        
        print("\n🎉 LISTO - Puedes procesar emails ahora")
        print("   Comando: py core\\jobs_pipeline\\ingest_email_to_sheet_v2.py\n")
        
    except Exception as e:
        print(f"\n❌ ERROR al regenerar token: {e}")
        print("\nSolución:")
        print("1. Verifica que credentials.json sea válido")
        print("2. Asegúrate de tener acceso a internet")
        print("3. Intenta de nuevo\n")

if __name__ == "__main__":
    main()
