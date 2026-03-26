#!/usr/bin/env python3
"""
Clean up expired jobs and apply correct colors to TOP 10 valid offers
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from core.sheets.sheet_manager import SheetManager

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get Google API credentials"""
    creds = None
    base_path = Path(__file__).parent
    token_path = base_path / "data" / "credentials" / "token.json"
    credentials_path = base_path / "data" / "credentials" / "credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def archive_expired_jobs():
    """Archive all expired jobs in Google Sheets"""
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    sheet_manager = SheetManager()
    service = build('sheets', 'v4', credentials=get_credentials())
    
    # Tab mapping with CORRECT sheet IDs
    tab_map = {
        'linkedin': {'name': 'LinkedIn', 'gid': 186301015},
        'indeed': {'name': 'Indeed', 'gid': 1628260752},
        'glassdoor': {'name': 'Glassdoor', 'gid': 1232939118}
    }
    
    requests = []
    archived_count = 0
    
    for tab_key, tab_info in tab_map.items():
        jobs = sheet_manager.get_all_jobs(tab_key)
        
        for job in jobs:
            if job.get('Status', '').lower() == 'expired':
                row_num = job.get('_row')
                # Update status cell to "Archived"
                requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": tab_info['gid'],
                            "startRowIndex": row_num - 1,
                            "endRowIndex": row_num,
                            "startColumnIndex": 20,  # Status column (approximately)
                            "endColumnIndex": 21
                        },
                        "rows": [{
                            "values": [{
                                "userEnteredValue": {"stringValue": "Archived"}
                            }]
                        }],
                        "fields": "userEnteredValue"
                    }
                })
                archived_count += 1
    
    if requests:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    
    print(f"✅ Archived: {archived_count} expired jobs")
    return requests

def apply_top_10_colors():
    """Apply colors to TOP 10 valid LinkedIn jobs with URLs"""
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    sheet_manager = SheetManager()
    service = build('sheets', 'v4', credentials=get_credentials())
    
    # Get LinkedIn jobs with valid URLs and FitScore >= 7
    jobs = sheet_manager.get_all_jobs('linkedin')
    valid_jobs = [j for j in jobs 
                  if (j.get('Status', '').lower() != 'expired' and 
                      j.get('ApplyURL', '').strip() and 
                      j.get('FitScore', '') and 
                      str(j.get('FitScore', '')).replace('.', '').isdigit() and
                      float(j.get('FitScore', '0')) >= 7)]
    
    # Sort by FitScore descending
    valid_jobs.sort(key=lambda x: (float(x.get('FitScore', '0')), x.get('CreatedAt', '')), reverse=True)
    
    # Get TOP 10 row numbers
    top_10_rows = [j.get('_row') for j in valid_jobs[:10]]
    top_3_rows = top_10_rows[:3]
    
    requests = []
    
    # Green for top 3
    for row in top_3_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": 186301015,  # LinkedIn tab - CORRECT ID
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": 0,
                    "endColumnIndex": 25
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.0,
                            "green": 1.0,
                            "blue": 0.0,
                            "alpha": 0.3
                        }
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })
    
    # Yellow for remaining 7
    for row in top_10_rows[3:]:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": 186301015,  # LinkedIn tab - CORRECT ID
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": 0,
                    "endColumnIndex": 25
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 0.0,
                            "alpha": 0.3
                        }
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })
    
    body = {'requests': requests}
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    
    print(f"✅ Colored TOP 10 Offers:")
    print(f"   🟩 Green (Top 3 New): {top_3_rows}")
    print(f"   🟨 Yellow (Top 10): {top_10_rows}")
    
    # Print details
    print("\n📋 TOP 10 Details:")
    for i, row in enumerate(top_10_rows, 1):
        job = [j for j in valid_jobs if j.get('_row') == row][0]
        role = job.get('Role', 'Unknown')[:45]
        fit = job.get('FitScore')
        color = "GREEN" if i <= 3 else "YELLOW"
        print(f"   {i:2}. {color:6} | Row {row:3} | FIT {fit:4} | {role}")

if __name__ == "__main__":
    print("="*70)
    print("🧹 CLEANUP EXPIRED + COLOR TOP 10")
    print("="*70)
    
    archive_expired_jobs()
    apply_top_10_colors()
    
    print("\n✅ Done!")
    print(f"View: https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEETS_ID')}/edit")
