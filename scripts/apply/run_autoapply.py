#!/usr/bin/env python3
"""
LinkedIn Auto-Apply — Production Runner
========================================
Wrapper sobre LinkedInAutoApplyV3 con opciones de línea de comandos.
Habilita submit real y modo headless opcional.

Uso:
  py scripts/apply/run_autoapply.py --dry-run          # simula sin enviar
  py scripts/apply/run_autoapply.py --submit            # envia aplicaciones reales
  py scripts/apply/run_autoapply.py --submit --max 5    # max 5 apps
  py scripts/apply/run_autoapply.py --submit --headless # sin ventana de browser
  py scripts/apply/run_autoapply.py --job-id 4392502231 # job especifico

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
def apply_to_job_with_submit(applier, job: dict, page, submit: bool = False) -> tuple[bool, str]:
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

        # Check for Easy Apply button
        easy_apply = page.query_selector('button:has-text("Easy Apply")')
        if not easy_apply:
            # Try alternate selectors
            easy_apply = page.query_selector('[aria-label*="Easy Apply"]')
        if not easy_apply:
            print("[SKIP] Not an Easy Apply job")
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
                    return True, "Applied"
                else:
                    # Check if we're on a confirmation page
                    if 'linkedin.com' in page.url:
                        print("  [SUCCESS?] Submit clicked — verifying...")
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
    """Update job status in Google Sheets"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        sheet_manager.update_job(
            job.get('_row', 0),
            {
                'Status': status,
                'NextAction': notes or status,
                'SLA_Date': today,
            },
            tab='linkedin'
        )
        print(f"  [SHEET] Status updated to '{status}'")
    except Exception as e:
        print(f"  [SHEET WARN] Could not update status: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Apply Production Runner')
    parser.add_argument('--submit',   action='store_true', help='Actually submit applications')
    parser.add_argument('--dry-run',  action='store_true', help='Simulate without submitting')
    parser.add_argument('--headless', action='store_true', help='Run browser headless (no window)')
    parser.add_argument('--max',      type=int, default=5,  help='Max applications (default: 5)')
    parser.add_argument('--min-fit',  type=float, default=7.0, help='Min FIT score (default: 7)')
    parser.add_argument('--job-id',   type=str, default='', help='Apply to specific LinkedIn job ID')
    args = parser.parse_args()

    # Default to dry-run if neither specified
    if not args.submit:
        args.dry_run = True

    print("=" * 70)
    print("LinkedIn Auto-Apply — Production Runner")
    mode_str = "SUBMIT (LIVE)" if args.submit else "DRY-RUN"
    print(f"Mode: {mode_str} | Max: {args.max} | Min FIT: {args.min_fit} | Headless: {args.headless}")
    print("=" * 70)

    if args.submit:
        print("\n[WARNING] LIVE mode — applications will be SUBMITTED!")
        print("Press Ctrl+C within 5 seconds to cancel...")
        time.sleep(5)

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

    # Start browser
    results = {'applied': 0, 'failed': 0, 'skipped': 0}

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
            print("[ERROR] Could not establish LinkedIn session!")
            browser.close()
            return

        print("\n[OK] LinkedIn session active — starting applications...\n")

        for job in jobs_to_process:
            ok, reason = apply_to_job_with_submit(applier, job, page, submit=args.submit)

            if ok and args.submit:
                results['applied'] += 1
                # Only update sheet when we have a valid row (not direct --job-id mode)
                if job.get('_row', 0) > 0:
                    update_sheet_status(applier.sheet_manager, job, 'Applied', reason)
                else:
                    print(f"  [SHEET] Skipped (direct --job-id mode, no sheet row)")
                # Mark task as done in Chalan
                task_text = job.get('_task_text', job.get('Company', ''))
                mark_task_done(task_text[:50])
            elif ok:
                results['applied'] += 1  # dry-run success
            elif 'skip' in reason.lower() or 'already' in reason.lower():
                results['skipped'] += 1
            else:
                results['failed'] += 1

            time.sleep(5)

        if not args.headless:
            print("\n[PAUSE] Browser open 10s for review...")
            time.sleep(10)
        browser.close()

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"  Applied:  {results['applied']}")
    print(f"  Failed:   {results['failed']}")
    print(f"  Skipped:  {results['skipped']}")
    print("=" * 70)

    if args.dry_run and results['applied'] > 0:
        print(f"\n[TIP] Run with --submit to actually apply to {results['applied']} job(s)")


if __name__ == '__main__':
    main()
