#!/usr/bin/env python3
"""
Clean Closed Jobs — LinkedIn Job Status Checker
================================================
Revisa cada job en el Sheet y detecta los que ya no aceptan aplicaciones:
  - "No longer accepting applications"
  - "Job no longer available"
  - "This job is no longer active"
  - La página devuelve 404 o redirige
  - Error al cargar (vacante eliminada)

Esos rows se ELIMINAN del Sheet (o se marcan con --mark en vez de borrar).

Uso:
  py scripts/maintenance/clean_closed_jobs.py             # revisa todos, borra cerrados
  py scripts/maintenance/clean_closed_jobs.py --dry-run  # solo muestra, no borra
  py scripts/maintenance/clean_closed_jobs.py --mark      # marca "Skip - Closed" en vez de borrar
  py scripts/maintenance/clean_closed_jobs.py --limit 30 # solo 30 jobs
  py scripts/maintenance/clean_closed_jobs.py --tab Indeed
"""
import sys
import re
import os
import time
import json
import argparse
import requests
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

SHEET_ID   = os.getenv('GOOGLE_SHEETS_ID')
TOKEN_PATH = Path(__file__).parent.parent.parent / 'data' / 'credentials' / 'token.json'
COOKIES_F  = Path(__file__).parent.parent.parent / 'data' / 'linkedin_cookies.json'

HEADERS_GUEST = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
    'Referer': 'https://www.linkedin.com/',
}

# Phrases that indicate a job is closed/unavailable
CLOSED_PHRASES = [
    'no longer accepting applications',
    'no longer available',
    'this job is closed',
    'this job is no longer active',
    'this position has been filled',
    'job posting has been removed',
    'ya no se aceptan solicitudes',
    'esta oferta ya no',
    'oferta no disponible',
    'no se aceptan',
    'puesto ya cubierto',
]

# Statuses that should be removed (cleanup stale data)
STALE_STATUSES = {
    'skip - closed',
    'skip - expired',
    'skip - no applications',
    'skip - duplicate',
    'expired',
    'closed',
    'no longer available',
}


def build_cookie_header() -> str | None:
    if not COOKIES_F.exists():
        return None
    try:
        cookies = json.loads(COOKIES_F.read_text())
        return '; '.join(
            f"{c['name']}={c['value']}"
            for c in cookies if c.get('domain', '').endswith('linkedin.com')
        )
    except Exception:
        return None


def check_job_status(url: str) -> tuple[bool, str]:
    """
    Check if a LinkedIn job is still open.
    Returns (is_closed: bool, reason: str)
    """
    if not url or 'linkedin.com' not in url.lower():
        return False, 'not_linkedin'

    # Extract job ID — use guest API for efficient check
    m = re.search(r'/jobs/(?:view|comm/jobs/view)/(\d+)', url)
    if not m:
        return False, 'no_job_id'

    job_id = m.group(1)
    api_url = f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}'

    headers = dict(HEADERS_GUEST)
    cookie_str = build_cookie_header()
    if cookie_str:
        headers['Cookie'] = cookie_str

    try:
        resp = requests.get(api_url, headers=headers, timeout=12, allow_redirects=True)

        if resp.status_code == 404:
            return True, 'HTTP 404 - job not found'

        if resp.status_code == 429:
            # Rate limit — don't mark as closed, just skip
            return False, 'rate_limited'

        if resp.status_code != 200:
            return False, f'HTTP {resp.status_code}'

        html_lower = resp.text.lower()

        # Check for closed indicators
        for phrase in CLOSED_PHRASES:
            if phrase in html_lower:
                return True, f'closed: "{phrase}"'

        # Check if page is essentially empty (< 500 chars usually means error page)
        if len(resp.text.strip()) < 300:
            return True, 'empty response (job likely deleted)'

        return False, 'open'

    except requests.Timeout:
        return False, 'timeout'
    except requests.RequestException as e:
        return False, f'request error: {e}'


def get_sheet(tab: str):
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ['https://www.googleapis.com/auth/spreadsheets']
    )
    return gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(tab)


def batch_delete_rows(ws, row_indices: list[int]):
    """Delete multiple rows using Sheets batchUpdate in a single API call."""
    if not row_indices:
        return 0

    sheet_id_num = ws.id
    # Sort descending so indices stay valid
    sorted_rows = sorted(set(row_indices), reverse=True)

    requests_body = []
    for sheet_row in sorted_rows:
        requests_body.append({
            "deleteDimension": {
                "range": {
                    "sheetId":    sheet_id_num,
                    "dimension":  "ROWS",
                    "startIndex": sheet_row - 1,  # 0-indexed
                    "endIndex":   sheet_row,
                }
            }
        })

    # Send in batches of 100
    deleted = 0
    batch_size = 100
    for i in range(0, len(requests_body), batch_size):
        batch = requests_body[i:i + batch_size]
        ws.spreadsheet.batch_update({"requests": batch})
        deleted += len(batch)
        if i + batch_size < len(requests_body):
            time.sleep(2)

    return deleted


def main():
    parser = argparse.ArgumentParser(description='Remove closed/expired LinkedIn jobs from Sheet')
    parser.add_argument('--dry-run', action='store_true', help='Solo preview, no cambios')
    parser.add_argument('--mark',    action='store_true', help='Marcar como Skip-Closed en vez de borrar')
    parser.add_argument('--limit',   type=int, default=0, help='Max jobs a revisar (0=todos)')
    parser.add_argument('--delay',   type=float, default=2.0, help='Delay entre requests (s)')
    parser.add_argument('--tab',     default='LinkedIn', help='Sheet tab (default: LinkedIn)')
    args = parser.parse_args()

    print("=" * 70)
    print("LinkedIn Job Status Checker — Remove Closed Jobs")
    mode = "DRY-RUN" if args.dry_run else ("MARK" if args.mark else "DELETE")
    print(f"Mode: {mode} | Tab: {args.tab} | Limit: {args.limit or 'all'}")
    print("=" * 70)

    ws = get_sheet(args.tab)
    all_vals = ws.get_all_values()
    headers = all_vals[0]

    col = {
        'company': next((i for i, h in enumerate(headers) if 'company' in h.lower()), 1),
        'role':    next((i for i, h in enumerate(headers) if h.lower() == 'role'), 2),
        'url':     next((i for i, h in enumerate(headers) if 'applyurl' in h.lower()), 5),
        'status':  next((i for i, h in enumerate(headers) if 'status' in h.lower()), 12),
    }

    # Build list of checkable rows
    # Check: New status jobs + any stale-status jobs (for cleanup)
    checkable = []
    stale_rows = []

    for sheet_row, row in enumerate(all_vals[1:], start=2):
        url    = row[col['url']]    if len(row) > col['url']    else ''
        status = row[col['status']] if len(row) > col['status'] else ''
        company = row[col['company']] if len(row) > col['company'] else ''

        # Already closed/expired status → queue for immediate deletion
        if status.lower() in STALE_STATUSES:
            stale_rows.append(sheet_row)
            continue

        # Skip already applied or skipped for other reasons
        if any(x in status.lower() for x in ('applied', 'application submitted')):
            continue

        if 'linkedin.com' in url.lower() and url:
            checkable.append({'sheet_row': sheet_row, 'url': url, 'company': company,
                              'status': status, 'role': row[col['role']] if len(row) > col['role'] else ''})

    print(f"\n[SCAN] Total rows: {len(all_vals)-1}")
    print(f"[SCAN] Jobs to check: {len(checkable)}")
    if stale_rows:
        print(f"[SCAN] Already-stale rows (immediate delete): {len(stale_rows)}")

    if args.limit > 0:
        checkable = checkable[:args.limit]
        print(f"[LIMIT] Checking first {len(checkable)}")

    rows_to_remove = list(stale_rows)
    closed_jobs = []

    for i, job in enumerate(checkable, 1):
        print(f"\n[{i}/{len(checkable)}] Checking: {job['company']} — {job['role'][:50]}")
        print(f"  URL: {job['url'][:70]}")

        is_closed, reason = check_job_status(job['url'])

        if reason == 'rate_limited':
            print("  [RATE LIMIT] Waiting 30s...")
            time.sleep(30)
            is_closed, reason = check_job_status(job['url'])

        if is_closed:
            print(f"  [CLOSED] {reason}")
            rows_to_remove.append(job['sheet_row'])
            closed_jobs.append({**job, 'reason': reason})
        else:
            print(f"  [OK] {reason}")

        if i < len(checkable):
            time.sleep(args.delay)

    print(f"\n{'='*70}")
    print(f"FOUND {len(rows_to_remove)} rows to remove:")
    print(f"  - Already stale: {len(stale_rows)}")
    print(f"  - Newly detected closed: {len(closed_jobs)}")

    if not rows_to_remove:
        print("\n[CLEAN] All checked jobs are still open!")
        return

    if args.dry_run:
        print("\n[DRY-RUN] Would remove:")
        for j in closed_jobs:
            print(f"  Row {j['sheet_row']}: {j['company']} — {j['reason']}")
        return

    if args.mark:
        # Mark as Skip - Closed instead of deleting
        status_col_idx = col['status'] + 1
        updates = []
        for j in closed_jobs:
            updates.append(gspread.Cell(j['sheet_row'], status_col_idx, 'Skip - Closed'))
        if stale_rows:
            print(f"  [INFO] {len(stale_rows)} already-stale rows left as-is (already marked)")
        if updates:
            ws.update_cells(updates)
            print(f"\n[OK] Marked {len(updates)} rows as 'Skip - Closed'")
    else:
        # DELETE (default)
        deleted = batch_delete_rows(ws, rows_to_remove)
        print(f"\n[OK] Deleted {deleted} closed/stale job rows from Sheet")

    print("\n[DONE] Clean complete!")
    remaining = len(all_vals) - 1 - len(rows_to_remove)
    print(f"[INFO] Approx. {remaining} active job rows remain in {args.tab} tab")


if __name__ == '__main__':
    main()
