"""
Quick view of jobs from Google Sheets
Shows LinkedIn jobs with FIT >= 7
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.sheets.sheet_manager import SheetManager

def main():
    print("\n" + "="*70)
    print("JOBS FROM GOOGLE SHEETS - LinkedIn Filter")
    print("="*70 + "\n")
    
    sheet_manager = SheetManager()
    all_jobs = sheet_manager.get_all_jobs(tab="registry")
    
    if not all_jobs:
        print("[ERROR] No jobs found")
        return
    
    print(f"[INFO] Total jobs: {len(all_jobs)}\n")
    
    # Filter LinkedIn jobs
    linkedin_jobs = []
    external_jobs = []
    
    for job in all_jobs:
        url = job.get('ApplyURL', '')
        fit = job.get('FitScore', 0)
        
        try:
            fit_score = float(fit)
        except:
            fit_score = 0
        
        if 'linkedin.com/jobs' in url:
            linkedin_jobs.append({**job, 'FitScore': fit_score})
        elif url:
            external_jobs.append({**job, 'FitScore': fit_score})
    
    print(f"[LINKEDIN] Found {len(linkedin_jobs)} LinkedIn jobs")
    print(f"[EXTERNAL] Found {len(external_jobs)} external jobs\n")
    
    # Show LinkedIn jobs with FIT >= 7
    high_fit_linkedin = [j for j in linkedin_jobs if j['FitScore'] >= 7]
    
    if high_fit_linkedin:
        print(f"✅ HIGH FIT LINKEDIN JOBS (>= 7):\n")
        for i, job in enumerate(high_fit_linkedin, 1):
            company = job.get('Company', 'Unknown')
            role = job.get('Role', 'Unknown')
            fit = job.get('FitScore', 0)
            url = job.get('ApplyURL', '')
            status = job.get('Status', '')
            
            print(f"{i}. {company} - {role}")
            print(f"   FIT: {fit}/10 | Status: {status}")
            print(f"   URL: {url[:80]}...")
            print()
    else:
        print("❌ NO HIGH FIT LINKEDIN JOBS (>= 7)\n")
        
        # Show ALL LinkedIn jobs regardless of FIT
        if linkedin_jobs:
            print(f"📋 ALL LINKEDIN JOBS (any FIT):\n")
            for i, job in enumerate(linkedin_jobs[:10], 1):
                company = job.get('Company', 'Unknown')
                role = job.get('Role', 'Unknown')
                fit = job.get('FitScore', 0)
                status = job.get('Status', '')
                
                print(f"{i}. {company} - {role}")
                print(f"   FIT: {fit}/10 | Status: {status}")
                print()
        else:
            print("❌ NO LINKEDIN JOBS AT ALL\n")
    
    # Show external jobs with high FIT
    high_fit_external = [j for j in external_jobs if j['FitScore'] >= 7]
    
    if high_fit_external:
        print(f"\n⚠️  HIGH FIT EXTERNAL JOBS (>= 7) - Not LinkedIn:\n")
        for i, job in enumerate(high_fit_external[:5], 1):
            company = job.get('Company', 'Unknown')
            role = job.get('Role', 'Unknown')
            fit = job.get('FitScore', 0)
            url = job.get('ApplyURL', '')
            
            print(f"{i}. {company} - {role}")
            print(f"   FIT: {fit}/10")
            print(f"   URL: {url[:80]}...")
            print()
    
    print("="*70)
    print("\n[SUMMARY]")
    print(f"  LinkedIn jobs: {len(linkedin_jobs)}")
    print(f"  LinkedIn high FIT (>=7): {len(high_fit_linkedin)}")
    print(f"  External jobs: {len(external_jobs)}")
    print(f"  External high FIT (>=7): {len(high_fit_external)}")
    print("="*70)

if __name__ == "__main__":
    main()
