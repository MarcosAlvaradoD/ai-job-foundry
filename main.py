#!/usr/bin/env python3
"""
🚀 AI Job Foundry - Main Entry Point
====================================
Este archivo redirige al Control Center que tiene toda la funcionalidad.

USO RECOMENDADO:
    py control_center.py

NOTA: El Control Center ya incluye:
- ✅ Validación OAuth automática al inicio
- ✅ Menú interactivo con 19 opciones
- ✅ Pipeline completo y operaciones individuales
- ✅ Todo funcionando correctamente
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("🚀 AI JOB FOUNDRY")
    print("="*70)
    print()
    print("Redirigiendo al Control Center...")
    print("(Tiene validación OAuth automática + menú interactivo)")
    print()
    
    # Verificar que control_center.py existe
    control_center = Path(__file__).parent / "control_center.py"
    
    if not control_center.exists():
        print("❌ ERROR: control_center.py no encontrado")
        print(f"   Buscado en: {control_center}")
        return 1
    
    # Ejecutar control center
    try:
        result = subprocess.run(
            [sys.executable, str(control_center)],
            cwd=Path(__file__).parent
        )
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
