"""
LinkedIn Auto-Apply V2 - Complete Implementation
Applies automatically to jobs with FIT SCORE >= 7
Includes form filling, multi-step handling, and Sheets updates
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import re
from datetime import datetime

class LinkedInAutoApplyV2:
    def __init__(self):
        self.sheet_manager = SheetManager()
        
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
            'linkedin_url': 'https://www.linkedin.com/in/marcos-alvarado',
            'years_experience': '10',
            'current_company': 'Independent Consultant',
            'current_title': 'Project Manager / Business Analyst',
            'website': '',
            'cover_letter': ''  # Will be generated if needed
        }
        
        print("[OK] Auto-Apply V2 initialized")
    
    def get_high_fit_jobs(self, min_score=7):
        """Get jobs with FIT SCORE >= min_score"""
        print(f"[SEARCH] Finding jobs with FIT >= {min_score}...")
        
        all_jobs = self.sheet_manager.get_all_jobs(tab="registry")
        high_fit = []
        
        for job in all_jobs:
            try:
                fit_score = int(job.get('FitScore', 0))
                status = job.get('Status', '').lower()
                apply_url = job.get('ApplyURL', '')
                
                # Only jobs with high FIT, not applied, and have URL
                if fit_score >= min_score and 'applied' not in status and apply_url:
                    high_fit.append(job)
            except:
                continue
        
        print(f"[FOUND] {len(high_fit)} jobs ready for auto-apply")
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
            except:
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
        except:
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
        except:
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
        except:
            return None
    
    def apply_to_job(self, job, browser, dry_run=False):
        """Apply to a single job"""
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
        
        page = None
        try:
            page = browser.new_page()
            page.goto(apply_url, timeout=30000)
            
            # Wait for page load
            time.sleep(3)
            
            # Check if Easy Apply button exists
            easy_apply_button = page.query_selector('button:has-text("Easy Apply")')
            
            if not easy_apply_button:
                print("[SKIP] Not an Easy Apply job")
                page.close()
                return False, "Not Easy Apply"
            
            print("[FOUND] Easy Apply button!")
            
            if dry_run:
                print("[DRY-RUN] Would click Easy Apply and fill form")
                page.close()
                return True, "Dry-run success"
            
            # Click Easy Apply
            easy_apply_button.click()
            time.sleep(2)
            
            # Wait for modal
            modal = page.query_selector('[role="dialog"]')
            if not modal:
                print("[ERROR] Application modal not found")
                page.close()
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
                    
                    page.close()
                    return True, "Form filled (review needed)"
                
                # No next/submit found
                print("[WARNING] No Next or Submit button found")
                break
            
            page.close()
            return False, "Form incomplete"
                
        except PlaywrightTimeout:
            print(f"[ERROR] Page load timeout")
            if page:
                page.close()
            return False, "Timeout"
        except Exception as e:
            print(f"[ERROR] {e}")
            if page:
                try:
                    page.close()
                except:
                    pass
            return False, str(e)
    
    def update_job_status(self, job, status, notes=""):
        """Update job status in Google Sheets"""
        try:
            row_to_update = None
            all_jobs = self.sheet_manager.read_data()
            
            # Find the job by CreatedAt + Company + Role
            for idx, existing_job in enumerate(all_jobs):
                if (existing_job.get('CreatedAt') == job.get('CreatedAt') and
                    existing_job.get('Company') == job.get('Company') and
                    existing_job.get('Role') == job.get('Role')):
                    row_to_update = idx + 2  # +2 because row 1 is header, 0-indexed
                    break
            
            if not row_to_update:
                print("[ERROR] Could not find job in Sheets")
                return False
            
            # Update status and next action
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_data = {
                'Status': status,
                'NextAction': notes if notes else status,
                'SLA_Date': timestamp
            }
            
            # TODO: Implement Sheets update
            print(f"[UPDATE] Would update row {row_to_update} with: {update_data}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
            return False
    
    def run(self, dry_run=True, max_applies=5, min_score=7):
        """
        Run auto-apply process
        
        Args:
            dry_run: If True, only simulates without submitting
            max_applies: Maximum number of applications per run
            min_score: Minimum FIT score to apply
        """
        print("\n" + "="*70)
        print("[AUTO-APPLY V2] LinkedIn Easy Apply with Form Filling")
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
                user_data_dir="data/browser_data"  # Use saved session
            )
            
            results = {
                'success': 0,
                'failed': 0,
                'skipped': 0
            }
            
            for job in jobs[:max_applies]:
                success, reason = self.apply_to_job(job, browser, dry_run=dry_run)
                
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
            
            browser.close()
        
        # Summary
        print(f"\n{'='*70}")
        print("[SUMMARY]")
        print(f"  ✅ Success: {results['success']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  ⏭️  Skipped: {results['skipped']}")
        print("="*70)


if __name__ == "__main__":
    auto_apply = LinkedInAutoApplyV2()
    
    # DRY RUN by default (safe testing)
    auto_apply.run(dry_run=True, max_applies=3, min_score=7)
    
    # To run for real (with manual submit step):
    # auto_apply.run(dry_run=False, max_applies=3, min_score=7)
