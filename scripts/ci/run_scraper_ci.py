#!/usr/bin/env python3
"""
CI Runner — Multi-Source Scraper para GitHub Actions CI
========================================================
Corre los 3 scrapers en secuencia: LinkedIn → Indeed → Computrabajo.
  - Fuerza headless=True (no hay display en el servidor)
  - Lee SCRAPER_MODE del entorno (live | dry-run)
  - Guarda log en logs/scraper_YYYYMMDD_HHMMSS.log
  - Imprime resumen al final para el log de GitHub Actions

Uso (automático vía workflow):
  python scripts/ci/run_scraper_ci.py
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# ── Logging a archivo + stdout ─────────────────────────────────────────────────
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── Forzar headless en CI ──────────────────────────────────────────────────────
os.environ["PLAYWRIGHT_HEADLESS"] = "true"
# PROJECT_ROOT debe apuntar al workspace de GitHub Actions
os.environ.setdefault("PROJECT_ROOT", str(ROOT))


def main():
    mode = os.environ.get("SCRAPER_MODE", "live").lower().strip()
    dry_run = (mode == "dry-run")

    log.info("=" * 60)
    log.info("AI Job Foundry — Multi-Source Scraper CI")
    log.info(f"Mode    : {'DRY-RUN' if dry_run else 'LIVE'}")
    log.info(f"Root    : {ROOT}")
    log.info(f"Log     : {log_file}")
    log.info(f"Date    : {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    log.info("=" * 60)

    # Verificar que los archivos de credenciales existen
    creds = [
        ROOT / "data" / "credentials" / "linkedin_auth.json",
        ROOT / "data" / "credentials" / "credentials.json",
        ROOT / "data" / "credentials" / "token.json",
    ]
    missing = [str(c) for c in creds if not c.exists()]
    if missing:
        log.error(f"Missing credentials: {missing}")
        log.error("Check that GitHub Secrets are configured correctly.")
        sys.exit(1)

    log.info("Credentials: OK")

    linkedin_count = 0
    indeed_count = 0
    computrabajo_count = 0
    had_error = False

    # ── 1. LinkedIn ────────────────────────────────────────────────────────────
    log.info("-" * 60)
    log.info("Running LinkedIn scraper...")
    try:
        from core.ingestion.linkedin_search_scraper_v3 import LinkedInSearchScraper

        async def run_linkedin():
            scraper = LinkedInSearchScraper(headless=True)
            await scraper.run(dry_run=dry_run)
            return scraper.jobs_found or []

        jobs = asyncio.run(run_linkedin())
        linkedin_count = len(jobs)
        log.info(f"LinkedIn: {linkedin_count} jobs found")
    except ImportError as e:
        log.error(f"LinkedIn ImportError: {e}")
        had_error = True
    except Exception as e:
        log.error(f"LinkedIn scraper error: {e}", exc_info=True)
        had_error = True

    # ── 2. Indeed ─────────────────────────────────────────────────────────────
    log.info("-" * 60)
    log.info("Running Indeed scraper...")
    try:
        from core.ingestion.indeed_scraper import IndeedScraper

        async def run_indeed():
            scraper = IndeedScraper(headless=True)
            await scraper.run(dry_run=dry_run)
            return scraper.jobs_found or []

        jobs = asyncio.run(run_indeed())
        indeed_count = len(jobs)
        log.info(f"Indeed: {indeed_count} jobs found")
    except ImportError as e:
        log.warning(f"Indeed ImportError (skipping): {e}")
    except Exception as e:
        log.error(f"Indeed scraper error: {e}", exc_info=True)
        had_error = True

    # ── 3. Computrabajo ────────────────────────────────────────────────────────
    log.info("-" * 60)
    log.info("Running Computrabajo scraper...")
    try:
        from core.ingestion.computrabajo_scraper import ComputrabajoScraper

        async def run_computrabajo():
            scraper = ComputrabajoScraper(headless=True)
            await scraper.run(dry_run=dry_run)
            return scraper.jobs_found or []

        jobs = asyncio.run(run_computrabajo())
        computrabajo_count = len(jobs)
        log.info(f"Computrabajo: {computrabajo_count} jobs found")
    except ImportError as e:
        log.warning(f"Computrabajo ImportError (skipping): {e}")
    except Exception as e:
        log.error(f"Computrabajo scraper error: {e}", exc_info=True)
        had_error = True

    # ── Summary ────────────────────────────────────────────────────────────────
    total = linkedin_count + indeed_count + computrabajo_count
    log.info("=" * 60)
    log.info(
        f"RESULTADO: LinkedIn={linkedin_count} | Indeed={indeed_count} "
        f"| Computrabajo={computrabajo_count} | TOTAL={total}"
    )
    if not dry_run:
        log.info("Jobs guardados en pestañas LinkedIn / Indeed / Computrabajo de Google Sheets")
    log.info("=" * 60)

    sys.exit(1 if had_error else 0)


if __name__ == "__main__":
    main()
