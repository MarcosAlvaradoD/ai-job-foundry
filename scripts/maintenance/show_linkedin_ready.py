#!/usr/bin/env python3
"""
Show LinkedIn jobs with FIT >= 7 that should be eligible for auto-apply
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ✅ FIX: Windows UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

def show_linkedin_jobs():
    """Show LinkedIn jobs with FIT >= 7"""
    print("\n🔍 LINKEDIN JOBS WITH FIT ≥ 7")
    print("="*70)
    
    # Get credentials
    base_path = Path(__file__).parent.parent.parent
    token_path = base_path / "data" / "credentials" / "token.json"
    
    creds = Credentials.from_authorized_user_file(
        str(token_path),
        ['https://www.googleapis.com/auth/spreadsheets']
    )
    
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    spreadsheet = client.open_by_key(sheet_id)
    
    # Get LinkedIn tab
    try:
        worksheet = spreadsheet.worksheet('LinkedIn')
    except Exception:
        print("❌ LinkedIn tab not found")
        return
    
    all_values = worksheet.get_all_values()
    headers = all_values[0]
    data_rows = all_values[1:]
    
    # Find columns
    try:
        role_col = headers.index('Role')
    except Exception:
        role_col = 2
    
    try:
        company_col = headers.index('Company')
    except Exception:
        company_col = 1
    
    try:
        url_col = headers.index('ApplyURL')
    except Exception:
        url_col = 5
    
    try:
        fit_col = headers.index('FitScore')
    except Exception:
        fit_col = 15
    
    try:
        status_col = headers.index('Status')
    except Exception:
        status_col = 12
    
    try:
        source_col = headers.index('Source')
    except Exception:
        source_col = 6
    
    # Find jobs with FIT >= 7
    eligible_jobs = []
    
    for idx, row in enumerate(data_rows, start=2):
        fit_score = row[fit_col] if len(row) > fit_col else ''
        status = row[status_col] if len(row) > status_col else ''
        
        if not fit_score or fit_score == 'Unknown':
            continue
        
        try:
            fit_num = float(fit_score.split('/')[0])
            
            if fit_num >= 7:
                role = row[role_col] if len(row) > role_col else ''
                company = row[company_col] if len(row) > company_col else ''
                url = row[url_col] if len(row) > url_col else ''
                source = row[source_col] if len(row) > source_col else ''
                
                # Check if Easy Apply
                is_easy_apply = 'easyApply' in url.lower() or '/easy-apply/' in url.lower()
                
                eligible_jobs.append({
                    'row': idx,
                    'role': role,
                    'company': company,
                    'fit': fit_num,
                    'status': status,
                    'url': url[:80] + '...' if len(url) > 80 else url,
                    'easy_apply': is_easy_apply,
                    'source': source
                })
        except Exception:
            continue
    
    # Print results
    if not eligible_jobs:
        print("❌ No LinkedIn jobs with FIT >= 7 found")
        return
    
    print(f"\n📊 Found {len(eligible_jobs)} LinkedIn jobs with FIT ≥ 7\n")
    
    for job in eligible_jobs:
        emoji = "🔥" if job['fit'] >= 8 else "✅"
        easy_emoji = "⚡" if job['easy_apply'] else "⚠️"
        
        print(f"{emoji} Row {job['row']}: {job['role']}")
        print(f"   Company:    {job['company']}")
        print(f"   FIT Score:  {job['fit']}/10")
        print(f"   Status:     {job['status']}")
        print(f"   Easy Apply: {easy_emoji} {'YES' if job['easy_apply'] else 'NO (needs check)'}")
        print(f"   URL:        {job['url']}")
        print()
    
    # Summary
    easy_apply_count = sum(1 for j in eligible_jobs if j['easy_apply'])
    needs_check = len(eligible_jobs) - easy_apply_count
    not_applied = sum(1 for j in eligible_jobs if j['status'] != 'Applied')
    
    print("="*70)
    print("📈 SUMMARY:")
    print("-"*70)
    print(f"  Total LinkedIn FIT≥7:     {len(eligible_jobs)}")
    print(f"  Confirmed Easy Apply:     {easy_apply_count}")
    print(f"  Needs URL check:          {needs_check}")
    print(f"  Not yet applied:          {not_applied}")
    print("="*70)
    
    if easy_apply_count > 0:
        print(f"\n✅ {easy_apply_count} jobs confirmed for auto-apply!")
        print("   Run: py run_daily_pipeline.py --apply --dry-run")
    elif needs_check > 0:
        print(f"\n⚠️  {needs_check} jobs need URL verification")
        print("   The URLs might be Easy Apply but need checking")
    
    print()


if __name__ == '__main__':
    try:
        show_linkedin_jobs()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
