#!/usr/bin/env python3
"""
Generate Cover Letters — LiteLLM powered
=========================================
Para cada job en el Sheet de LinkedIn con FIT >= min_score y Status != Applied,
genera una carta de presentación personalizada usando LiteLLM y la guarda en la
columna "Notes" del Sheet.

Usa Chalan para obtener contexto de Marcos antes de generar.

Uso:
  py scripts/apply/generate_cover_letters.py             # FIT>=8, primeros 10
  py scripts/apply/generate_cover_letters.py --min 7     # FIT>=7
  py scripts/apply/generate_cover_letters.py --limit 5   # solo 5 jobs
  py scripts/apply/generate_cover_letters.py --dry-run   # no escribe en Sheet
  py scripts/apply/generate_cover_letters.py --tab Indeed
"""
import sys
import os
import re
import time
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
SHEET_ID     = os.getenv('GOOGLE_SHEETS_ID')
LITELLM_URL  = os.getenv('LITELLM_URL', 'http://localhost:4000')
LITELLM_KEY  = os.getenv('LITELLM_KEY', 'sk-1234567890abcdef')
LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'local-llama')
CHALAN_URL   = os.getenv('CHALAN_URL', 'http://localhost:4001')
TOKEN_PATH   = Path(__file__).parent.parent.parent / 'data' / 'credentials' / 'token.json'

CANDIDATE_SUMMARY = """
Marcos Alberto Alvarado de la Torre
Guadalajara, México | markalvati@gmail.com | +52 33 2332 0358
LinkedIn: linkedin.com/in/marcosalvarado-it

EXPERIENCIA (10+ años):
- Gerente de Proyectos TI / Product Owner / BA
- Migraciones ERP: Dynamics AX, SAP, Intelisis
- ETL & Integración de datos (Python, SQL, SSIS)
- Equipos cross-funcionales LATAM (12-13 personas)
- Agile, Scrum, Lean Six Sigma, BPMN

LOGROS CLAVE:
- Migración ERP de USD 2M+ para empresa manufacturera (on-time, on-budget)
- Implementación BI/ETL con reducción 40% en tiempo de reportes
- Certificaciones: PSPO I, LSSGB, AWS Cloud Practitioner (en progreso)
"""

# ── Chalan context ────────────────────────────────────────────────────────────
def get_chalan_context() -> str:
    try:
        r = requests.get(f'{CHALAN_URL}/context', timeout=5)
        if r.status_code == 200:
            return r.json().get('context', '')
    except Exception:
        pass
    return ''


# ── LiteLLM call ─────────────────────────────────────────────────────────────
def generate_cover_letter(job: dict, chalan_context: str = '') -> str:
    company  = job.get('company', 'la empresa')
    role     = job.get('role', 'el puesto')
    location = job.get('location', '')
    notes    = job.get('notes', '')
    fit      = job.get('fit', '')

    system_msg = "Eres un redactor experto en cartas de presentación para empleos TI en LATAM."
    if chalan_context:
        system_msg += f"\n\nContexto adicional del candidato:\n{chalan_context[:800]}"

    prompt = f"""Escribe una carta de presentación profesional y personalizada en español.

CANDIDATO:
{CANDIDATE_SUMMARY}

VACANTE:
- Empresa: {company}
- Puesto: {role}
- Ubicación: {location or 'México/Remoto'}
- Notas: {notes or 'Sin notas adicionales'}
- FIT Score: {fit}/10

INSTRUCCIONES:
- Longitud: 3 párrafos (max 250 palabras)
- Tono: profesional pero cercano
- Resalta experiencia más relevante para ESTE puesto específico
- Menciona la empresa por nombre
- Cierra con CTA claro
- NO uses bullets ni listas — prosa fluida
- Empieza con "Estimado equipo de {company},"
"""

    try:
        resp = requests.post(
            f'{LITELLM_URL}/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {LITELLM_KEY}',
            },
            json={
                'model': LITELLM_MODEL,
                'messages': [
                    {'role': 'system', 'content': system_msg},
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': 600,
                'temperature': 0.7,
            },
            timeout=90
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        else:
            return f'[ERROR {resp.status_code}] {resp.text[:200]}'
    except Exception as e:
        return f'[ERROR] {e}'


# ── Sheet management ──────────────────────────────────────────────────────────
def get_sheet(tab: str):
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ['https://www.googleapis.com/auth/spreadsheets']
    )
    return gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(tab)


def get_eligible_jobs(ws, min_score: float) -> list[dict]:
    all_vals = ws.get_all_values()
    headers = all_vals[0]

    col = {
        'company':  next((i for i, h in enumerate(headers) if 'company' in h.lower()), 1),
        'role':     next((i for i, h in enumerate(headers) if h.lower() == 'role'), 2),
        'location': next((i for i, h in enumerate(headers) if 'location' in h.lower()), 3),
        'url':      next((i for i, h in enumerate(headers) if 'applyurl' in h.lower()), 5),
        'status':   next((i for i, h in enumerate(headers) if 'status' in h.lower()), 12),
        'notes':    next((i for i, h in enumerate(headers) if 'notes' in h.lower()), -1),
        'fit':      next((i for i, h in enumerate(headers) if 'fitscore' in h.lower()), 17),
        'why':      next((i for i, h in enumerate(headers) if h.lower() == 'why'), -1),
    }

    jobs = []
    for sheet_row, row in enumerate(all_vals[1:], start=2):
        status = row[col['status']] if len(row) > col['status'] else ''
        fit_raw = row[col['fit']] if len(row) > col['fit'] else ''

        # Skip already applied, skipped, or rejected
        if any(x in status.lower() for x in ('applied', 'skip', 'rejected', 'duplicate')):
            continue

        # Parse FIT score
        try:
            fit_num = float(str(fit_raw).split('/')[0])
        except Exception:
            continue

        if fit_num < min_score:
            continue

        company  = row[col['company']]  if len(row) > col['company']  else ''
        role     = row[col['role']]     if len(row) > col['role']      else ''
        location = row[col['location']] if len(row) > col['location'] else ''
        notes    = row[col['notes']]    if col['notes'] >= 0 and len(row) > col['notes'] else ''
        why      = row[col['why']]      if col['why']   >= 0 and len(row) > col['why']   else ''

        # Skip Unknown company (not yet enriched)
        if 'unknown' in company.lower() or 'pending' in role.lower():
            continue

        # Skip if cover letter already generated (Notes starts with "Estimado")
        if notes.startswith('Estimado') or '[CL]' in notes:
            continue

        jobs.append({
            'sheet_row': sheet_row,
            'company':   company,
            'role':      role,
            'location':  location,
            'fit':       fit_num,
            'status':    status,
            'notes':     notes,
            'why':       why,
            'notes_col': col['notes'] + 1 if col['notes'] >= 0 else None,
        })

    return sorted(jobs, key=lambda j: -j['fit'])


def save_cover_letter(ws, job: dict, letter: str, dry_run: bool):
    if not job['notes_col']:
        print("  [SKIP] No Notes column found")
        return

    prefix = f"[CL {datetime.now().strftime('%Y-%m-%d')}]\n"
    content = prefix + letter

    if dry_run:
        print(f"  [DRY-RUN] Would save cover letter ({len(letter)} chars) to Notes col")
        print(f"  Preview:\n  {letter[:200]}...")
        return

    ws.update_cell(job['sheet_row'], job['notes_col'], content)
    print(f"  [OK] Cover letter saved ({len(letter)} chars)")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Generate cover letters via LiteLLM')
    parser.add_argument('--min',     type=float, default=8.0, help='Min FIT score (default: 8)')
    parser.add_argument('--limit',   type=int,   default=10,  help='Max jobs to process (default: 10)')
    parser.add_argument('--tab',     default='LinkedIn', help='Sheet tab (default: LinkedIn)')
    parser.add_argument('--dry-run', action='store_true', help='Do not write to Sheet')
    parser.add_argument('--delay',   type=float, default=5.0, help='Delay between LLM calls (s)')
    args = parser.parse_args()

    print("=" * 70)
    print("Cover Letter Generator — LiteLLM + Google Sheets")
    print(f"Tab: {args.tab} | Min FIT: {args.min} | Limit: {args.limit} | Dry-run: {args.dry_run}")
    print("=" * 70)

    # Pre-fetch Chalan context once
    print("\n[CHALAN] Fetching context...")
    chalan_ctx = get_chalan_context()
    print(f"[OK] Context: {len(chalan_ctx)} chars" if chalan_ctx else "[WARN] No Chalan context available")

    print(f"\n[SHEET] Connecting to {args.tab} tab...")
    ws = get_sheet(args.tab)

    jobs = get_eligible_jobs(ws, args.min)
    print(f"[FOUND] {len(jobs)} jobs eligible (FIT>={args.min}, not applied, company known)")

    if not jobs:
        print("[INFO] Nothing to do.")
        return

    if args.limit > 0:
        jobs = jobs[:args.limit]
        print(f"[LIMIT] Processing first {len(jobs)}")

    generated = 0
    failed = 0

    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] {job['company']} — {job['role']} (FIT: {job['fit']}/10)")

        letter = generate_cover_letter(job, chalan_ctx)

        if letter.startswith('[ERROR'):
            print(f"  [FAILED] {letter}")
            failed += 1
        else:
            save_cover_letter(ws, job, letter, args.dry_run)
            generated += 1

        if i < len(jobs):
            time.sleep(args.delay)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"  Generated: {generated}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {len(jobs)}")
    print("=" * 70)

    if generated > 0 and not args.dry_run:
        print(f"\n[OK] {generated} cover letters saved in Notes column!")
        print("[TIP] Open the Sheet to review and customize before applying")


if __name__ == '__main__':
    main()
