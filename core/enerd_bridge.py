"""
enerd_bridge.py — Puente entre ai-job-foundry y ENERD
=====================================================
Cuando el auto-apply procesa un formulario de empleo, llama a ENERD
para obtener respuestas inteligentes campo por campo usando el perfil
profesional de Marcos + contexto de la oferta específica.

Si ENERD no está disponible → fallback a CV_DATA hardcodeado.

Uso:
    from core.enerd_bridge import ENERDBridge

    bridge = ENERDBridge()
    result = await bridge.analyze_job(job_data, form_fields)
    # result.field_answers["salary_expectation"] == "50000"
    # result.clarifications_needed == []
"""
import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("job_foundry.enerd_bridge")

ENERD_URL = os.getenv("ENERD_URL", "http://localhost:4010")
ENERD_TIMEOUT = float(os.getenv("ENERD_TIMEOUT", "30"))

# ── Fallback: datos hardcodeados del CV ──────────────────────────────────────
CV_FALLBACK: dict[str, str] = {
    "first_name":                "Marcos",
    "last_name":                 "Alvarado",
    "email":                     "markalvati@gmail.com",
    "phone":                     "3323320358",
    "phone_country":             "Mexico (+52)",
    "city":                      "Guadalajara",
    "location":                  "Guadalajara, Jalisco, Mexico",
    "english_proficiency":       "Professional",
    "spanish_proficiency":       "Native",
    "work_authorization_mexico": "Yes",
    "willing_to_relocate":       "No",
    "remote_work":               "Yes",
    "travel_availability":       "Yes",
    "salary_expectation_mxn":   "50000",
    "salary_expectation_usd":   "35000",
    "years_experience":          "10",
    "python_experience":         "Yes",
    "sql_experience":            "Yes",
    "agile_experience":          "Yes",
    "scrum_experience":          "Yes",
    "power_bi_experience":       "Yes",
    "erp_experience":            "Yes",
    "banking_experience":        "Yes",
    "healthcare_experience":     "Yes",
    "manufacturing_experience":  "Yes",
    "aviation_experience":       "No",
}


@dataclass
class JobAnalysisResult:
    """Resultado del análisis de ENERD para un formulario de empleo."""
    field_answers:          dict[str, str]  = field(default_factory=dict)
    cover_letter:           str | None      = None
    clarifications_needed:  list[dict]      = field(default_factory=list)
    confidence:             float           = 1.0
    source:                 str             = "enerd"  # "enerd" | "fallback"
    job_title:              str             = ""
    company:                str             = ""


class ENERDBridge:
    """
    Puente entre ai-job-foundry y ENERD.

    Uso básico:
        bridge = ENERDBridge()
        result = await bridge.analyze_job(job, form_fields)
        answer = result.field_answers.get("salary_expectation", CV_FALLBACK["salary_expectation_mxn"])
    """

    def __init__(self, enerd_url: str = ENERD_URL, timeout: float = ENERD_TIMEOUT):
        self.base_url = enerd_url.rstrip("/")
        self.timeout  = timeout
        self._online: bool | None = None  # None = not checked yet

    async def is_online(self) -> bool:
        """Verifica si ENERD está disponible."""
        try:
            async with httpx.AsyncClient(timeout=3) as c:
                r = await c.get(f"{self.base_url}/health")
                self._online = r.status_code < 500
        except Exception:
            self._online = False
        return bool(self._online)

    async def analyze_job(
        self,
        job: dict,
        form_fields: list[dict] | None = None,
        generate_cover_letter: bool = False,
    ) -> JobAnalysisResult:
        """
        Analiza un trabajo y genera respuestas para el formulario.

        Args:
            job: dict con claves: title, company, description, url, location, fit_score, why
            form_fields: lista de {name, label, type, options?, required?}
                         Si None, retorna solo el perfil base.
            generate_cover_letter: Si True, genera una carta de presentación personalizada.

        Returns:
            JobAnalysisResult con field_answers listo para usar en el form-filler.
        """
        online = await self.is_online()
        if not online:
            log.warning("ENERD offline — usando fallback CV_DATA")
            return self._fallback_result(job, form_fields)

        try:
            payload = {
                "job":                   job,
                "form_fields":           form_fields or [],
                "generate_cover_letter": generate_cover_letter,
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/jobs/analyze",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

            result = JobAnalysisResult(
                field_answers         = data.get("field_answers", {}),
                cover_letter          = data.get("cover_letter"),
                clarifications_needed = data.get("clarifications_needed", []),
                confidence            = data.get("confidence", 1.0),
                source                = "enerd",
                job_title             = data.get("job_title", job.get("title", "")),
                company               = data.get("company", job.get("company", "")),
            )
            log.info(
                f"ENERD analysis: {result.job_title}@{result.company} | "
                f"confidence={result.confidence} | "
                f"fields={len(result.field_answers)} | "
                f"clarifications={len(result.clarifications_needed)}"
            )
            return result

        except Exception as e:
            log.warning(f"ENERD analyze_job failed: {e} — using fallback")
            return self._fallback_result(job, form_fields)

    async def get_field_answer(
        self,
        field_name: str,
        field_label: str,
        field_type: str,
        job: dict,
        options: list[str] | None = None,
    ) -> str:
        """
        Obtiene la respuesta para UN campo específico.
        Útil cuando el formulario se procesa campo por campo en tiempo real.
        """
        online = await self.is_online()
        if not online:
            return self._get_fallback_answer(field_name, field_label)

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{self.base_url}/api/jobs/field",
                    json={
                        "field_name":  field_name,
                        "field_label": field_label,
                        "field_type":  field_type,
                        "job":         job,
                        "options":     options or [],
                    },
                )
                if resp.status_code == 200:
                    return resp.json().get("answer", "")
        except Exception as e:
            log.warning(f"ENERD get_field_answer failed: {e}")

        return self._get_fallback_answer(field_name, field_label)

    async def get_pending_clarifications(self) -> list[dict]:
        """Retorna campos que ENERD no pudo responder y necesitan input del usuario."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/jobs/clarifications")
                if resp.status_code == 200:
                    return resp.json().get("clarifications", [])
        except Exception:
            pass
        return []

    async def answer_clarification(self, clarif_id: str, answer: str) -> bool:
        """Envía la respuesta del usuario para una clarificación pendiente."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(
                    f"{self.base_url}/api/jobs/clarifications/{clarif_id}/answer",
                    json={"answer": answer},
                )
                return resp.status_code == 200
        except Exception:
            pass
        return False

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _fallback_result(self, job: dict, form_fields: list[dict] | None) -> JobAnalysisResult:
        """Resultado usando solo CV_DATA hardcodeado."""
        answers: dict[str, str] = {}
        if form_fields:
            for f in form_fields:
                name  = f.get("name", "")
                label = f.get("label", "")
                answers[name] = self._get_fallback_answer(name, label)
        return JobAnalysisResult(
            field_answers = answers or CV_FALLBACK.copy(),
            source        = "fallback",
            job_title     = job.get("title", ""),
            company       = job.get("company", ""),
            confidence    = 0.7,
        )

    def _get_fallback_answer(self, field_name: str, field_label: str = "") -> str:
        """Busca en CV_FALLBACK por nombre o label de campo."""
        key = field_name.lower()
        lbl = field_label.lower()
        for cv_key, cv_val in CV_FALLBACK.items():
            if cv_key in key or cv_key in lbl:
                return cv_val
        # Defaults genéricos
        if any(k in key or k in lbl for k in ["yes", "no", "boolean", "check"]):
            return "Yes"
        if any(k in key or k in lbl for k in ["year", "experience", "exp"]):
            return "10"
        return ""


# ── Función helper de alto nivel ──────────────────────────────────────────────

async def enrich_cv_data_for_job(job: dict, base_cv_data: dict) -> dict:
    """
    Función de conveniencia: toma el CV_DATA base y lo enriquece con respuestas
    inteligentes de ENERD para el trabajo específico.

    Retorna un nuevo dict combinando base_cv_data + respuestas de ENERD.
    """
    bridge = ENERDBridge()
    result = await bridge.analyze_job(job, generate_cover_letter=True)

    if result.source == "enerd" and result.confidence >= 0.5:
        enriched = {**base_cv_data, **result.field_answers}
        if result.cover_letter:
            enriched["cover_letter"] = result.cover_letter
        log.info(f"CV data enriched by ENERD (confidence={result.confidence})")
        return enriched

    log.info("Using base CV_DATA (ENERD unavailable or low confidence)")
    return base_cv_data
