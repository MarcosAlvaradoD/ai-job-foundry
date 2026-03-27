#!/usr/bin/env python3
"""FIX: OAuth Invalid Scope Error"""
import os
from pathlib import Path

token_path = Path("data/credentials/token.json")
credentials_path = Path("data/credentials/credentials.json")

print("="*70)
print("🔧 FIX OAUTH - Invalid Scope Error")
print("="*70)

if token_path.exists():
    print(f"\n1️⃣ Borrando token antiguo: {token_path}")
    os.remove(token_path)
    print("   ✅ Token borrado")
else:
    print(f"\n1️⃣ Token no existe: {token_path}")

if not credentials_path.exists():
    print(f"\n❌ ERROR: No se encontró credentials.json")
    exit(1)

print(f"\n2️⃣ Credentials.json encontrado")
print("\n3️⃣ Iniciando re-autenticación...")
print("Se abrirá tu navegador - acepta TODOS los permisos\n")

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

try:
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    print("\n✅ Re-autenticación exitosa!")
    print(f"✅ Nuevo token guardado")
    print("\n🎉 OAUTH CORREGIDO")
except Exception as e:
    print(f"\n❌ Error: {e}")
