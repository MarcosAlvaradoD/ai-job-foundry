#!/usr/bin/env python3
"""
reauth_google.py — Re-autenticar Google OAuth (Sheets + Gmail)
==============================================================
Usar cuando el token.json expire o sea revocado.

Abre un browser para autenticación → guarda el nuevo token.

Uso:
  py scripts/maintenance/reauth_google.py
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.sheets.sheet_manager import SheetManager

def main():
    print("=" * 60)
    print("  Google OAuth Re-auth — AI Job Foundry")
    print("=" * 60)
    print()
    print("Se abrirá un browser para autenticación con Google.")
    print("Autoriza acceso a: Sheets + Gmail")
    print()

    try:
        sm = SheetManager()
        print()
        print("[OK] Token guardado en data/credentials/token.json")
        print("[OK] Verificando acceso al Sheet...")
        jobs = sm.get_all_jobs(tab='linkedin')
        print(f"[OK] LinkedIn tab: {len(jobs)} jobs encontrados")
        print()
        print("Re-autenticación completada exitosamente.")
        print("Ahora puedes correr: py scripts/apply/run_easy_apply.py")
    except Exception as e:
        print(f"[ERROR] {e}")
        print()
        print("Verifica que credentials.json existe en data/credentials/")

if __name__ == '__main__':
    main()
