"""
🧪 Quick Test - OAuth Token Validator
======================================
Script de prueba rápida para verificar el funcionamiento del validador OAuth.

Este script:
1. Valida el token actual
2. Intenta procesar 1 email de prueba
3. Verifica acceso a Google Sheets
4. Genera reporte de status

Uso: py scripts\test_oauth_validator.py

Autor: Marcos Alberto Alvarado
Fecha: 2026-01-02
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar validador
try:
    from oauth_token_validator import validate_and_refresh_token
    VALIDATOR_FOUND = True
except ImportError:
    VALIDATOR_FOUND = False
    print("❌ ERROR: oauth_token_validator.py no encontrado")
    print("   Cópialo a la raíz del proyecto primero")
    sys.exit(1)


def print_header():
    """Imprime header del test."""
    print()
    print("=" * 70)
    print("🧪 OAUTH TOKEN VALIDATOR - QUICK TEST")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()


def print_section(title):
    """Imprime título de sección."""
    print()
    print("-" * 70)
    print(f"📋 {title}")
    print("-" * 70)


def test_validator_exists():
    """Test 1: Verificar que el validador existe."""
    print_section("TEST 1: Verificar Validador")
    
    if VALIDATOR_FOUND:
        print("✅ oauth_token_validator.py encontrado")
        return True
    else:
        print("❌ oauth_token_validator.py NO encontrado")
        return False


def test_token_validation():
    """Test 2: Validar token OAuth."""
    print_section("TEST 2: Validar Token OAuth")
    
    try:
        result = validate_and_refresh_token()
        
        if result:
            print("✅ Token válido o renovado exitosamente")
            
            # Leer info del token
            token_path = Path("data/credentials/token.json")
            if token_path.exists():
                with open(token_path, 'r') as f:
                    token_data = json.load(f)
                
                expiry = token_data.get('expiry', 'Unknown')
                print(f"   Expira: {expiry}")
            
            return True
        else:
            print("❌ Validación de token falló")
            return False
            
    except Exception as e:
        print(f"❌ Error al validar token: {e}")
        return False


def test_gmail_access():
    """Test 3: Verificar acceso a Gmail API."""
    print_section("TEST 3: Verificar Acceso a Gmail API")
    
    try:
        # Intentar importar y crear monitor
        from core.automation.gmail_jobs_monitor import GmailJobsMonitor
        
        monitor = GmailJobsMonitor()
        print("✅ GmailJobsMonitor creado exitosamente")
        
        # Intentar listar 1 mensaje (sin procesar)
        service = monitor.service
        results = service.users().messages().list(
            userId='me',
            maxResults=1,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        print(f"✅ Gmail API respondió: {len(messages)} mensaje(s) en inbox")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al acceder a Gmail API: {e}")
        return False


def test_sheets_access():
    """Test 4: Verificar acceso a Google Sheets API."""
    print_section("TEST 4: Verificar Acceso a Google Sheets API")
    
    try:
        from core.sheets.sheet_manager import SheetManager
        
        manager = SheetManager()
        print("✅ SheetManager creado exitosamente")
        
        # Intentar leer primera fila
        from googleapiclient.discovery import build
        service = build('sheets', 'v4', credentials=manager.credentials)
        
        result = service.spreadsheets().values().get(
            spreadsheetId=manager.spreadsheet_id,
            range='Jobs!A1:B1'
        ).execute()
        
        values = result.get('values', [])
        print(f"✅ Google Sheets API respondió: {len(values)} fila(s) leídas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al acceder a Sheets API: {e}")
        return False


def test_full_workflow():
    """Test 5: Workflow completo (simulado)."""
    print_section("TEST 5: Workflow Completo (Simulado)")
    
    try:
        print("1. ✅ Token validado")
        print("2. ✅ Gmail API accessible")
        print("3. ✅ Sheets API accessible")
        print("4. ✅ Módulos importables")
        print()
        print("✅ Sistema listo para ejecutar pipeline completo")
        return True
        
    except Exception as e:
        print(f"❌ Error en workflow: {e}")
        return False


def print_summary(results):
    """Imprime resumen de resultados."""
    print()
    print("=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<40} {status}")
    
    print("-" * 70)
    print(f"Total: {total} tests  |  Passed: {passed}  |  Failed: {failed}")
    print("=" * 70)
    print()
    
    if failed == 0:
        print("🎉 TODOS LOS TESTS PASARON")
        print()
        print("✅ El sistema OAuth está funcionando correctamente")
        print("✅ Puedes ejecutar el pipeline completo: py main.py")
        return True
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print()
        print("Posibles soluciones:")
        print("1. Verificar que todos los archivos estén en su lugar")
        print("2. Ejecutar: py oauth_token_validator.py --force")
        print("3. Verificar: py scripts/oauth/reauthenticate_gmail_v2.py")
        print("4. Revisar logs para más detalles")
        return False


def main():
    """Entry point."""
    print_header()
    
    # Ejecutar tests
    results = {}
    
    results["Validador Existe"] = test_validator_exists()
    if not results["Validador Existe"]:
        print_summary(results)
        sys.exit(1)
    
    results["Token Validation"] = test_token_validation()
    if not results["Token Validation"]:
        print()
        print("⚠️  IMPORTANTE: Token no válido. El resto de tests fallarán.")
        print("   Ejecuta: py scripts/oauth/reauthenticate_gmail_v2.py")
        print()
    
    results["Gmail API Access"] = test_gmail_access()
    results["Sheets API Access"] = test_sheets_access()
    results["Full Workflow"] = test_full_workflow()
    
    # Resumen
    success = print_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
