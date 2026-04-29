"""
LinkedIn Easy Apply - COMPLETE AUTOMATION
Handles entire Easy Apply flow from start to finish

Author: Marcos Alberto Alvarado
Date: 2026-01-28
"""

import asyncio
import os
import sys
import json
import re
import urllib.request as _urllib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.sheets.sheet_manager import SheetManager
from core.enerd_bridge import ENERDBridge, CV_FALLBACK

# CV DATA - COMPLETE
CV_DATA = {
    "first_name": "Marcos",
    "last_name": "Alvarado",
    "email": "markalvati@gmail.com",
    "phone": "3323320358",
    "phone_country": "Mexico (+52)",
    "city": "Guadalajara",
    "resume_path": r"C:\Users\MSI\Desktop\ai-job-foundry\data\cv\CV_Marcos_Alvarado_2026.pdf",

    # Screening answers
    "english_proficiency": "Professional",
    "spanish_proficiency": "Native",
    "work_authorization_mexico": "Yes",
    "willing_to_relocate": "No",
    "remote_work": "Yes",
    "travel_availability": "Yes",
    "salary_expectation_mxn": "50000",    # Prioridad: conseguir empleo
    "salary_expectation_usd": "35000",    # Equivalente aprox USD
    "years_experience": "10",
    
    # Technical skills
    "python_experience": "Yes",
    "sql_experience": "Yes",
    "agile_experience": "Yes",
    "scrum_experience": "Yes",
    "power_bi_experience": "Yes",
    
    # Industry experience
    "erp_experience": "Yes",
    "banking_experience": "Yes",
    "healthcare_experience": "Yes",
    "manufacturing_experience": "Yes",
    "aviation_experience": "No"
}


class EasyApplyBot:
    """Complete Easy Apply automation"""
    
    def __init__(self, dry_run=False):
        load_dotenv()
        self.dry_run = dry_run
        self.sheet_manager = SheetManager()
        self.cv_data = CV_DATA.copy()
        self._bridge = ENERDBridge()          # ENERD bridge para respuestas inteligentes
        self._base_cv = CV_DATA.copy()        # Respaldo original, nunca se modifica
        self._current_job: dict = {}          # Job activo — se actualiza por enrich_for_job

    async def enrich_for_job(self, job: dict) -> None:
        """
        Consulta ENERD para enriquecer cv_data con respuestas específicas para ESTE trabajo.
        Si ENERD no está disponible, usa el CV_DATA original sin interrupciones.
        """
        title   = job.get('Role', job.get('title', 'N/A'))
        company = job.get('Company', job.get('company', 'N/A'))
        print(f"   🧠 ENERD analizando oferta: {title} @ {company}...")

        job_normalized = {
            "title":       title,
            "company":     company,
            "description": job.get('description', job.get('Why', '')),
            "url":         job.get('ApplyURL', job.get('url', '')),
            "location":    job.get('Location', ''),
            "fit_score":   job.get('FitScore', 0),
            "why":         job.get('Why', ''),
        }
        self._current_job = job_normalized   # Guardar para uso en screening

        enriched = await self._bridge.analyze_job(
            job=job_normalized,
            generate_cover_letter=True,
        )

        if enriched.source == "enerd" and enriched.confidence >= 0.5:
            # Fusionar respuestas de ENERD sobre base original
            self.cv_data = {**self._base_cv, **enriched.field_answers}
            if enriched.cover_letter:
                self.cv_data['cover_letter'] = enriched.cover_letter
            print(f"   ✅ ENERD: {len(enriched.field_answers)} campos enriquecidos "
                  f"(confianza={enriched.confidence:.0%})")
            if enriched.clarifications_needed:
                print(f"   ❓ {len(enriched.clarifications_needed)} campos pendientes "
                      f"— ver http://localhost:4010 > Clarificaciones")
        else:
            self.cv_data = self._base_cv.copy()
            print(f"   ⚡ ENERD offline/baja confianza — usando CV_DATA base")
        
    async def click_easy_apply(self, page: Page) -> bool:
        """Click Easy Apply button using JavaScript — handles obfuscated LinkedIn class names."""
        try:
            # Use JS to find the REAL apply button in the job detail area (not sidebar cards)
            clicked = await page.evaluate("""
                () => {
                    const EASY_KEYWORDS = ['easy apply', 'solicitar fácil', 'solicitar facil',
                                           'quick apply', 'solicitar'];
                    const NAV_SKIP      = ['home', 'me', 'jobs', 'messaging', 'notifications',
                                           'skip to', 'for business', 'post a job', 'find a job',
                                           'search', 'premium', 'recruiter'];

                    // Restrict search to the main job view — exclude the sidebar job cards
                    const jobRoot = document.querySelector(
                        '.jobs-details, .job-view-layout, '
                        + '.jobs-unified-top-card, '
                        + '[class*="jobs-details"], '
                        + '[class*="job-view"]'
                    ) || document.querySelector('main') || document;

                    const buttons = Array.from(jobRoot.querySelectorAll('button'));

                    for (const btn of buttons) {
                        const text = (btn.innerText || btn.textContent || '').toLowerCase().trim();
                        const aria = (btn.getAttribute('aria-label') || '').toLowerCase();

                        if (btn.closest('nav, header, [role="navigation"], aside')) continue;
                        if (NAV_SKIP.some(kw => text === kw || text.startsWith(kw + '\\n'))) continue;
                        // Skip multiline texts that are job card previews (> 40 chars)
                        if (text.length > 60) continue;

                        if (EASY_KEYWORDS.some(kw => text === kw || aria.includes(kw))) {
                            const rect = btn.getBoundingClientRect();
                            if (rect.width > 10 && rect.height > 10) {
                                btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                                btn.click();
                                return { clicked: true, text: text, aria: aria };
                            }
                        }
                    }
                    return null;
                }
            """)

            if clicked:
                print(f"   ✅ Clicked Easy Apply (text='{clicked.get('text','')}')")
                await asyncio.sleep(2)
                return True

            # Fallback: standard Playwright selectors
            for selector in [
                'button[aria-label*="Easy Apply"]',
                'button[aria-label*="Solicitar"]',
                'button:has-text("Easy Apply")',
                'button:has-text("Solicitar fácil")',
            ]:
                try:
                    btn = page.locator(selector).first
                    if await btn.count() > 0 and await btn.is_visible(timeout=1500):
                        await btn.click()
                        print(f"   ✅ Clicked Easy Apply (fallback: {selector})")
                        await asyncio.sleep(2)
                        return True
                except Exception:
                    continue

            return False
        except Exception as e:
            print(f"   ❌ Easy Apply click failed: {e}")
            return False
    
    async def fill_contact_info(self, page: Page) -> bool:
        """Fill Contact Info step"""
        print("   📝 Filling contact info...")
        
        try:
            # Email
            try:
                email_field = page.locator('input[id*="email" i]').first
                if await email_field.is_visible(timeout=2000):
                    await email_field.fill(self.cv_data['email'])
                    print(f"      ✓ Email: {self.cv_data['email']}")
            except Exception:
                pass

            # Phone country code
            try:
                phone_country = page.locator('select[id*="phone" i]').first
                if await phone_country.is_visible(timeout=2000):
                    await phone_country.select_option(label=self.cv_data['phone_country'])
                    print(f"      ✓ Phone country: {self.cv_data['phone_country']}")
            except Exception:
                pass

            # Phone number
            try:
                phone_field = page.locator('input[id*="phone" i]').first
                if await phone_field.is_visible(timeout=2000):
                    await phone_field.fill(self.cv_data['phone'])
                    print(f"      ✓ Phone: {self.cv_data['phone']}")
            except Exception:
                pass
            
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            print(f"   ❌ Contact info failed: {e}")
            return False
    
    async def upload_resume(self, page: Page) -> bool:
        """Upload resume if needed"""
        print("   📄 Checking resume...")
        
        try:
            # Check if resume already uploaded
            resume_uploaded = page.locator('text=/Resume|CV|uploaded/i')
            if await resume_uploaded.count() > 0:
                print("      ✓ Resume already uploaded")
                return True
            
            # Look for upload button
            upload_selectors = [
                'input[type="file"]',
                'button:has-text("Upload")',
                'button:has-text("Choose file")'
            ]
            
            for selector in upload_selectors:
                try:
                    uploader = page.locator(selector).first
                    if await uploader.is_visible(timeout=2000):
                        if os.path.exists(self.cv_data['resume_path']):
                            await uploader.set_input_files(self.cv_data['resume_path'])
                            print(f"      ✓ Uploaded: {Path(self.cv_data['resume_path']).name}")
                            await asyncio.sleep(2)
                            return True
                except Exception:
                    continue
            
            print("      - No upload needed")
            return True
            
        except Exception as e:
            print(f"   ⚠️ Resume upload: {e}")
            return True  # Don't fail if can't upload
    
    async def answer_screening_questions(self, page: Page) -> bool:
        """Answer all screening questions intelligently"""
        print("   ❓ Answering screening questions...")
        
        try:
            # Get all form groups (questions)
            form_groups = page.locator('div[data-test-form-element], .jobs-easy-apply-form-section__grouping')
            count = await form_groups.count()
            
            if count == 0:
                print("      - No screening questions")
                return True
            
            print(f"      Found {count} question groups")
            
            for i in range(count):
                group = form_groups.nth(i)
                
                # Get question text
                try:
                    question_text = await group.locator('label, legend, span').first.inner_text()
                    question_lower = question_text.lower()
                    
                    print(f"      Q: {question_text[:80]}...")
                    
                    # STRATEGY 1: Match question keywords to pre-loaded cv_data
                    answer = self._match_screening_answer(question_lower)

                    # STRATEGY 2: ENERD — IA local lee la pregunta + opciones en vivo
                    if not answer:
                        try:
                            # Extraer opciones visibles en el formulario (radio/select)
                            options: list[str] = []
                            radio_labels = group.locator('label')
                            for r in range(await radio_labels.count()):
                                txt = (await radio_labels.nth(r).inner_text()).strip()
                                if txt and len(txt) < 120:
                                    options.append(txt)
                            select_opts = group.locator('select option')
                            for r in range(await select_opts.count()):
                                txt = (await select_opts.nth(r).inner_text()).strip()
                                if txt and txt not in ('', '--', 'Select'):
                                    options.append(txt)

                            print(f"         🧠 ENERD analizando: '{question_text[:60]}' "
                                  f"opciones={options[:4]}")
                            answer = await self._bridge.get_field_answer(
                                field_name  = question_lower[:80],
                                field_label = question_text[:120],
                                field_type  = "radio" if options else "text",
                                job         = self._current_job,
                                options     = options,
                            )
                            if answer:
                                print(f"         🤖 ENERD: '{answer}'")
                            else:
                                print(f"         ❓ ENERD sin respuesta — guardando duda")
                        except Exception as _e:
                            print(f"         ⚠️ ENERD lookup error: {_e}")

                    if answer:
                        filled = await self._fill_question(group, answer, question_lower)
                        if filled:
                            print(f"         A: {answer}")
                        else:
                            print(f"         ⚠️ Could not fill answer")
                    else:
                        print(f"         - Sin respuesta (campo guardado en clarificaciones)")
                    
                except Exception as e:
                    continue
            
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            print(f"   ⚠️ Screening questions: {e}")
            return True  # Don't fail the whole application
    
    def _match_screening_answer(self, question: str) -> Optional[str]:
        """Match question to answer from CV data"""
        
        # English proficiency
        if any(word in question for word in ['english', 'inglés', 'proficiency in english']):
            return self.cv_data['english_proficiency']
        
        # Spanish
        if any(word in question for word in ['spanish', 'español']):
            return self.cv_data['spanish_proficiency']
        
        # Work authorization
        if any(word in question for word in ['work authorization', 'autorización', 'legally authorized']):
            return self.cv_data['work_authorization_mexico']
        
        # Relocation
        if any(word in question for word in ['relocate', 'relocation', 'move to', 'mudarte']):
            return self.cv_data['willing_to_relocate']
        
        # Remote work
        if any(word in question for word in ['remote', 'remoto', 'work from home']):
            return self.cv_data['remote_work']
        
        # Travel
        if any(word in question for word in ['travel', 'viajar', 'available to travel']):
            return self.cv_data['travel_availability']
        
        # Salary
        if any(word in question for word in ['salary', 'salario', 'compensation', 'expectation']):
            if 'mxn' in question or 'pesos' in question:
                return self.cv_data['salary_expectation_mxn']
            else:
                return self.cv_data['salary_expectation_mxn']
        
        # Years experience
        if any(word in question for word in ['years', 'años', 'experience', 'experiencia']):
            return self.cv_data['years_experience']
        
        # Python
        if 'python' in question:
            return self.cv_data['python_experience']
        
        # SQL
        if 'sql' in question:
            return self.cv_data['sql_experience']
        
        # Agile/Scrum
        if any(word in question for word in ['agile', 'scrum', 'ágil']):
            return self.cv_data['agile_experience']
        
        # Power BI
        if 'power bi' in question or 'powerbi' in question:
            return self.cv_data['power_bi_experience']
        
        # ERP
        if 'erp' in question:
            return self.cv_data['erp_experience']
        
        # Industry specific
        if 'banking' in question or 'bank' in question:
            return self.cv_data['banking_experience']
        
        if 'healthcare' in question or 'health' in question:
            return self.cv_data['healthcare_experience']
        
        if 'manufacturing' in question:
            return self.cv_data['manufacturing_experience']
        
        if 'aviation' in question or 'airline' in question:
            return self.cv_data['aviation_experience']
        
        return None
    
    async def _fill_question(self, group, answer: str, question: str) -> bool:
        """Fill a question with appropriate input type"""
        try:
            # Radio buttons (Yes/No, options)
            radio = group.locator('input[type="radio"]')
            if await radio.count() > 0:
                # Find matching option
                labels = group.locator('label')
                for i in range(await labels.count()):
                    label_text = await labels.nth(i).inner_text()
                    if answer.lower() in label_text.lower():
                        await labels.nth(i).click()
                        await asyncio.sleep(0.3)
                        return True
                return False
            
            # Dropdown/Select
            select = group.locator('select')
            if await select.count() > 0:
                try:
                    await select.first.select_option(label=answer)
                    await asyncio.sleep(0.3)
                    return True
                except Exception:
                    # Try by value
                    try:
                        await select.first.select_option(value=answer)
                        await asyncio.sleep(0.3)
                        return True
                    except Exception:
                        return False
            
            # Text input (salary, years, etc)
            text_input = group.locator('input[type="text"], input[type="number"], textarea')
            if await text_input.count() > 0:
                await text_input.first.fill(answer)
                await asyncio.sleep(0.3)
                return True
            
            return False
            
        except Exception as e:
            return False
    
    async def click_next(self, page: Page) -> bool:
        """Click Next/Continue button"""
        try:
            selectors = [
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'button:has-text("Siguiente")',
                'button:has-text("Continuar")',
                'button[aria-label*="Continue"]',
                'button[aria-label*="Next"]'
            ]
            
            for selector in selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=2000) and await button.is_enabled():
                        await button.click()
                        print("   ➡️  Clicked Next")
                        await asyncio.sleep(2)
                        return True
                except Exception:
                    continue

            return False
        except Exception:
            return False
    
    async def submit_application(self, page: Page) -> bool:
        """Submit the final application"""
        try:
            selectors = [
                'button:has-text("Submit application")',
                'button:has-text("Submit")',
                'button:has-text("Enviar")',
                'button:has-text("Send")',
                'button[aria-label*="Submit"]'
            ]
            
            for selector in selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        if self.dry_run:
                            print("   🎯 [DRY RUN] Would submit application")
                            return True
                        else:
                            await button.click()
                            print("   🎯 Application SUBMITTED!")
                            await asyncio.sleep(3)
                            return True
                except Exception:
                    continue

            return False
        except Exception:
            return False
    
    async def detect_apply_type(self, page: Page) -> str:
        """
        Detect if job has Easy Apply or requires External application.
        Uses JavaScript evaluation to find the apply button reliably across
        LinkedIn UI versions (2025/2026).

        Returns:
            "easy_apply" if Easy Apply button found
            "external" if only external apply button found
            "unknown" if no apply button found
        """
        try:
            # ── STEP 0: Check for expired FIRST before anything else ──────────
            # Wait for page content (not just nav bar)
            try:
                await page.wait_for_selector('h1, .jobs-details, .job-view-layout', timeout=8000)
            except Exception:
                pass
            await asyncio.sleep(2)

            body_text = (await page.inner_text('body')).lower()
            expired_signals = [
                'no longer accepting applications',
                'this job is closed',
                'job is no longer available',
                'this listing has expired',
                'ya no acepta solicitudes',
                'oferta cerrada',
                'no longer available',
            ]
            if any(s in body_text for s in expired_signals):
                print("   ⏱️  Job is EXPIRED (no longer accepting applications)")
                return "expired"

            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            # ── STEP 1: JS search — ONLY in the left job detail panel ─────────
            # LinkedIn layout: left panel = job details + apply button
            #                  right panel = sidebar with other job cards
            # We must ignore the sidebar completely.
            result = await page.evaluate("""
                () => {
                    const EASY_KW = ['easy apply', 'solicitar fácil', 'solicitar facil', 'quick apply'];
                    const EXT_KW  = ['apply on company website', 'apply on linkedin'];

                    // Target: the LEFT job content panel only (not the sidebar)
                    // LinkedIn puts the apply button in the top-card area
                    const PANEL_SELECTORS = [
                        '.jobs-details__main-content',
                        '.job-details-jobs-unified-top-card__container--two-pane',
                        '.jobs-unified-top-card',
                        '.job-view-layout',
                        '.jobs-details',
                        'main',
                    ];
                    let panel = null;
                    for (const sel of PANEL_SELECTORS) {
                        panel = document.querySelector(sel);
                        if (panel) break;
                    }
                    if (!panel) panel = document;

                    // Find buttons ONLY within the panel
                    const buttons = Array.from(panel.querySelectorAll('button'));

                    for (const btn of buttons) {
                        // Use trimmed first line only (ignore multiline sidebar card text)
                        const rawText = (btn.innerText || btn.textContent || '');
                        const firstLine = rawText.split('\\n')[0].toLowerCase().trim();
                        const aria = (btn.getAttribute('aria-label') || '').toLowerCase();

                        // Skip nav / header elements
                        if (btn.closest('nav, header, [role="navigation"], aside')) continue;

                        // Match on EXACT easy apply keywords (first line only, ≤ 30 chars)
                        if (firstLine.length <= 30) {
                            if (EASY_KW.some(kw => firstLine === kw || aria.includes(kw))) {
                                const rect = btn.getBoundingClientRect();
                                if (rect.width > 10 && rect.height > 10) {
                                    return {
                                        type: 'easy_apply',
                                        text: firstLine,
                                        aria: aria.slice(0, 60),
                                        cls:  btn.className.slice(0, 80),
                                    };
                                }
                            }
                        }
                    }

                    // Check for external apply link
                    const links = Array.from(panel.querySelectorAll('a, button'));
                    for (const el of links) {
                        const firstLine = (el.innerText || '').split('\\n')[0].toLowerCase().trim();
                        const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                        if (EXT_KW.some(kw => firstLine.includes(kw) || aria.includes(kw))) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 10 && rect.height > 10)
                                return { type: 'external', text: firstLine };
                        }
                    }

                    return null;
                }
            """)

            if result:
                btn_type = result.get('type', 'unknown')
                btn_text = result.get('text', '')
                btn_cls  = result.get('cls', '')
                print(f"   🔍 Detected: {btn_type} — text='{btn_text}'")
                if btn_cls:
                    print(f"       class: {btn_cls[:80]}")
                return btn_type

            # ── STEP 2: Fallback Playwright selectors ─────────────────────────
            await asyncio.sleep(2)
            for sel in [
                'button[aria-label*="Easy Apply"]',
                'button[aria-label*="Solicitar fácil"]',
                'button.jobs-apply-button--top-card',
            ]:
                try:
                    el = page.locator(sel).first
                    if await el.count() > 0 and await el.is_visible(timeout=1500):
                        print(f"   🔍 Easy Apply (fallback): {sel}")
                        return "easy_apply"
                except Exception:
                    continue

            title = await page.title()
            print(f"   ⚠️  No apply button found — {title[:60]}")
            return "unknown"

        except Exception as e:
            print(f"   ⚠️ detect_apply_type error: {e}")
            return "unknown"
    
    async def process_easy_apply(self, job: Dict, page: Page) -> bool:
        """
        Complete Easy Apply workflow from start to finish
        
        Steps:
        1. Navigate to job
        2. Detect apply type (Easy Apply vs External)
        3. Click Easy Apply
        4. Fill contact info
        5. Upload resume
        6. Answer screening questions (loop through all pages)
        7. Review
        8. Submit
        """
        url = job.get('ApplyURL', '')
        role = job.get('Role', 'Unknown')
        company = job.get('Company', 'Unknown')
        
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}🎯 Processing: {role} at {company}")
        print(f"   URL: {url}")
        
        # Step 1: Navigate
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.evaluate("window.scrollTo(0, 0)")

            # If it's a search results URL, click the first job card to load the job detail
            if '/jobs/search/' in page.url or '/jobs/search/' in url:
                print("   🔍 Search URL detected — clicking first job result...")
                try:
                    # Wait for job cards list
                    await page.wait_for_selector(
                        '.jobs-search-results__list-item, .job-card-container, [data-job-id]',
                        timeout=10000
                    )
                    first_card = page.locator(
                        '.jobs-search-results__list-item, .job-card-container'
                    ).first
                    if await first_card.count() > 0:
                        await first_card.click()
                        await asyncio.sleep(2)
                        # Extract currentJobId and navigate to direct job URL
                        import re as _re
                        m = _re.search(r"currentJobId=(\d+)", page.url)
                        if m:
                            job_id = m.group(1)
                            direct_url = f"https://www.linkedin.com/jobs/view/{job_id}"
                            print(f"   ➡️  Navigating direct: {direct_url}")
                            await page.goto(direct_url, wait_until="domcontentloaded", timeout=20000)
                            await asyncio.sleep(3)
                        else:
                            # No jobId extracted — wait for panel
                            try:
                                await page.wait_for_selector(
                                    '.jobs-details, button[aria-label*="Easy Apply"]',
                                    timeout=8000
                                )
                            except Exception:
                                await asyncio.sleep(4)
                        print(f"   ✅ Clicked first result, now at: {page.url[:80]}")
                    else:
                        print("   ⚠️  No job cards found in search results")
                except Exception as e:
                    print(f"   ⚠️  Could not click job result: {e}")

            # Wait for job title to confirm page fully loaded
            try:
                await page.wait_for_selector('h1, .job-details-jobs-unified-top-card__job-title', timeout=8000)
            except Exception:
                pass
            await asyncio.sleep(3)
            print("   ✅ Page loaded")
        except Exception as e:
            print(f"   ❌ Navigation failed: {e}")
            return False
        
        # Step 2: Detect apply type
        apply_type = await self.detect_apply_type(page)
        
        if apply_type == "expired":
            print("   ⏱️  Job expired — marking Skip-Expired in Sheet")
            job['_apply_type'] = 'expired'
            self.update_job_status(job, 'Skip-Expired')
            return False
        elif apply_type == "external":
            print("   ⚠️  This is an EXTERNAL apply (not Easy Apply)")
            job['_apply_type'] = 'external'
            # Capture the external apply URL for manual follow-up
            try:
                ext_href = await page.evaluate('''
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        for (const a of links) {
                            const t = (a.innerText || '').toLowerCase().trim();
                            const h = a.href || '';
                            if ((t === 'apply' || t === 'apply now') && !h.includes('linkedin.com')) {
                                return h;
                            }
                        }
                        return null;
                    }
                ''')
                ext_info = f"external_url={ext_href}" if ext_href else "no external URL found"
                self.chalan_store(
                    f"EXTERNAL: {role} @ {company} — needs manual apply. {ext_info}. LinkedIn: {page.url}",
                    importance=6, tags=["auto_apply", "external", "manual_needed"]
                )
                if ext_href:
                    print(f"   🔗 External URL: {ext_href[:100]}")
            except Exception:
                pass
            self.update_job_status(job, 'External Apply')
            return False
        elif apply_type == "unknown":
            # Check if job is expired / no longer accepting applications
            try:
                page_text = (await page.inner_text('body')).lower()
                expired_signals = [
                    'no longer accepting applications',
                    'this job is closed',
                    'job is no longer available',
                    'this listing has expired',
                    'ya no acepta solicitudes',
                    'oferta cerrada',
                ]
                if any(s in page_text for s in expired_signals):
                    print("   ⏱️  Job EXPIRED — marking in Sheet")
                    self.update_job_status(job, 'Skip-Expired')
                    job['_apply_type'] = 'expired'
                    return False
            except Exception:
                pass

            # --- AI Supervisor: ask what to do ---
            print("   🤖 Calling AI supervisor...")
            decision = await self.ai_supervisor(
                page,
                "Could not find Easy Apply button. Is there a button I'm missing? Should I scroll?",
                extra_context=f"{company} {role}"
            )
            action = decision.get("action", "skip")
            selector = decision.get("selector", "")

            if action == "click" and selector:
                try:
                    el = page.locator(selector).first
                    if await el.count() > 0 and await el.is_visible(timeout=3000):
                        await el.click()
                        await asyncio.sleep(3)
                        # Re-detect after AI click
                        apply_type2 = await self.detect_apply_type(page)
                        if apply_type2 == "easy_apply":
                            print("   ✅ AI found the button — continuing!")
                            # Fall through to Easy Apply flow below
                        else:
                            print("   ❌ AI click didn't reveal Easy Apply")
                            self.chalan_store(
                                f"FAIL: {company} / {role} — AI tried '{selector}' but no Easy Apply appeared. URL: {page.url}",
                                importance=5, tags=["auto_apply", "fail"]
                            )
                            self.update_job_status(job, 'Skip-NoButton')
                            return False
                    else:
                        print(f"   ❌ AI selector not visible: {selector}")
                        self.update_job_status(job, 'Skip-NoButton')
                        return False
                except Exception as ex:
                    print(f"   ❌ AI click failed: {ex}")
                    self.update_job_status(job, 'Skip-NoButton')
                    return False
            elif action == "wait":
                await asyncio.sleep(5)
                apply_type2 = await self.detect_apply_type(page)
                if apply_type2 != "easy_apply":
                    self.update_job_status(job, 'Skip-NoButton')
                    return False
            elif action == "scroll":
                await page.evaluate("window.scrollTo(0, 400)")
                await asyncio.sleep(2)
                apply_type2 = await self.detect_apply_type(page)
                if apply_type2 != "easy_apply":
                    self.update_job_status(job, 'Skip-NoButton')
                    return False
            else:
                # AI said skip or no good option
                self.chalan_store(
                    f"SKIP: {company} / {role} — no Easy Apply button found. AI reason: {decision.get('reason','?')}. URL: {page.url}",
                    importance=4, tags=["auto_apply", "skip"]
                )
                print("   ⚠️  AI decided to skip this job")
                self.update_job_status(job, 'Skip-NoButton')
                return False
        
        print("   ✅ Easy Apply detected")
        
        # Step 3: Click Easy Apply
        if not await self.click_easy_apply(page):
            print("   ❌ Easy Apply button not found")
            return False
        
        # Steps 3-7: Loop through application pages
        max_pages = 10
        for page_num in range(max_pages):
            print(f"\n   📄 Page {page_num + 1}/{max_pages}")
            
            await asyncio.sleep(1)
            
            # Check if we're done (success message)
            try:
                success = page.locator('text=/Application sent|submitted|enviada/i')
                if await success.count() > 0:
                    print("   🎉 Application completed successfully!")
                    self.chalan_store(
                        f"SUCCESS: {role} @ {company} applied via Easy Apply. URL: {url}",
                        importance=8, tags=["auto_apply", "success"]
                    )
                    return True
            except Exception:
                pass
            
            # Fill contact info
            await self.fill_contact_info(page)
            
            # Upload resume
            await self.upload_resume(page)
            
            # Answer screening questions
            await self.answer_screening_questions(page)
            
            # Try to go next
            if await self.click_next(page):
                continue
            
            # Try to submit
            if await self.submit_application(page):
                print("   🎉 Application submitted!")
                return True
            
            # If can't click next or submit, we're stuck
            if page_num > 0:
                print("   ⚠️ Cannot proceed - might be waiting for manual action")
                break
        
        return False
    
    # ── AI Supervisor + Chalan memory ────────────────────────────────────────

    def chalan_recall(self, query: str, limit: int = 5) -> list:
        """Fetch relevant memories from Chalan about linkedin apply outcomes."""
        try:
            url = f"http://localhost:4001/memories?category=linkedin_apply&limit={limit}"
            req = _urllib.Request(url, headers={"Content-Type": "application/json"})
            with _urllib.urlopen(req, timeout=5) as resp:
                memories = json.loads(resp.read())
            # Filter for query relevance (simple substring match)
            q = query.lower()
            return [m for m in memories if q in m.get("content", "").lower()][:limit]
        except Exception:
            return []

    def chalan_store(self, content: str, importance: int = 6, tags: list = None):
        """Save a lesson learned to Chalan memory."""
        try:
            payload = json.dumps({
                "content": content,
                "category": "linkedin_apply",
                "importance": importance,
                "tags": tags or ["auto_apply"]
            }).encode()
            req = _urllib.Request(
                "http://localhost:4001/memory",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with _urllib.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
            return result.get("saved", False)
        except Exception:
            return False

    async def ai_supervisor(self, page, situation: str, extra_context: str = "") -> dict:
        """
        Call LiteLLM when the bot is stuck.
        Returns: {"action": "click|skip|wait|scroll", "selector": "...", "reason": "..."}
        """
        try:
            url   = page.url
            title = await page.title()

            # Collect visible interactive elements
            elements = await page.evaluate("""
                () => {
                    const out = [];
                    document.querySelectorAll('button, [role="button"], a[href*="jobs"]').forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 5 && rect.height > 5) {
                            out.push({
                                tag:  el.tagName,
                                text: (el.innerText || el.textContent || '').trim().slice(0, 60),
                                aria: el.getAttribute('aria-label') || '',
                                cls:  (el.className || '').slice(0, 80)
                            });
                        }
                    });
                    return out.slice(0, 20);
                }
            """)

            # Recall any relevant Chalan memories
            company_hint = extra_context[:40] if extra_context else ""
            memories = self.chalan_recall(company_hint) if company_hint else []
            mem_text = ""
            if memories:
                mem_text = "\nPast experience:\n" + "\n".join(
                    f"  - {m['content']}" for m in memories[:3]
                )

            prompt = (
                f"You supervise a LinkedIn Easy Apply bot.\n"
                f"Situation: {situation}\n"
                f"URL: {url}\n"
                f"Page title: {title}\n"
                f"Extra context: {extra_context}\n"
                f"{mem_text}\n"
                f"Visible elements (buttons/links):\n"
                + json.dumps(elements[:15], ensure_ascii=False) +
                "\n\nWhat should the bot do RIGHT NOW?"
                " Reply ONLY with valid JSON, no markdown:\n"
                '{"action":"click|skip|wait|scroll","selector":"CSS selector if click (else empty)","reason":"brief"}'
            )

            data = json.dumps({
                "model": "qwen2.5:14b",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.1
            }).encode()

            req = _urllib.Request(
                "http://localhost:4000/v1/chat/completions",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer sk-1234567890abcdef"
                },
                method="POST"
            )
            with _urllib.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read())

            raw = result["choices"][0]["message"]["content"].strip()
            # Extract JSON even if model wraps it in ```
            s = raw.find("{")
            e = raw.rfind("}") + 1
            if s != -1 and e > s:
                decision = json.loads(raw[s:e])
                print(f"   🤖 AI says: {decision.get('action','?')} — {decision.get('reason','')[:80]}")
                return decision
        except Exception as ex:
            print(f"   🤖 AI supervisor error: {ex}")
        return {"action": "skip", "selector": "", "reason": "AI supervisor unavailable"}

    async def linkedin_login(self, page: Page) -> bool:
        """Login to LinkedIn - uses stored session first, falls back to form login."""
        # Step 1: Navigate to feed and check if already logged in (via storage_state)
        print("Checking LinkedIn session...")
        try:
            await page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            if any(k in page.url for k in ["feed", "mynetwork", "/jobs"]):
                print("LinkedIn session active (no login needed)\n")
                return True
        except Exception:
            pass

        # Step 2: Session invalid or expired - fall back to credentials login
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")

        if not email or not password:
            print("LinkedIn credentials not found in .env")
            return False

        print("Session expired, logging in with credentials...")
        try:
            await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            await page.wait_for_selector('input[name="session_key"]', timeout=15000)
            await page.fill('input[name="session_key"]', email)
            await page.fill('input[name="session_password"]', password)
            await page.click('button[type="submit"]')
            await asyncio.sleep(5)

            if any(k in page.url for k in ["feed", "mynetwork"]):
                print("Logged in successfully\n")
                return True
            else:
                print(f"Login may have failed - current URL: {page.url}\n")
                return False

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def _classify_job_modality(self, job: Dict) -> str:
        """
        Clasifica una vacante por modalidad para decidir si aplica automático o requiere revisión.

        Reglas de Marcos:
          - remote / home office / hybrid  → AUTO (si FIT >= min_fit)
          - presencial en GDL/Guadalajara  → AUTO (si FIT >= min_fit)
          - presencial fuera de GDL        → REVIEW (color en sheet, columna Sí/No)
          - desconocido                    → AUTO (beneficio de la duda)

        Returns: "auto" | "review" | "skip"
        """
        remote_scope = job.get('RemoteScope', '').lower().strip()
        location     = job.get('Location', '').lower().strip()

        GDL_KEYWORDS    = ['guadalajara', 'gdl', 'jalisco']
        REMOTE_KEYWORDS = ['remote', 'remoto', 'home office', 'wfh', 'hybrid',
                           'híbrido', 'mixto', 'work from home']
        ONSITE_KEYWORDS = ['on-site', 'onsite', 'presencial', 'in-office', 'in office']

        is_remote  = any(w in remote_scope for w in REMOTE_KEYWORDS) or \
                     any(w in location     for w in REMOTE_KEYWORDS)
        is_onsite  = any(w in remote_scope for w in ONSITE_KEYWORDS)
        is_gdl     = any(w in location     for w in GDL_KEYWORDS)

        if is_remote:
            return "auto"
        if is_onsite and is_gdl:
            return "auto"
        if is_onsite and not is_gdl:
            return "review"
        # Sin info clara → beneficio de la duda
        return "auto"

    def get_eligible_jobs(self, min_fit: int = 7, max_jobs: int = 10) -> List[Dict]:
        """
        Obtiene vacantes del sheet de LinkedIn con las reglas de Marcos:
          - FIT score >= min_fit
          - Remoto/Híbrido                   → aplica automático
          - Presencial en GDL                → aplica automático
          - Presencial fuera de GDL          → marca en sheet para revisión manual, NO aplica
        """
        try:
            all_jobs = self.sheet_manager.get_all_jobs(tab='linkedin')

            eligible      = []
            review_jobs   = []
            skipped_fit   = 0
            skipped_no_url= 0

            for job in all_jobs:
                # FIT score — handles "7/10", "7", "70%" formats
                fit = job.get('FitScore', 0)
                try:
                    fit_str = str(fit).strip()
                    if '/' in fit_str:
                        fit = int(fit_str.split('/')[0])   # "7/10" → 7
                    elif fit_str.replace('%','').isdigit():
                        fit = int(fit_str.replace('%',''))
                    elif fit_str.isdigit():
                        fit = int(fit_str)
                    else:
                        fit = 0
                except Exception:
                    fit = 0

                if fit < min_fit:
                    skipped_fit += 1
                    continue

                # URL requerida
                if not job.get('ApplyURL'):
                    skipped_no_url += 1
                    continue

                # Ya aplicó o rechazado
                status = job.get('Status', '').lower()
                if any(w in status for w in ['applied', 'rejected', 'revision', 'skip']):
                    continue

                # Clasificar por modalidad
                modality = self._classify_job_modality(job)

                if modality == "auto":
                    eligible.append(job)
                    if len(eligible) >= max_jobs:
                        break
                elif modality == "review":
                    review_jobs.append(job)

            # Marcar vacantes presenciales fuera de GDL en el sheet
            if review_jobs:
                print(f"\n⚠️  {len(review_jobs)} vacantes presenciales fuera de GDL → marcadas para revisión manual")
                for rjob in review_jobs:
                    self._mark_for_manual_review(rjob)

            print(f"\n📊 Resumen de selección:")
            print(f"   FIT < {min_fit}      : {skipped_fit} omitidas")
            print(f"   Sin URL        : {skipped_no_url} omitidas")
            print(f"   Revisión manual: {len(review_jobs)} presenciales fuera de GDL")
            print(f"   Auto-apply     : {len(eligible)} vacantes\n")
            return eligible

        except Exception as e:
            print(f"❌ Error obteniendo vacantes: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _mark_for_manual_review(self, job: Dict):
        """Marca la fila en el sheet con fondo naranja y columna ReviewNeeded=SI"""
        try:
            row_num = job.get('_row')
            if not row_num:
                return

            # Escribir "REVISION" en la columna Status y nota de ubicación
            location = job.get('Location', 'desconocida')
            self.sheet_manager.update_job(
                row_id=row_num,
                updates={'Status': 'REVISION', 'ReviewNeeded': 'SI - Presencial fuera GDL'},
                tab='linkedin'
            )

            # Color naranja en la fila (señal visual)
            self.sheet_manager.set_row_color(
                row_index=row_num,
                tab='linkedin',
                red=1.0, green=0.6, blue=0.0   # Naranja
            )

            role    = job.get('Role', 'N/A')
            company = job.get('Company', 'N/A')
            print(f"   🟠 Marcada para revisión: {role} @ {company} ({location})")

        except Exception as e:
            print(f"   ⚠️ No se pudo marcar para revisión: {e}")
    
    def update_job_status(self, job: Dict, status: str):
        """Update job status in Sheets"""
        if self.dry_run:
            return
        
        try:
            row_num = job.get('_row')
            if row_num:
                self.sheet_manager.update_job(
                    row_id=row_num,
                    updates={'Status': status},
                    tab='linkedin'
                )
        except Exception as e:
            print(f"⚠️ Could not update status: {e}")
    
    async def run(self, min_fit: int = 7, max_jobs: int = 10):
        """Main execution"""
        print("=" * 80)
        print(f"{'[DRY RUN MODE] ' if self.dry_run else ''}LINKEDIN EASY APPLY AUTOMATION")
        print("=" * 80)
        print(f"Min FIT Score: {min_fit}")
        print(f"Max Jobs: {max_jobs}")
        print(f"Resume: {Path(self.cv_data['resume_path']).name}")
        print("=" * 80)
        
        # Get eligible jobs
        jobs = self.get_eligible_jobs(min_fit, max_jobs)
        
        if not jobs:
            print("❌ No eligible jobs found")
            return
        
        # Launch browser
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Load existing LinkedIn session cookies (Playwright storage_state format)
            _session_candidates = [
                r'C:\Users\MSI\Desktop\ai-job-foundry\data\credentials\linkedin_session.json',
                r'C:\Users\MSI\Desktop\ai-job-foundry\data\credentials\linkedin_auth.json',
            ]
            _storage_state = None
            for _sf in _session_candidates:
                if Path(_sf).exists():
                    _storage_state = _sf
                    print(f'Loading LinkedIn session: {Path(_sf).name}')
                    break
            if not _storage_state:
                print('No saved session found -- will attempt fresh login')

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                storage_state=_storage_state
            )
            
            page = await context.new_page()
            
            # Login
            if not await self.linkedin_login(page):
                await browser.close()
                return
            
            # Process each job
            success_count = 0
            external_count = 0
            expired_count = 0
            failed_count = 0

            for i, job in enumerate(jobs, 1):
                print(f"\n{'='*80}")
                print(f"JOB {i}/{len(jobs)}: {job.get('Role', 'N/A')} @ {job.get('Company', 'N/A')}")
                print(f"{'='*80}")

                # ── ENERD: enriquecer CV con respuestas inteligentes por trabajo ──
                await self.enrich_for_job(job)

                success = await self.process_easy_apply(job, page)

                apply_type = job.get('_apply_type', '')
                if apply_type == 'expired':
                    expired_count += 1
                    print(f"⏱️  EXPIRED: {job.get('Role')}")
                elif apply_type == 'external':
                    external_count += 1
                    print(f"⚠️  EXTERNAL APPLY: {job.get('Role')}")
                elif success:
                    success_count += 1
                    self.update_job_status(job, 'Applied')
                    print(f"✅ SUCCESS: {job.get('Role')}")
                else:
                    failed_count += 1
                    print(f"❌ FAILED: {job.get('Role')}")

                await asyncio.sleep(3)

            await browser.close()

            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Total processed: {len(jobs)}")
            print(f"✅ Easy Apply Success:        {success_count}")
            print(f"⚠️  External Apply (skipped): {external_count}")
            print(f"⏱️  Expired (skipped):         {expired_count}")
            print(f"❌ Failed:                    {failed_count}")
            print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Easy Apply Automation')
    parser.add_argument('--live', action='store_true', help='Live mode (actually apply)')
    parser.add_argument('--min-fit', type=int, default=7, help='Minimum FIT score')
    parser.add_argument('--max-jobs', type=int, default=5, help='Maximum jobs to process')
    
    args = parser.parse_args()
    
    bot = EasyApplyBot(dry_run=not args.live)
    asyncio.run(bot.run(min_fit=args.min_fit, max_jobs=args.max_jobs))
