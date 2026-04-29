#!/usr/bin/env python3
"""
run_easy_apply.py — LinkedIn Easy Apply Runner (producción)
============================================================
Script principal para aplicar automáticamente a trabajos de LinkedIn.
Usa EasyApplyBot (async Playwright) — el engine más completo.

Características:
  - Detecta Easy Apply vs External (solo aplica Easy Apply)
  - Llena datos de contacto, sube CV, responde screening questions
  - Maneja dropdowns, radios, inputs de texto/número y textareas
  - Remote/Híbrido/GDL → aplica automático
  - Presencial fuera de GDL → marca REVISION en Sheet (no aplica)
  - Actualiza Google Sheets con status=Applied
  - Dry-run por defecto (seguro)

Uso:
  py scripts/apply/run_easy_apply.py                # dry-run (preview)
  py scripts/apply/run_easy_apply.py --live         # aplica de verdad
  py scripts/apply/run_easy_apply.py --live --max 5 # aplica máx 5
  py scripts/apply/run_easy_apply.py --live --min 8 # solo FIT >= 8
"""

import sys
import asyncio
import time
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ajustar path para importar desde raíz del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.automation.auto_apply_linkedin_easy_complete import EasyApplyBot


def confirm_live_run(max_jobs: int, min_fit: int) -> bool:
    """Pide confirmación antes de aplicar en modo live."""
    print("\n" + "!" * 70)
    print("  MODO LIVE — Las aplicaciones serán ENVIADAS a LinkedIn")
    print(f"  Max jobs: {max_jobs}  |  Min FIT: {min_fit}")
    print("!" * 70)
    print("\nPresiona Ctrl+C para cancelar.")
    print("Continuando en 5 segundos...")
    try:
        for i in range(5, 0, -1):
            print(f"  {i}...", end=' ', flush=True)
            time.sleep(1)
        print()
        return True
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] No se enviaron aplicaciones.")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='LinkedIn Easy Apply — Automation Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  py scripts/apply/run_easy_apply.py                  # preview (dry-run)
  py scripts/apply/run_easy_apply.py --live           # aplicar de verdad
  py scripts/apply/run_easy_apply.py --live --max 3   # hasta 3 aplicaciones
  py scripts/apply/run_easy_apply.py --live --min 8   # solo FIT >= 8
        """
    )
    parser.add_argument('--live',  action='store_true',
                        help='Modo live: envía aplicaciones reales (default: dry-run)')
    parser.add_argument('--max',   type=int, default=5,
                        help='Máximo de aplicaciones por sesión (default: 5)')
    parser.add_argument('--min',   type=int, default=7,
                        help='FIT score mínimo para aplicar (default: 7)')
    args = parser.parse_args()

    dry_run = not args.live

    print("=" * 70)
    print("  AI JOB FOUNDRY — LinkedIn Easy Apply")
    mode_label = "DRY-RUN (preview)" if dry_run else "LIVE (enviando aplicaciones reales)"
    print(f"  Modo:     {mode_label}")
    print(f"  Min FIT:  {args.min}/10")
    print(f"  Max jobs: {args.max}")
    print("=" * 70)

    if not dry_run:
        if not confirm_live_run(args.max, args.min):
            return

    bot = EasyApplyBot(dry_run=dry_run)

    try:
        asyncio.run(bot.run(min_fit=args.min, max_jobs=args.max))
    except KeyboardInterrupt:
        print("\n\n[DETENIDO] Proceso interrumpido por usuario.")


if __name__ == '__main__':
    main()
