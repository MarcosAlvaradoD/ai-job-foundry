#!/usr/bin/env python3
"""
OAuth Token Regenerator
Elimina token.json y fuerza nueva autenticación con todos los scopes necesarios
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# TODOS los scopes necesarios
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',        # Google Sheets R/W
    'https://www.googleapis.com/auth/gmail.readonly',      # Gmail read
    'https://www.googleapis.com/auth/gmail.modify',        # Gmail modify labels
    'https://www.googleapis.com/auth/gmail.labels'          # Gmail labels
]

def regenerate_token():
    """Elimina token viejo y genera uno nuevo con todos los scopes"""
    
    print("\n" + "="*70)
    print("🔐 OAUTH TOKEN REGENERATOR")
    print("="*70)
    
    # Paths
    cred_dir = project_root / "data" / "credentials"
    token_path = cred_dir / "token.json"
    credentials_path = cred_dir / "credentials.json"
    
    # Check if credentials.json exists
    if not credentials_path.exists():
        print(f"❌ Error: credentials.json no encontrado en {credentials_path}")
        print(f"\n📝 Para obtener credentials.json:")
        print(f"   1. Ve a https://console.cloud.google.com/apis/credentials")
        print(f"   2. Crea un nuevo OAuth 2.0 Client ID (Desktop app)")
        print(f"   3. Descarga el JSON y guárdalo como credentials.json")
        print(f"   4. Cópialo a: {cred_dir}/")
        return False
    
    # Delete old token
    if token_path.exists():
        print(f"🗑️  Eliminando token viejo...")
        token_path.unlink()
        print(f"✅ Token eliminado")
    else:
        print(f"ℹ️  No hay token previo")
    
    print(f"\n🔐 Iniciando flujo de autenticación OAuth...")
    print(f"📋 Scopes solicitados:")
    for scope in SCOPES:
        print(f"   • {scope}")
    
    print(f"\n🌐 Se abrirá tu navegador para autenticar...")
    print(f"⚠️  IMPORTANTE: Acepta TODOS los permisos solicitados\n")
    
    try:
        # OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            SCOPES
        )
        
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("\n" + "="*70)
        print("✅ TOKEN GENERADO EXITOSAMENTE")
        print("="*70)
        print(f"📁 Guardado en: {token_path}")
        print(f"✅ El sistema ya puede acceder a:")
        print(f"   • Google Sheets (lectura/escritura)")
        print(f"   • Gmail (lectura de emails)")
        print(f"   • Gmail (modificar etiquetas)")
        print(f"   • Gmail (mover a papelera)")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante autenticación: {e}")
        print(f"\n💡 Posibles causas:")
        print(f"   • No aceptaste los permisos")
        print(f"   • Credenciales.json inválido")
        print(f"   • Problema de red")
        return False

if __name__ == "__main__":
    success = regenerate_token()
    sys.exit(0 if success else 1)
