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

import json as _json

SHEET_ID    = os.getenv("GOOGLE_SHEETS_ID")
NVIDIA_KEY  = os.getenv("NVIDIA_API_KEY",  "").strip().strip('"').strip("'")
GEMINI_KEY  = os.getenv("GEMINI_API_KEY",  "").strip().strip('"').strip("'")

# ─────────────────────────────────────────────────────────────────────
# MULTI-BACKEND con fallback automático
#
# Prioridad de uso (de más rápido/barato a más lento):
#   1. LLM_URL explícita en .env   → solo ese backend (override manual)
#   2. Gemini Flash (gratis ~15 rpm, OpenAI-compatible)
#   3. NVIDIA NIM (~5 rpm, gratis con key)
#   4. Ollama local (sin límite, privado)
#
# Cuando un backend devuelve 429 se salta al siguiente
# automáticamente sin interrumpir el batch.
# ─────────────────────────────────────────────────────────────────────

def _build_backends() -> list:
    """Construye la lista ordenada de backends disponibles."""
    # Override manual: si LLM_URL está en .env, usar solo ese
    explicit = os.getenv("LLM_URL", "").strip()
    if explicit:
        key = NVIDIA_KEY if "nvidia" in explicit else (
              GEMINI_KEY  if "google"  in explicit else None)
        return [{"name": "Custom", "url": explicit,
                 "model": os.getenv("LLM_MODEL", "gpt-4o-mini"), "key": key}]

    backends = []

    # 1️⃣  Gemini (OpenAI-compatible endpoint)
    if GEMINI_KEY:
        backends.append({
            "name":  "Gemini Flash",
            "url":   "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "model": "gemini-2.0-flash",
            "key":   GEMINI_KEY,
        })

    # 2️⃣  NVIDIA NIM
    if NVIDIA_KEY:
        backends.append({
            "name":  "NVIDIA NIM",
            "url":   "https://integrate.api.nvidia.com/v1/chat/completions",
            "model": "meta/llama-3.3-70b-instruct",
            "key":   NVIDIA_KEY,
        })

    # 3️⃣  Ollama local (solo si responde)
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if r.status_code == 200:
            backends.append({
                "name":  "Ollama local",
                "url":   "http://127.0.0.1:11434/v1/chat/completions",
                "model": os.getenv("LLM_MODEL", "qwen2.5-14b-instruct"),
                "key":   None,
            })
    except Exception:
        pass

    if not backends:
        # Sin configuración válida — Ollama como último recurso (fallará claro)
        backends.append({
            "name":  "Ollama local (sin config)",
            "url":   "http://127.0.0.1:11434/v1/chat/completions",
            "model": os.getenv("LLM_MODEL", "qwen2.5-14b-instruct"),
            "key":   None,
        })

    return backends

# Lista mutable: cuando un backend da 429 definitivo se mueve al final
BACKENDS: list = _build_backends()

# Backend activo (índice 0 siempre es el actual)
def _active_backend() -> dict:
    return BACKENDS[0]

def _rotate_backend(reason: str = "429"):
    """Mueve el backend actual al final y activa el siguiente."""
    if len(BACKENDS) > 1:
        exhausted = BACKENDS.pop(0)
        print(f"   🔄 Backend '{exhausted['name']}' agotado ({reason}) → usando '{BACKENDS[0]['name']}'")
        BACKENDS.append(exhausted)  # lo pone al final por si se recupera
    else:
        print(f"   ⚠️  Solo hay 1 backend disponible, no se puede rotar.")

# Para el resumen del header
LLM_URL   = _active_backend()["url"]
LLM_MODEL = _active_backend()["model"]

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

def _call_backend(backend: dict, prompt: str) -> dict | None:
    """
    Llama a un backend LLM. Devuelve el resultado o None si hay 429
    (para que el llamador rote al siguiente backend).
    """
    headers = {"Content-Type": "application/json"}
    if backend["key"]:
        headers["Authorization"] = f"Bearer {backend['key']}"

    try:
        response = requests.post(
            backend["url"],
            headers=headers,
            json={
                "model": backend["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300,
            },
            timeout=30,
        )

        if response.status_code == 429:
            return None  # señal para rotar backend

        # Key expirada / inválida → rotar (None = rotar al siguiente)
        if response.status_code in (400, 401, 403):
            try:
                err_body = response.json()
                err_msg  = str(err_body).lower()
            except Exception:
                err_msg = response.text.lower()
            if any(w in err_msg for w in ("expired", "invalid", "unauthorized", "forbidden", "api key")):
                return None  # señal para rotar backend

        if response.status_code != 200:
            return {"fit_score": 5,
                    "why": f"AI unavailable (HTTP {response.status_code})",
                    "seniority": "Unknown"}

        content = response.json()["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()
        result  = _json.loads(content)
        # Incluir nombre del backend en Why para detectar scores de Ollama
        why_raw = result.get("why", "Analysis completed")[:180]
        return {
            "fit_score": min(10, max(0, int(result.get("fit_score", 5)))),
            "why":       f"[{backend['name']}] {why_raw}",
            "seniority": result.get("seniority", "Unknown"),
        }

    except Exception as e:
        return {"fit_score": 5, "why": f"Error: {str(e)[:100]}", "seniority": "Unknown"}


def analyze_with_ai(job_data: dict) -> dict:
    """Analiza job con IA usando multi-backend con fallback automático en 429."""
    role     = job_data.get("Role",     "Unknown")
    company  = job_data.get("Company",  "Unknown")
    location = job_data.get("Location", "Unknown")

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

    # Intentar con cada backend; rotar en 429
    attempts_per_backend = 2
    tried = 0
    while tried < len(BACKENDS) * attempts_per_backend:
        backend = _active_backend()
        result  = _call_backend(backend, prompt)

        if result is None:
            # 429 → rotar al siguiente backend sin esperar
            _rotate_backend("429")
            tried += 1
            continue

        return result

    return {"fit_score": 5, "why": "AI unavailable (all backends exhausted)", "seniority": "Unknown"}


def main():
    print("\n" + "="*70)
    print("🎯 CALCULATE FIT SCORES - LINKEDIN TAB")
    print("="*70)
    print(f"Sheet:   {SHEET_ID}")
    print(f"Backends disponibles ({len(BACKENDS)}):")
    for i, b in enumerate(BACKENDS):
        marker = "▶" if i == 0 else " "
        print(f"  {marker} [{i+1}] {b['name']} — {b['model']}")
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
    
    # Filter: sin score, score fallido, o generado por Ollama (no confiable)
    pending = []
    for j in jobs:
        fit = j.get('FitScore')
        why = str(j.get('Why', ''))
        no_score    = not fit or fit == 0 or str(fit).strip() == ''
        bad_score   = 'AI unavailable' in why or why.startswith('Error:')
        ollama_score = '[Ollama local]' in why  # Ollama da scores genéricos, re-procesar
        if no_score or bad_score or ollama_score:
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
            
            # Sleep dinámico según el backend activo
            active_url = _active_backend()["url"]
            if "127.0.0.1" in active_url or "localhost" in active_url:
                sleep_secs = 2   # Ollama local — sin límite
            elif "google" in active_url:
                sleep_secs = 4   # Gemini — 15 rpm → 4s entre requests
            else:
                sleep_secs = 13  # NVIDIA NIM — ~5 rpm → 13s entre requests
            time.sleep(sleep_secs)
            
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
