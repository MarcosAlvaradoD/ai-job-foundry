"""
Encuentra el job de Glassdoor con el FIT score mas alto
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "="*70)
    print("GLASSDOOR - BEST FIT JOBS FINDER")
    print("="*70 + "\n")
    
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    # Read Glassdoor tab
    try:
        result = manager.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Glassdoor!A1:Z1000"
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("No data found in Glassdoor tab")
            return
        
        headers = values[0]
        rows = values[1:]
        
        print(f"Total rows: {len(rows)}\n")
        
        # Find all column indices
        col_map = {header: idx for idx, header in enumerate(headers)}
        
        # Parse and sort jobs by FIT score
        jobs_with_fit = []
        for i, row in enumerate(rows, start=2):  # Start at 2 (row 1 is headers)
            if len(row) > col_map.get('FitScore', 999):
                fit_str = row[col_map['FitScore']] if row[col_map['FitScore']] else "0"
                try:
                    fit_score = int(fit_str.split('/')[0]) if '/' in fit_str else int(fit_str)
                except:
                    fit_score = 0
                
                status = row[col_map['Status']] if len(row) > col_map.get('Status', 999) and row[col_map['Status']] else "Unknown"
                
                jobs_with_fit.append({
                    'row_num': i,
                    'fit_score': fit_score,
                    'status': status,
                    'data': row
                })
        
        # Sort by FIT score descending
        jobs_with_fit.sort(key=lambda x: x['fit_score'], reverse=True)
        
        # Show top 10
        print("="*70)
        print("TOP 10 GLASSDOOR JOBS BY FIT SCORE")
        print("="*70)
        for i, job in enumerate(jobs_with_fit[:10], 1):
            company = job['data'][col_map['Company']] if len(job['data']) > col_map.get('Company', 999) else "?"
            role = job['data'][col_map['Role']] if len(job['data']) > col_map.get('Role', 999) else "?"
            print(f"{i}. FIT: {job['fit_score']} | Status: {job['status']} | {company} - {role}")
        
        # Show DETAILED info of #1
        if jobs_with_fit:
            best_job = jobs_with_fit[0]
            print(f"\n" + "="*70)
            print(f"BEST JOB DETAILS (Row #{best_job['row_num']})")
            print("="*70)
            
            for header, idx in sorted(col_map.items(), key=lambda x: x[1]):
                if len(best_job['data']) > idx and best_job['data'][idx]:
                    value = best_job['data'][idx]
                    # Truncate long URLs
                    if 'URL' in header.upper() and len(value) > 80:
                        value = value[:80] + "..."
                    print(f"{header:20s}: {value}")
            
            print("\n" + "="*70)
            print("FULL URL FOR TESTING:")
            print("="*70)
            if len(best_job['data']) > col_map.get('ApplyURL', 999):
                print(best_job['data'][col_map['ApplyURL']])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
