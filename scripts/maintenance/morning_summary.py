# -*- coding: utf-8 -*-
"""
morning_summary.py — Resumen matutino de ofertas para Marcos
=============================================================
Lee todas las pestanas del sheet, cuenta por FIT score (filtrado por GeoOK),
y manda el resumen al bot de Telegram.

Uso:
  py scripts/maintenance/morning_summary.py
  py scripts/maintenance/morning_summary.py --dry-run   # solo imprime, no manda
"""

import sys
import os
import argparse
import requests
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# Cargar token de Telegram desde TheAgora
THEAGORA_ENV = ROOT.parent / "TheAgora" / ".env"
if THEAGORA_ENV.exists():
    load_dotenv(THEAGORA_ENV, override=False)

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

ACTIVE_TABS = ["linkedin", "indeed", "glassdoor", "adzuna", "computrabajo", "jobleads"]

# Columnas clave
FIT_COLS  = ["FIT", "Fit", "fit", "FitScore", "FIT_Score"]
GEO_COLS  = ["GeoOK", "Geo", "geo_ok"]
STAT_COLS = ["Status", "status"]
ROLE_COLS = ["Role", "Title", "title", "role"]


def _get_val(job: dict, candidates: list) -> str:
    for c in candidates:
        v = job.get(c, "")
        if v:
            return str(v).strip()
    return ""


def _parse_fit(fit_str: str) -> int:
    """Extrae numero de FIT. Acepta '8', '8/10', '8.5', '9 - Perfil solido', etc."""
    if not fit_str:
        return -1
    import re
    m = re.search(r"(\d+)", fit_str)
    if m:
        return int(m.group(1))
    return -1


def build_summary(dry_run: bool = False) -> str:
    from core.sheets.sheet_manager import SheetManager

    sm = SheetManager()
    now = datetime.now()

    counts   = defaultdict(int)   # fit_score -> count
    eligible = 0
    total    = 0
    us_only  = 0
    no_score = 0
    top_jobs = []  # (fit, tab, role) para las mejores

    for tab in ACTIVE_TABS:
        try:
            jobs = sm.get_all_jobs(tab)
        except Exception as e:
            print(f"  [WARN] No se pudo leer {tab}: {e}")
            continue

        for job in jobs:
            status = _get_val(job, STAT_COLS).lower()
            if any(s in status for s in ("applied", "expired", "rejected")):
                continue

            geo = _get_val(job, GEO_COLS)
            if geo == "US_ONLY":
                us_only += 1
                continue

            total += 1
            fit_str = _get_val(job, FIT_COLS)
            fit     = _parse_fit(fit_str)

            if fit < 0:
                no_score += 1
                continue

            eligible += 1
            counts[fit] += 1

            role = _get_val(job, ROLE_COLS) or "?"
            top_jobs.append((fit, tab.capitalize(), role[:40]))

    # Ordenar top jobs por fit desc
    top_jobs.sort(key=lambda x: -x[0])

    # ── Construir mensaje ──────────────────────────────────────────────────────
    lines = [
        f"Good morning Marcos! Resumen de jobs al {now.strftime('%d %b %Y %H:%M')}",
        "",
        f"Total activos elegibles: {total} (excluidos US_ONLY: {us_only})",
        f"Con FIT score: {eligible} | Sin analizar: {no_score}",
        "",
        "Distribucion por FIT:",
    ]

    for score in sorted(counts.keys(), reverse=True):
        bar_count = counts[score]
        bar = "■" * min(bar_count, 20)
        lines.append(f"  {score:2d}/10  [{bar}]  {bar_count}")

    # Top 5 ofertas
    if top_jobs:
        lines += ["", "Top 5 mejores ofertas:"]
        for i, (fit, tab, role) in enumerate(top_jobs[:5], 1):
            lines.append(f"  {i}. [{fit}/10] {role} ({tab})")

    # Resumen ejecutivo
    perfect   = counts.get(10, 0)
    excellent = counts.get(9, 0) + counts.get(8, 0)
    good      = counts.get(7, 0) + counts.get(6, 0)
    lines += [
        "",
        f"Perfectas 10/10: {perfect}",
        f"Excelentes 8-9/10: {excellent}",
        f"Buenas 6-7/10: {good}",
    ]

    return "\n".join(lines)


def send_telegram(message: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Falta TELEGRAM_TOKEN o TELEGRAM_CHAT_ID")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=15)
        if r.status_code == 200:
            print("[OK] Mensaje enviado a Telegram")
            return True
        else:
            print(f"[ERROR] Telegram: {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram send: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Resumen matutino de jobs")
    parser.add_argument("--dry-run", action="store_true", help="Solo imprime, no manda a Telegram")
    args = parser.parse_args()

    print("[morning_summary] Generando resumen...")
    try:
        summary = build_summary(dry_run=args.dry_run)
        print("\n" + "=" * 60)
        print(summary)
        print("=" * 60 + "\n")

        if not args.dry_run:
            send_telegram(summary)
        else:
            print("[dry-run] No se mando a Telegram")
    except Exception as e:
        error_msg = f"[morning_summary] ERROR: {e}"
        print(error_msg)
        if not args.dry_run and TELEGRAM_TOKEN:
            send_telegram(f"⚠️ Error en el resumen matutino: {e}")


if __name__ == "__main__":
    main()
