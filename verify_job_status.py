#!/usr/bin/env python3
"""
Job Status Verifier - Checks if job postings are still active
Visits URLs periodically and marks expired ones automatically

Features:
- Detects 404 errors
- Detects "No longer available" messages
- Rate limiting to avoid blocks
- Updates Google Sheets automatically
- Skips already Applied/Rejected/Expired jobs

Usage:
    py verify_job_status.py --all           # Check all jobs
    py verify_job_status.py --new           # Only check New jobs
    py verify_job_status.py --high-fit      # Only check FIT >= 7
    py verify_job_status.py --limit 10      # Check only 10 jobs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import time
from datetime import datetime
from typing import Dict, List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from core.sheets.sheet_manager import SheetManager

class JobStatusVerifier:
    def __init__(self):
        self.sheet_manager = SheetManager()
        self.results = {
            'checked': 0,
            'still_active': 0,
            'expired': 0,
            'error': 0,
            'skipped': 0
        }
    
    def log(self, msg: str, level: str = "INFO"):
        """Unified logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARN": "⚠️ ",
            "EXPIRED": "🚫"
        }.get(level, "")
        print(f"[{timestamp}] {prefix} {msg}")
    
    def is_job_expired(self, page, url: str) -> tuple[bool, str]:
        """
        Visits URL and determines if job posting is expired
        Returns: (is_expired: bool, reason: str)
        """
        try:
            # Navigate with timeout
            response = page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Check HTTP status
            if response.status == 404:
                return True, "404 Not Found"
            
            if response.status >= 500:
                return False, f"Server error {response.status} (assume active)"
            
            # Wait a bit for dynamic content
            time.sleep(2)
            
            # Get page content
            content = page.content().lower()
            
            # LinkedIn patterns
            linkedin_expired_patterns = [
                'no longer accepting applications',
                'this job is no longer available',
                'posting has been removed',
                'job posting not found',
                'the job you are trying to view',
                'oops! we can\'t find that job',
            ]
            
            # Indeed patterns
            indeed_expired_patterns = [
                'this job has expired',
                'job has been removed',
                'no longer available',
                'job posting has expired',
            ]
            
            # Glassdoor patterns (English + Spanish)
            glassdoor_expired_patterns = [
                'job not found',
                'this job is no longer available',
                'posting has been removed',
                'este empleo no está disponible',  # Spanish
                'no es posible acceder a su contenido',  # Spanish
            ]
            
            all_patterns = linkedin_expired_patterns + indeed_expired_patterns + glassdoor_expired_patterns
            
            for pattern in all_patterns:
                if pattern in content:
                    return True, f"Detected: '{pattern}'"
            
            # If we got here, job is probably still active
            return False, "Active (no expiration detected)"
            
        except PlaywrightTimeout:
            return False, "Timeout (assume active)"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def verify_jobs(self, jobs: List[Dict], rate_limit_seconds: int = 3):
        """Verify a list of jobs"""
        
        if not jobs:
            self.log("No jobs to verify", "WARN")
            return
        
        self.log(f"Starting verification of {len(jobs)} jobs...", "INFO")
        self.log(f"Rate limit: {rate_limit_seconds}s between requests", "INFO")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            for idx, job in enumerate(jobs, 1):
                job_id = job.get('row_index', idx)
                company = job.get('Company', 'Unknown')
                role = job.get('Role', 'Unknown')
                url = job.get('ApplyURL', '')
                status = job.get('Status', '')
                
                if not url:
                    self.log(f"[{idx}/{len(jobs)}] Skipping {role} at {company}: No URL", "WARN")
                    self.results['skipped'] += 1
                    continue
                
                # Skip already processed
                if status in ['Applied', 'Rejected', 'Expired', 'Interview']:
                    self.log(f"[{idx}/{len(jobs)}] Skipping {role} at {company}: Status={status}", "INFO")
                    self.results['skipped'] += 1
                    continue
                
                self.log(f"[{idx}/{len(jobs)}] Checking: {role} at {company}...", "INFO")
                self.results['checked'] += 1
                
                # Check if expired
                is_expired, reason = self.is_job_expired(page, url)
                
                if is_expired:
                    self.log(f"  ❌ EXPIRED: {reason}", "EXPIRED")
                    self.results['expired'] += 1
                    
                    # Update status in Sheets
                    try:
                        self.sheet_manager.update_job_status(job_id, 'Expired')
                        self.log(f"  ✅ Updated Sheets: Status → Expired", "SUCCESS")
                    except Exception as e:
                        self.log(f"  ⚠️  Failed to update Sheets: {e}", "ERROR")
                        self.results['error'] += 1
                else:
                    self.log(f"  ✅ Still active: {reason}", "SUCCESS")
                    self.results['still_active'] += 1
                
                # Rate limiting
                if idx < len(jobs):
                    time.sleep(rate_limit_seconds)
            
            browser.close()
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total Checked:     {self.results['checked']}")
        print(f"  Still Active:    {self.results['still_active']}")
        print(f"  Expired:         {self.results['expired']}")
        print(f"  Errors:          {self.results['error']}")
        print(f"  Skipped:         {self.results['skipped']}")
        print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Verify job posting status automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py verify_job_status.py --all           # Check all jobs
  py verify_job_status.py --new           # Only New status jobs
  py verify_job_status.py --high-fit      # Only FIT >= 7
  py verify_job_status.py --limit 10      # Check first 10 only
        """
    )
    
    parser.add_argument('--all', action='store_true',
                       help='Check all jobs (excluding Applied/Rejected/Expired)')
    parser.add_argument('--new', action='store_true',
                       help='Only check jobs with Status=New')
    parser.add_argument('--high-fit', action='store_true',
                       help='Only check jobs with FIT >= 7')
    parser.add_argument('--limit', type=int,
                       help='Limit number of jobs to check')
    parser.add_argument('--rate-limit', type=int, default=3,
                       help='Seconds between requests (default: 3)')
    
    args = parser.parse_args()
    
    if not any([args.all, args.new, args.high_fit]):
        parser.print_help()
        return
    
    verifier = JobStatusVerifier()
    sheet_manager = SheetManager()
    
    # Get all jobs
    all_jobs = sheet_manager.get_all_jobs()
    
    # Filter based on arguments
    jobs_to_check = []
    
    for job in all_jobs:
        status = job.get('Status', '')
        fit_score = job.get('FitScore', 0)
        
        # Skip already processed
        if status in ['Applied', 'Rejected', 'Expired', 'Interview']:
            continue
        
        # Apply filters
        if args.new and status != 'New':
            continue
        
        if args.high_fit:
            try:
                if int(fit_score) < 7:
                    continue
            except:
                continue
        
        jobs_to_check.append(job)
    
    # Apply limit
    if args.limit:
        jobs_to_check = jobs_to_check[:args.limit]
    
    # Run verification
    verifier.verify_jobs(jobs_to_check, rate_limit_seconds=args.rate_limit)
    verifier.print_summary()

if __name__ == '__main__':
    main()
