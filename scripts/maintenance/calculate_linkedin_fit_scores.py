#!/usr/bin/env python3
"""
CALCULATE FIT SCORES - SIMPLE & WORKING
Calcula FIT scores para jobs de LinkedIn que NO tienen score
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import time
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
import os

# Windows UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
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
- LATAM projects, cross-functional teams (12-13+ people)
- Agile, Scrum, Lean Six Sigma

ROLES SEEKING:
- Project Manager, Product Owner, IT Manager
- Business Analyst Lead, Technical Program Manager
- NOT: Software Developer/Programmer roles

PRIORITIES:
- Remote work (family with baby)
- LATAM or remote-friendly positions
- Leadership roles
"""

def analyze_with_ai(job_data: dict) -> dict:
    """Analiza job con IA"""
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
            return {'fit_score': 5, 'why': 'AI unavailable', 'seniority': 'Unknown'}
        
        content = response.json()['choices'][0]['message']['content']
        
        import json
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        
        fit_score = min(10, max(0, int(result.get('fit_score', 5))))
        
        return {
            'fit_score': fit_score,
            'why': result.get('why', 'Analysis completed')[:200],
            'seniority': result.get('seniority', 'Unknown')
        }
        
    except Exception as e:
        return {'fit_score': 5, 'why': f'Error: {str(e)[:100]}', 'seniority': 'Unknown'}


def main():
    print("\n" + "="*70)
    print("🎯 CALCULATE FIT SCORES - LINKEDIN TAB")
    print("="*70)
    print(f"Sheet: {SHEET_ID}")
    print(f"LLM: {LLM_URL}")
    print("="*70 + "\n")
    
    sheet_manager = SheetManager()
    
    # Read LinkedIn tab
    print("📊 Reading LinkedIn tab...")
    jobs = sheet_manager.get_all_jobs('linkedin')  # ✅ CORRECTO: get_all_jobs() no read_tab()
    
    # Add row numbers (starts at 2, after headers)
    for i, job in enumerate(jobs, start=2):
        job['_row'] = i
    
    if not jobs:
        print("❌ No jobs in LinkedIn tab")
        return
    
    print(f"✅ Found {len(jobs)} total jobs\n")
    
    # Filter: NO FIT score
    pending = []
    for j in jobs:
        fit = j.get('FitScore')
        if not fit or fit == 0 or fit == '' or str(fit).strip() == '':
            pending.append(j)
    
    if not pending:
        print("✅ All jobs have FIT scores!")
        return
    
    print(f"📋 {len(pending)} jobs need FIT scores\n")
    print("="*70)
    
    processed = 0
    errors = 0
    
    for i, job in enumerate(pending, 1):
        try:
            role = job.get('Role', 'Unknown')
            company = job.get('Company', 'Unknown')
            row = job.get('_row', 0)
            
            print(f"\n[{i}/{len(pending)}] {role} @ {company}")
            print(f"   Row: {row}")
            
            # Analyze
            print(f"   🤖 Analyzing...")
            result = analyze_with_ai(job)
            
            print(f"   ✅ FIT: {result['fit_score']}/10")
            
            # Save
            print(f"   💾 Saving...")
            updates = {
                'FitScore': result['fit_score'],
                'Why': result['why'],
                'Seniority': result['seniority']
            }
            
            sheet_manager.update_job(row, updates, 'linkedin')  # ✅ minúscula para coincidir con self.tabs
            
            print(f"   ✅ Saved!")
            processed += 1
            
            # Rate limit
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            errors += 1
            continue
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Processed: {processed}")
    print(f"Errors: {errors}")
    print("="*70)
    
    if processed > 0:
        print("\n✅ FIT scores calculated!")
        print(f"\nView: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0")


if __name__ == "__main__":
    main()
