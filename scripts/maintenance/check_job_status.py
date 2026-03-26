#!/usr/bin/env python3
"""
Comprehensive job status checker across ALL tabs
Shows FIT scores, sources, and eligibility for auto-apply
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

def check_all_jobs():
    """Check status of all jobs across all tabs"""
    print("\n📊 COMPREHENSIVE JOB STATUS CHECK")
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
    
    all_worksheets = spreadsheet.worksheets()
    
    total_jobs = 0
    total_with_fit = 0
    total_fit_7_plus = 0
    total_linkedin = 0
    total_linkedin_easy_apply = 0
    
    tab_summary = []
    
    for worksheet in all_worksheets:
        tab_name = worksheet.title
        
        # Skip config tabs
        if tab_name.lower() in ['config', 'settings', 'dashboard', 'summary', 'resumen', 'registry']:
            continue
        
        try:
            all_values = worksheet.get_all_values()
            
            if len(all_values) < 2:
                continue
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            # Find columns
            try:
                source_col = headers.index('Source')
            except:
                source_col = 6
            
            try:
                fit_col = headers.index('FitScore')
            except:
                fit_col = 15
            
            try:
                status_col = headers.index('Status')
            except:
                status_col = 12
            
            # Count stats
            tab_total = len(data_rows)
            tab_with_fit = 0
            tab_fit_7_plus = 0
            tab_linkedin = 0
            tab_easy_apply = 0
            
            for row in data_rows:
                source = row[source_col] if len(row) > source_col else ''
                fit_score = row[fit_col] if len(row) > fit_col else ''
                status = row[status_col] if len(row) > status_col else ''
                
                # Count with FIT score
                if fit_score and fit_score.strip() and fit_score != 'Unknown':
                    tab_with_fit += 1
                    
                    # Extract numeric FIT score
                    try:
                        fit_num = float(fit_score.split('/')[0])
                        if fit_num >= 7:
                            tab_fit_7_plus += 1
                    except:
                        pass
                
                # Count LinkedIn
                if 'linkedin' in source.lower():
                    tab_linkedin += 1
                    
                    # Check if Easy Apply (would need to check ApplyURL)
                    # For now, assume all LinkedIn could be Easy Apply
                    if status != 'Applied':
                        tab_easy_apply += 1
            
            if tab_total > 0:
                tab_summary.append({
                    'tab': tab_name,
                    'total': tab_total,
                    'with_fit': tab_with_fit,
                    'fit_7_plus': tab_fit_7_plus,
                    'linkedin': tab_linkedin,
                    'easy_apply': tab_easy_apply
                })
                
                total_jobs += tab_total
                total_with_fit += tab_with_fit
                total_fit_7_plus += tab_fit_7_plus
                total_linkedin += tab_linkedin
                total_linkedin_easy_apply += tab_easy_apply
                
        except Exception as e:
            print(f"  ❌ Error in {tab_name}: {e}")
            continue
    
    # Print summary
    print("\n📋 BY TAB:")
    print("-"*70)
    for tab in tab_summary:
        print(f"  {tab['tab']:15s} | {tab['total']:4d} jobs | "
              f"{tab['with_fit']:4d} scored | "
              f"{tab['fit_7_plus']:2d} FIT≥7 | "
              f"{tab['linkedin']:2d} LinkedIn")
    
    print("\n" + "="*70)
    print("📈 TOTALS:")
    print("="*70)
    print(f"  Total jobs:                {total_jobs:4d}")
    print(f"  Jobs WITH FIT score:       {total_with_fit:4d} ({total_with_fit/total_jobs*100:.1f}%)")
    print(f"  Jobs WITHOUT FIT score:    {total_jobs - total_with_fit:4d}")
    print(f"  Jobs with FIT >= 7:        {total_fit_7_plus:4d}")
    print(f"  LinkedIn jobs:             {total_linkedin:4d}")
    print(f"  LinkedIn Easy Apply ready: {total_linkedin_easy_apply:4d}")
    print("="*70)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-"*70)
    
    if total_jobs - total_with_fit > 0:
        print(f"  ⚠️  {total_jobs - total_with_fit} jobs need FIT scores calculated")
        print("     Run: py scripts\\maintenance\\calculate_all_fit_scores_v2.py")
    
    if total_fit_7_plus == 0:
        print("  ⚠️  No jobs with FIT >= 7 for auto-apply")
        print("     Options:")
        print("     1. Run LinkedIn scraper to find new jobs")
        print("     2. Lower FIT threshold (not recommended)")
        print("     3. Wait for better job matches")
    elif total_linkedin_easy_apply == 0:
        print("  ⚠️  Jobs with FIT >= 7 exist but none are LinkedIn Easy Apply")
        print("     Manual application required for these jobs")
    else:
        print(f"  ✅ {total_linkedin_easy_apply} LinkedIn Easy Apply jobs ready!")
        print("     Run: py run_daily_pipeline.py --apply --dry-run")
    
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        check_all_jobs()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
