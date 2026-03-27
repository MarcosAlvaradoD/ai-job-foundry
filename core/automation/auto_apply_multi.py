#!/usr/bin/env python3
"""
auto_apply_multi.py — Auto-apply multi-sitio para AI Job Foundry.
Soporta: LinkedIn Easy Apply, Indeed Quick Apply, Computrabajo, Adzuna, Glassdoor.
Usa CHALAN para recordar respuestas de formularios y preguntar por Telegram si falta algo.

Uso:
    py core/automation/auto_apply_multi.py --dry-run
    py core/automation/auto_apply_multi.py --live --sites linkedin indeed
    py core/automation/auto_apply_multi.py --live --max 5
"""
import sys
import os
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv
from core.sheets.sheet_manager import SheetManager
from core.automation.apply_profile import get_profile
from core.automation.form_filler import fill_form_fields, handle_linkedin_easy_apply_steps

load_dotenv()

# ── Configuracion ─────────────────────────────────────────────────────────────
FIT_THRESHOLD = 7
MAX_PER_RUN   = 10
DELAY_BETWEEN = 6  # segundos entre aplicaciones

ALL_SITES = ["linkedin", "indeed", "glassdoor", "adzuna", "computrabajo", "jobleads"]

BLOCKED_STATUSES = {"APPLIED", "EXPIRED", "REJECTED", "NO MATCH", "INVALID", "APPLICATION SUBMITTED"}

# ── Detectores de botones por sitio ──────────────────────────────────────────
SITE_APPLY_BUTTONS = {
    "linkedin": [
        'button:has-text("Easy Apply")',
        'button:has-text("Apply now")',
    ],
    "indeed": [
        'button:has-text("Apply now")',
        'button:has-text("Apply on company site")',
        'a:has-text("Apply now")',
        'button:has-text("Aplicar ahora")',
        'button:has-text("Solicitar empleo")',
    ],
    "glassdoor": [
        'button:has-text("Easy Apply")',
        'a:has-text("Apply Now")',
        'button:has-text("Apply")',
    ],
    "adzuna": [
        'a:has-text("Apply")',
        'button:has-text("Apply")',
        'a:has-text("Solicitar")',
    ],
    "computrabajo": [
        'a:has-text("Postularme")',
        'button:has-text("Postularme")',
        'a:has-text("Aplicar")',
        'button:has-text("Aplicar")',
        'a:has-text("Enviar curriculum")',
    ],
    "jobleads": [
        'a:has-text("Apply")',
        'button:has-text("Apply")',
    ],
}

SITE_SUBMIT_BUTTONS = {
    "linkedin":     ['button:has-text("Submit application")', 'button:has-text("Review")'],
    "indeed":       ['button:has-text("Submit")', 'button:has-text("Continue")', 'button:has-text("Apply")'],
    "glassdoor":    ['button:has-text("Submit")', 'button:has-text("Apply Now")'],
    "adzuna":       ['button:has-text("Submit")', 'button:has-text("Send Application")'],
    "computrabajo": ['button:has-text("Enviar")', 'button:has-text("Postularme")', 'input[type="submit"]'],
    "jobleads":     ['button:has-text("Submit")', 'button:has-text("Apply")'],
}


def _safe_fit(v) -> int:
    try:
        s = str(v).strip()
        return int(s.split("/")[0]) if "/" in s else int(s)
    except Exception:
        return 0


class MultiSiteApplier:
    def __init__(self, dry_run: bool = True, sites: list = None, max_apps: int = MAX_PER_RUN):
        self.dry_run  = dry_run
        self.sites    = sites or ALL_SITES
        self.max_apps = max_apps
        self.sm       = SheetManager()
        self.profile  = get_profile()
        self.applied  = 0
        self.errors   = []

    def get_eligible_jobs(self) -> list:
        """Obtiene jobs elegibles de todas las tabs seleccionadas."""
        eligible = []
        for tab in self.sites:
            try:
                jobs = self.sm.get_all_jobs(tab)
                for i, j in enumerate(jobs, start=2):
                    j["_row"] = i
                    j["_tab"] = tab
                    j["_fit"] = _safe_fit(j.get("FitScore", 0))
                    if (
                        j["_fit"] >= FIT_THRESHOLD and
                        j.get("Status", "").upper().strip() not in BLOCKED_STATUSES and
                        j.get("ApplyURL", "").strip() not in ("", "Unknown", "N/A", "None")
                    ):
                        eligible.append(j)
            except Exception as e:
                print(f"  [WARN] Error leyendo tab {tab}: {e}")

        eligible.sort(key=lambda x: x["_fit"], reverse=True)
        return eligible[:self.max_apps]

    async def find_and_click_apply(self, page: Page, site: str) -> bool:
        """Encuentra y hace clic en el botón de aplicar para el sitio dado."""
        buttons = SITE_APPLY_BUTTONS.get(site, [])
        for selector in buttons:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=3000):
                    await btn.click()
                    await asyncio.sleep(2)
                    return True
            except Exception:
                continue
        return False

    async def find_and_click_submit(self, page: Page, site: str) -> bool:
        """Intenta hacer clic en el botón de submit para el sitio dado."""
        buttons = SITE_SUBMIT_BUTTONS.get(site, [])
        for selector in buttons:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=3000):
                    await btn.click()
                    return True
            except Exception:
                continue
        return False

    async def apply_to_job(self, job: dict, page: Page) -> bool:
        """Aplica a un job en el sitio correspondiente."""
        url    = job.get("ApplyURL", "")
        title  = job.get("Role", "?")
        company= job.get("Company", "?")
        site   = job.get("_tab", "linkedin")
        fit    = job.get("_fit", 0)

        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}[{site.upper()}] FIT={fit} — {title} @ {company}")
        print(f"  URL: {url[:80]}")

        if self.dry_run:
            print("  OK [DRY RUN] Se aplicaria a este job")
            return True

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)

            # LinkedIn tiene flujo especial multi-paso
            if site == "linkedin":
                clicked = await self.find_and_click_apply(page, site)
                if not clicked:
                    print("  WARN Boton Easy Apply no encontrado")
                    return False
                await asyncio.sleep(1.5)
                success = await handle_linkedin_easy_apply_steps(page, job)
                if success:
                    print(f"  OK Aplicacion enviada en LinkedIn")
                    return True
                else:
                    print(f"  WARN No se pudo completar el formulario LinkedIn")
                    return False

            # Otros sitios: flujo generico
            clicked = await self.find_and_click_apply(page, site)
            if not clicked:
                print(f"  WARN Boton de aplicar no encontrado en {site}")
                return False

            await asyncio.sleep(2)

            # Rellenar formulario si hay campos
            fill_result = await fill_form_fields(page, job, site, ask_missing=True)
            if fill_result["filled"]:
                print(f"  INFO Campos rellenados: {len(fill_result['filled'])}")
            if fill_result["asked"]:
                print(f"  INFO Preguntas enviadas por Telegram: {len(fill_result['asked'])}")

            await asyncio.sleep(1)

            submitted = await self.find_and_click_submit(page, site)
            if submitted:
                print(f"  OK Aplicacion enviada en {site}")
                return True
            else:
                print(f"  WARN Submit no encontrado — puede requerir revision manual")
                return False

        except Exception as e:
            print(f"  ERR Error: {e}")
            self.errors.append({"job": f"{title} @ {company}", "error": str(e)})
            return False

    async def update_status(self, job: dict, applied: bool):
        """Actualiza el status en Google Sheets."""
        try:
            row = job.get("_row")
            tab = job.get("_tab", "linkedin")
            if not row:
                return
            if applied:
                self.sm.update_job(row, {
                    "Status": "Application submitted",
                    "NextAction": f"Auto-applied {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }, tab)
            else:
                self.sm.update_job(row, {
                    "NextAction": "Auto-apply fallido — revision manual"
                }, tab)
        except Exception as e:
            print(f"  WARN Error actualizando sheet: {e}")

    async def run(self):
        """Ejecuta el auto-apply para todos los sitios configurados."""
        print()
        print("=" * 65)
        print("  AI JOB FOUNDRY - AUTO-APPLY MULTI-SITIO")
        print("=" * 65)
        print(f"  Modo:   {'DRY RUN (sin aplicaciones reales)' if self.dry_run else 'LIVE (aplicaciones reales)'}")
        print(f"  Sitios: {', '.join(self.sites)}")
        print(f"  FIT:    >= {FIT_THRESHOLD}")
        print(f"  Max:    {self.max_apps} aplicaciones")
        print("=" * 65)
        print()

        eligible = self.get_eligible_jobs()
        if not eligible:
            print("  Sin jobs elegibles. Corre calculate_all_tabs_fit_scores.py primero.")
            return

        print(f"  Jobs elegibles: {len(eligible)}")
        for j in eligible:
            print(f"    FIT={j['_fit']} [{j['_tab'].upper()}] {j.get('Role','?')[:40]} @ {j.get('Company','?')[:20]}")
        print()

        if self.dry_run:
            print("  [DRY RUN] Ninguna aplicacion sera enviada.")
            return

        # Cargar perfil antes de iniciar el browser
        self.profile.load()
        print(f"  Perfil cargado: {len(self.profile._cache)} campos disponibles")
        print()

        async with async_playwright() as pw:
            print("  Iniciando browser...")
            browser = await pw.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

            # Usar sesion guardada si existe
            session_file = Path("data/credentials/browser_session.json")
            ctx = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                storage_state=str(session_file) if session_file.exists() else None,
            )
            page = await ctx.new_page()

            for job in eligible:
                if self.applied >= self.max_apps:
                    print(f"\n  Limite de {self.max_apps} aplicaciones alcanzado.")
                    break

                applied = await self.apply_to_job(job, page)
                await self.update_status(job, applied)
                if applied:
                    self.applied += 1

                await asyncio.sleep(DELAY_BETWEEN)

            # Guardar sesion del browser para proxima vez
            try:
                session_file.parent.mkdir(parents=True, exist_ok=True)
                await ctx.storage_state(path=str(session_file))
            except Exception:
                pass

            await browser.close()

        print()
        print("=" * 65)
        print(f"  RESULTADO: {self.applied} aplicaciones enviadas | {len(self.errors)} errores")
        print("=" * 65)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true", default=True)
    parser.add_argument("--live",     action="store_true")
    parser.add_argument("--sites",    nargs="*", default=ALL_SITES)
    parser.add_argument("--max",      type=int, default=MAX_PER_RUN)
    args = parser.parse_args()

    dry_run = not args.live

    if not dry_run:
        print("\n" + "=" * 65)
        print("  AVISO: MODO LIVE — se enviaran aplicaciones reales")
        print("=" * 65)
        confirm = input("  Escribe YES para confirmar: ")
        if confirm.strip().upper() != "YES":
            print("  Cancelado.\n")
            return

    applier = MultiSiteApplier(dry_run=dry_run, sites=args.sites, max_apps=args.max)
    asyncio.run(applier.run())


if __name__ == "__main__":
    main()
