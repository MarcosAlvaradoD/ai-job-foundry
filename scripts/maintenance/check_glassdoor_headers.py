#!/usr/bin/env python3
"""
Quick script to check Glassdoor tab headers
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

base_path = Path(__file__).parent.parent.parent
token_path = base_path / "data" / "credentials" / "token.json"

creds = Credentials.from_authorized_user_file(
    str(token_path),
    ['https://www.googleapis.com/auth/spreadsheets']
)

client = gspread.authorize(creds)
sheet_id = os.getenv('GOOGLE_SHEETS_ID')
spreadsheet = client.open_by_key(sheet_id)

# Check Glassdoor tab
worksheet = spreadsheet.worksheet('Glassdoor')
all_values = worksheet.get_all_values()

print("\n📋 GLASSDOOR HEADERS:")
print("="*70)
headers = all_values[0]
for idx, header in enumerate(headers):
    print(f"  Column {chr(65+idx)} ({idx}): '{header}'")

print("\n📊 Sample row (row 2):")
if len(all_values) > 1:
    row2 = all_values[1]
    for idx, value in enumerate(row2[:20]):  # First 20 columns
        if value:
            print(f"  {headers[idx]}: {value}")

print("\n" + "="*70)
