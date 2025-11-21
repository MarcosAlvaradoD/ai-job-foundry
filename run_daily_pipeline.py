#!/usr/bin/env python3
"""
Daily Pipeline - Master orchestrator for AI Job Foundry
Controls the entire job search automation workflow

Usage:
    py run_daily_pipeline.py --all              # Run complete pipeline
    py run_daily_pipeline.py --emails           # Process emails only
    py run_daily_pipeline.py --analyze          # AI analysis only
    py run_daily_pipeline.py --apply            # Auto-apply only
    py run_daily_pipeline.py --emails --analyze # Email + AI
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def log(msg: str, level: str = "INFO"):
    """Unified logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARN": "⚠️ "
    }.get(level, "")
    print(f"[{timestamp}] {prefix} {msg}")

def run_email_processing():
    """Step 1: Process new emails from JOBS/Inbound"""
    log("STEP 1: Processing emails...", "INFO")
    
    try:
        from core.ingestion.ingest_email_to_sheet_v2 import main as ingest_main
        ingest_main()
        log("Email processing completed", "SUCCESS")
        return True
    except Exception as e:
        log(f"Email processing failed: {e}", "ERROR")
        return False

def run_ai_analysis():
    """Step 2: Analyze jobs with AI and calculate FIT SCORES"""
    log("STEP 2: Running AI analysis...", "INFO")
    
    try:
        import sys
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        # Load environment
        load_dotenv()
        
        # Find CV file
        cv_path = Path(__file__).parent / "data" / "cv_descriptor.txt"
        if not cv_path.exists():
            log(f"CV not found at {cv_path}", "ERROR")
            return False
        
        # Get Sheet ID from .env
        sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        if not sheet_id:
            log("GOOGLE_SHEETS_ID not found in .env", "ERROR")
            return False
        
        # Set args for the analysis script
        sys.argv = [
            'enrich_sheet_with_llm_v3.py',
            '--sheet', sheet_id,
            '--cv', str(cv_path),
            '--min-fit', '0',
            '--force'
        ]
        
        from core.enrichment.enrich_sheet_with_llm_v3 import main as analyze_main
        analyze_main()
        log("AI analysis completed", "SUCCESS")
        return True
    except Exception as e:
        log(f"AI analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_auto_apply(dry_run: bool = True):
    """Step 3: Auto-apply to high-fit jobs"""
    mode = "DRY RUN" if dry_run else "LIVE"
    log(f"STEP 3: Auto-apply ({mode})...", "INFO")
    
    if dry_run:
        log("Dry run mode - no real applications", "WARN")
    
    try:
        # TODO: Import auto-apply module when ready
        log("Auto-apply module not implemented yet", "WARN")
        return True
    except Exception as e:
        log(f"Auto-apply failed: {e}", "ERROR")
        return False

def check_expired_jobs():
    """Step 4: Mark jobs as expired if >30 days old OR URL is dead"""
    log("STEP 4: Checking for expired jobs...", "INFO")
    
    try:
        from core.sheets.sheet_manager import SheetManager
        from datetime import timedelta
        
        sheet_manager = SheetManager()
        jobs = sheet_manager.get_all_jobs()
        
        today = datetime.now()
        expired_count = 0
        
        # Method 1: Check by date (>30 days)
        log("  Checking by date (>30 days old)...", "INFO")
        for job in jobs:
            created_at = job.get('CreatedAt', '')
            status = job.get('Status', '')
            
            if not created_at or status in ['Applied', 'Rejected', 'Expired']:
                continue
            
            try:
                created_date = datetime.fromisoformat(created_at)
                days_old = (today - created_date).days
                
                if days_old > 30:
                    # Mark as expired
                    log(f"  Expiring: {job.get('Role')} at {job.get('Company')} ({days_old} days old)", "WARN")
                    expired_count += 1
                    row_index = job.get('row_index')
                    if row_index:
                        sheet_manager.update_job_status(row_index, 'Expired')
            except:
                continue
        
        if expired_count > 0:
            log(f"  Date check: Marked {expired_count} jobs as expired", "SUCCESS")
        else:
            log("  Date check: No expired jobs found", "INFO")
        
        # Method 2: Verify URLs (optional, can be slow)
        log("  Verifying URLs (checking if postings are still live)...", "INFO")
        
        # Get jobs to verify (only New status, FIT >= 7, not expired by date)
        jobs_to_verify = []
        for job in jobs:
            status = job.get('Status', '')
            fit_score = job.get('FitScore', 0)
            
            if status == 'New':
                try:
                    if int(fit_score) >= 7:
                        jobs_to_verify.append(job)
                except:
                    pass
        
        if jobs_to_verify:
            log(f"  Verifying {len(jobs_to_verify)} high-fit jobs...", "INFO")
            
            # Import and run verifier
            from verify_job_status import JobStatusVerifier
            verifier = JobStatusVerifier()
            verifier.verify_jobs(jobs_to_verify[:5], rate_limit_seconds=3)  # Limit to 5 to save time
            
            log(f"  URL verification: {verifier.results['expired']} expired, {verifier.results['still_active']} active", "SUCCESS")
        else:
            log("  No high-fit jobs to verify", "INFO")
        
        return True
    except Exception as e:
        log(f"Expired check failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def generate_report():
    """Step 5: Generate daily summary report"""
    log("STEP 5: Generating report...", "INFO")
    
    try:
        from core.sheets.sheet_manager import SheetManager
        
        sheet_manager = SheetManager()
        jobs = sheet_manager.get_all_jobs()
        
        # Count by status
        stats = {
            'total': len(jobs),
            'new': 0,
            'applied': 0,
            'interview': 0,
            'rejected': 0,
            'expired': 0,
            'high_fit': 0  # FIT >= 7
        }
        
        for job in jobs:
            status = job.get('Status', 'Unknown')
            fit_score = job.get('FitScore', 0)
            
            if status == 'New':
                stats['new'] += 1
            elif status == 'Applied':
                stats['applied'] += 1
            elif status == 'Interview':
                stats['interview'] += 1
            elif status == 'Rejected':
                stats['rejected'] += 1
            elif status == 'Expired':
                stats['expired'] += 1
            
            try:
                if int(fit_score) >= 7:
                    stats['high_fit'] += 1
            except:
                pass
        
        # Print report
        print("\n" + "="*60)
        print("📊 DAILY REPORT - AI JOB FOUNDRY")
        print("="*60)
        print(f"Total Jobs:       {stats['total']}")
        print(f"  New:            {stats['new']}")
        print(f"  Applied:        {stats['applied']}")
        print(f"  Interview:      {stats['interview']}")
        print(f"  Rejected:       {stats['rejected']}")
        print(f"  Expired:        {stats['expired']}")
        print(f"  High Fit (7+):  {stats['high_fit']}")
        print("="*60 + "\n")
        
        log("Report generated", "SUCCESS")
        return True
    except Exception as e:
        log(f"Report generation failed: {e}", "ERROR")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='AI Job Foundry - Daily Pipeline Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py run_daily_pipeline.py --all              # Full pipeline
  py run_daily_pipeline.py --emails           # Process emails only
  py run_daily_pipeline.py --emails --analyze # Email + AI analysis
  py run_daily_pipeline.py --apply --dry-run  # Test auto-apply
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Run complete pipeline (emails + analyze + expire check + report)')
    parser.add_argument('--emails', action='store_true',
                       help='Process new emails')
    parser.add_argument('--analyze', action='store_true',
                       help='Run AI analysis on new jobs')
    parser.add_argument('--apply', action='store_true',
                       help='Auto-apply to high-fit jobs')
    parser.add_argument('--expire', action='store_true',
                       help='Check and mark expired jobs')
    parser.add_argument('--report', action='store_true',
                       help='Generate daily report')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode (no real applications)')
    
    args = parser.parse_args()
    
    # If no flags, show help
    if not any([args.all, args.emails, args.analyze, args.apply, args.expire, args.report]):
        parser.print_help()
        return
    
    print("\n" + "="*70)
    print("🚀 AI JOB FOUNDRY - DAILY PIPELINE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    results = []
    
    # Run selected steps
    if args.all or args.emails:
        results.append(('Email Processing', run_email_processing()))
    
    if args.all or args.analyze:
        results.append(('AI Analysis', run_ai_analysis()))
    
    if args.all or args.apply:
        results.append(('Auto-Apply', run_auto_apply(dry_run=args.dry_run)))
    
    if args.all or args.expire:
        results.append(('Expire Check', check_expired_jobs()))
    
    if args.all or args.report:
        results.append(('Report', generate_report()))
    
    # Final summary
    print("\n" + "="*70)
    print("📈 PIPELINE SUMMARY")
    print("="*70)
    for step, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step:20} {status}")
    print("="*70)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Exit code
    sys.exit(0 if all(r[1] for r in results) else 1)

if __name__ == '__main__':
    main()
