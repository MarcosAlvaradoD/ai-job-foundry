#!/usr/bin/env python3
"""
cv_generator.py — Generador de CV personalizado por vacante
============================================================
Lee el perfil desde data/cv_profile.json, opcionalmente personaliza
el summary y skills para la vacante con LiteLLM local, genera PDF
con Playwright y lo guarda en data/cvs/.

Uso:
  py scripts/apply/cv_generator.py                              # CV base
  py scripts/apply/cv_generator.py --company "Google" --role "PM Senior"
  py scripts/apply/cv_generator.py --tab LinkedIn --min-fit 8  # batch
  py scripts/apply/cv_generator.py --dry-run                   # solo HTML
  py scripts/apply/cv_generator.py --no-tailor                 # sin LiteLLM
  py scripts/apply/cv_generator.py --update-sheet              # escribe path en Notes
"""

import sys
import os
import re
import json
import math
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).parent.parent.parent
PROFILE_FILE = ROOT_DIR / "data" / "cv_profile.json"
TEMPLATE_FILE= ROOT_DIR / "templates" / "cv_marcos.html"
OUTPUT_DIR   = ROOT_DIR / "data" / "cvs"
LOG_FILE     = ROOT_DIR / "data" / "cv_generator.log"

sys.path.insert(0, str(ROOT_DIR))
from dotenv import load_dotenv
load_dotenv()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
LITELLM_URL  = os.getenv("LITELLM_URL",  "http://localhost:4000")
LITELLM_KEY  = os.getenv("LITELLM_KEY",  "sk-1234567890abcdef")
LITELLM_MODEL= os.getenv("LITELLM_MODEL","local-llama")
CHALAN_URL   = os.getenv("CHALAN_URL",   "http://localhost:4001")
SHEET_ID     = os.getenv("GOOGLE_SHEETS_ID")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("cv_generator")


# ─────────────────────────────────────────────────────────────────────────────
# SALARY UTILS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_salary(profile: dict) -> dict:
    """
    Convierte salario mínimo MXN mensual a expectativa USD anual.
    Redondea hacia arriba al siguiente múltiplo de $5,000 USD.

    Ejemplo:
      50,000 MXN/mes → 2,500 USD/mes → 30,000 USD/año → pide $30,000
      Si diera 22,000 USD/año → redondea a $25,000
      Si diera 28,000 USD/año → redondea a $30,000
    """
    sal = profile.get("salary", {})
    mxn_monthly   = float(sal.get("min_mxn_monthly", 50000))
    exchange_rate  = float(sal.get("exchange_rate_mxn_usd", 20.0))

    monthly_usd = mxn_monthly / exchange_rate
    annual_usd  = monthly_usd * 12
    # Round UP to next multiple of 5,000
    ask_usd_annual = int(math.ceil(annual_usd / 5000) * 5000)
    ask_usd_monthly= int(math.ceil(monthly_usd / 500)  * 500)

    return {
        "mxn_monthly":      int(mxn_monthly),
        "usd_monthly":      ask_usd_monthly,
        "usd_annual":       int(annual_usd),
        "usd_annual_ask":   ask_usd_annual,
        "display_mxn":      f"MXN ${mxn_monthly:,.0f}/mes",
        "display_usd":      f"USD ${ask_usd_annual:,}/año (${ask_usd_monthly:,}/mes)",
        "display_mxn_annual": f"MXN ${mxn_monthly * 12:,.0f}/año",
    }


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE LOADER
# ─────────────────────────────────────────────────────────────────────────────

def load_profile() -> dict:
    if not PROFILE_FILE.exists():
        log.error(f"Perfil no encontrado: {PROFILE_FILE}")
        sys.exit(1)
    return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# LiteLLM TAILOR
# ─────────────────────────────────────────────────────────────────────────────

def tailor_with_llm(profile: dict, job: dict) -> dict:
    """
    Llama a LiteLLM para personalizar summary y top skills según la vacante.
    Retorna dict con 'summary' y 'skills_highlight' tailored, o el original si falla.
    """
    try:
        import requests
        company  = job.get("company", "la empresa")
        role     = job.get("role",    "el puesto")
        desc     = job.get("description", "")[:800]
        fit      = job.get("fit", "")

        base_summary = profile.get("summary", "")
        skills_mgmt  = profile.get("skills", {}).get("management", [])
        skills_tech  = profile.get("skills", {}).get("technical",  [])
        all_skills   = skills_mgmt + skills_tech

        prompt = f"""Eres un experto en CVs para LATAM. Personaliza el perfil de Marcos para esta vacante.

VACANTE:
- Empresa: {company}
- Puesto: {role}
- FIT Score: {fit}/10
- Descripción: {desc or "No disponible"}

SUMMARY ACTUAL (2-3 frases):
{base_summary}

SKILLS DISPONIBLES:
{json.dumps(all_skills, ensure_ascii=False)}

TAREA: Retorna EXACTAMENTE un JSON con dos campos:
1. "summary": versión personalizada del summary (max 3 frases, resaltando lo más relevante para ESTE puesto)
2. "skills_highlight": lista de 8-10 skills más relevantes para este puesto (del listado disponible, sin inventar)

Responde SOLO el JSON, sin texto adicional. Ejemplo:
{{"summary": "...", "skills_highlight": ["skill1", "skill2"]}}
"""
        resp = requests.post(
            f"{LITELLM_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LITELLM_KEY}", "Content-Type": "application/json"},
            json={
                "model": LITELLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.3,
            },
            timeout=60,
        )

        if not resp.ok:
            log.warning(f"LiteLLM error {resp.status_code}: {resp.text[:100]}")
            return {}

        raw = resp.json()["choices"][0]["message"]["content"].strip()

        # Extraer JSON de la respuesta (puede venir con texto alrededor)
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            log.warning("LiteLLM no retornó JSON válido — usando perfil base")
            return {}

        tailored = json.loads(json_match.group())
        log.info(f"  [TAILOR] Summary personalizado ({len(tailored.get('summary',''))} chars)")
        return tailored

    except Exception as e:
        log.warning(f"LiteLLM tailor error: {e} — usando perfil base")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# HTML BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def _skill_tags(skills: list[str]) -> str:
    return "".join(f'<span class="skill-tag">{s}</span>' for s in skills)


def _experience_html(experience: list[dict]) -> str:
    parts = []
    for exp in experience:
        start = exp.get("start", "")
        end   = exp.get("end")   or ("Presente" if exp.get("current") else "")

        # Format dates: "2022-06" → "Jun 2022"
        def fmt_date(d: str) -> str:
            if not d or d == "Presente":
                return d
            try:
                dt = datetime.strptime(d, "%Y-%m")
                return dt.strftime("%b %Y")
            except Exception:
                return d

        date_str = f"{fmt_date(start)} – {fmt_date(end) if end else 'Presente'}"
        bullets_html = "".join(f"<li>{b}</li>" for b in exp.get("bullets", []))

        parts.append(f"""
<div class="exp-entry">
  <div class="exp-header">
    <span class="exp-company">{exp.get('company','')}</span>
    <span class="exp-dates">{date_str}</span>
  </div>
  <div class="exp-role">{exp.get('role','')}</div>
  <div class="exp-location">📍 {exp.get('location','')}</div>
  <ul class="exp-bullets">{bullets_html}</ul>
</div>""")

    return "\n".join(parts)


def _education_html(education: list[dict]) -> str:
    parts = []
    for edu in education:
        end = edu.get("end", "")
        end_str = f" · {end}" if end else ""
        parts.append(f"""
<div class="edu-entry">
  <div class="edu-degree">{edu.get('degree','')}</div>
  <div class="edu-institution">{edu.get('institution','')}{end_str}</div>
</div>""")
    return "\n".join(parts)


def _certs_html(certs: list[dict]) -> str:
    parts = []
    for c in certs:
        status = c.get("status", "active")
        if status == "active":
            badge = '<span class="cert-status-active">✓ Activa</span>'
        else:
            badge = '<span class="cert-status-progress">⏳ En curso</span>'
        parts.append(f'<div class="cert-entry"><span class="cert-name">{c["name"]}</span> {badge}</div>')
    return "\n".join(parts)


def _languages_html(languages: list[dict]) -> str:
    return "".join(
        f'<span class="lang-row"><span class="lang-name">{l["lang"]}</span>'
        f' <span class="lang-level">— {l["level"]}</span></span>'
        for l in languages
    )


def build_html(profile: dict, job: dict, tailored: dict, salary: dict) -> str:
    """Rellena el template HTML con los datos del perfil (+ personalización si hay)."""
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    personal = profile["personal"]
    skills   = profile["skills"]

    # Summary: tailored > base
    summary = tailored.get("summary") or profile.get("summary", "")

    # Skills: tailored highlight list o full management + technical
    if tailored.get("skills_highlight"):
        mgmt_tags = _skill_tags(tailored["skills_highlight"][:5])
        tech_tags = _skill_tags(tailored["skills_highlight"][5:])
    else:
        mgmt_tags = _skill_tags(skills.get("management", []))
        tech_tags = _skill_tags(skills.get("technical",  []))

    # Tailored badge
    tailored_badge = ""
    if tailored and job.get("company"):
        tailored_badge = f'<span class="tailored-badge">✓ Personalizado para {job.get("company","")}</span>'

    replacements = {
        "{{NAME}}":               personal.get("name", ""),
        "{{HEADLINE}}":           profile.get("headline", ""),
        "{{EMAIL}}":              personal.get("email", ""),
        "{{PHONE}}":              personal.get("phone", ""),
        "{{LOCATION}}":           personal.get("location", ""),
        "{{LINKEDIN}}":           personal.get("linkedin", ""),
        "{{SUMMARY}}":            summary,
        "{{SKILLS_MANAGEMENT}}":  mgmt_tags,
        "{{SKILLS_TECHNICAL}}":   tech_tags,
        "{{EXPERIENCE_HTML}}":    _experience_html(profile.get("experience", [])),
        "{{EDUCATION_HTML}}":     _education_html(profile.get("education",  [])),
        "{{CERTS_HTML}}":         _certs_html(profile.get("certifications", [])),
        "{{LANGUAGES_HTML}}":     _languages_html(skills.get("languages", [])),
        "{{SALARY_DISPLAY_MXN}}": salary.get("display_mxn", ""),
        "{{SALARY_DISPLAY_USD}}": salary.get("display_usd", ""),
        "{{TAILORED_BADGE}}":     tailored_badge,
    }

    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))

    return html


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(html: str, output_path: Path) -> bool:
    """Genera PDF desde HTML usando Playwright Chromium."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page    = browser.new_page()
            page.set_content(html, wait_until="domcontentloaded")
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={"top": "14mm", "right": "16mm", "bottom": "14mm", "left": "16mm"},
            )
            browser.close()

        log.info(f"  [PDF] Guardado: {output_path}")
        return True

    except ImportError:
        log.error("Playwright no instalado: py -m playwright install chromium")
        return False
    except Exception as e:
        log.error(f"PDF error: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# SHEET HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_jobs_from_sheet(tab: str, min_fit: float) -> list[dict]:
    """Lee jobs elegibles del Sheet (misma lógica que generate_cover_letters.py)."""
    try:
        from core.sheets.sheet_manager import SheetManager
        sm       = SheetManager()
        all_jobs = sm.get_all_jobs(tab=tab.lower())
        jobs = []
        for j in all_jobs:
            status = str(j.get("Status", "")).lower().strip()
            if any(s in status for s in ("applied", "skip", "rejected", "duplicate")):
                continue
            try:
                fit = float(str(j.get("FIT", j.get("Fit_Score", j.get("FitScore", 0)))).split("/")[0])
            except (ValueError, TypeError):
                continue
            if fit < min_fit:
                continue
            jobs.append({
                "id":          str(j.get("ID", j.get("Job_ID", j.get("_row", "")))).strip(),
                "company":     j.get("Company", "?"),
                "role":        j.get("Role",    j.get("Title", "?")),
                "fit":         fit,
                "url":         j.get("URL",     j.get("ApplyURL", "")),
                "description": j.get("Description", j.get("Notes", "")),
                "_row":        j.get("_row", 0),
                "_tab":        tab,
            })
        jobs.sort(key=lambda x: x["fit"], reverse=True)
        return jobs
    except Exception as e:
        log.error(f"SheetManager error: {e}")
        return []


def update_sheet_cv_path(job: dict, pdf_path: Path):
    """Escribe la ruta del PDF generado en la columna Notes del Sheet."""
    try:
        from core.sheets.sheet_manager import SheetManager
        sm = SheetManager()
        row = job.get("_row", 0)
        tab = job.get("_tab", "LinkedIn")
        if not row:
            log.warning("  [SHEET] No _row disponible — skip update")
            return
        note = f"[CV {datetime.now().strftime('%Y-%m-%d')}] {pdf_path}"
        sm.update_job(row, {"Notes": note}, tab=tab.lower())
        log.info(f"  [SHEET] Notes actualizado con path del CV")
    except Exception as e:
        log.warning(f"  [SHEET] No se pudo actualizar: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PROCESS ONE JOB
# ─────────────────────────────────────────────────────────────────────────────

def process_job(
    profile:       dict,
    salary:        dict,
    job:           dict,
    do_tailor:     bool,
    dry_run:       bool,
    update_sheet:  bool,
    output_prefix: str = "",
) -> Path | None:
    """
    Genera el CV para una vacante.
    Retorna la ruta del PDF generado (o None en dry-run / error).
    """
    company = job.get("company", "base")
    role    = job.get("role",    "")

    log.info(f"\n{'='*60}")
    log.info(f"  {company} — {role} (FIT: {job.get('fit','N/A')}/10)")
    log.info(f"{'='*60}")

    # Tailor with LLM
    tailored = {}
    if do_tailor and (company != "base"):
        log.info("  [LLM] Personalizando summary/skills...")
        tailored = tailor_with_llm(profile, job)

    # Build HTML
    html = build_html(profile, job, tailored, salary)

    # Filename: cv_GooglePM_20260427.pdf
    safe_company = re.sub(r"[^\w]", "", company.replace(" ", "_"))[:20]
    safe_role    = re.sub(r"[^\w]", "", role.replace(" ", "_"))[:15]
    date_str     = datetime.now().strftime("%Y%m%d")
    filename     = f"cv_{safe_company}_{safe_role}_{date_str}.pdf"
    if output_prefix:
        filename = f"{output_prefix}_{filename}"
    pdf_path = OUTPUT_DIR / filename

    if dry_run:
        # Solo guarda el HTML para inspección
        html_path = pdf_path.with_suffix(".html")
        html_path.write_text(html, encoding="utf-8")
        log.info(f"  [DRY-RUN] HTML guardado: {html_path}")
        log.info(f"  [DRY-RUN] PDF omitido (usa --no-dry-run para generarlo)")
        return None

    # Generate PDF
    ok = generate_pdf(html, pdf_path)
    if not ok:
        return None

    # Update Sheet
    if update_sheet and job.get("_row"):
        update_sheet_cv_path(job, pdf_path)

    return pdf_path


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="cv_generator — CV personalizado por vacante con LiteLLM + Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Modo base (sin vacante específica)
    parser.add_argument("--no-tailor", action="store_true",
                        help="No personalizar con LiteLLM — usa perfil base")
    # Vacante manual
    parser.add_argument("--company",  default="", help="Empresa (ej: Google)")
    parser.add_argument("--role",     default="", help="Puesto (ej: PM Senior)")
    parser.add_argument("--fit",      type=float, default=0.0,
                        help="FIT score para incluir en el CV")
    # Desde Sheet
    parser.add_argument("--tab",      default="", help="Tab del Sheet (ej: LinkedIn, Indeed)")
    parser.add_argument("--min-fit",  type=float, default=8.0,
                        help="FIT mínimo para batch desde Sheet (default: 8)")
    parser.add_argument("--max-jobs", type=int,   default=5,
                        help="Máximo de jobs a procesar en batch (default: 5)")
    # Output
    parser.add_argument("--dry-run",      action="store_true",
                        help="Genera HTML pero no PDF (para review)")
    parser.add_argument("--update-sheet", action="store_true",
                        help="Escribe ruta del PDF en Notes del Sheet")
    parser.add_argument("--delay", type=float, default=3.0,
                        help="Segundos entre PDFs en batch (default: 3)")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("CV Generator — LiteLLM + Playwright")
    log.info(f"Tailor: {'NO' if args.no_tailor else 'LiteLLM'} | "
             f"Dry-run: {args.dry_run} | Update-sheet: {args.update_sheet}")
    log.info("=" * 60)

    # Cargar perfil
    profile = load_profile()
    salary  = calculate_salary(profile)

    log.info(f"Perfil: {profile['personal']['name']}")
    log.info(f"Salario mínimo: {salary['display_mxn']} | USD: {salary['display_usd']}")

    do_tailor = not args.no_tailor
    results   = {"ok": 0, "failed": 0}

    # ── Modo batch (desde Sheet) ──────────────────────────────────────────────
    if args.tab:
        log.info(f"\n[BATCH] Tab: {args.tab} | Min FIT: {args.min_fit}")
        jobs = get_jobs_from_sheet(args.tab, args.min_fit)
        if not jobs:
            log.info("[INFO] Sin jobs elegibles en el Sheet.")
            return
        jobs = jobs[:args.max_jobs]
        log.info(f"[FOUND] {len(jobs)} jobs a procesar\n")

        for i, job in enumerate(jobs, 1):
            log.info(f"[{i}/{len(jobs)}]")
            pdf = process_job(profile, salary, job, do_tailor, args.dry_run, args.update_sheet)
            if pdf:
                results["ok"] += 1
            else:
                results["failed"] += 1
            if i < len(jobs):
                time.sleep(args.delay)

    # ── Modo manual (--company / --role) ──────────────────────────────────────
    elif args.company or args.role:
        job = {
            "company":     args.company or "General",
            "role":        args.role    or "PM / BA",
            "fit":         args.fit,
            "description": "",
        }
        pdf = process_job(profile, salary, job, do_tailor, args.dry_run, args.update_sheet)
        if pdf:
            results["ok"] += 1
        else:
            results["failed"] += 1

    # ── Modo base (sin vacante) ───────────────────────────────────────────────
    else:
        log.info("[BASE] Generando CV base sin personalización...")
        pdf = process_job(
            profile, salary, {"company": "base", "role": ""}, False, args.dry_run, False
        )
        if pdf:
            results["ok"] += 1
        else:
            results["failed"] += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    log.info(f"\n{'='*60}")
    log.info(f"DONE — CVs generados: {results['ok']} | Fallidos: {results['failed']}")
    log.info(f"Directorio: {OUTPUT_DIR}")
    log.info("=" * 60)

    if results["ok"] > 0 and not args.dry_run:
        log.info("\n[TIP] Abre los PDFs en data/cvs/ para revisar antes de enviar")
    elif args.dry_run:
        log.info("\n[TIP] Revisa los .html en data/cvs/ — quita --dry-run para generar PDFs")


if __name__ == "__main__":
    main()
