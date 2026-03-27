#!/usr/bin/env python3
"""
AI Job Analyzer v2 — Gap analysis estructurado + CHALAN context + semaforo
Calcula FIT scores usando LiteLLM (con fallback a Claude si el local falla)
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Usar LiteLLM como proxy (tiene fallback a Claude automatico)
LLM_URL   = os.getenv("LLM_URL",   "http://127.0.0.1:4000/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "local-llama")
LLM_KEY   = os.getenv("LITELLM_KEY", "sk-1234567890abcdef")
CHALAN_URL = os.getenv("CHALAN_URL", "http://localhost:4001")


def _get_chalan_profile() -> str:
    """Intenta obtener el perfil actualizado de Marcos desde CHALAN."""
    try:
        r = requests.get(f"{CHALAN_URL}/context", timeout=4)
        if r.status_code == 200:
            ctx = r.json().get("context", "")
            if ctx:
                return ctx
    except Exception:
        pass
    # Fallback: perfil hardcodeado si CHALAN no esta disponible
    return """PERFIL DE MARCOS:
- Project Manager / Business Analyst Senior, 10+ anos experiencia
- Especialidades: ERP migrations (Dynamics AX, SAP), ETL, BI/Power BI, LATAM projects
- Idiomas: Espanol nativo, Ingles fluido
- Modalidad buscada: Remoto preferido, hibrido aceptable
- NO busca: roles de Software Developer / Programmer puro
- Industrias: Fintech, Retail, Manufactura, Gobierno"""


class AIAnalyzer:
    """Analizador de jobs con IA — gap analysis estructurado + semaforo"""

    def __init__(self):
        self.llm_url   = LLM_URL
        self.llm_model = LLM_MODEL
        self.llm_key   = LLM_KEY
        self._profile  = None   # se carga lazy

    def _load_profile(self) -> str:
        if self._profile is None:
            self._profile = _get_chalan_profile()
        return self._profile

    def analyze_job(self, job_data: dict) -> dict:
        """
        Analiza un job y retorna FIT score + gap analysis estructurado.

        Retorna:
            {
                'fit_score':      int (0-10),
                'tienes':         str  — bullets de requisitos que Marcos SI cumple
                'faltan':         str  — bullets de requisitos que le FALTAN
                'recomendacion':  str  — 'Aplica' | 'Borderline' | 'No apliques'
                'seniority':      str
                'why':            str  — resumen corto para la columna Why del sheet
            }
        """
        role        = job_data.get('Role', 'Unknown')
        company     = job_data.get('Company', 'Unknown')
        description = job_data.get('full_description', job_data.get('Description', ''))
        profile     = self._load_profile()

        prompt = f"""{profile}

OFERTA A ANALIZAR:
Titulo: {role}
Empresa: {company}
Descripcion: {description[:1500]}

TAREA: Analiza si esta oferta es buena para Marcos. Se muy especifico — no uses respuestas genericas.

FIT SCORE 0-10:
- 0-3: No match (developer puro, junior, presencial obligatorio en otra ciudad)
- 4-5: Bajo (pocas coincidencias)
- 6-7: Medio (algunas skills, algo falta)
- 8-9: Buen match (PM/BA/IT Manager, skills alineadas, remoto)
- 10: Match perfecto (todo coincide)

Responde SOLO en JSON valido, sin markdown:
{{
  "fit_score": 8,
  "tienes": "- PM Senior 10+ anos\\n- Experiencia ERP\\n- LATAM projects",
  "faltan": "- Certificacion PMP requerida\\n- Experiencia en Salesforce",
  "recomendacion": "Aplica",
  "seniority": "Senior",
  "why": "PM Senior remoto con ERP, falta PMP cert"
}}

recomendacion debe ser exactamente: "Aplica", "Borderline" o "No apliques"
tienes y faltan: lista de bullets especificos del job, NO genericos
"""
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 400
                },
                headers={
                    "Authorization": f"Bearer {self.llm_key}",
                    "Content-Type": "application/json"
                },
                timeout=45
            )

            if response.status_code != 200:
                print(f"  LLM HTTP {response.status_code}: {response.text[:100]}")
                return self._default_response()

            content = response.json()['choices'][0]['message']['content']
            content = content.replace('```json', '').replace('```', '').strip()

            # Extraer JSON aunque haya texto extra antes/despues
            start = content.find('{')
            end   = content.rfind('}') + 1
            if start >= 0 and end > start:
                content = content[start:end]

            result = json.loads(content)

            fit = min(10, max(0, int(result.get('fit_score', 5))))
            tienes = result.get('tienes', '')
            faltan = result.get('faltan', '')
            rec    = result.get('recomendacion', 'Borderline')
            why_short = result.get('why', f"{rec} | {tienes[:60]}")

            return {
                'fit_score':     fit,
                'tienes':        tienes,
                'faltan':        faltan,
                'recomendacion': rec,
                'seniority':     result.get('seniority', 'Unknown'),
                'why':           f"[{rec}] {why_short}"
            }

        except Exception as e:
            print(f"  Warning analisis IA: {e}")
            return self._default_response()

    def _default_response(self) -> dict:
        return {
            'fit_score':     5,
            'tienes':        '- Pendiente de analisis',
            'faltan':        '- Pendiente de analisis',
            'recomendacion': 'Borderline',
            'seniority':     'Unknown',
            'why':           'LLM no disponible - analizar manualmente'
        }
