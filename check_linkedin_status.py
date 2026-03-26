#!/usr/bin/env python3
"""Quick check of LinkedIn jobs status"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from core.sheets.sheet_manager import SheetManager

def main():
    sheet_mgr = SheetManager()
    
    # Get LinkedIn data
    print('\n' + '='*70)
    print('LINKEDIN TAB STATUS')
    print('='*70)
    
    jobs = sheet_mgr.get_all_jobs(tab='linkedin')
    
    if not jobs:
        print('No data found in LinkedIn tab')
        return
    
    print(f'\nTotal jobs: {len(jobs)}')
    
    # Count by status
    statuses = {}
    fit_scores = []
    ready_for_apply = []
    
    for job in jobs:
        # Status
        status = job.get('Status', 'Unknown')
        statuses[status] = statuses.get(status, 0) + 1
        
        # FIT score
        try:
            fit_score = float(job.get('FitScore', 0))
            if fit_score > 0:
                fit_scores.append(fit_score)
        except:
            fit_score = 0
        
        # Easy Apply
        easy = job.get('EasyApply', '')
        
        # Check if ready for auto-apply
        if (fit_score >= 7 and 
            easy == 'Yes' and 
            status not in ['Applied', 'Rejected', 'EXPIRED', 'Application submitted']):
            
            role = job.get('Role', 'Unknown')
            company = job.get('Company', 'Unknown')
            ready_for_apply.append((fit_score, role, company))
    
    # Print status breakdown
    print('\nStatus breakdown:')
    for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
        print(f'  {status}: {count}')
    
    # FIT scores summary
    if fit_scores:
        avg_fit = sum(fit_scores) / len(fit_scores)
        max_fit = max(fit_scores)
        min_fit = min(fit_scores)
        fit_7_plus = [f for f in fit_scores if f >= 7]
        
        print(f'\nFIT Scores (n={len(fit_scores)}):')
        print(f'  Average: {avg_fit:.1f}')
        print(f'  Range: {min_fit:.1f} - {max_fit:.1f}')
        print(f'  FIT >= 7: {len(fit_7_plus)} jobs')
    
    # Ready for auto-apply
    print(f'\n{"="*70}')
    print(f'READY FOR AUTO-APPLY: {len(ready_for_apply)} jobs')
    print(f'{"="*70}')
    
    if ready_for_apply:
        ready_for_apply.sort(reverse=True)  # Sort by FIT score desc
        print('\nTop candidates:')
        for i, (fit, role, company) in enumerate(ready_for_apply[:10], 1):
            print(f'{i}. [FIT {fit:.0f}] {role[:50]} @ {company[:30]}')
    
    print()

if __name__ == '__main__':
    main()
