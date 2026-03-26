#!/usr/bin/env python3
"""
TEST DEL NUEVO PARSER DE GLASSDOOR
Prueba el parser mejorado con el HTML guardado
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.automation.job_bulletin_processor import JobBulletinProcessor

def main():
    print("\n" + "="*70)
    print("🧪 TEST DEL NUEVO PARSER DE GLASSDOOR")
    print("="*70 + "\n")
    
    # Leer el HTML guardado
    html_file = "GLASSDOOR_EMAIL_SAMPLE.html"
    
    if not Path(html_file).exists():
        print(f"❌ No se encontró {html_file}")
        print("   Ejecuta primero: py ANALIZAR_EMAIL_GLASSDOOR.py")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📄 HTML cargado: {len(html_content)} caracteres\n")
    
    # Crear procesador y extraer jobs
    processor = JobBulletinProcessor()
    jobs = processor.extract_glassdoor_jobs(html_content)
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Jobs extraídos: {len(jobs)}")
    print()
    
    if jobs:
        for i, job in enumerate(jobs, 1):
            print(f"📌 Job #{i}:")
            print(f"   Título: {job.get('Role', 'N/A')}")
            print(f"   Empresa: {job.get('Company', 'N/A')}")
            print(f"   Location: {job.get('Location', 'N/A')}")
            print(f"   Salario: {job.get('Comp', 'N/A')}")
            print(f"   URL: {job.get('ApplyURL', 'N/A')}")
            print()
    else:
        print("❌ No se extrajeron jobs")
        print("   Revisa los patrones de regex")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
