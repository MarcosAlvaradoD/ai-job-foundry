"""
Encuentra el MEJOR job de Glassdoor con Status=New
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "="*70)
    print("GLASSDOOR - BEST NEW JOBS (Status=New)")
    print("="*70 + "\n")
    
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    result = manager.service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Glassdoor!A1:Z1000"
    ).execute()
    
    values = result.get('values', [])
    if not values:
        return
    
    headers = values[0]
    rows = values[1:]
    
    col_map = {header: idx for idx, header in enumerate(headers)}
    
    # Filter only "New" jobs
    new_jobs = []
    for i, row in enumerate(rows, start=2):
        status = row[col_map['Status']] if len(row) > col_map.get('Status', 999) and row[col_map['Status']] else ""
        
        if status == "New":
            fit_str = row[col_map['FitScore']] if len(row) > col_map.get('FitScore', 999) and row[col_map['FitScore']] else "0"
            try:
                fit_score = int(fit_str.split('/')[0]) if '/' in fit_str else int(fit_str)
            except Exception:
                fit_score = 0
            
            new_jobs.append({
                'row_num': i,
                'fit_score': fit_score,
                'data': row
            })
    
    # Sort by FIT
    new_jobs.sort(key=lambda x: x['fit_score'], reverse=True)
    
    print(f"Total NEW jobs: {len(new_jobs)}\n")
    print("="*70)
    print("TOP 10 NEW JOBS BY FIT SCORE")
    print("="*70)
    for i, job in enumerate(new_jobs[:10], 1):
        company = job['data'][col_map['Company']] if len(job['data']) > col_map.get('Company', 999) else "?"
        role = job['data'][col_map['Role']] if len(job['data']) > col_map.get('Role', 999) else "?"
        location = job['data'][col_map['Location']] if len(job['data']) > col_map.get('Location', 999) else "?"
        print(f"{i}. FIT: {job['fit_score']} | {company} - {role}")
        print(f"   Location: {location}")
    
    # Show best NEW job details
    if new_jobs:
        best = new_jobs[0]
        print(f"\n" + "="*70)
        print(f"BEST NEW JOB - FULL DETAILS (Row #{best['row_num']})")
        print("="*70)
        
        for header, idx in sorted(col_map.items(), key=lambda x: x[1]):
            if len(best['data']) > idx and best['data'][idx]:
                value = best['data'][idx]
                if 'URL' in header.upper() and len(value) > 80:
                    value = value[:80] + "..."
                print(f"{header:20s}: {value}")
        
        print("\n" + "="*70)
        print("FULL APPLY URL:")
        print("="*70)
        if len(best['data']) > col_map.get('ApplyURL', 999):
            print(best['data'][col_map['ApplyURL']])

if __name__ == "__main__":
    main()
