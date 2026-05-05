#!/usr/bin/env python3
"""
AI JOB FOUNDRY - OCC MUNDIAL MX SCRAPER (Playwright)
=====================================================
Scraper de OCC Mundial México usando Playwright.
URL pattern: occ.com.mx/empleos/de-{slug}/en-todo-el-pais/

OCC bloquea HTTP simple (403) — requiere browser headless real.
Strategy 1: JSON-LD structured data (<script type="application/ld+json">)
Strategy 2: CSS card selectors (fallback)

No requiere autenticación — búsqueda pública.
"""
import sys, os, asyncio, json, re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

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

_BASE_URL  = "https://www.occ.com.mx"
_LOG_DIR   = PROJECT_ROOT / "logs"

# CSS card selectors to try in priority order
# TODO: confirm exact selectors from DevTools inspection
_CARD_SELECTORS = [
    '[class*="CardJob"]',
    '[class*="card-job"]',
    '[class*="JobCard"]',
    'article[class*="job"]',
    '[data-testid*="job"]',
    '[class*="listado"] > div',
    '.card',
]


def _query_to_slug(query: str) -> str:
    """Convert search query to OCC URL slug: 'Project Manager' → 'project-manager'"""
    slug = query.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug


def _detect_remote(text: str) -> str:
    t = text.lower()
    if "remot" in t or "home office" in t or "trabajo remoto" in t:
        return "Remote"
    if "híbrid" in t or "hybrid" in t:
        return "Hybrid"
    return "OnSite"


class OccScraper:
    def __init__(self, headless: bool = None):
        if headless is None:
            headless = os.environ.get("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
        self.headless      = headless
        self.jobs_found: list[dict] = []
        self.dry_run       = True
        self.sheet_manager = None

    async def run(self, dry_run: bool = True):
        self.dry_run = dry_run
        if not dry_run:
            self.sheet_manager = SheetManager()

        print(f"\n{CYAN}{'='*70}")
        print(f"OCC MUNDIAL MX SCRAPER  (Playwright)")
        print(f"{'='*70}{END}")
        print(f"Mode: {YELLOW}{'DRY RUN' if dry_run else 'LIVE'}{END}\n")

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 900},
                locale="es-MX",
            )
            page = await context.new_page()

            try:
                for query, source in get_mexico_queries("en"):
                    await self._search(page, query, source)
                    await asyncio.sleep(3)

                for query, source in get_latam_queries("en"):
                    await self._search(page, query, source)
                    await asyncio.sleep(3)

                self._print_summary()

                if not dry_run and self.jobs_found:
                    self._save_to_sheets()
            finally:
                await browser.close()

    async def _load_page(self, page, url: str):
        """Navigate and wait for content to settle."""
        await page.goto(url, timeout=40000, wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await asyncio.sleep(4)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

    async def _extract_jsonld(self, page) -> list[dict]:
        """Extract JobPosting objects from JSON-LD scripts in the page."""
        jobs = []
        try:
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                raw = await script.inner_text()
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
                    if not title or not apply_url:
                        continue
                    jobs.append({
                        "title": title, "company": company,
                        "location": location or "México",
                        "apply_url": apply_url,
                        "remote": _detect_remote(location + " " + title),
                    })
        except Exception as exc:
            print(f"  {YELLOW}JSON-LD error: {exc}{END}")
        return jobs

    async def _find_cards(self, page):
        """Try CSS selectors and return first non-empty match."""
        for sel in _CARD_SELECTORS:
            try:
                cards = await page.query_selector_all(sel)
                if cards:
                    print(f"  Selector matched '{sel}': {len(cards)} cards")
                    return cards
            except Exception:
                continue
        return []

    async def _search(self, page, query: str, query_source: str):
        slug = _query_to_slug(query)
        url  = f"{_BASE_URL}/empleos/de-{slug}/en-todo-el-pais/"
        print(f"\n{CYAN}[OCC] Searching: {query} → {url}{END}")

        try:
            await self._load_page(page, url)

            # ── Strategy 1: JSON-LD ──────────────────────────────────────────
            jsonld_jobs = await self._extract_jsonld(page)
            if jsonld_jobs:
                print(f"  JSON-LD: {len(jsonld_jobs)} jobs")
                count = 0
                for jl in jsonld_jobs[:20]:
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
                print(f"  {GREEN}Found {count} jobs (JSON-LD){END}")
                return

            # ── Strategy 2: CSS card selectors ───────────────────────────────
            cards = await self._find_cards(page)

            if not cards:
                _LOG_DIR.mkdir(exist_ok=True)
                debug_path = _LOG_DIR / f"debug_occ_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                try:
                    await page.screenshot(path=str(debug_path), full_page=True)
                    print(f"  {YELLOW}0 cards — screenshot: {debug_path.name}{END}")
                except Exception:
                    pass
                print(f"  {YELLOW}No cards found for: {query}{END}")
                return

            count = 0
            for card in cards[:20]:
                try:
                    # Title — try multiple selector patterns
                    title_el = await card.query_selector(
                        'h2 a, h3 a, [class*="title"] a, [class*="Title"] a, '
                        '[class*="name"] a, [class*="Name"] a, a[class*="job"]'
                    )
                    title = (await title_el.inner_text()).strip() if title_el else ""

                    # Company
                    company_el = await card.query_selector(
                        '[class*="company"], [class*="Company"], '
                        '[class*="empresa"], [class*="Empresa"]'
                    )
                    company = (await company_el.inner_text()).strip() if company_el else ""

                    # Location
                    loc_el = await card.query_selector(
                        '[class*="location"], [class*="Location"], '
                        '[class*="lugar"], [class*="ciudad"], [class*="Ciudad"]'
                    )
                    location = (await loc_el.inner_text()).strip() if loc_el else "México"

                    # URL
                    apply_url = ""
                    if title_el:
                        href = await title_el.get_attribute("href")
                        if href:
                            apply_url = (href if href.startswith("http")
                                         else f"{_BASE_URL}{href}")

                    if not title or not apply_url:
                        continue

                    self.jobs_found.append({
                        'Role':        title[:100],
                        'Company':     company[:100],
                        'Location':    location[:100],
                        'ApplyURL':    apply_url,
                        'Source':      'OCC Mundial MX',
                        'SearchQuery': query,
                        'QuerySource': query_source,
                        'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                        'Status':      'New',
                        'RemoteScope': _detect_remote(location + " " + title),
                    })
                    count += 1
                except Exception:
                    continue

            print(f"  {GREEN}Found {count} jobs (CSS){END}")

        except Exception as e:
            print(f"  {RED}Error searching '{query}': {e}{END}")

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
