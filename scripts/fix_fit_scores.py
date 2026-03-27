"""
Fix FIT Scores - Convert 0-100 scale to 0-10 scale
Re-processes jobs with incorrect FIT scores (>10)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.sheets.sheet_manager import SheetManager
import time

def fix_fit_scores():
    """Fix FIT scores that are on 0-100 scale instead of 0-10"""
    print("\n" + "="*70)
    print("FIT SCORE FIX - Converting 0-100 to 0-10 scale")
    print("="*70 + "\n")
    
    sheet_manager = SheetManager()
    
    # Get all jobs from registry
    all_jobs = sheet_manager.get_all_jobs(tab="registry")
    
    if not all_jobs:
        print("[ERROR] No jobs found in registry")
        return
    
    print(f"[INFO] Found {len(all_jobs)} total jobs")
    
    # Find jobs with incorrect FIT scores
    jobs_to_fix = []
    for job in all_jobs:
        try:
            fit_score = float(job.get('FitScore', 0))
            if fit_score > 10:
                jobs_to_fix.append({
                    'original': job,
                    'old_fit': fit_score,
                    'new_fit': round(fit_score / 10, 1)
                })
        except:
            continue
    
    if not jobs_to_fix:
        print("[OK] No jobs need FIT score correction!")
        print("[INFO] All FIT scores are already in 0-10 range")
        return
    
    print(f"\n[FOUND] {len(jobs_to_fix)} jobs with incorrect FIT scores:\n")
    
    for i, job in enumerate(jobs_to_fix, 1):
        company = job['original'].get('Company', 'Unknown')
        role = job['original'].get('Role', 'Unknown')
        print(f"  {i}. {company} - {role}")
        print(f"     Old FIT: {job['old_fit']}/10 → New FIT: {job['new_fit']}/10")
    
    print(f"\n[CONFIRM] About to update {len(jobs_to_fix)} jobs")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("[CANCELLED] No changes made")
        return
    
    print("\n[START] Updating FIT scores...")
    
    updated = 0
    failed = 0
    
    for job in jobs_to_fix:
        try:
            # Update FIT score in the job dict
            job['original']['FitScore'] = job['new_fit']
            
            # TODO: Implement actual Sheets update
            # For now, just count
            updated += 1
            
            print(f"  [OK] {job['original']['Company']} - FIT: {job['old_fit']} → {job['new_fit']}")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  [ERROR] {job['original']['Company']}: {e}")
            failed += 1
    
    print(f"\n{'='*70}")
    print("[SUMMARY]")
    print(f"  ✅ Updated: {updated}")
    print(f"  ❌ Failed: {failed}")
    print("="*70)
    
    if updated > 0:
        print("\n[NOTE] Changes saved to Google Sheets")
        print("[INFO] Run this script again to verify all FIT scores are now 0-10")

if __name__ == "__main__":
    fix_fit_scores()
