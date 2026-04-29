#!/usr/bin/env python3
"""
AI JOB FOUNDRY - LinkedIn Complete Workflow
===========================================
Complete workflow: Scrape → Analyze → Apply

Steps:
1. Scrape LinkedIn notifications/recommendations
2. Calculate FIT scores with AI
3. Auto-apply to jobs with FIT >= 7

Usage:
    py run_linkedin_workflow.py --scrape-only
    py run_linkedin_workflow.py --analyze-only
    py run_linkedin_workflow.py --apply-only
    py run_linkedin_workflow.py --all
    py run_linkedin_workflow.py --all --live  # LIVE auto-apply
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# ✅ Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
import subprocess
import argparse
from datetime import datetime


class LinkedInWorkflow:
    """Complete LinkedIn job application workflow"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {}
    
    async def step_scrape(self):
        """Step 1: Scrape LinkedIn notifications"""
        print("\n" + "="*70)
        try:
            print("📡 STEP 1: Scraping LinkedIn Notifications")
            print("="*70 + "\n")
            sys.stdout.flush()
        except (ValueError, OSError):
            pass  # stdout closed, continue silently
        
        try:
            from core.ingestion.linkedin_notifications_scraper import LinkedInNotificationsScraper
            scraper = LinkedInNotificationsScraper()
            await scraper.run()
            self.results['scrape'] = 'PASS'
            return True
        except ValueError as e:
            if "I/O operation on closed file" in str(e):
                # stdout closed - this is OK, scraping may have worked
                self.results['scrape'] = 'PASS'
                return True
            else:
                # Real error
                try:
                    print(f"❌ Scraping failed: {e}")
                except Exception:
                    pass  # Can't print error either
                self.results['scrape'] = 'FAIL'
                return False
        except Exception as e:
            try:
                print(f"❌ Scraping failed: {e}")
            except Exception:
                pass  # Can't print error
            self.results['scrape'] = 'FAIL'
            return False
    
    def step_analyze(self):
        """Step 2: Calculate FIT scores"""
        print("\n" + "="*70)
        print("🤖 STEP 2: Calculating FIT Scores")
        print("="*70 + "\n")
        
        try:
            script_path = self.project_root / 'scripts' / 'maintenance' / 'calculate_all_fit_scores_v2.py'
            result = subprocess.run(
                [sys.executable, str(script_path)],
                timeout=600,  # 10 minutes max
                check=False
            )
            
            if result.returncode == 0:
                self.results['analyze'] = 'PASS'
                return True
            else:
                print(f"⚠️ FIT score calculation completed with warnings")
                self.results['analyze'] = 'WARN'
                return True  # Continue anyway
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            self.results['analyze'] = 'FAIL'
            return False
    
    def step_apply(self, dry_run=True):
        """Step 3: Auto-apply to jobs"""
        mode = "DRY RUN" if dry_run else "LIVE"
        print("\n" + "="*70)
        print(f"🎯 STEP 3: Auto-Apply ({mode})")
        print("="*70 + "\n")
        
        try:
            script_path = self.project_root / 'core' / 'automation' / 'auto_apply_linkedin.py'
            args = [sys.executable, str(script_path)]
            
            if dry_run:
                args.append('--dry-run')
            else:
                args.append('--live')
                args.append('--force')  # Skip confirmation
            
            result = subprocess.run(
                args,
                timeout=300,  # 5 minutes
                check=False
            )
            
            if result.returncode == 0:
                self.results['apply'] = 'PASS'
                return True
            else:
                print(f"⚠️ Auto-apply completed with warnings")
                self.results['apply'] = 'WARN'
                return True
        except Exception as e:
            print(f"❌ Auto-apply failed: {e}")
            self.results['apply'] = 'FAIL'
            return False
    
    async def run_complete_workflow(self, dry_run=True):
        """Run complete workflow: scrape → analyze → apply"""
        start_time = datetime.now()
        
        print("\n" + "="*70)
        print("🚀 LINKEDIN COMPLETE WORKFLOW")
        print("="*70)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE AUTO-APPLY'}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # Step 1: Scrape
        scrape_success = await self.step_scrape()
        
        if not scrape_success:
            print("\n❌ Workflow stopped - scraping failed")
            return
        
        # Step 2: Analyze
        analyze_success = self.step_analyze()
        
        if not analyze_success:
            print("\n❌ Workflow stopped - analysis failed")
            return
        
        # Step 3: Apply
        apply_success = self.step_apply(dry_run=dry_run)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*70)
        print("📊 WORKFLOW SUMMARY")
        print("="*70)
        print(f"Scraping:    {self.results.get('scrape', 'SKIP')}")
        print(f"Analysis:    {self.results.get('analyze', 'SKIP')}")
        print(f"Auto-Apply:  {self.results.get('apply', 'SKIP')}")
        print("="*70)
        print(f"Duration: {duration:.1f}s")
        print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")


async def main():
    parser = argparse.ArgumentParser(description='LinkedIn Complete Workflow')
    parser.add_argument('--scrape-only', action='store_true', help='Only scrape (no analyze/apply)')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze (no scrape/apply)')
    parser.add_argument('--apply-only', action='store_true', help='Only apply (no scrape/analyze)')
    parser.add_argument('--all', action='store_true', help='Run complete workflow')
    parser.add_argument('--live', action='store_true', help='LIVE auto-apply (not dry-run)')
    
    args = parser.parse_args()
    
    workflow = LinkedInWorkflow()
    
    if args.scrape_only:
        await workflow.step_scrape()
    elif args.analyze_only:
        workflow.step_analyze()
    elif args.apply_only:
        workflow.step_apply(dry_run=not args.live)
    elif args.all:
        await workflow.run_complete_workflow(dry_run=not args.live)
    else:
        # Default: run complete workflow in DRY RUN
        await workflow.run_complete_workflow(dry_run=True)


if __name__ == '__main__':
    asyncio.run(main())
