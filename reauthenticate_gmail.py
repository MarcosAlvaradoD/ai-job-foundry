"""
RE-AUTHENTICATE GMAIL - Genera nuevo token OAuth
Ejecuta este script cuando necesites re-autenticar con Gmail

SCOPES REQUERIDOS:
- gmail.readonly
- gmail.modify (para labels)
- spreadsheets

USO:
py reauthenticate_gmail.py
"""

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes necesarios
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets'
]

def reauthenticate():
    """Re-autentica con Gmail y crea nuevo token"""
    
    print("="*70)
    print("🔐 RE-AUTENTICACIÓN GMAIL")
    print("="*70)
    
    token_path = Path("data/credentials/token.json")
    credentials_path = Path("data/credentials/credentials.json")
    
    # Verificar que existe credentials.json
    if not credentials_path.exists():
        print(f"\n[ERROR] No se encontró: {credentials_path}")
        print("[INFO] Necesitas el archivo credentials.json de Google Cloud Console")
        print("[STEPS]")
        print("1. Ve a: https://console.cloud.google.com/")
        print("2. APIs & Services > Credentials")
        print("3. Create Credentials > OAuth 2.0 Client ID")
        print("4. Download JSON y guárdalo en data/credentials/credentials.json")
        return False
    
    print(f"\n[INFO] Encontrado credentials.json")
    print(f"[INFO] Scopes requeridos:")
    for scope in SCOPES:
        print(f"   - {scope}")
    
    print("\n[INFO] Iniciando flujo OAuth...")
    print("[INFO] Se abrirá tu navegador para autenticarte")
    print("[TIP] Acepta TODOS los permisos solicitados\n")
    
    try:
        # Crear flujo OAuth
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES
        )
        
        # Ejecutar servidor local para callback
        creds = flow.run_local_server(port=0)
        
        # Guardar token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("\n" + "="*70)
        print("✅ AUTENTICACIÓN EXITOSA")
        print("="*70)
        print(f"\n[OK] Token guardado en: {token_path}")
        print("[OK] Permisos concedidos:")
        for scope in SCOPES:
            print(f"   ✓ {scope.split('/')[-1]}")
        
        print("\n[NEXT] Ahora puedes ejecutar:")
        print("   py -m core.automation.gmail_jobs_monitor_v2")
        
        return True
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERROR EN AUTENTICACIÓN")
        print("="*70)
        print(f"\n[ERROR] {e}")
        print("\n[TROUBLESHOOTING]")
        print("1. Verifica que credentials.json sea válido")
        print("2. Verifica que el proyecto de Google Cloud tenga APIs habilitadas:")
        print("   - Gmail API")
        print("   - Google Sheets API")
        print("3. Verifica que OAuth consent screen esté configurado")
        return False


if __name__ == "__main__":
    success = reauthenticate()
    
    if not success:
        print("\n[INFO] Necesitas ayuda? Revisa:")
        print("   docs/SOLUCION_DUPLICADOS.md")
        exit(1)
