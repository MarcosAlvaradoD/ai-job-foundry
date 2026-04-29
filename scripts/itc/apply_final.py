#!/usr/bin/env python3
"""
RH-IT HOME - Auto-Apply FINAL VERSION
Usa los IDs correctos detectados por debug_form.py
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

CV_DATA = {
    # Datos generales
    'nombre': 'Marcos Alberto',
    'apellidos': 'Alvarado de la Torre',
    'fecha_nacimiento': '1985-02-07',  # YYYY-MM-DD (formato para input type="date")
    'email': os.getenv('USER_EMAIL', 'markalvati@gmail.com'),
    'telefono': os.getenv('USER_PHONE', '+523323320358'),
    
    # Selects (valores exactos)
    'red_social': 'LINKEDIN',
    'pais': 'México',
    'estado': 'Jalisco',
    
    # Estudios
    'grado_estudio': 'Licenciatura',
    'estatus_estudio': 'Titulado',
    'area_estudio': 'Informática',  # Valor EXACTO del dropdown (ver foto)
    
    # Certificaciones
    'cert1_nombre': 'Lean Six Sigma Black Belt',
    'cert1_codigo': 'LSS-BB-2024',
    'cert1_fecha': '2024-01-15',  # YYYY-MM-DD
    
    'cert2_nombre': 'Scrum Master Certification',
    'cert2_codigo': 'SM-PSM-2024',
    'cert2_fecha': '2024-03-20',  # YYYY-MM-DD
    
    # Skills (valores del dropdown)
    'skill_primario_padre': 'Project Manager',
    'skill_primario': 'PM / ERP Migrations',  # Ajustar según opciones
    'experiencia_primario': 'EXPERT +9',
    
    'skill_secundario_padre': 'Manager',
    'skill_secundario': 'IT Management',
    'experiencia_secundario': 'EXPERT +9',
    
    'nivel_ingles': '3 - AVANZADO',
    
    # Status actual
    'empresa_actual': 'Freelance Consulting',
    'tipo_contrato_actual': '4 - FACTURACION DE SERVICIOS',
    'prestaciones': 'IMSS, Aguinaldo, Vacaciones, PTU',
    'ingreso_actual': '65000',
    'moneda_actual': 'MX PESOS',
    'periodicidad_actual': 'Mes',
    'disponibilidad': '1 - INMEDIATA',
    'reubicacion': 'No',
    
    # Expectativas
    'ingreso_expectativa': '75000',
    'moneda_expectativa': 'MX PESOS',
    'periodicidad_expectativa': 'Mes',
    'tipo_contrato_expectativa': '1 - NOMINA 100%',
    
    # Referencias (opcional)
    'referencia_nombre': '',
    'referencia_email': '',
    
    # Archivos
    'foto_path': r'data\cv\Foto.jpg',
    'cv_path': r'data\cv\Alvarado Marcos.pdf'
}

async def fill_field(page, id_selector, value, field_name):
    """Helper para llenar campo con manejo de errores"""
    try:
        await page.fill(f'#{id_selector}', str(value), timeout=3000)
        print(f"  ✅ {field_name}: {value}")
        return True
    except Exception as e:
        print(f"  ⚠️  {field_name}: Error - {str(e)[:50]}")
        return False

async def select_option(page, id_selector, value, field_name):
    """Helper para seleccionar opción con manejo de errores"""
    try:
        # Intentar por texto visible
        await page.select_option(f'#{id_selector}', label=value, timeout=3000)
        print(f"  ✅ {field_name}: {value}")
        return True
    except Exception:
        try:
            # Intentar por value
            await page.select_option(f'#{id_selector}', value=value, timeout=3000)
            print(f"  ✅ {field_name}: {value}")
            return True
        except Exception as e:
            print(f"  ⚠️  {field_name}: No se pudo seleccionar '{value}'")
            return False

async def apply_to_job(job_id: int, dry_run: bool = False):
    """Aplica a vacante con los IDs correctos"""
    
    url = f"https://vacantes.rh-itchome.com/aplicar/{job_id}"
    print(f"\n{'='*70}")
    print(f"🎯 APLICANDO A VACANTE {job_id}")
    print(f"{'='*70}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"URL: {url}")
    print(f"{'='*70}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("🌐 Abriendo formulario...")
        await page.goto(url, wait_until='domcontentloaded')
        await asyncio.sleep(3)
        
        print("\n📝 DATOS GENERALES")
        print("-" * 70)
        await fill_field(page, 'txtNombre', CV_DATA['nombre'], 'Nombre')
        await fill_field(page, 'txtApellidos', CV_DATA['apellidos'], 'Apellidos')
        await fill_field(page, 'dtmNacimiento', CV_DATA['fecha_nacimiento'], 'Fecha nacimiento')
        await fill_field(page, 'txtEmail', CV_DATA['email'], 'Email')
        await fill_field(page, 'txtCelular', CV_DATA['telefono'], 'Teléfono')
        
        await select_option(page, 'lstRedSocial', CV_DATA['red_social'], 'Red Social')
        await select_option(page, 'lstPais', CV_DATA['pais'], 'País')
        await asyncio.sleep(0.5)
        await select_option(page, 'lstEstado', CV_DATA['estado'], 'Estado')
        
        print("\n📚 ESTUDIOS")
        print("-" * 70)
        await select_option(page, 'lstGradoEstudio', CV_DATA['grado_estudio'], 'Grado de estudios')
        await select_option(page, 'lstEstatusEstudio', CV_DATA['estatus_estudio'], 'Estatus')
        await select_option(page, 'lstAreaEstudio', CV_DATA['area_estudio'], 'Área')
        
        print("\n🏆 CERTIFICACIONES")
        print("-" * 70)
        if CV_DATA.get('cert1_nombre'):
            await fill_field(page, 'txtCertiNombre_1', CV_DATA['cert1_nombre'], 'Certificación 1')
            await fill_field(page, 'txtCertiCodigo_1', CV_DATA['cert1_codigo'], 'Código 1')
            await fill_field(page, 'txtCertiFecha_1', CV_DATA['cert1_fecha'], 'Fecha 1')
        
        if CV_DATA.get('cert2_nombre'):
            await fill_field(page, 'txtCertiNombre_2', CV_DATA['cert2_nombre'], 'Certificación 2')
            await fill_field(page, 'txtCertiCodigo_2', CV_DATA['cert2_codigo'], 'Código 2')
            await fill_field(page, 'txtCertiFecha_2', CV_DATA['cert2_fecha'], 'Fecha 2')
        
        print("\n💼 SKILLS")
        print("-" * 70)
        await select_option(page, 'lstSkillPrimarioPadre', CV_DATA['skill_primario_padre'], 'Skill primario (padre)')
        await asyncio.sleep(0.5)
        # El segundo dropdown se llena solo basado en el padre
        await select_option(page, 'lstExperienciaPrimario', CV_DATA['experiencia_primario'], 'Experiencia primaria')
        
        await select_option(page, 'lstSkillSecundarioPadre', CV_DATA['skill_secundario_padre'], 'Skill secundario (padre)')
        await asyncio.sleep(0.5)
        await select_option(page, 'lstExperienciaSecundario', CV_DATA['experiencia_secundario'], 'Experiencia secundaria')
        
        await select_option(page, 'lstIngles', CV_DATA['nivel_ingles'], 'Nivel de inglés')

        print("\n💰 ESTATUS Y EXPECTATIVAS")
        print("-" * 70)
        await fill_field(page, 'txtEmpresaActual', CV_DATA['empresa_actual'], 'Empresa actual')
        await select_option(page, 'lstTipoContratoActual', CV_DATA['tipo_contrato_actual'], 'Tipo contrato actual')
        await fill_field(page, 'txtPrestaciones', CV_DATA['prestaciones'], 'Prestaciones')
        await fill_field(page, 'numIngresoActual', CV_DATA['ingreso_actual'], 'Ingreso actual')
        await select_option(page, 'lstMonedaIA', CV_DATA['moneda_actual'], 'Moneda actual')
        await select_option(page, 'lstPeriodicidadIA', CV_DATA['periodicidad_actual'], 'Periodicidad actual')
        
        await select_option(page, 'lstDisponibilidad', CV_DATA['disponibilidad'], 'Disponibilidad')
        await select_option(page, 'lstDispuesto', CV_DATA['reubicacion'], 'Reubicación')
        
        # Expectativas
        await fill_field(page, 'numIngresoExpectativa', CV_DATA['ingreso_expectativa'], 'Expectativa ingreso')
        await select_option(page, 'lstMonedaEI', CV_DATA['moneda_expectativa'], 'Moneda expectativa')
        await select_option(page, 'lstPeriodicidadEI', CV_DATA['periodicidad_expectativa'], 'Periodicidad expectativa')
        await select_option(page, 'lstTipoContratoEI', CV_DATA['tipo_contrato_expectativa'], 'Tipo contrato deseado')
        
        # Referencias (opcional)
        if CV_DATA.get('referencia_nombre'):
            await fill_field(page, 'txtReferenciaNombre', CV_DATA['referencia_nombre'], 'Referencia nombre')
            await fill_field(page, 'txtReferenciaEmail', CV_DATA['referencia_email'], 'Referencia email')
        
        print("\n📎 ARCHIVOS")
        print("-" * 70)
        try:
            file_inputs = await page.query_selector_all('input[type="file"]')
            
            if len(file_inputs) >= 2:
                # Foto
                if os.path.exists(CV_DATA['foto_path']):
                    await file_inputs[0].set_input_files(CV_DATA['foto_path'])
                    print(f"  ✅ Foto subida: {CV_DATA['foto_path']}")
                else:
                    print(f"  ⚠️  Foto no encontrada (opcional)")
                
                # CV
                if os.path.exists(CV_DATA['cv_path']):
                    await file_inputs[1].set_input_files(CV_DATA['cv_path'])
                    print(f"  ✅ CV subido: {CV_DATA['cv_path']}")
                else:
                    print(f"  ❌ CV no encontrado: {CV_DATA['cv_path']}")
                    print("     FORMULARIO NO SE PUEDE ENVIAR SIN CV")
                    await browser.close()
                    return False
        except Exception as e:
            print(f"  ⚠️  Error subiendo archivos: {e}")
        
        print(f"\n{'='*70}")
        print("✅ FORMULARIO COMPLETADO (99%)")
        print(f"{'='*70}\n")
        
        # PAUSA PARA CHECKBOX MANUAL
        print("📋 ACCIÓN REQUERIDA:")
        print("   1. Busca el checkbox 'Aviso de Privacidad' al final del formulario")
        print("   2. MÁRCALO manualmente (1 click)")
        print("   3. Regresa aquí y presiona Enter")
        print(f"\n{'='*70}\n")
        
        if dry_run:
            print("🔍 DRY RUN - El formulario NO se enviará")
            input("Presiona Enter para cerrar...")
        else:
            input("⏸️  Presiona Enter cuando HAYAS MARCADO el checkbox de privacidad...")
            
            print(f"\n{'='*70}")
            print("📤 ¿ENVIAR APLICACIÓN?")
            print(f"{'='*70}")
            print(f"Vacante: {job_id}")
            print(f"URL: {url}")
            print(f"{'='*70}\n")
            
            confirm = input("Escribe 'y' para ENVIAR, 'n' para cancelar: ").lower()
            
            if confirm == 'y':
                print("\n📤 Enviando aplicación...")
                try:
                    # Hacer scroll hacia el botón Enviar
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1)
                    
                    # Click en botón Enviar
                    await page.click('a:has-text("Enviar")', timeout=5000)
                    
                    print("   ✅ Click en 'Enviar' ejecutado")
                    print("   ⏳ Esperando confirmación...")
                    
                    # Esperar a que cambie la URL o aparezca confirmación
                    await asyncio.sleep(5)
                    
                    current_url = page.url
                    print(f"\n   📍 URL después de enviar: {current_url}")
                    
                    if current_url != url:
                        print("\n   ✅ ¡APLICACIÓN ENVIADA EXITOSAMENTE!")
                    else:
                        print("\n   ⚠️  La URL no cambió - verifica en el navegador")
                        input("   Presiona Enter para continuar...")
                    
                except Exception as e:
                    print(f"\n   ⚠️  Error al hacer click en Enviar: {str(e)[:80]}")
                    print("   Intenta hacer click MANUALMENTE en el botón 'Enviar'")
                    input("\n   Presiona Enter cuando hayas enviado manualmente...")
                
                print(f"\n{'='*70}")
                print("✅ PROCESO COMPLETADO")
                print(f"{'='*70}\n")
            else:
                print("\n⏭️  Aplicación cancelada por el usuario")
                print(f"{'='*70}\n")
        
        print(f"\n{'='*70}\n")
        await browser.close()
        return True

async def apply_to_multiple_jobs(job_ids: list, dry_run: bool = False):
    """Aplica a múltiples vacantes con pausa entre cada una"""
    print(f"\n{'='*70}")
    print(f"🎯 APLICACIÓN MASIVA - {len(job_ids)} VACANTES")
    print(f"{'='*70}")
    print(f"IDs: {', '.join(map(str, job_ids))}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    if not dry_run:
        confirm = input(f"¿Confirmas aplicar a {len(job_ids)} vacantes? (y/n): ").lower()
        if confirm != 'y':
            print("\n❌ Operación cancelada")
            return
    
    results = []
    for i, job_id in enumerate(job_ids, 1):
        print(f"\n{'🔵'*35}")
        print(f"     VACANTE {i}/{len(job_ids)} - ID: {job_id}")
        print(f"{'🔵'*35}\n")
        
        success = await apply_to_job(job_id, dry_run)
        results.append({'job_id': job_id, 'success': success})
        
        if i < len(job_ids):
            print(f"\n{'⏱️ '*35}")
            print(f"  Esperando 10 segundos antes de la siguiente vacante...")
            print(f"  (Puedes presionar Ctrl+C para cancelar)")
            print(f"{'⏱️ '*35}\n")
            
            try:
                await asyncio.sleep(10)
            except KeyboardInterrupt:
                print("\n\n⚠️  Proceso interrumpido por el usuario")
                break
    
    # Resumen final
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN DE APLICACIONES")
    print(f"{'='*70}")
    print(f"Total procesadas: {len(results)}/{len(job_ids)}")
    print(f"{'='*70}\n")
    
    for r in results:
        status = "✅ ENVIADA" if r['success'] else "❌ FALLIDA"
        print(f"  Vacante {r['job_id']}: {status}")
    
    print(f"\n{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Auto-apply RH-IT Home - VERSIÓN FINAL')
    parser.add_argument('--job-id', type=int, help='ID de vacante individual')
    parser.add_argument('--job-ids', type=str, help='IDs separados por coma')
    parser.add_argument('--dry-run', action='store_true', help='Modo prueba')
    
    args = parser.parse_args()
    
    if args.job_id:
        asyncio.run(apply_to_job(args.job_id, args.dry_run))
    elif args.job_ids:
        job_ids = [int(x.strip()) for x in args.job_ids.split(',')]
        asyncio.run(apply_to_multiple_jobs(job_ids, args.dry_run))
    else:
        print("❌ Error: Especifica --job-id o --job-ids")
        print("\nEjemplos:")
        print("  py scripts\\itc\\apply_final.py --job-id 262 --dry-run")
        print("  py scripts\\itc\\apply_final.py --job-ids 262,214,218")

if __name__ == "__main__":
    main()
