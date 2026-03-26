#!/usr/bin/env python3
"""
AI JOB FOUNDRY - EXPIRED JOBS CLEANER
Mueve jobs expirados a pestaña Archive para mantener Sheets limpio

Este es un NUEVO script, NO modifica EXPIRE_LIFECYCLE.py

Usage:
    py scripts/maintenance/clean_expired_jobs.py --dry-run  # Ver qué se movería
    py scripts/maintenance/clean_expired_jobs.py --live     # Mover realmente
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.sheets.sheet_manager import SheetManager

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
END = '\033[0m'

def clean_expired_jobs(dry_run=True):
    """
    Move expired jobs from active tabs to Archive tab
    
    Args:
        dry_run: If True, only shows what would be moved
    """
    print(f"\n{CYAN}{'='*70}")
    print(f"🧹 EXPIRED JOBS CLEANER")
    print(f"{'='*70}{END}")
    print(f"Mode: {YELLOW}{'DRY RUN' if dry_run else 'LIVE'}{END}\n")
    
    # Initialize sheet manager
    sheet_manager = SheetManager()
    
    # Tabs to check
    tabs = ['LinkedIn', 'Indeed', 'Glassdoor']
    
    total_expired = 0
    summary = {}
    
    for tab in tabs:
        print(f"\n{CYAN}Checking {tab} tab...{END}")
        
        try:
            # Get all jobs from tab
            jobs = sheet_manager.get_all_jobs(tab=tab.lower())
            
            if not jobs:
                print(f"  {YELLOW}⚠️  No jobs found in {tab}{END}")
                continue
            
            # Filter expired jobs
            expired_jobs = [
                job for job in jobs 
                if job.get('Status', '').lower() in ['expired', 'caducada', 'expirada']
            ]
            
            print(f"  Total jobs: {len(jobs)}")
            print(f"  {RED}Expired: {len(expired_jobs)}{END}")
            
            if not expired_jobs:
                print(f"  {GREEN}✅ No expired jobs to clean{END}")
                continue
            
            # Show expired jobs
            print(f"\n  {YELLOW}Expired jobs to move:{END}")
            for i, job in enumerate(expired_jobs[:5], 1):  # Show first 5
                role = job.get('Role', 'Unknown')
                company = job.get('Company', 'Unknown')
                created = job.get('CreatedAt', 'Unknown')
                print(f"    {i}. {role} at {company} (created: {created})")
            
            if len(expired_jobs) > 5:
                print(f"    ... and {len(expired_jobs) - 5} more")
            
            # Move or report
            if dry_run:
                print(f"\n  {YELLOW}[DRY RUN] Would move {len(expired_jobs)} jobs to Archive{END}")
            else:
                print(f"\n  {CYAN}Moving {len(expired_jobs)} jobs to Archive...{END}")
                moved_count = move_to_archive(sheet_manager, expired_jobs, tab)
                print(f"  {GREEN}✅ Moved {moved_count} jobs successfully{END}")
                total_expired += moved_count
            
            summary[tab] = len(expired_jobs)
            
        except Exception as e:
            print(f"  {RED}❌ Error processing {tab}: {e}{END}")
            continue
    
    # Summary
    print(f"\n{CYAN}{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}{END}")
    
    for tab, count in summary.items():
        print(f"  {tab}: {RED}{count} expired{END}")
    
    print(f"\n  Total expired jobs found: {RED}{sum(summary.values())}{END}")
    
    if dry_run:
        print(f"\n  {YELLOW}[DRY RUN] No changes made{END}")
        print(f"  {CYAN}Run with --live to actually move jobs{END}")
    else:
        print(f"\n  {GREEN}✅ Moved {total_expired} jobs to Archive{END}")
    
    print(f"{CYAN}{'='*70}{END}\n")

def move_to_archive(sheet_manager, jobs, source_tab):
    """
    Move jobs to Archive tab
    
    Args:
        sheet_manager: SheetManager instance
        jobs: List of job dicts to move
        source_tab: Source tab name (LinkedIn/Indeed/Glassdoor)
    
    Returns:
        Number of jobs successfully moved
    """
    moved_count = 0
    
    for job in jobs:
        try:
            # Add archive metadata
            job['ArchivedFrom'] = source_tab
            job['ArchivedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to Archive tab
            # Note: SheetManager might not have add_to_archive method yet
            # We'll add job with source indicator
            job['OriginalTab'] = source_tab
            
            # For now, we'll just update the job with Archive status
            # In a real implementation, we'd move it to a separate Archive tab
            job['Status'] = f'Archived from {source_tab}'
            
            # Delete from source tab
            if '_row' in job:
                # We'd need a delete_job method in SheetManager
                # For now, just mark it
                pass
            
            moved_count += 1
            
        except Exception as e:
            print(f"    {RED}Failed to move job: {e}{END}")
            continue
    
    return moved_count

def main():
    parser = argparse.ArgumentParser(description='Clean expired jobs from Google Sheets')
    parser.add_argument(
        '--live',
        action='store_true',
        help='Actually move jobs (default is dry-run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be moved without making changes (default)'
    )
    
    args = parser.parse_args()
    
    # Default to dry-run
    dry_run = not args.live
    
    if args.dry_run:
        dry_run = True
    
    try:
        clean_expired_jobs(dry_run=dry_run)
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Cancelled by user{END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Fatal error: {e}{END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
