"""
Agrega columna SourceType a Google Sheets para tracking
"""
import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

def add_source_type_column():
    """
    Agrega columna SourceType despues de Source
    Valores posibles:
    - "Email Individual" - Email directo de recruiter
    - "Bulletin" - Boletin con multiples jobs
    - "Scraping" - LinkedIn/Indeed scraper
    """
    print("\n" + "="*70)
    print("ADDING SOURCE TYPE COLUMN")
    print("="*70 + "\n")
    
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    tabs = ["Jobs", "LinkedIn", "Indeed", "Glassdoor"]
    
    for tab in tabs:
        print(f"Processing tab: {tab}")
        
        try:
            # Get current headers
            result = manager.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{tab}!A1:Z1"
            ).execute()
            
            headers = result.get('values', [[]])[0]
            
            if 'SourceType' in headers:
                print(f"  [SKIP] SourceType already exists\n")
                continue
            
            # Find Source column
            if 'Source' not in headers:
                print(f"  [ERROR] Source column not found\n")
                continue
            
            source_idx = headers.index('Source')
            insert_idx = source_idx + 1
            
            # Insert column letter (convert index to letter)
            insert_col = chr(65 + insert_idx)  # A=0, B=1, etc
            
            print(f"  Source at column {chr(65 + source_idx)}")
            print(f"  Inserting SourceType at column {insert_col}")
            
            # Insert blank column
            request = {
                'insertDimension': {
                    'range': {
                        'sheetId': manager._get_sheet_id(tab),
                        'dimension': 'COLUMNS',
                        'startIndex': insert_idx,
                        'endIndex': insert_idx + 1
                    }
                }
            }
            
            manager.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
            # Set header name
            manager.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{tab}!{insert_col}1",
                valueInputOption='RAW',
                body={'values': [['SourceType']]}
            ).execute()
            
            print(f"  [SUCCESS] SourceType column added\n")
            
        except Exception as e:
            print(f"  [ERROR] {e}\n")
    
    print("="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Update email processors to set SourceType:")
    print("   - Individual emails: 'Email Individual'")
    print("   - Bulletins: 'Bulletin'")
    print("2. Update scrapers to set SourceType:")
    print("   - LinkedIn: 'Scraping - LinkedIn'")
    print("   - Indeed: 'Scraping - Indeed'")
    print("3. This will help you track where each job came from")

if __name__ == "__main__":
    try:
        manager = SheetManager()
        # Helper to get sheet ID
        def get_sheet_id(tab_name):
            sheet_metadata = manager.service.spreadsheets().get(
                spreadsheetId=os.getenv("GOOGLE_SHEETS_ID")
            ).execute()
            for sheet in sheet_metadata.get('sheets', []):
                if sheet['properties']['title'] == tab_name:
                    return sheet['properties']['sheetId']
            return None
        
        manager._get_sheet_id = get_sheet_id
        add_source_type_column()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
