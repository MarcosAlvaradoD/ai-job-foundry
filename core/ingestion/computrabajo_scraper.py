#!/usr/bin/env python3
"""
AI JOB FOUNDRY - COMPUTRABAJO MX SCRAPER
=========================================
Scraper de Computrabajo México usando Playwright.
Escribe resultados directamente a la pestaña "Computrabajo" de Google Sheets.
No requiere autenticación — Computrabajo es público.
"""
import sys, os, asyncio
import urllib.parse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.ingestion.queries import get_mexico_queries, get_latam_queries
from core.sheets.sheet_manager import SheetManager

GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'
CYAN  = '\033[96m'; END = '\033[0m'

COMPUTRABAJO_HEADERS = [
    'Role', 'Company', 'Location', 'ApplyURL', 'Source',
    'SearchQuery', 'QuerySource', 'DateFound', 'Status', 'RemoteScope',
]

_LOG_DIR = PROJECT_ROOT / "logs"

# Card selectors to try in priority order (Computrabajo changes markup frequently)
_CARD_SELECTORS = [
    'article[data-id]',
    '[class*="OfferCard"]',
    '.offerBlock',
    'article.box_offer',
    '[data-cy="offer-list-item"]',
    '.of-base',
]


class ComputrabajoScraper:
    def __init__(self, headless: bool = None):
        if headless is None:
            headless = os.environ.get("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
        self.headless   = headless
        self.jobs_found: list[dict] = []
        self.dry_run    = True
        self.sheet_manager = None

    async def run(self, dry_run: bool = True):
        self.dry_run = dry_run
        if not dry_run:
            self.sheet_manager = SheetManager()

        print(f"\n{CYAN}{'='*70}")
        print(f"COMPUTRABAJO MX SCRAPER")
        print(f"{'='*70}{END}")
        print(f"Mode: {YELLOW}{'DRY RUN' if dry_run else 'LIVE'}{END}\n")

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()

            try:
                for query, source in get_mexico_queries("es"):
                    await self._search(page, query, source)
                    await asyncio.sleep(4)

                for query, source in get_latam_queries("es"):
                    await self._search(page, query, source)
                    await asyncio.sleep(4)

                self._print_summary()

                if not dry_run and self.jobs_found:
                    self._save_to_sheets()
            finally:
                await browser.close()

    async def _find_cards(self, page):
        """Try all card selectors and return the first non-empty match."""
        for sel in _CARD_SELECTORS:
            try:
                cards = await page.query_selector_all(sel)
                if cards:
                    print(f"  Selector matched '{sel}': {len(cards)} cards")
                    return cards
            except Exception:
                continue
        return []

    async def _extract_jsonld(self, page) -> list[dict]:
        """
        Extract jobs from JSON-LD <script type="application/ld+json"> blocks.
        JobPosting schema is far more stable than CSS selectors.
        Returns list of job dicts (same shape as the CSS-based path).
        """
        import json as _json
        try:
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            jobs = []
            for script in scripts:
                raw = await script.inner_text()
                try:
                    data = _json.loads(raw)
                except Exception:
                    continue
                # May be a single object or a list
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "JobPosting":
                        title    = item.get("title", "").strip()
                        company  = ""
                        org      = item.get("hiringOrganization", {})
                        if isinstance(org, dict):
                            company = org.get("name", "").strip()
                        location = ""
                        loc_obj  = item.get("jobLocation", {})
                        if isinstance(loc_obj, dict):
                            addr = loc_obj.get("address", {})
                            if isinstance(addr, dict):
                                location = (addr.get("addressLocality") or
                                            addr.get("addressRegion") or "México").strip()
                        apply_url = (item.get("url") or item.get("sameAs") or "").strip()
                        if not title or not apply_url:
                            continue
                        loc_lower = location.lower()
                        remote = ("Remote" if ("remot" in loc_lower or "home office" in loc_lower)
                                  else "Hybrid" if ("híbrid" in loc_lower or "hybrid" in loc_lower)
                                  else "OnSite")
                        jobs.append({
                            "title": title, "company": company,
                            "location": location, "apply_url": apply_url, "remote": remote,
                        })
            return jobs
        except Exception as exc:
            print(f"  {YELLOW}JSON-LD extraction error: {exc}{END}")
            return []

    async def _load_page(self, page, url: str):
        """Navigate to url and wait for content to settle."""
        await page.goto(url, timeout=40000, wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await asyncio.sleep(4)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

    async def _search(self, page, query: str, query_source: str):
        print(f"\n{CYAN}[Computrabajo] Searching: {query}{END}")

        encoded_q = urllib.parse.quote_plus(query)
        slug      = query.lower().replace(" ", "-")

        # Primary URL: search endpoint with remote filter (r=10)
        url = f"https://www.computrabajo.com.mx/ofertas-de-trabajo?q={encoded_q}&r=10"

        try:
            await self._load_page(page, url)

            # ── Strategy 1: JSON-LD structured data (most stable) ────────────
            jsonld_jobs = await self._extract_jsonld(page)
            if jsonld_jobs:
                print(f"  JSON-LD: {len(jsonld_jobs)} jobs extracted")
                count = 0
                for jl in jsonld_jobs[:20]:
                    self.jobs_found.append({
                        'Role':        jl["title"][:100],
                        'Company':     jl["company"][:100],
                        'Location':    jl["location"][:100],
                        'ApplyURL':    jl["apply_url"],
                        'Source':      'Computrabajo MX',
                        'SearchQuery': query,
                        'QuerySource': query_source,
                        'CreatedAt':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                        'Status':      'New',
                        'RemoteScope': jl["remote"],
                    })
                    count += 1
                print(f"  {GREEN}Found {count} jobs (JSON-LD){END}")
                return

            # ── Strategy 2: CSS card selectors ───────────────────────────────
            cards = await self._find_cards(page)

            if not cards:
                # Save debug screenshot for CI artifact inspection
                _LOG_DIR.mkdir(exist_ok=True)
                debug_path = _LOG_DIR / f"debug_computrabajo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                try:
                    await page.screenshot(path=str(debug_path), full_page=True)
                    print(f"  {YELLOW}0 cards on primary URL — screenshot: {debug_path.name}{END}")
                except Exception:
                    pass

                # Fallback: slug-based URL
                url2 = f"https://www.computrabajo.com.mx/trabajo-de-{slug}?r=10"
                print(f"  {YELLOW}Trying fallback URL: {url2}{END}")
                await self._load_page(page, url2)

                # Try JSON-LD again on fallback page
                jsonld_jobs = await self._extract_jsonld(page)
                if jsonld_jobs:
                    print(f"  JSON-LD (fallback): {len(jsonld_jobs)} jobs extracted")
                    count = 0
                    for jl in jsonld_jobs[:20]:
                        self.jobs_found.append({
                            'Role':        jl["title"][:100],
                            'Company':     jl["company"][:100],
                            'Location':    jl["location"][:100],
                            'ApplyURL':    jl["apply_url"],
                            'Source':      'Computrabajo MX',
                            'SearchQuery': query,
                            'QuerySource': query_source,
                            'CreatedAt':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                            'Status':      'New',
                            'RemoteScope': jl["remote"],
                        })
                        count += 1
                    print(f"  {GREEN}Found {count} jobs (JSON-LD fallback){END}")
                    return

                cards = await self._find_cards(page)

            print(f"  CSS cards found: {len(cards)}")
            count = 0

            for card in cards[:20]:
                try:
                    # Title
                    title_el = await card.query_selector('h2 a, .tO > a, [class*="title"] a, a[class*="Title"]')
                    title = (await title_el.inner_text()).strip() if title_el else ""

                    # Company
                    company_el = await card.query_selector(
                        '[class*="company"], [class*="Company"], .dO > p:first-child, p.dO_fi'
                    )
                    company = (await company_el.inner_text()).strip() if company_el else ""

                    # Location
                    loc_el = await card.query_selector(
                        '[class*="location"], [class*="Location"], .dO > p:last-child, span.dO_fi'
                    )
                    location = (await loc_el.inner_text()).strip() if loc_el else "México"

                    # URL — href from title anchor
                    apply_url = ""
                    if title_el:
                        href = await title_el.get_attribute("href")
                        if href:
                            apply_url = (href if href.startswith("http")
                                         else "https://www.computrabajo.com.mx" + href)

                    if not title or not apply_url:
                        continue

                    loc_lower = location.lower()
                    remote = ("Remote" if ("remot" in loc_lower or "home office" in loc_lower)
                              else "Hybrid" if ("híbrid" in loc_lower or "hybrid" in loc_lower)
                              else "OnSite")

                    self.jobs_found.append({
                        'Role':        title[:100],
                        'Company':     company[:100],
                        'Location':    location[:100],
                        'ApplyURL':    apply_url,
                        'Source':      'Computrabajo MX',
                        'SearchQuery': query,
                        'QuerySource': query_source,
                        'CreatedAt':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                        'Status':      'New',
                        'RemoteScope': remote,
                    })
                    count += 1
                except Exception:
                    continue

            print(f"  {GREEN}Found {count} jobs (CSS){END}")

        except Exception as e:
            print(f"  {RED}Error searching '{query}': {e}{END}")

    def _print_summary(self):
        print(f"\n{CYAN}{'='*70}")
        print(f"COMPUTRABAJO SCRAPING SUMMARY")
        print(f"{'='*70}{END}")
        print(f"  Total: {GREEN}{len(self.jobs_found)}{END}")
        by_source: dict[str, int] = {}
        for j in self.jobs_found:
            k = j['QuerySource']
            by_source[k] = by_source.get(k, 0) + 1
        for k, v in by_source.items():
            print(f"    {k}: {v} jobs")

    def _save_to_sheets(self):
        print(f"\n{CYAN}Saving to Google Sheets → Computrabajo tab...{END}")
        try:
            self.sheet_manager.ensure_headers('computrabajo', COMPUTRABAJO_HEADERS)
            existing_urls: set[str] = set()
            try:
                rows = self.sheet_manager.get_all_jobs(tab='computrabajo')
                existing_urls = {r.get('ApplyURL', '') for r in rows}
            except Exception:
                pass

            new_jobs = [j for j in self.jobs_found if j['ApplyURL'] not in existing_urls]
            if not new_jobs:
                print(f"  {YELLOW}No new jobs (all duplicates){END}")
                return

            tab_name = self.sheet_manager.tabs['computrabajo']
            headers  = self.sheet_manager._get_headers(tab_name)
            rows_out = [[str(j.get(h, '') or '') for h in headers] for j in new_jobs]
            self.sheet_manager.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab_name}!A2",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows_out},
            ).execute()
            print(f"  {GREEN}Saved {len(new_jobs)} new jobs to Computrabajo tab{END}")
        except Exception as e:
            print(f"  {RED}Error saving to Sheets: {e}{END}")
            raise
