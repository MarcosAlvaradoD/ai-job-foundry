#!/usr/bin/env python3
"""
HELPER: Login LinkedIn - Copia cookies de tu navegador regular
"""
import asyncio
from playwright.async_api import async_playwright
import os
import json

async def copy_linkedin_session():
    print("="*70)
    print("🔐 LINKEDIN SESSION COPY")
    print("="*70)
    print("\nEste script:")
    print("1. Usa las cookies de tu Chrome/Edge donde YA estás loggeado")
    print("2. Las copia para que auto-apply funcione")
    print("\n" + "="*70)
    
    # Detectar perfil de Chrome/Edge
    chrome_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    edge_path = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data")
    
    if os.path.exists(chrome_path):
        user_data_dir = chrome_path
        print(f"\n✅ Chrome detectado: {chrome_path}")
    elif os.path.exists(edge_path):
        user_data_dir = edge_path
        print(f"\n✅ Edge detectado: {edge_path}")
    else:
        print("\n❌ No se encontró Chrome ni Edge")
        print("   Por favor, usa Chrome o Edge y asegúrate de estar loggeado en LinkedIn")
        return
    
    input("\n⚠️  CIERRA Chrome/Edge completamente antes de continuar\n   Presiona Enter cuando esté cerrado...")
    
    async with async_playwright() as p:
        print("\n🌐 Abriendo LinkedIn con tu perfil...")
        
        # Launch with user profile
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome" if "Chrome" in user_data_dir else "msedge"
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Go to LinkedIn
        await page.goto("https://www.linkedin.com/feed/")
        await asyncio.sleep(3)
        
        current_url = page.url
        
        if 'feed' in current_url or 'mynetwork' in current_url or 'jobs' in current_url:
            print("\n✅ Sesión de LinkedIn detectada!")
            
            # Save storage state (cookies)
            os.makedirs("data/credentials", exist_ok=True)
            await context.storage_state(path="data/credentials/linkedin_session.json")
            
            print("💾 Cookies guardadas en: data/credentials/linkedin_session.json")
            print("\n" + "="*70)
            print("🎉 LISTO - Auto-apply ahora funcionará")
            print("="*70)
        else:
            print(f"\n⚠️  No estás loggeado en LinkedIn")
            print(f"   URL actual: {current_url}")
            print("\n   Por favor:")
            print("   1. Abre Chrome/Edge normalmente")
            print("   2. Ve a linkedin.com")
            print("   3. Haz login")
            print("   4. Cierra el navegador")
            print("   5. Ejecuta este script de nuevo")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(copy_linkedin_session())
