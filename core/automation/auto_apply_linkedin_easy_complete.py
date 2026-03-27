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
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.sheets.sheet_manager import SheetManager

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
    
    # Industry    "erp_experience": "Yes",
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
        self.cv_data = CV_DATA
        
    async def click_easy_apply(self, page: Page) -> bool:
        """Click Easy Apply button"""
        try:
            # Multiple ways to find it
            selectors = [
                'button:has-text("Easy Apply")',
                'button:has-text("Solicitar fácil")',
                'button:has-text("Quick Apply")',
                'button.jobs-apply-button'
            ]
            
            for selector in selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        await button.click()
                        print("   ✅ Clicked Easy Apply")
                        await asyncio.sleep(2)
                        return True
                except:
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
            except:
                pass
            
            # Phone country code
            try:
                phone_country = page.locator('select[id*="phone" i]').first
                if await phone_country.is_visible(timeout=2000):
                    await phone_country.select_option(label=self.cv_data['phone_country'])
                    print(f"      ✓ Phone country: {self.cv_data['phone_country']}")
            except:
                pass
            
            # Phone number
            try:
                phone_field = page.locator('input[id*="phone" i]').first
                if await phone_field.is_visible(timeout=2000):
                    await phone_field.fill(self.cv_data['phone'])
                    print(f"      ✓ Phone: {self.cv_data['phone']}")
            except:
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
                except:
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
            # Get all form groups (questions)            form_groups = page.locator('div[data-test-form-element], .jobs-easy-apply-form-section__grouping')
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
                    
                    # STRATEGY: Match question keywords to answers
                    answer = self._match_screening_answer(question_lower)
                    
                    if answer:
                        # Try different input types
                        filled = await self._fill_question(group, answer, question_lower)
                        if filled:
                            print(f"         A: {answer}")
                        else:
                            print(f"         ⚠️ Could not fill answer")
                    else:
                        print(f"         - No matching answer found")
                    
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
                except:
                    # Try by value
                    try:
                        await select.first.select_option(value=answer)
                        await asyncio.sleep(0.3)
                        return True
                    except:
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
                except:
                    continue
            
            return False
        except:
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
                except:
                    continue
            
            return False
        except:
            return False
    
    async def detect_apply_type(self, page: Page) -> str:
        """
        Detect if job has Easy Apply or requires External application
        
        Returns:
            "easy_apply" if Easy Apply button found
            "external" if only external apply button found
        """
        try:
            # Wait for page to fully load (LinkedIn 2026 lazy-loads apply button)
            await asyncio.sleep(5)
            # Ensure top of page is visible (sticky apply bar)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            # FIRST: Check for Easy Apply button (most specific selectors first)
            easy_apply_selectors = [
                # LinkedIn's specific Easy Apply selectors
                'button.jobs-apply-button--top-card',
                'button[aria-label*="Easy Apply"]',
                'button[aria-label*="easy apply"]',
                'button[aria-label*="Solicitar fácil"]',
                'button[aria-label*="Apply to"]',
                'button:has-text("Easy Apply"):visible',
                'button:has-text("Solicitar fácil"):visible',
                'button.jobs-apply-button:has-text("Easy Apply")',
                'button.jobs-apply-button:has-text("Solicitar")',
                # LinkedIn 2025/2026 new UI selectors
                'button[data-live-test-job-apply-button]',
                '.jobs-apply-button',
                'button:has-text("Quick Apply")',
                # Broad last-resort: any Apply button that isn't navigation
                'button:has-text("Apply"):visible',
            ]
            
            for selector in easy_apply_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.count() > 0:
                        if await button.is_visible(timeout=2000):
                            print(f"   🔍 Easy Apply detected (selector: {selector[:40]}...)")
                            return "easy_apply"
                except Exception as sel_err:
                    continue
            
            # SECOND: Check for external apply
            external_selectors = [
                # LinkedIn's external apply selectors
                'a.jobs-apply-button--top-card',
                'a[href*="applyUrl"]',
                'button:has-text("Apply"):visible:not(:has-text("Easy"))',
                'button:has-text("Solicitar"):visible:not(:has-text("fácil"))',
                'a:has-text("Apply on company website")',
                'a[class*="jobs-apply-button"]',
            ]
            
            for selector in external_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.count() > 0:
                        if await button.is_visible(timeout=2000):
                            print(f"   🔍 External apply detected (selector: {selector[:40]}...)")
                            return "external"
                except Exception as sel_err:
                    continue
            
            # THIRD: Try to find ANY apply-related button
            print("   🔍 Searching for any apply button...")
            all_buttons = page.locator('button, a[class*="apply"]')
            count = await all_buttons.count()
            print(f"   Found {count} potential apply buttons")
            
            # Debug: Print first 5 button texts
            for i in range(min(5, count)):
                try:
                    btn = all_buttons.nth(i)
                    text = await btn.inner_text(timeout=1000)
                    print(f"   Button {i}: {text.strip()[:50]}")
                except:
                    continue
            
            return "unknown"
            
        except Exception as e:
            print(f"   ⚠️ Error detecting apply type: {e}")
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
            # Scroll to top so the sticky apply button is visible
            await page.evaluate("window.scrollTo(0, 0)")
            # Wait for job title to confirm page fully loaded
            try:
                await page.wait_for_selector('h1, .job-details-jobs-unified-top-card__job-title', timeout=8000)
            except Exception:
                pass
            await asyncio.sleep(5)
            print("   ✅ Page loaded")
        except Exception as e:
            print(f"   ❌ Navigation failed: {e}")
            return False
        
        # Step 2: Detect apply type
        apply_type = await self.detect_apply_type(page)
        
        if apply_type == "external":
            print("   ⚠️  This is an EXTERNAL apply (not Easy Apply)")
            job['_apply_type'] = 'external'  # Mark for summary
            self.update_job_status(job, 'External Apply')
            return False
        elif apply_type == "unknown":
            print("   ⚠️  Could not detect apply type")
            self.update_job_status(job, 'No Easy Apply')
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
                    return True
            except:
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
    
    async def linkedin_login(self, page: Page) -> bool:
        """Login to LinkedIn"""
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            print("❌ LinkedIn credentials not found in .env")
            return False
        
        print("🔐 Logging into LinkedIn...")
        
        try:
            await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            await page.fill('input[name="session_key"]', email)
            await page.fill('input[name="session_password"]', password)
            await page.click('button[type="submit"]')
            await asyncio.sleep(5)
            
            if 'feed' in page.url or 'mynetwork' in page.url:
                print("✅ Logged in successfully\n")
                return True
            else:
                print("⚠️ Login may have failed\n")
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {e}")
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
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Login
            if not await self.linkedin_login(page):
                await browser.close()
                return
            
            # Process each job
            success_count = 0
            external_count = 0
            failed_count = 0
            
            for i, job in enumerate(jobs, 1):
                print(f"\n{'='*80}")
                print(f"JOB {i}/{len(jobs)}")
                print(f"{'='*80}")
                
                success = await self.process_easy_apply(job, page)
                
                # Check if it was marked as External
                if job.get('_apply_type') == 'external':
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
            print(f"✅ Easy Apply Success: {success_count}")
            print(f"⚠️  External Apply (skipped): {external_count}")
            print(f"❌ Failed: {failed_count}")
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
