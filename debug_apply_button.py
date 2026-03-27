"""
DEBUG: Detectar el botón de Easy Apply real en LinkedIn (2026)
Hace login, navega a una vacante y muestra TODOS los botones con sus atributos.

Uso: py debug_apply_button.py
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

JOB_URL = "https://www.linkedin.com/jobs/view/4368862694"
AUTH_STATE_FILE = Path("data/credentials/linkedin_auth.json")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Intentar restaurar sesión guardada
        if AUTH_STATE_FILE.exists():
            print("Restaurando sesión guardada...")
            context = await browser.new_context(
                storage_state=str(AUTH_STATE_FILE),
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )
        else:
            print("No hay sesión guardada. Haciendo login manual...")
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )

        page = await context.new_page()

        # Si no hay sesión, hacer login
        if not AUTH_STATE_FILE.exists():
            email    = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            print(f"Email: {email}")

            await page.goto('https://www.linkedin.com/login')
            await asyncio.sleep(2)
            await page.fill('input[name="session_key"]',      email)
            await page.fill('input[name="session_password"]', password)
            await page.click('button[type="submit"]')
            await asyncio.sleep(6)  # Más tiempo para 2FA si aplica

            if 'feed' in page.url or 'mynetwork' in page.url or 'checkpoint' not in page.url:
                print(f"Login OK. URL: {page.url}")
                # Guardar sesión para siguiente vez
                AUTH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                await context.storage_state(path=str(AUTH_STATE_FILE))
                print(f"Sesión guardada en: {AUTH_STATE_FILE}")
            else:
                print(f"Login FALLO. URL: {page.url}")
                print("Puede requerir verificación manual. Complétala en el navegador.")
                await asyncio.sleep(30)  # Dar tiempo para resolver CAPTCHA/2FA
                await context.storage_state(path=str(AUTH_STATE_FILE))
                print("Sesión guardada (con verificación).")

        # Navegar a la vacante
        print(f"\nNavegando a: {JOB_URL}")
        await page.goto(JOB_URL, wait_until='domcontentloaded')

        # Esperar que cargue el contenido de jobs
        try:
            await page.wait_for_selector(
                '.jobs-details, .job-details-jobs-unified-top-card, .jobs-search__job-details',
                timeout=15000
            )
            print("Contenido de jobs cargado.")
        except Exception:
            print("Timeout esperando contenido de jobs. Continuando de todas formas...")

        await asyncio.sleep(3)

        # Verificar si estamos logueados
        is_guest = await page.locator('a[href*="/login"]').count() > 0
        is_logged = await page.locator('a[href*="/feed/"]').count() > 0
        print(f"\nEstado: {'GUEST (no logueado)' if is_guest and not is_logged else 'LOGUEADO'}")

        # Mostrar TODOS los botones con sus atributos
        print("\n=== TODOS LOS BOTONES EN LA PÁGINA ===")
        buttons = page.locator('button')
        count = await buttons.count()
        print(f"Total botones: {count}")

        for i in range(count):
            btn = buttons.nth(i)
            try:
                text        = (await btn.inner_text(timeout=500)).strip().replace('\n', ' ')[:60]
                aria_label  = await btn.get_attribute('aria-label') or ''
                class_name  = await btn.get_attribute('class') or ''
                is_visible  = await btn.is_visible()

                # Solo mostrar si es visible o parece relevante
                if is_visible or 'apply' in (text + aria_label + class_name).lower():
                    print(f"\n  [{i}] VISIBLE={is_visible}")
                    if text:        print(f"       text       : {text}")
                    if aria_label:  print(f"       aria-label : {aria_label}")
                    if class_name:  print(f"       class      : {class_name[:80]}")
            except Exception:
                continue

        # Buscar específicamente botones de apply
        print("\n=== BUSCANDO BOTONES DE APPLY ===")
        apply_selectors = [
            'button[class*="jobs-apply"]',
            'button[aria-label*="apply" i]',
            'button[aria-label*="solicitar" i]',
            'button[aria-label*="Apply" i]',
            'button:has-text("Easy Apply")',
            'button:has-text("Solicitar")',
            'button:has-text("Apply")',
            '[data-control-name*="apply"]',
        ]
        for sel in apply_selectors:
            found = await page.locator(sel).count()
            if found > 0:
                elem     = page.locator(sel).first
                txt      = (await elem.inner_text(timeout=500)).strip()[:50]
                aria     = await elem.get_attribute('aria-label') or ''
                cls      = await elem.get_attribute('class') or ''
                visible  = await elem.is_visible()
                print(f"\n  ENCONTRADO con: {sel}")
                print(f"    text={txt!r}  aria={aria!r}  visible={visible}")
                print(f"    class={cls[:80]}")

        print("\n=== URL FINAL ===")
        print(page.url)

        input("\nPresiona ENTER para cerrar el navegador...")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
