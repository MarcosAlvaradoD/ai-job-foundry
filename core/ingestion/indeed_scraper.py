#!/usr/bin/env python3
"""
AI JOB FOUNDRY - INDEED MX SCRAPER
====================================
Scraper de Indeed México usando Playwright.
Escribe resultados directamente a la pestaña "Indeed" de Google Sheets.
No requiere autenticación — Indeed es público.
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

INDEED_HEADERS = [
    'Role', 'Company', 'Location', 'ApplyURL', 'Source',
    'SearchQuery', 'QuerySource', 'DateFound', 'Status', 'RemoteScope',
]

class IndeedScraper:
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
        print(f"INDEED MX SCRAPER")
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
                for query, source in get_mexico_queries("en"):
                    await self._search(page, query, source)
                    await asyncio.sleep(4)

                for query, source in get_latam_queries("en"):
                    await self._search(page, query, source)
                    await asyncio.sleep(4)

                self._print_summary()

                if not dry_run and self.jobs_found:
                    self._save_to_sheets()
            finally:
                await browser.close()

    async def _search(self, page, query: str, query_source: str):
        print(f"\n{CYAN}[Indeed] Searching: {query}{END}")
        encoded = query.replace(" ", "+")
        url = f"https://mx.indeed.com/jobs?q={encoded}&l=M%C3%A9xico&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11"
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Indeed job cards
            cards = await page.query_selector_all('[data-jk]')
            if not cards:
                cards = await page.query_selector_all('.job_seen_beacon')
            if not cards:
                cards = await page.query_selector_all('.resultContent')

            print(f"  Found {len(cards)} cards")
            count = 0

            for card in cards[:20]:
                try:
                    # Title
                    title_el = await card.query_selector('h2.jobTitle span, h2 a span, [data-testid="job-title"]')
                    title = (await title_el.inner_text()).strip() if title_el else ""

                    # Company
                    company_el = await card.query_selector('[data-testid="company-name"], .companyName')
                    company = (await company_el.inner_text()).strip() if company_el else ""

                    # Location
                    loc_el = await card.query_selector('[data-testid="text-location"], .companyLocation')
                    location = (await loc_el.inner_text()).strip() if loc_el else "México"

                    # URL
                    job_id = await card.get_attribute("data-jk")
                    apply_url = f"https://mx.indeed.com/viewjob?jk={job_id}" if job_id else ""

                    if not title or not apply_url:
                        continue

                    # Remote detection
                    loc_lower = location.lower()
                    remote = ("Remote" if "remot" in loc_lower
                              else "Hybrid" if "híbrid" in loc_lower or "hybrid" in loc_lower
                              else "OnSite")

                    job = {
                        'Role':        title[:100],
                        'Company':     company[:100],
                        'Location':    location[:100],
                        'ApplyURL':    apply_url,
                        'Source':      'Indeed MX',
                        'SearchQuery': query,
                        'QuerySource': query_source,
                        'DateFound':   datetime.now().strftime('%Y-%m-%d'),
                        'Status':      'New',
                        'RemoteScope': remote,
                    }
                    self.jobs_found.append(job)
                    count += 1
                except Exception as e:
                    continue

            print(f"  {GREEN}Found {count} jobs{END}")

        except Exception as e:
            print(f"  {RED}Error searching '{query}': {e}{END}")

    def _print_summary(self):
        print(f"\n{CYAN}{'='*70}")
        print(f"INDEED SCRAPING SUMMARY")
        print(f"{'='*70}{END}")
        print(f"  Total: {GREEN}{len(self.jobs_found)}{END}")
        by_source = {}
        for j in self.jobs_found:
            k = j['QuerySource']
            by_source[k] = by_source.get(k, 0) + 1
        for k, v in by_source.items():
            print(f"    {k}: {v} jobs")

    def _save_to_sheets(self):
        print(f"\n{CYAN}Saving to Google Sheets → Indeed tab...{END}")
        try:
            self.sheet_manager.ensure_headers('indeed', INDEED_HEADERS)
            existing_urls = set()
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
            rows     = [[str(j.get(h, '') or '') for h in headers] for j in new_jobs]
            self.sheet_manager.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab_name}!A2",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows},
            ).execute()
            print(f"  {GREEN}Saved {len(new_jobs)} new jobs to Indeed tab{END}")
        except Exception as e:
            print(f"  {RED}Error saving to Sheets: {e}{END}")
            raise
