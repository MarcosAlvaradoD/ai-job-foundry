#!/usr/bin/env python3
"""
AI JOB FOUNDRY - Calculate FIT Scores for ALL Jobs (ENHANCED)
✅ Procesa TODAS las pestañas automáticamente
✅ Maneja jobs con Role="Unknown" usando Notes + Company
✅ Usa LM Studio (Qwen 2.5 14B)
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ✅ FIX: Windows UTF-8 support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials
from core.enrichment.ai_analyzer import AIAnalyzer
import time

load_dotenv()


def extract_role_from_notes(notes, company):
    """
    Extrae información relevante de Notes cuando Role="Unknown"
    """
    if not notes or notes == 'Unknown':
        return f"Job position at {company}"
    
    # Notes format: "Remote info | LLM v1 | LLM v2"
    # Extraer la parte relevante
    parts = notes.split('|')
    relevant_info = ' '.join([p.strip() for p in parts if 'LLM' not in p and 'México' in p or 'Remote' in p])
    
    if relevant_info:
        return f"{relevant_info} at {company}"
    else:
        return f"Position at {company}"


def calculate_all_fit_scores():
    """Calcula FIT scores para todos los jobs sin score"""
    print("\n🤖 AI JOB FOUNDRY - FIT Score Calculator (ENHANCED)")
    print("="*70)
    print("Calculando FIT scores con LM Studio (Qwen 2.5 14B)")
    print("✅ NUEVO: Procesa jobs con Role='Unknown' usando Notes")
    print("="*70)
    
    # Initialize AI Analyzer
    ai_analyzer = AIAnalyzer()
    print("✅ AI Analyzer inicializado")
    
    # Get credentials
    base_path = Path(__file__).parent.parent.parent
    token_path = base_path / "data" / "credentials" / "token.json"
    
    creds = Credentials.from_authorized_user_file(
        str(token_path),
        ['https://www.googleapis.com/auth/spreadsheets']
    )
    
    # Connect to sheet
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    if not sheet_id:
        print("❌ GOOGLE_SHEETS_ID not found in .env")
        return
    
    spreadsheet = client.open_by_key(sheet_id)
    print("✅ Conectado a Google Sheets")
    
    # ✅ Procesar TODAS las pestañas
    all_worksheets = spreadsheet.worksheets()
    print(f"\n📑 Found {len(all_worksheets)} tabs")
    
    total_analyzed = 0
    total_skipped = 0
    tabs_processed = 0
    
    for worksheet in all_worksheets:
        tab_name = worksheet.title
        
        # ⚠️ Skip non-job tabs
        if tab_name.lower() in ['config', 'settings', 'dashboard', 'summary', 'resumen']:
            print(f"\n  ⏭️  Skipping '{tab_name}' (config tab)")
            continue
        
        print(f"\n📋 Processing '{tab_name}'...")
        
        try:
            # Get all values
            all_values = worksheet.get_all_values()
            
            if len(all_values) < 2:
                print(f"  ⚠️  No data in '{tab_name}'")
                continue
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            print(f"  📊 Found {len(data_rows)} jobs")
            
            # Find columns
            try:
                role_col = headers.index('Role')
            except:
                role_col = 2  # Column C
            
            try:
                company_col = headers.index('Company')
            except:
                company_col = 1  # Column B
            
            try:
                url_col = headers.index('ApplyURL')
            except:
                url_col = 5  # Column F
            
            try:
                fit_col = headers.index('FitScore')
            except:
                fit_col = 15  # Column P (Glassdoor format)
            
            try:
                why_col = headers.index('Why')
            except:
                why_col = 16  # Column Q
            
            try:
                seniority_col = headers.index('Seniority')
            except:
                seniority_col = 10  # Column K
            
            try:
                notes_col = headers.index('Notes')
            except:
                notes_col = 14  # Column O
            
            analyzed_count = 0
            skipped_count = 0
            unknown_role_count = 0
            
            for idx, row in enumerate(data_rows, start=2):
                # Check if FIT score already exists
                current_fit = row[fit_col] if len(row) > fit_col else ''
                
                if current_fit and current_fit.strip() and current_fit != 'Unknown':
                    skipped_count += 1
                    continue
                
                # Get job data
                role = row[role_col] if len(row) > role_col else 'Unknown'
                company = row[company_col] if len(row) > company_col else 'Unknown'
                url = row[url_col] if len(row) > url_col else ''
                notes = row[notes_col] if len(row) > notes_col else ''
                
                # ✅ NUEVO: Handle Role="Unknown"
                if role == 'Unknown' or not role.strip():
                    # Use Notes + Company as context
                    role = extract_role_from_notes(notes, company)
                    unknown_role_count += 1
                
                # Skip if still no useful info
                if company == 'Unknown' and role == 'Unknown':
                    continue
                
                print(f"    🤖 Analyzing [{idx}] {role[:50]}...")
                
                try:
                    # Prepare job data for AI
                    job_data = {
                        'Role': role,
                        'Company': company,
                        'ApplyURL': url,
                        'full_description': f"{role} at {company}. Context: {notes[:200]}"
                    }
                    
                    # Analyze with AI
                    result = ai_analyzer.analyze_job(job_data)
                    
                    # Get results
                    fit_score = result.get('fit_score', 5)
                    why = result.get('why', 'AI analysis completed')
                    seniority = result.get('seniority', 'Mid-Level')
                    
                    # Update FIT score
                    worksheet.update_cell(idx, fit_col + 1, f"{fit_score}/10")
                    
                    # Update Why
                    worksheet.update_cell(idx, why_col + 1, why)
                    
                    # Update Seniority
                    worksheet.update_cell(idx, seniority_col + 1, seniority)
                    
                    emoji = "🔥" if fit_score >= 7 else "✅"
                    print(f"       {emoji} FIT: {fit_score}/10 | {seniority}")
                    analyzed_count += 1
                    
                    # Rate limiting (Google Sheets API)
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"       ❌ Error: {e}")
                    continue
            
            print(f"  ✅ Analyzed {analyzed_count} jobs in '{tab_name}'")
            if unknown_role_count > 0:
                print(f"     ℹ️  {unknown_role_count} had Role='Unknown' (used Notes+Company)")
            print(f"  ℹ️  Skipped {skipped_count} jobs (already have FIT score)")
            
            total_analyzed += analyzed_count
            total_skipped += skipped_count
            
            if analyzed_count > 0:
                tabs_processed += 1
                
        except Exception as e:
            print(f"  ❌ Error processing '{tab_name}': {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*70)
    print(f"📊 FIT Score Calculation Complete")
    print(f"   Tabs processed: {tabs_processed}")
    print(f"   Jobs analyzed: {total_analyzed}")
    print(f"   Jobs skipped (already scored): {total_skipped}")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        calculate_all_fit_scores()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
