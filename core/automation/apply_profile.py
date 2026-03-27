#!/usr/bin/env python3
"""
apply_profile.py — Perfil de datos para rellenar formularios de empleo.
Lee datos de CHALAN (apply_profile) con fallback a .env y valores por defecto.
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CHALAN_URL = os.getenv("CHALAN_URL", "http://localhost:4001")

# Campos estándar con sus alias (para fuzzy matching de etiquetas de formulario)
FIELD_ALIASES = {
    "phone": ["phone", "telephone", "mobile", "celular", "telefono", "tel"],
    "years_experience": ["years of experience", "años de experiencia", "experience", "experiencia", "yoe"],
    "salary_expectation": ["salary", "salario", "sueldo", "compensation", "expectativa salarial", "remuneracion"],
    "notice_period": ["notice period", "availability", "available", "start date", "disponibilidad", "inicio"],
    "work_authorization": ["work authorization", "visa", "authorized to work", "permiso de trabajo", "citizenship"],
    "english_level": ["english", "ingles", "english proficiency", "english level", "nivel de ingles"],
    "linkedin_url": ["linkedin", "linkedin url", "linkedin profile", "perfil de linkedin"],
    "portfolio_url": ["portfolio", "website", "portafolio", "sitio web"],
    "cover_letter": ["cover letter", "carta de presentacion", "motivacion", "why do you want"],
    "current_location": ["location", "city", "ubicacion", "ciudad", "where are you located"],
    "remote_preference": ["remote", "hybrid", "on-site", "modalidad", "trabajo remoto"],
    "highest_education": ["education", "degree", "educacion", "nivel educativo", "titulo"],
    "full_name": ["full name", "nombre completo", "nombre", "name", "first name", "last name"],
    "email": ["email", "correo", "e-mail"],
    "current_title": ["current title", "current role", "puesto actual", "titulo actual", "job title"],
    "how_did_you_hear": ["how did you hear", "como te enteraste", "referral", "source"],
    "relocate_willing": ["willing to relocate", "disponible para reubicacion", "relocate"],
}

DEFAULTS = {
    "phone":           os.getenv("APPLY_PHONE", ""),
    "years_experience": os.getenv("APPLY_YEARS_EXP", "8"),
    "work_authorization": os.getenv("APPLY_WORK_AUTH", "Ciudadano mexicano"),
    "english_level":   os.getenv("APPLY_ENGLISH", "B2 - Avanzado"),
    "remote_preference": os.getenv("APPLY_REMOTE_PREF", "Remoto / Hibrido"),
    "relocate_willing": "No",
    "how_did_you_hear": "LinkedIn",
}


class ApplyProfile:
    """Gestiona el perfil de datos para rellenar formularios de empleo."""

    def __init__(self):
        self._cache: dict = {}
        self._loaded = False

    def load(self):
        """Carga perfil desde CHALAN."""
        try:
            r = requests.get(f"{CHALAN_URL}/apply/profile", timeout=5)
            if r.status_code == 200:
                self._cache = r.json()
                self._loaded = True
        except Exception:
            pass
        # Aplicar defaults para campos vacíos
        for k, v in DEFAULTS.items():
            if k not in self._cache and v:
                self._cache[k] = v

    def get(self, field: str) -> str | None:
        """Retorna el valor de un campo, o None si no está."""
        if not self._loaded:
            self.load()
        return self._cache.get(field)

    def set(self, field: str, value: str):
        """Guarda un campo en CHALAN y en caché local."""
        self._cache[field] = value
        try:
            requests.post(
                f"{CHALAN_URL}/apply/profile",
                json={field: value},
                timeout=5
            )
        except Exception:
            pass

    def match_field(self, label: str) -> str | None:
        """
        Fuzzy match de una etiqueta de formulario al nombre de campo del perfil.
        Retorna el nombre del campo si hay match, None si no.
        """
        label_lower = label.lower().strip()
        for field, aliases in FIELD_ALIASES.items():
            for alias in aliases:
                if alias in label_lower or label_lower in alias:
                    return field
        return None

    def ask_question(self, field: str, label: str, job: str, company: str, site: str) -> int | None:
        """
        Crea una pregunta pendiente en CHALAN para que Telegram la pida al usuario.
        Retorna el ID de la pregunta o None si falla.
        """
        try:
            r = requests.post(
                f"{CHALAN_URL}/apply/questions",
                json={"field": field, "label": label, "job": job, "company": company, "site": site},
                timeout=5
            )
            if r.status_code == 200:
                return r.json().get("question_id")
        except Exception:
            pass
        return None

    def wait_for_answer(self, question_id: int, timeout: int = 120, poll_interval: int = 5) -> str | None:
        """
        Espera la respuesta a una pregunta pendiente (polling CHALAN).
        Retorna la respuesta o None si timeout.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                r = requests.get(f"{CHALAN_URL}/apply/questions", timeout=5)
                if r.status_code == 200:
                    questions = r.json()
                    for q in questions:
                        if q.get("id") == question_id and q.get("status") == "answered":
                            answer = q.get("answer")
                            if answer:
                                self._cache[q.get("field", "")] = answer
                                return answer
            except Exception:
                pass
            time.sleep(poll_interval)
        return None


# Singleton
_profile = None

def get_profile() -> ApplyProfile:
    global _profile
    if _profile is None:
        _profile = ApplyProfile()
        _profile.load()
    return _profile
