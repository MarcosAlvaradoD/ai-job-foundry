#!/usr/bin/env python3
"""
Force AI Analysis on ALL Jobs - FIXED VERSION
Recalculates FIT scores for jobs with:
- Role = "Pending AI Analysis"
- Role = "Unknown" 
- FIT Score = 0 or empty
"""

import sys
from pathlib import Path
import time
import json
import requests
from dotenv import load_dotenv
import os

# Add project root to path BEFORE any other imports
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")

CV_TEXT = """
CANDIDATE: Marcos Alberto Alvarado de la Torre
LOCATION: Guadalajara, Mexico
EXPERIENCE: 10+ years

EXPERTISE:
- Project Manager / Product Owner / IT Manager
- ERP migrations (Dynamics AX, SAP, Intelisis)
- ETL & Data Integration (Python, SQL, SSIS)
- Business Analysis & Requirements
- LATAM projects, cross-functional teams

ROLES SEEKING:
- Project Manager, Product Owner, IT Manager
- Business Analyst Lead, Technical Program Manager
- NOT: Software Developer/Programmer roles

PRIORITIES:
- Remote work (family with baby)
- LATAM or remote-friendly positions
"""

def analyze_with_ai(job_data: dict) -> dict:
    """Analiza job con IA local"""
    role = job_data.get('Role', 'Unknown')
    company = job_data.get('Company', 'Unknown')
    location = job_data.get('Location', 'Unknown')
    
    prompt = f"""Eres un experto en análisis de ofertas laborales.

CANDIDATO:
{CV_TEXT}

OFERTA:
Título: {role}
Empresa: {company}
Ubicación: {location}

INSTRUCCIONES:
Calcula FIT SCORE (0-10):
- 0-3: No match (developer, junior, presencial obligatorio)
- 4-6: Medio
- 7-8: Buen match (PM/BA/IT Manager)
- 9-10: Excelente (PM Senior, LATAM, remoto, ERP/ETL)

Responde SOLO en JSON:
{{
  "fit_score": 8,
  "why": "Razón breve",
  "seniority": "Mid-Level | Senior | Lead"
}}"""
    
    try:
        response = requests.post(
            LLM_URL,
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return {'fit_score': 0, 'why': 'AI unavailable', 'seniority': 'Unknown'}
        
        content = response.json()['choices'][0]['message']['content']
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        
        fit_score = min(10, max(0, int(result.get('fit_score', 0))))
        
        return {
            'fit_score': fit_score,
            'why': result.get('why', 'Analysis completed')[:200],
            'seniority': result.get('seniority', 'Unknown')
        }
        
    except Exception as e:
        print(f"      ⚠️  AI Error: {str(e)[:100]}")
        return {'fit_score': 0, 'why': f'Error: {str(e)[:100]}', 'seniority': 'Unknown'}


def main():
    """Force analyze ALL jobs needing FIT scores"""
    
    print("\n" + "="*70)
    print("🤖 FORCE AI ANALYSIS - ALL PENDING JOBS (FIXED)")
    print("="*70)
    print("Calculating FIT scores for jobs with:")
    print("  • Role = 'Pending AI Analysis' or 'Unknown'")
    print("  • FIT Score = 0 or empty")
    print("="*70 + "\n")
    
    try:
        from core.sheets.sheet_manager import SheetManager
        
        sheet_manager = SheetManager()
        
        # Get all tabs
        tabs = ['linkedin', 'indeed', 'glassdoor']  # Minúsculas para coincidir con SheetManager
        
        total_analyzed = 0
        total_errors = 0
        total_skipped = 0
        
        for tab in tabs:
            print(f"\n📊 Processing '{tab}' tab...")
            
            try:
                # Read all jobs from tab
                jobs = sheet_manager.get_all_jobs(tab)
                
                if not jobs:
                    print(f"   ⏭️  No jobs in tab")
                    continue
                
                # Add row numbers (starts at 2, after headers)
                for i, job in enumerate(jobs, start=2):
                    job['_row'] = i
                
                # Filter: pending or unknown roles, no fit score
                pending = []
                for j in jobs:
                    role = str(j.get('Role', '')).strip()
                    fit = j.get('FitScore')
                    
                    if (role in ['Pending AI Analysis', 'Unknown', ''] or 
                        not fit or fit == 0 or str(fit).strip() == ''):
                        pending.append(j)
                
                print(f"   📋 Total jobs: {len(jobs)}")
                print(f"   ⏭️  Pending analysis: {len(pending)}")
                
                if not pending:
                    print(f"   ✅ All jobs have FIT scores!")
                    continue
                
                # Analyze each pending job
                for idx, job in enumerate(pending, 1):
                    try:
                        role = job.get('Role', 'Unknown')
                        company = job.get('Company', 'Unknown')
                        row = job.get('_row', 0)
                        
                        # Progress indicator
                        progress = f"[{idx}/{len(pending)}]"
                        
                        # Analyze with AI
                        result = analyze_with_ai(job)
                        
                        fit_score = result.get('fit_score', 0)
                        
                        if fit_score > 0:
                            # Save to Sheets
                            updates = {
                                'FitScore': fit_score,
                                'Why': result.get('why', '')[:200],
                                'Seniority': result.get('seniority', 'Unknown')
                            }
                            
                            try:
                                sheet_manager.update_job(row, updates, tab)
                                print(f"   {progress} ✅ {role[:25]:25} FIT={fit_score}/10 (row {row})")
                                total_analyzed += 1
                            except Exception as sheet_error:
                                if 'quota' in str(sheet_error).lower() or '429' in str(sheet_error):
                                    print(f"\n   ⚠️  RATE LIMIT HIT - Google Sheets quota exceeded")
                                    print(f"   📊 Analyzed so far: {total_analyzed}")
                                    print(f"   💡 Tip: Wait 1 minute and run again to continue")
                                    return 0
                                else:
                                    print(f"   {progress} ❌ Sheets error: {str(sheet_error)[:50]}")
                                    total_errors += 1
                        else:
                            print(f"   {progress} ⏭️  Skipped (AI returned FIT=0)")
                            total_skipped += 1
                        
                        # Rate limit protection (1.5 sec per write to avoid 429)
                        if fit_score > 0:
                            time.sleep(1.5)
                        else:
                            time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"   [{idx}/{len(pending)}] ❌ Error: {str(e)[:100]}")
                        total_errors += 1
                        continue
                
                print(f"\n   ✅ Tab '{tab}' completed")
                
            except Exception as e:
                print(f"   ❌ Error processing tab '{tab}': {e}")
                total_errors += 1
        
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total Analyzed: {total_analyzed}")
        print(f"Total Skipped: {total_skipped}")
        print(f"Total Errors: {total_errors}")
        print("="*70)
        
        if total_analyzed > 0:
            print("\n✅ AI Analysis completed successfully!")
            print(f"   {total_analyzed} new FIT scores calculated")
            print("\n📊 View results:")
            print("   https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg/edit")
            print("\n🚀 Next step: Auto-apply to high-scoring jobs")
            print("   py core/automation/auto_apply_linkedin_ai_local.py --dry-run")
        else:
            print("\n⚠️  No jobs were analyzed")
            print("This means all jobs already have FIT scores!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
