#!/usr/bin/env python3
"""
FIX OAUTH TOKEN - Regenera token.json válido
Usa la ruta CORRECTA de credentials.json
"""
import os
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# SCOPES correctos para Gmail + Sheets
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets'
]

# RUTAS CORRECTAS
CREDENTIALS_FILE = project_root / "data" / "credentials" / "credentials.json"
TOKEN_FILE = project_root / "data" / "credentials" / "token.json"

def main():
    print("\n" + "="*70)
    print("🔧 FIX OAUTH TOKEN - AI JOB FOUNDRY")
    print("="*70 + "\n")
    
    # Verificar que credentials.json existe
    if not CREDENTIALS_FILE.exists():
        print(f"❌ ERROR: No se encontró credentials.json")
        print(f"   Ubicación esperada: {CREDENTIALS_FILE}")
        print(f"   Descárgalo de Google Cloud Console:")
        print(f"   https://console.cloud.google.com/apis/credentials")
        return
    
    print(f"✅ credentials.json encontrado: {CREDENTIALS_FILE}")
    
    # Borrar token antiguo si existe
    if TOKEN_FILE.exists():
        print(f"🗑️  Borrando token expirado: {TOKEN_FILE}")
        TOKEN_FILE.unlink()
    
    print("\n📝 Scopes a autorizar:")
    for scope in SCOPES:
        print(f"   - {scope}")
    
    print("\n🌐 Abriendo navegador para autorizar...")
    print("   ⚠️  IMPORTANTE: Inicia sesión con markalvati@gmail.com")
    print()
    
    # Crear flow de autenticación
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES
    )
    
    # Ejecutar servidor local para OAuth
    creds = flow.run_local_server(port=0)
    
    # Guardar token nuevo
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print("\n" + "="*70)
    print("✅ TOKEN GENERADO EXITOSAMENTE")
    print("="*70)
    print(f"📁 Guardado en: {TOKEN_FILE}")
    print("\n🎉 Ahora puedes ejecutar:")
    print("   py control_center.py")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
