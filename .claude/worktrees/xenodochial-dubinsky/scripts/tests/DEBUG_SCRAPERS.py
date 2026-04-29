#!/usr/bin/env python3
"""
SCRAPER DEBUGGER
Prueba cada scraper individualmente para identificar qué está fallando

Tests:
1. LinkedIn Scraper
2. Indeed Scraper  
3. Glassdoor Scraper (si existe)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import asyncio
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "="*70)
    print("📦 TESTING IMPORTS")
    print("="*70 + "\n")
    
    modules_to_test = [
        ('playwright', 'playwright.async_api'),
        ('gspread', 'gspread'),
        ('BeautifulSoup', 'bs4'),
        ('requests', 'requests'),
        ('dotenv', 'dotenv')
    ]
    
    all_ok = True
    for name, module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {name:20s} OK")
        except ImportError as e:
            print(f"  ❌ {name:20s} FALTA - {e}")
            all_ok = False
    
    return all_ok

def test_linkedin_scraper():
    """Test LinkedIn scraper"""
    print("\n" + "="*70)
    print("🔗 TESTING LINKEDIN SCRAPER")
    print("="*70 + "\n")
    
    scraper_file = Path("core/ingestion/linkedin_scraper_V2.py")
    
    if not scraper_file.exists():
        print("❌ linkedin_scraper_V2.py no encontrado")
        return False
    
    print("  ✅ Archivo encontrado")
    
    try:
        # Try to import
        from core.ingestion.linkedin_scraper_V2 import LinkedInScraper
        print("  ✅ Import exitoso")
        
        # Check if can instantiate
        scraper = LinkedInScraper()
        print("  ✅ Instancia creada")
        
        print("\n💡 Para probar scraping real:")
        print("   py core\\ingestion\\linkedin_scraper_V2.py")
        print("\n⚠️  Asegúrate de tener:")
        print("   1. Playwright instalado: py -m playwright install chromium")
        print("   2. Sesión activa de LinkedIn")
        print("   3. Búsquedas configuradas en .env")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_indeed_scraper():
    """Test Indeed scraper"""
    print("\n" + "="*70)
    print("🔗 TESTING INDEED SCRAPER")
    print("="*70 + "\n")
    
    scraper_file = Path("core/ingestion/indeed_scraper.py")
    
    if not scraper_file.exists():
        print("❌ indeed_scraper.py no encontrado")
        return False
    
    print("  ✅ Archivo encontrado")
    
    try:
        # Try to import
        from core.ingestion.indeed_scraper import IndeedScraper
        print("  ✅ Import exitoso")
        
        # Check if can instantiate
        scraper = IndeedScraper()
        print("  ✅ Instancia creada")
        
        print("\n💡 Para probar scraping real:")
        print("   py core\\ingestion\\indeed_scraper.py")
        print("\n⚠️  Problema conocido:")
        print("   - Chromium se congela frecuentemente")
        print("   - Timeout no lo resuelve")
        print("   - Requiere investigación adicional")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_glassdoor_scraper():
    """Test Glassdoor scraper"""
    print("\n" + "="*70)
    print("🔗 TESTING GLASSDOOR SCRAPER")
    print("="*70 + "\n")
    
    # Search for Glassdoor scraper
    potential_files = [
        Path("core/ingestion/glassdoor_scraper.py"),
        Path("core/ingestion/glassdoor_scraper_v2.py"),
        Path("scripts/glassdoor_scraper.py")
    ]
    
    found = None
    for f in potential_files:
        if f.exists():
            found = f
            break
    
    if not found:
        print("  ⚠️  No se encontró scraper de Glassdoor")
        print("  💡 Los boletines de Glassdoor SÍ llegan por email")
        print("  💡 Puedes procesarlos con job_bulletin_processor.py")
        return None
    
    print(f"  ✅ Archivo encontrado: {found}")
    
    try:
        # This would need to be customized based on actual file
        print("  ℹ️  Scraper encontrado pero no testeado automáticamente")
        print("  💡 Ejecutar manualmente para probar")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_playwright_installation():
    """Test if Playwright browsers are installed"""
    print("\n" + "="*70)
    print("🌐 TESTING PLAYWRIGHT")
    print("="*70 + "\n")
    
    try:
        from playwright.sync_api import sync_playwright
        
        print("  ✅ Playwright importado correctamente")
        
        # Try to launch browser
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.google.com")
                title = page.title()
                browser.close()
                
                print(f"  ✅ Chromium OK (title: {title})")
                return True
                
        except Exception as e:
            print(f"  ❌ Chromium NO disponible: {e}")
            print("\n💡 Instalar con:")
            print("   py -m playwright install chromium")
            return False
            
    except ImportError:
        print("  ❌ Playwright no instalado")
        print("\n💡 Instalar con:")
        print("   pip install playwright --break-system-packages")
        print("   py -m playwright install chromium")
        return False

def test_env_config():
    """Test .env configuration"""
    print("\n" + "="*70)
    print("⚙️  TESTING .ENV CONFIGURATION")
    print("="*70 + "\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'GOOGLE_SHEETS_ID',
        'LM_STUDIO_URL',
        'GEMINI_API_KEY'
    ]
    
    optional_vars = [
        'LINKEDIN_EMAIL',
        'LINKEDIN_PASSWORD'
    ]
    
    all_ok = True
    
    print("Variables requeridas:")
    for var in required_vars:
        val = os.getenv(var)
        if val:
            # Show first/last 4 chars only
            if len(val) > 20:
                display = f"{val[:4]}...{val[-4:]}"
            else:
                display = val[:10] + "..."
            print(f"  ✅ {var:25s}: {display}")
        else:
            print(f"  ❌ {var:25s}: NO CONFIGURADO")
            all_ok = False
    
    print("\nVariables opcionales:")
    for var in optional_vars:
        val = os.getenv(var)
        if val:
            print(f"  ✅ {var:25s}: Configurado")
        else:
            print(f"  ⚠️  {var:25s}: No configurado")
    
    return all_ok

def main():
    print("\n" + "="*70)
    print("🔍 SCRAPER DEBUGGER")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {
        'imports': test_imports(),
        'env': test_env_config(),
        'playwright': test_playwright_installation(),
        'linkedin': test_linkedin_scraper(),
        'indeed': test_indeed_scraper(),
        'glassdoor': test_glassdoor_scraper()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESUMEN DE TESTS")
    print("="*70 + "\n")
    
    for test, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        
        print(f"  {test.upper():20s}: {status}")
    
    # Recommendations
    print("\n" + "="*70)
    print("💡 RECOMENDACIONES")
    print("="*70 + "\n")
    
    if not results['imports']:
        print("  1. Instalar dependencias faltantes")
        print("     pip install [paquete] --break-system-packages")
    
    if not results['playwright']:
        print("  2. Instalar Playwright browsers")
        print("     py -m playwright install chromium")
    
    if not results['env']:
        print("  3. Configurar variables en .env")
        print("     Ver archivo .env.example")
    
    if results['linkedin'] is False:
        print("  4. Revisar LinkedIn scraper")
        print("     Puede tener problemas de import o dependencias")
    
    if results['indeed'] is False:
        print("  5. Revisar Indeed scraper")
        print("     Problema conocido: Chromium freeze")
    
    if results['glassdoor'] is None:
        print("  6. Glassdoor: Usar job_bulletin_processor.py")
        print("     Los boletines llegan por email")
    
    print("\n" + "="*70)
    print("✅ DEBUG COMPLETO")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
