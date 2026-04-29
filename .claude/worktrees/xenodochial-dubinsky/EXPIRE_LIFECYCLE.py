"""
EXPIRE LIFECYCLE MANAGER - Sistema de dos pasos para jobs expirados

PASO 1: Marca jobs como EXPIRED (primera vez que se detecta)
PASO 2: Borra jobs que YA están marcados como EXPIRED (segunda vez)

Uso:
  py EXPIRE_LIFECYCLE.py --mark     # Marca nuevos expired
  py EXPIRE_LIFECYCLE.py --delete   # Borra los ya marcados
  py EXPIRE_LIFECYCLE.py --full     # Marca Y borra en una ejecución
"""
import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class ExpireLifecycleManager:
    def __init__(self):
        self.manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.tabs = ["Jobs", "Registry", "LinkedIn", "Indeed", "Glassdoor"]
    
    def mark_expired_by_date(self, days_threshold=30, dry_run=False):
        """
        PASO 1: Marca jobs como EXPIRED si tienen más de X días
        """
        print("\n" + "="*70)
        print(f"📅 MARKING EXPIRED JOBS (>{days_threshold} days old)")
        print("="*70)
        print(f"Dry run: {dry_run}")
        print("="*70 + "\n")
        
        total_marked = 0
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        for tab in self.tabs:
            print(f"Processing: {tab}")
            try:
                # Get all data
                result = self.manager.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{tab}!A1:Z10000"
                ).execute()
                
                values = result.get('values', [])
                if not values:
                    print(f"  No data\n")
                    continue
                
                headers = values[0]
                rows = values[1:]
                
                # Find columns
                if 'CreatedAt' not in headers or 'Status' not in headers:
                    print(f"  [SKIP] Missing CreatedAt or Status column\n")
                    continue
                
                created_idx = headers.index('CreatedAt')
                status_idx = headers.index('Status')
                company_idx = headers.index('Company') if 'Company' in headers else -1
                role_idx = headers.index('Role') if 'Role' in headers else -1
                
                # Get sheet ID for batch update
                sheet_metadata = self.manager.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                
                sheet_id = None
                for sheet in sheet_metadata.get('sheets', []):
                    if sheet['properties']['title'] == tab:
                        sheet_id = sheet['properties']['sheetId']
                        break
                
                # Find jobs to mark
                jobs_to_mark = []
                for i, row in enumerate(rows, start=2):
                    # Skip if already expired
                    if len(row) > status_idx and row[status_idx] == 'EXPIRED':
                        continue
                    
                    # Check date
                    if len(row) > created_idx and row[created_idx]:
                        try:
                            # Parse date
                            date_str = row[created_idx]
                            # Try different formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %I:%M:%S %p', '%Y-%m-%d']:
                                try:
                                    created_date = datetime.strptime(date_str.split('.')[0], fmt)
                                    break
                                except Exception:
                                    continue
                            else:
                                continue
                            
                            # Check if old enough
                            if created_date < cutoff_date:
                                company = row[company_idx] if company_idx >= 0 and len(row) > company_idx else "Unknown"
                                role = row[role_idx] if role_idx >= 0 and len(row) > role_idx else "Unknown"
                                age_days = (datetime.now() - created_date).days
                                
                                jobs_to_mark.append({
                                    'row': i,
                                    'company': company,
                                    'role': role,
                                    'age_days': age_days
                                })
                        except Exception as e:
                            continue
                
                if not jobs_to_mark:
                    print(f"  No expired jobs found\n")
                    continue
                
                print(f"  Found {len(jobs_to_mark)} jobs to mark:")
                for job in jobs_to_mark[:3]:
                    print(f"    - {job['company'][:30]:30s} | {job['role'][:30]:30s} | {job['age_days']} days")
                if len(jobs_to_mark) > 3:
                    print(f"    ... and {len(jobs_to_mark) - 3} more")
                
                if not dry_run:
                    # Batch update
                    status_col = chr(65 + status_idx)
                    for job in jobs_to_mark:
                        cell = f"{tab}!{status_col}{job['row']}"
                        self.manager.service.spreadsheets().values().update(
                            spreadsheetId=self.spreadsheet_id,
                            range=cell,
                            valueInputOption='RAW',
                            body={'values': [['EXPIRED']]}
                        ).execute()
                    
                    print(f"  ✅ Marked {len(jobs_to_mark)} jobs as EXPIRED")
                else:
                    print(f"  [DRY RUN] Would mark {len(jobs_to_mark)} jobs")
                
                total_marked += len(jobs_to_mark)
                print()
                
            except Exception as e:
                print(f"  [ERROR] {e}\n")
        
        print("="*70)
        print(f"TOTAL MARKED: {total_marked}")
        print("="*70 + "\n")
        
        return total_marked
    
    def delete_expired_jobs(self, dry_run=False):
        """
        PASO 2: Borra jobs que YA están marcados como EXPIRED
        """
        print("\n" + "="*70)
        print("🗑️  DELETING EXPIRED JOBS")
        print("="*70)
        print(f"Dry run: {dry_run}")
        print("="*70 + "\n")
        
        total_deleted = 0
        
        for tab in self.tabs:
            print(f"Processing: {tab}")
            try:
                # Get all data
                result = self.manager.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{tab}!A1:Z10000"
                ).execute()
                
                values = result.get('values', [])
                if not values:
                    print(f"  No data\n")
                    continue
                
                headers = values[0]
                rows = values[1:]
                
                # Find Status column
                if 'Status' not in headers:
                    print(f"  [SKIP] No Status column\n")
                    continue
                
                status_idx = headers.index('Status')
                
                # Find EXPIRED jobs (from bottom to top)
                rows_to_delete = []
                for i, row in enumerate(rows, start=2):
                    if len(row) > status_idx and row[status_idx] == 'EXPIRED':
                        rows_to_delete.append(i)
                
                if not rows_to_delete:
                    print(f"  No EXPIRED jobs found\n")
                    continue
                
                print(f"  Found {len(rows_to_delete)} EXPIRED jobs to delete")
                
                if dry_run:
                    print(f"  [DRY RUN] Would delete rows: {rows_to_delete[:5]}...")
                else:
                    # Get sheet ID
                    sheet_metadata = self.manager.service.spreadsheets().get(
                        spreadsheetId=self.spreadsheet_id
                    ).execute()
                    
                    sheet_id = None
                    for sheet in sheet_metadata.get('sheets', []):
                        if sheet['properties']['title'] == tab:
                            sheet_id = sheet['properties']['sheetId']
                            break
                    
                    if not sheet_id:
                        print(f"  [ERROR] Could not find sheet ID\n")
                        continue
                    
                    # Delete rows (from bottom to top)
                    rows_to_delete.sort(reverse=True)
                    
                    requests = []
                    for row_num in rows_to_delete:
                        requests.append({
                            'deleteDimension': {
                                'range': {
                                    'sheetId': sheet_id,
                                    'dimension': 'ROWS',
                                    'startIndex': row_num - 1,
                                    'endIndex': row_num
                                }
                            }
                        })
                    
                    # Execute batch delete
                    self.manager.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body={'requests': requests}
                    ).execute()
                    
                    print(f"  ✅ Deleted {len(rows_to_delete)} jobs")
                
                total_deleted += len(rows_to_delete)
                print()
                
            except Exception as e:
                print(f"  [ERROR] {e}\n")
        
        print("="*70)
        print(f"TOTAL DELETED: {total_deleted}")
        print("="*70 + "\n")
        
        return total_deleted

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mark', action='store_true', help='Mark expired jobs (PASO 1)')
    parser.add_argument('--delete', action='store_true', help='Delete EXPIRED jobs (PASO 2)')
    parser.add_argument('--full', action='store_true', help='Mark AND delete (both steps)')
    parser.add_argument('--days', type=int, default=30, help='Days threshold for expiration')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')
    args = parser.parse_args()
    
    manager = ExpireLifecycleManager()
    
    if not (args.mark or args.delete or args.full):
        print("\n❌ Error: Must specify --mark, --delete, or --full")
        print("\nUsage:")
        print("  py EXPIRE_LIFECYCLE.py --mark            # Marca jobs expirados (>30 días)")
        print("  py EXPIRE_LIFECYCLE.py --delete          # Borra jobs YA marcados como EXPIRED")
        print("  py EXPIRE_LIFECYCLE.py --full            # Hace ambos pasos")
        print("  py EXPIRE_LIFECYCLE.py --mark --days 60  # Marca jobs >60 días")
        print("  py EXPIRE_LIFECYCLE.py --delete --dry-run # Ver qué se borraría")
        print()
        return
    
    if args.mark or args.full:
        print("\n" + "="*70)
        print("PASO 1: MARCAR EXPIRED")
        print("="*70)
        manager.mark_expired_by_date(days_threshold=args.days, dry_run=args.dry_run)
    
    if args.delete or args.full:
        print("\n" + "="*70)
        print("PASO 2: BORRAR EXPIRED")
        print("="*70)
        manager.delete_expired_jobs(dry_run=args.dry_run)
    
    print("\n" + "="*70)
    print("✅ LIFECYCLE COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
