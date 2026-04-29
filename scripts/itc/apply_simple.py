#!/usr/bin/env python3
"""
RH-IT HOME - Auto-Apply SIMPLE VERSION
Usa JavaScript para llenar campos (más confiable)
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
    'nombre': 'Marcos Alberto',
    'apellidos': 'Alvarado de la Torre',
    'fecha_nacimiento': '15/06/1985',
    'email': os.getenv('USER_EMAIL', 'markalvati@gmail.com'),
    'telefono': os.getenv('USER_PHONE', '+523323320358'),
    'foto_path': r'data\cv\Foto.jpg',
    'cv_path': r'data\cv\Alvarado Marcos.pdf'
}

async def fill_form_with_js(page):
    """Llena el formulario usando JavaScript"""
    
    print("\n📝 Llenando formulario con JavaScript...")
    
    # Helper function para llenar inputs
    fill_js = """
    function fillField(selector, value) {
        const elem = document.querySelector(selector);
        if (elem) {
            elem.value = value;
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
        return false;
    }
    """
    
    await page.evaluate(fill_js)
    
    # Llenar campos uno por uno
    fields = {
        # Datos generales - buscar por placeholder o label text
        "input:has-text('Nombre')": CV_DATA['nombre'],
        "input[placeholder*='Nombre']": CV_DATA['nombre'],
        "input[placeholder*='Apellidos']": CV_DATA['apellidos'],
        "input[type='email']": CV_DATA['email'],
        "input[type='tel']": CV_DATA['telefono'],
        "input[type='date']": CV_DATA['fecha_nacimiento'],
    }
    
    for selector, value in fields.items():
        try:
            await page.fill(selector, value, timeout=2000)
            print(f"  ✅ {selector[:30]}... = {value}")
        except Exception:
            print(f"  ⚠️  {selector[:30]}... - no encontrado")
    
    await asyncio.sleep(1)

async def apply_with_simple_selectors(job_id: int, dry_run: bool = False):
    """Versión simplificada"""
    
    url = f"https://vacantes.rh-itchome.com/aplicar/{job_id}"
    print(f"\n{'='*70}")
    print(f"🎯 APLICANDO A VACANTE {job_id}")
    print(f"{'='*70}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("🌐 Abriendo formulario...")
        await page.goto(url, wait_until='domcontentloaded')
        await asyncio.sleep(3)
        
        # Llenar con JS
        await fill_form_with_js(page)
        
        # Subir archivos
        print("\n📎 Subiendo archivos...")
        
        try:
            # Buscar input de CV (último input file generalmente)
            file_inputs = await page.query_selector_all('input[type="file"]')
            
            if len(file_inputs) >= 2:
                # Primer input = Foto
                if os.path.exists(CV_DATA['foto_path']):
                    await file_inputs[0].set_input_files(CV_DATA['foto_path'])
                    print(f"  ✅ Foto subida")
                
                # Segundo input = CV
                if os.path.exists(CV_DATA['cv_path']):
                    await file_inputs[1].set_input_files(CV_DATA['cv_path'])
                    print(f"  ✅ CV subido")
                else:
                    print(f"  ❌ CV no encontrado: {CV_DATA['cv_path']}")
            
        except Exception as e:
            print(f"  ⚠️  Error subiendo archivos: {e}")
        
        print(f"\n{'='*70}")
        print("⏸️  REVISA EL NAVEGADOR")
        print("   El resto debes llenarlo MANUALMENTE")
        print("   (selectores, checkboxes, etc)")
        print(f"{'='*70}\n")
        
        input("Presiona Enter cuando termines de llenar manualmente...")
        
        if not dry_run:
            confirm = input("¿Enviar aplicación? (y/n): ").lower()
            if confirm == 'y':
                print("✅ Enviando...")
                # Buscar botón Enviar
                await page.click('a:has-text("Enviar")')
                await asyncio.sleep(3)
                print("✅ APLICACIÓN ENVIADA")
            else:
                print("⏭️  Cancelado")
        
        await browser.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job-id', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    asyncio.run(apply_with_simple_selectors(args.job_id, args.dry_run))

if __name__ == "__main__":
    main()
