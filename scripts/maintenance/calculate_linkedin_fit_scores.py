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

SHEET_ID   = os.getenv("GOOGLE_SHEETS_ID")
NVIDIA_KEY = os.getenv("NVIDIA_API_KEY", "").strip().strip('"').strip("'")

# Auto-selección de backend (prioridad: Ollama local → NVIDIA NIM):
#   1) Si LLM_URL está explícitamente en .env → úsala tal cual
#   2) Si Ollama está corriendo en localhost:11434 → úsalo (gratis, privado)
#   3) Si Ollama no responde Y NVIDIA_API_KEY tiene valor → NVIDIA NIM (nube)
#   4) Si ninguno → Ollama de todas formas (fallará con mensaje claro)

def _detect_backend():
    """Detecta si Ollama está corriendo; si no, cae a NVIDIA NIM."""
    # Si el usuario fijó LLM_URL manualmente en .env, respetarlo
    explicit_url = os.getenv("LLM_URL", "")
    if explicit_url:
        model = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")
        return explicit_url, model

    # Intentar Ollama local (timeout corto para no bloquear)
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if r.status_code == 200:
            return ("http://127.0.0.1:11434/v1/chat/completions",
                    os.getenv("LLM_MODEL", "qwen2.5-14b-instruct"))
    except Exception:
        pass

    # Fallback: NVIDIA NIM si hay key
    if NVIDIA_KEY:
        return ("https://integrate.api.nvidia.com/v1/chat/completions",
                "meta/llama-3.3-70b-instruct")

    # Último recurso: Ollama (fallará con mensaje de error claro)
    return ("http://127.0.0.1:11434/v1/chat/completions",
            os.getenv("LLM_MODEL", "qwen2.5-14b-instruct"))

LLM_URL, LLM_MODEL = _detect_backend()

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
    
    # Auth header: solo si hay API key (NVIDIA NIM / OpenAI) — Ollama local no lo necesita
    headers = {"Content-Type": "application/json"}
    if NVIDIA_KEY and "127.0.0.1" not in LLM_URL and "localhost" not in LLM_URL:
        headers["Authorization"] = f"Bearer {NVIDIA_KEY}"

    try:
        response = requests.post(
            LLM_URL,
            headers=headers,
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            },
            timeout=30
        )

        if response.status_code != 200:
            return {'fit_score': 5, 'why': f'AI unavailable (HTTP {response.status_code})', 'seniority': 'Unknown'}
        
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
    backend = ("NVIDIA NIM (nube)" if "nvidia" in LLM_URL
               else "Ollama local" if "127.0.0.1" in LLM_URL or "localhost" in LLM_URL
               else "API externa")
    print(f"Sheet:   {SHEET_ID}")
    print(f"Backend: {backend}")
    print(f"LLM URL: {LLM_URL}")
    print(f"Model:   {LLM_MODEL}")
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
    
    # Filter: sin score O score fallido anteriormente ("AI unavailable" / "Error:")
    pending = []
    for j in jobs:
        fit = j.get('FitScore')
        why = str(j.get('Why', ''))
        no_score  = not fit or fit == 0 or str(fit).strip() == ''
        bad_score = 'AI unavailable' in why or why.startswith('Error:')
        if no_score or bad_score:
            pending.append(j)

    if not pending:
        print("✅ All jobs have valid FIT scores!")
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
