#!/usr/bin/env python3
"""
Enrich Unknown Jobs — LinkedIn Job Detail Fetcher
=================================================
Busca en el Sheet de LinkedIn los rows donde Company='Unknown'
o Role contiene 'Pending AI Analysis', extrae el LinkedIn Job ID
de la URL, hace fetch del detalle de la vacante y actualiza el Sheet.

Usa la API pública de LinkedIn (no requiere login) más fallback con cookies.

Uso:
  py scripts/maintenance/enrich_unknown_jobs.py             # procesa todos
  py scripts/maintenance/enrich_unknown_jobs.py --dry-run  # solo muestra
  py scripts/maintenance/enrich_unknown_jobs.py --limit 20 # solo 20 filas
"""
import sys
import re
import time
import json
import argparse
import requests
import os
from pathlib import Path
from datetime import datetime

# Windows UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
SHEET_ID   = os.getenv('GOOGLE_SHEETS_ID')
TOKEN_PATH = Path(__file__).parent.parent.parent / 'data' / 'credentials' / 'token.json'
COOKIES_F  = Path(__file__).parent.parent.parent / 'data' / 'linkedin_cookies.json'

LINKEDIN_GUEST_API = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

HEADERS_GUEST = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
    'Referer': 'https://www.linkedin.com/',
}

# ── LinkedIn fetch ────────────────────────────────────────────────────────────
def build_cookie_header():
    """Build Cookie header string from saved linkedin_cookies.json"""
    if not COOKIES_F.exists():
        return None
    try:
        cookies = json.loads(COOKIES_F.read_text())
        return '; '.join(f"{c['name']}={c['value']}" for c in cookies if c.get('domain', '').endswith('linkedin.com'))
    except Exception:
        return None


def fetch_job_details(job_id: str, use_cookies: bool = True) -> dict:
    """
    Fetch job title, company, location from LinkedIn.
    Returns dict with keys: title, company, location, description (truncated)
    """
    url = LINKEDIN_GUEST_API.format(job_id=job_id)
    headers = dict(HEADERS_GUEST)

    if use_cookies:
        cookie_str = build_cookie_header()
        if cookie_str:
            headers['Cookie'] = cookie_str

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return parse_job_html(resp.text, job_id)
        elif resp.status_code == 429:
            print(f"  [RATE LIMIT] Job {job_id} — waiting 30s")
            time.sleep(30)
            return fetch_job_details(job_id, use_cookies=use_cookies)
        else:
            print(f"  [HTTP {resp.status_code}] Job {job_id}")
            return {}
    except requests.RequestException as e:
        print(f"  [ERROR] Job {job_id}: {e}")
        return {}


def parse_job_html(html: str, job_id: str) -> dict:
    """Parse company, title, location from LinkedIn job page HTML"""
    result = {'job_id': job_id}

    # Title — <h2 class="...top-card-layout__title...">
    title_match = re.search(
        r'<h2[^>]*(?:top-card-layout__title|job-details-jobs-unified-top-card__job-title)[^>]*>\s*(.*?)\s*</h2>',
        html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        result['title'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()

    # Company — <a class="...topcard__org-name-link...">
    company_match = re.search(
        r'<a[^>]*(?:topcard__org-name-link|job-details-jobs-unified-top-card__company-name)[^>]*>\s*(.*?)\s*</a>',
        html, re.IGNORECASE | re.DOTALL
    )
    if company_match:
        result['company'] = re.sub(r'<[^>]+>', '', company_match.group(1)).strip()

    # Fallback: look for og:title meta
    if 'title' not in result:
        og_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
        if og_match:
            val = og_match.group(1).strip()
            # Format is usually "Job Title at Company | LinkedIn"
            at_match = re.match(r'^(.+?)\s+(?:at|en|@)\s+(.+?)(?:\s*\||\s*$)', val)
            if at_match:
                result['title']   = at_match.group(1).strip()
                result['company'] = at_match.group(2).strip()
            else:
                result['title'] = val.replace(' | LinkedIn', '').strip()

    # Location
    loc_match = re.search(
        r'<span[^>]*(?:topcard__flavor--bullet|job-details-jobs-unified-top-card__bullet)[^>]*>\s*(.*?)\s*</span>',
        html, re.IGNORECASE | re.DOTALL
    )
    if loc_match:
        result['location'] = re.sub(r'<[^>]+>', '', loc_match.group(1)).strip()

    # Description snippet (first 400 chars)
    desc_match = re.search(
        r'<div[^>]*(?:description__text|jobs-description__content)[^>]*>(.*?)</div>',
        html, re.IGNORECASE | re.DOTALL
    )
    if desc_match:
        raw = re.sub(r'<[^>]+>', ' ', desc_match.group(1))
        result['description'] = re.sub(r'\s+', ' ', raw).strip()[:400]

    return result


# ── Sheet management ──────────────────────────────────────────────────────────
def get_sheet(tab: str = 'LinkedIn'):
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH),
        ['https://www.googleapis.com/auth/spreadsheets']
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(tab)


def extract_job_id(url: str) -> str | None:
    """Extract LinkedIn job ID from URL"""
    m = re.search(r'/jobs/(?:view|comm/jobs/view)/(\d+)', url)
    return m.group(1) if m else None


def get_unknown_rows(ws, headers: list) -> list[dict]:
    """Return rows where company is Unknown or role is Pending AI Analysis"""
    all_vals = ws.get_all_values()

    company_col = next((i for i, h in enumerate(headers) if 'company' in h.lower()), 1)
    role_col    = next((i for i, h in enumerate(headers) if h.lower() == 'role'), 2)
    url_col     = next((i for i, h in enumerate(headers) if 'applyurl' in h.lower()), 5)
    status_col  = next((i for i, h in enumerate(headers) if 'status' in h.lower()), 12)
    fit_col     = next((i for i, h in enumerate(headers) if 'fitscore' in h.lower()), 17)

    result = []
    seen_job_ids = set()  # track to avoid duplicate fetches

    for sheet_row, row in enumerate(all_vals[1:], start=2):
        company = row[company_col] if len(row) > company_col else ''
        role    = row[role_col]    if len(row) > role_col    else ''
        url     = row[url_col]     if len(row) > url_col     else ''
        status  = row[status_col]  if len(row) > status_col  else ''
        fit     = row[fit_col]     if len(row) > fit_col     else ''

        # Skip already applied
        if status.lower() in ('applied', 'skip', 'rejected'):
            continue

        is_unknown = ('unknown' in company.lower() or 'pending' in role.lower())
        if not is_unknown:
            continue

        job_id = extract_job_id(url)
        if not job_id:
            continue

        # Don't fetch same job ID twice
        if job_id in seen_job_ids:
            continue
        seen_job_ids.add(job_id)

        result.append({
            'sheet_row': sheet_row,
            'job_id': job_id,
            'url': url,
            'company': company,
            'role': role,
            'fit': fit,
            'status': status,
            # column indices for update
            'company_col': company_col + 1,  # gspread uses 1-indexed
            'role_col':    role_col + 1,
            'url_col':     url_col + 1,
        })

    return result


def update_row(ws, row_info: dict, details: dict, dry_run: bool = False):
    """Update Sheet row with fetched job details"""
    new_company  = details.get('company', row_info['company'])
    new_role     = details.get('title',   row_info['role'])
    new_location = details.get('location', '')

    if not new_company or new_company.lower() in ('unknown', 'none', ''):
        new_company = row_info['company']  # keep original
    if not new_role or 'pending' in new_role.lower():
        new_role = row_info['role']  # keep original

    print(f"  -> Company: {new_company}")
    print(f"  -> Role:    {new_role}")
    if new_location:
        print(f"  -> Location:{new_location}")

    if dry_run:
        print("  [DRY-RUN] Would update Sheet")
        return

    updates = []
    if new_company != row_info['company']:
        updates.append(gspread.Cell(row_info['sheet_row'], row_info['company_col'], new_company))
    if new_role != row_info['role']:
        updates.append(gspread.Cell(row_info['sheet_row'], row_info['role_col'], new_role))

    # Location: find or skip (column may not exist)
    if updates:
        ws.update_cells(updates)
        print("  [OK] Sheet updated")
    else:
        print("  [SKIP] Nothing changed")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Enrich Unknown LinkedIn jobs')
    parser.add_argument('--dry-run', action='store_true', help='Do not write to Sheet')
    parser.add_argument('--limit', type=int, default=0, help='Max rows to process (0=all)')
    parser.add_argument('--delay', type=float, default=2.5, help='Delay between requests (s)')
    parser.add_argument('--tab',   default='LinkedIn', help='Sheet tab (default: LinkedIn)')
    args = parser.parse_args()

    print("=" * 70)
    print("LinkedIn Job Enricher - Unknown Company/Role Filler")
    print(f"Tab: {args.tab} | Dry-run: {args.dry_run} | Limit: {args.limit or 'all'} | Delay: {args.delay}s")
    print("=" * 70)

    print("\n[SHEET] Connecting to Google Sheets...")
    ws = get_sheet(args.tab)
    headers = ws.row_values(1)
    print(f"[OK] Connected. Columns: {headers[:10]}...")

    rows = get_unknown_rows(ws, headers)
    print(f"\n[FOUND] {len(rows)} unknown jobs with LinkedIn job IDs")

    if args.limit > 0:
        rows = rows[:args.limit]
        print(f"[LIMIT] Processing first {len(rows)} rows")

    enriched = 0
    failed   = 0

    for i, row_info in enumerate(rows, 1):
        print(f"\n[{i}/{len(rows)}] Job ID: {row_info['job_id']} (Row {row_info['sheet_row']})")
        print(f"  Current: {row_info['company']} | {row_info['role']}")

        details = fetch_job_details(row_info['job_id'])

        if details.get('title') or details.get('company'):
            update_row(ws, row_info, details, dry_run=args.dry_run)
            enriched += 1
        else:
            print(f"  [FAILED] Could not fetch details for job {row_info['job_id']}")
            failed += 1

        if i < len(rows):
            time.sleep(args.delay)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"  Enriched: {enriched}")
    print(f"  Failed:   {failed}")
    print(f"  Total:    {len(rows)}")
    print("=" * 70)

    if enriched > 0 and not args.dry_run:
        print(f"\n[OK] {enriched} jobs updated in Google Sheet!")
        print("[TIP] Run recalculate_fit_scores.py to re-score with real job titles")


if __name__ == '__main__':
    main()
