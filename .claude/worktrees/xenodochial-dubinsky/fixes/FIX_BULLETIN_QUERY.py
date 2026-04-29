#!/usr/bin/env python3
"""
FIX BULLETINS PROCESSOR
Corrige la query de Gmail para encontrar los boletines correctamente

Problema: Boletines están en INBOX/CATEGORY_UPDATES, no en JOBS/Inbound
Solución: Cambiar query para buscar por remitente en lugar de etiqueta
"""
import sys
from pathlib import Path

def fix_bulletin_processor():
    """Fix the Gmail query in job_bulletin_processor.py"""
    
    processor_file = Path("core/automation/job_bulletin_processor.py")
    
    if not processor_file.exists():
        print("❌ job_bulletin_processor.py no encontrado")
        return False
    
    # Read current content
    with open(processor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the query
    old_query = "query = 'label:JOBS/Inbound newer_than:60d'"
    
    new_query = """query = 'from:(noreply@glassdoor.com OR jobs-noreply@linkedin.com OR noreply@indeed.com) newer_than:30d'"""
    
    if old_query not in content:
        print("⚠️  La query no coincide exactamente")
        print("⚠️  Puede que ya esté modificada")
        
        # Show current query
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "query = " in line and "newer_than" in line:
                print(f"\n📝 Query actual (línea {i+1}):")
                print(f"   {line.strip()}")
        return False
    
    # Replace query
    new_content = content.replace(old_query, new_query)
    
    # Backup original
    backup_file = Path("core/automation/job_bulletin_processor.py.backup_query")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Backup creado: {backup_file}")
    
    # Write new content
    with open(processor_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Bulletin processor actualizado")
    print("\n📋 Cambio realizado:")
    print("   ANTES: label:JOBS/Inbound newer_than:60d")
    print("   DESPUÉS: from:(glassdoor OR linkedin OR indeed) newer_than:30d")
    print("\n💡 Ahora busca directamente por remitente, sin depender de etiquetas")
    
    return True

def main():
    print("="*70)
    print("🔧 FIX BULLETIN PROCESSOR")
    print("="*70)
    print("Corrigiendo query de Gmail para encontrar boletines...\n")
    
    success = fix_bulletin_processor()
    
    print("\n" + "="*70)
    if success:
        print("✅ FIX APLICADO EXITOSAMENTE")
        print("="*70)
        print("\n💡 Siguiente paso: Probar el processor")
        print("   Comando: py core\\automation\\job_bulletin_processor.py")
        print("\n📧 Esto debería encontrar los boletines de:")
        print("   - Glassdoor (3 boletines encontrados hoy)")
        print("   - LinkedIn (1 boletín encontrado hoy)")
        print("   - Indeed (cuando lleguen)")
    else:
        print("❌ FIX NO APLICADO")
        print("="*70)
        print("\n💡 Revisar manualmente job_bulletin_processor.py")
    
    print()

if __name__ == '__main__':
    main()
