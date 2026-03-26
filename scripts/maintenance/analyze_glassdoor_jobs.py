#!/usr/bin/env python3
"""
Count valid jobs in Glassdoor tab
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

headers = all_values[0]
data_rows = all_values[1:]

print("\n📊 GLASSDOOR JOB ANALYSIS")
print("="*70)

# Find columns
role_col = headers.index('Role')
fit_col = headers.index('FitScore')
status_col = headers.index('Status')

total = len(data_rows)
has_fit_score = 0
no_fit_score = 0
role_unknown = 0
role_empty = 0
role_valid = 0

print(f"\nTotal jobs: {total}")
print("\nAnalyzing...")

for idx, row in enumerate(data_rows, start=2):
    role = row[role_col] if len(row) > role_col else ''
    fit_score = row[fit_col] if len(row) > fit_col else ''
    
    # Check FIT score
    if fit_score and fit_score.strip() and fit_score != 'Unknown':
        has_fit_score += 1
    else:
        no_fit_score += 1
    
    # Check Role
    if not role or not role.strip():
        role_empty += 1
    elif role.lower() == 'unknown':
        role_unknown += 1
    else:
        role_valid += 1

print("\n" + "="*70)
print("📈 RESULTS:")
print("="*70)
print(f"✅ Jobs WITH FIT score:     {has_fit_score:4d} ({has_fit_score/total*100:.1f}%)")
print(f"❌ Jobs WITHOUT FIT score:  {no_fit_score:4d} ({no_fit_score/total*100:.1f}%)")
print()
print(f"✅ Jobs with VALID Role:    {role_valid:4d} ({role_valid/total*100:.1f}%)")
print(f"❌ Jobs with Role=Unknown:  {role_unknown:4d} ({role_unknown/total*100:.1f}%)")
print(f"❌ Jobs with Role=Empty:    {role_empty:4d} ({role_empty/total*100:.1f}%)")
print("="*70)

# Show first 5 jobs WITHOUT fit score
print("\n📋 First 5 jobs WITHOUT FIT score:")
print("-"*70)
count = 0
for idx, row in enumerate(data_rows, start=2):
    if count >= 5:
        break
    
    fit_score = row[fit_col] if len(row) > fit_col else ''
    
    if not fit_score or not fit_score.strip() or fit_score == 'Unknown':
        role = row[role_col] if len(row) > role_col else ''
        company = row[1] if len(row) > 1 else ''
        status = row[status_col] if len(row) > status_col else ''
        
        print(f"  Row {idx}: {role} at {company}")
        print(f"          FitScore: '{fit_score}' | Status: {status}")
        count += 1

print()
