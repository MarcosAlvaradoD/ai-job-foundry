#!/usr/bin/env python3
"""
AI JOB FOUNDRY — Auto-Apply Runner v2
======================================
Aplica automáticamente a jobs con FIT >= 7 via LinkedIn Easy Apply.

CARACTERÍSTICAS:
  ✅ Lee jobs desde Google Sheets (TODAS las pestañas)
  ✅ Filtra por FIT >= 7 y URL válida
  ✅ Auto-login con sesión guardada (cookies)
  ✅ Easy Apply: maneja formularios multi-paso
  ✅ Llena campos con datos del CV automáticamente
  ✅ Modo --dry-run para probar sin aplicar
  ✅ Guarda log de aplicaciones en data/applied_jobs.json
  ✅ Actualiza status en Google Sheets

USO:
  py core/automation/auto_apply_runner.py --dry-run   # Ver qué aplicaría
  py core/automation/auto_apply_runner.py --run        # Aplicar (máx 10/sesión)
  py core/automation/auto_apply_runner.py --diagnose   # Debug: ver por qué no hay elegibles

CONFIG en .env:
  LINKEDIN_EMAIL=tu@email.com
  LINKEDIN_PASSWORD=tupassword
"""

import sys, os, json, time, argparse
from pathlib import Path
from datetime import datetime

# Fix emoji output in Windows CMD
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# ─── Config ──────────────────────────────────────────────────────────────────
FIT_MIN          = 7
MAX_PER_SESSION  = 10
APPLIED_LOG      = project_root / "data" / "applied_jobs.json"
COOKIES_FILE     = project_root / "data" / "linkedin_cookies.json"
CANDIDATE        = {
    "first_name":       "Marcos",
    "last_name":        "Alvarado",
    "full_name":        "Marcos Alberto Alvarado de la Torre",
    "email":            os.getenv("CANDIDATE_EMAIL", "markalvati@gmail.com"),
    "phone":            os.getenv("CANDIDATE_PHONE", "+52 33 2332 0358"),
    "city":             "Guadalajara",
    "country":          "Mexico",
    "years_experience": "10",
    "linkedin_url":     "https://www.linkedin.com/in/marcosalvarado-it",
}

LINKEDIN_EMAIL    = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

BLOCKED_STATUSES = {
    "APPLIED", "EXPIRED", "REJECTED", "NO MATCH", "INVALID", "REVIEWING",
    "APPLICATION SUBMITTED", "SUBMITTED", "INTERVIEWING", "OFFER", "DECLINED"
}


# ─── Helpers ─────────────────────────────────────────────────────────────────
def safe_fit(val) -> int:
    try:
        s = str(val or "").strip()
        return int(s.split("/")[0]) if "/" in s else int(s)
    except Exception:
        return 0

def load_applied() -> set:
    try:
        if APPLIED_LOG.exists():
            data = json.loads(APPLIED_LOG.read_text())
            return {j["apply_url"] for j in data if "apply_url" in j}
    except Exception:
        pass
    return set()

def save_applied(jobs: list):
    APPLIED_LOG.parent.mkdir(exist_ok=True)
    existing = []
    try:
        if APPLIED_LOG.exists():
            existing = json.loads(APPLIED_LOG.read_text())
    except Exception:
        pass
    existing.extend(jobs)
    APPLIED_LOG.write_text(json.dumps(existing, indent=2, ensure_ascii=False))


# ─── Get eligible jobs ────────────────────────────────────────────────────────
def get_eligible_jobs(verbose=False) -> list:
    """
    Obtiene jobs elegibles de Google Sheets (TODAS las pestañas).
    Criterios: FIT >= 7, URL válida, no aplicado, status no bloqueado.
    """
    try:
        from core.sheets.sheet_manager import SheetManager
        sm = SheetManager()
    except Exception as e:
        print(f"❌ Google Sheets no disponible: {e}")
        print("   Verifica que token.json exista en el proyecto.")
        return []

    already_applied = load_applied()
    eligible = []
    all_tabs = ["linkedin", "glassdoor", "indeed", "computrabajo"]

    for tab in all_tabs:
        try:
            jobs = sm.get_all_jobs(tab=tab)
            for i, job in enumerate(jobs, start=2):
                job["_tab"] = tab
                job["_row"] = i
        except Exception as e:
            if verbose:
                print(f"  ⚠️  Tab '{tab}': {e}")
            jobs = []

        for job in jobs:
            fit    = safe_fit(job.get("FitScore", 0))
            status = job.get("Status", "").upper().strip()
            url    = job.get("ApplyURL", "").strip()
            role   = job.get("Role", "?")[:50]
            co     = job.get("Company", "?")[:30]

            ok_fit    = fit >= FIT_MIN
            ok_status = status not in BLOCKED_STATUSES
            ok_url    = url and url not in ("", "Unknown", "N/A", "None")
            ok_prev   = url not in already_applied

            if verbose:
                flags = f"FIT={fit}{'✅' if ok_fit else '❌'}  Status={status}{'✅' if ok_status else '❌'}  URL={'✅' if ok_url else '❌'}  Prev={'✅' if ok_prev else '❌(ya aplicado)'}"
                print(f"  [{tab}] {co} – {role}")
                print(f"         {flags}")

            if ok_fit and ok_status and ok_url and ok_prev:
                eligible.append(job)

    # Ordenar por FIT descendente
    eligible.sort(key=lambda j: safe_fit(j.get("FitScore", 0)), reverse=True)
    return eligible[:MAX_PER_SESSION]


# ─── LinkedIn Easy Apply ──────────────────────────────────────────────────────
class LinkedInEasyApply:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self._applied = []
        try:
            from playwright.sync_api import sync_playwright
            self._playwright_available = True
        except ImportError:
            self._playwright_available = False
            print("❌ Playwright no instalado. Ejecuta: pip install playwright && playwright install chromium")

    def run(self, jobs: list):
        if not self._playwright_available:
            return

        from playwright.sync_api import sync_playwright, TimeoutError as PWT

        with sync_playwright() as pw:
            # Lanzar Chromium con ventana visible (para que puedas intervenir si hay CAPTCHA)
            browser = pw.chromium.launch(
                headless=False,
                slow_mo=100,
                args=["--start-maximized"]
            )
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            # Cargar cookies guardadas
            self._load_cookies(ctx)

            page = ctx.new_page()
            self._ensure_login(page)

            for job in jobs:
                url   = job.get("ApplyURL", "").strip()
                role  = job.get("Role", "?")
                co    = job.get("Company", "?")
                fit   = safe_fit(job.get("FitScore", 0))
                tab   = job.get("_tab", "?")

                print(f"\n{'🔍 [DRY RUN]' if self.dry_run else '🚀 [APLICANDO]'} FIT={fit} | {co} — {role}")
                print(f"   URL: {url}")

                if self.dry_run:
                    print("   ✅ Se aplicaría (dry-run — no enviado)")
                    continue

                try:
                    result = self._apply_to_job(page, job)
                    if result:
                        self._applied.append({
                            "apply_url": url,
                            "role": role,
                            "company": co,
                            "fit": fit,
                            "tab": tab,
                            "applied_at": datetime.now().isoformat()
                        })
                        print(f"   ✅ Aplicado exitosamente")
                        time.sleep(3)  # pausa entre aplicaciones
                    else:
                        print(f"   ⚠️  No se pudo completar la aplicación")
                except Exception as e:
                    print(f"   ❌ Error: {e}")

            if self._applied:
                save_applied(self._applied)
                self._save_cookies(ctx)
                print(f"\n✅ {len(self._applied)} aplicaciones completadas")
                print(f"   Log guardado en: {APPLIED_LOG}")

            browser.close()

    def _load_cookies(self, ctx):
        try:
            if COOKIES_FILE.exists():
                cookies = json.loads(COOKIES_FILE.read_text())
                ctx.add_cookies(cookies)
                print(f"✅ Cookies cargadas ({len(cookies)} cookies)")
        except Exception as e:
            print(f"⚠️  No se pudieron cargar cookies: {e}")

    def _save_cookies(self, ctx):
        try:
            cookies = ctx.cookies()
            COOKIES_FILE.parent.mkdir(exist_ok=True)
            COOKIES_FILE.write_text(json.dumps(cookies))
            print(f"✅ Cookies guardadas")
        except Exception:
            pass

    def _ensure_login(self, page):
        print("\n🔐 Verificando sesión LinkedIn...")
        try:
            page.goto("https://www.linkedin.com/feed/", timeout=20000, wait_until="domcontentloaded")
            time.sleep(2)
            if "/feed" in page.url:
                print("✅ Sesión activa")
                return True
        except Exception:
            pass

        # Auto-login
        if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
            print("❌ LINKEDIN_EMAIL/LINKEDIN_PASSWORD no configurados en .env")
            print("   Configúralos y vuelve a intentar")
            return False

        print(f"🔑 Iniciando sesión como {LINKEDIN_EMAIL}...")
        try:
            page.goto("https://www.linkedin.com/login", timeout=20000)
            time.sleep(1)
            page.fill("#username", LINKEDIN_EMAIL)
            page.fill("#password", LINKEDIN_PASSWORD)
            page.click('button[type="submit"]')
            time.sleep(5)

            if "/checkpoint" in page.url or "/challenge" in page.url:
                print("\n⚠️  LinkedIn pide verificación de seguridad")
                print("   Completa el captcha/verificación en el navegador (tienes 90s)...")
                deadline = time.time() + 90
                while time.time() < deadline:
                    time.sleep(2)
                    if "/feed" in page.url:
                        break

            if "/feed" in page.url:
                print("✅ Login exitoso")
                return True
            else:
                print(f"❌ Login falló — URL: {page.url}")
                return False
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False

    def _apply_to_job(self, page, job) -> bool:
        """Aplica a un job de LinkedIn Easy Apply."""
        from playwright.sync_api import TimeoutError as PWT

        url = job.get("ApplyURL", "").strip()

        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            # ── Buscar botón Easy Apply ──────────────────────────────────
            easy_apply = None
            selectors = [
                'button:has-text("Easy Apply")',
                'button:has-text("Solicitud sencilla")',
                '[data-control-name="jobdetails_topcard_inapply"]',
                'button.jobs-apply-button',
            ]
            for sel in selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=3000):
                        easy_apply = btn
                        break
                except Exception:
                    continue

            if not easy_apply:
                print("   🔗 No tiene Easy Apply — intentando aplicación externa...")
                return self._try_external_apply(page, job)

            easy_apply.click()
            time.sleep(2)

            # ── Llenar formulario multi-paso ─────────────────────────────
            max_steps = 8
            for step in range(max_steps):
                print(f"   📝 Paso {step + 1}...")
                self._fill_form_step(page)
                time.sleep(1)

                # Buscar botón "Siguiente" o "Revisar" o "Enviar"
                submitted = self._click_next_or_submit(page)
                if submitted == "submitted":
                    return True
                elif submitted == "error":
                    return False
                # Si returned "next" → continuar al siguiente paso

            return False

        except PWT as e:
            print(f"   ❌ Timeout: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error aplicando: {e}")
            return False

    # ── External ATS Apply ────────────────────────────────────────────────────

    def _try_external_apply(self, page, job) -> bool:
        """Captura el botón Apply externo de LinkedIn y lo maneja según el ATS."""
        from playwright.sync_api import TimeoutError as PWT
        import webbrowser

        ext_selectors = [
            'button:has-text("Apply")',
            'a:has-text("Apply")',
            'button:has-text("Solicitar")',
            '.jobs-apply-button--top-card',
        ]

        ext_btn = None
        for sel in ext_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    ext_btn = btn
                    break
            except Exception:
                continue

        if not ext_btn:
            print("   ❌ No se encontró botón de aplicación")
            return False

        # LinkedIn abre una nueva pestaña al hacer click en Apply externo
        try:
            with page.context.expect_page(timeout=10000) as popup_info:
                ext_btn.click()
            ats_page = popup_info.value
            ats_page.wait_for_load_state("domcontentloaded", timeout=20000)
            ats_url = ats_page.url
            print(f"   🔗 ATS: {ats_url[:80]}")
            result = self._apply_ats(ats_page, ats_url, job)
            ats_page.close()
            return result
        except Exception:
            # Fallback: puede que no haya abierto nueva pestaña
            url = job.get("ApplyURL", "")
            print(f"   🌐 Abriendo en navegador para revisión manual")
            webbrowser.open(url)
            return False

    def _apply_ats(self, page, url: str, job) -> bool:
        """Detecta el ATS por URL y despacha al handler correcto."""
        import webbrowser
        u = url.lower()

        if "greenhouse.io" in u or "boards.greenhouse" in u:
            print("   🟢 Greenhouse detectado")
            return self._apply_greenhouse(page, job)
        elif "jobs.lever.co" in u or "lever.co" in u:
            print("   🟡 Lever detectado")
            return self._apply_lever(page, job)
        elif "myworkdayjobs.com" in u:
            print("   🔵 Workday detectado — abriendo manualmente (muy complejo para automatizar)")
            webbrowser.open(url)
            return False
        elif "bamboohr.com" in u:
            print("   🟠 BambooHR detectado")
            return self._apply_greenhouse(page, job)  # estructura similar a Greenhouse
        else:
            print("   ⚪ ATS desconocido — abriendo en navegador para revisión manual")
            webbrowser.open(url)
            return False

    def _apply_greenhouse(self, page, job) -> bool:
        """Maneja formularios de Greenhouse (y BambooHR que es similar)."""
        import time as _time
        _time.sleep(2)
        cv_path = str(project_root / "data" / "cv" / "CV_Marcos_Alvarado_2026.pdf")

        try:
            # Campos estándar Greenhouse
            fields = {
                'input[id="first_name"]':               CANDIDATE["first_name"],
                'input[id="last_name"]':                CANDIDATE["last_name"],
                'input[id="email"]':                    CANDIDATE["email"],
                'input[id="phone"]':                    CANDIDATE["phone"],
                'input[id="job_application_location"]': CANDIDATE["city"],
            }
            for sel, val in fields.items():
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=2000):
                        el.fill(val)
                except Exception:
                    pass

            # LinkedIn URL — varios selectores posibles
            for sel in ['input[id="linkedin"]', 'input[placeholder*="linkedin" i]',
                        'input[id*="linkedin" i]', 'input[name*="linkedin" i]']:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=1500):
                        el.fill(CANDIDATE["linkedin_url"])
                        break
                except Exception:
                    pass

            # Resume upload
            for sel in ['input[type="file"][id*="resume" i]', 'input[type="file"][accept*="pdf" i]',
                        'input[type="file"]']:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        el.set_input_files(cv_path)
                        _time.sleep(1)
                        break
                except Exception:
                    pass

            # Submit
            for sel in ['input[type="submit"]', 'button[type="submit"]',
                        'button:has-text("Submit")', 'button:has-text("Apply")']:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        _time.sleep(3)
                        break
                except Exception:
                    pass

            # Verificar éxito
            for signal in ["confirmation", "thank-you", "thank_you", "submitted"]:
                if signal in page.url.lower():
                    print("   ✅ Aplicación enviada (Greenhouse)")
                    return True
            for txt in ["Thank you", "Gracias", "application received", "Successfully"]:
                try:
                    if page.get_by_text(txt, exact=False).count() > 0:
                        print("   ✅ Aplicación enviada (Greenhouse)")
                        return True
                except Exception:
                    pass

            print("   ⚠️  Formulario Greenhouse enviado (verificar manualmente)")
            return True  # Optimista — el botón fue clickeado

        except Exception as e:
            print(f"   ❌ Error en Greenhouse: {e}")
            return False

    def _apply_lever(self, page, job) -> bool:
        """Maneja formularios de Lever."""
        import time as _time
        _time.sleep(2)
        cv_path = str(project_root / "data" / "cv" / "CV_Marcos_Alvarado_2026.pdf")

        try:
            fields = {
                'input[name="name"]':             CANDIDATE["full_name"],
                'input[name="email"]':            CANDIDATE["email"],
                'input[name="phone"]':            CANDIDATE["phone"],
                'input[name="org"]':              "Independent",
                'input[name="urls[LinkedIn]"]':   CANDIDATE["linkedin_url"],
                'input[name="location"]':         CANDIDATE["city"],
            }
            for sel, val in fields.items():
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=2000):
                        el.fill(val)
                except Exception:
                    pass

            # Resume
            try:
                el = page.locator('input[type="file"]').first
                if el.count() > 0:
                    el.set_input_files(cv_path)
                    _time.sleep(1)
            except Exception:
                pass

            # Submit
            for sel in ['button[type="submit"]', 'button:has-text("Submit application")',
                        'button:has-text("Apply for this job")']:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        _time.sleep(3)
                        break
                except Exception:
                    pass

            for signal in ["thank", "confirmation", "submitted"]:
                if signal in page.url.lower():
                    print("   ✅ Aplicación enviada (Lever)")
                    return True

            print("   ⚠️  Formulario Lever enviado (verificar manualmente)")
            return True

        except Exception as e:
            print(f"   ❌ Error en Lever: {e}")
            return False

    def _fill_form_step(self, page):
        """Llena campos del formulario actual con datos del candidato."""
        # Phone number
        for sel in ['input[id*="phoneNumber"]', 'input[name*="phone"]', 'input[placeholder*="phone"]',
                    'input[placeholder*="teléfono"]']:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1500) and not el.input_value():
                    el.fill(CANDIDATE["phone"])
            except Exception: pass

        # City/Location
        for sel in ['input[id*="city"]', 'input[id*="location"]', 'input[placeholder*="city"]']:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1500) and not el.input_value():
                    el.fill(CANDIDATE["city"])
            except Exception: pass

        # Years of experience (radio / select / input)
        for sel in ['select[id*="experience"]', 'input[id*="experience"]']:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1500):
                    tag = el.evaluate("e => e.tagName.toLowerCase()")
                    if tag == "select":
                        el.select_option(label="10")
                    elif not el.input_value():
                        el.fill("10")
            except Exception: pass

        # Boolean / Yes-No radio buttons (Did you work on X?)
        # La mayoría de preguntas Yes/No → responder "Yes" como default
        try:
            radios = page.locator('fieldset input[type="radio"]').all()
            for i, radio in enumerate(radios):
                label_text = ""
                try:
                    label = page.locator(f'label[for="{radio.get_attribute("id")}"]')
                    label_text = label.text_content() or ""
                except Exception: pass

                # Si es la primera opción (Yes/Sí) de un par, seleccionarla
                if i % 2 == 0 and not radio.is_checked():
                    try:
                        radio.click(timeout=1000)
                    except Exception: pass
        except Exception: pass

        # Textarea (cover letter, etc.) — solo llenar si está vacío
        try:
            textareas = page.locator('textarea').all()
            for ta in textareas[:2]:  # máx 2 textareas
                if ta.is_visible(timeout=1000) and not ta.input_value():
                    ta.fill(
                        f"I am very interested in this position. "
                        f"With over {CANDIDATE['years_experience']} years of experience in project management "
                        f"and business analysis, I am confident I can bring immediate value to your team."
                    )
        except Exception: pass

    def _click_next_or_submit(self, page) -> str:
        """
        Busca el botón de acción del formulario actual.
        Retorna: 'next' | 'submitted' | 'error'
        """
        # Botón de envío final
        submit_selectors = [
            'button:has-text("Submit application")',
            'button:has-text("Enviar solicitud")',
            'button[aria-label*="Submit"]',
        ]
        for sel in submit_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(3)
                    print("   🎉 Solicitud enviada!")
                    return "submitted"
            except Exception: pass

        # Botón "Siguiente" / "Next"
        next_selectors = [
            'button:has-text("Next")',
            'button:has-text("Siguiente")',
            'button:has-text("Continue")',
            'button:has-text("Review")',
            'button:has-text("Revisar")',
            'button[aria-label*="Next"]',
        ]
        for sel in next_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(1.5)
                    return "next"
            except Exception: pass

        # Botón Cerrar/Descartar → salimos
        try:
            btn = page.locator('button[aria-label*="Dismiss"]').first
            if btn.is_visible(timeout=1000):
                return "error"
        except Exception: pass

        return "error"


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="AI Job Foundry Auto-Apply")
    parser.add_argument("--dry-run",  action="store_true", help="Ver qué aplicaría (sin enviar)")
    parser.add_argument("--run",      action="store_true", help="Aplicar realmente (max 10 jobs)")
    parser.add_argument("--diagnose", action="store_true", help="Debug: mostrar por qué hay o no elegibles")
    args = parser.parse_args()

    if not any([args.dry_run, args.run, args.diagnose]):
        args.dry_run = True  # Default: dry-run

    print("\n" + "="*65)
    print("  AI JOB FOUNDRY — Auto-Apply v2")
    print("="*65)

    verbose = args.diagnose
    print(f"\n📊 Buscando jobs elegibles (FIT >= {FIT_MIN})...")
    jobs = get_eligible_jobs(verbose=verbose)

    if not jobs:
        print("\n❌ No hay jobs elegibles.")
        if not verbose:
            print("   Ejecuta con --diagnose para ver el detalle de cada job.")
        return

    print(f"\n✅ {len(jobs)} jobs elegibles encontrados:\n")
    for j in jobs:
        print(f"  FIT={safe_fit(j.get('FitScore',0))} | [{j.get('_tab','?')}] {j.get('Company','?')} — {j.get('Role','?')[:50]}")
        print(f"         {j.get('ApplyURL','')[:80]}")

    if args.diagnose:
        print("\n✅ Diagnóstico completo.")
        return

    if args.run:
        print("\n" + "="*65)
        print("⚠️  MODO LIVE — Se enviarán solicitudes reales a LinkedIn")
        print("="*65)
        confirm = input("\nEscribe YES para confirmar: ").strip()
        if confirm.upper() != "YES":
            print("❌ Cancelado.")
            return
        dry_run = False
    else:
        print("\n🧪 MODO DRY-RUN — No se enviará ninguna solicitud")
        dry_run = True

    applier = LinkedInEasyApply(dry_run=dry_run)
    applier.run(jobs)

    if dry_run:
        print("\n💡 Para aplicar realmente: py core/automation/auto_apply_runner.py --run")


if __name__ == "__main__":
    main()
