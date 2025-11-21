"""
FIX OAUTH SCOPE ERROR - Gmail Monitor V2
El error es: 'invalid_scope: Bad Request'

CAUSA: token.json tiene scopes antiguos
SOLUCIÓN: Eliminar token.json y re-autenticar con scopes correctos
"""

import os
from pathlib import Path

print("="*70)
print("🔧 FIX OAUTH SCOPE ERROR")
print("="*70)

token_path = Path("data/credentials/token.json")

if token_path.exists():
    print(f"\n[INFO] Encontrado token antiguo: {token_path}")
    print("[INFO] Eliminando token antiguo...")
    
    # Backup
    backup_path = token_path.with_suffix('.json.old')
    os.rename(token_path, backup_path)
    
    print(f"[OK] Token respaldado en: {backup_path}")
    print(f"[OK] Token antiguo eliminado")
    
    print("\n" + "="*70)
    print("✅ FIX APLICADO")
    print("="*70)
    print("\n[NEXT] Ejecuta el monitor nuevamente:")
    print("   py -m core.automation.gmail_jobs_monitor_v2")
    print("\n[INFO] Se abrirá navegador para re-autenticar con scopes correctos")
    print("[INFO] Acepta todos los permisos solicitados")
    
else:
    print(f"\n[INFO] No se encontró token en: {token_path}")
    print("[OK] No hay nada que arreglar")
    print("\n[NEXT] Ejecuta directamente:")
    print("   py -m core.automation.gmail_jobs_monitor_v2")
