#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
AI JOB FOUNDRY - LINKEDIN SEARCH SCRAPER V3
Busca activamente jobs en LinkedIn por keywords

NUEVO script - NO modifica linkedin_notifications_scraper.py

Strategy: Two-track search to return only Mexico/LATAM-eligible roles.
  Track 1 — QUERIES_MEXICO: searched with geoId=Mexico so LinkedIn returns
             roles targeting workers in Mexico.
  Track 2 — QUERIES_LATAM_GLOBAL: no geo filter, keyword already contains
             "LATAM" / "remote" so results are naturally LATAM-eligible.
  Post-filter: is_us_only() drops any card whose location indicates a
               US state/city without a LATAM/Mexico/global hint.

Keywords updated 2026-04-28
Target companies: Accenture, Deloitte, KPMG, Capgemini, IBM, SAP, Oracle

Usage:
    py core/ingestion/linkedin_search_scraper_v3.py --dry-run  # Test mode
    py core/ingestion/linkedin_search_scraper_v3.py --live     # Save to Sheets
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
import argparse
from playwright.async_api import async_playwright, Page

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.sheets.sheet_manager import SheetManager
from core.utils.linkedin_credentials import get_linkedin_credentials

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
END = '\033[0m'

# ── Búsquedas con location=México (geoId LinkedIn para México)
# Devuelve roles publicados para trabajadores en México
QUERIES_MEXICO = [
    "SAP Project Manager",
    "ERP Implementation Manager",
    "IT Manager",
    "Digital Transformation Manager",
    "Technology Consulting Manager",
    "IT Business Partner",
    "AI Project Manager",
    "Technology Program Manager",
    "Program Manager",
    "Business Process Manager",
]

# ── Búsquedas globales con "LATAM" en keyword (ya auto-filtran)
QUERIES_LATAM_GLOBAL = [
    "IT Manager LATAM remote",
    "Program Manager LATAM remote",
    "SAP Consultant LATAM remote",
]

# GeoId de México en LinkedIn
MEXICO_GEO_ID = "103323778"

# Frases que indican que el rol es SOLO para residentes de USA (descartar)
US_ONLY_PHRASES = [
    "must be located in",
    "must reside in the united states",
    "us-based only",
    "us citizens only",
    "authorized to work in the us",
    "must be in the us",
    "located in the us",
    "within the united states",
    "based in the us",
    "only us residents",
    "applicants must be",  # usually followed by US state
]


class LinkedInSearchScraper:
    """
    LinkedIn job search scraper
    Searches for specific keywords and extracts job listings.
    Filters results to Mexico/LATAM-eligible roles only.
    """

    def __init__(self, dry_run=True, headless=None):
        self.dry_run = dry_run
        self.jobs_found = []
        self.sheet_manager = SheetManager() if not dry_run else None
        # headless=None → lee PLAYWRIGHT_HEADLESS del entorno (CI la pone a "true")
        # headless=True/False → override explícito
        if headless is None:
            self.headless = os.environ.get("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
        else:
            self.headless = headless

    async def run(self, dry_run=None):
        """Main scraping workflow. dry_run param sobreescribe el del constructor si se pasa."""
        if dry_run is not None:
            self.dry_run = dry_run
            if dry_run and self.sheet_manager is None:
                pass  # ya estaba en dry_run
            elif not dry_run and self.sheet_manager is None:
                self.sheet_manager = SheetManager()

        print(f"\n{CYAN}{'='*70}")
        print(f"LINKEDIN SEARCH SCRAPER V3")
        print(f"{'='*70}{END}")
        print(f"Mode: {YELLOW}{'DRY RUN' if self.dry_run else 'LIVE'}{END}\n")

        async with async_playwright() as p:
            # Launch browser — headless en CI, visible en local
            print(f"{CYAN}Launching browser...{END}")
            browser = await p.firefox.launch(headless=self.headless)

            # Reusar sesion guardada si existe
            AUTH_FILE = PROJECT_ROOT / "data" / "credentials" / "linkedin_auth.json"
            if AUTH_FILE.exists():
                print(f"{CYAN}Reusing saved LinkedIn session from {AUTH_FILE}{END}")
                context = await browser.new_context(storage_state=str(AUTH_FILE))
            else:
                context = await browser.new_context()
            page = await context.new_page()

            try:
                # Login
                if not await self.login(page):
                    print(f"{RED}Login failed{END}")
                    return

                # Search Mexico-targeted queries
                for query in QUERIES_MEXICO:
                    print(f"\n{CYAN}{'='*70}")
                    print(f"[MX] Searching: {query}")
                    print(f"{'='*70}{END}")
                    jobs = await self.search_jobs(page, query, geo_id=MEXICO_GEO_ID)
                    # Filter US-only
                    before = len(jobs)
                    jobs = [j for j in jobs if not self.is_us_only(j)]
                    filtered = before - len(jobs)
                    if filtered:
                        print(f"  {YELLOW}Filtered {filtered} US-only jobs{END}")
                    self.jobs_found.extend(jobs)
                    print(f"  {GREEN}Found {len(jobs)} Mexico-eligible jobs{END}")
                    await asyncio.sleep(3)

                # Search LATAM global queries (no geo filter, keyword already filters)
                for query in QUERIES_LATAM_GLOBAL:
                    print(f"\n{CYAN}{'='*70}")
                    print(f"[LATAM] Searching: {query}")
                    print(f"{'='*70}{END}")
                    jobs = await self.search_jobs(page, query, geo_id=None)
                    before = len(jobs)
                    jobs = [j for j in jobs if not self.is_us_only(j)]
                    filtered = before - len(jobs)
                    if filtered:
                        print(f"  {YELLOW}Filtered {filtered} US-only jobs{END}")
                    self.jobs_found.extend(jobs)
                    print(f"  {GREEN}Found {len(jobs)} LATAM-eligible jobs{END}")
                    await asyncio.sleep(3)

                # Summary
                self.print_summary()

                # Save to Sheets
                if not self.dry_run and self.jobs_found:
                    self.save_to_sheets()

            finally:
                await browser.close()

    async def login(self, page: Page) -> bool:
        """Login to LinkedIn - first tries saved session, then fresh login"""
        try:
            # Check if already logged in via saved session
            print(f"{CYAN}Checking LinkedIn session...{END}")
            await page.goto('https://www.linkedin.com/feed', wait_until='domcontentloaded', timeout=20000)
            await asyncio.sleep(3)

            if 'feed' in page.url or 'mynetwork' in page.url:
                print(f"{GREEN}Session active - already logged in{END}")
                return True

            # Session expired or no session - do fresh login
            email, password = get_linkedin_credentials()
            print(f"{CYAN}Session expired, logging in fresh...{END}")
            await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)

            # Fill login form with longer timeout
            await page.fill('#username', email, timeout=30000)
            await page.fill('#password', password, timeout=10000)
            await page.click('button[type="submit"]')

            # Wait for redirect
            await asyncio.sleep(6)

            current_url = page.url
            if 'feed' in current_url or 'jobs' in current_url:
                # Save session for next time
                AUTH_FILE = PROJECT_ROOT / "data" / "credentials" / "linkedin_auth.json"
                AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
                await page.context.storage_state(path=str(AUTH_FILE))
                print(f"{GREEN}Logged in and session saved{END}")
                return True
            elif 'checkpoint' in current_url or 'challenge' in current_url:
                print(f"{YELLOW}LinkedIn requires verification - complete it manually in the browser window{END}")
                await asyncio.sleep(30)  # Give user time
                return True
            else:
                print(f"{YELLOW}Login result unclear: {current_url}{END}")
                return True

        except Exception as e:
            print(f"{RED}Login error: {e}{END}")
            return False

    async def search_jobs(self, page: Page, query: str, max_results=20, geo_id: str = None) -> list:
        """
        Search for jobs with given query

        Args:
            page: Playwright page
            query: Search query
            max_results: Max jobs to extract
            geo_id: LinkedIn geoId for location filter (e.g. MEXICO_GEO_ID)

        Returns:
            List of job dicts
        """
        jobs = []

        try:
            # Build URL — with Mexico geoId if requested
            encoded_query = query.replace(' ', '%20')
            if geo_id:
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location=M%C3%A9xico&geoId={geo_id}&f_WT=2&f_LF=f_AL"
            else:
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&f_WT=2&f_LF=f_AL"

            print(f"  {CYAN}Opening: {search_url}{END}")
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(5)

            # Dismiss any login/signup popups — try multiple known selectors
            popup_selectors = [
                'button[aria-label="Dismiss"]',
                'button[aria-label="Dismiss Sign In Modal"]',
                'button.modal__dismiss',
                '[data-tracking-control-name="public_jobs_contextual-sign-in-modal_modal_dismiss"]',
                'button.contextual-sign-in-modal__modal-dismiss-btn',
                '[aria-label="Cerrar"]',
                'button[data-modal-dismiss]',
                '.sign-in-modal button.dismiss',
            ]
            for sel in popup_selectors:
                try:
                    btn = page.locator(sel)
                    if await btn.count() > 0:
                        await btn.first.click(timeout=2000)
                        await asyncio.sleep(0.5)
                        break
                except Exception:
                    continue
            # Also press Escape as fallback — closes most LinkedIn modals
            try:
                await page.keyboard.press('Escape')
                await asyncio.sleep(0.5)
            except Exception:
                pass

            # Scroll to load more jobs
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

            # Extract job cards - multiple selectors for LinkedIn 2025/2026 UI
            CARD_SELECTORS = [
                'div.job-search-card',                          # old UI
                'li.jobs-search-results__list-item',            # logged-in feed
                'div[data-job-id]',                             # data attribute
                'li[data-occludable-job-id]',                   # occludable list
                '.scaffold-layout__list-item',                  # scaffold layout
                'li.ember-view.jobs-search-results__list-item', # ember variant
            ]

            job_cards = None
            count = 0
            for sel in CARD_SELECTORS:
                candidate = page.locator(sel)
                c = await candidate.count()
                if c > 0:
                    job_cards = candidate
                    count = c
                    print(f"  {CYAN}Selector '{sel}' -> {c} cards{END}")
                    break

            if not job_cards or count == 0:
                # Debug: dump a sample of the page HTML to diagnose
                html_sample = await page.evaluate("document.body.innerHTML.substring(0, 2000)")
                print(f"  {YELLOW}No job cards found. HTML sample: {html_sample[:500]}{END}")
            else:
                print(f"  {CYAN}Found {count} job cards{END}")

            # Extract each job
            for i in range(min(count, max_results)):
                try:
                    card = job_cards.nth(i)

                    # Extract data - try multiple selectors per field
                    title_elem = card.locator('h3.base-search-card__title, a.job-card-list__title, .job-card-container__link strong, h3[class*="title"]').first
                    company_elem = card.locator('h4.base-search-card__subtitle, .job-card-container__company-name, a[class*="company"], span[class*="company"]').first
                    location_elem = card.locator('span.job-search-card__location, .job-card-container__metadata-item, li[class*="location"]').first
                    link_elem = card.locator('a.base-card__full-link, a.job-card-list__title, a[class*="job-card"]').first

                    title = await title_elem.inner_text(timeout=2000) if await title_elem.count() > 0 else "Unknown"
                    company = await company_elem.inner_text(timeout=2000) if await company_elem.count() > 0 else "Unknown"
                    location = await location_elem.inner_text(timeout=2000) if await location_elem.count() > 0 else "Unknown"
                    url = await link_elem.get_attribute('href', timeout=2000) if await link_elem.count() > 0 else ""

                    # Clean URL (remove tracking params)
                    if url and '?' in url:
                        url = url.split('?')[0]

                    job = {
                        'Role': title.strip(),
                        'Company': company.strip(),
                        'Location': location.strip(),
                        'ApplyURL': url,
                        'Source': 'LinkedIn Search',
                        'SearchQuery': query,
                        'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Status': 'New',
                        'RemoteScope': 'Remote'  # We filtered for remote
                    }

                    jobs.append(job)

                    if i < 5:  # Show first 5
                        print(f"    {i+1}. {title[:50]} at {company}")

                except Exception as e:
                    print(f"    {YELLOW}Could not extract job {i+1}: {e}{END}")
                    continue

        except Exception as e:
            print(f"  {RED}Search error: {e}{END}")

        return jobs

    def is_us_only(self, job: dict) -> bool:
        """Returns True only if job is clearly US-only, no LATAM/Mexico eligibility."""
        location = (job.get("location") or job.get("Location") or "").lower()
        title = (job.get("title") or job.get("Role") or "").lower()

        # If title mentions LATAM/Mexico/global → keep it (never filter)
        latam_hints = ["latam", "latin america", "mexico", "méxico", "global",
                       "worldwide", "international", "remote", "us or lat"]
        if any(h in title for h in latam_hints):
            return False
        if any(h in location for h in latam_hints):
            return False

        # Hard phrases that mean US-only
        hard_us_phrases = [
            "must be located in",
            "must reside in the united states",
            "us citizens only",
            "must be in the us",
            "only us residents",
            "authorized to work in the us",
        ]
        for phrase in hard_us_phrases:
            if phrase in location:
                return True

        # Location is a specific US city/state with no remote/global hint
        us_state_codes = [
            ", al", ", ak", ", az", ", ar", ", ca", ", co", ", ct", ", de",
            ", fl", ", ga", ", hi", ", id", ", il", ", in", ", ia", ", ks",
            ", ky", ", la", ", me", ", md", ", ma", ", mi", ", mn", ", ms",
            ", mo", ", mt", ", ne", ", nv", ", nh", ", nj", ", nm", ", ny",
            ", nc", ", nd", ", oh", ", ok", ", or", ", pa", ", ri", ", sc",
            ", sd", ", tn", ", tx", ", ut", ", vt", ", va", ", wa", ", wv",
            ", wi", ", wy", ", dc",
        ]
        # Only filter on state code if location ends with it (e.g., "Austin, TX" not "México")
        for code in us_state_codes:
            if location.endswith(code) or f"{code} " in location:
                return True

        return False

    def print_summary(self):
        """Print summary of scraping"""
        print(f"\n{CYAN}{'='*70}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*70}{END}")

        print(f"  Total jobs found: {GREEN}{len(self.jobs_found)}{END}")

        # Group by search query
        by_query = {}
        for job in self.jobs_found:
            query = job.get('SearchQuery', 'Unknown')
            by_query[query] = by_query.get(query, 0) + 1

        print(f"\n  By search query:")
        for query, count in by_query.items():
            print(f"    - {query}: {count}")

        # Show first 10 jobs
        if self.jobs_found:
            print(f"\n  {CYAN}Sample jobs (first 10):{END}")
            for i, job in enumerate(self.jobs_found[:10], 1):
                print(f"    {i}. {job['Role'][:40]} at {job['Company']}")

        print(f"{CYAN}{'='*70}{END}\n")

    def save_to_sheets(self):
        """Save jobs to Google Sheets.

        Strategy: jobs land in the 'Staging' tab first so Marcos can
        review them before they enter the main LinkedIn pipeline.
        Duplicates are checked against both Staging AND LinkedIn tabs.
        """
        print(f"\n{CYAN}Saving to Google Sheets (Staging tab)...{END}")

        # Column order for the Staging tab — must be written as headers on first run
        STAGING_HEADERS = [
            'Role', 'Company', 'Location', 'ApplyURL',
            'Source', 'SearchQuery', 'CreatedAt', 'Status', 'RemoteScope',
        ]

        try:
            # Initialize Staging headers if the tab is blank (first-ever run)
            self.sheet_manager.ensure_headers('staging', STAGING_HEADERS)

            # Collect already-known URLs from both Staging and LinkedIn
            existing_urls: set = set()
            for check_tab in ('staging', 'linkedin'):
                try:
                    rows = self.sheet_manager.get_all_jobs(tab=check_tab)
                    existing_urls.update(j.get('ApplyURL', '') for j in rows)
                except Exception:
                    pass  # Tab may not exist yet — first run

            # Only keep genuinely new jobs
            new_jobs = [
                job for job in self.jobs_found
                if job.get('ApplyURL', '') not in existing_urls
            ]

            print(f"  Total scraped:  {len(self.jobs_found)}")
            print(f"  Duplicates:     {len(self.jobs_found) - len(new_jobs)}")
            print(f"  New jobs:       {GREEN}{len(new_jobs)}{END}")
            print(f"  Destination:    {CYAN}Staging tab{END} (revisar y promover a LinkedIn)")

            if not new_jobs:
                print(f"  {YELLOW}No hay jobs nuevos que guardar{END}")
                return

            # ONE batch write — avoids the 60 writes/min quota (HTTP 429)
            tab_name = self.sheet_manager.tabs['staging']
            headers  = self.sheet_manager._get_headers(tab_name)
            rows     = [[str(job.get(h, '') or '') for h in headers] for job in new_jobs]

            try:
                self.sheet_manager.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_manager.spreadsheet_id,
                    range=f"{tab_name}!A2",
                    valueInputOption="USER_ENTERED",
                    body={"values": rows},
                ).execute()
                saved = len(rows)
            except Exception as e:
                print(f"    {RED}Batch write error: {e}{END}")
                saved = 0

            print(f"  {GREEN}Guardados {saved}/{len(new_jobs)} jobs en Staging{END}")
            print(f"\n  {YELLOW}Próximo paso: revisa la pestaña 'Staging' en el Sheet,")
            print(f"  mueve los que quieras a 'LinkedIn', y borra los demás.{END}")

        except Exception as e:
            print(f"  {RED}Save error: {e}{END}")


def main():
    parser = argparse.ArgumentParser(description='Search LinkedIn for jobs')
    parser.add_argument(
        '--live',
        action='store_true',
        help='Save jobs to Sheets (default is dry-run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - do not save (default)'
    )

    args = parser.parse_args()

    # Default to dry-run
    dry_run = not args.live

    if args.dry_run:
        dry_run = True

    try:
        scraper = LinkedInSearchScraper(dry_run=dry_run)
        asyncio.run(scraper.run())
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Cancelled by user{END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
