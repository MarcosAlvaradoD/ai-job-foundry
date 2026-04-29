#!/usr/bin/env python3
"""
FIX VERIFICACIÓN DE JOBS EXPIRADOS
Actualiza run_daily_pipeline.py para verificar más jobs correctamente

Este script hace 3 cambios:
1. Aumenta límite de 5 → 100 jobs
2. Elimina filtro restrictivo de Status='New' solo
3. Elimina filtro de FIT>=7 (verifica TODOS)

ANTES:
  - Solo 5 jobs máximo
  - Solo Status='New' + FIT>=7
  
DESPUÉS:
  - 100 jobs máximo
  - Todos los Status excepto Applied/Rejected/Expired/Interview
  - Todos los FIT scores
"""
import sys
from pathlib import Path

# Rutas
project_root = Path(__file__).parent
pipeline_file = project_root / "run_daily_pipeline.py"
backup_file = project_root / "run_daily_pipeline.py.BEFORE_VERIFY_FIX"

def apply_fix():
    print("="*70)
    print("🔧 FIX VERIFICACIÓN DE JOBS EXPIRADOS")
    print("="*70)
    print()
    
    # Verificar que existe el archivo
    if not pipeline_file.exists():
        print(f"❌ ERROR: No se encontró {pipeline_file}")
        return False
    
    # Crear backup
    print(f"1️⃣  Creando backup...")
    print(f"   {backup_file}")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print(f"   ✅ Backup creado\n")
    
    # Aplicar cambios
    print(f"2️⃣  Aplicando fix...")
    
    new_content = original_content
    
    # Cambio 1: Aumentar límite de 5 a 100
    old_line_1 = "verifier.verify_jobs(jobs_to_verify[:5], rate_limit_seconds=3)  # Limit to 5 to save time"
    new_line_1 = "verifier.verify_jobs(jobs_to_verify[:100], rate_limit_seconds=3)  # Increased limit"
    
    if old_line_1 in new_content:
        new_content = new_content.replace(old_line_1, new_line_1)
        print(f"   ✅ Cambio 1: Límite 5 → 100 jobs")
    else:
        print(f"   ⚠️  Advertencia: No se encontró línea exacta para Cambio 1")
    
    # Cambio 2 y 3: Reemplazar todo el bloque de filtros
    old_block = """        # Get jobs to verify (only New status, FIT >= 7, not expired by date)
        jobs_to_verify = []
        for job in jobs:
            status = job.get('Status', '')
            fit_score = job.get('FitScore', 0)
            
            if status == 'New':
                try:
                    if int(fit_score) >= 7:
                        jobs_to_verify.append(job)
                except Exception:
                    pass"""
    
    new_block = """        # Get jobs to verify (all status except final ones, all FIT scores)
        jobs_to_verify = []
        final_statuses = ['Applied', 'Rejected', 'Expired', 'Interview']
        
        for job in jobs:
            status = job.get('Status', '')
            
            # Skip final statuses (ya no necesitan verificación)
            if status in final_statuses:
                continue
            
            # Agregar job para verificación (SIN filtro de FIT)
            jobs_to_verify.append(job)"""
    
    if old_block in new_content:
        new_content = new_content.replace(old_block, new_block)
        print(f"   ✅ Cambio 2: Filtro Status='New' eliminado")
        print(f"   ✅ Cambio 3: Filtro FIT>=7 eliminado")
    else:
        print(f"   ⚠️  Advertencia: No se encontró bloque exacto para Cambio 2-3")
        print(f"   💡 Aplicando cambio alternativo...")
        
        # Try individual lines
        old_status_check = "            if status == 'New':"
        new_status_check = "            if status not in ['Applied', 'Rejected', 'Expired', 'Interview']:"
        
        if old_status_check in new_content:
            new_content = new_content.replace(old_status_check, new_status_check)
            print(f"   ✅ Status check actualizado")
    
    # Guardar archivo modificado
    print(f"\n3️⃣  Guardando cambios...")
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✅ Archivo actualizado: {pipeline_file}\n")
    
    # Resumen
    print("="*70)
    print("📊 RESUMEN DE CAMBIOS")
    print("="*70)
    print(f"✅ Backup creado:     {backup_file.name}")
    print(f"✅ Archivo modificado: {pipeline_file.name}")
    print()
    print("CAMBIOS APLICADOS:")
    print("  1. Límite de verificación: 5 → 100 jobs")
    print("  2. Filtro de Status: 'New' → todos excepto finales")
    print("  3. Filtro de FIT: eliminado (verifica todos)")
    print("="*70)
    print()
    
    # Instrucciones de test
    print("🧪 SIGUIENTE PASO - TEST:")
    print()
    print("  py run_daily_pipeline.py --expire")
    print()
    print("ESPERADO:")
    print("  - Debe verificar más de 5 jobs")
    print("  - Debe verificar jobs con Status != 'New'")
    print("  - Debe usar Playwright para verificación real")
    print()
    print("Si algo falla, restaura con:")
    print(f"  copy {backup_file.name} run_daily_pipeline.py")
    print()
    
    return True

def main():
    success = apply_fix()
    
    if success:
        print("✅ FIX APLICADO EXITOSAMENTE\n")
        sys.exit(0)
    else:
        print("❌ ERROR AL APLICAR FIX\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
