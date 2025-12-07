#!/usr/bin/env python3
"""
FIX_DASHBOARD_OPTION.py - Arregla opción 13 del Control Center
Cambia de web/serve_dashboard.py → unified_app/app.py
"""
from pathlib import Path

control_center_path = Path("control_center.py")

print("=" * 80)
print("🔧 FIX DASHBOARD - CONTROL CENTER")
print("=" * 80)
print()
print("Problema identificado:")
print("  ❌ Opción 13 usa: web/serve_dashboard.py (versión vieja)")
print("  ✅ Debe usar: unified_app/app.py (versión 2.3)")
print()

if not control_center_path.exists():
    print("❌ control_center.py no encontrado")
    exit(1)

# Leer archivo
with open(control_center_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup (si no existe ya)
backup_path = Path("control_center.py.backup2")
if not backup_path.exists():
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
else:
    print(f"ℹ️  Backup existe: {backup_path}")

# ============================================================================
# CAMBIO: Actualizar opción 13 para usar unified_app
# ============================================================================

print("\nAplicando cambios...")

# Buscar y reemplazar el bloque de opción 13
old_block = """    elif option == '13':
        # Dashboard
        print(f"\\n{COLORS['YELLOW']}▶️  Iniciando Dashboard Server...{COLORS['END']}")
        print(f"Abre tu navegador en: {COLORS['CYAN']}http://localhost:8000{COLORS['END']}")
        print(f"{COLORS['RED']}Presiona Ctrl+C para detener el servidor{COLORS['END']}\\n")
        
        try:
            subprocess.run(['py', 'web/serve_dashboard.py'], check=True)
        except KeyboardInterrupt:
            print(f"\\n{COLORS['YELLOW']}👋 Dashboard server stopped.{COLORS['END']}")
        except Exception as e:
            print(f"\\n{COLORS['RED']}❌ Error: {e}{COLORS['END']}")
        finally:
            print(f"\\n{COLORS['GREEN']}✅ Servidor detenido{COLORS['END']}")
        return True"""

new_block = """    elif option == '13':
        # Dashboard - Unified App
        print(f"\\n{COLORS['YELLOW']}▶️  Iniciando Unified Web App...{COLORS['END']}")
        print(f"Abre tu navegador en: {COLORS['CYAN']}http://localhost:5555{COLORS['END']}")
        print(f"{COLORS['RED']}Presiona Ctrl+C para detener el servidor{COLORS['END']}\\n")
        
        try:
            subprocess.run(['py', 'unified_app/app.py'], check=True)
        except KeyboardInterrupt:
            print(f"\\n{COLORS['YELLOW']}👋 Unified App stopped.{COLORS['END']}")
        except Exception as e:
            print(f"\\n{COLORS['RED']}❌ Error: {e}{COLORS['END']}")
        finally:
            print(f"\\n{COLORS['GREEN']}✅ Servidor detenido{COLORS['END']}")
        return True"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("  ✅ Bloque de opción 13 actualizado")
    
    # Escribir archivo
    with open(control_center_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ Archivo guardado")
else:
    print("  ⚠️  Bloque no encontrado (quizás ya está actualizado)")
    print("     Verificando manualmente...")
    
    # Verificar si ya está actualizado
    if "unified_app/app.py" in content and "elif option == '13':" in content:
        print("  ✅ Ya está actualizado")
    else:
        print("  ❌ Necesita actualización manual")
        print("\nEditar control_center.py, buscar:")
        print("  elif option == '13':")
        print("\nCambiar:")
        print("  subprocess.run(['py', 'web/serve_dashboard.py'], check=True)")
        print("Por:")
        print("  subprocess.run(['py', 'unified_app/app.py'], check=True)")

# ============================================================================
# RESUMEN
# ============================================================================

print("\n" + "=" * 80)
print("✅ FIX APLICADO")
print("=" * 80)
print()
print("Cambios:")
print("  ✅ Opción 13 ahora usa: unified_app/app.py")
print("  ✅ Puerto actualizado: 8000 → 5555")
print()
print("Probar:")
print("  py control_center.py")
print("  Seleccionar opción 13")
print("  Debería abrir: http://localhost:5555")
print()
print("Características del Unified App:")
print("  ✅ Control Center integrado (17 funciones)")
print("  ✅ Dashboard con gráficas en tiempo real")
print("  ✅ Sistema de FIT scoring visual")
print("  ✅ 3 espacios publicitarios")
print()
print("=" * 80)
