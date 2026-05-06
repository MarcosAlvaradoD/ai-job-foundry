#!/usr/bin/env python3
"""
LinkedIn Auto-Apply — Production Runner
========================================
Wrapper sobre LinkedInAutoApplyV3 con opciones de línea de comandos.
Habilita submit real y modo headless opcional.

Uso:
  py scripts/apply/run_autoapply.py --dry-run            # simula sin enviar
  py scripts/apply/run_autoapply.py --submit             # envía a todos (Easy Apply + ATS externos)
  py scripts/apply/run_autoapply.py --submit --max 5     # max 5 apps
  py scripts/apply/run_autoapply.py --submit --headless  # sin ventana de browser
  py scripts/apply/run_autoapply.py --job-id 4392502231  # job específico
  py scripts/apply/run_autoapply.py --submit --no-external  # solo LinkedIn Easy Apply

Plataformas externas soportadas: Workable, Greenhouse, Lever, SmartRecruiters, BambooHR, Ashby, Workday, Generic
IA: LM Studio/Ollama (local, prioritario) → Gemini Flash → NVIDIA NIM → respuesta genérica

El script:
  1. Lee jobs de Google Sheets (FIT >= min_score, Status != Applied)
  2. También procesa jobs especificados por --job-id directamente
  3. Usa las cookies guardadas en data/linkedin_cookies.json
  4. Si las cookies expiraron, hace auto-login con LINKEDIN_EMAIL/PASSWORD del .env
  5. Con --submit: llena el formulario Y hace click en Submit
  6. Actualiza Google Sheets con status="Applied" y fecha
  7. Actualiza tasks_queue de Chalan DB como completado
"""
import sys
import argparse
import time
import json
import os
import re
import logging
import urllib.request
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
load_dotenv()

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# ── Logging a archivo ─────────────────────────────────────────────────────────
_LOG_DIR = Path(__file__).parent.parent.parent / "logs"

def setup_logging() -> logging.Logger:
    """Configura logger dual: consola + archivo logs/autoapply_YYYYMMDD.log"""
    _LOG_DIR.mkdir(exist_ok=True)
    log_file = _LOG_DIR / f"autoapply_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger("autoapply")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger  # ya inicializado

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                             datefmt="%H:%M:%S")
    # Archivo
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    # Consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info(f"Log iniciado: {log_file}")
    return logger

log = setup_logging()

# ── Telegram helper ───────────────────────────────────────────────────────────
def send_telegram(msg: str, parse_mode: str = "HTML") -> bool:
    """Envía mensaje a Telegram. Retorna True si OK, False si falla (no crítico)."""
    token   = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return False
    try:
        url  = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": msg,
                           "parse_mode": parse_mode}).encode()
        req  = urllib.request.Request(url, data=data,
                                      headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        log.warning(f"Telegram error (no crítico): {e}")
        return False

# ── Screenshot helper ─────────────────────────────────────────────────────────
_SS_DIR = _LOG_DIR / "screenshots"

def take_screenshot(page, label: str) -> str:
    """Guarda screenshot en logs/screenshots/. Retorna la ruta o ''."""
    try:
        _SS_DIR.mkdir(parents=True, exist_ok=True)
        fname = _SS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label[:40]}.png"
        page.screenshot(path=str(fname), full_page=False)
        log.info(f"Screenshot: {fname.name}")
        return str(fname)
    except Exception as e:
        log.warning(f"Screenshot falló: {e}")
        return ""

# ── CAPTCHA detection ─────────────────────────────────────────────────────────
CAPTCHA_SIGNALS = (
    '/checkpoint', '/challenge', '/uas/login-captcha',
    'recaptcha', 'captcha', 'verify you', 'are you human',
)

def is_captcha_page(page) -> bool:
    """Detecta si la página actual es un CAPTCHA / challenge de LinkedIn."""
    url_lower   = page.url.lower()
    title_lower = page.title().lower()
    return any(s in url_lower or s in title_lower for s in CAPTCHA_SIGNALS)

def handle_captcha(page, job: dict) -> bool:
    """
    Notifica por Telegram y espera hasta 3 minutos a que el usuario
    resuelva el CAPTCHA manualmente. Retorna True si se resolvió.
    """
    company = job.get('Company', 'Unknown')
    role    = job.get('Role', 'Unknown')
    ss_path = take_screenshot(page, f"captcha_{company[:20]}")

    msg = (
        f"⚠️ <b>Auto-Apply — CAPTCHA detectado</b>\n\n"
        f"Job: <b>{company}</b> — {role}\n"
        f"URL: {page.url[:80]}\n\n"
        f"Resuelve el CAPTCHA en el browser.\n"
        f"Esperando <b>3 minutos</b>..."
    )
    send_telegram(msg)
    log.warning(f"CAPTCHA detectado en {company} — esperando resolución manual (180s)...")

    start = time.time()
    while time.time() - start < 180:
        time.sleep(5)
        if not is_captcha_page(page):
            log.info("CAPTCHA resuelto — continuando")
            send_telegram("✅ <b>CAPTCHA resuelto</b> — continuando aplicaciones.")
            return True

    log.error("CAPTCHA no resuelto en 3 minutos — saltando este job")
    send_telegram("❌ <b>CAPTCHA timeout</b> — job saltado, continuando con el siguiente.")
    return False


# ── tasks_queue helpers ───────────────────────────────────────────────────────
def mark_task_done(task_text_fragment: str):
    """Mark a task in Chalan tasks_queue as completed"""
    if not HAS_PSYCOPG2:
        return
    try:
        conn = psycopg2.connect(host='localhost', port=15432, dbname='theagora',
                                user='theagora', password=os.getenv('THEAGORA_DB_PASSWORD', 'changeme'))
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks_queue SET status='completed', completed_at=NOW() "
            "WHERE status='pending' AND task_text ILIKE %s",
            (f'%{task_text_fragment}%',)
        )
        updated = cur.rowcount
        conn.commit()
        conn.close()
        if updated:
            print(f"  [DB] {updated} task(s) marked completed in tasks_queue")
    except Exception as e:
        print(f"  [DB WARN] Could not update tasks_queue: {e}")


def get_pending_apply_tasks() -> list[dict]:
    """Get all pending APPLY LinkedIn tasks from tasks_queue"""
    if not HAS_PSYCOPG2:
        return []
    try:
        conn = psycopg2.connect(host='localhost', port=15432, dbname='theagora',
                                user='theagora', password=os.getenv('THEAGORA_DB_PASSWORD', 'changeme'))
        cur = conn.cursor()
        cur.execute(
            "SELECT id, task_text, priority FROM tasks_queue "
            "WHERE status='pending' AND task_text ILIKE 'APPLY LinkedIn%' "
            "ORDER BY priority DESC, id"
        )
        rows = cur.fetchall()
        conn.close()
        tasks = []
        for row_id, text, prio in rows:
            # Extract LinkedIn job ID if present
            m = re.search(r'\(ID:\s*(\d+)', text)
            job_id = m.group(1) if m else None
            tasks.append({'id': row_id, 'text': text, 'priority': prio, 'job_id': job_id})
        return tasks
    except Exception as e:
        print(f"[DB WARN] Cannot read tasks_queue: {e}")
        return []


# ── Enhanced apply_to_job with real submit ────────────────────────────────────
def apply_to_job_with_submit(applier, job: dict, page, submit: bool = False,
                             try_external: bool = False) -> tuple[bool, str]:
    """
    Extended version of apply_to_job that actually submits.
    submit=True: clicks Submit button after filling form
    submit=False: same as dry_run in V3 (fills but doesn't submit)
    """
    company = job.get('Company', 'Unknown')
    role    = job.get('Role', 'Unknown')
    url     = job.get('ApplyURL', '')
    fit     = job.get('FitScore', 0)

    print(f"\n{'='*70}")
    print(f"[APPLY] {company} - {role}")
    print(f"[FIT]   {fit}/10")
    print(f"[URL]   {url}")
    print(f"[MODE]  {'SUBMIT' if submit else 'DRY-RUN'}")
    print(f"{'='*70}")

    if not url:
        return False, "No URL"

    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    try:
        page.goto(url, timeout=30000)
        time.sleep(3)

        # ── CAPTCHA check inmediato post-navegación ──────────────────────────
        if is_captcha_page(page):
            resolved = handle_captcha(page, job)
            if not resolved:
                return False, "CAPTCHA no resuelto"
            # Volver a la URL del job tras resolver
            page.goto(url, timeout=30000)
            time.sleep(3)

        # Check for Easy Apply / LinkedIn Apply button
        # Cubre: EN ("Easy Apply"), ES ("Solicitud sencilla") y clase CSS jobs-apply-button
        # LinkedIn renombró "Easy Apply" → "LinkedIn Apply" / "Solicitud sencilla" en MX
        easy_apply = page.query_selector(
            'button:has-text("Easy Apply"), '
            'button:has-text("Solicitud sencilla"), '
            'button[aria-label*="Easy Apply"], '
            'button[aria-label*="easy apply"], '
            'button[aria-label*="Solicitud sencilla"], '
            'button.jobs-apply-button, '
            '.jobs-apply-button--top-card'
        )

        if not easy_apply:
            if try_external:
                print("[EXT] No Easy Apply — detecting external ATS...")

                # Strategy: click the Apply button and capture where LinkedIn redirects us.
                # LinkedIn opens external ATSs in a new tab (popup). We intercept it.
                ext_url = None

                # First try: find href on the Apply link directly (some LinkedIn pages have it)
                # Selectores EN + ES (mx.linkedin.com muestra UI en español)
                for sel in (
                    'a[data-tracking-control-name*="apply"]',
                    'a:has-text("Apply"):not([aria-label*="Easy"])',
                    'a:has-text("Solicitar"):not([aria-label*="Solicitud sencilla"])',
                    'a[href*="workable"], a[href*="greenhouse"], a[href*="lever.co"], '
                    'a[href*="smartrecruiters"], a[href*="bamboohr"], a[href*="ashby"]',
                ):
                    try:
                        el = page.query_selector(sel)
                        if el:
                            href = el.get_attribute("href") or ""
                            if href and "linkedin.com" not in href and href.startswith("http"):
                                ext_url = href
                                print(f"[EXT] Direct href found: {ext_url[:80]}")
                                break
                    except Exception:
                        pass

                # Second try: click Apply and capture the popup/new-tab URL
                # LI-03: el botón "Apply" en LinkedIn puede ser <a> no <button>
                # Agrega "Solicitar" para mx.linkedin.com (UI en español)
                if not ext_url:
                    apply_btn = page.query_selector(
                        'button:has-text("Apply"):not(:has-text("Easy")), '
                        'button:has-text("Solicitar"):not(:has-text("Solicitud")), '
                        'a.jobs-apply-button:not([aria-label*="Easy"]), '
                        'a[data-tracking-control-name*="apply"]:not([aria-label*="Easy"])'
                    )
                    if apply_btn:
                        try:
                            with page.expect_popup(timeout=8000) as popup_info:
                                apply_btn.click()
                            popup_page = popup_info.value
                            popup_page.wait_for_load_state("domcontentloaded", timeout=15000)
                            ext_url = popup_page.url
                            print(f"[EXT] Popup URL captured: {ext_url[:80]}")
                            popup_page.close()
                        except Exception:
                            # No popup — might navigate in same tab
                            try:
                                apply_btn.click()
                                page.wait_for_url(lambda u: "linkedin.com" not in u, timeout=8000)
                                ext_url = page.url
                                print(f"[EXT] Navigation URL: {ext_url[:80]}")
                            except Exception:
                                pass

                if not ext_url:
                    print("[SKIP] Could not resolve external apply URL")
                    return False, "Not Easy Apply — external URL not found"

                from core.automation.auto_apply_external import ExternalApplier, detect_platform
                platform = detect_platform(ext_url)
                print(f"[EXT] Platform: {platform.upper()} | {ext_url[:80]}")

                from playwright.async_api import async_playwright as _async_pw
                import asyncio

                headless_ext = getattr(page, '_headless_hint', False)

                async def _do_external():
                    ext_applier = ExternalApplier()
                    async with _async_pw() as pw:
                        browser2 = await pw.chromium.launch(
                            headless=headless_ext,
                            args=['--disable-blink-features=AutomationControlled']
                        )
                        ctx2  = await browser2.new_context(viewport={"width": 1280, "height": 900})
                        page2 = await ctx2.new_page()
                        # Pass the resolved external URL directly
                        job_ext = {**job, "ApplyURL": ext_url}
                        result  = await ext_applier.apply(page2, job_ext, submit=submit)
                        await browser2.close()
                        return result

                try:
                    ok_ext, reason_ext = asyncio.run(_do_external())
                    return ok_ext, reason_ext
                except Exception as e:
                    return False, f"External apply error: {e}"
            else:
                print("[SKIP] Not an Easy Apply job (--external disabled)")
                return False, "Not Easy Apply"

        print("[FOUND] Easy Apply button")

        if not submit:
            print("[DRY-RUN] Would click Easy Apply and fill form")
            return True, "Dry-run success"

        # Click Easy Apply
        easy_apply.click()
        time.sleep(2)

        modal = page.query_selector('[role="dialog"]')
        if not modal:
            print("[ERROR] Modal not found")
            return False, "Modal not found"

        print("[OK] Modal opened — filling form...")

        # Multi-step form
        max_steps = 6
        for step in range(1, max_steps + 1):
            print(f"  [STEP {step}] Analyzing form...")
            applier.handle_easy_apply_form(page)
            time.sleep(1.5)

            # Next/Continue button?
            next_btn = applier.check_for_next_step(page)
            if next_btn:
                print(f"  [NEXT] Clicking Continue (step {step})")
                next_btn.click()
                time.sleep(2)
                continue

            # Submit button?
            submit_btn = applier.check_for_submit(page)
            if submit_btn:
                print("  [SUBMIT] Clicking Submit application...")
                submit_btn.click()
                time.sleep(3)

                # Verify success
                success_indicators = [
                    page.query_selector('[data-test-modal="post-apply-modal"]'),
                    page.query_selector(':has-text("Application submitted")'),
                    page.query_selector(':has-text("Your application was sent")'),
                ]
                submitted = any(el is not None for el in success_indicators)

                if submitted:
                    print("  [SUCCESS] Application submitted!")
                    ss = take_screenshot(page, f"applied_{company[:25]}")
                    log.info(f"Aplicado: {company} — {role} | screenshot: {ss or 'N/A'}")
                    return True, "Applied"
                else:
                    # Check if we're on a confirmation page
                    if 'linkedin.com' in page.url:
                        print("  [SUCCESS?] Submit clicked — verifying...")
                        ss = take_screenshot(page, f"applied_verify_{company[:20]}")
                        log.info(f"Aplicado (verify): {company} — {role}")
                        return True, "Applied (verify)"
                    return False, "Submit clicked but unconfirmed"

            # Check for Close/Dismiss (already applied?)
            already = page.query_selector(':has-text("already applied")')
            if already:
                print("  [SKIP] Already applied to this job")
                return False, "Already applied"

            print(f"  [WARN] No Next or Submit found at step {step}")
            break

        return False, "Form incomplete"

    except PlaywrightTimeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def update_sheet_status(sheet_manager, job: dict, status: str, notes: str = ""):
    """Update job status in Google Sheets (uses _source_tab to write to the right tab)."""
    try:
        today    = datetime.now().strftime("%Y-%m-%d")
        tab_key  = job.get('_source_tab', 'linkedin')
        sheet_manager.update_job(
            job.get('_row', 0),
            {
                'Status': status,
                'NextAction': notes or status,
                'SLA_Date': today,
            },
            tab=tab_key,
        )
        print(f"  [SHEET] Status updated to '{status}' (tab: {tab_key})")
    except Exception as e:
        print(f"  [SHEET WARN] Could not update status: {e}")


def apply_external_direct(job: dict, submit: bool, headless: bool) -> tuple[bool, str]:
    """Apply directly to an external ATS URL (Computrabajo, OCC, Adzuna jobs).

    These jobs have URLs that go straight to Workable/Greenhouse/Lever/etc.
    We use ExternalApplier directly — no LinkedIn session needed.
    """
    import asyncio
    from playwright.async_api import async_playwright as _async_pw
    from core.automation.auto_apply_external import ExternalApplier

    url     = job.get('ApplyURL', '')
    company = job.get('Company', 'Unknown')
    role    = job.get('Role', 'Unknown')
    fit     = job.get('FitScore', '?')
    source  = job.get('_source_tab', 'external')

    print(f"\n{'='*70}")
    print(f"[APPLY-EXT] {company} - {role}")
    print(f"[FIT]       {fit}/10  |  [SOURCE] {source}")
    print(f"[URL]       {url}")
    print(f"[MODE]      {'SUBMIT' if submit else 'DRY-RUN'}")
    print(f"{'='*70}")

    async def _run():
        applier = ExternalApplier()
        # Use customized CV if pre-generated (FIT >= 8)
        if job.get('_cv_path'):
            from pathlib import Path as _Path
            cv_path_str = str(job['_cv_path'])
            if _Path(cv_path_str).exists():
                applier.cv['resume_path'] = cv_path_str
                print(f"  [CV] Using custom CV: {_Path(cv_path_str).name}")

        async with _async_pw() as pw:
            browser = await pw.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage']
            )
            ctx  = await browser.new_context(
                viewport={'width': 1280, 'height': 900},
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/124.0.0.0 Safari/537.36'
                ),
            )
            page = await ctx.new_page()
            try:
                result = await applier.apply(page, job, submit=submit)
            finally:
                await browser.close()
            return result

    try:
        return asyncio.run(_run())
    except Exception as e:
        return False, f"External direct apply error: {e}"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Apply Production Runner')
    parser.add_argument('--submit',     action='store_true', help='Actually submit applications')
    parser.add_argument('--dry-run',    action='store_true', help='Simulate without submitting')
    parser.add_argument('--headless',   action='store_true', help='Run browser headless (no window)')
    parser.add_argument('--max',        type=int, default=5,  help='Max applications (default: 5)')
    parser.add_argument('--min-fit',    type=float, default=7.0, help='Min FIT score (default: 7)')
    parser.add_argument('--job-id',     type=str, default='', help='Apply to specific LinkedIn job ID')
    parser.add_argument('--no-confirm', action='store_true', help='Skip 5-second safety pause (for pipeline use)')
    parser.add_argument('--no-external',  action='store_true',
                        help='Only attempt LinkedIn Easy Apply (skip external ATS sites)')
    parser.add_argument('--skip-cv-gen', action='store_true',
                        help='Skip AI CV customization — always use base CV (faster, no LLM call)')
    args = parser.parse_args()

    # external is ON by default; --no-external disables it
    args.external = not args.no_external

    # Default to dry-run if neither specified
    if not args.submit:
        args.dry_run = True

    print("=" * 70)
    print("LinkedIn Auto-Apply — Production Runner")
    mode_str = "SUBMIT (LIVE)" if args.submit else "DRY-RUN"
    ext_str  = " + External ATS" if args.external else " (Easy Apply only)"
    print(f"Mode: {mode_str}{ext_str} | Max: {args.max} | Min FIT: {args.min_fit} | Headless: {args.headless}")
    print("=" * 70)

    if args.submit and not args.no_confirm:
        print("\n[WARNING] LIVE mode — applications will be SUBMITTED!")
        print("Press Ctrl+C within 5 seconds to cancel...")
        time.sleep(5)
    elif args.submit and args.no_confirm:
        print("\n[WARNING] LIVE mode — applications will be SUBMITTED (pipeline mode, no pause)")

    from core.automation.linkedin_auto_apply import LinkedInAutoApplyV3
    from playwright.sync_api import sync_playwright

    applier = LinkedInAutoApplyV3()

    # Get jobs to process
    jobs_to_process = []

    if args.job_id:
        # Direct job ID mode
        jobs_to_process.append({
            'Company': 'Direct Apply',
            'Role': f'Job ID {args.job_id}',
            'ApplyURL': f'https://www.linkedin.com/jobs/view/{args.job_id}',
            'FitScore': 'N/A',
            '_row': 0,
        })
        print(f"\n[MODE] Direct apply to job ID: {args.job_id}")
    else:
        # From Sheet (FIT >= min_fit)
        jobs_to_process = applier.get_high_fit_jobs(min_score=args.min_fit)
        if not jobs_to_process:
            print("[INFO] No eligible jobs found in Sheet. Checking tasks_queue...")
            # Fallback: check tasks_queue for jobs with direct IDs
            pending_tasks = get_pending_apply_tasks()
            for task in pending_tasks:
                if task['job_id']:
                    jobs_to_process.append({
                        'Company': task['text'][:50],
                        'Role': 'From tasks_queue',
                        'ApplyURL': f'https://www.linkedin.com/jobs/view/{task["job_id"]}',
                        'FitScore': task['priority'],
                        '_row': 0,
                        '_task_id': task['id'],
                        '_task_text': task['text'],
                    })

    if not jobs_to_process:
        print("[INFO] No jobs to process. Done.")
        return

    jobs_to_process = jobs_to_process[:args.max]
    print(f"\n[PLAN] Processing {len(jobs_to_process)} jobs:")
    for i, j in enumerate(jobs_to_process, 1):
        print(f"  {i}. {j['Company']} - {j['Role']} (FIT: {j['FitScore']})")

    # ── CV resolution (before browser opens — fail fast on CV errors) ─────────
    if not args.skip_cv_gen:
        try:
            from core.automation.cv_customizer import get_cv_for_job
            log.info("[CV] Resolving CV paths (FIT>=8 → custom, FIT<8 → base)...")
            for job in jobs_to_process:
                job['_cv_path'] = get_cv_for_job(job)
                log.info(f"  [CV] {job['Company']}: {job['_cv_path'].name}")
        except Exception as e:
            log.warning(f"[CV] Customizer error ({e}) — all jobs will use base CV")
    else:
        log.info("[CV] --skip-cv-gen set — using base CV for all jobs")

    # Start browser
    results = {'applied': 0, 'failed': 0, 'skipped': 0}
    applied_jobs = []
    error_jobs   = []

    # ── Split jobs by apply route ─────────────────────────────────────────────
    linkedin_jobs = [j for j in jobs_to_process
                     if 'linkedin.com' in j.get('ApplyURL', '').lower()]
    external_jobs = [j for j in jobs_to_process
                     if 'linkedin.com' not in j.get('ApplyURL', '').lower()]

    log.info(f"Routing: {len(linkedin_jobs)} LinkedIn jobs | "
             f"{len(external_jobs)} direct external jobs")

    # ── Helper: record result ─────────────────────────────────────────────────
    def record(job, ok, reason):
        company = job.get('Company', 'Unknown')
        role    = job.get('Role', 'Unknown')
        fit     = job.get('FitScore', '?')
        if ok and args.submit:
            results['applied'] += 1
            applied_jobs.append(f"• {company} — {role} (FIT {fit})")
            if job.get('_row', 0) > 0:
                update_sheet_status(applier.sheet_manager, job, 'Applied', reason)
            else:
                log.info("Sheet skip (direct --job-id mode)")
            mark_task_done(job.get('_task_text', job.get('Company', ''))[:50])
        elif ok:
            results['applied'] += 1
            applied_jobs.append(f"• {company} — {role} [DRY-RUN]")
        elif any(k in reason.lower() for k in ('skip', 'already', 'not easy', 'no url', 'captcha')):
            results['skipped'] += 1
            log.info(f"Skipped: {company} — {reason}")
        else:
            results['failed'] += 1
            error_jobs.append(f"• {company} — {role}: {reason}")
            log.warning(f"Failed: {company} — {reason}")

    # ── 1. LinkedIn jobs (Easy Apply + external via LinkedIn redirect) ─────────
    if linkedin_jobs:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=args.headless,
                args=['--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage']
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()

            if not applier.ensure_linkedin_session(context, page):
                log.error("[ERROR] Could not establish LinkedIn session — skipping LinkedIn jobs")
                for job in linkedin_jobs:
                    record(job, False, "LinkedIn session failed")
            else:
                log.info("LinkedIn session active — processing LinkedIn jobs...")
                for job in linkedin_jobs:
                    ok, reason = apply_to_job_with_submit(
                        applier, job, page,
                        submit=args.submit,
                        try_external=getattr(args, 'external', False),
                    )
                    record(job, ok, reason)
                    time.sleep(5)

            if not args.headless:
                log.info("Browser open 10s for review...")
                time.sleep(10)
            browser.close()

    # ── 2. External direct jobs (Computrabajo, Adzuna, OCC → ATS directo) ─────
    if external_jobs:
        log.info(f"\nProcessing {len(external_jobs)} external direct jobs "
                 f"(Computrabajo / Adzuna / OCC)...")
        for job in external_jobs:
            ok, reason = apply_external_direct(
                job, submit=args.submit, headless=args.headless
            )
            record(job, ok, reason)
            time.sleep(3)

    # ── Summary ───────────────────────────────────────────────────────────────
    today = datetime.now().strftime('%d/%m/%Y %H:%M')
    mode_label = "LIVE" if args.submit else "DRY-RUN"

    log.info("=" * 60)
    log.info("RESUMEN AUTO-APPLY")
    log.info(f"  Aplicados: {results['applied']}")
    log.info(f"  Fallidos:  {results['failed']}")
    log.info(f"  Saltados:  {results['skipped']}")
    log.info("=" * 60)

    # ── Telegram summary ──────────────────────────────────────────────────────
    status_icon = "✅" if results['applied'] > 0 else "⚠️"
    jobs_list   = "\n".join(applied_jobs) if applied_jobs else "  (ninguno)"
    errors_list = ("\n<b>Errores:</b>\n" + "\n".join(error_jobs)) if error_jobs else ""

    tg_msg = (
        f"🤖 <b>Auto-Apply — {today}</b>\n"
        f"{status_icon} Modo: {mode_label}\n\n"
        f"📋 <b>{results['applied']}</b> aplicaciones enviadas:\n"
        f"{jobs_list}\n"
        f"⏭ Saltados: {results['skipped']}{errors_list}\n\n"
        f"<i>Revisa Google Sheets → pestaña LinkedIn</i>"
    )
    if send_telegram(tg_msg):
        log.info("Telegram enviado ✓")

    if args.dry_run and results['applied'] > 0:
        log.info(f"[TIP] Corre con --submit para aplicar a {results['applied']} job(s)")


if __name__ == '__main__':
    main()
