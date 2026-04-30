"""
AI JOB FOUNDRY - Definiciones centrales de búsqueda
====================================================
Todas las queries usadas por LinkedIn, Indeed y Computrabajo.
QuerySource:
  "Mark"   = query definida por Marcos (criterio original del usuario)
  "Claude" = query sugerida/optimizada por Claude (criterio estratégico)

Al final el FIT score, las ofertas y las entrevistas dirán quién gana.
"""

# ── Queries en inglés — plataformas internacionales (LinkedIn, Indeed) ──────
# Formato: (query_text, source, track)
# track: "mexico" = con filtro geográfico MX | "latam" = keyword ya incluye región

QUERIES_EN = [
    # Mark's original queries
    ("SAP Project Manager",              "Mark",   "mexico"),
    ("ERP Implementation Manager",       "Mark",   "mexico"),
    ("IT Manager",                       "Mark",   "mexico"),
    ("IT Business Partner",              "Mark",   "mexico"),
    ("Program Manager",                  "Mark",   "mexico"),
    # Claude's strategic additions
    ("Digital Transformation Manager",   "Claude", "mexico"),
    ("Technology Consulting Manager",    "Claude", "mexico"),
    ("AI Project Manager",               "Claude", "mexico"),
    ("Technology Program Manager",       "Claude", "mexico"),
    ("Business Process Manager",         "Claude", "mexico"),
    ("Enterprise Solutions Manager",     "Claude", "mexico"),
    # LATAM/remote keyword tracks
    ("IT Manager LATAM remote",          "Mark",   "latam"),
    ("Program Manager LATAM remote",     "Mark",   "latam"),
    ("SAP Consultant LATAM remote",      "Claude", "latam"),
    ("Digital Transformation LATAM",     "Claude", "latam"),
    ("ERP Project Manager remote LATAM", "Claude", "latam"),
]

# ── Queries en español — Computrabajo MX ─────────────────────────────────────
QUERIES_ES = [
    # Mark's equivalents in Spanish
    ("Gerente de Proyectos SAP",         "Mark",   "mexico"),
    ("Gerente de TI",                    "Mark",   "mexico"),
    ("IT Business Partner",              "Mark",   "mexico"),
    ("Director de Proyectos ERP",        "Mark",   "mexico"),
    # Claude's strategic Spanish additions
    ("Gerente de Transformación Digital","Claude", "mexico"),
    ("Consultor SAP Senior",             "Claude", "mexico"),
    ("Gerente de Tecnología",            "Claude", "mexico"),
    ("Program Manager TI",               "Claude", "mexico"),
    ("Director de Proyectos TI",         "Claude", "mexico"),
    ("Gerente de Implementación ERP",    "Claude", "mexico"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_mexico_queries(lang: str = "en") -> list[tuple]:
    """Returns queries for Mexico geo filter."""
    pool = QUERIES_EN if lang == "en" else QUERIES_ES
    return [(q, src) for q, src, track in pool if track == "mexico"]

def get_latam_queries(lang: str = "en") -> list[tuple]:
    """Returns LATAM/global keyword queries (no geo filter needed)."""
    pool = QUERIES_EN if lang == "en" else QUERIES_ES
    return [(q, src) for q, src, track in pool if track == "latam"]

def get_all_queries(lang: str = "en") -> list[tuple]:
    """Returns all queries as (query_text, source) tuples."""
    pool = QUERIES_EN if lang == "en" else QUERIES_ES
    return [(q, src) for q, src, track in pool]
