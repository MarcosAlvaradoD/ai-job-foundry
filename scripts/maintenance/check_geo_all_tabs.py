# -*- coding: utf-8 -*-
"""
check_geo_all_tabs.py — Filtro geografico para ofertas remotas
==============================================================
Revisa cada URL en el sheet y determina si la oferta aplica para Marcos
(Guadalajara MX, visa turista USA, NO work authorization USA).

Resultados posibles en columna 'GeoOK':
  GLOBAL   -> Aplica (remoto global / LATAM confirmado)
  MX       -> Aplica (Mexico / Guadalajara)
  UNKNOWN  -> Aplica (sin restricciones detectadas, beneficio de la duda)
  US_ONLY  -> NO aplica (requiere presencia o auth en USA)

El script ademas pinta las filas US_ONLY de gris para que se vean diferentes.

Uso:
  py scripts/maintenance/check_geo_all_tabs.py
  py scripts/maintenance/check_geo_all_tabs.py --tab LinkedIn
  py scripts/maintenance/check_geo_all_tabs.py --rerun-all   # re-check aun si ya tiene GeoOK
  py scripts/maintenance/check_geo_all_tabs.py --no-fetch    # solo analiza texto, sin descargar URLs
"""

import sys
import time
import argparse
from pathlib import Path

# Setup path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from core.sheets.sheet_manager import SheetManager
from core.enrichment.geo_checker import check_geo_eligibility

ACTIVE_TABS = {
    "LinkedIn":     "linkedin",
    "Indeed":       "indeed",
    "Glassdoor":    "glassdoor",
    "Adzuna":       "adzuna",
    "Computrabajo": "computrabajo",
    "JobLeads":     "jobleads",
}

# Color gris para US_ONLY — RGBA 0.0-1.0
GREY_COLOR = {"red": 0.78, "green": 0.78, "blue": 0.78}
# Blanco = restablecer (para recalculos)
WHITE_COLOR = {"red": 1.0, "green": 1.0, "blue": 1.0}


def process_tab(sm: SheetManager, tab_key: str, tab_name: str,
                rerun: bool = False, fetch_url: bool = True,
                rerun_unknown: bool = False) -> dict:
    """
    Procesa un tab completo y escribe la columna GeoOK.
    Returns: stats dict
    """
    stats = {"total": 0, "skipped": 0, "global": 0, "mx": 0,
             "unknown": 0, "us_only": 0, "errors": 0}

    try:
        jobs = sm.get_all_jobs(tab_key)
    except Exception as e:
        print(f"  [ERROR] No se pudo leer tab {tab_name}: {e}")
        return stats

    stats["total"] = len(jobs)

    for job in jobs:
        row = job.get("_row")
        if not row:
            continue

        # Saltar si ya tiene GeoOK y no se pide rerun
        existing = str(job.get("GeoOK", "")).strip()
        if existing and not rerun:
            # --rerun-unknown: solo repetir los que quedaron UNKNOWN
            if rerun_unknown and existing == "UNKNOWN":
                pass  # continuar — re-analizar con fetch
            else:
                stats["skipped"] += 1
                continue

        # Saltar jobs ya aplicados o expirados
        status = str(job.get("Status", "")).lower()
        if "applied" in status or "expired" in status or "rejected" in status:
            stats["skipped"] += 1
            continue

        try:
            geo = check_geo_eligibility(job, fetch_url=fetch_url, delay=1.0)
            geo_value = geo["geo"]  # GLOBAL | MX | US_ONLY | UNKNOWN

            # Escribir en columna GeoOK del sheet
            sm.update_cell(tab_key, row, "GeoOK", geo_value)

            # Si es US_ONLY → pintar gris la fila
            if geo_value == "US_ONLY":
                try:
                    _paint_row_grey(sm, tab_key, row)
                except Exception:
                    pass
                stats["us_only"] += 1
                icon = "[NO]"
            elif geo_value == "MX":
                stats["mx"] += 1
                icon = "[MX]"
            elif geo_value == "GLOBAL":
                stats["global"] += 1
                icon = "[GL]"
            else:
                stats["unknown"] += 1
                icon = "[??]"

            title = str(job.get("Role", job.get("Title", "??")))[:45]
            conf  = f"{geo['confidence']:.0%}"
            print(f"    {icon} [{conf}] r{row} {title}")
            print(f"         -> {geo['reason'][:75]}")

        except Exception as e:
            stats["errors"] += 1
            print(f"    [ERR] r{row}: {e}")

        # Rate limit (30 writes/min max)
        time.sleep(0.5)

    return stats


def _paint_row_grey(sm: SheetManager, tab_key: str, row_num: int):
    """Pinta toda la fila de gris para indicar US_ONLY."""
    sheet_id = sm._get_sheet_id(sm.tabs.get(tab_key, tab_key))
    requests_body = [{
        "repeatCell": {
            "range": {
                "sheetId":       sheet_id,
                "startRowIndex": row_num - 1,
                "endRowIndex":   row_num,
                "startColumnIndex": 0,
                "endColumnIndex": 26,
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": GREY_COLOR
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    }]
    sm.service.spreadsheets().batchUpdate(
        spreadsheetId=sm.spreadsheet_id,
        body={"requests": requests_body}
    ).execute()


def main():
    parser = argparse.ArgumentParser(description="Geo-filter de ofertas remotas")
    parser.add_argument("--tab",            help="Procesar solo este tab (ej: LinkedIn)")
    parser.add_argument("--rerun-all",      action="store_true", help="Re-chequear incluso si ya tiene GeoOK")
    parser.add_argument("--rerun-unknown",  action="store_true", help="Re-chequear solo los clasificados como UNKNOWN (con fetch)")
    parser.add_argument("--no-fetch",       action="store_true", help="Solo analizar texto sin descargar URLs")
    args = parser.parse_args()

    fetch_url      = not args.no_fetch
    rerun          = args.rerun_all
    rerun_unknown  = args.rerun_unknown

    print()
    print("=" * 60)
    print("  GEO CHECKER — Filtro de elegibilidad geografica")
    print("  Marcos: Guadalajara MX | Visa turista USA | No work auth")
    print("=" * 60)
    if not fetch_url:
        print("  Modo: solo texto (--no-fetch)")
    if rerun_unknown:
        print("  Modo: re-analizar UNKNOWN con fetch de URL")
    print()

    sm = SheetManager()
    total_stats = {"total": 0, "skipped": 0, "global": 0, "mx": 0,
                   "unknown": 0, "us_only": 0, "errors": 0}

    tabs_to_process = {}
    if args.tab:
        if args.tab in ACTIVE_TABS:
            tabs_to_process = {args.tab: ACTIVE_TABS[args.tab]}
        else:
            print(f"Tab '{args.tab}' no reconocido. Opciones: {list(ACTIVE_TABS.keys())}")
            sys.exit(1)
    else:
        tabs_to_process = ACTIVE_TABS

    for tab_name, tab_key in tabs_to_process.items():
        print(f"\n[{tab_name}]")
        stats = process_tab(sm, tab_key, tab_name, rerun=rerun, fetch_url=fetch_url, rerun_unknown=rerun_unknown)

        for k in total_stats:
            total_stats[k] += stats[k]

        processed = stats["total"] - stats["skipped"]
        print(f"  Total: {stats['total']} | Procesados: {processed} | "
              f"Skipped: {stats['skipped']} | Errores: {stats['errors']}")
        print(f"  -> Global: {stats['global']} | MX: {stats['mx']} | "
              f"Unknown: {stats['unknown']} | US_ONLY: {stats['us_only']} [pintados gris]")

    print()
    print("=" * 60)
    print("  RESUMEN FINAL")
    print("=" * 60)
    elegibles = total_stats["global"] + total_stats["mx"] + total_stats["unknown"]
    print(f"  Elegibles: {elegibles} (Global:{total_stats['global']} + MX:{total_stats['mx']} + Unknown:{total_stats['unknown']})")
    print(f"  Descartados US_ONLY: {total_stats['us_only']} [pintados en gris]")
    print(f"  Errores: {total_stats['errors']}")
    print()


if __name__ == "__main__":
    main()
