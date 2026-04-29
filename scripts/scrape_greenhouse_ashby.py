"""
scrape_greenhouse_ashby.py
==========================
Corre los scrapers de Greenhouse y Ashby, normaliza los resultados
e inserta en Google Sheets usando el pipeline existente.

Uso:
    py scripts/scrape_greenhouse_ashby.py
    py scripts/scrape_greenhouse_ashby.py --dry-run      # no escribe en Sheets
    py scripts/scrape_greenhouse_ashby.py --sector ai    # solo empresas de AI
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ingestion.greenhouse_scraper import scrape_greenhouse, get_greenhouse_companies_for_sector
from core.ingestion.ashby_scraper import scrape_ashby

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)


def normalize_job(job: dict, idx: int) -> dict:
    """Convierte el formato de Greenhouse/Ashby al formato del pipeline existente."""
    return {
        "Row":         None,
        "Date Added":  job.get("posted_at", "")[:10],
        "Company":     job.get("company", ""),
        "Role":        job.get("title", ""),
        "Location":    job.get("location", "Remote"),
        "Job URL":     job.get("url", ""),
        "Source":      job.get("source", "").capitalize(),
        "Status":      "New",
        "Fit Score":   "",
        "Notes":       job.get("compensation", "") or "",
        "Description": job.get("description", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape Greenhouse + Ashby y cargar a Sheets")
    parser.add_argument("--dry-run",  action="store_true", help="No escribe en Sheets")
    parser.add_argument("--sector",   default=None,        help="Sector: ai, saas, latam_tech")
    parser.add_argument("--company",  default=None,        help="Empresa específica (slug)")
    args = parser.parse_args()

    # ── Definir qué empresas buscar ────────────────────────────────────────────
    gh_companies  = None
    ash_companies = None

    if args.sector:
        gh_companies = get_greenhouse_companies_for_sector(args.sector)
        log.info(f"Sector '{args.sector}': {len(gh_companies)} empresas en Greenhouse")
    elif args.company:
        gh_companies  = [args.company]
        ash_companies = [args.company]

    # ── Scraping ───────────────────────────────────────────────────────────────
    log.info("=== Scraping Greenhouse ===")
    gh_jobs = scrape_greenhouse(gh_companies)

    log.info("=== Scraping Ashby ===")
    ash_jobs = scrape_ashby(ash_companies)

    all_jobs = gh_jobs + ash_jobs
    log.info(f"Total: {len(all_jobs)} vacantes ({len(gh_jobs)} GH + {len(ash_jobs)} Ashby)")

    if not all_jobs:
        log.info("Sin vacantes nuevas.")
        return

    # ── Normalizar ─────────────────────────────────────────────────────────────
    normalized = [normalize_job(j, i) for i, j in enumerate(all_jobs)]

    # ── Imprimir preview ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  VACANTES ENCONTRADAS: {len(normalized)}")
    print(f"{'='*60}")
    for j in normalized[:10]:
        print(f"  [{j['Source']}] {j['Company']} — {j['Role']} ({j['Location']})")
        print(f"         {j['Job URL'][:70]}")
    if len(normalized) > 10:
        print(f"  ... y {len(normalized)-10} más")
    print()

    if args.dry_run:
        log.info("--dry-run: no se escribió en Sheets.")
        return

    # ── Insertar en Sheets usando pipeline existente ───────────────────────────
    try:
        from core.sheets.sheet_manager import SheetManager
        sm = SheetManager()

        inserted = 0
        skipped  = 0
        for job in normalized:
            try:
                result = sm.insert_job(job)
                if result:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                log.warning(f"Error insertando {job['Company']}/{job['Role']}: {e}")
                skipped += 1

        log.info(f"Sheets: {inserted} insertadas, {skipped} omitidas (duplicadas o error)")

    except ImportError as e:
        log.error(f"No se pudo importar SheetManager: {e}")
        log.info("Tip: asegúrate de correr desde la raíz del proyecto con credenciales configuradas.")


if __name__ == "__main__":
    main()
