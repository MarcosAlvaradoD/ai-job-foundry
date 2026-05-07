#!/usr/bin/env python3
"""
AI JOB FOUNDRY - ADZUNA MX SCRAPER (REST API)
==============================================
Scraper de Adzuna México usando su API pública.
No requiere browser — puro HTTP REST JSON.

Límites free tier: 250 calls/day, 2500/month
Nuestro uso: ~15-20 queries/día → bien dentro del límite

Registro: developer.adzuna.com
Secrets GHA: ADZUNA_APP_ID, ADZUNA_APP_KEY
"""
import sys, os, asyncio
import urllib.request
import urllib.parse
import json
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ingestion.queries import get_mexico_queries, get_latam_queries
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'
CYAN  = '\033[96m'; END = '\033[0m'

ADZUNA_HEADERS = [
    'Role', 'Company', 'Location', 'ApplyURL', 'Source',
    'SearchQuery', 'QuerySource', 'DateFound', 'Status', 'RemoteScope',
    'SalaryMin', 'SalaryMax',
]

_API_BASE    = "https://api.adzuna.com/v1/api/jobs/mx/search"
_APP_ID      = os.getenv("ADZUNA_APP_ID",  "").strip()
_APP_KEY     = os.getenv("ADZUNA_APP_KEY", "").strip()
_MAX_RESULTS = 50    # max per API call (Adzuna cap)
_MAX_AGE     = 14    # only jobs from last 14 days


def _detect_remote(text: str) -> str:
    t = text.lower()
    if "remot" in t or "home office" in t or "trabajo remoto" in t:
        return "Remote"
    if "híbrid" in t or "hybrid" in t:
        return "Hybrid"
    return "OnSite"


def _fetch_json(url: str, retries: int = 3, backoff: float = 5.0) -> dict | None:
    """Fetch Adzuna API endpoint and return parsed JSON, or None on error."""
    req = urllib.request.Request(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"  {RED}Adzuna 401 — verifica ADZUNA_APP_ID y ADZUNA_APP_KEY{END}")
                return None  # no point retrying auth errors
            if e.code == 429:
                print(f"  {YELLOW}Adzuna 429 rate-limit — esperando {backoff*2}s{END}")
                time.sleep(backoff * 2)
            last_exc = e
        except Exception as exc:
            last_exc = exc
        if attempt < retries:
            print(f"  {YELLOW}Adzuna fetch attempt {attempt}/{retries}: {last_exc} — retry in {backoff}s{END}")
            time.sleep(backoff)
    print(f"  {RED}Adzuna fetch failed ({retries} attempts): {last_exc}{END}")
    return None


class AdzunaScraper:
    def __init__(self, headless: bool = None):
        # headless param kept for interface parity — not used (no browser)
        self.headless       = headless
        self.jobs_found: list[dict] = []
        self.dry_run        = True
        self.sheet_manager  = None
        self._calls_today   = 0

    async def run(self, dry_run: bool = True):
        self.dry_run = dry_run
        if not dry_run:
            self.sheet_manager = SheetManager()

        print(f"\n{CYAN}{'='*70}")
        print(f"ADZUNA MX SCRAPER  (REST API, no browser)")
        print(f"{'='*70}{END}")

        if not _APP_ID or not _APP_KEY:
            print(f"{RED}❌ ADZUNA_APP_ID / ADZUNA_APP_KEY no configurados{END}")
            print(f"   Regístrate en developer.adzuna.com y agrega los secrets")
            return

        print(f"Mode:   {YELLOW}{'DRY RUN' if dry_run else 'LIVE'}{END}")
        print(f"App ID: {_APP_ID[:8]}***")
        print(f"Limits: 250 calls/day, 2500/month\n")

        for query, source in get_mexico_queries("en"):
            self._search(query, source)
            await asyncio.sleep(1)   # gentle rate control

        for query, source in get_latam_queries("en"):
            self._search(query, source)
            await asyncio.sleep(1)

        self._print_summary()

        if not dry_run and self.jobs_found:
            self._save_to_sheets()

    def _search(self, query: str, query_source: str):
        """Call Adzuna search API for one query and collect results."""
        print(f"\n{CYAN}[Adzuna] Searching: {query}{END}")

        params = {
            "app_id":           _APP_ID,
            "app_key":          _APP_KEY,
            "results_per_page": _MAX_RESULTS,
            "what":             query,
            "max_days_old":     _MAX_AGE,
            "sort_by":          "date",
            "content-type":     "application/json",
        }
        url = f"{_API_BASE}/1?{urllib.parse.urlencode(params)}"

        data = _fetch_json(url)
        if not data:
            return

        results = data.get("results", [])
        self._calls_today += 1
        print(f"  API results: {len(results)} (total available: {data.get('count', '?')})")

        count = 0
        for job in results:
            try:
                title   = (job.get("title") or "").strip()
                company = (job.get("company", {}) or {}).get("display_name", "").strip()

                # Location: Adzuna returns area as a list, e.g. ["México", "Ciudad de México"]
                area    = (job.get("location", {}) or {}).get("area", [])
                location = ", ".join(area[-2:]) if area else "México"   # last 2 = most specific

                apply_url   = (job.get("redirect_url") or "").strip()
                salary_min  = job.get("salary_min") or ""
                salary_max  = job.get("salary_max") or ""
                description = (job.get("description") or "")

                if not title or not apply_url:
                    continue

                remote = _detect_remote(title + " " + description + " " + location)

                self.jobs_found.append({
                    'Role':        title[:100],
                    'Company':     company[:100],
                    'Location':    location[:100],
                    'ApplyURL':    apply_url,
                    'Source':      'Adzuna MX',
                    'SearchQuery': query,
                    'QuerySource': query_source,
                    'CreatedAt':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                    'Status':      'New',
                    'RemoteScope': remote,
                    'SalaryMin':   str(salary_min),
                    'SalaryMax':   str(salary_max),
                })
                count += 1
            except Exception:
                continue

        print(f"  {GREEN}Parsed {count} jobs  (API calls today: {self._calls_today}){END}")

    def _print_summary(self):
        print(f"\n{CYAN}{'='*70}")
        print(f"ADZUNA SCRAPING SUMMARY")
        print(f"{'='*70}{END}")
        print(f"  Total: {GREEN}{len(self.jobs_found)}{END}")
        print(f"  API calls used: {self._calls_today}/250 daily budget")
        by_source: dict[str, int] = {}
        for j in self.jobs_found:
            k = j['QuerySource']
            by_source[k] = by_source.get(k, 0) + 1
        for k, v in by_source.items():
            print(f"    {k}: {v} jobs")

    def _save_to_sheets(self):
        print(f"\n{CYAN}Saving to Google Sheets → Adzuna tab...{END}")
        try:
            self.sheet_manager.ensure_headers('adzuna', ADZUNA_HEADERS)
            existing_urls: set[str] = set()
            try:
                rows = self.sheet_manager.get_all_jobs(tab='adzuna')
                existing_urls = {r.get('ApplyURL', '') for r in rows}
            except Exception:
                pass

            new_jobs = [j for j in self.jobs_found if j['ApplyURL'] not in existing_urls]
            if not new_jobs:
                print(f"  {YELLOW}No new jobs (all duplicates){END}")
                return

            tab_name = self.sheet_manager.tabs['adzuna']
            headers  = self.sheet_manager._get_headers(tab_name)
            rows_out = [[str(j.get(h, '') or '') for h in headers] for j in new_jobs]
            self.sheet_manager.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab_name}!A2",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows_out},
            ).execute()
            print(f"  {GREEN}Saved {len(new_jobs)} new jobs to Adzuna tab{END}")
        except Exception as e:
            print(f"  {RED}Error saving to Sheets: {e}{END}")
            raise
