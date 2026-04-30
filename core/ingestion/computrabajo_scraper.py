#!/usr/bin/env python3
"""
AI JOB FOUNDRY - COMPUTRABAJO MX SCRAPER
=========================================
Scraper de Computrabajo México usando Playwright.
Escribe resultados directamente a la pestaña "Computrabajo" de Google Sheets.
No requiere autenticación — Computrabajo es público.
"""
import sys, os, asyncio
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
                viewport={"width": 1280, "height": 800},
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

    async def _search(self, page, query: str, query_source: str):
        print(f"\n{CYAN}[Computrabajo] Searching: {query}{END}")
        encoded = query.lower().replace(" ", "-")
        url = f"https://www.computrabajo.com.mx/trabajo-de-{encoded}"
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Wait for job listings to appear
            try:
                await page.wait_for_selector(
                    'article.box_offer, [data-cy="offer-list-item"], .of-base',
                    timeout=10000,
                )
            except Exception:
                pass

            # Computrabajo job cards
            cards = await page.query_selector_all('article.box_offer')
            if not cards:
                cards = await page.query_selector_all('[data-cy="offer-list-item"]')
            if not cards:
                cards = await page.query_selector_all('.of-base')

            print(f"  Found {len(cards)} cards")
            count = 0

            for card in cards[:20]:
                try:
                    # Title
                    title_el = await card.query_selector('h2.title a, [data-cy="title"]')
                    title = (await title_el.inner_text()).strip() if title_el else ""

                    # Company
                    company_el = await card.query_selector('p.dO_fi, [data-cy="company"]')
                    company = (await company_el.inner_text()).strip() if company_el else ""

                    # Location
                    loc_el = await card.query_selector('span.dO_fi, [data-cy="location"]')
                    location = (await loc_el.inner_text()).strip() if loc_el else "México"

                    # URL — get href from title link
                    apply_url = ""
                    if title_el:
                        href = await title_el.get_attribute("href")
                        if href:
                            if href.startswith("http"):
                                apply_url = href
                            else:
                                apply_url = "https://www.computrabajo.com.mx" + href

                    if not title or not apply_url:
                        continue

                    # Remote detection
                    loc_lower = location.lower()
                    remote = ("Remote" if "remot" in loc_lower or "home office" in loc_lower
                              else "Hybrid" if "híbrid" in loc_lower or "hybrid" in loc_lower
                              else "OnSite")

                    job = {
                        'Role':        title[:100],
                        'Company':     company[:100],
                        'Location':    location[:100],
                        'ApplyURL':    apply_url,
                        'Source':      'Computrabajo MX',
                        'SearchQuery': query,
                        'QuerySource': query_source,
                        'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                        'Status':      'New',
                        'RemoteScope': remote,
                    }
                    self.jobs_found.append(job)
                    count += 1
                except Exception:
                    continue

            print(f"  {GREEN}Found {count} jobs{END}")

        except Exception as e:
            print(f"  {RED}Error searching '{query}': {e}{END}")

    def _print_summary(self):
        print(f"\n{CYAN}{'='*70}")
        print(f"COMPUTRABAJO SCRAPING SUMMARY")
        print(f"{'='*70}{END}")
        print(f"  Total: {GREEN}{len(self.jobs_found)}{END}")
        by_source = {}
        for j in self.jobs_found:
            k = j['QuerySource']
            by_source[k] = by_source.get(k, 0) + 1
        for k, v in by_source.items():
            print(f"    {k}: {v} jobs")

    def _save_to_sheets(self):
        print(f"\n{CYAN}Saving to Google Sheets → Computrabajo tab...{END}")
        try:
            self.sheet_manager.ensure_headers('computrabajo', COMPUTRABAJO_HEADERS)
            existing_urls = set()
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
            rows     = [[str(j.get(h, '') or '') for h in headers] for j in new_jobs]
            self.sheet_manager.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab_name}!A2",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows},
            ).execute()
            print(f"  {GREEN}Saved {len(new_jobs)} new jobs to Computrabajo tab{END}")
        except Exception as e:
            print(f"  {RED}Error saving to Sheets: {e}{END}")
            raise
