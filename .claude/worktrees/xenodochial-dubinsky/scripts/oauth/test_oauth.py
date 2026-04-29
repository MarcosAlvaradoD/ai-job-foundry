"""
Test OAuth - Verifica que el token funcione correctamente
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n🔐 VERIFICANDO OAUTH...\n")

# Test 1: Token existe
token_path = "data/credentials/token.json"
if os.path.exists(token_path):
    print(f"✅ Token encontrado: {token_path}")
else:
    print(f"❌ Token NO encontrado: {token_path}")
    exit(1)

# Test 2: Token es válido JSON
import json
try:
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    print(f"✅ Token es JSON válido")
except Exception as e:
    print(f"❌ Token corrupto: {e}")
    exit(1)

# Test 3: Verificar scopes
expected_scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar"
]

token_scopes = token_data.get('scopes', [])
print(f"\n📋 Scopes en token: {len(token_scopes)}")
for scope in token_scopes:
    scope_name = scope.split('/')[-1]
    print(f"   ✅ {scope_name}")

missing = [s for s in expected_scopes if s not in token_scopes]
if missing:
    print(f"\n⚠️  Scopes faltantes:")
    for scope in missing:
        print(f"   ❌ {scope.split('/')[-1]}")
else:
    print(f"\n✅ TODOS LOS SCOPES PRESENTES")

# Test 4: Intentar crear credentials
print(f"\n🔄 Probando credenciales...")
try:
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file(token_path, expected_scopes)
    print(f"✅ Credenciales creadas exitosamente")
    
    # Test 5: Verificar que no estén expiradas
    if creds.valid:
        print(f"✅ Token válido y no expirado")
    elif creds.expired and creds.refresh_token:
        print(f"⏳ Token expirado pero puede refrescarse")
        print(f"   Refrescando...")
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        print(f"✅ Token refrescado exitosamente")
        
        # Guardar token refrescado
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        print(f"✅ Token actualizado guardado")
    else:
        print(f"❌ Token inválido y sin refresh_token")
        exit(1)
    
except Exception as e:
    print(f"❌ ERROR al crear credenciales: {e}")
    exit(1)

# Test 6: Probar conexión a Gmail
print(f"\n📧 Probando conexión a Gmail...")
try:
    from googleapiclient.discovery import build
    gmail = build('gmail', 'v1', credentials=creds)
    profile = gmail.users().getProfile(userId='me').execute()
    email = profile.get('emailAddress', 'Unknown')
    print(f"✅ Gmail conectado: {email}")
except Exception as e:
    print(f"❌ Error conectando a Gmail: {e}")
    exit(1)

# Test 7: Probar conexión a Sheets
print(f"\n📊 Probando conexión a Google Sheets...")
try:
    sheets = build('sheets', 'v4', credentials=creds)
    sheet_id = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"
    result = sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
    title = result.get('properties', {}).get('title', 'Unknown')
    print(f"✅ Google Sheets conectado: {title}")
except Exception as e:
    print(f"❌ Error conectando a Sheets: {e}")
    exit(1)

print(f"\n🎉 TODOS LOS TESTS PASARON")
print(f"\n✅ OAuth está funcionando correctamente")
print(f"   Puedes ejecutar:")
print(f"   py core\\jobs_pipeline\\ingest_email_to_sheet_v2.py\n")
