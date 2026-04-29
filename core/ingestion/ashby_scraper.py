"""
ashby_scraper.py
================
Scraper de vacantes en empresas que usan Ashby ATS.
API pública: https://api.ashbyhq.com/posting-api/job-board/{company}

NO modifica código existente — agrega una nueva fuente al pipeline.
Integración: usar desde scripts/scrape_greenhouse_ashby.py

Uso:
    from core.ingestion.ashby_scraper import scrape_ashby
    jobs = scrape_ashby(["retool", "replit", "cursor"])
"""

import requests
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

ASHBY_API = "https://api.ashbyhq.com/posting-api/job-board/{company}"

# Empresas tech conocidas con Ashby ATS
DEFAULT_COMPANIES = [
    "retool", "replit", "cursor", "perplexity", "together",
    "anyscale", "modal", "cartesia", "langchain", "llamaindex",
    "weaviate", "qdrant", "pinecone", "chroma",
]

PM_KEYWORDS = [
    "product manager", "product owner", "business analyst",
    "technical program", "program manager", "ai product",
    "ml product", "data product", "growth",
]


def scrape_ashby(companies: list[str] = None, keywords: list[str] = None) -> list[dict]:
    """
    Descarga vacantes de empresas en Ashby ATS.

    Args:
        companies: lista de slugs de empresa
        keywords: palabras clave para filtrar por título

    Returns:
        lista de dicts con formato compatible con ai-job-foundry pipeline
    """
    companies = companies or DEFAULT_COMPANIES
    keywords  = keywords  or PM_KEYWORDS
    results   = []

    for company in companies:
        try:
            url  = ASHBY_API.format(company=company)
            resp = requests.get(
                url, timeout=15,
                headers={"User-Agent": "Mozilla/5.0"},
                params={"includeCompensation": "true"},
            )
            if resp.status_code == 404:
                log.debug(f"Ashby: {company} no encontrado")
                continue
            if resp.status_code != 200:
                log.warning(f"Ashby {company}: HTTP {resp.status_code}")
                continue

            data = resp.json()
            jobs = data.get("jobs", [])
            log.info(f"Ashby {company}: {len(jobs)} vacantes totales")

            for job in jobs:
                title = job.get("title", "").lower()
                if not any(kw in title for kw in keywords):
                    continue

                # Extraer localización
                location = job.get("location", "") or ""
                if isinstance(location, dict):
                    location = location.get("name", "")

                # Compensación si está disponible
                comp = ""
                if job.get("compensation"):
                    c = job["compensation"]
                    comp = f"{c.get('min', '')} - {c.get('max', '')} {c.get('currency', 'USD')}"

                results.append({
                    "title":        job.get("title", ""),
                    "company":      company.capitalize(),
                    "location":     location,
                    "url":          job.get("jobUrl", "") or f"https://jobs.ashbyhq.com/{company}/{job.get('id', '')}",
                    "source":       "ashby",
                    "job_id":       str(job.get("id", "")),
                    "posted_at":    job.get("publishedAt", datetime.now().isoformat()),
                    "description":  job.get("descriptionPlain", "")[:500],
                    "compensation": comp,
                })

            count = sum(1 for r in results if r["company"] == company.capitalize())
            log.info(f"Ashby {company}: {count} relevantes")

        except Exception as e:
            log.warning(f"Ashby {company} error: {e}")

    log.info(f"Ashby total: {len(results)} vacantes relevantes de {len(companies)} empresas")
    return results
