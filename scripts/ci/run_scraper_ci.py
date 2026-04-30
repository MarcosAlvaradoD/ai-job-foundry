#!/usr/bin/env python3
"""
CI Runner — LinkedIn Scraper para GitHub Actions
=================================================
Wrapper que adapta linkedin_search_scraper_v3.py para correr en CI:
  - Fuerza headless=True (no hay display en el servidor)
  - Lee SCRAPER_MODE del entorno (live | dry-run)
  - Guarda log en logs/scraper_YYYYMMDD.log
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

# ── Importar y correr el scraper ───────────────────────────────────────────────
def main():
    mode = os.environ.get("SCRAPER_MODE", "live").lower().strip()
    dry_run = (mode == "dry-run")

    log.info("=" * 60)
    log.info("LinkedIn Scraper — GitHub Actions CI")
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

    # Importar scraper y correr
    try:
        from core.ingestion.linkedin_search_scraper_v3 import LinkedInSearchScraper

        async def run():
            scraper = LinkedInSearchScraper(headless=True)
            jobs = await scraper.run(dry_run=dry_run)
            return jobs

        jobs = asyncio.run(run())

        log.info("=" * 60)
        log.info(f"RESULTADO: {len(jobs)} jobs encontrados")
        if not dry_run:
            log.info("Jobs guardados en pestaña Staging de Google Sheets")
        log.info("=" * 60)

        # Exit code 0 = éxito
        sys.exit(0)

    except ImportError as e:
        log.error(f"Import error: {e}")
        log.error("Verifica que el scraper v3 tiene el constructor headless=True")
        sys.exit(1)
    except Exception as e:
        log.error(f"Scraper error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
