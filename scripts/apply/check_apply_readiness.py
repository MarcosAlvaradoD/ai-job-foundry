#!/usr/bin/env python3
"""
check_apply_readiness.py — Pre-apply checklist report
======================================================
Antes de correr run_autoapply.py, muestra un reporte de cuantos
jobs estan listos para aplicar y cuales necesitan atencion.

Clasifica todos los jobs del Sheet en:
  READY       — FIT >= min_fit, Easy Apply, Status=New, no problemas
  NEED_CL     — READY pero sin carta de presentacion en Notes
  LOW_FIT     — FIT < min_fit (candidatos debiles)
  NO_SCORE    — Sin FIT score (necesita calculate_linkedin_fit_scores)
  APPLIED     — Ya aplicado
  SKIPPED     — Skip-* (cerradas, duplicadas, US-Only, etc.)

Uso:
  py scripts/apply/check_apply_readiness.py
  py scripts/apply/check_apply_readiness.py --min 7
  py scripts/apply/check_apply_readiness.py --tab Indeed
  py scripts/apply/check_apply_readiness.py --show-ready   # lista jobs READY
  py scripts/apply/check_apply_readiness.py --show-all     # lista todo
"""
import sys
import os
import re
import argparse
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

SHEET_ID   = os.getenv('GOOGLE_SHEETS_ID')
TOKEN_PATH = Path(__file__).parent.parent.parent / 'data' / 'credentials' / 'token.json'


def get_sheet(tab: str):
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ['https://www.googleapis.com/auth/spreadsheets']
    )
    return gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(tab)


def parse_fit(s: str) -> float:
    """Parse FIT score from '8', '8/10', '8.5', '9 - Perfil solido'."""
    if not s:
        return -1.0
    m = re.search(r'(\d+(?:\.\d+)?)', str(s))
    return float(m.group(1)) if m else -1.0


def classify_jobs(all_vals: list, col: dict, min_fit: float) -> dict:
    buckets = defaultdict(list)

    for sheet_row, row in enumerate(all_vals[1:], start=2):
        def g(c):
            return row[col[c]] if len(row) > col[c] else ''

        company = g('company')
        role    = g('role')
        status  = g('status').lower()
        notes   = g('notes')
        fit_raw = g('fit')
        url     = g('url')

        label   = f"{company} — {role[:45]}"

        # Already applied
        if any(x in status for x in ('applied', 'application submitted')):
            buckets['applied'].append((sheet_row, label, fit_raw))
            continue

        # Skipped for various reasons
        if status.startswith('skip') or status in ('expired', 'closed', 'no longer available', 'rejected'):
            buckets['skipped'].append((sheet_row, label, status))
            continue

        fit = parse_fit(fit_raw)

        # No FIT score at all
        if fit < 0:
            buckets['no_score'].append((sheet_row, label, url[:60]))
            continue

        # Below threshold
        if fit < min_fit:
            buckets['low_fit'].append((sheet_row, label, fit))
            continue

        # Above threshold — check if ready
        has_easy_apply = 'easy apply' in notes.lower() or 'easy apply' in role.lower()
        has_cl = notes.startswith('Estimado') or '[CL]' in notes or '[CL ' in notes

        if not has_cl:
            buckets['need_cl'].append((sheet_row, label, fit))
        else:
            buckets['ready'].append((sheet_row, label, fit))

    return dict(buckets)


def print_bucket(name: str, items: list, show: bool, max_display: int = 20):
    print(f"  {name}: {len(items)}")
    if show and items:
        for item in items[:max_display]:
            if len(item) == 3:
                row, label, extra = item
                print(f"    [{row:3d}] {label}  ({extra})")
        if len(items) > max_display:
            print(f"    ... y {len(items) - max_display} mas")


def main():
    parser = argparse.ArgumentParser(description='Pre-apply readiness report')
    parser.add_argument('--min',        type=float, default=7.0, help='Min FIT score (default: 7)')
    parser.add_argument('--tab',        default='LinkedIn',      help='Sheet tab (default: LinkedIn)')
    parser.add_argument('--show-ready', action='store_true',     help='List jobs in READY bucket')
    parser.add_argument('--show-all',   action='store_true',     help='List all buckets')
    args = parser.parse_args()

    print("=" * 70)
    print("AI Job Foundry — Apply Readiness Report")
    print(f"Tab: {args.tab} | Min FIT: {args.min}")
    print("=" * 70)

    ws = get_sheet(args.tab)
    all_vals = ws.get_all_values()
    if not all_vals:
        print("[ERROR] Sheet vacio o sin acceso.")
        return

    headers = all_vals[0]
    col = {
        'company': next((i for i, h in enumerate(headers) if 'company'   in h.lower()), 1),
        'role':    next((i for i, h in enumerate(headers) if h.lower() == 'role'), 2),
        'url':     next((i for i, h in enumerate(headers) if 'applyurl'  in h.lower()), 5),
        'status':  next((i for i, h in enumerate(headers) if 'status'    in h.lower()), 12),
        'notes':   next((i for i, h in enumerate(headers) if 'notes'     in h.lower()), 22),
        'fit':     next((i for i, h in enumerate(headers) if 'fitscore'  in h.lower()), 20),
    }

    buckets = classify_jobs(all_vals, col, args.min)

    total = sum(len(v) for v in buckets.values())
    ready     = buckets.get('ready',    [])
    need_cl   = buckets.get('need_cl',  [])
    no_score  = buckets.get('no_score', [])
    low_fit   = buckets.get('low_fit',  [])
    applied   = buckets.get('applied',  [])
    skipped   = buckets.get('skipped',  [])

    print(f"\n[TOTAL] {total} filas en {args.tab} tab")
    print()
    print("CLASIFICACION:")
    print_bucket("READY (tienen CL, FIT OK)      ", ready,   args.show_ready or args.show_all)
    print_bucket("NEED_CL (FIT OK, falta carta)  ", need_cl, args.show_all)
    print_bucket("NO_SCORE (sin analizar)         ", no_score, args.show_all)
    print_bucket("LOW_FIT (FIT < {:.0f})           ".format(args.min), low_fit, args.show_all)
    print_bucket("APPLIED (ya aplicado)           ", applied, args.show_all)
    print_bucket("SKIPPED (cerradas/dup/US-Only)  ", skipped, args.show_all)

    actionable = len(ready) + len(need_cl)
    print(f"\n{'='*70}")
    print("ACCIONES RECOMENDADAS:")

    if no_score:
        print(f"\n  1. Calcula FIT scores para {len(no_score)} jobs sin analizar:")
        print(f"     py scripts/maintenance/calculate_linkedin_fit_scores.py")

    if need_cl:
        print(f"\n  2. Genera cartas para {len(need_cl)} jobs con FIT >= {args.min} sin CL:")
        print(f"     py scripts/apply/generate_cover_letters.py --min {args.min:.0f}")

    if ready:
        print(f"\n  3. Aplica a {len(ready)} jobs READY (tienen CL + FIT OK):")
        print(f"     py scripts/apply/run_autoapply.py --dry-run  # preview")
        print(f"     py scripts/apply/run_autoapply.py --submit   # aplicar")

    if not actionable:
        print("\n  Sin jobs listos para aplicar.")
        print("  Corre: py scripts/maintenance/run_maintenance.py")

    if applied:
        print(f"\n  INFO: {len(applied)} jobs ya aplicados.")

    print("=" * 70)


if __name__ == '__main__':
    main()
