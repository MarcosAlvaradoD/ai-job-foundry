#!/usr/bin/env python3
"""
run_maintenance.py — Pipeline de mantenimiento diario
======================================================
Orquesta todos los scripts de limpieza en el orden correcto:

  1. enrich_unknown_jobs     — llena Company/Role faltantes via LinkedIn guest API
  2. deduplicate_linkedin    — borra filas duplicadas (mismo job ID)
  3. clean_closed_jobs       — borra jobs que ya no aceptan aplicaciones
  4. calculate_fit_scores    — calcula FIT score para nuevas vacantes sin score

Modo normal (diario):
  py scripts/maintenance/run_maintenance.py

Modo deep (semanal - sin límite de jobs a verificar):
  py scripts/maintenance/run_maintenance.py --deep

Modo dry-run (preview sin cambios):
  py scripts/maintenance/run_maintenance.py --dry-run

Solo un paso:
  py scripts/maintenance/run_maintenance.py --only enrich
  py scripts/maintenance/run_maintenance.py --only dedup
  py scripts/maintenance/run_maintenance.py --only clean
  py scripts/maintenance/run_maintenance.py --only fit
"""
import sys
import os
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_step(name: str, script: str, extra_args: list[str] = None, dry_run: bool = False) -> bool:
    """Run a maintenance script as a subprocess. Returns True if successful."""
    args = [sys.executable, str(ROOT / script)]
    if extra_args:
        args.extend(extra_args)
    if dry_run:
        args.append('--dry-run')

    print(f"\n{'='*70}")
    print(f"[STEP] {name}")
    print(f"  cmd: {' '.join(args[1:])}")
    print(f"{'='*70}")

    t0 = time.time()
    try:
        result = subprocess.run(
            args,
            cwd=str(ROOT),
            capture_output=False,   # let output pass through
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        elapsed = time.time() - t0
        if result.returncode == 0:
            print(f"\n  [OK] {name} completado en {elapsed:.1f}s")
            return True
        else:
            print(f"\n  [WARN] {name} termino con codigo {result.returncode} ({elapsed:.1f}s)")
            return False
    except Exception as e:
        elapsed = time.time() - t0
        print(f"\n  [ERROR] {name} fallo: {e} ({elapsed:.1f}s)")
        return False


def main():
    parser = argparse.ArgumentParser(description='Pipeline de mantenimiento diario ai-job-foundry')
    parser.add_argument('--dry-run', action='store_true', help='Preview sin cambios en el Sheet')
    parser.add_argument('--deep',    action='store_true', help='Modo profundo: sin limite en clean_closed')
    parser.add_argument('--only',    choices=['enrich', 'dedup', 'clean', 'fit'],
                        help='Ejecutar solo un paso especifico')
    parser.add_argument('--tab',     default='LinkedIn', help='Sheet tab (default: LinkedIn)')
    args = parser.parse_args()

    start = datetime.now()
    mode  = 'DRY-RUN' if args.dry_run else ('DEEP' if args.deep else 'NORMAL')
    step  = args.only or 'ALL'

    print("=" * 70)
    print("AI Job Foundry — Daily Maintenance Pipeline")
    print(f"Mode: {mode} | Steps: {step} | Tab: {args.tab}")
    print(f"Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = {}

    # ── Step 1: Enrich Unknown Jobs ───────────────────────────────────────────
    if not args.only or args.only == 'enrich':
        ok = run_step(
            "Enrich Unknown Jobs (Company/Role via LinkedIn API)",
            "scripts/maintenance/enrich_unknown_jobs.py",
            extra_args=['--tab', args.tab, '--limit', '50'],
            dry_run=args.dry_run,
        )
        results['enrich'] = ok
        if ok:
            time.sleep(3)  # brief pause between steps

    # ── Step 2: Deduplicate ───────────────────────────────────────────────────
    if not args.only or args.only == 'dedup':
        dedup_args = ['--tab', args.tab] if args.tab != 'LinkedIn' else []
        ok = run_step(
            "Deduplicate (remove duplicate job rows)",
            "scripts/maintenance/deduplicate_linkedin_sheet.py",
            extra_args=dedup_args or None,
            dry_run=args.dry_run,
        )
        results['dedup'] = ok
        if ok:
            time.sleep(3)

    # ── Step 3: Clean Closed Jobs ─────────────────────────────────────────────
    if not args.only or args.only == 'clean':
        clean_args = ['--tab', args.tab]
        if not args.deep:
            # Daily mode: check max 30 jobs to stay fast
            clean_args += ['--limit', '30']
        ok = run_step(
            "Clean Closed Jobs (no longer accepting applications)",
            "scripts/maintenance/clean_closed_jobs.py",
            extra_args=clean_args,
            dry_run=args.dry_run,
        )
        results['clean'] = ok
        if ok:
            time.sleep(3)

    # ── Step 4: FIT Scores ────────────────────────────────────────────────────
    if not args.only or args.only == 'fit':
        ok = run_step(
            "Calculate FIT Scores (new jobs without score)",
            "scripts/maintenance/calculate_linkedin_fit_scores.py",
            dry_run=False,  # fit scores script doesn't support --dry-run
        )
        results['fit'] = ok

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed_total = (datetime.now() - start).total_seconds()
    print(f"\n{'='*70}")
    print("MAINTENANCE PIPELINE SUMMARY")
    print(f"Total time: {elapsed_total:.0f}s")
    print()
    for step_name, ok in results.items():
        status = '[OK]  ' if ok else '[WARN]'
        print(f"  {status} {step_name}")

    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"\n[WARN] {len(failed)} step(s) had issues: {', '.join(failed)}")
        print("       Check output above for details.")
    else:
        print(f"\n[DONE] All {len(results)} step(s) completed successfully!")

    print("=" * 70)


if __name__ == '__main__':
    main()
