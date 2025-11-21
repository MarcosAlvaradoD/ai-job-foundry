# -*- coding: utf-8 -*-
"""Quick script to check FIT scores in Google Sheets"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.sheets.sheet_manager import SheetManager

sm = SheetManager()

print("CHECKING FIT SCORES IN GOOGLE SHEETS\n")
print("="*70)

# Check Registry tab
print("\n[REGISTRY TAB]")
try:
    jobs = sm.get_all_jobs('registry')
    print(f"Total jobs: {len(jobs)}")
    
    if jobs:
        fit_scores = []
        for job in jobs:
            fit = job.get('FitScore', 'N/A')
            company = job.get('Company', 'Unknown')[:30]
            role = job.get('Role', 'Unknown')[:40]
            status = job.get('Status', 'Unknown')
            
            try:
                fit_int = int(fit)
                fit_scores.append(fit_int)
            except:
                fit_int = 0
            
            print(f"  FIT: {fit:>3} | {company:30} | {role:40} | {status}")
        
        if fit_scores:
            print(f"\nStatistics:")
            print(f"  Average FIT: {sum(fit_scores)/len(fit_scores):.1f}/10")
            print(f"  High FIT (7+): {sum(1 for f in fit_scores if f >= 7)} jobs")
            print(f"  Medium FIT (5-6): {sum(1 for f in fit_scores if 5 <= f < 7)} jobs")
            print(f"  Low FIT (0-4): {sum(1 for f in fit_scores if f < 5)} jobs")
    else:
        print("  No jobs found in Registry tab")
except Exception as e:
    print(f"  Error: {e}")

# Check Jobs tab (alternative name)
print("\n[JOBS TAB]")
try:
    jobs = sm.get_all_jobs('Jobs')
    print(f"Total jobs: {len(jobs)}")
    
    if jobs:
        fit_scores = []
        for job in jobs:
            fit = job.get('FitScore', 'N/A')
            company = job.get('Company', 'Unknown')[:30]
            role = job.get('Role', 'Unknown')[:40]
            status = job.get('Status', 'Unknown')
            
            try:
                fit_int = int(fit)
                fit_scores.append(fit_int)
            except:
                fit_int = 0
            
            print(f"  FIT: {fit:>3} | {company:30} | {role:40} | {status}")
        
        if fit_scores:
            print(f"\nStatistics:")
            print(f"  Average FIT: {sum(fit_scores)/len(fit_scores):.1f}/10")
            print(f"  High FIT (7+): {sum(1 for f in fit_scores if f >= 7)} jobs")
            print(f"  Medium FIT (5-6): {sum(1 for f in fit_scores if 5 <= f < 7)} jobs")
            print(f"  Low FIT (0-4): {sum(1 for f in fit_scores if f < 5)} jobs")
    else:
        print("  No jobs found in Jobs tab")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
