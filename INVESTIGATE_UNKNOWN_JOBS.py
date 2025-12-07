"""
Investiga los jobs "Unknown" de Glassdoor
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
    print("GLASSDOOR UNKNOWN JOBS INVESTIGATION")
    print("="*70 + "\n")
    
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    # Read Glassdoor tab
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
    
    # Find "Unknown" jobs
    unknown_jobs = []
    known_jobs = []
    
    for i, row in enumerate(rows, start=2):
        company = row[col_map['Company']] if len(row) > col_map.get('Company', 999) else ""
        role = row[col_map['Role']] if len(row) > col_map.get('Role', 999) else ""
        status = row[col_map['Status']] if len(row) > col_map.get('Status', 999) else ""
        
        if company == "Unknown" or role == "Unknown Role":
            unknown_jobs.append({
                'row': i,
                'data': row,
                'status': status
            })
        elif company and role:
            known_jobs.append({
                'row': i,
                'company': company,
                'role': role,
                'status': status
            })
    
    print(f"Total Glassdoor jobs: {len(rows)}")
    print(f"Unknown jobs: {len(unknown_jobs)} ({len(unknown_jobs)/len(rows)*100:.1f}%)")
    print(f"Known jobs: {len(known_jobs)} ({len(known_jobs)/len(rows)*100:.1f}%)")
    
    # Analyze Unknown jobs
    print(f"\n" + "="*70)
    print("UNKNOWN JOBS ANALYSIS (First 5)")
    print("="*70)
    
    for i, job in enumerate(unknown_jobs[:5], 1):
        print(f"\n{i}. Row #{job['row']} - Status: {job['status']}")
        print("-" * 70)
        
        # Show all available data
        for header, idx in sorted(col_map.items(), key=lambda x: x[1]):
            if len(job['data']) > idx and job['data'][idx]:
                value = job['data'][idx]
                if len(value) > 80:
                    value = value[:80] + "..."
                print(f"  {header:20s}: {value}")
    
    # Analyze Known jobs with Status=New
    print(f"\n" + "="*70)
    print("KNOWN JOBS WITH STATUS=NEW (First 10)")
    print("="*70)
    
    new_known = [j for j in known_jobs if j['status'] == 'New']
    print(f"\nFound {len(new_known)} known jobs with Status=New\n")
    
    for i, job in enumerate(new_known[:10], 1):
        print(f"{i}. {job['company']} - {job['role'][:50]}")
        print(f"   Status: {job['status']}")
    
    # Status breakdown
    print(f"\n" + "="*70)
    print("STATUS BREAKDOWN")
    print("="*70)
    
    status_counts = {}
    for job in unknown_jobs:
        s = job['status'] if job['status'] else 'Empty'
        status_counts[s] = status_counts.get(s, 0) + 1
    
    print("\nUnknown Jobs:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    status_counts_known = {}
    for job in known_jobs:
        s = job['status'] if job['status'] else 'Empty'
        status_counts_known[s] = status_counts_known.get(s, 0) + 1
    
    print("\nKnown Jobs:")
    for status, count in sorted(status_counts_known.items()):
        print(f"  {status}: {count}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
