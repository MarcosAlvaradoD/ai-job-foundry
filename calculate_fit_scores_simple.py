#!/usr/bin/env python3
"""
SIMPLE FIT SCORE CALCULATOR
Toma URLs de LinkedIn → Analiza con IA → Escribe FIT score → Siguiente
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import time
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
import os

load_dotenv()

# Config
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID", "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg")
LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")

# Perfil de Marcos (embedded)
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
- Project Manager
- Product Owner
- IT Manager
- Business Analyst Lead
- Technical Program Manager
- NOT: Software Developer/Programmer roles

PRIORITIES:
- Remote work (family with baby)
- LATAM or remote-friendly positions
- Leadership roles
"""

def analyze_with_ai(job_data: dict) -> dict:
    """Analiza job con IA y retorna FIT score"""
    
    role = job_data.get('Role', 'Unknown')
    company = job_data.get('Company', 'Unknown')
    location = job_data.get('Location', 'Unknown')
    
    prompt = f"""Eres un experto en análisis de ofertas laborales.

CANDIDATO:
{CV_TEXT}

OFERTA A ANALIZAR:
Título: {role}
Empresa: {company}
Ubicación: {location}

INSTRUCCIONES:
Calcula un FIT SCORE del 0 al 10:
- 0-3: No match (developer, junior, presencial obligatorio)
- 4-6: Medio (algunas skills coinciden)
- 7-8: Buen match (PM/BA/IT Manager, buenas skills)
- 9-10: Excelente match (PM Senior, LATAM, remoto, ERP/ETL)

Responde SOLO en formato JSON:
{{
  "fit_score": 8,
  "why": "Razón breve (max 100 palabras)",
  "seniority": "Mid-Level | Senior | Lead"
}}"""
    
    try:
        print(f"   🤖 Analyzing with AI...")
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
            print(f"   ⚠️  AI Error: {response.status_code}")
            return {'fit_score': 5, 'why': 'AI unavailable', 'seniority': 'Unknown'}
        
        content = response.json()['choices'][0]['message']['content']
        
        # Parse JSON
        import json
        content = content.replace('```json', '').replace('```', '').strip()
        result = json.loads(content)
        
        fit_score = min(10, max(0, int(result.get('fit_score', 5))))
        
        print(f"   ✅ FIT Score: {fit_score}/10")
        
        return {
            'fit_score': fit_score,
            'why': result.get('why', 'Analysis completed')[:200],
            'seniority': result.get('seniority', 'Unknown')
        }
        
    except Exception as e:
        print(f"   ❌ AI Error: {e}")
        return {'fit_score': 5, 'why': f'Error: {str(e)[:100]}', 'seniority': 'Unknown'}


def main():
    """Procesa LinkedIn jobs sin FIT score"""
    
    print("\n" + "="*70)
    print("🎯 SIMPLE FIT SCORE CALCULATOR")
    print("="*70)
    print(f"Sheet: {SHEET_ID}")
    print(f"LLM: {LLM_URL}")
    print("="*70 + "\n")
    
    # Init
    sheet_manager = SheetManager()
    
    # Read LinkedIn tab
    print("📊 Reading LinkedIn tab...")
    jobs = sheet_manager.read_tab('LinkedIn')
    
    if not jobs:
        print("❌ No jobs found in LinkedIn tab")
        return
    
    print(f"✅ Found {len(jobs)} jobs\n")
    
    # Filter: solo jobs sin FIT score
    pending = [j for j in jobs if not j.get('FitScore') or j.get('FitScore') == 0]
    
    if not pending:
        print("✅ All jobs already have FIT scores!")
        return
    
    print(f"📋 {len(pending)} jobs need FIT scores\n")
    print("="*70)
    
    # Process each job
    processed = 0
    errors = 0
    
    for i, job in enumerate(pending, 1):
        try:
            role = job.get('Role', 'Unknown')
            company = job.get('Company', 'Unknown')
            row = job.get('_row', 0)
            
            print(f"\n[{i}/{len(pending)}] {role} @ {company}")
            print(f"   Row: {row}")
            
            # Analyze with AI
            result = analyze_with_ai(job)
            
            # Write to Sheets
            print(f"   💾 Saving to Sheets...")
            updates = {
                'FitScore': result['fit_score'],
                'Why': result['why'],
                'Seniority': result['seniority']
            }
            
            sheet_manager.update_job('LinkedIn', row, updates)
            
            print(f"   ✅ Saved!")
            processed += 1
            
            # Rate limit protection
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
        print("\nNext: Check Google Sheets")
        print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0")
    else:
        print("\n⚠️  No jobs were processed")


if __name__ == "__main__":
    main()
