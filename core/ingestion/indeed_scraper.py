#!/usr/bin/env python3
"""
AI JOB FOUNDRY - INDEED MX SCRAPER (RSS)
=========================================
Scraper de Indeed México usando el feed RSS público.
Mucho más estable en CI/headless que Playwright — no requiere browser.
Escribe resultados directamente a la pestaña "Indeed" de Google Sheets.
No requiere autenticación — Indeed RSS es público.
"""
import sys, os, asyncio
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ingestion.queries import get_mexico_queries, get_latam_queries
from core.sheets.sheet_manager import SheetManager

GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'
CYAN  = '\033[96m'; END = '\033[0m'

INDEED_HEADERS = [
    'Role', 'Company', 'Location', 'ApplyURL', 'Source',
    'SearchQuery', 'QuerySource', 'DateFound', 'Status', 'RemoteScope',
]

_RSS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def _fetch_rss(url: str, retries: int = 3, backoff: float = 3.0):
    """
    Fetch an RSS URL synchronously and return raw XML text, or None on error.
    Retries up to `retries` times with `backoff` seconds between attempts.
    Returns None if the response looks like an HTML page (anti-bot block).
    """
    import time as _time
    req = urllib.request.Request(url, headers=_RSS_HEADERS)
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                text = resp.read().decode("utf-8", errors="replace")
                # Detect HTML block page (Indeed returns HTML on bot detection)
                stripped = text.lstrip()
                if stripped.startswith("<!") or stripped[:5].lower().startswith("<html"):
                    print(f"  {YELLOW}RSS returned HTML (anti-bot block?) — skipping{END}")
                    return None
                return text
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                print(f"  {YELLOW}RSS fetch attempt {attempt}/{retries} failed: {exc} — retrying in {backoff}s{END}")
                _time.sleep(backoff)
    print(f"  {RED}RSS fetch error (all {retries} attempts): {last_exc}{END}")
    return None


def _parse_location_from_description(desc: str) -> str:
    """Extract 'Location: ...' line from Indeed RSS <description> HTML."""
    if not desc:
        return "México"
    for line in desc.replace("<br>", "\n").replace("<br/>", "\n").splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("location:"):
            return stripped.split(":", 1)[1].strip() or "México"
    return "México"


def _detect_remote(title: str, description: str) -> str:
    combined = (title + " " + description).lower()
    if "remot" in combined or "home office" in combined or "trabajo remoto" in combined:
        return "Remote"
    if "híbrid" in combined or "hybrid" in combined:
        return "Hybrid"
    return "OnSite"


class IndeedScraper:
    def __init__(self, headless: bool = None):
        # headless param kept for interface compatibility with run_scraper_ci.py
        # RSS mode does not launch a browser, so this is intentionally ignored.
        self.headless = headless
        self.jobs_found: list[dict] = []
        self.dry_run = True
        self.sheet_manager = None

    async def run(self, dry_run: bool = True):
        self.dry_run = dry_run
        if not dry_run:
            self.sheet_manager = SheetManager()

        print(f"\n{CYAN}{'='*70}")
        print(f"INDEED MX SCRAPER  (RSS mode — no browser required)")
        print(f"{'='*70}{END}")
        print(f"Mode: {YELLOW}{'DRY RUN' if dry_run else 'LIVE'}{END}\n")

        for query, source in get_mexico_queries("en"):
            self._search_rss(query, source, remote=False)
            await asyncio.sleep(1)
            self._search_rss(query, source, remote=True)
            await asyncio.sleep(1)

        for query, source in get_latam_queries("en"):
            self._search_rss(query, source, remote=True)
            await asyncio.sleep(1)

        self._print_summary()

        if not dry_run and self.jobs_found:
            self._save_to_sheets()

    def _search_rss(self, query: str, query_source: str, remote: bool = False):
        """Fetch one Indeed RSS page and parse job items into self.jobs_found."""
        label = f"{query} [remote]" if remote else query
        print(f"\n{CYAN}[Indeed RSS] Searching: {label}{END}")

        if remote:
            q_encoded = urllib.parse.quote_plus(query + " remote")
            url = f"https://mx.indeed.com/rss?q={q_encoded}&sort=date&fromage=7"
        else:
            q_encoded = urllib.parse.quote_plus(query)
            url = f"https://mx.indeed.com/rss?q={q_encoded}&l=M%C3%A9xico&sort=date&fromage=7"

        xml_text = _fetch_rss(url)
        if not xml_text:
            return

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            print(f"  {RED}RSS parse error: {exc}{END}")
            return

        channel = root.find("channel")
        if channel is None:
            print(f"  {YELLOW}No <channel> in RSS response{END}")
            return

        items = channel.findall("item")
        print(f"  Found {len(items)} items in RSS feed")

        count = 0
        for item in items[:20]:
            try:
                title = (item.findtext("title") or "").strip()
                link  = (item.findtext("link")  or "").strip()
                # <source> in Indeed RSS carries the company name
                company_el = item.find("source")
                company = (company_el.text or "").strip() if company_el is not None else ""
                description = item.findtext("description") or ""

                if not title or not link:
                    continue

                location     = _parse_location_from_description(description)
                remote_scope = _detect_remote(title, description)

                job = {
                    'Role':        title[:100],
                    'Company':     company[:100],
                    'Location':    location[:100],
                    'ApplyURL':    link,
                    'Source':      'Indeed MX',
                    'SearchQuery': query,
                    'QuerySource': query_source,
                    'CreatedAt':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                    'Status':      'New',
                    'RemoteScope': remote_scope,
                }
                self.jobs_found.append(job)
                count += 1
            except Exception:
                continue

        print(f"  {GREEN}Parsed {count} jobs{END}")

    def _print_summary(self):
        print(f"\n{CYAN}{'='*70}")
        print(f"INDEED SCRAPING SUMMARY")
        print(f"{'='*70}{END}")
        print(f"  Total: {GREEN}{len(self.jobs_found)}{END}")
        by_source: dict[str, int] = {}
        for j in self.jobs_found:
            k = j['QuerySource']
            by_source[k] = by_source.get(k, 0) + 1
        for k, v in by_source.items():
            print(f"    {k}: {v} jobs")

    def _save_to_sheets(self):
        print(f"\n{CYAN}Saving to Google Sheets → Indeed tab...{END}")
        try:
            self.sheet_manager.ensure_headers('indeed', INDEED_HEADERS)
            existing_urls: set[str] = set()
            try:
                rows = self.sheet_manager.get_all_jobs(tab='indeed')
                existing_urls = {r.get('ApplyURL', '') for r in rows}
            except Exception:
                pass

            new_jobs = [j for j in self.jobs_found if j['ApplyURL'] not in existing_urls]
            if not new_jobs:
                print(f"  {YELLOW}No new jobs (all duplicates){END}")
                return

            tab_name = self.sheet_manager.tabs['indeed']
            headers  = self.sheet_manager._get_headers(tab_name)
            rows_out = [[str(j.get(h, '') or '') for h in headers] for j in new_jobs]
            self.sheet_manager.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab_name}!A2",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows_out},
            ).execute()
            print(f"  {GREEN}Saved {len(new_jobs)} new jobs to Indeed tab{END}")
        except Exception as e:
            print(f"  {RED}Error saving to Sheets: {e}{END}")
            raise
