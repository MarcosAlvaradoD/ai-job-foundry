#!/usr/bin/env python3
"""
AI JOB FOUNDRY - AUTO FORM FILLER
Llena formularios de aplicación automáticamente

Uso:
    py boards\auto_fill_application.py --url "https://vacantes.rh-itchome.com/aplicar/262" --dry-run
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from playwright.async_api import async_playwright
import argparse
from core.utils.llm_client import LLMClient
from dotenv import load_dotenv
import os

load_dotenv()

class AutoFormFiller:
    def __init__(self, url: str, dry_run: bool = True):
        self.url = url
        self.dry_run = dry_run
        self.llm_client = LLMClient()
        self.cv_data = self._load_cv_data()
    
    def _load_cv_data(self) -> dict:
        return {
            'nombre_completo': 'Marcos Alberto Alvarado de la Torre',
            'email': os.getenv('USER_EMAIL', ''),
            'telefono': os.getenv('USER_PHONE', ''),
            'ciudad': 'Guadalajara',
            'anos_experiencia': '10+',
            'nivel_ingles': 'Avanzado',
            'expectativa_salarial': '75,000 - 85,000 MXN',
            'perfil': 'PM/IT Manager 10+ años: ERP migrations, ETL, LATAM projects'
        }

    async def extract_form_fields(self, page) -> list:
        """Extrae TODOS los campos del formulario"""
        print("\n📋 Extrayendo campos del formulario...")
        fields = []
        inputs = await page.query_selector_all('input, select, textarea')
        
        for input_elem in inputs:
            try:
                tag_name = await input_elem.evaluate('el => el.tagName.toLowerCase()')
                field_type = await input_elem.get_attribute('type') or tag_name
                field_name = await input_elem.get_attribute('name') or await input_elem.get_attribute('id') or 'unknown'
                field_required = await input_elem.get_attribute('required') is not None
                
                label = ""
                try:
                    field_id = await input_elem.get_attribute('id')
                    if field_id:
                        label_elem = await page.query_selector(f'label[for="{field_id}"]')
                        if label_elem:
                            label = await label_elem.inner_text()
                except Exception:
                    pass
                
                options = []
                if tag_name == 'select':
                    option_elems = await input_elem.query_selector_all('option')
                    for opt in option_elems:
                        opt_text = await opt.inner_text()
                        options.append(opt_text.strip())
                
                field_info = {
                    'type': field_type,
                    'name': field_name,
                    'label': label.strip(),
                    'required': field_required,
                    'options': options if options else None,
                    'element': input_elem
                }
                
                fields.append(field_info)
                print(f"  📝 {field_name} ({field_type}) - {label} {'[REQ]' if field_required else ''}")
            except Exception:
                continue
        
        return fields

    def generate_answer_with_ai(self, field: dict) -> str:
        """Genera respuesta apropiada para un campo"""
        field_name_lower = field['name'].lower()
        field_label_lower = field['label'].lower()
        
        if 'nombre' in field_name_lower or 'name' in field_name_lower:
            return self.cv_data['nombre_completo']
        if 'email' in field_name_lower or 'correo' in field_name_lower:
            return self.cv_data['email']
        if 'telefono' in field_name_lower or 'phone' in field_name_lower:
            return self.cv_data['telefono']
        if 'ciudad' in field_name_lower or 'city' in field_name_lower:
            return self.cv_data['ciudad']
        if 'ingles' in field_label_lower or 'english' in field_label_lower:
            if field['options']:
                for opt in field['options']:
                    if 'avanzado' in opt.lower():
                        return opt
            return self.cv_data['nivel_ingles']
        if 'experiencia' in field_label_lower:
            if field['options']:
                for opt in field['options']:
                    if '10' in opt or '+9' in opt or 'expert' in opt.lower():
                        return opt
            return self.cv_data['anos_experiencia']
        if 'salario' in field_label_lower or 'sueldo' in field_label_lower:
            return self.cv_data['expectativa_salarial']
        
        if field['type'] in ['textarea', 'text'] and len(field['label']) > 20:
            prompt = f"Eres PM/IT Manager 10+ años. Campo: '{field['label']}'. Respuesta profesional (max 150 palabras):"
            try:
                response = self.llm_client.complete(prompt, max_tokens=200)
                return response.strip()
            except Exception:
                return self.cv_data['perfil']
        
        if field['options']:
            return field['options'][0]
        return ""

    async def fill_form(self, page, fields: list):
        """Llena el formulario automáticamente"""
        print("\n✍️  Llenando formulario...")
        for field in fields:
            try:
                answer = self.generate_answer_with_ai(field)
                if not answer:
                    continue
                print(f"  📝 {field['name']}: {answer[:50]}{'...' if len(answer) > 50 else ''}")
                if self.dry_run:
                    continue
                element = field['element']
                if field['type'] == 'select':
                    await element.select_option(label=answer)
                else:
                    await element.fill(answer)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  ⚠️  Error: {field['name']}")
                continue
    
    async def run(self, submit: bool = False):
        """Proceso completo"""
        print("\n" + "="*70)
        print("🚀 AUTO FORM FILLER")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            await page.goto(self.url, wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            fields = await self.extract_form_fields(page)
            print(f"\n📊 Campos: {len(fields)}")
            await self.fill_form(page, fields)
            
            if not self.dry_run and submit:
                submit_btn = await page.query_selector('button[type="submit"]')
                if submit_btn and input("\n⚠️  Enviar? (y/n): ").lower() == 'y':
                    await submit_btn.click()
                    print("✅ Enviado!")
            
            if not self.dry_run:
                print("\nPresiona Enter para cerrar...")
                input()
            await browser.close()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--submit', action='store_true')
    args = parser.parse_args()
    filler = AutoFormFiller(args.url, dry_run=args.dry_run)
    await filler.run(submit=args.submit)

if __name__ == "__main__":
    asyncio.run(main())
