"""
Quick check de jobs de Glassdoor
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
    print("GLASSDOOR JOBS CHECK - AI JOB FOUNDRY")
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
        
        print(f"Total rows: {len(rows)}")
        print(f"Headers: {headers}\n")
        
        # Find key columns
        try:
            url_idx = headers.index('ApplyURL')
            status_idx = headers.index('Status')
            company_idx = headers.index('Company')
            role_idx = headers.index('Role')
            fit_idx = headers.index('FitScore') if 'FitScore' in headers else None
        except ValueError as e:
            print(f"Error finding columns: {e}")
            print(f"Available headers: {headers}")
            return
        
        # Analyze data
        total_jobs = len(rows)
        with_url = sum(1 for row in rows if len(row) > url_idx and row[url_idx].strip())
        without_url = total_jobs - with_url
        
        # Status breakdown
        status_counts = {}
        for row in rows:
            if len(row) > status_idx:
                status = row[status_idx] if row[status_idx] else "Unknown"
                status_counts[status] = status_counts.get(status, 0) + 1
        
        print("="*70)
        print("GLASSDOOR JOBS SUMMARY")
        print("="*70)
        print(f"Total Jobs: {total_jobs}")
        print(f"With URL: {with_url}")
        print(f"Without URL: {without_url}")
        print(f"\nStatus Breakdown:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        
        # Sample jobs with URLs
        print(f"\n" + "="*70)
        print("SAMPLE JOBS WITH URLs (First 5):")
        print("="*70)
        count = 0
        for row in rows:
            if len(row) > url_idx and row[url_idx].strip():
                company = row[company_idx] if len(row) > company_idx else "?"
                role = row[role_idx] if len(row) > role_idx else "?"
                url = row[url_idx]
                status = row[status_idx] if len(row) > status_idx else "?"
                fit = row[fit_idx] if fit_idx and len(row) > fit_idx else "?"
                
                print(f"\n{count+1}. {company} - {role}")
                print(f"   Status: {status} | FIT: {fit}")
                print(f"   URL: {url[:80]}...")
                
                count += 1
                if count >= 5:
                    break
        
        print(f"\n" + "="*70)
        
    except Exception as e:
        print(f"Error reading Glassdoor tab: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
