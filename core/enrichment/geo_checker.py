# -*- coding: utf-8 -*-
"""
geo_checker.py — Verificador de elegibilidad geografica para ofertas remotas
=============================================================================
Marcos esta en Guadalajara, Mexico con visa turista USA (no de trabajo).

Reglas:
  GLOBAL  -> OK  — remoto para cualquier pais, o mencion expresa de LATAM/MX
  MX      -> OK  — remoto dentro de Mexico
  US_ONLY -> NO  — requiere estar/residir en USA
  UNKNOWN -> OK  — no se encontro restriccion, asumir global

El checker hace 2 cosas:
  1. Analiza el texto del job ya guardado en el sheet (rapido, sin fetch)
  2. Si la URL esta disponible, hace fetch y analiza el texto completo

Uso:
  from core.enrichment.geo_checker import check_geo_eligibility
  result = check_geo_eligibility(job_row)
  # result: { "geo": "GLOBAL|MX|US_ONLY|UNKNOWN", "eligible": True|False,
  #           "reason": "...", "confidence": 0-1 }
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

# ── Patterns ──────────────────────────────────────────────────────────────────

# Indica que es US-Only o requiere presencia en USA
US_ONLY_PATTERNS = [
    r"\bU\.?S\.?\s*only\b",
    r"\bunited states only\b",
    r"\bmust be (located|based|residing|resident) in (the )?u\.?s\.?",
    r"\bmust (live|reside|work) in (the )?u\.?s\.?a?\.?\b",
    r"\bauthorized to work in (the )?u\.?s\.?",
    r"\bwork authorization (in|for) (the )?u\.?s",
    r"\bu\.?s\.?\s+work (visa|permit|authorization)",
    r"\blegally authorized to work in (the )?united states",
    r"\bonly (hire|considering|accepting).*(us|u\.s\.|united states)",
    r"\blocated in (the )?(united states|usa|u\.s\.a?)\b",
    r"\bmust have (us|u\.s\.) citizenship",
    r"\bsociedad?\s*(de)?\s*riesgo.*(usa|estados unidos)",  # visa sponsorship denial
    r"\bcannot (sponsor|provide) (visa|work authorization)",
    r"\bno visa sponsorship",
    r"\bnot eligible.*(outside|international)",
    r"\bdomestic (only|candidates)",
]

# Indica que es explicitamente global o acepta LATAM/Mexico
GLOBAL_PATTERNS = [
    r"\bremote.*(worldwide|world.?wide|global|anywhere|any.?where|all countries)",
    r"\b(worldwide|global|anywhere|international)\s+remote",
    r"\bopen to (candidates|applicants) (from )?anywhere",
    r"\bwork from anywhere",
    r"\blocated anywhere",
    r"\blatam\b",
    r"\blatin america\b",
    r"\bmexico\b",
    r"\bm[eé]xico\b",
    r"\bgdl\b",
    r"\bguadalajara\b",
    r"\bremote.*(latam|latin)",
    r"\blatam.*(remote|position|role|job)",
    r"\bhiring (in|from) (multiple|all) (countries|locations|regions)",
    r"\b(open|available) (to |for )?(all|international|global) (candidates|applicants)",
]

# Indica Mexico especificamente
MX_PATTERNS = [
    r"\bm[eé]xico\b",
    r"\bmexican candidates\b",
    r"\bguadalajara\b",
    r"\bcdmx\b",
    r"\bciudad de m[eé]xico\b",
    r"\bremoto en m[eé]xico\b",
]


def _clean_text(text: str) -> str:
    """Normaliza texto para busqueda de patrones."""
    return " ".join(text.lower().split())


def _score_text(text: str) -> dict:
    """
    Analiza el texto y devuelve scores para cada categoria.
    Returns: {"us_only": int, "global": int, "mx": int}
    """
    t = _clean_text(text)
    us_hits   = sum(1 for p in US_ONLY_PATTERNS if re.search(p, t, re.IGNORECASE))
    global_hits = sum(1 for p in GLOBAL_PATTERNS if re.search(p, t, re.IGNORECASE))
    mx_hits   = sum(1 for p in MX_PATTERNS if re.search(p, t, re.IGNORECASE))
    return {"us_only": us_hits, "global": global_hits, "mx": mx_hits}


def _decide(scores: dict, source: str = "") -> dict:
    """Convierte scores en decision final."""
    us  = scores["us_only"]
    gl  = scores["global"]
    mx  = scores["mx"]

    if us > 0 and gl == 0 and mx == 0:
        return {
            "geo": "US_ONLY",
            "eligible": False,
            "reason": f"Restriccion USA detectada ({us} indicadores). No aplica con visa turista.",
            "confidence": min(0.9, 0.5 + us * 0.2),
        }
    if us > 0 and (gl > 0 or mx > 0):
        # Hay senales mixtas — probable US Only pero con mencion de otros paises
        return {
            "geo": "US_ONLY",
            "eligible": False,
            "reason": f"Indicadores mixtos: {us} restricciones USA vs {gl} global. Se asume US Only por seguridad.",
            "confidence": 0.6,
        }
    if mx > 0:
        return {
            "geo": "MX",
            "eligible": True,
            "reason": f"Menciona Mexico/Guadalajara ({mx} refs). Elegible.",
            "confidence": min(0.95, 0.6 + mx * 0.15),
        }
    if gl > 0:
        return {
            "geo": "GLOBAL",
            "eligible": True,
            "reason": f"Remoto global confirmado ({gl} indicadores). Elegible.",
            "confidence": min(0.95, 0.5 + gl * 0.15),
        }
    # Sin senales claras
    return {
        "geo": "UNKNOWN",
        "eligible": True,   # beneficio de la duda
        "reason": "Sin restricciones geograficas explicitas detectadas. Asumido global.",
        "confidence": 0.4,
    }


# ── Fetch page text ────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

def _fetch_job_text(url: str, timeout: int = 10) -> Optional[str]:
    """Descarga la pagina de la oferta y extrae el texto relevante."""
    if not url or not url.startswith("http"):
        return None
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Priorizar elementos de descripcion
        for sel in [
            "[class*='description']", "[class*='job-detail']", "[class*='jobDescriptionText']",
            "[class*='show-more-less']", "article", "main", ".job-description",
        ]:
            el = soup.select_one(sel)
            if el and len(el.get_text()) > 100:
                return el.get_text(" ", strip=True)[:5000]
        return soup.get_text(" ", strip=True)[:5000]
    except Exception:
        return None


# ── Main public function ───────────────────────────────────────────────────────

def check_geo_eligibility(
    job: dict,
    fetch_url: bool = True,
    delay: float = 1.0,
) -> dict:
    """
    Verifica si una oferta es elegible para Marcos (Guadalajara, MX, sin work auth USA).

    Args:
        job:       Dict del row del sheet (necesita al menos 'ApplyURL' o texto de la oferta)
        fetch_url: Si True, intenta descargar la URL para analisis mas profundo
        delay:     Segundos de pausa antes del fetch (rate limit)

    Returns:
        {
          "geo":        "GLOBAL" | "MX" | "US_ONLY" | "UNKNOWN",
          "eligible":   True | False,
          "reason":     "explicacion",
          "confidence": 0.0 - 1.0,
          "source":     "text" | "url" | "combined"
        }
    """
    # 1. Construir texto base de campos ya disponibles en el sheet
    base_text = " ".join([
        str(job.get("Title", "")),
        str(job.get("Role", "")),
        str(job.get("Company", "")),
        str(job.get("Location", "")),
        str(job.get("Description", "")),
        str(job.get("Why", "")),         # campo del ai_analyzer
        str(job.get("Tienes", "")),
        str(job.get("Faltan", "")),
    ])
    base_scores = _score_text(base_text)

    # Si ya hay señal fuerte solo con el texto del sheet, no hace falta fetch
    if base_scores["us_only"] >= 2 or base_scores["global"] >= 2:
        result = _decide(base_scores, "text")
        result["source"] = "text"
        return result

    # 2. Fetch URL para analisis mas completo
    url = str(job.get("ApplyURL", "") or job.get("URL", "") or "")
    page_text = None
    if fetch_url and url:
        time.sleep(delay)
        page_text = _fetch_job_text(url)

    if page_text:
        combined_text = base_text + " " + page_text
        combined_scores = _score_text(combined_text)
        result = _decide(combined_scores, "combined")
        result["source"] = "combined"
    else:
        result = _decide(base_scores, "text")
        result["source"] = "text"

    return result


# ── Batch processor ───────────────────────────────────────────────────────────

def batch_check_geo(jobs: list, fetch_url: bool = True, delay: float = 1.5) -> list:
    """
    Verifica elegibilidad geografica para una lista de jobs.
    Retorna la misma lista con campo '_geo' agregado.
    """
    results = []
    for job in jobs:
        try:
            geo = check_geo_eligibility(job, fetch_url=fetch_url, delay=delay)
        except Exception as e:
            geo = {
                "geo": "UNKNOWN", "eligible": True,
                "reason": f"Error en verificacion: {e}", "confidence": 0.0,
                "source": "error"
            }
        job["_geo"] = geo
        results.append(job)
    return results


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        {"Title": "Senior PM", "Location": "Remote - USA Only",
         "Description": "Must be authorized to work in the US. No visa sponsorship."},
        {"Title": "IT Project Manager", "Location": "Remote LATAM",
         "Description": "We are hiring across Latin America including Mexico."},
        {"Title": "Business Analyst", "Location": "Remote",
         "Description": "100% remote, work from anywhere in the world."},
        {"Title": "PM Senior", "Location": "Remote",
         "Description": "Join our team remotely."},
    ]
    for tc in test_cases:
        r = check_geo_eligibility(tc, fetch_url=False)
        icon = "[OK]" if r["eligible"] else "[NO]"
        print(f"{icon} {tc['Title']} | {r['geo']} | conf:{r['confidence']:.0%} | {r['reason'][:60]}")
