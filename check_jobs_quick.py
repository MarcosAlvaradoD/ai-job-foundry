#!/usr/bin/env python3
"""
Quick Job Status Check
Shows current job counts, FIT scores, and what's ready for auto-apply
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from core.sheets.sheet_manager import SheetManager


def main():
    print("\n" + "="*70)
    print("📊 QUICK JOB STATUS CHECK")
    print("="*70 + "\n")
    
    sheet_manager = SheetManager()
    
    # Get all tabs
    tabs = ['LinkedIn', 'Indeed', 'Glassdoor', 'JobLeads', 'Computrabajo', 'Jobs']
    
    total_jobs = 0
    total_with_fit = 0
    total_ready_apply = 0
    
    print("📋 Jobs by Source:")
    print("-" * 70)
    
    for tab in tabs:
        try:
            jobs = sheet_manager.get_all_jobs(tab=tab.lower())
            
            with_fit = sum(1 for j in jobs if j.get('FitScore') and j.get('FitScore') != '')
            
            # Count ready for auto-apply
            ready = sum(
                1 for j in jobs
                if (
                    j.get('FitScore') and 
                    str(j.get('FitScore', '')).strip() and
                    (
                        (isinstance(j.get('FitScore'), (int, float)) and j.get('FitScore') >= 7) or
                        (isinstance(j.get('FitScore'), str) and '/' in j.get('FitScore') and int(j.get('FitScore').split('/')[0]) >= 7)
                    ) and
                    j.get('Status', '').upper() not in ['APPLIED', 'EXPIRED', 'REJECTED', 'APPLICATION SUBMITTED'] and
                    'linkedin.com/jobs' in j.get('ApplyURL', '').lower()
                )
            )
            
            total_jobs += len(jobs)
            total_with_fit += with_fit
            total_ready_apply += ready
            
            # Status emoji
            if ready > 0:
                status = "🔥"
            elif with_fit > 0:
                status = "✅"
            else:
                status = "⚪"
            
            print(f"{status} {tab:15} {len(jobs):4} jobs | {with_fit:3} with FIT | {ready:2} ready to apply")
            
        except Exception as e:
            print(f"⚠️  {tab:15} Error: {e}")
    
    print("-" * 70)
    print(f"{'TOTAL':15} {total_jobs:4} jobs | {total_with_fit:3} with FIT | {total_ready_apply:2} ready to apply")
    print("=" * 70 + "\n")
    
    # Summary
    if total_ready_apply > 0:
        print(f"🔥 {total_ready_apply} LinkedIn jobs ready for auto-apply!")
        print(f"   Run: py core\\automation\\auto_apply_linkedin.py --dry-run")
    elif total_with_fit < total_jobs:
        missing = total_jobs - total_with_fit
        print(f"🤖 {missing} jobs need FIT score calculation")
        print(f"   Run: py scripts\\maintenance\\calculate_all_fit_scores_v2.py")
    else:
        print("✅ All jobs have FIT scores")
        print("ℹ️  No LinkedIn jobs with FIT >= 7 available")
        print("\n💡 Try:")
        print("   1. Run LinkedIn scraper: py run_linkedin_workflow.py --scrape-only")
        print("   2. Check Glassdoor/JobLeads for manual applications")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
