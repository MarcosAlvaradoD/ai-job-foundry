#!/usr/bin/env python3
"""
PATCH_CONTROL_CENTER.py - Actualiza menú del Control Center
REEMPLAZA opción 17 "Ver Estado del Proyecto" con "Interview Copilot"
(Sin huecos en el menú - profesional)
"""
from pathlib import Path

control_center_path = Path("control_center.py")

print("=" * 80)
print("🔧 PARCHE PARA CONTROL CENTER")
print("=" * 80)
print()
print("Cambios:")
print("  ❌ Opción 17: 'Ver Estado del Proyecto' → ELIMINADA")
print("  ✅ Opción 17: '🎤 Interview Copilot' → AGREGADA")
print()

if not control_center_path.exists():
    print("❌ control_center.py no encontrado")
    exit(1)

# Leer archivo
with open(control_center_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Backup
backup_path = Path("control_center.py.backup")
with open(backup_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f"✅ Backup creado: {backup_path}")

# ============================================================================
# PASO 1: Actualizar menú (opción 17)
# ============================================================================

print("\nPASO 1: Actualizando menú...")

new_lines = []
for line in lines:
    # Reemplazar línea del menú
    if '17. 📈 Ver Estado del Proyecto' in line:
        new_lines.append('    print("  17. 🎤 Interview Copilot (prep entrevistas)")\n')
        print("  ✅ Menú actualizado: línea 17")
    else:
        new_lines.append(line)

# ============================================================================
# PASO 2: Actualizar handler (elif option == '17')
# ============================================================================

print("PASO 2: Actualizando handler...")

final_lines = []
in_option_17 = False
skip_until_elif = False

for i, line in enumerate(new_lines):
    # Detectar inicio de opción 17
    if "elif option == '17':" in line:
        in_option_17 = True
        # Reemplazar con nuevo handler
        final_lines.append("    elif option == '17':\n")
        final_lines.append("        # Interview Copilot\n")
        final_lines.append("        print(f\"\\n{COLORS['CYAN']}🎤 Interview Copilot{COLORS['END']}\")\n")
        final_lines.append("        print(\"\\nOpciones:\")\n")
        final_lines.append("        print(\"  1. Session Recorder (grabar + transcribir)\")\n")
        final_lines.append("        print(\"  2. Simple Mode (sin grabar)\")\n")
        final_lines.append("        print(\"  3. V2 con Job Context\")\n")
        final_lines.append("        \n")
        final_lines.append("        copilot_option = input(f\"\\n{COLORS['BOLD']}Selecciona [1/2/3]: {COLORS['END']}\").strip()\n")
        final_lines.append("        \n")
        final_lines.append("        if copilot_option == '1':\n")
        final_lines.append("            return run_command(\n")
        final_lines.append("                ['py', 'core/copilot/interview_copilot_session_recorder.py'],\n")
        final_lines.append("                'Interview Copilot - Session Recorder'\n")
        final_lines.append("            )\n")
        final_lines.append("        elif copilot_option == '2':\n")
        final_lines.append("            return run_command(\n")
        final_lines.append("                ['py', 'core/copilot/interview_copilot_simple.py'],\n")
        final_lines.append("                'Interview Copilot - Simple Mode'\n")
        final_lines.append("            )\n")
        final_lines.append("        elif copilot_option == '3':\n")
        final_lines.append("            return run_command(\n")
        final_lines.append("                ['py', 'core/copilot/interview_copilot_v2.py'],\n")
        final_lines.append("                'Interview Copilot V2 - Job Context'\n")
        final_lines.append("            )\n")
        final_lines.append("        else:\n")
        final_lines.append("            print(f\"{COLORS['RED']}❌ Opción inválida{COLORS['END']}\")\n")
        final_lines.append("            return False\n")
        skip_until_elif = True
        print("  ✅ Handler actualizado: opción 17")
        continue
    
    # Skip líneas del handler viejo hasta encontrar siguiente elif
    if skip_until_elif:
        if line.strip().startswith('elif option ==') or line.strip().startswith('else:'):
            skip_until_elif = False
            in_option_17 = False
            final_lines.append(line)
        continue
    
    final_lines.append(line)

# ============================================================================
# PASO 3: Escribir archivo actualizado
# ============================================================================

print("\nPASO 3: Guardando cambios...")

with open(control_center_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("✅ control_center.py actualizado")

# ============================================================================
# RESUMEN
# ============================================================================

print("\n" + "=" * 80)
print("✅ PARCHE APLICADO EXITOSAMENTE")
print("=" * 80)
print()
print("Cambios realizados:")
print("  ✅ Opción 17: 'Ver Estado del Proyecto' → '🎤 Interview Copilot'")
print("  ✅ Handler actualizado con 3 modos de copilot")
print("  ✅ Sin huecos en el menú (0-19 consecutivos)")
print()
print("Para revertir cambios:")
print("  copy control_center.py.backup control_center.py")
print()
print("Probar:")
print("  py control_center.py")
print("  Seleccionar opción 17")
print()
print("=" * 80)
