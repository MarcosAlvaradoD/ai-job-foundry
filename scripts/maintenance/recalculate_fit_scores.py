#!/usr/bin/env python3
"""
AI JOB FOUNDRY - Recalculate FIT Scores with Salary Weight
Recalcula FIT scores considerando salario como factor crítico
"""
import os
import re
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

load_dotenv()

# Salary thresholds (MXN per month)
SALARY_MIN_ACCEPTABLE = 30000  # $30k MXN = ~$1,700 USD
SALARY_PREFERRED = 50000        # $50k MXN = ~$2,900 USD
SALARY_EXCELLENT = 80000        # $80k MXN = ~$4,600 USD

# Minimum national wage Mexico 2024
SALARY_MIN_NATIONAL = 7468      # Salario mínimo legal


def extract_salary_from_text(text):
    """Extract salary from compensation text"""
    if not text:
        return None, None
    
    text = str(text).upper()
    
    # Remove commas
    text = text.replace(',', '')
    
    # Patterns for salary extraction
    patterns = [
        # MXN patterns
        r'(\d+)\s*K?\s*MXN',
        r'MXN\s*\$?(\d+)',
        r'\$(\d+)\s*MXN',
        r'(\d+)\s*PESOS',
        # USD patterns
        r'(\d+)\s*K?\s*USD',
        r'USD\s*\$?(\d+)',
        r'\$(\d+)\s*USD',
        # Range patterns
        r'(\d+)\s*-\s*(\d+)',
        r'(\d+)\s*A\s*(\d+)',
    ]
    
    currency = None
    amount = None
    
    # Check for currency
    if 'USD' in text or 'DOLLAR' in text:
        currency = 'USD'
    elif 'MXN' in text or 'PESO' in text:
        currency = 'MXN'
    
    # Extract amount
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                # Range found, take max
                amount = max(int(match.group(1)), int(match.group(2)))
            else:
                amount = int(match.group(1))
            
            # Adjust if in thousands
            if 'K' in text and amount < 1000:
                amount *= 1000
            
            break
    
    if amount and not currency:
        # Guess currency based on amount
        if amount < 10000:
            # Probably USD (in thousands)
            currency = 'USD'
            if amount < 1000:
                amount *= 1000
        else:
            # Probably MXN
            currency = 'MXN'
    
    return amount, currency


def convert_to_mxn(amount, currency):
    """Convert salary to MXN"""
    if not amount:
        return None
    
    if currency == 'USD':
        # USD to MXN (approximate rate: 1 USD = 17 MXN)
        return amount * 17
    else:
        return amount


def calculate_salary_penalty(salary_mxn):
    """Calculate FIT score penalty/bonus based on salary"""
    if not salary_mxn:
        return 0  # No data, no penalty
    
    # CRITICAL: Below minimum acceptable
    if salary_mxn < SALARY_MIN_ACCEPTABLE:
        # Severe penalty: -5 to -3 points
        if salary_mxn < 20000:
            return -5  # Extremely low
        else:
            return -3  # Below minimum
    
    # Below preferred
    elif salary_mxn < SALARY_PREFERRED:
        return -1  # Small penalty
    
    # Good range
    elif salary_mxn < SALARY_EXCELLENT:
        return 0  # No change
    
    # Excellent
    else:
        return +1  # Bonus point


def recalculate_fit_scores():
    """Recalculate FIT scores for all jobs"""
    print("\n💰 Recalculating FIT Scores with Salary Weight...")
    print("="*70)
    print(f"Minimum acceptable: ${SALARY_MIN_ACCEPTABLE:,} MXN")
    print(f"Preferred:          ${SALARY_PREFERRED:,} MXN")
    print(f"Excellent:          ${SALARY_EXCELLENT:,} MXN")
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
    
    # Process Jobs tab
    try:
        print(f"\n📋 Processing 'Jobs' tab...")
        worksheet = spreadsheet.worksheet('Jobs')
        
        # Get all values
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            print(f"  No data")
            return
        
        headers = all_values[0]
        data_rows = all_values[1:]
        
        print(f"  Found {len(data_rows)} jobs")
        
        # Find columns
        try:
            comp_col = headers.index('Comp')
        except:
            comp_col = 9  # Column J
        
        try:
            fit_col = headers.index('FitScore')
        except:
            fit_col = 16  # Column Q
        
        try:
            why_col = headers.index('Why')
        except:
            why_col = 17  # Column R
        
        updated_count = 0
        
        for idx, row in enumerate(data_rows, start=2):
            if len(row) <= max(comp_col, fit_col):
                continue
            
            # Get current values
            comp_text = row[comp_col] if len(row) > comp_col else ''
            current_fit = row[fit_col] if len(row) > fit_col else ''
            current_why = row[why_col] if len(row) > why_col else ''
            
            # Extract salary
            salary_amount, currency = extract_salary_from_text(comp_text)
            
            if not salary_amount:
                continue
            
            # Convert to MXN
            salary_mxn = convert_to_mxn(salary_amount, currency)
            
            # Calculate penalty
            penalty = calculate_salary_penalty(salary_mxn)
            
            if penalty == 0:
                continue  # No change needed
            
            # Get current FIT score
            try:
                current_score = int(str(current_fit).split('/')[0]) if current_fit else 5
            except:
                current_score = 5
            
            # Calculate new score
            new_score = max(0, min(10, current_score + penalty))
            
            # Only update if changed
            if new_score != current_score:
                try:
                    # Update FIT score
                    worksheet.update_cell(idx, fit_col + 1, f"{new_score}/10")
                    
                    # Update Why column with salary note
                    salary_note = f"[Salary: ${salary_mxn:,.0f} MXN]"
                    if penalty < 0:
                        salary_note += f" Below minimum (penalty {penalty})"
                    elif penalty > 0:
                        salary_note += f" Excellent (bonus +{penalty})"
                    
                    new_why = f"{current_why} | {salary_note}" if current_why else salary_note
                    worksheet.update_cell(idx, why_col + 1, new_why)
                    
                    print(f"    ✅ Row {idx}: {current_score} → {new_score}/10")
                    print(f"       Salary: ${salary_mxn:,.0f} MXN (penalty: {penalty})")
                    updated_count += 1
                    
                except Exception as e:
                    print(f"    ❌ Row {idx}: Error - {e}")
        
        print(f"\n  ✅ Updated {updated_count} FIT scores")
        
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print(f"📊 Recalculation complete")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        recalculate_fit_scores()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
