#!/usr/bin/env python3
"""
DEBUG: Detecta los selectores correctos del formulario ITC
"""
import asyncio
from playwright.async_api import async_playwright

async def inspect_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://vacantes.rh-itchome.com/aplicar/262")
        await asyncio.sleep(3)
        
        print("\n=== DETECTANDO CAMPOS DEL FORMULARIO ===\n")
        
        # Detectar inputs
        inputs = await page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"], input[type="date"]')
        
        for i, inp in enumerate(inputs, 1):
            name = await inp.get_attribute('name')
            id_attr = await inp.get_attribute('id')
            placeholder = await inp.get_attribute('placeholder')
            
            print(f"Input {i}:")
            print(f"  name: {name}")
            print(f"  id: {id_attr}")
            print(f"  placeholder: {placeholder}")
            print()
        
        # Detectar selects
        selects = await page.query_selector_all('select')
        
        print("\n=== SELECTS ===\n")
        for i, sel in enumerate(selects, 1):
            name = await sel.get_attribute('name')
            id_attr = await sel.get_attribute('id')
            
            print(f"Select {i}:")
            print(f"  name: {name}")
            print(f"  id: {id_attr}")
            print()
        
        input("\nPresiona Enter para cerrar...")
        await browser.close()

asyncio.run(inspect_form())
