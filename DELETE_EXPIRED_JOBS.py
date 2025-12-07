"""
DELETE ALL EXPIRED JOBS - Elimina filas expiradas de Google Sheets
"""
import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

def delete_expired_jobs(tab_name, dry_run=True):
    """
    Elimina jobs con Status=EXPIRED de una pestana
    """
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    # Get all data
    result = manager.service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1:Z10000"
    ).execute()
    
    values = result.get('values', [])
    if not values:
        return 0
    
    headers = values[0]
    rows = values[1:]
    
    # Find Status column
    if 'Status' not in headers:
        print(f"  [SKIP] No Status column found")
        return 0
    
    status_idx = headers.index('Status')
    
    # Find rows to delete (from bottom to top to avoid index issues)
    rows_to_delete = []
    for i, row in enumerate(rows, start=2):  # Row 1 is headers, data starts at 2
        if len(row) > status_idx and row[status_idx] == 'EXPIRED':
            rows_to_delete.append(i)
    
    if not rows_to_delete:
        print(f"  No EXPIRED jobs found")
        return 0
    
    print(f"  Found {len(rows_to_delete)} EXPIRED jobs to delete")
    
    if dry_run:
        print(f"  [DRY RUN] Would delete rows: {rows_to_delete[:5]}... (first 5)")
        return len(rows_to_delete)
    
    # Delete rows (from bottom to top)
    rows_to_delete.sort(reverse=True)
    
    # Get sheet ID
    sheet_metadata = manager.service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()
    
    sheet_id = None
    for sheet in sheet_metadata.get('sheets', []):
        if sheet['properties']['title'] == tab_name:
            sheet_id = sheet['properties']['sheetId']
            break
    
    if not sheet_id:
        print(f"  [ERROR] Could not find sheet ID for {tab_name}")
        return 0
    
    # Batch delete requests
    requests = []
    for row_num in rows_to_delete:
        requests.append({
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': row_num - 1,  # 0-indexed
                    'endIndex': row_num
                }
            }
        })
    
    # Execute batch delete
    manager.service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()
    
    print(f"  [SUCCESS] Deleted {len(rows_to_delete)} EXPIRED jobs")
    return len(rows_to_delete)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Actually delete (default is dry run)')
    args = parser.parse_args()
    
    dry_run = not args.live
    
    print("\n" + "="*70)
    if dry_run:
        print("DRY RUN - DELETE EXPIRED JOBS (no changes will be made)")
    else:
        print("LIVE MODE - DELETING EXPIRED JOBS")
    print("="*70 + "\n")
    
    tabs = ["Jobs", "Registry", "LinkedIn", "Indeed", "Glassdoor"]
    
    total_deleted = 0
    
    for tab in tabs:
        print(f"Processing: {tab}")
        try:
            deleted = delete_expired_jobs(tab, dry_run=dry_run)
            total_deleted += deleted
            print()
        except Exception as e:
            print(f"  [ERROR] {e}\n")
    
    print("="*70)
    if dry_run:
        print(f"TOTAL EXPIRED FOUND: {total_deleted}")
        print("\nTo actually delete, run:")
        print("  py DELETE_EXPIRED_JOBS.py --live")
    else:
        print(f"TOTAL DELETED: {total_deleted}")
        print("\n[SUCCESS] All EXPIRED jobs have been removed!")
    print("="*70)

if __name__ == "__main__":
    main()
