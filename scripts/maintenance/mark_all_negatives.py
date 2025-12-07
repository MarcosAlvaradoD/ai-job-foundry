#!/usr/bin/env python3
"""
AI JOB FOUNDRY - Mark Negative Status in ALL Tabs
Marca como EXPIRED cualquier status negativo en TODAS las pestañas
"""
import os
import re
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

load_dotenv()

# Negative keywords (expanded)
NEGATIVE_KEYWORDS = [
    # English
    'no longer accepting',
    'position has been filled',
    'not accepting',
    'position filled',
    'no longer considered',
    'applications closed',
    'expired',
    'caduco',
    'caducó',
    'not available',
    'no disponible',
    'este empleo no',
    'payment is too low',
    'salary too low',
    
    # Spanish
    'ya no acepta',
    'posición cerrada',
    'no disponible',
    'este empleo caduco',
    'este trabajo no está',
    'puesto cubierto',
    'aplicaciones cerradas'
]

# User rejection keywords
USER_REJECTION = [
    'payment too low',
    'salary too low',
    'not interested',
    'withdrew',
    'declining'
]


def mark_all_negatives():
    """Mark negative status in ALL tabs"""
    print("\n🚫 Marking negative status in ALL tabs...")
    print("="*70)
    
    # Credentials
    creds = Credentials.from_authorized_user_file(
        'data/credentials/token.json',
        ['https://www.googleapis.com/auth/spreadsheets']
    )
    
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    if not sheet_id:
        print("❌ GOOGLE_SHEETS_ID not found")
        return
    
    spreadsheet = client.open_by_key(sheet_id)
    
    # ALL tabs
    tabs_to_process = ['Jobs', 'LinkedIn', 'Indeed', 'Glassdoor']
    
    total_expired = 0
    total_user_rejected = 0
    
    for tab_name in tabs_to_process:
        try:
            print(f"\n📋 Processing '{tab_name}'...")
            worksheet = spreadsheet.worksheet(tab_name)
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            if len(all_values) < 2:
                print(f"  No data")
                continue
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            print(f"  Found {len(data_rows)} rows")
            
            # Find Status column
            try:
                status_col_idx = headers.index('Status')
            except:
                status_col_idx = 12  # Column M
            
            # Find NextAction column
            try:
                next_col_idx = headers.index('NextAction')
            except:
                next_col_idx = 13  # Column N
            
            expired_count = 0
            rejected_count = 0
            
            for idx, row in enumerate(data_rows, start=2):
                if len(row) <= status_col_idx:
                    continue
                
                status = str(row[status_col_idx]).strip().lower()
                
                if not status or status in ['expired', 'rejected_by_user']:
                    continue
                
                # Check user rejection FIRST
                is_user_rejected = any(keyword in status for keyword in USER_REJECTION)
                
                if is_user_rejected:
                    try:
                        worksheet.update_cell(idx, status_col_idx + 1, 'REJECTED_BY_USER')
                        
                        timestamp = datetime.now().strftime('%Y-%m-%d')
                        note = f"[{timestamp}] User rejected"
                        worksheet.update_cell(idx, next_col_idx + 1, note)
                        
                        print(f"    ✅ Row {idx}: REJECTED_BY_USER")
                        rejected_count += 1
                        total_user_rejected += 1
                    except Exception as e:
                        print(f"    ❌ Row {idx}: {e}")
                    continue
                
                # Check if negative
                is_negative = any(keyword in status for keyword in NEGATIVE_KEYWORDS)
                
                if is_negative:
                    try:
                        worksheet.update_cell(idx, status_col_idx + 1, 'EXPIRED')
                        
                        timestamp = datetime.now().strftime('%Y-%m-%d')
                        note = f"[{timestamp}] Auto-marked: {status[:40]}"
                        worksheet.update_cell(idx, next_col_idx + 1, note)
                        
                        print(f"    ✅ Row {idx}: EXPIRED")
                        expired_count += 1
                        total_expired += 1
                    except Exception as e:
                        print(f"    ❌ Row {idx}: {e}")
            
            if expired_count > 0 or rejected_count > 0:
                print(f"  ✅ {expired_count} EXPIRED, {rejected_count} REJECTED")
            else:
                print(f"  ℹ️  No updates needed")
                
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            continue
    
    print("\n" + "="*70)
    print(f"📊 TOTAL:")
    print(f"   EXPIRED:          {total_expired}")
    print(f"   REJECTED_BY_USER: {total_user_rejected}")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        mark_all_negatives()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
