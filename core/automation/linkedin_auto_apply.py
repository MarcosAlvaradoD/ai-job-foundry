"""
LinkedIn Auto-Apply V3 - WITH AUTOMATIC LOGIN
Applies automatically to jobs with FIT SCORE >= 7
NOW INCLUDES: Auto-login from .env credentials + cookie management
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.sheets.sheet_manager import SheetManager
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import re
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInAutoApplyV3:
    def __init__(self):
        self.sheet_manager = SheetManager()
        self.cookies_file = "data/linkedin_cookies.json"
        self.browser_data_dir = "data/browser_data"
        
        # Load LinkedIn credentials from .env
        self.linkedin_email = os.getenv('LINKEDIN_EMAIL')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        
        if not self.linkedin_email or not self.linkedin_password:
            print("[WARNING] LinkedIn credentials not found in .env!")
            print("[INFO] Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file")
        
        # Candidate data from CV
        self.candidate_data = {
            'full_name': 'Marcos Alberto Alvarado de la Torre',
            'first_name': 'Marcos',
            'last_name': 'Alvarado',
            'email': 'markalvati@gmail.com',
            'phone': '+52 33 2332 0358',
            'location': 'Guadalajara, Jalisco, Mexico',
            'city': 'Guadalajara',
            'country': 'Mexico',
            'linkedin_url': 'https://www.linkedin.com/in/marcosalvarado-it',
            'years_experience': '10',
            'current_company': 'Independent Consultant',
            'current_title': 'Project Manager / Business Analyst',
            'website': '',
            'cover_letter': ''  # Will be generated if needed
        }
        
        print("[OK] Auto-Apply V3 initialized (with auto-login support)")
    
    def load_cookies(self, context):
        """Load saved cookies if they exist"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    context.add_cookies(cookies)
                    print(f"[OK] Loaded {len(cookies)} cookies from {self.cookies_file}")
                    return True
            return False
        except Exception as e:
            print(f"[WARNING] Could not load cookies: {e}")
            return False
    
    def save_cookies(self, context):
        """Save current cookies for future use"""
        try:
            cookies = context.cookies()
            os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            print(f"[OK] Saved {len(cookies)} cookies to {self.cookies_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not save cookies: {e}")
            return False
    
    def is_logged_in(self, page):
        """Check if we're logged into LinkedIn"""
        try:
            page.goto('https://www.linkedin.com/feed/', timeout=15000)
            time.sleep(2)
            
            # Check if we're on the feed page (logged in)
            if '/feed' in page.url:
                print("[OK] Already logged into LinkedIn!")
                return True
            
            # Check if we're redirected to login
            if '/login' in page.url or '/checkpoint' in page.url:
                print("[INFO] Not logged in - will attempt auto-login")
                return False
            
            return False
        except Exception as e:
            print(f"[WARNING] Could not verify login status: {e}")
            return False
    
    def login_to_linkedin(self, page):
        """
        Login a LinkedIn usando credenciales del .env.
        Usa wait_for_selector() con múltiples selectores fallback
        para no depender de un solo selector que LinkedIn puede cambiar.
        """
        try:
            if not self.linkedin_email or not self.linkedin_password:
                print("[ERROR] LinkedIn credentials not configured in .env")
                return False

            print("\n[LOGIN] Starting automatic LinkedIn login...")
            print(f"[INFO] Email: {self.linkedin_email}")

            page.goto('https://www.linkedin.com/login', timeout=30000)

            # Esperar a que la página termine de cargar completamente
            try:
                page.wait_for_load_state('networkidle', timeout=10000)
            except Exception:
                pass  # continuar igual si timeout

            # ── Descartar popups de cookies / consent ──────────────────────
            DISMISS_SELECTORS = [
                'button[action-type="ACCEPT"]',
                'button:has-text("Accept")',
                'button:has-text("Aceptar")',
                'button:has-text("Reject")',
                'button:has-text("Allow all")',
                '[data-test-id="accept-btn"]',
            ]
            for dsel in DISMISS_SELECTORS:
                try:
                    btn = page.query_selector(dsel)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(1)
                        print(f"[OK] Consent popup dismissed: {dsel}")
                        break
                except Exception:
                    pass

            # ── Email field ──────────────────────────────────────────────────
            EMAIL_SELECTORS = [
                '#username',
                'input[name="session_key"]',
                'input[type="email"]',
                'input[autocomplete="username"]',
                'input[autocomplete="email"]',
            ]
            # Debug: ver qué página tenemos exactamente
            print(f"[DEBUG] URL pre-login: {page.url}")
            print(f"[DEBUG] Title: {page.title()}")

            # Verificar/esperar que #username sea visible (con fallback a query_selector)
            email_el = None
            for attempt in range(3):
                try:
                    email_el = page.wait_for_selector('#username', state='visible', timeout=6000)
                    if email_el:
                        print(f"[OK] #username visible (intento {attempt+1})")
                        break
                except Exception:
                    # Si no aparece, probar scroll y esperar un poco más
                    try:
                        page.evaluate("window.scrollTo(0,200)")
                        time.sleep(1)
                    except Exception:
                        pass

            if not email_el:
                # Buscar el primer input de email/session_key que sea VISIBLE
                # (LinkedIn renderiza 2 forms: uno oculto SSO y uno visible)
                try:
                    for sel in ('input[name="session_key"]', 'input[type="email"]'):
                        for el in page.query_selector_all(sel):
                            if el.is_visible():
                                email_el = el
                                print(f"[OK] Email visible encontrado via: {sel}")
                                break
                        if email_el:
                            break
                except Exception:
                    pass

            if not email_el:
                print(f"[ERROR] No se encontró campo email. URL: {page.url}")
                # Debug inputs
                try:
                    for inp in page.query_selector_all('input')[:8]:
                        print(f"  input type={inp.get_attribute('type')} "
                              f"id={inp.get_attribute('id')} vis={inp.is_visible()}")
                except Exception:
                    pass
                return False

            # Limpiar + llenar con click → fill (API estándar, sin force)
            email_el.click()
            email_el.fill(self.linkedin_email)
            print(f"[OK] Email ingresado")

            # ── Password ─────────────────────────────────────────────────────
            pwd_el = None
            try:
                pwd_el = page.wait_for_selector('#password', state='visible', timeout=4000)
            except Exception:
                # Buscar el primer input password VISIBLE (puede haber varios ocultos)
                try:
                    for el in page.query_selector_all('input[type="password"]'):
                        if el.is_visible():
                            pwd_el = el
                            print("[OK] Password visible encontrado via query_selector_all")
                            break
                except Exception:
                    pass

            if not pwd_el:
                print("[ERROR] Campo password no encontrado")
                return False

            pwd_el.click()
            pwd_el.fill(self.linkedin_password)
            print("[OK] Password ingresado")

            # ── Submit — Enter en password (evita clickar SSO buttons) ───────
            try:
                pwd_el.press('Enter')
                print("[OK] Login submitted (Enter)")
            except Exception as e:
                print(f"[ERROR] Submit: {e}")
                return False

            print("[CLICK] Login submitted — waiting for navigation...")

            # Esperar que cargue feed o challenge (max 15s)
            try:
                page.wait_for_url(
                    lambda url: '/feed' in url or '/checkpoint' in url or '/challenge' in url,
                    timeout=15000,
                )
            except Exception:
                pass  # si no redirigió, revisamos URL igual

            # ── Challenge / CAPTCHA ──────────────────────────────────────────
            if any(k in page.url for k in ('/checkpoint', '/challenge', '/uas/login-captcha')):
                print("\n" + "="*70)
                print("[SECURITY] LinkedIn requiere verificación manual!")
                print("[ACTION] Completa el check en el browser — esperando 90s...")
                print("="*70 + "\n")
                start = time.time()
                while time.time() - start < 90:
                    time.sleep(3)
                    if '/feed' in page.url:
                        print("[SUCCESS] Verificación completada!")
                        return True
                print("[ERROR] Timeout de verificación (90s)")
                return False

            if '/feed' in page.url:
                print("[SUCCESS] Login exitoso!")
                return True

            print(f"[ERROR] Login falló — URL inesperada: {page.url}")
            return False

        except Exception as e:
            print(f"[ERROR] Login exception: {e}")
            return False

    def ensure_linkedin_session(self, context, page):
        """
        Establece sesión LinkedIn.
        Estrategia: credenciales .env (primario) con cookies locales como caché.
        Si hay cookies y ya estamos logueados, las usamos para ahorra un login.
        Si no, siempre hacemos login con email/password del .env.
        """
        print("\n[SESSION] Checking LinkedIn session...")

        # Intentar cachear sesión con cookies (evita login si ya está activa)
        self.load_cookies(context)

        if self.is_logged_in(page):
            print("[OK] Sesión activa (cookies válidas)")
            return True

        # Cookies expiradas o no existen → login con credenciales .env
        print("[INFO] Sesión inválida — iniciando login con credenciales .env...")
        if self.login_to_linkedin(page):
            self.save_cookies(context)  # guardar cookies frescas para la próxima vez
            return True

        print("[ERROR] Could not establish LinkedIn session")
        return False
    
    def get_high_fit_jobs(self, min_score=7,
                          tabs=('linkedin', 'computrabajo', 'adzuna', 'occ')):
        """Get jobs with FIT SCORE >= min_score and Status=New from all source tabs.

        Each returned job carries '_source_tab' so the runner can route correctly:
          - linkedin.com URL  → LinkedIn Easy Apply / external via LinkedIn redirect
          - other URL         → ExternalApplier direct (Workable, Greenhouse, etc.)
        """
        print(f"\n[SEARCH] Finding jobs with FIT >= {min_score} and Status=New "
              f"across tabs: {', '.join(tabs)}...")

        high_fit        = []
        skipped_applied = 0
        skipped_status  = 0
        by_tab: dict    = {}

        for tab_key in tabs:
            try:
                tab_jobs = self.sheet_manager.get_all_jobs(tab=tab_key)
                tab_count = 0
                for job in tab_jobs:
                    try:
                        fit_score = int(job.get('FitScore', 0) or 0)
                        status    = job.get('Status', '').strip().lower()
                        apply_url = job.get('ApplyURL', '').strip()

                        # Skip terminal statuses
                        if status in ('applied', 'rejected', 'interview', 'offer'):
                            skipped_applied += 1
                            continue

                        # Only "new" or blank (not manually reviewed/deferred)
                        if status not in ('new', ''):
                            skipped_status += 1
                            continue

                        if fit_score >= min_score and apply_url:
                            job['_source_tab'] = tab_key
                            high_fit.append(job)
                            tab_count += 1

                    except Exception as e:
                        print(f"    [WARN] Skipping job ({tab_key}) parse error: {e}")
                        continue

                by_tab[tab_key] = tab_count
            except Exception as e:
                print(f"  [WARN] Could not read tab '{tab_key}': {e}")

        total = len(high_fit)
        print(f"[FOUND] {total} jobs ready for auto-apply:")
        for tab_key, count in by_tab.items():
            if count:
                print(f"  • {tab_key}: {count}")
        if skipped_applied:
            print(f"[SKIP] {skipped_applied} already processed (Applied/Rejected/etc)")
        if skipped_status:
            print(f"[SKIP] {skipped_status} non-New status (manual review pending)")
        return high_fit
    
    def detect_field_type(self, input_element):
        """Detect what type of field this is"""
        try:
            # Get various attributes
            label_text = ""
            placeholder = input_element.get_attribute('placeholder') or ""
            name = input_element.get_attribute('name') or ""
            id_attr = input_element.get_attribute('id') or ""
            aria_label = input_element.get_attribute('aria-label') or ""
            
            # Try to get associated label
            try:
                label = input_element.locator('xpath=../preceding-sibling::label[1]').text_content()
                label_text = label.lower() if label else ""
            except Exception:
                pass
            
            # Combine all text for matching
            combined = f"{label_text} {placeholder} {name} {id_attr} {aria_label}".lower()
            
            # Field type detection
            if any(x in combined for x in ['first name', 'firstname', 'fname']):
                return 'first_name'
            elif any(x in combined for x in ['last name', 'lastname', 'lname']):
                return 'last_name'
            elif any(x in combined for x in ['full name', 'name', 'your name']):
                return 'full_name'
            elif 'email' in combined or 'e-mail' in combined:
                return 'email'
            elif 'phone' in combined or 'mobile' in combined or 'telephone' in combined:
                return 'phone'
            elif any(x in combined for x in ['city', 'location', 'where']):
                return 'location'
            elif 'linkedin' in combined:
                return 'linkedin_url'
            elif any(x in combined for x in ['years', 'experience', 'how long']):
                return 'years_experience'
            elif 'company' in combined:
                return 'current_company'
            elif 'website' in combined or 'portfolio' in combined:
                return 'website'
            
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def fill_form_field(self, input_element, field_type):
        """Fill a form field based on its type"""
        try:
            value = self.candidate_data.get(field_type, '')
            
            if not value:
                print(f"    [SKIP] No data for {field_type}")
                return False
            
            # Clear existing value
            input_element.fill('')
            time.sleep(0.3)
            
            # Type new value
            input_element.type(value, delay=50)
            time.sleep(0.3)
            
            print(f"    [FILL] {field_type}: {value}")
            return True
        except Exception as e:
            print(f"    [ERROR] Failed to fill {field_type}: {e}")
            return False
    
    def handle_easy_apply_form(self, page):
        """Handle Easy Apply form filling"""
        try:
            print("[FORM] Analyzing form fields...")
            
            # Wait for form to load
            time.sleep(2)
            
            # Find all input fields
            inputs = page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"]')
            
            if not inputs:
                print("[WARNING] No input fields found")
                return False
            
            print(f"[FORM] Found {len(inputs)} input fields")
            
            # Fill each field
            filled_count = 0
            for input_elem in inputs:
                field_type = self.detect_field_type(input_elem)
                
                if field_type != 'unknown':
                    if self.fill_form_field(input_elem, field_type):
                        filled_count += 1
            
            print(f"[FORM] Filled {filled_count}/{len(inputs)} fields")
            
            # Handle dropdowns/selects
            selects = page.query_selector_all('select')
            if selects:
                print(f"[FORM] Found {len(selects)} dropdown menus (manual review needed)")
            
            # Handle radio buttons
            radios = page.query_selector_all('input[type="radio"]')
            if radios:
                print(f"[FORM] Found {len(radios)} radio options (manual review needed)")
            
            return filled_count > 0
            
        except Exception as e:
            print(f"[ERROR] Form handling failed: {e}")
            return False
    
    def check_for_next_step(self, page):
        """Check if there's a Next/Continue button"""
        try:
            # Common button texts
            next_buttons = [
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'button:has-text("Review")',
                'button[aria-label*="Continue"]',
                'button[aria-label*="Next"]'
            ]
            
            for selector in next_buttons:
                button = page.query_selector(selector)
                if button and button.is_visible():
                    return button
            
            return None
        except Exception:
            return None

    def check_for_submit(self, page):
        """Check if there's a Submit button"""
        try:
            submit_buttons = [
                'button:has-text("Submit")',
                'button:has-text("Submit application")',
                'button[aria-label*="Submit"]',
                'button[type="submit"]'
            ]
            
            for selector in submit_buttons:
                button = page.query_selector(selector)
                if button and button.is_visible():
                    return button
            
            return None
        except Exception:
            return None

    def apply_to_job(self, job, page, dry_run=False):
        """Apply to a single job (using existing page with session)"""
        company = job.get('Company', 'Unknown')
        role = job.get('Role', 'Unknown')
        apply_url = job.get('ApplyURL', '')
        fit_score = job.get('FitScore', 0)
        created_at = job.get('CreatedAt', '')
        
        print(f"\n{'='*70}")
        print(f"[APPLY] {company} - {role}")
        print(f"[FIT] {fit_score}/10 | Created: {created_at}")
        print(f"[URL] {apply_url}")
        print(f"{'='*70}")
        
        if not apply_url:
            print("[SKIP] No apply URL")
            return False, "No URL"
        
        try:
            page.goto(apply_url, timeout=30000)
            
            # Wait for page load
            time.sleep(3)
            
            # Check if Easy Apply / LinkedIn Apply button exists
            # LinkedIn renombró "Easy Apply" → "LinkedIn Apply" con clase jobs-apply-button
            easy_apply_button = page.query_selector(
                'button:has-text("Easy Apply"), '
                'button[aria-label*="Easy Apply"], '
                'button[aria-label*="easy apply"], '
                'button.jobs-apply-button, '
                '.jobs-apply-button--top-card'
            )

            if not easy_apply_button:
                print("[SKIP] Not an Easy Apply / LinkedIn Apply job")
                return False, "Not Easy Apply"

            print("[FOUND] Easy Apply / LinkedIn Apply button!")
            
            if dry_run:
                print("[DRY-RUN] Would click Easy Apply and fill form")
                return True, "Dry-run success"
            
            # Click Easy Apply
            easy_apply_button.click()
            time.sleep(2)
            
            # Wait for modal
            modal = page.query_selector('[role="dialog"]')
            if not modal:
                print("[ERROR] Application modal not found")
                return False, "Modal not found"
            
            print("[OK] Application modal opened")
            
            # Multi-step form handling
            max_steps = 5
            current_step = 1
            
            while current_step <= max_steps:
                print(f"\n[STEP {current_step}] Processing form...")
                
                # Fill current form
                self.handle_easy_apply_form(page)
                
                time.sleep(2)
                
                # Check for Next/Continue button
                next_button = self.check_for_next_step(page)
                if next_button:
                    print("[CLICK] Next/Continue button")
                    next_button.click()
                    time.sleep(2)
                    current_step += 1
                    continue
                
                # Check for Submit button
                submit_button = self.check_for_submit(page)
                if submit_button:
                    print("[SUBMIT] Ready to submit application")
                    print("[PAUSE] Review form before final submit? (manual step)")
                    
                    # In production, uncomment to actually submit:
                    # submit_button.click()
                    # time.sleep(2)
                    # print("[SUCCESS] Application submitted!")
                    
                    return True, "Form filled (review needed)"
                
                # No next/submit found
                print("[WARNING] No Next or Submit button found")
                break
            
            return False, "Form incomplete"
                
        except PlaywrightTimeout:
            print(f"[ERROR] Page load timeout")
            return False, "Timeout"
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    def update_job_status(self, job, status, notes=""):
        """Update job status in Google Sheets"""
        try:
            # Use _row if already available (set by get_all_jobs)
            row_to_update = job.get('_row')

            if not row_to_update or row_to_update < 2:
                # Fallback: search by Company + Role + CreatedAt
                all_jobs = self.sheet_manager.get_all_jobs(tab="registry")
                for existing_job in all_jobs:
                    if (existing_job.get('CreatedAt') == job.get('CreatedAt') and
                        existing_job.get('Company') == job.get('Company') and
                        existing_job.get('Role') == job.get('Role')):
                        row_to_update = existing_job.get('_row')
                        break

            if not row_to_update or row_to_update < 2:
                print(f"[ERROR] Could not find job in Sheets: {job.get('Company')} - {job.get('Role')}")
                return False

            # Update status and next action
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_data = {
                'Status': status,
                'NextAction': notes if notes else status,
                'SLA_Date': timestamp
            }

            # Determine tab from job source
            job_tab = "linkedin" if "linkedin.com" in job.get('ApplyURL', '').lower() else "registry"
            self.sheet_manager.update_job(row_to_update, update_data, tab=job_tab)
            print(f"[UPDATE] Row {row_to_update} ({job.get('Company')}) → Status={status}")
            return True

        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
            return False
    
    def run(self, dry_run=True, max_applies=5, min_score=7):
        """
        Run auto-apply process with automatic login
        
        Args:
            dry_run: If True, only simulates without submitting
            max_applies: Maximum number of applications per run
            min_score: Minimum FIT score to apply
        """
        print("\n" + "="*70)
        print("[AUTO-APPLY V3] LinkedIn Easy Apply with AUTO-LOGIN")
        print(f"[CONFIG] Dry-run: {dry_run} | Max applies: {max_applies} | Min FIT: {min_score}")
        print("="*70 + "\n")
        
        # Get high FIT jobs
        jobs = self.get_high_fit_jobs(min_score=min_score)
        
        if not jobs:
            print("[INFO] No high-FIT jobs found. Nothing to do.")
            return
        
        print(f"\n[PLAN] Found {len(jobs)} jobs. Will process {min(len(jobs), max_applies)}:")
        for i, job in enumerate(jobs[:max_applies], 1):
            print(f"  {i}. {job['Company']} - {job['Role']} (FIT: {job['FitScore']}/10)")
        
        if dry_run:
            print("\n[DRY-RUN] This is a simulation. Forms will be analyzed but not submitted.")
        else:
            print("\n[LIVE] This is a LIVE run. Applications will be filled (manual submit).")
        
        # Start browser
        print("\n[START] Starting browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Show browser for monitoring
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            # Ensure we have a valid LinkedIn session
            if not self.ensure_linkedin_session(context, page):
                print("\n[ERROR] Could not establish LinkedIn session!")
                print("[ACTION] Please check your credentials in .env file")
                browser.close()
                return
            
            print("\n[OK] LinkedIn session established - starting applications...\n")
            
            results = {
                'success': 0,
                'failed': 0,
                'skipped': 0
            }
            
            for job in jobs[:max_applies]:
                success, reason = self.apply_to_job(job, page, dry_run=dry_run)
                
                if success:
                    results['success'] += 1
                    if not dry_run:
                        self.update_job_status(job, 'Applied', reason)
                elif 'skip' in reason.lower():
                    results['skipped'] += 1
                else:
                    results['failed'] += 1
                
                # Delay between applications
                time.sleep(5)
            
            # Keep browser open for manual review
            print("\n[PAUSE] Browser will stay open for 10 seconds for review...")
            time.sleep(10)
            
            browser.close()
        
        # Summary
        print(f"\n{'='*70}")
        print("[SUMMARY]")
        print(f"  ✅ Success: {results['success']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  ⏭️  Skipped: {results['skipped']}")
        print("="*70)


if __name__ == "__main__":
    auto_apply = LinkedInAutoApplyV3()
    
    # DRY RUN by default (safe testing)
    auto_apply.run(dry_run=True, max_applies=3, min_score=7)
    
    # To run for real (with manual submit step):
    # auto_apply.run(dry_run=False, max_applies=3, min_score=7)
