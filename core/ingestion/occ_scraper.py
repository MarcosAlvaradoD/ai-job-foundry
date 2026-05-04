#!/usr/bin/env python3
"""
AI JOB FOUNDRY - OCC MUNDIAL MX SCRAPER (RSS + JSON-LD)
=========================================================
Scraper de OCC Mundial México.
Strategy 1: RSS feed (público, sin browser, más estable)
Strategy 2: HTTP + JSON-LD structured data fallback

OCC Mundial es el job board más grande de México con millones de vacantes.
No requiere autenticación — búsqueda pública.
"""
import sys, os, asyncio
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import json
import re
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ingestion.queries import get_mexico_queries, get_latam_queries
from core.sheets.sheet_manager import SheetManager

GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'
CYAN  = '\033[96m'; END = '\033[0m'

OCC_HEADERS = [
    'Role', 'Company', 'Location', 'ApplyURL', 'Source',
    'SearchQuery', 'QuerySource', 'DateFound', 'Status', 'RemoteScope',
]

_BASE_URL = "https://www.occ.com.mx"

_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
}

_RSS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "es-MX,es;q=0.9",
}


def _http_get(url: str, headers: dict, retries: int = 3, backoff: float = 3.0) -> str | None:
    """Fetch URL and return text, or None on persistent failure."""
    req = urllib.request.Request(url, headers=headers)
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                # Handle gzip transparently (urllib does this automatically)
                raw = resp.read()
                # Try utf-8 first, fall back to latin-1 (common in MX sites)
                try:
                    return raw.decode("utf-8", errors="replace")
                except Exception:
                    return raw.decode("latin-1", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503):
                print(f"  {YELLOW}OCC HTTP {e.code} on attempt {attempt}/{retries}{END}")
            last_exc = e
        except Exception as exc:
            last_exc = exc
        if attempt < retries:
            time.sleep(backoff)
    print(f"  {RED}OCC fetch failed ({retries} attempts): {last_exc}{END}")
    return None


def _detect_remote(text: str) -> str:
    t = text.lower()
    if "remot" in t or "home office" in t or "trabajo remoto" in t:
        return "Remote"
    if "híbrid" in t or "hybrid" in t:
        return "Hybrid"
    return "OnSite"


def _extract_jsonld_jobs(html: str) -> list[dict]:
    """Extract JobPosting objects from JSON-LD scripts embedded in HTML."""
    jobs = []
    pattern = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(html):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if item.get("@type") != "JobPosting":
                continue
            title   = item.get("title", "").strip()
            company = ""
            org = item.get("hiringOrganization", {})
            if isinstance(org, dict):
                company = org.get("name", "").strip()
            location = ""
            loc_obj = item.get("jobLocation", {})
            if isinstance(loc_obj, dict):
                addr = loc_obj.get("address", {})
                if isinstance(addr, dict):
                    location = (addr.get("addressLocality") or
                                addr.get("addressRegion") or "México").strip()
            apply_url = (item.get("url") or item.get("sameAs") or "").strip()
            if not title:
                continue
            if not apply_url:
                continue
            jobs.append({
                "title":     title,
                "company":   company,
                "location":  location or "México",
                "apply_url": apply_url,
                "remote":    _detect_remote(location + " " + title),
            })
    return jobs


class OccScraper:
    def __init__(self, headless: bool = None):
        # headless param kept for interface parity with other scrapers — not used (no browser)
        self.headless = headless
        self.jobs_found: list[dict] = []
        self.dry_run = True
        self.sheet_manager = None

    async def run(self, dry_run: bool = True):
        self.dry_run = dry_run
        if not dry_run:
            self.sheet_manager = SheetManager()

        print(f"\n{CYAN}{'='*70}")
        print(f"OCC MUNDIAL MX SCRAPER  (RSS + HTTP, no browser required)")
        print(f"{'='*70}{END}")
        print(f"Mode: {YELLOW}{'DRY RUN' if dry_run else 'LIVE'}{END}\n")

        for query, source in get_mexico_queries("en"):
            self._search(query, source)
            await asyncio.sleep(1.5)

        for query, source in get_latam_queries("en"):
            self._search(query, source)
            await asyncio.sleep(1.5)

        self._print_summary()

        if not dry_run and self.jobs_found:
            self._save_to_sheets()

    # ── Search: RSS first, JSON-LD fallback ───────────────────────────────────

    def _search(self, query: str, query_source: str):
        print(f"\n{CYAN}[OCC] Searching: {query}{END}")

        # Strategy 1: RSS feed
        count = self._search_rss(query, query_source)
        if count > 0:
            return

        # Strategy 2: HTTP + JSON-LD
        print(f"  {YELLOW}RSS yielded 0 — trying JSON-LD HTTP fallback{END}")
        self._search_jsonld(query, query_source)

    def _search_rss(self, query: str, query_source: str) -> int:
        """
        Fetch OCC RSS feed for query.
        URL: https://www.occ.com.mx/empleos/rss/?q={query}
        Returns number of jobs found (0 if feed empty or unavailable).
        """
        q_enc = urllib.parse.quote_plus(query)
        url   = f"{_BASE_URL}/empleos/rss/?q={q_enc}"

        text = _http_get(url, _RSS_HEADERS)
        if not text:
            return 0

        # Detect HTML block page
        stripped = text.lstrip()
        if stripped.startswith("<!") or stripped[:5].lower().startswith("<html"):
            print(f"  {YELLOW}RSS returned HTML — OCC may have blocked the request{END}")
            return 0

        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            print(f"  {YELLOW}RSS parse error: {exc}{END}")
            return 0

        channel = root.find("channel")
        if channel is None:
            print(f"  {YELLOW}No <channel> in RSS response{END}")
            return 0

        items = channel.findall("item")
        print(f"  RSS items: {len(items)}")

        count = 0
        for item in items[:20]:
            try:
                title   = (item.findtext("title") or "").strip()
                link    = (item.findtext("link")  or "").strip()
                desc    = item.findtext("description") or ""
                # OCC RSS: company is usually in <author> or <dc:creator>
                company = ""
                for tag in ("author", "{http://purl.org/dc/elements/1.1/}creator"):
                    val = item.findtext(tag)
                    if val:
                        company = val.strip()
                        break
                location = "México"
                # Try to extract location from description
                for line in desc.replace("<br>", "\n").replace("<br/>", "\n").splitlines():
                    l = line.strip().lower()
                    if l.startswith("ubicación:") or l.startswith("location:"):
                        location = line.split(":", 1)[1].strip() or "México"
                        break

                if not title or not link:
                    continue

                self.jobs_found.append({
                    'Role':        title[:100],
                    'Company':     company[:100],
                    'Location':    location[:100],
                    'ApplyURL':    link,
                    'Source':      'OCC Mundial MX',
                    'SearchQuery': query,
                    'QuerySource': query_source,
                    'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                    'Status':      'New',
                    'RemoteScope': _detect_remote(title + " " + location + " " + desc),
                })
                count += 1
            except Exception:
                continue

        print(f"  {GREEN}Parsed {count} jobs (RSS){END}")
        return count

    def _search_jsonld(self, query: str, query_source: str):
        """
        HTTP GET the OCC search results page and extract JobPosting JSON-LD.
        URL: https://www.occ.com.mx/empleos/?busqueda={query}&estado=Todo%20el%20pa%C3%ADs
        """
        q_enc = urllib.parse.quote_plus(query)
        url   = f"{_BASE_URL}/empleos/?busqueda={q_enc}&estado=Todo%20el%20pa%C3%ADs"

        html = _http_get(url, _HTTP_HEADERS)
        if not html:
            return

        jobs = _extract_jsonld_jobs(html)
        print(f"  JSON-LD jobs: {len(jobs)}")

        count = 0
        for jl in jobs[:20]:
            self.jobs_found.append({
                'Role':        jl["title"][:100],
                'Company':     jl["company"][:100],
                'Location':    jl["location"][:100],
                'ApplyURL':    jl["apply_url"],
                'Source':      'OCC Mundial MX',
                'SearchQuery': query,
                'QuerySource': query_source,
                'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                'Status':      'New',
                'RemoteScope': jl["remote"],
            })
            count += 1
        print(f"  {GREEN}Parsed {count} jobs (JSON-LD){END}")

    # ── Summary & Sheet save ──────────────────────────────────────────────────

    def _print_summary(self):
        print(f"\n{CYAN}{'='*70}")
        print(f"OCC SCRAPING SUMMARY")
        print(f"{'='*70}{END}")
        print(f"  Total: {GREEN}{len(self.jobs_found)}{END}")
        by_source: dict[str, int] = {}
        for j in self.jobs_found:
            k = j['QuerySource']
            by_source[k] = by_source.get(k, 0) + 1
        for k, v in by_source.items():
            print(f"    {k}: {v} jobs")

    def _save_to_sheets(self):
        print(f"\n{CYAN}Saving to Google Sheets → OCC tab...{END}")
        try:
            self.sheet_manager.ensure_headers('occ', OCC_HEADERS)
            existing_urls: set[str] = set()
            try:
                rows = self.sheet_manager.get_all_jobs(tab='occ')
                existing_urls = {r.get('ApplyURL', '') for r in rows}
            except Exception:
                pass

            new_jobs = [j for j in self.jobs_found if j['ApplyURL'] not in existing_urls]
            if not new_jobs:
                print(f"  {YELLOW}No new jobs (all duplicates){END}")
                return

            tab_name = self.sheet_manager.tabs['occ']
            headers  = self.sheet_manager._get_headers(tab_name)
            rows_out = [[str(j.get(h, '') or '') for h in headers] for j in new_jobs]
            self.sheet_manager.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab_name}!A2",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows_out},
            ).execute()
            print(f"  {GREEN}Saved {len(new_jobs)} new jobs to OCC tab{END}")
        except Exception as e:
            print(f"  {RED}Error saving to Sheets: {e}{END}")
            raise
