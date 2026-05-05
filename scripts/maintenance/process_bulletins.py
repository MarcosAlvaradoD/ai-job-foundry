#!/usr/bin/env python3
"""
JOB BULLETIN PROCESSOR - STANDALONE
Process email bulletins from LinkedIn/Indeed/Glassdoor with multiple jobs

Can be run directly without pipeline:
    py process_bulletins.py
"""
import sys
import os
from pathlib import Path

# Add project root to path  (scripts/maintenance/ → scripts/ → project root)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_oauth():
    """Check if OAuth token exists"""
    token_path = project_root / "data" / "credentials" / "token.json"
    
    if not token_path.exists():
        print("\n" + "="*70)
        print("❌ ERROR: Token OAuth no encontrado")
        print("="*70)
        print(f"\nArchivo requerido: {token_path}")
        print("\n🔧 SOLUCIÓN:")
        print("   1. Ejecuta: py reauthenticate_gmail.py")
        print("   2. Acepta todos los permisos")
        print("   3. Vuelve a ejecutar este script")
        print("\n")
        sys.exit(1)
    
    print("✅ OAuth token encontrado")

def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("📬 JOB BULLETIN PROCESSOR - STANDALONE")
    print("="*70)
    print("\nProcesa boletines de job boards con múltiples ofertas")
    print("Fuentes: LinkedIn, Indeed, Glassdoor\n")
    
    # Check OAuth first
    print("🔐 Verificando OAuth...")
    check_oauth()
    
    # Import and run bulletin processor
    print("\n🚀 Iniciando procesador de boletines...\n")
    
    try:
        from core.automation.job_bulletin_processor import main as process_bulletins
        process_bulletins()
        
        print("\n" + "="*70)
        print("✅ PROCESAMIENTO COMPLETADO")
        print("="*70)
        print("\n💡 TIP: Ver resultados en:")
        print("   • Google Sheets")
        print("   • py control_center.py → Opción 14")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERROR EN PROCESAMIENTO")
        print("="*70)
        print(f"\nError: {str(e)}\n")
        
        print("🔧 TROUBLESHOOTING:")
        print("   1. Verifica OAuth: py reauthenticate_gmail.py")
        print("   2. Revisa logs en: logs/")
        print("   3. Ejecuta pipeline completo: py control_center.py → Opción 1")
        print("\n")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
