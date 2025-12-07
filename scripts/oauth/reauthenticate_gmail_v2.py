#!/usr/bin/env python3
"""
Gmail OAuth Re-authentication Script (Windows-compatible, no emojis)
Regenera token.json cuando el OAuth client fue eliminado o expiró
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/spreadsheets'
]

def main():
    """Re-authenticate Gmail and regenerate token"""
    print("\n" + "="*70)
    print("GMAIL OAUTH RE-AUTHENTICATION")
    print("="*70)
    
    # Paths
    creds_dir = project_root / "data" / "credentials"
    credentials_path = creds_dir / "credentials.json"
    token_path = creds_dir / "token.json"
    
    # Verify credentials.json exists
    if not credentials_path.exists():
        print(f"\n[ERROR] No se encontro credentials.json")
        print(f"   Ubicacion esperada: {credentials_path}")
        print(f"\nPASOS PARA OBTENER credentials.json:")
        print("   1. Ve a: https://console.cloud.google.com/")
        print("   2. Crea/selecciona un proyecto")
        print("   3. Habilita Gmail API y Google Sheets API")
        print("   4. Crea credenciales OAuth 2.0")
        print("   5. Descarga el JSON y guardalo como credentials.json")
        print(f"   6. Colocalo en: {creds_dir}")
        return 1
    
    print(f"\n[OK] credentials.json encontrado")
    
    # Delete old token if exists
    if token_path.exists():
        print(f"[INFO] Eliminando token antiguo...")
        token_path.unlink()
        print(f"   [OK] Token eliminado")
    
    # Start OAuth flow
    print(f"\n[INFO] Iniciando flujo OAuth...")
    print(f"   Se abrira tu navegador para autenticacion")
    print(f"   IMPORTANTE: Acepta TODOS los permisos solicitados\n")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES
        )
        
        # Run local server for OAuth callback
        creds = flow.run_local_server(
            port=0,
            authorization_prompt_message='Abriendo navegador para autenticacion...',
            success_message='Autenticacion exitosa! Puedes cerrar esta ventana.',
            open_browser=True
        )
        
        # Save new token
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        
        print("\n" + "="*70)
        print("[SUCCESS] RE-AUTENTICACION EXITOSA")
        print("="*70)
        print(f"Nuevo token guardado en: {token_path}")
        print(f"Scopes autorizados:")
        for scope in SCOPES:
            print(f"   - {scope.split('/')[-1]}")
        
        print("\nPROXIMOS PASOS:")
        print("   1. Ejecuta: py control_center.py")
        print("   2. Prueba Opcion 1 (Pipeline Completo)")
        print("   3. Verifica que no hay errores de OAuth")
        print("\n")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*70)
        print("[ERROR] ERROR EN RE-AUTENTICACION")
        print("="*70)
        print(f"Error: {str(e)}\n")
        
        print("TROUBLESHOOTING:")
        print("   1. Verifica que credentials.json es valido")
        print("   2. Asegurate de que Gmail API esta habilitado")
        print("   3. Verifica que el proyecto OAuth no fue eliminado")
        print("   4. Intenta crear nuevas credenciales OAuth")
        print("\n")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
