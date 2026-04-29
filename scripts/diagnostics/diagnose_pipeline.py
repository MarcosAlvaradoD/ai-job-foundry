#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO DEL PIPELINE
===================================
Muestra el estado real de:
1. Jobs en cada pestaña del Sheet
2. Cuántos tienen ApplyURL vs vacía
3. Cuántos son elegibles para auto-apply (FIT>=7 + URL + status)
4. Qué tabs existen en el Sheet
5. Headers de cada tab (para detectar desalineación de columnas)

USO:
  py scripts/diagnostics/diagnose_pipeline.py

Autor: AI Job Foundry — Marcos Alvarado
"""

import sys
import os
from pathlib import Path

# Asegurar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

SHEET_ID = os.getenv('GOOGLE_SHEETS_ID', '1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg')

FIT_THRESHOLD = 7
BLOCKED_STATUSES = {'APPLIED', 'EXPIRED', 'REJECTED', 'NO MATCH', 'INVALID'}

def get_credentials():
    token_path = PROJECT_ROOT / "data" / "credentials" / "token.json"
    creds_path = PROJECT_ROOT / "data" / "credentials" / "credentials.json"
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
    return creds

def safe_fit(v):
    try:
        if not v: return 0
        s = str(v).strip()
        if '/' in s: return int(s.split('/')[0])
        return int(float(s))
    except Exception: return 0

def main():
    print("=" * 65)
    print("🔍 AI JOB FOUNDRY — DIAGNÓSTICO DE PIPELINE")
    print("=" * 65)

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    ss = service.spreadsheets()

    # ── 1. Listar todas las pestañas ──────────────────────────────────
    meta = ss.get(spreadsheetId=SHEET_ID).execute()
    sheets = meta.get('sheets', [])
    tab_names = [s['properties']['title'] for s in sheets]

    print(f"\n📋 PESTAÑAS EN EL SHEET ({len(tab_names)}):")
    for t in tab_names:
        print(f"   • {t}")

    # ── 2. Analizar cada pestaña ──────────────────────────────────────
    TARGET_TABS = ['LinkedIn', 'Indeed', 'Glassdoor', 'JobLeads', 'Computrabajo', 'Jobs']
    total_eligible = 0
    total_with_url = 0

    for tab in TARGET_TABS:
        if tab not in tab_names:
            print(f"\n⚠️  Tab '{tab}' — NO EXISTE en el sheet")
            continue

        print(f"\n{'─'*65}")
        print(f"📁 TAB: {tab}")

        result = ss.values().get(
            spreadsheetId=SHEET_ID,
            range=f"{tab}!A1:R500"
        ).execute()
        values = result.get('values', [])

        if not values:
            print("   ❌ Vacía o sin datos")
            continue

        headers = values[0]
        rows = values[1:]

        print(f"   Headers ({len(headers)}): {headers[:10]}")

        # Verificar columna ApplyURL
        url_col = None
        fit_col = None
        status_col = None
        role_col = None
        for i, h in enumerate(headers):
            h_clean = h.strip().lower()
            if h_clean == 'applyurl': url_col = i
            elif h_clean in ('fitscore', 'fit', 'fit_score'): fit_col = i
            elif h_clean == 'status': status_col = i
            elif h_clean == 'role': role_col = i

        print(f"   ApplyURL col: {f'✅ col {url_col} ({headers[url_col]})' if url_col is not None else '❌ NO ENCONTRADA'}")
        print(f"   FitScore col: {f'✅ col {fit_col} ({headers[fit_col]})' if fit_col is not None else '❌ NO ENCONTRADA'}")
        print(f"   Status col:   {f'✅ col {status_col}' if status_col is not None else '❌ NO ENCONTRADA'}")

        # Stats de datos
        n_total = len(rows)
        n_with_url = sum(1 for r in rows if url_col is not None and url_col < len(r) and r[url_col].strip() not in ('', 'Unknown', 'N/A'))
        n_empty_url = n_total - n_with_url
        n_fit7 = sum(1 for r in rows if fit_col is not None and fit_col < len(r) and safe_fit(r[fit_col]) >= FIT_THRESHOLD)
        n_eligible = 0

        eligible_jobs = []
        for i, r in enumerate(rows):
            url  = r[url_col].strip() if (url_col is not None and url_col < len(r)) else ''
            fit  = safe_fit(r[fit_col]) if (fit_col is not None and fit_col < len(r)) else 0
            stat = r[status_col].strip().upper() if (status_col is not None and status_col < len(r)) else ''
            role = r[role_col].strip() if (role_col is not None and role_col < len(r)) else '?'

            if fit >= FIT_THRESHOLD and stat not in BLOCKED_STATUSES and url not in ('', 'Unknown', 'N/A'):
                n_eligible += 1
                eligible_jobs.append({'role': role, 'fit': fit, 'status': stat, 'url': url[:60]})

        total_with_url += n_with_url
        total_eligible += n_eligible

        print(f"\n   📊 RESUMEN:")
        print(f"      Total jobs:        {n_total:>4}")
        print(f"      Con ApplyURL:      {n_with_url:>4}  {'✅' if n_with_url > 0 else '❌ PROBLEMA'}")
        print(f"      Sin ApplyURL:      {n_empty_url:>4}  {'⚠️' if n_empty_url > 5 else '✅'}")
        print(f"      FIT >= {FIT_THRESHOLD}:         {n_fit7:>4}")
        print(f"      ELEGIBLES apply:   {n_eligible:>4}  {'✅' if n_eligible > 0 else '❌'}")

        if eligible_jobs:
            print(f"\n   🎯 JOBS LISTOS PARA AUTO-APPLY (FIT>={FIT_THRESHOLD} + URL + Status OK):")
            for j in eligible_jobs[:8]:
                print(f"      [{j['fit']}/10] {j['role'][:45]:<45} | {j['url']}")

        # Mostrar sample de jobs SIN URL si hay muchos
        if n_empty_url > 0 and url_col is not None:
            missing_sample = [
                r[role_col].strip() if (role_col is not None and role_col < len(r)) else '?'
                for r in rows if url_col < len(r) and r[url_col].strip() in ('', 'Unknown', 'N/A')
            ][:5]
            if missing_sample:
                print(f"\n   ⚠️  Muestra de jobs SIN URL ({n_empty_url} total):")
                for role in missing_sample:
                    print(f"      - {role[:55]}")

    # ── 3. Resumen global ─────────────────────────────────────────────
    print(f"\n{'='*65}")
    print(f"📈 RESUMEN GLOBAL")
    print(f"{'='*65}")
    print(f"   Jobs con ApplyURL:      {total_with_url}")
    print(f"   Jobs elegibles apply:   {total_eligible}")

    if total_eligible > 0:
        print(f"\n   ✅ Hay {total_eligible} jobs listos — ejecuta:")
        print(f"      py core/automation/auto_apply_linkedin.py --dry-run")
        print(f"      py core/automation/auto_apply_linkedin.py --live")
    else:
        print(f"\n   ❌ Ningún job elegible. Acciones recomendadas:")
        print(f"      1. Procesar emails:  py core/automation/job_bulletin_processor.py")
        print(f"      2. Calcular FIT:     py scripts/maintenance/calculate_linkedin_fit_scores_v2.py")
        print(f"      3. Re-ejecutar este diagnóstico")

    print(f"\n{'='*65}")

if __name__ == '__main__':
    main()
