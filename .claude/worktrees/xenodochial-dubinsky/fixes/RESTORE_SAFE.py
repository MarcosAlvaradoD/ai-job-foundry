#!/usr/bin/env python3
"""
RESTORE_SAFE.py - Restauración Segura
Solo arregla imports rotos, NO mueve archivos
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).parent

print("=" * 80)
print("🔧 RESTAURACIÓN SEGURA - AI JOB FOUNDRY")
print("=" * 80)
print()
print("Este script:")
print("  ✅ Arregla imports rotos")
print("  ✅ Elimina duplicados")
print("  ❌ NO mueve archivos que funcionan")
print()

# ============================================================================
# PASO 1: Arreglar verify_job_status.py
# ============================================================================

print("PASO 1: Arreglando verify_job_status.py...")
print("-" * 80)

verify_path = ROOT / "scripts" / "maintenance" / "verify_job_status.py"

if verify_path.exists():
    with open(verify_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "sys.path.insert" in content:
        print("✓  verify_job_status.py ya tiene sys.path fix")
    else:
        # Read lines
        lines = content.split('\n')
        
        # Find where to insert (after docstring or first import)
        insert_at = 0
        in_docstring = False
        
        for i, line in enumerate(lines):
            # Skip docstring
            if '"""' in line or "'''" in line:
                if in_docstring:
                    insert_at = i + 1
                    in_docstring = False
                    break
                else:
                    in_docstring = True
            
            # Or insert before first import
            elif (line.startswith('from ') or line.startswith('import ')) and not in_docstring:
                insert_at = i
                break
        
        if insert_at == 0:
            insert_at = 5  # Default
        
        # Add sys.path fix
        fix_lines = [
            "import sys",
            "from pathlib import Path",
            "sys.path.insert(0, str(Path(__file__).parent.parent.parent))",
            ""
        ]
        
        new_lines = lines[:insert_at] + fix_lines + lines[insert_at:]
        
        # Write back
        with open(verify_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ FIXED: verify_job_status.py")
        print("   Added sys.path.insert() at line", insert_at)
else:
    print("⚠️  verify_job_status.py not found in scripts/maintenance/")
    print("   Checking root...")
    
    root_verify = ROOT / "verify_job_status.py"
    if root_verify.exists():
        print("✓  Found in root - already OK")
    else:
        print("❌ Not found anywhere!")

print()

# ============================================================================
# PASO 2: Verificar otros scripts en scripts/maintenance/
# ============================================================================

print("PASO 2: Verificando otros scripts en scripts/maintenance/...")
print("-" * 80)

maintenance_dir = ROOT / "scripts" / "maintenance"
if maintenance_dir.exists():
    fixed_count = 0
    
    for py_file in maintenance_dir.glob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if imports from core
        needs_fix = False
        if ("from core." in content or "import core." in content):
            if "sys.path.insert" not in content:
                needs_fix = True
        
        if needs_fix:
            # Add sys.path fix
            lines = content.split('\n')
            
            # Find first import
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    fix = [
                        "import sys",
                        "from pathlib import Path", 
                        "sys.path.insert(0, str(Path(__file__).parent.parent.parent))",
                        ""
                    ]
                    lines = lines[:i] + fix + lines[i:]
                    break
            
            # Write back
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ FIXED: {py_file.name}")
            fixed_count += 1
        else:
            print(f"✓  OK: {py_file.name}")
    
    if fixed_count > 0:
        print(f"\n✅ Fixed {fixed_count} scripts")
    else:
        print("\n✓  All scripts OK")
else:
    print("⚠️  scripts/maintenance/ not found")

print()

# ============================================================================
# PASO 3: Limpiar archivos duplicados/temporales
# ============================================================================

print("PASO 3: Limpiando archivos duplicados...")
print("-" * 80)

to_delete = [
    "PROCESS_ALL_EMAILS_FIXED.bat",
    "START_CONTROL_CENTER_FIXED.bat",
    "UNDO_ORGANIZATION.py",
    "SIMPLE_FIX.py",
]

deleted_count = 0
for filename in to_delete:
    file_path = ROOT / filename
    if file_path.exists():
        file_path.unlink()
        print(f"🗑️  Deleted: {filename}")
        deleted_count += 1
    else:
        print(f"✓  Not found (OK): {filename}")

if deleted_count > 0:
    print(f"\n✅ Deleted {deleted_count} unnecessary files")
else:
    print("\n✓  No unnecessary files found")

print()

# ============================================================================
# PASO 4: Verificar archivos críticos
# ============================================================================

print("PASO 4: Verificando archivos críticos...")
print("-" * 80)

critical_files = {
    "control_center.py": "Main control center",
    "run_daily_pipeline.py": "Daily automation",
    "START_CONTROL_CENTER.bat": "Launcher",
    "core/automation/email_classifier.py": "Email classifier",
    "core/copilot/interview_copilot_session_recorder.py": "Interview copilot",
    "unified_app/app.py": "Web dashboard",
}

all_ok = True
for file_path, description in critical_files.items():
    full_path = ROOT / file_path
    if full_path.exists():
        print(f"✅ {file_path:50s} ({description})")
    else:
        print(f"❌ {file_path:50s} MISSING!")
        all_ok = False

print()

# ============================================================================
# RESUMEN
# ============================================================================

print("=" * 80)
print("📊 RESUMEN DE RESTAURACIÓN")
print("=" * 80)
print()

if all_ok:
    print("✅ TODOS LOS ARCHIVOS CRÍTICOS PRESENTES")
    print()
    print("Siguiente paso:")
    print("  py scripts\\maintenance\\verify_job_status.py")
    print()
    print("Si funciona, entonces:")
    print("  .\\START_CONTROL_CENTER.bat")
else:
    print("⚠️  ALGUNOS ARCHIVOS CRÍTICOS FALTAN")
    print()
    print("Por favor revisa los archivos marcados como MISSING")

print("=" * 80)
