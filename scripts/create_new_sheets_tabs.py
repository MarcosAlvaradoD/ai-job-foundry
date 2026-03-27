#!/usr/bin/env python3
"""
Create new Google Sheets tabs for Adzuna, Computrabajo, and JobLeads
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load environment
load_dotenv()

SHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get OAuth credentials"""
    token_path = project_root / "data" / "credentials" / "token.json"
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    return creds

def create_tabs():
    """Create new tabs for Adzuna, Computrabajo, and JobLeads"""
    print("\n" + "="*70)
    print("📊 CREATING NEW GOOGLE SHEETS TABS")
    print("="*70)
    
    # Get credentials
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Get existing sheets
    spreadsheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    existing_sheets = {sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])}
    
    print(f"\n✅ Connected to Google Sheets")
    print(f"   Existing tabs: {', '.join(sorted(existing_sheets))}")
    
    # Define new tabs
    new_tabs = ['Adzuna', 'Computrabajo', 'JobLeads']
    
    # Filter out tabs that already exist
    tabs_to_create = [tab for tab in new_tabs if tab not in existing_sheets]
    
    if not tabs_to_create:
        print(f"\n✅ All tabs already exist!")
        return
    
    print(f"\n📋 Creating tabs: {', '.join(tabs_to_create)}")
    
    # Create batch request
    requests = []
    for tab_name in tabs_to_create:
        requests.append({
            'addSheet': {
                'properties': {
                    'title': tab_name,
                    'gridProperties': {
                        'frozenRowCount': 1  # Freeze header row
                    }
                }
            }
        })
    
    # Execute batch request
    body = {'requests': requests}
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body=body
    ).execute()
    
    print(f"\n✅ Created {len(tabs_to_create)} new tabs!")
    
    # Add headers to each new tab
    headers = [
        'CreatedAt', 'Company', 'Role', 'Location', 'RemoteScope',
        'ApplyURL', 'Source', 'RecruiterEmail', 'Currency', 'Comp',
        'Seniority', 'WorkAuthReq', 'Status', 'NextAction', 'Notes',
        'FitScore', 'Why', 'SLA_Date', 'Regio'
    ]
    
    for tab_name in tabs_to_create:
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{tab_name}!A1",
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        print(f"   ✅ Added headers to {tab_name}")
    
    print(f"\n{'='*70}")
    print(f"✅ DONE! New tabs ready for job processing")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    try:
        create_tabs()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
