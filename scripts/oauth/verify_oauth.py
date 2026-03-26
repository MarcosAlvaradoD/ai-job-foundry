"""
Verificador de Token OAuth - Confirma que todo está sincronizado
"""
import os
import json
from pathlib import Path

print("\n🔍 VERIFICANDO CONFIGURACIÓN OAUTH\n")

# 1. Verificar ubicaciones de archivos
print("📁 Verificando archivos...")
creds_path = "data/credentials/credentials.json"
token_path = "data/credentials/token.json"
token_alt_path = "workflows/token.json"

if os.path.exists(creds_path):
    print(f"   ✅ {creds_path}")
else:
    print(f"   ❌ {creds_path} NO ENCONTRADO")

if os.path.exists(token_path):
    print(f"   ✅ {token_path}")
else:
    print(f"   ❌ {token_path} NO ENCONTRADO")

if os.path.exists(token_alt_path):
    print(f"   ℹ️  {token_alt_path} (alternativo existe)")

# 2. Verificar scopes del token
print("\n📋 Verificando scopes del token...")
if os.path.exists(token_path):
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    scopes = token_data.get('scopes', [])
    print(f"   Total scopes: {len(scopes)}")
    
    expected_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]
    
    all_match = True
    for scope in expected_scopes:
        if scope in scopes:
            print(f"   ✅ {scope.split('/')[-1]}")
        else:
            print(f"   ❌ {scope.split('/')[-1]} FALTANTE")
            all_match = False
    
    # Verificar scopes extra
    for scope in scopes:
        if scope not in expected_scopes:
            print(f"   ⚠️  {scope.split('/')[-1]} (extra, no esperado)")
    
    if all_match and len(scopes) == len(expected_scopes):
        print("\n✅ TODOS LOS SCOPES CORRECTOS")
    else:
        print("\n❌ SCOPES NO COINCIDEN")
        print("   Ejecuta: py fix_oauth_complete.py")
else:
    print("   ❌ Token no encontrado")

# 3. Verificar refresh_token
print("\n🔑 Verificando refresh token...")
if os.path.exists(token_path):
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    if token_data.get('refresh_token'):
        print("   ✅ Refresh token presente")
    else:
        print("   ❌ Refresh token FALTANTE")
        print("   El token no podrá renovarse automáticamente")

# 4. Test rápido de autenticación
print("\n🧪 Testeando autenticación...")
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    creds = Credentials.from_authorized_user_file(token_path, expected_scopes)
    
    if creds.valid:
        print("   ✅ Credenciales VÁLIDAS")
    elif creds.expired and creds.refresh_token:
        print("   ⏳ Token expirado, intentando refresh...")
        try:
            creds.refresh(Request())
            print("   ✅ Token REFRESCADO exitosamente")
            
            # Guardar token actualizado
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
            print("   💾 Token guardado")
        except Exception as e:
            print(f"   ❌ Error al refrescar: {e}")
    else:
        print("   ❌ Credenciales INVÁLIDAS")
        print("   Ejecuta: py fix_oauth_complete.py")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Resumen
print("\n" + "="*60)
print("RESUMEN:")
print("="*60)

if os.path.exists(token_path):
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    scopes_ok = len(token_data.get('scopes', [])) == 6
    refresh_ok = bool(token_data.get('refresh_token'))
    
    if scopes_ok and refresh_ok:
        print("✅ CONFIGURACIÓN COMPLETA Y CORRECTA")
        print("\n🚀 Puedes ejecutar:")
        print("   py core\\jobs_pipeline\\ingest_email_to_sheet_v2.py")
        print("   py optimize_batch_updates.py")
    else:
        print("⚠️  CONFIGURACIÓN INCOMPLETA")
        print("\n📝 EJECUTA:")
        print("   py fix_oauth_complete.py")
else:
    print("❌ TOKEN NO ENCONTRADO")
    print("\n📝 EJECUTA:")
    print("   py fix_oauth_complete.py")

print("="*60 + "\n")
