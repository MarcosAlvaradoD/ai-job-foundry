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
        """Get jobs eligible for auto-apply (FIT 7+, not applied)"""
        all_jobs = self.sheet_manager.get_all_jobs()
        
        eligible = [
            job for job in all_jobs
            if (
                self._safe_fit_score(job.get('FitScore', 0)) >= FIT_SCORE_THRESHOLD and
                job.get('Status') != 'Applied' and
                job.get('ApplyURL') and
                'linkedin.com' in job.get('ApplyURL', '').lower() and
                'easy apply' in job.get('ApplyType', '').lower()
            )
        ]
        
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
            row_index = job.get('_row_index')  # Assuming this is stored
            
            if applied:
                self.sheet_manager.update_job_status(
                    row_index,
                    status='Applied',
                    notes=f"Auto-applied on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                print(f"✅ Updated status to 'Applied'")
            else:
                self.sheet_manager.update_job_status(
                    row_index,
                    status='ApplicationFailed',
                    notes='Auto-apply failed - requires manual application'
                )
                print(f"⚠️ Updated status to 'ApplicationFailed'")
                
        except Exception as e:
            print(f"❌ Failed to update Google Sheets: {e}")
    
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
            
            # Create context with LinkedIn session
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Check if user needs to login
            print("\n⚠️ IMPORTANT: You must be logged into LinkedIn in this browser!")
            print("Please login manually if needed, then press Enter...")
            
            if not self.dry_run:
                input()
            
            # Process each eligible job
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
    
    args = parser.parse_args()
    
    # Determine mode
    if args.live:
        dry_run = False
        print("\n⚠️ WARNING: LIVE MODE - Real applications will be submitted!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cancelled")
            return
    else:
        dry_run = True
    
    # Run auto-applier
    applier = LinkedInAutoApplier(dry_run=dry_run)
    await applier.run()


if __name__ == '__main__':
    asyncio.run(main())
