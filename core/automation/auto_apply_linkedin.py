#!/usr/bin/env python3
"""
AI JOB FOUNDRY - AUTO-APPLY LINKEDIN
Automatically applies to LinkedIn Easy Apply jobs with FIT score 7+

Features:
- DRY RUN mode (testing without applying)
- LIVE mode (real applications)
- Rate limiting (max 10 applications per run)
- Stealth mode with Playwright
- Integration with Google Sheets
- Application tracking

Usage:
    py core/automation/auto_apply_linkedin.py --dry-run
    py core/automation/auto_apply_linkedin.py --live
    
Or via runner:
    py run_auto_apply.py --dry-run
    py run_auto_apply.py --live
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ✅ FIX: Windows UTF-8 support for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import time
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Constants
FIT_SCORE_THRESHOLD = 7
MAX_APPLICATIONS_PER_RUN = 10
APPLICATION_DELAY = 5  # seconds between applications


class LinkedInAutoApplier:
    """Automated LinkedIn Easy Apply application system"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.sheet_manager = SheetManager()
        self.applications_submitted = 0
        self.errors = []
    
    def _safe_fit_score(self, fit_value):
        """Safely convert FitScore to int, handling empty strings and formats like '8/10'"""
        try:
            if not fit_value or fit_value == '':
                return 0
            fit_str = str(fit_value).strip()
            if '/' in fit_str:
                return int(fit_str.split('/')[0])
            return int(fit_str)
        except Exception:
            return 0
        
    async def get_eligible_jobs(self):
        """
        Get jobs eligible for auto-apply from LinkedIn tab
        
        Criteria:
        - FIT score >= 7
        - Status != 'Applied' and != 'EXPIRED'
        - Has ApplyURL
        - From LinkedIn source (in LinkedIn tab)
        """
        # Get jobs specifically from LinkedIn tab
        linkedin_jobs = self.sheet_manager.get_all_jobs(tab='linkedin')
        
        # Add row numbers (starts at 2, after headers)
        for i, job in enumerate(linkedin_jobs, start=2):
            job['_row'] = i
        
        # FIX 2026-03-26: El filtro 'linkedin.com/jobs' era demasiado estricto.
        # Muchas URLs son de tipo /comm/jobs/, tracking, o redirect que igualmente
        # funcionan al navegar con Playwright. Solo requerir que tengan URL válida.
        BLOCKED_STATUSES = {'APPLIED', 'EXPIRED', 'REJECTED', 'NO MATCH', 'INVALID'}

        eligible = [
            job for job in linkedin_jobs
            if (
                self._safe_fit_score(job.get('FitScore', 0)) >= FIT_SCORE_THRESHOLD and
                job.get('Status', '').upper().strip() not in BLOCKED_STATUSES and
                job.get('ApplyURL', '').strip() not in ('', 'Unknown', 'N/A', 'None') and
                'linkedin.com' in job.get('ApplyURL', '').lower()  # Solo requerir dominio linkedin
            )
        ]

        if not eligible:
            # Debug: mostrar cuántos jobs hay y por qué no pasan el filtro
            print(f"\n🔍 DEBUG: {len(linkedin_jobs)} jobs en pestaña LinkedIn")
            for job in linkedin_jobs[:10]:
                fit = self._safe_fit_score(job.get('FitScore', 0))
                status = job.get('Status', '').upper().strip()
                url = job.get('ApplyURL', '')
                print(f"   • FIT={fit} | Status={status} | URL={'✅' if url else '❌ VACÍA'} | {job.get('Role','?')[:40]}")
            print()
        
        return eligible[:MAX_APPLICATIONS_PER_RUN]
    
    async def apply_to_job(self, job, page):
        """Apply to a single job using Playwright"""
        try:
            job_url = job.get('ApplyURL')
            job_title = job.get('Role', 'Unknown')
            company = job.get('Company', 'Unknown')
            
            print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Applying to: {job_title} at {company}")
            print(f"URL: {job_url}")
            
            if self.dry_run:
                print("✅ [DRY RUN] Would apply to this job")
                return True
            
            # Navigate to job page
            await page.goto(job_url, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Look for Easy Apply button
            easy_apply_button = page.locator('button:has-text("Easy Apply")').first
            
            if not await easy_apply_button.is_visible():
                print("❌ Easy Apply button not found")
                return False
            
            # Click Easy Apply
            await easy_apply_button.click()
            await asyncio.sleep(2)
            
            # Fill out application form
            # Note: This is a simplified version. Real implementation needs:
            # - Handle multi-step forms
            # - Fill in required fields
            # - Upload resume if needed
            # - Answer screening questions
            
            # Look for submit button
            submit_button = page.locator('button:has-text("Submit application")').first
            
            if await submit_button.is_visible():
                await submit_button.click()
                await asyncio.sleep(2)
                
                print("✅ Application submitted successfully")
                return True
            else:
                print("⚠️ Submit button not found - may require manual completion")
                return False
                
        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            self.errors.append({
                'job': f"{job_title} at {company}",
                'error': str(e)
            })
            return False
    
    async def update_job_status(self, job, applied=True):
        """Update job status in Google Sheets"""
        try:
            row = job.get('_row')  # Row number in sheet
            
            if not row:
                print("⚠️ Cannot update status - no row number")
                return
            
            if applied:
                updates = {
                    'Status': 'Application submitted',
                    'NextAction': f"Auto-applied {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
                self.sheet_manager.update_job(row, updates, 'linkedin')
                print(f"   ✅ Status → 'Application submitted'")
            else:
                updates = {
                    'Status': 'ParsedOK',
                    'NextAction': 'Auto-apply failed - manual needed'
                }
                self.sheet_manager.update_job(row, updates, 'linkedin')
                print(f"   ⚠️ Status → 'ParsedOK' (apply failed)")
                
        except Exception as e:
            print(f"   ❌ Failed to update Google Sheets: {e}")
    
    async def run(self):
        """Main auto-apply workflow"""
        print("\n" + "="*70)
        print("🚀 AI JOB FOUNDRY - AUTO-APPLY LINKEDIN")
        print("="*70)
        print(f"Mode: {'DRY RUN (testing only)' if self.dry_run else 'LIVE (real applications)'}")
        print(f"FIT Score threshold: {FIT_SCORE_THRESHOLD}+")
        print(f"Max applications per run: {MAX_APPLICATIONS_PER_RUN}")
        print("="*70 + "\n")
        
        # Get eligible jobs
        print("📋 Fetching eligible jobs from Google Sheets...")
        eligible_jobs = await self.get_eligible_jobs()
        
        if not eligible_jobs:
            print("\n✨ No eligible jobs found for auto-apply")
            print("Criteria: FIT score 7+, LinkedIn Easy Apply, not already applied")
            return
        
        print(f"\n✅ Found {len(eligible_jobs)} eligible jobs\n")
        
        # Start Playwright
        async with async_playwright() as p:
            print("🌐 Starting browser...")
            
            # Launch browser with stealth settings
            browser = await p.chromium.launch(
                headless=False,  # Set to True for headless mode
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # ✅ FIXED: Usa perfil de Chrome donde YA estás loggeado
            # Esto permite que LinkedIn mantenga la sesión
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                storage_state="data/credentials/linkedin_session.json" if os.path.exists("data/credentials/linkedin_session.json") else None
            )
            
            page = await context.new_page()
            
            # ✅ AUTO-LOGIN CHECK
            # Navigate to LinkedIn to check session
            print("\n🔐 Checking LinkedIn session...")
            await page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            # Check if logged in (look for feed)
            current_url = page.url
            if 'login' in current_url or 'checkpoint' in current_url:
                print("⚠️  Not logged in - attempting auto-login...")
                
                # Get credentials from .env
                linkedin_email = os.getenv('LINKEDIN_EMAIL')
                linkedin_password = os.getenv('LINKEDIN_PASSWORD')
                
                if not linkedin_email or not linkedin_password:
                    print("\n❌ ERROR: LinkedIn credentials not found in .env!")
                    print("Please add:")
                    print("  LINKEDIN_EMAIL=your@email.com")
                    print("  LINKEDIN_PASSWORD=your_password")
                    await browser.close()
                    return
                
                # Navigate to login page
                print("🔐 Logging in...")
                await page.goto("https://www.linkedin.com/login", wait_until='domcontentloaded')
                await asyncio.sleep(2)
                
                # Fill credentials
                await page.fill('input#username', linkedin_email)
                await asyncio.sleep(1)
                await page.fill('input#password', linkedin_password)
                await asyncio.sleep(1)
                
                # Click sign in
                await page.click('button[type="submit"]')
                await asyncio.sleep(5)
                
                # Check if login successful
                current_url = page.url
                if 'feed' not in current_url and 'checkpoint' not in current_url:
                    print("\n❌ ERROR: Auto-login failed!")
                    print("Possible reasons:")
                    print("  - Wrong credentials")
                    print("  - LinkedIn detected automation")
                    print("  - 2FA required (login manually once)")
                    await browser.close()
                    return
                
                print("✅ Auto-login successful!")
            else:
                print("✅ LinkedIn session already active!")
            
            # ✅ GUARDAR sesión para próximas ejecuciones
            os.makedirs("data/credentials", exist_ok=True)
            await context.storage_state(path="data/credentials/linkedin_session.json")
            print("   💾 Sesión guardada para próximas ejecuciones")
            
            # Process each eligible job (NO USER INPUT REQUIRED)
            for i, job in enumerate(eligible_jobs, 1):
                print(f"\n[{i}/{len(eligible_jobs)}] Processing job...")
                
                success = await self.apply_to_job(job, page)
                
                if not self.dry_run:
                    await self.update_job_status(job, applied=success)
                
                if success:
                    self.applications_submitted += 1
                
                # Rate limiting delay
                if i < len(eligible_jobs):
                    print(f"\n⏱️ Waiting {APPLICATION_DELAY} seconds before next application...")
                    await asyncio.sleep(APPLICATION_DELAY)
            
            await browser.close()
        
        # Summary
        print("\n" + "="*70)
        print("📊 AUTO-APPLY SUMMARY")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Jobs processed: {len(eligible_jobs)}")
        print(f"Applications {'(would be) ' if self.dry_run else ''}submitted: {self.applications_submitted}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors:
                print(f"  - {error['job']}: {error['error']}")
        
        print("="*70 + "\n")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Apply')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - no real applications'
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Live mode - submit real applications'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt (for pipeline automation)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.live:
        dry_run = False
        print("\n⚠️ WARNING: LIVE MODE - Real applications will be submitted!")
        # ✅ FIX: Skip confirmation if --force flag is present (for pipeline automation)
        if not args.force:
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Cancelled")
                return
        else:
            print("✅ Auto-confirmed with --force flag")
    else:
        dry_run = True
    
    # Run auto-applier
    applier = LinkedInAutoApplier(dry_run=dry_run)
    await applier.run()


if __name__ == '__main__':
    asyncio.run(main())
