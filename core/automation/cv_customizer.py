"""
cv_customizer.py — Integración CV personalizado por vacante
===========================================================
Módulo thin que conecta cv_generator.py con el pipeline de auto-apply.

Lógica:
  - FIT >= 8  → CV personalizado con keywords del JD (con cache por job_id)
  - FIT 7     → CV base (CV_Marcos_Alvarado_2026.pdf)
  - FIT < 7   → No debería llegar aquí (autoapply ya filtra por min_fit=7)

Cache:
  - data/cv/generated/{job_id}.pdf
  - Si ya existe → retorna inmediatamente sin llamar a LLM ni Playwright
  - Cache manual: borra el archivo para forzar regeneración

Uso:
  from core.automation.cv_customizer import get_cv_for_job

  # job dict con claves: job_id/ID, FitScore, Company, Role, Description
  cv_path = get_cv_for_job(job)
  # → Path al PDF a usar para esta aplicación
"""

import json
import logging
import re
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
_ROOT      = Path(__file__).parent.parent.parent.resolve()
_BASE_CV   = _ROOT / "data" / "cv" / "CV_Marcos_Alvarado_2026.pdf"
_CACHE_DIR = _ROOT / "data" / "cv" / "generated"

sys.path.insert(0, str(_ROOT))

log = logging.getLogger("cv_customizer")

# ── Lazy imports (evita cargar Playwright/requests si no se necesitan) ─────────
_profile_cache: dict | None = None
_salary_cache:  dict | None = None


def _get_profile_and_salary():
    global _profile_cache, _salary_cache
    if _profile_cache is None:
        from scripts.apply.cv_generator import load_profile, calculate_salary
        _profile_cache = load_profile()
        _salary_cache  = calculate_salary(_profile_cache)
    return _profile_cache, _salary_cache


def _tailor_with_multibackend(profile: dict, job: dict) -> dict:
    """
    Personaliza summary y skills usando AI multi-backend LOCAL-FIRST.
    Retorna dict con 'summary' y 'skills_highlight', o {} si falla.
    """
    try:
        # Importar _call_llm (local-first: LM Studio → Gemini → NVIDIA NIM)
        from core.automation.auto_apply_external import _call_llm

        company = job.get("Company", job.get("company", "la empresa"))
        role    = job.get("Role",    job.get("role",    "el puesto"))
        desc    = (job.get("Description", job.get("description", "")) or "")[:800]
        fit     = job.get("FitScore", job.get("fit", ""))

        skills_mgmt = profile.get("skills", {}).get("management", [])
        skills_tech = profile.get("skills", {}).get("technical",  [])
        all_skills  = skills_mgmt + skills_tech

        prompt = f"""Eres un experto en CVs para búsqueda de empleo en LATAM/USA.
Personaliza el perfil de Marcos para esta vacante específica.

VACANTE:
- Empresa: {company}
- Puesto: {role}
- FIT Score: {fit}/10
- Descripción: {desc or "No disponible"}

SUMMARY ACTUAL:
{profile.get("summary", "")}

SKILLS DISPONIBLES:
{json.dumps(all_skills[:30], ensure_ascii=False)}

TAREA: Retorna EXACTAMENTE un JSON con dos campos:
1. "summary": versión personalizada (max 3 frases, resaltando lo más relevante para ESTE puesto, en inglés)
2. "skills_highlight": lista de 8-10 skills más relevantes para este puesto (SOLO del listado disponible, sin inventar)

Responde SOLO el JSON, sin texto adicional:
{{"summary": "...", "skills_highlight": ["skill1", "skill2"]}}"""

        raw = _call_llm(prompt, max_tokens=500)
        if not raw:
            return {}

        # Extraer JSON de la respuesta
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            log.warning("[CV] AI no retornó JSON válido — usando perfil base")
            return {}

        tailored = json.loads(json_match.group())
        log.info(f"[CV] ✓ Personalizado: summary={len(tailored.get('summary',''))} chars, "
                 f"skills={len(tailored.get('skills_highlight',[]))}")
        return tailored

    except Exception as e:
        log.warning(f"[CV] Tailor error: {e} — usando perfil base")
        return {}


def _generate_custom_cv(job: dict, output_path: Path) -> bool:
    """
    Genera PDF personalizado para el job.
    Retorna True si OK, False si falla (en ese caso usar CV base).
    """
    try:
        from scripts.apply.cv_generator import build_html, generate_pdf

        profile, salary = _get_profile_and_salary()
        tailored = _tailor_with_multibackend(profile, job)
        html     = build_html(profile, job, tailored, salary)

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        ok = generate_pdf(html, output_path)
        return ok

    except Exception as e:
        log.error(f"[CV] Error generando PDF: {e}")
        return False


def get_cv_for_job(job: dict, fit_threshold: float = 8.0) -> Path:
    """
    Retorna la Path al CV PDF a usar para esta solicitud.

    Args:
        job: dict con claves Company/company, Role/role, FitScore/fit,
             Description/description, y job_id / ID / _row como clave de cache
        fit_threshold: FIT mínimo para generar CV personalizado (default 8.0)

    Returns:
        Path al PDF existente (nunca None — fallback a CV base si algo falla)
    """
    # ── Resolver FIT score ──────────────────────────────────────────────────
    try:
        fit = float(str(job.get("FitScore", job.get("fit", 0))).split("/")[0])
    except (ValueError, TypeError):
        fit = 0.0

    # ── FIT < threshold → CV base ───────────────────────────────────────────
    if fit < fit_threshold:
        log.info(f"[CV] FIT {fit:.1f} < {fit_threshold} → CV base")
        return _BASE_CV if _BASE_CV.exists() else Path(str(_BASE_CV))

    # ── Resolver job_id para cache ──────────────────────────────────────────
    job_id = str(
        job.get("job_id") or
        job.get("ID")     or
        job.get("Job_ID") or
        job.get("_row")   or
        "unknown"
    ).strip()

    # Extraer ID numérico de URL de LinkedIn si está en ApplyURL
    if job_id in ("unknown", "0", "") and job.get("ApplyURL"):
        m = re.search(r'/jobs/view/(\d+)', job.get("ApplyURL", ""))
        if m:
            job_id = m.group(1)

    company = re.sub(r"[^\w]", "", str(job.get("Company", job.get("company", "co"))).replace(" ", "_"))[:20]
    role    = re.sub(r"[^\w]", "", str(job.get("Role",    job.get("role",    "pm"))).replace(" ", "_"))[:15]
    cache_name = f"{job_id}_{company}_{role}.pdf"
    cache_path = _CACHE_DIR / cache_name

    # ── Cache hit → retornar inmediatamente ────────────────────────────────
    if cache_path.exists():
        log.info(f"[CV] Cache hit → {cache_path.name}")
        return cache_path

    # ── Cache miss → generar CV personalizado ──────────────────────────────
    log.info(f"[CV] FIT {fit:.1f} >= {fit_threshold} → generando CV personalizado para "
             f"{job.get('Company', '?')} — {job.get('Role', '?')}")

    ok = _generate_custom_cv(job, cache_path)
    if ok and cache_path.exists():
        log.info(f"[CV] ✓ CV generado: {cache_path.name} ({cache_path.stat().st_size // 1024}KB)")
        return cache_path

    # ── Fallback a CV base si algo falló ───────────────────────────────────
    log.warning("[CV] Generación falló — usando CV base como fallback")
    return _BASE_CV


def clear_cv_cache(job_id: str | None = None):
    """
    Limpia el cache de CVs generados.
    Si job_id es None, borra todos. Útil al actualizar el CV base.
    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if job_id:
        for f in _CACHE_DIR.glob(f"{job_id}_*.pdf"):
            f.unlink()
            log.info(f"[CV] Cache borrado: {f.name}")
    else:
        count = 0
        for f in _CACHE_DIR.glob("*.pdf"):
            f.unlink()
            count += 1
        log.info(f"[CV] Cache limpiado: {count} archivos borrados")


if __name__ == "__main__":
    # Test rápido
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    test_job = {
        "job_id":      "test_4404879580",
        "Company":     "Murmuration",
        "Role":        "Senior Project Manager",
        "FitScore":    8.5,
        "Description": (
            "Senior PM for civic tech campaigns. ERP, SAP, Agile, stakeholder management, "
            "Salesforce, EveryAction, 501c3 nonprofits, remote team leadership."
        ),
        "ApplyURL":    "https://murmuration.workable.com/j/test",
    }

    cv = get_cv_for_job(test_job)
    print(f"\n✅ CV seleccionado: {cv}")
    print(f"   Existe: {cv.exists()}")
    print(f"   Tamaño: {cv.stat().st_size // 1024 if cv.exists() else 'N/A'} KB")
