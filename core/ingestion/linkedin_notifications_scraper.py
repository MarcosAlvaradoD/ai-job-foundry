#!/usr/bin/env python3
"""
AI JOB FOUNDRY - LinkedIn Notifications Scraper
================================================
Scrapes job recommendations from LinkedIn notifications panel

Features:
- Extracts jobs from the right-side recommendations panel
- Saves to Google Sheets (LinkedIn tab)
- Integrates with AI analysis for FIT scores
- Works with existing auto-apply system

Author: Marcos Alberto Alvarado
Created: 2026-01-18
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ✅ Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import re
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
import os

load_dotenv()


class LinkedInNotificationsScraper:
    """Scrapes LinkedIn job recommendations from notifications panel"""
    
    def __init__(self):
        self.sheet_manager = SheetManager()
        self.jobs_found = []
        self.session_file = "data/credentials/linkedin_session.json"
    
    async def check_login(self, page):
        """Check if user is logged into LinkedIn"""
        print("🔐 Checking LinkedIn session...")
        
        try:
            await page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            current_url = page.url
            if 'login' in current_url or 'checkpoint' in current_url:
                return False
            
            print("✅ LinkedIn session active")
            return True
        except Exception as e:
            print(f"❌ Error checking login: {e}")
            return False
    
    async def scrape_job_recommendations(self, page):
        """
        Scrape job recommendations from LinkedIn feed
        
        This scrapes the "Recommended for you" jobs that appear in:
        1. LinkedIn feed (main page)
        2. Jobs page recommendations
        3. Notifications panel (right side)
        """
        print("\n📋 Scraping LinkedIn job recommendations...")
        jobs = []
        
        try:
            # Navigate to LinkedIn Jobs page
            print("🌐 Navigating to LinkedIn Jobs...")
            await page.goto("https://www.linkedin.com/jobs/", wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(3)
            
            # Scroll to load more jobs
            print("📜 Scrolling to load recommendations...")
            for i in range(3):
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(1)
            
            # Extract job cards from recommendations
            print("🔍 Extracting job listings...")
            
            # Try multiple selectors (LinkedIn changes these frequently)
            job_selectors = [
                "div.job-card-container",
                "li.jobs-job-board-list__item",
                "div.scaffold-layout__list-item",
                "div[data-job-id]",
                "li[data-occludable-job-id]"
            ]
            
            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    print(f"✅ Found {len(job_elements)} jobs using selector: {selector}")
                    break
            
            if not job_elements:
                print("⚠️ No job cards found with standard selectors")
                return jobs
            
            # Extract job data from each card
            for idx, job_card in enumerate(job_elements[:20], 1):  # Limit to 20 jobs
                try:
                    # Extract job URL
                    job_url = None
                    link = await job_card.query_selector("a[href*='/jobs/view/']")
                    if link:
                        job_url = await link.get_attribute("href")
                        # Clean URL (remove tracking params)
                        if job_url and '?' in job_url:
                            job_url = job_url.split('?')[0]
                    
                    if not job_url:
                        continue
                    
                    # Extract job ID from URL
                    job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                    if not job_id_match:
                        continue
                    job_id = job_id_match.group(1)
                    
                    # Extract job title
                    title_element = await job_card.query_selector("h3, .job-card-list__title, [class*='job-title']")
                    title = await title_element.inner_text() if title_element else "Unknown"
                    title = title.strip()
                    
                    # Extract company name
                    company_element = await job_card.query_selector(".job-card-container__company-name, [class*='company-name'], h4")
                    company = await company_element.inner_text() if company_element else "Unknown"
                    company = company.strip()
                    
                    # Extract location
                    location_element = await job_card.query_selector(".job-card-container__metadata-item, [class*='location']")
                    location = await location_element.inner_text() if location_element else "Unknown"
                    location = location.strip()
                    
                    # Check if Easy Apply
                    easy_apply_badge = await job_card.query_selector("[class*='easy-apply']")
                    easy_apply = "Yes" if easy_apply_badge else "Unknown"
                    
                    job_data = {
                        'job_id': job_id,
                        'url': f"https://www.linkedin.com/jobs/view/{job_id}",
                        'title': title,
                        'company': company,
                        'location': location,
                        'easy_apply': easy_apply,
                        'source': 'LinkedIn Notifications',
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    jobs.append(job_data)
                    print(f"  ✅ [{idx}] {title} at {company}")
                    
                except Exception as e:
                    print(f"  ⚠️ Error extracting job {idx}: {e}")
                    continue
            
            print(f"\n✅ Extracted {len(jobs)} job listings")
            
        except Exception as e:
            print(f"❌ Error scraping jobs: {e}")
        
        return jobs
    
    async def save_to_sheets(self, jobs):
        """Save jobs to Google Sheets LinkedIn tab"""
        if not jobs:
            print("⚠️ No jobs to save")
            return
        
        print(f"\n💾 Saving {len(jobs)} jobs to Google Sheets...")
        
        # Get existing URLs to avoid duplicates
        existing_jobs = self.sheet_manager.get_all_jobs(tab='linkedin')
        existing_urls = {job.get('ApplyURL', '') for job in existing_jobs}
        
        new_jobs = 0
        duplicates = 0
        
        for job in jobs:
            if job['url'] in existing_urls:
                duplicates += 1
                continue
            
            # Format job for Sheets
            job_data = {
                'CreatedAt': job['scraped_at'],
                'Company': job['company'],
                'Role': job['title'],
                'Location': job['location'],
                'RemoteScope': 'Unknown',  # Will be determined by AI
                'ApplyURL': job['url'],
                'Source': 'LinkedIn',
                'RecruiterEmail': '',
                'Currency': 'USD',
                'Comp': '',
                'Seniority': '',
                'WorkAuthReq': '',
                'Status': 'New',
                'NextAction': '',
                'Notes': f"Scraped from LinkedIn notifications on {job['scraped_at']}",
                'FitScore': '',  # Will be calculated by AI
                'Why': ''
            }
            
            try:
                self.sheet_manager.add_job(job_data, tab='linkedin')
                new_jobs += 1
                print(f"  ✅ Saved: {job['title']}")
            except Exception as e:
                print(f"  ❌ Error saving {job['title']}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"  New jobs saved: {new_jobs}")
        print(f"  Duplicates skipped: {duplicates}")
    
    async def run(self):
        """Main scraping workflow"""
        print("\n" + "="*70)
        print("🔍 LINKEDIN NOTIFICATIONS SCRAPER")
        print("="*70)
        print(f"Target: Job recommendations & notifications")
        print(f"Output: Google Sheets (LinkedIn tab)")
        print("="*70 + "\n")
        
        async with async_playwright() as p:
            print("🌐 Starting browser...")
            
            # Launch browser
            browser = await p.chromium.launch(
                headless=False,  # Set to True for background operation
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Load saved session if exists
            storage_state = None
            if os.path.exists(self.session_file):
                storage_state = self.session_file
                print("📂 Loading saved LinkedIn session...")
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                storage_state=storage_state
            )
            
            page = await context.new_page()
            
            # Check if logged in
            is_logged_in = await self.check_login(page)
            
            if not is_logged_in:
                print("\n❌ Not logged into LinkedIn!")
                print("\nPlease:")
                print("1. Login to LinkedIn in your browser")
                print("2. Keep the session active")
                print("3. Run this script again")
                await browser.close()
                return
            
            # Save session for future use
            os.makedirs("data/credentials", exist_ok=True)
            await context.storage_state(path=self.session_file)
            print("💾 LinkedIn session saved\n")
            
            # Scrape jobs
            jobs = await self.scrape_job_recommendations(page)
            
            if jobs:
                # Save to Google Sheets
                await self.save_to_sheets(jobs)
            else:
                print("⚠️ No jobs found to save")
            
            await browser.close()
            
            print("\n" + "="*70)
            print("✅ SCRAPING COMPLETE")
            print("="*70)


async def main():
    scraper = LinkedInNotificationsScraper()
    await scraper.run()


if __name__ == '__main__':
    asyncio.run(main())
