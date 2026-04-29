#!/usr/bin/env python3
"""
RH-IT HOME (ITC) - Auto-Apply Script
Aplica automáticamente a vacantes de https://vacantes.rh-itchome.com/

Uso:
    py scripts\itc\apply_to_job.py --job-id 262
    py scripts\itc\apply_to_job.py --job-ids 179,180,196,214
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from playwright.async_api import async_playwright
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

# Datos del CV
CV_DATA = {
    'nombre': 'Marcos Alberto',
    'apellidos': 'Alvarado de la Torre',
    'fecha_nacimiento': '1985-02-07',  # AJUSTA ESTO
    'email': os.getenv('USER_EMAIL', 'markalvati@gmail.com'),
    'telefono': os.getenv('USER_PHONE', '+523323320358'),
    'red_social': 'https://www.linkedin.com/in/marcosalvarado-it/',
    'pais': 'México',
    'estado': 'Jalisco',
    
    # Estudios
    'grado_estudios': 'Licenciatura',
    'estatus_estudios': 'Titulado',
    'area_estudios': 'Ingeniería en Sistemas',
    
    # Certificaciones
    'cert1_nombre': 'Lean Six Sigma Black Belt',
    'cert1_codigo': 'LSS-BB-2024',
    'cert1_fecha': '2024-01-15',
    
    'cert2_nombre': 'Scrum Master',
    'cert2_codigo': 'SM-2024',
    'cert2_fecha': '2024-03-20',
    
    # Skills
    'skill_primario': 'Project Manager',
    'skill_primario_nombre': 'Project Management / ERP Migrations',
    'skill_primario_experiencia': 'EXPERT +9',
    
    'skill_secundario': 'Manager',
    'skill_secundario_nombre': 'IT Management / Infrastructure',
    'skill_secundario_experiencia': 'EXPERT +9',
    
    'nivel_ingles': '3 - AVANZADO',
    
    # Status actual
    'empresa_actual': 'Freelance / Consulting',
    'tipo_contrato': '1 - NOMINA 100%',
    'prestaciones': 'IMSS, Aguinaldo, Vacaciones, PTU',
    'ingreso_actual': '65000',
    'moneda_actual': 'MX PESOS',
    'periodicidad_actual': 'Mes',
    'disponibilidad': '1 - INMEDIATA',
    'reubicacion': 'No',
    'lugar_reubicacion': '',
    
    # Expectativas
    'expectativa_ingreso': '70000',
    'moneda_expectativa': 'MX PESOS',
    'periodicidad_expectativa': 'Mes',
    'tipo_contrato_deseado': '1 - NOMINA 100%',
    
    # Referencia (opcional)
    'nombre_referencia': '',
    'email_referencia': '',
    
    # Archivos
    'foto_path': r'data\cv\Foto.jpg',  # AJUSTA ESTO
    'cv_path': r'data\cv\Alvarado Marcos.pdf'  # AJUSTA ESTO
}

async def apply_to_job(job_id: int, dry_run: bool = False):
    """Aplica a una vacante de RH-IT Home"""
    
    url = f"https://vacantes.rh-itchome.com/aplicar/{job_id}"
    print(f"\n{'='*70}")
    print(f"🎯 APLICANDO A VACANTE {job_id}")
    print(f"{'='*70}")
    print(f"URL: {url}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate
        print("🌐 Abriendo formulario...")
        await page.goto(url, wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        if dry_run:
            print("\n⏸️  DRY RUN - Presiona Enter para ver qué campos se llenarían...")
            input()
        
        print("\n📝 Llenando formulario...")
        
        # DATOS GENERALES
        await page.fill('input[name="nombre"]', CV_DATA['nombre'])
        print(f"  ✅ Nombre: {CV_DATA['nombre']}")
        
        await page.fill('input[name="apellidos"]', CV_DATA['apellidos'])
        print(f"  ✅ Apellidos: {CV_DATA['apellidos']}")
        
        await page.fill('input[name="fecha_nacimiento"]', CV_DATA['fecha_nacimiento'])
        print(f"  ✅ Fecha nacimiento: {CV_DATA['fecha_nacimiento']}")
        
        await page.fill('input[name="email"]', CV_DATA['email'])
        print(f"  ✅ Email: {CV_DATA['email']}")
        
        await page.fill('input[name="telefono"]', CV_DATA['telefono'])
        print(f"  ✅ Teléfono: {CV_DATA['telefono']}")

        # Red Social
        await page.select_option('select[name="red_social"]', CV_DATA['red_social'])
        print(f"  ✅ Red social: {CV_DATA['red_social']}")
        
        # País y Estado
        await page.select_option('select[name="pais"]', CV_DATA['pais'])
        await asyncio.sleep(0.5)
        await page.select_option('select[name="estado"]', CV_DATA['estado'])
        print(f"  ✅ Ubicación: {CV_DATA['estado']}, {CV_DATA['pais']}")
        
        # ESTUDIOS
        await page.select_option('select[name="grado_estudios"]', CV_DATA['grado_estudios'])
        await page.fill('input[name="estatus_estudios"]', CV_DATA['estatus_estudios'])
        await page.fill('input[name="area_estudios"]', CV_DATA['area_estudios'])
        print(f"  ✅ Estudios: {CV_DATA['grado_estudios']} - {CV_DATA['area_estudios']}")
        
        # CERTIFICACIONES
        if CV_DATA.get('cert1_nombre'):
            await page.fill('input[name="cert1_nombre"]', CV_DATA['cert1_nombre'])
            await page.fill('input[name="cert1_codigo"]', CV_DATA['cert1_codigo'])
            await page.fill('input[name="cert1_fecha"]', CV_DATA['cert1_fecha'])
            print(f"  ✅ Certificación 1: {CV_DATA['cert1_nombre']}")
        
        if CV_DATA.get('cert2_nombre'):
            await page.fill('input[name="cert2_nombre"]', CV_DATA['cert2_nombre'])
            await page.fill('input[name="cert2_codigo"]', CV_DATA['cert2_codigo'])
            await page.fill('input[name="cert2_fecha"]', CV_DATA['cert2_fecha'])
            print(f"  ✅ Certificación 2: {CV_DATA['cert2_nombre']}")
        
        # SKILLS
        await page.select_option('select[name="skill_primario"]', CV_DATA['skill_primario'])
        await asyncio.sleep(0.3)
        await page.fill('input[name="skill_primario_nombre"]', CV_DATA['skill_primario_nombre'])
        await page.select_option('select[name="skill_primario_exp"]', CV_DATA['skill_primario_experiencia'])
        print(f"  ✅ Skill primario: {CV_DATA['skill_primario_nombre']} ({CV_DATA['skill_primario_experiencia']})")
        
        await page.select_option('select[name="skill_secundario"]', CV_DATA['skill_secundario'])
        await asyncio.sleep(0.3)
        await page.fill('input[name="skill_secundario_nombre"]', CV_DATA['skill_secundario_nombre'])
        await page.select_option('select[name="skill_secundario_exp"]', CV_DATA['skill_secundario_experiencia'])
        print(f"  ✅ Skill secundario: {CV_DATA['skill_secundario_nombre']} ({CV_DATA['skill_secundario_experiencia']})")
        
        # Nivel de Inglés
        await page.select_option('select[name="nivel_ingles"]', CV_DATA['nivel_ingles'])
        print(f"  ✅ Nivel de inglés: {CV_DATA['nivel_ingles']}")
        
        # ESTATUS Y EXPECTATIVAS
        await page.fill('input[name="empresa_actual"]', CV_DATA['empresa_actual'])
        await page.select_option('select[name="tipo_contrato"]', CV_DATA['tipo_contrato'])
        await page.fill('input[name="prestaciones"]', CV_DATA['prestaciones'])
        print(f"  ✅ Empresa actual: {CV_DATA['empresa_actual']}")
        
        await page.fill('input[name="ingreso_actual"]', CV_DATA['ingreso_actual'])
        await page.select_option('select[name="moneda_actual"]', CV_DATA['moneda_actual'])
        await page.select_option('select[name="periodicidad_actual"]', CV_DATA['periodicidad_actual'])
        print(f"  ✅ Ingreso actual: {CV_DATA['ingreso_actual']} {CV_DATA['moneda_actual']}/{CV_DATA['periodicidad_actual']}")
        
        await page.select_option('select[name="disponibilidad"]', CV_DATA['disponibilidad'])
        print(f"  ✅ Disponibilidad: {CV_DATA['disponibilidad']}")
        
        # Reubicación
        await page.check(f'input[name="reubicacion"][value="{'Si' if CV_DATA['reubicacion'] == 'Si' else 'No'}"]')
        if CV_DATA['reubicacion'] == 'Si' and CV_DATA.get('lugar_reubicacion'):
            await page.select_option('select[name="lugar_reubicacion"]', CV_DATA['lugar_reubicacion'])
        print(f"  ✅ Reubicación: {CV_DATA['reubicacion']}")
        
        # EXPECTATIVAS
        await page.fill('input[name="expectativa_ingreso"]', CV_DATA['expectativa_ingreso'])
        await page.select_option('select[name="moneda_expectativa"]', CV_DATA['moneda_expectativa'])
        await page.select_option('select[name="periodicidad_expectativa"]', CV_DATA['periodicidad_expectativa'])
        await page.select_option('select[name="tipo_contrato_deseado"]', CV_DATA['tipo_contrato_deseado'])
        print(f"  ✅ Expectativa: {CV_DATA['expectativa_ingreso']} {CV_DATA['moneda_expectativa']}/{CV_DATA['periodicidad_expectativa']}")
        
        # Referencias (opcional)
        if CV_DATA.get('nombre_referencia'):
            await page.fill('input[name="nombre_referencia"]', CV_DATA['nombre_referencia'])
            await page.fill('input[name="email_referencia"]', CV_DATA['email_referencia'])
            print(f"  ✅ Referencia: {CV_DATA['nombre_referencia']}")

        # ARCHIVOS
        print("\n📎 Archivos...")
        
        # Foto (opcional)
        if os.path.exists(CV_DATA['foto_path']):
            await page.set_input_files('input[name="foto"]', CV_DATA['foto_path'])
            print(f"  ✅ Foto subida: {CV_DATA['foto_path']}")
        else:
            print(f"  ⚠️  Foto no encontrada: {CV_DATA['foto_path']}")
        
        # CV (requerido)
        if os.path.exists(CV_DATA['cv_path']):
            await page.set_input_files('input[name="cv"]', CV_DATA['cv_path'])
            print(f"  ✅ CV subido: {CV_DATA['cv_path']}")
        else:
            print(f"  ❌ CV no encontrado: {CV_DATA['cv_path']}")
            print("     El formulario NO se puede enviar sin CV")
            await browser.close()
            return False
        
        # Aceptar aviso de privacidad
        await page.check('input[type="checkbox"]')
        print("  ✅ Aviso de privacidad aceptado")
        
        print(f"\n{'='*70}")
        
        if dry_run:
            print("✅ DRY RUN COMPLETADO - Formulario listo pero NO enviado")
            print("   Revisa el navegador para verificar que todo esté correcto")
            print("\nPresiona Enter para cerrar...")
            input()
        else:
            # Enviar formulario
            print("📤 ¿Enviar aplicación? (y/n): ", end='')
            confirm = input().lower()
            
            if confirm == 'y':
                # Click en botón Enviar
                await page.click('a:has-text("Enviar")')
                await asyncio.sleep(3)
                
                print("\n✅ APLICACIÓN ENVIADA!")
                print(f"   Vacante {job_id} - {url}")
            else:
                print("\n⏭️  Aplicación cancelada por el usuario")
        
        print(f"{'='*70}\n")
        
        await browser.close()
        return True

async def apply_to_multiple_jobs(job_ids: list, dry_run: bool = False):
    """Aplica a múltiples vacantes"""
    print(f"\n{'='*70}")
    print(f"🎯 APLICANDO A {len(job_ids)} VACANTES")
    print(f"{'='*70}")
    print(f"IDs: {', '.join(map(str, job_ids))}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    results = []
    for i, job_id in enumerate(job_ids, 1):
        print(f"\n[{i}/{len(job_ids)}] Procesando vacante {job_id}...")
        success = await apply_to_job(job_id, dry_run)
        results.append({'job_id': job_id, 'success': success})
        
        if i < len(job_ids):
            print("\n⏱️  Esperando 5 segundos antes de la siguiente...")
            await asyncio.sleep(5)
    
    # Resumen
    print(f"\n{'='*70}")
    print("📊 RESUMEN")
    print(f"{'='*70}")
    for r in results:
        status = "✅ ENVIADA" if r['success'] else "❌ FALLIDA"
        print(f"  Vacante {r['job_id']}: {status}")
    print(f"{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Auto-apply a vacantes de RH-IT Home')
    parser.add_argument('--job-id', type=int, help='ID de una vacante individual')
    parser.add_argument('--job-ids', type=str, help='IDs separados por coma (ej: 179,180,196)')
    parser.add_argument('--dry-run', action='store_true', help='Modo prueba (no envía)')
    
    args = parser.parse_args()
    
    if args.job_id:
        asyncio.run(apply_to_job(args.job_id, args.dry_run))
    elif args.job_ids:
        job_ids = [int(x.strip()) for x in args.job_ids.split(',')]
        asyncio.run(apply_to_multiple_jobs(job_ids, args.dry_run))
    else:
        print("❌ Error: Debes especificar --job-id o --job-ids")
        print("\nEjemplos:")
        print("  py scripts\\itc\\apply_to_job.py --job-id 262 --dry-run")
        print("  py scripts\\itc\\apply_to_job.py --job-ids 179,180,196,214")

if __name__ == "__main__":
    main()
