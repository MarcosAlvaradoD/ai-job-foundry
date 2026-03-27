#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate FIT Scores — TODAS LAS TABS
Corre gap analysis + semaforo de colores en LinkedIn, Indeed, Glassdoor,
Adzuna, Computrabajo y JobLeads.

Uso:
    py scripts/maintenance/calculate_all_tabs_fit_scores.py
    py scripts/maintenance/calculate_all_tabs_fit_scores.py --tab LinkedIn
    py scripts/maintenance/calculate_all_tabs_fit_scores.py --rerun-all
"""
import sys
import os
import time
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.enrichment.ai_analyzer import AIAnalyzer
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

# Tabs activas con sus nombres en SheetManager
ACTIVE_TABS = {
    'LinkedIn':    'linkedin',
    'Indeed':      'indeed',
    'Glassdoor':   'glassdoor',
    'Adzuna':      'adzuna',
    'Computrabajo':'computrabajo',
    'JobLeads':    'jobleads',
}

# Colores semaforo (referencia visual)
SEMAFORO = {
    (8, 10): 'VERDE  — Aplica ya',
    (6,  7): 'AMARILLO — Revisa antes',
    (4,  5): 'NARANJA  — Solo si no hay mejor',
    (0,  3): 'ROJO     — No apliques',
}


def process_tab(sheet_manager: SheetManager, analyzer: AIAnalyzer,
                display_name: str, tab_key: str,
                rerun_all: bool = False) -> dict:
    """
    Procesa una pestaña completa: FIT score + gap analysis + semaforo.
    Retorna stats del procesamiento.
    """
    print(f"\n{'='*70}")
    print(f"  TAB: {display_name}")
    print(f"{'='*70}")

    try:
        jobs = sheet_manager.get_all_jobs(tab_key)
    except Exception as e:
        print(f"  No se pudo leer la tab '{display_name}': {e}")
        return {'tab': display_name, 'total': 0, 'processed': 0, 'skipped': 0, 'errors': 0}

    if not jobs:
        print(f"  Sin datos en {display_name} — saltando")
        return {'tab': display_name, 'total': 0, 'processed': 0, 'skipped': 0, 'errors': 0}

    # Filtrar jobs que necesitan FIT score
    if rerun_all:
        pending = jobs
        print(f"  Modo --rerun-all: recalculando {len(pending)} jobs")
    else:
        pending = [j for j in jobs if not str(j.get('FitScore', '')).strip()]
        print(f"  Total: {len(jobs)} | Sin FIT score: {len(pending)}")

    if not pending:
        print(f"  Todos tienen FIT score. Usa --rerun-all para recalcular.")
        return {'tab': display_name, 'total': len(jobs), 'processed': 0, 'skipped': len(jobs), 'errors': 0}

    processed = 0
    errors = 0
    writes_this_minute = 0
    minute_start = time.time()

    for idx, job in enumerate(pending, 1):
        role    = job.get('Role', 'Unknown')[:50]
        company = job.get('Company', 'Unknown')[:30]
        print(f"\n  [{idx}/{len(pending)}] {role} @ {company}")
        print(f"    Fila: {job['_row']}")

        # Rate limit protection
        elapsed = time.time() - minute_start
        if writes_this_minute >= 50 and elapsed < 60:
            wait = int(61 - elapsed)
            print(f"    Rate limit: esperando {wait}s...")
            time.sleep(wait)
            writes_this_minute = 0
            minute_start = time.time()
        if elapsed >= 60:
            writes_this_minute = 0
            minute_start = time.time()

        try:
            result = analyzer.analyze_job(job)
            fit = result.get('fit_score', 5)
            rec = result.get('recomendacion', '')
            print(f"    FIT: {fit}/10  [{rec}]")

            updates = {
                'FitScore':  fit,
                'Why':       result.get('why', ''),
                'Seniority': result.get('seniority', ''),
                'Tienes':    result.get('tienes', ''),
                'Faltan':    result.get('faltan', ''),
            }

            sheet_manager.update_job(job['_row'], updates, tab_key)
            writes_this_minute += 1

            # Semaforo de color
            sheet_manager.color_row_by_fit(job['_row'], fit, tab_key)
            print(f"    Color aplicado")
            processed += 1

            time.sleep(0.6)

        except Exception as e:
            print(f"    Error: {e}")
            errors += 1

    return {
        'tab':       display_name,
        'total':     len(jobs),
        'processed': processed,
        'skipped':   len(jobs) - len(pending),
        'errors':    errors
    }


def main():
    parser = argparse.ArgumentParser(description='FIT Scores para todas las tabs')
    parser.add_argument('--tab',       help='Procesar solo una tab (ej: LinkedIn)')
    parser.add_argument('--rerun-all', action='store_true',
                        help='Recalcular FIT aunque ya exista')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("  CALCULATE FIT SCORES — TODAS LAS TABS")
    print("  Gap analysis + Semaforo de colores")
    print("="*70)

    sheet_id = os.getenv('GOOGLE_SHEETS_ID', 'N/A')
    print(f"\n  Sheet: {sheet_id}")
    print(f"  Modo:  {'Recalcular todo' if args.rerun_all else 'Solo sin FIT score'}")

    sheet_manager = SheetManager()
    analyzer      = AIAnalyzer()

    # Cargar perfil CHALAN una sola vez (lazy load en el analyzer)
    print("\n  Cargando perfil de CHALAN...")
    analyzer._load_profile()
    print(f"  Perfil: {'CHALAN (live)' if 'CHALAN' not in analyzer._profile[:10] else 'fallback hardcodeado'}")

    # Seleccionar tabs a procesar
    if args.tab:
        tabs_to_run = {
            k: v for k, v in ACTIVE_TABS.items()
            if k.lower() == args.tab.lower()
        }
        if not tabs_to_run:
            print(f"\n  Tab '{args.tab}' no reconocida.")
            print(f"  Tabs validas: {', '.join(ACTIVE_TABS.keys())}")
            sys.exit(1)
    else:
        tabs_to_run = ACTIVE_TABS

    all_stats = []
    for display_name, tab_key in tabs_to_run.items():
        stats = process_tab(
            sheet_manager, analyzer,
            display_name, tab_key,
            rerun_all=args.rerun_all
        )
        all_stats.append(stats)

    # Resumen final
    print("\n" + "="*70)
    print("  RESUMEN FINAL")
    print("="*70)
    print(f"  {'Tab':<15} {'Total':>6} {'Procesados':>11} {'Saltados':>9} {'Errores':>8}")
    print(f"  {'-'*55}")
    total_p = total_e = 0
    for s in all_stats:
        print(f"  {s['tab']:<15} {s['total']:>6} {s['processed']:>11} {s['skipped']:>9} {s['errors']:>8}")
        total_p += s['processed']
        total_e += s['errors']
    print(f"  {'-'*55}")
    print(f"  {'TOTAL':<15} {'':>6} {total_p:>11} {'':>9} {total_e:>8}")
    print("="*70)
    print(f"\n  Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    print()


if __name__ == "__main__":
    main()
