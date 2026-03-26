#!/usr/bin/env python3
"""
Update Google Sheets colors for job offers
- Top 10 high FitScore: Yellow background
- Top 3 new offers: Green background
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

def get_credentials():
    """Get Google API credentials"""
    creds = None
    base_path = Path(__file__).parent  # ai-job-foundry directory
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

def update_sheet_colors():
    """Update colors in Google Sheets"""
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")

    if not spreadsheet_id:
        print("❌ GOOGLE_SHEETS_ID not found in .env")
        return
    
    print(f"Spreadsheet ID: {spreadsheet_id}")
    
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    top_10_rows = [6,7,8,9,181,182,183,184,185,186]  # 1-based rows

    # Top 3 new offers (green) - rows 6,7,8
    top_3_rows = [6,7,8]

    requests = []

    # First, set all top 10 to yellow
    for row in top_10_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": 0,  # LinkedIn tab (first tab)
                    "startRowIndex": row-1,  # 0-based
                    "endRowIndex": row,     # exclusive
                    "startColumnIndex": 0,
                    "endColumnIndex": 20    # All columns
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 0.0
                        }
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })

    # Then override top 3 to green
    for row in top_3_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": row-1,
                    "endRowIndex": row,
                    "startColumnIndex": 0,
                    "endColumnIndex": 20
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.0,
                            "green": 1.0,
                            "blue": 0.0
                        }
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })

    # Execute the batch update
    body = {
        'requests': requests
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

    print("✅ Colors updated successfully!")
    print(f"Updated {len(requests)} cell ranges")

if __name__ == "__main__":
    update_sheet_colors()