"""
greenhouse_scraper.py
=====================
Scraper de vacantes en empresas que usan Greenhouse ATS.
API pública: https://boards-api.greenhouse.io/v1/boards/{company}/jobs

NO modifica código existente — agrega una nueva fuente al pipeline.
Integración: usar desde scripts/scrape_greenhouse_ashby.py

Uso:
    from core.ingestion.greenhouse_scraper import scrape_greenhouse
    jobs = scrape_greenhouse(["stripe", "airbnb", "figma"])
"""

import requests
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"

# Empresas tech conocidas con Greenhouse (ajustar según tu búsqueda)
DEFAULT_COMPANIES = [
    "stripe", "airbnb", "figma", "notion", "linear",
    "vercel", "supabase", "planetscale", "neon", "anthropic",
    "openai", "databricks", "huggingface", "mistral", "cohere",
]

# Palabras clave relevantes para PM/BA con AI skills
PM_KEYWORDS = [
    "product manager", "product owner", "business analyst",
    "technical program", "program manager", "ai product",
    "ml product", "data product", "growth",
]


def scrape_greenhouse(companies: list[str] = None, keywords: list[str] = None) -> list[dict]:
    """
    Descarga vacantes de empresas en Greenhouse ATS.

    Args:
        companies: lista de slugs de empresa (ej: ["stripe", "airbnb"])
        keywords: palabras clave para filtrar por título

    Returns:
        lista de dicts con formato compatible con ai-job-foundry pipeline
    """
    companies = companies or DEFAULT_COMPANIES
    keywords  = keywords  or PM_KEYWORDS
    results   = []

    for company in companies:
        try:
            url  = GREENHOUSE_API.format(company=company)
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 404:
                log.debug(f"Greenhouse: {company} no encontrado")
                continue
            if resp.status_code != 200:
                log.warning(f"Greenhouse {company}: HTTP {resp.status_code}")
                continue

            data = resp.json()
            jobs = data.get("jobs", [])
            log.info(f"Greenhouse {company}: {len(jobs)} vacantes totales")

            for job in jobs:
                title = job.get("title", "").lower()
                if not any(kw in title for kw in keywords):
                    continue

                location = ""
                for loc in job.get("offices", []):
                    location = loc.get("name", "")
                    break

                results.append({
                    "title":       job.get("title", ""),
                    "company":     company.capitalize(),
                    "location":    location,
                    "url":         job.get("absolute_url", ""),
                    "source":      "greenhouse",
                    "job_id":      str(job.get("id", "")),
                    "posted_at":   job.get("updated_at", datetime.now().isoformat()),
                    "description": _extract_description(job),
                })

            log.info(f"Greenhouse {company}: {sum(1 for r in results if r['company'] == company.capitalize())} relevantes")

        except Exception as e:
            log.warning(f"Greenhouse {company} error: {e}")

    log.info(f"Greenhouse total: {len(results)} vacantes relevantes de {len(companies)} empresas")
    return results


def _extract_description(job: dict) -> str:
    """Extrae descripción limpia del job."""
    content = job.get("content", "") or ""
    # Remover HTML básico
    import re
    clean = re.sub(r"<[^>]+>", " ", content)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]


def get_greenhouse_companies_for_sector(sector: str = "ai") -> list[str]:
    """
    Retorna lista de empresas por sector.
    Útil para búsquedas dirigidas.
    """
    sectors = {
        "ai": [
            "anthropic", "openai", "cohere", "mistral", "huggingface",
            "databricks", "scale-ai", "weights-biases", "modal",
        ],
        "saas": [
            "stripe", "figma", "notion", "linear", "vercel",
            "supabase", "loom", "miro", "airtable",
        ],
        "latam_tech": [
            "clip-mx", "conekta", "kueski", "kavak",
            "rappi", "credijusto",
        ],
    }
    return sectors.get(sector, [])
