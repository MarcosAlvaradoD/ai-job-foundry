#!/usr/bin/env python3
"""
AI JOB FOUNDRY - Mark Expired Jobs (FIXED - handles duplicate headers)
Marca como EXPIRED los trabajos con "No longer accepting applications"
"""
import os
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

load_dotenv()

def mark_expired_jobs():
    """Mark jobs as EXPIRED based on status column"""
    print("\n🚫 Marking expired jobs...")
    print("="*70)
    
    # Get credentials
    creds = Credentials.from_authorized_user_file(
        'data/credentials/token.json',
        ['https://www.googleapis.com/auth/spreadsheets']
    )
    
    # Connect to sheet
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    if not sheet_id:
        print("❌ GOOGLE_SHEETS_ID not found in .env")
        return
    
    spreadsheet = client.open_by_key(sheet_id)
    
    # Process each tab
    tabs_to_check = ['Jobs', 'LinkedIn', 'Indeed', 'Glassdoor']
    
    total_expired = 0
    total_user_rejected = 0
    
    for tab_name in tabs_to_check:
        try:
            print(f"\n📋 Checking '{tab_name}' tab...")
            worksheet = spreadsheet.worksheet(tab_name)
            
            # Get all values (raw)
            all_values = worksheet.get_all_values()
            
            if len(all_values) < 2:
                print(f"  No data in {tab_name}")
                continue
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            print(f"  Found {len(data_rows)} rows")
            
            # Find Status column (M = index 12)
            try:
                status_col_idx = headers.index('Status')
            except ValueError:
                # Fallback to column M (index 12)
                status_col_idx = 12
                print(f"  Using column M (index 12) for Status")
            
            # Find NextAction column (N = index 13)
            try:
                next_action_col_idx = headers.index('NextAction')
            except ValueError:
                next_action_col_idx = 13
                print(f"  Using column N (index 13) for NextAction")
            
            expired_count = 0
            user_rejected_count = 0
            
            # Check each row
            for idx, row in enumerate(data_rows, start=2):  # Start at row 2 (after header)
                if len(row) <= status_col_idx:
                    continue
                
                status = str(row[status_col_idx]).strip()
                
                if not status:
                    continue
                
                status_lower = status.lower()
                
                # Keywords for expired/closed positions
                expired_keywords = [
                    'no longer accepting applications',
                    'position has been filled',
                    'no longer accepting',
                    'not accepting applications',
                    'position filled',
                    'no longer considered',
                    'applications closed'
                ]
                
                # Keywords for user rejection (salary, conditions, etc)
                user_rejection_keywords = [
                    'payment is too low',
                    'salary too low',
                    'too low payment',
                    'not interested',
                    'withdrew application',
                    'declining offer'
                ]
                
                # Check user rejection FIRST
                is_user_rejected = any(keyword in status_lower for keyword in user_rejection_keywords)
                
                if is_user_rejected and status != 'REJECTED_BY_USER':
                    try:
                        # Update Status column
                        worksheet.update_cell(idx, status_col_idx + 1, 'REJECTED_BY_USER')
                        
                        # Add note in NextAction column
                        timestamp = datetime.now().strftime('%Y-%m-%d')
                        note = f"[{timestamp}] User rejected: {status[:50]}"
                        worksheet.update_cell(idx, next_action_col_idx + 1, note)
                        
                        print(f"    ✅ Row {idx}: Marked REJECTED_BY_USER")
                        user_rejected_count += 1
                        total_user_rejected += 1
                        
                    except Exception as e:
                        print(f"    ❌ Row {idx}: Error - {e}")
                    continue
                
                # Check if expired
                is_expired = any(keyword in status_lower for keyword in expired_keywords)
                
                if is_expired and status != 'EXPIRED':
                    try:
                        # Update Status column
                        worksheet.update_cell(idx, status_col_idx + 1, 'EXPIRED')
                        
                        # Add note in NextAction column
                        timestamp = datetime.now().strftime('%Y-%m-%d')
                        note = f"[{timestamp}] Auto-marked: {status[:50]}"
                        worksheet.update_cell(idx, next_action_col_idx + 1, note)
                        
                        print(f"    ✅ Row {idx}: Marked EXPIRED")
                        expired_count += 1
                        total_expired += 1
                        
                    except Exception as e:
                        print(f"    ❌ Row {idx}: Error - {e}")
            
            if expired_count > 0 or user_rejected_count > 0:
                print(f"  ✅ {expired_count} EXPIRED, {user_rejected_count} REJECTED_BY_USER in {tab_name}")
            else:
                print(f"  ℹ️  No updates needed in {tab_name}")
            
        except Exception as e:
            print(f"  ⚠️  Error processing {tab_name}: {e}")
            continue
    
    print("\n" + "="*70)
    print(f"📊 SUMMARY:")
    print(f"   EXPIRED (company closed):      {total_expired}")
    print(f"   REJECTED_BY_USER (you passed): {total_user_rejected}")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        mark_expired_jobs()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
