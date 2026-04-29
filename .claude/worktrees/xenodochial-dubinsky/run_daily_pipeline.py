#!/usr/bin/env python3
"""
Daily Pipeline - Master orchestrator for AI Job Foundry
Controls the entire job search automation workflow

Usage:
    py run_daily_pipeline.py --all              # Run complete pipeline
    py run_daily_pipeline.py --emails           # Process emails only
    py run_daily_pipeline.py --bulletins        # Process bulletins only
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

def run_bulletin_processing():
    """Step 1b: Process job bulletins from LinkedIn/Indeed/Glassdoor"""
    log("STEP 1b: Processing bulletins...", "INFO")
    
    try:
        from core.automation.job_bulletin_processor import JobBulletinProcessor
        
        processor = JobBulletinProcessor()
        processor.process_bulletins(max_emails=50)
        
        log("Bulletin processing completed", "SUCCESS")
        return True
    except Exception as e:
        log(f"Bulletin processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
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
        # Import auto-apply module
        import asyncio
        from core.automation.auto_apply_linkedin import LinkedInAutoApplier
        
        # Run auto-applier (it handles job selection internally)
        applier = LinkedInAutoApplier(dry_run=dry_run)
        
        # Run async applier (method is 'run' not 'process_jobs')
        asyncio.run(applier.run())
        
        log(f"Auto-apply completed: {applier.applications_submitted} applications submitted", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Auto-apply failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def check_expired_jobs():
    """
    Step 4: Verify and cleanup expired jobs
    
    FLUJO:
    1. Borra jobs ya marcados como EXPIRED (limpieza)
    2. Verifica jobs actuales con Playwright (marca nuevos EXPIRED)
    3. Próxima ejecución: borra los que se marcaron + marca nuevos
    """
    log("STEP 4: Checking for expired jobs...", "INFO")
    
    try:
        # PASO 1: Borrar jobs EXPIRED existentes
        log("  [1/4] Deleting previously marked EXPIRED jobs...", "INFO")
        try:
            import subprocess
            result = subprocess.run(
                ['py', 'EXPIRE_LIFECYCLE.py', '--delete'],
                capture_output=True,
                text=True,
                timeout=180  # 3 min max (increased from 2)
            )
            
            if result.returncode == 0:
                # Parse output to get deletion count
                output = result.stdout
                if "TOTAL DELETED:" in output:
                    deleted = output.split("TOTAL DELETED:")[1].split("\n")[0].strip()
                    log(f"    ✅ Deleted {deleted} EXPIRED jobs", "SUCCESS")
                else:
                    log(f"    ✅ Cleanup completed", "SUCCESS")
            else:
                log(f"    ⚠️  Cleanup warning: {result.stderr[:100]}", "WARN")
        except Exception as e:
            log(f"    ⚠️  Cleanup skipped: {str(e)[:50]}", "WARN")
        
        # PASO 2: Verificar Glassdoor con Playwright
        log("  [2/4] Verifying Glassdoor jobs with Playwright...", "INFO")
        try:
            from GLASSDOOR_SMART_VERIFIER import GlassdoorSmartVerifier
            verifier = GlassdoorSmartVerifier()
            results = verifier.verify_all(limit=None, mark_expired=True)
            
            if results:
                expired_count = len(results.get('expired', []))
                active_count = len(results.get('active', []))
                log(f"    ✅ Glassdoor: {expired_count} expired, {active_count} active", "SUCCESS")
        except Exception as e:
            log(f"    ⚠️  Glassdoor verification failed: {str(e)[:50]}", "WARN")
        
        # PASO 3: Verificar LinkedIn con Playwright (usando V3 mejorada)
        log("  [3/4] Verifying LinkedIn jobs with Playwright...", "INFO")
        try:
            from LINKEDIN_SMART_VERIFIER_V3 import LinkedInSmartVerifierV3
            verifier = LinkedInSmartVerifierV3()
            results = verifier.verify_all(limit=None, mark_expired=True)
            
            if results:
                expired_count = len(results.get('expired', []))
                active_count = len(results.get('active', []))
                log(f"    ✅ LinkedIn: {expired_count} expired, {active_count} active", "SUCCESS")
        except Exception as e:
            log(f"    ⚠️  LinkedIn verification failed: {str(e)[:50]}", "WARN")
        
        # PASO 4: Verificar Indeed con Playwright
        log("  [4/4] Verifying Indeed jobs with Playwright...", "INFO")
        try:
            from INDEED_SMART_VERIFIER import IndeedSmartVerifier
            verifier = IndeedSmartVerifier()
            results = verifier.verify_all(limit=None, mark_expired=True)
            
            if results:
                expired_count = len(results.get('expired', []))
                active_count = len(results.get('active', []))
                log(f"    ✅ Indeed: {expired_count} expired, {active_count} active", "SUCCESS")
        except Exception as e:
            log(f"    ⚠️  Indeed verification failed: {str(e)[:50]}", "WARN")
        
        log("  ✅ Expiration check completed", "SUCCESS")
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
            except Exception:
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
  py run_daily_pipeline.py --bulletins        # Process bulletins only
  py run_daily_pipeline.py --emails --analyze # Email + AI analysis
  py run_daily_pipeline.py --apply --dry-run  # Test auto-apply
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Run complete pipeline (emails + bulletins + analyze + expire check + report)')
    parser.add_argument('--emails', action='store_true',
                       help='Process new emails (direct recruiter messages)')
    parser.add_argument('--bulletins', action='store_true',
                       help='Process job bulletins (LinkedIn/Indeed/Glassdoor)')
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
    if not any([args.all, args.emails, args.bulletins, args.analyze, args.apply, args.expire, args.report]):
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
    
    if args.all or args.bulletins:
        results.append(('Bulletin Processing', run_bulletin_processing()))
    
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
