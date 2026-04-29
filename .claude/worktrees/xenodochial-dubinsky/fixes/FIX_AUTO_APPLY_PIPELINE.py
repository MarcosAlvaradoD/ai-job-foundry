#!/usr/bin/env python3
"""
FIX AUTO-APPLY PIPELINE
Conecta el módulo Auto-Apply al pipeline principal

Problema: run_daily_pipeline.py tiene auto-apply como TODO
Solución: Integrar core/automation/run_auto_apply.py
"""
import sys
from pathlib import Path

def fix_auto_apply_integration():
    """Fix the auto-apply integration in run_daily_pipeline.py"""
    
    pipeline_file = Path("run_daily_pipeline.py")
    
    if not pipeline_file.exists():
        print("❌ run_daily_pipeline.py no encontrado")
        return False
    
    # Read current content
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the auto_apply function
    old_function = '''def run_auto_apply(dry_run: bool = True):
    """Step 3: Auto-apply to high-fit jobs"""
    mode = "DRY RUN" if dry_run else "LIVE"
    log(f"STEP 3: Auto-apply ({mode})...", "INFO")
    
    if dry_run:
        log("Dry run mode - no real applications", "WARN")
    
    try:
        # TODO: Import auto-apply module when ready
        log("Auto-apply module not implemented yet", "WARN")
        return True
    except Exception as e:
        log(f"Auto-apply failed: {e}", "ERROR")
        return False'''
    
    new_function = '''def run_auto_apply(dry_run: bool = True):
    """Step 3: Auto-apply to high-fit jobs"""
    mode = "DRY RUN" if dry_run else "LIVE"
    log(f"STEP 3: Auto-apply ({mode})...", "INFO")
    
    if dry_run:
        log("Dry run mode - no real applications", "WARN")
    
    try:
        # Import auto-apply module
        import asyncio
        from core.automation.auto_apply_linkedin import LinkedInAutoApplier
        
        # Run auto-applier
        applier = LinkedInAutoApplier(dry_run=dry_run)
        
        # Get high-fit jobs (FIT >= 7, Status = New)
        from core.sheets.sheet_manager import SheetManager
        sm = SheetManager()
        jobs = sm.get_all_jobs()
        
        high_fit_jobs = [
            j for j in jobs 
            if j.get('Status') == 'New' 
            and int(j.get('FitScore', '0').split('/')[0] if '/' in str(j.get('FitScore', '0')) else j.get('FitScore', 0)) >= 7
        ]
        
        if not high_fit_jobs:
            log("No high-fit jobs to apply", "INFO")
            return True
        
        log(f"Found {len(high_fit_jobs)} high-fit jobs to process", "INFO")
        
        # Run async applier
        asyncio.run(applier.process_jobs(high_fit_jobs[:10]))  # Limit to 10 per run
        
        log(f"Auto-apply completed: {applier.stats}", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Auto-apply failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False'''
    
    # Check if function exists
    if old_function not in content:
        print("⚠️  La función run_auto_apply no coincide exactamente")
        print("⚠️  Puede que ya esté modificada o tenga cambios")
        
        # Try to find the function location
        if "def run_auto_apply" in content:
            print("\n📝 Función actual encontrada. Mostrando contexto:\n")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "def run_auto_apply" in line:
                    # Show 20 lines around the function
                    start = max(0, i-2)
                    end = min(len(lines), i+20)
                    print('\n'.join(f"{j:3d}: {lines[j]}" for j in range(start, end)))
                    break
        return False
    
    # Replace function
    new_content = content.replace(old_function, new_function)
    
    # Backup original
    backup_file = Path("run_daily_pipeline.py.backup_autoapply")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Backup creado: {backup_file}")
    
    # Write new content
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Pipeline actualizado exitosamente")
    print("\n📋 Cambios realizados:")
    print("   - Importación de LinkedInAutoApplier")
    print("   - Conexión con SheetManager para obtener jobs")
    print("   - Procesamiento de hasta 10 jobs high-fit por ejecución")
    print("   - Soporte para dry-run y live mode")
    
    return True

def main():
    print("="*70)
    print("🔧 FIX AUTO-APPLY PIPELINE")
    print("="*70)
    print("Conectando módulo Auto-Apply al pipeline principal...\n")
    
    success = fix_auto_apply_integration()
    
    print("\n" + "="*70)
    if success:
        print("✅ FIX APLICADO EXITOSAMENTE")
        print("="*70)
        print("\n💡 Siguiente paso: Probar el pipeline")
        print("   Comando: py run_daily_pipeline.py --apply --dry-run")
        print("\n⚠️  IMPORTANTE: El auto-apply requiere:")
        print("   1. LinkedIn abierto y con sesión activa")
        print("   2. Playwright instalado: py -m playwright install chromium")
        print("   3. Jobs con FitScore >= 7 y Status = New")
    else:
        print("❌ FIX NO APLICADO")
        print("="*70)
        print("\n💡 Revisar manualmente run_daily_pipeline.py")
        print("   La función run_auto_apply() puede tener cambios diferentes")
    
    print()

if __name__ == '__main__':
    main()
