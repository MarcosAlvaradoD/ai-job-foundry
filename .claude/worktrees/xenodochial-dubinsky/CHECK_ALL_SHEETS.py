"""
Verificar estado actual de Google Sheets - TODAS las pestanas
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
    print("GOOGLE SHEETS - ESTADO COMPLETO")
    print("="*70 + "\n")
    
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    tabs = ["Jobs", "Registry", "LinkedIn", "Indeed", "Glassdoor"]
    
    total_all_tabs = 0
    
    for tab in tabs:
        try:
            result = manager.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{tab}!A1:Z10000"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f"{tab:15s}: 0 jobs")
                continue
            
            headers = values[0]
            rows = values[1:]
            
            # Count by status
            status_counts = {}
            for row in rows:
                status_idx = headers.index('Status') if 'Status' in headers else -1
                if status_idx >= 0 and len(row) > status_idx:
                    status = row[status_idx] if row[status_idx] else 'Empty'
                    status_counts[status] = status_counts.get(status, 0) + 1
            
            total = len(rows)
            total_all_tabs += total
            
            print(f"{tab:15s}: {total:4d} jobs")
            for status, count in sorted(status_counts.items()):
                print(f"  {status:15s}: {count:4d}")
            print()
            
        except Exception as e:
            print(f"{tab:15s}: ERROR - {e}\n")
    
    print("="*70)
    print(f"TOTAL ACROSS ALL TABS: {total_all_tabs}")
    print("="*70)

if __name__ == "__main__":
    main()
