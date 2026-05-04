"""
External Sites Auto-Apply
=========================
Handles job applications on external platforms (non-LinkedIn Easy Apply).

Supported platforms:
  • Workday       — myworkdayjobs.com  / wd*.myworkday.com
  • Greenhouse    — boards.greenhouse.io / job-boards.greenhouse.io
  • Lever         — jobs.lever.co
  • SmartRecruiters — jobs.smartrecruiters.com
  • Generic       — fallback for any other site (fills common field patterns)

Usage (standalone):
  from core.automation.auto_apply_external import ExternalApplier

  async with ExternalApplier(cv_data, ai_url="http://127.0.0.1:4000") as applier:
      ok, reason = await applier.apply(page, job)
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Optional, Tuple, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

# Raíz del proyecto: core/automation/auto_apply_external.py → ../../
_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

def _resolve_cv_path() -> str:
    """Busca el CV en el proyecto primero; fallback a rutas conocidas."""
    candidates = [
        _PROJECT_ROOT / "data" / "cv" / "CV_Marcos_Alvarado_2026.pdf",
        _PROJECT_ROOT / "data" / "cvs" / "cv_base__20260427.pdf",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    # Fallback: usar PROJECT_ROOT de .env si está seteado
    env_root = os.getenv("PROJECT_ROOT", "")
    if env_root:
        fallback = Path(env_root) / "data" / "cv" / "CV_Marcos_Alvarado_2026.pdf"
        if fallback.exists():
            return str(fallback)
    return str(candidates[0])  # devuelve la ruta canónica aunque no exista (el upload fallará con warning claro)

# ── CV defaults (override via cv_data param) ──────────────────────────────────
DEFAULT_CV = {
    "first_name":   "Marcos",
    "last_name":    "Alvarado",
    "full_name":    "Marcos Alvarado",
    "email":        "markalvati@gmail.com",
    "phone":        "3323320358",
    "phone_intl":   "+52 33 2332 0358",
    "city":         "Guadalajara",
    "country":      "Mexico",
    "linkedin_url": "https://www.linkedin.com/in/marcosalvarado-it",
    "resume_path":  _resolve_cv_path(),  # detecta la ruta correcta automáticamente
    # Screening defaults
    "years_experience":       "10",
    "salary_expectation_mxn": "60000",
    "salary_expectation_usd": "40000",
    "willing_to_relocate":    "No",
    "remote_work":            "Yes",
    "work_authorization":     "Yes",
    "english_proficiency":    "Professional",
    "spanish_proficiency":    "Native",
}

# ── AI helper ─────────────────────────────────────────────────────────────────
LLM_URL   = os.getenv("LLM_URL",   "http://127.0.0.1:4000/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "local-llama")
LLM_KEY   = os.getenv("LITELLM_KEY", "sk-1234567890abcdef")

MARCOS_PROFILE = """
Marcos Alvarado — Senior Project Manager / Business Analyst, 10+ years.
Especialidades: ERP migrations (SAP, Dynamics AX), ETL, BI/Power BI, LATAM projects.
Idiomas: Español nativo, Inglés profesional fluido.
Industrias: Fintech, Retail, Manufactura, Gobierno, Salud.
Modalidad: Remoto preferido, híbrido aceptable. Guadalajara, México.
""".strip()


def ask_ai(question: str, job: dict, cv: dict, max_words: int = 80) -> str:
    """Ask LM Studio / LiteLLM a custom application question. Falls back to generic."""
    title   = job.get("Role",    job.get("title",   "Project Manager"))
    company = job.get("Company", job.get("company", "the company"))
    prompt = (
        f"You are filling a job application for {title} at {company}.\n"
        f"Candidate profile:\n{MARCOS_PROFILE}\n\n"
        f"Answer this application question in {max_words} words or fewer, "
        f"professional and specific to the role:\n\n{question}"
    )
    try:
        r = requests.post(
            LLM_URL,
            headers={"Authorization": f"Bearer {LLM_KEY}"},
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.3,
            },
            timeout=20,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"    [AI WARN] LM Studio unavailable: {e}")

    # Fallback — generic but professional answer
    return (
        f"With 10+ years of experience in project management and ERP implementations, "
        f"I am confident I can contribute significantly to {company} as {title}. "
        f"My background in SAP, Agile methodologies, and cross-functional leadership "
        f"aligns well with this opportunity."
    )


# ── Platform detection ────────────────────────────────────────────────────────

def detect_platform(url: str) -> str:
    """Return platform key from URL, or 'generic'."""
    url_lower = url.lower()
    if "myworkdayjobs.com" in url_lower or "myworkday.com" in url_lower:
        return "workday"
    if "greenhouse.io" in url_lower:
        return "greenhouse"
    if "lever.co" in url_lower:
        return "lever"
    if "smartrecruiters.com" in url_lower:
        return "smartrecruiters"
    if "bamboohr.com" in url_lower:
        return "bamboohr"
    if "successfactors" in url_lower:
        return "successfactors"
    return "generic"


# ── ExternalApplier ───────────────────────────────────────────────────────────

class ExternalApplier:
    """Applies to external-site jobs using Playwright (async)."""

    def __init__(self, cv_data: Optional[dict] = None):
        self.cv = {**DEFAULT_CV, **(cv_data or {})}

    # ── public entry point ────────────────────────────────────────────────────

    async def apply(self, page, job: dict, submit: bool = True) -> Tuple[bool, str]:
        """
        Navigate to job.ApplyURL and fill + submit the external application.

        Returns (success: bool, reason: str)
        """
        url = job.get("ApplyURL", job.get("apply_url", ""))
        if not url:
            return False, "No ApplyURL"

        platform = detect_platform(url)
        print(f"    [EXT] Platform detected: {platform.upper()} — {url[:80]}")

        handler = {
            "workday":         self._apply_workday,
            "greenhouse":      self._apply_greenhouse,
            "lever":           self._apply_lever,
            "smartrecruiters": self._apply_smartrecruiters,
            "bamboohr":        self._apply_bamboohr,
            "successfactors":  self._apply_generic,   # complex — use generic for now
            "generic":         self._apply_generic,
        }.get(platform, self._apply_generic)

        try:
            return await handler(page, job, url, submit)
        except Exception as e:
            return False, f"External apply error: {e}"

    # ── Workday ───────────────────────────────────────────────────────────────

    async def _apply_workday(self, page, job, url, submit) -> Tuple[bool, str]:
        """
        Workday — most common for large enterprises (SAP, Deloitte, Accenture).
        Flow: job page → Apply → Guest or Account → Fill → Submit
        """
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Click Apply button
        apply_btn = await self._find_any(page, [
            'a[data-automation-id="applyButton"]',
            'button[data-automation-id="applyButton"]',
            'a:has-text("Apply")',
            'button:has-text("Apply Now")',
        ])
        if not apply_btn:
            return False, "Workday: Apply button not found"
        await apply_btn.click()
        await asyncio.sleep(3)

        # Guest apply (if modal appears)
        guest_btn = await self._find_any(page, [
            'button[data-automation-id="createAccountLink"]',
            'a:has-text("Apply Manually")',
            'button:has-text("Continue as Guest")',
            'a:has-text("Continue as Guest")',
        ])
        if guest_btn:
            await guest_btn.click()
            await asyncio.sleep(2)

        # Fill standard Workday fields
        await self._fill_field(page, '[data-automation-id="legalNameSection_firstName"]', self.cv["first_name"])
        await self._fill_field(page, '[data-automation-id="legalNameSection_lastName"]',  self.cv["last_name"])
        await self._fill_field(page, '[data-automation-id="email"]',                       self.cv["email"])
        await self._fill_field(page, '[data-automation-id="phone-number"]',                self.cv["phone"])

        # Resume upload
        await self._upload_resume(page, [
            'input[data-automation-id="file-upload-input-ref"]',
            'input[type="file"][accept*="pdf"]',
        ])

        # Handle multi-step "Next" buttons
        for step in range(1, 8):
            next_btn = await self._find_any(page, [
                'button[data-automation-id="bottom-navigation-next-button"]',
                'button:has-text("Next")',
                'button:has-text("Continue")',
            ])
            if not next_btn:
                break

            # Fill any visible text questions before advancing
            await self._fill_ai_questions(page, job)
            await asyncio.sleep(1)

            # Check if this is Submit
            submit_btn = await self._find_any(page, [
                'button[data-automation-id="bottom-navigation-next-button"]:has-text("Submit")',
                'button:has-text("Submit")',
            ])
            if submit_btn:
                if submit:
                    await submit_btn.click()
                    await asyncio.sleep(3)
                    return True, "Applied (Workday)"
                else:
                    return True, "Dry-run: Workday form filled"

            await next_btn.click()
            await asyncio.sleep(2)

        return False, "Workday: could not reach Submit"

    # ── Greenhouse ────────────────────────────────────────────────────────────

    async def _apply_greenhouse(self, page, job, url, submit) -> Tuple[bool, str]:
        """
        Greenhouse — common in tech / scale-ups.
        Usually a single-page form.
        """
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Standard fields
        await self._fill_field(page, '#first_name',  self.cv["first_name"])
        await self._fill_field(page, '#last_name',   self.cv["last_name"])
        await self._fill_field(page, '#email',       self.cv["email"])
        await self._fill_field(page, '#phone',       self.cv["phone_intl"])

        # LinkedIn URL (Greenhouse often asks)
        await self._fill_field(page, '#job_application_answers_linkedin',
                               self.cv["linkedin_url"])
        await self._fill_field(page, 'input[name*="linkedin"]', self.cv["linkedin_url"])

        # Resume upload
        await self._upload_resume(page, [
            '#resume',
            'input[name="resume"]',
            'input[type="file"]',
        ])

        # Cover letter (text area)
        cover_letter = ask_ai(
            f"Write a 3-sentence cover letter for {job.get('Role','this role')} "
            f"at {job.get('Company','this company')}.",
            job, self.cv, max_words=100
        )
        await self._fill_field(page, '#cover_letter', cover_letter)
        await self._fill_field(page, 'textarea[name="cover_letter"]', cover_letter)

        # Fill any custom questions
        await self._fill_ai_questions(page, job)

        if not submit:
            return True, "Dry-run: Greenhouse form filled"

        submit_btn = await self._find_any(page, [
            '#submit_app',
            'input[type="submit"]',
            'button:has-text("Submit Application")',
            'button[type="submit"]',
        ])
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return True, "Applied (Greenhouse)"

        return False, "Greenhouse: Submit button not found"

    # ── Lever ─────────────────────────────────────────────────────────────────

    async def _apply_lever(self, page, job, url, submit) -> Tuple[bool, str]:
        """
        Lever — common in funded startups.
        """
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Lever shows an "Apply" button on the job page that opens a modal/new page
        apply_btn = await self._find_any(page, [
            'a.template-btn-submit',
            'a:has-text("Apply for this job")',
            'a:has-text("Apply Now")',
            'button:has-text("Apply")',
        ])
        if apply_btn:
            await apply_btn.click()
            await asyncio.sleep(2)

        # Fill fields
        await self._fill_field(page, 'input[name="name"]',  self.cv["full_name"])
        await self._fill_field(page, 'input[name="email"]', self.cv["email"])
        await self._fill_field(page, 'input[name="phone"]', self.cv["phone_intl"])
        await self._fill_field(page, 'input[name="org"]',   "Independent Consultant")

        # LinkedIn / Website
        await self._fill_field(page, 'input[name="urls[LinkedIn]"]', self.cv["linkedin_url"])

        # Resume upload
        await self._upload_resume(page, [
            'input[name="resume"]',
            'input[type="file"]',
        ])

        # Cover letter / comments
        cover = ask_ai(
            f"Short cover letter for {job.get('Role')} at {job.get('Company')}.",
            job, self.cv, max_words=80
        )
        await self._fill_field(page, 'textarea[name="comments"]', cover)

        # Custom questions
        await self._fill_ai_questions(page, job)

        if not submit:
            return True, "Dry-run: Lever form filled"

        submit_btn = await self._find_any(page, [
            'button[type="submit"]:has-text("Submit application")',
            'button[type="submit"]',
        ])
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return True, "Applied (Lever)"

        return False, "Lever: Submit button not found"

    # ── SmartRecruiters ───────────────────────────────────────────────────────

    async def _apply_smartrecruiters(self, page, job, url, submit) -> Tuple[bool, str]:
        """SmartRecruiters — multi-step wizard."""
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Click the big Apply button on the listing page
        apply_btn = await self._find_any(page, [
            'a[data-ui="apply-btn"]',
            'button[data-ui="apply-btn"]',
            'a:has-text("Apply Now")',
        ])
        if apply_btn:
            await apply_btn.click()
            await asyncio.sleep(2)

        # Personal info
        await self._fill_field(page, 'input[name="firstName"]',   self.cv["first_name"])
        await self._fill_field(page, 'input[name="lastName"]',    self.cv["last_name"])
        await self._fill_field(page, 'input[name="email"]',       self.cv["email"])
        await self._fill_field(page, 'input[name="phoneNumber"]', self.cv["phone_intl"])

        # Resume upload
        await self._upload_resume(page, ['input[type="file"]'])

        # Multi-step navigation
        for _ in range(5):
            await self._fill_ai_questions(page, job)
            next_btn = await self._find_any(page, [
                'button[data-ui="btn-next"]',
                'button:has-text("Next")',
                'button:has-text("Continue")',
            ])
            submit_btn = await self._find_any(page, [
                'button[data-ui="btn-submit"]',
                'button:has-text("Send Application")',
                'button:has-text("Submit")',
            ])
            if submit_btn:
                if submit:
                    await submit_btn.click()
                    await asyncio.sleep(3)
                    return True, "Applied (SmartRecruiters)"
                return True, "Dry-run: SmartRecruiters form filled"
            if next_btn:
                await next_btn.click()
                await asyncio.sleep(2)
            else:
                break

        return False, "SmartRecruiters: could not reach Submit"

    # ── BambooHR ──────────────────────────────────────────────────────────────

    async def _apply_bamboohr(self, page, job, url, submit) -> Tuple[bool, str]:
        """BambooHR — simple single-page form."""
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        await self._fill_field(page, 'input#firstName', self.cv["first_name"])
        await self._fill_field(page, 'input#lastName',  self.cv["last_name"])
        await self._fill_field(page, 'input#email',     self.cv["email"])
        await self._fill_field(page, 'input#phone',     self.cv["phone_intl"])
        await self._fill_field(page, 'input#linkedIn',  self.cv["linkedin_url"])

        await self._upload_resume(page, ['input[type="file"]'])
        await self._fill_ai_questions(page, job)

        if not submit:
            return True, "Dry-run: BambooHR form filled"

        submit_btn = await self._find_any(page, [
            'button[type="submit"]',
            'input[type="submit"]',
        ])
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return True, "Applied (BambooHR)"

        return False, "BambooHR: Submit button not found"

    # ── Generic fallback ──────────────────────────────────────────────────────

    async def _apply_generic(self, page, job, url, submit) -> Tuple[bool, str]:
        """
        Generic handler — fills common name/email/phone/resume patterns.
        Works for ~70% of custom company ATS sites.
        """
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Try common field name patterns
        name_selectors = [
            'input[name*="name"][name*="first"]',
            'input[id*="firstName"]',
            'input[placeholder*="First name"]',
            'input[aria-label*="First name"]',
        ]
        last_selectors = [
            'input[name*="name"][name*="last"]',
            'input[id*="lastName"]',
            'input[placeholder*="Last name"]',
            'input[aria-label*="Last name"]',
        ]
        full_name_selectors = [
            'input[name="name"]',
            'input[id="name"]',
            'input[placeholder*="Full name"]',
            'input[aria-label*="Full name"]',
        ]
        email_selectors = [
            'input[type="email"]',
            'input[name*="email"]',
            'input[id*="email"]',
        ]
        phone_selectors = [
            'input[type="tel"]',
            'input[name*="phone"]',
            'input[id*="phone"]',
        ]

        # Fill what we can find
        filled = 0
        for sel in name_selectors:
            if await self._fill_field(page, sel, self.cv["first_name"]):
                filled += 1
                break
        for sel in last_selectors:
            if await self._fill_field(page, sel, self.cv["last_name"]):
                filled += 1
                break
        for sel in full_name_selectors:
            if await self._fill_field(page, sel, self.cv["full_name"]):
                filled += 1
                break
        for sel in email_selectors:
            if await self._fill_field(page, sel, self.cv["email"]):
                filled += 1
                break
        for sel in phone_selectors:
            if await self._fill_field(page, sel, self.cv["phone_intl"]):
                filled += 1
                break

        await self._upload_resume(page, ['input[type="file"]'])
        await self._fill_ai_questions(page, job)

        if filled == 0:
            return False, "Generic: no recognizable fields found"

        if not submit:
            return True, f"Dry-run: Generic form filled ({filled} fields)"

        submit_btn = await self._find_any(page, [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Apply")',
            'button:has-text("Send")',
        ])
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(3)
            return True, "Applied (Generic)"

        return False, "Generic: Submit button not found"

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _find_any(self, page, selectors: list):
        """Return the first element that matches any selector, or None."""
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    return el
            except Exception:
                pass
        return None

    async def _fill_field(self, page, selector: str, value: str) -> bool:
        """
        Safely fill a field. Returns True if found and filled.
        Clears existing content first.
        """
        try:
            el = await page.query_selector(selector)
            if el:
                await el.triple_click()
                await el.fill(value)
                return True
        except Exception:
            pass
        return False

    async def _upload_resume(self, page, selectors: list) -> bool:
        """Upload CV PDF if a file input is found."""
        resume_path = self.cv.get("resume_path", "")
        if not resume_path or not Path(resume_path).exists():
            print(f"    [RESUME WARN] CV file not found: {resume_path}")
            return False

        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.set_input_files(resume_path)
                    print(f"    [RESUME] Uploaded: {Path(resume_path).name}")
                    return True
            except Exception:
                pass
        return False

    async def _fill_ai_questions(self, page, job: dict) -> int:
        """
        Find all visible text areas / custom questions and fill them using AI.
        Returns number of questions answered.
        """
        answered = 0
        try:
            # Find textareas that are visible and empty
            textareas = await page.query_selector_all('textarea:visible')
            for ta in textareas:
                try:
                    current = await ta.input_value()
                    if current.strip():
                        continue  # already filled
                    # Get label or placeholder as the question
                    label = await self._get_label(page, ta)
                    if not label:
                        label = "Tell us about yourself and your qualifications."
                    answer = ask_ai(label, job, self.cv)
                    await ta.fill(answer)
                    answered += 1
                    print(f"    [AI] Answered: {label[:60]}...")
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

            # Also handle yes/no selects (work authorization, remote, etc.)
            selects = await page.query_selector_all('select:visible')
            for sel_el in selects:
                try:
                    label = await self._get_label(page, sel_el)
                    label_lower = (label or "").lower()
                    options = await sel_el.query_selector_all('option')
                    option_texts = [await o.inner_text() for o in options]

                    value_to_set = None
                    if any(k in label_lower for k in ["authorized", "eligible", "work in"]):
                        value_to_set = next((t for t in option_texts if "yes" in t.lower()), None)
                    elif any(k in label_lower for k in ["sponsor", "visa"]):
                        value_to_set = next((t for t in option_texts if "no" in t.lower()), None)
                    elif any(k in label_lower for k in ["remote", "relocat"]):
                        value_to_set = next((t for t in option_texts if "yes" in t.lower()), None)

                    if value_to_set:
                        await sel_el.select_option(label=value_to_set)
                        answered += 1
                except Exception:
                    pass
        except Exception as e:
            print(f"    [AI WARN] fill_ai_questions: {e}")

        return answered

    async def _get_label(self, page, element) -> str:
        """Try to find the label text for a form element."""
        try:
            # Method 1: aria-label attribute
            aria = await element.get_attribute("aria-label")
            if aria:
                return aria

            # Method 2: placeholder
            ph = await element.get_attribute("placeholder")
            if ph:
                return ph

            # Method 3: associated <label> via id
            el_id = await element.get_attribute("id")
            if el_id:
                label_el = await page.query_selector(f'label[for="{el_id}"]')
                if label_el:
                    return (await label_el.inner_text()).strip()

            # Method 4: parent container text (first 100 chars)
            parent_text = await page.evaluate(
                "(el) => el.closest('.field, .form-group, .question, [class*=question]')"
                "?.innerText?.slice(0, 100) || ''",
                element
            )
            if parent_text:
                return parent_text.strip()
        except Exception:
            pass
        return ""
