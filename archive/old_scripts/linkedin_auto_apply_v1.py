"""
LinkedIn Auto-Apply - Complete Version
Applies automatically to jobs with FIT SCORE >= 7
Features: Form filling, status updates, error handling
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager
from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

# User data for form filling
USER_DATA = {
    "first_name": "Marcos Alberto",
    "last_name": "Alvarado de la Torre",
    "full_name": "Marcos Alberto Alvarado de la Torre",
    "email": "markalvati@gmail.com",
    "phone": "+52 33 2332 0358",
    "phone_alt": "3323320358",  # Without country code
    "location": "Guadalajara, Jalisco, Mexico",
    "city": "Guadalajara",
    "state": "Jalisco",
    "country": "Mexico",
    "years_experience": "10",
    "linkedin": "https://www.linkedin.com/in/marcos-alvarado",
    "website": "",
}

class LinkedInAutoApply:
    def __init__(self):
        self.sheet_manager = SheetManager()
        print("[OK] Auto-Apply initialized")
    
    def get_high_fit_jobs(self, min_score=7):
        """Get jobs with FIT SCORE >= min_score"""
        print(f"[SEARCH] Finding jobs with FIT >= {min_score}...")
        
        all_jobs = self.sheet_manager.get_all_jobs('registry')  # Correct method name
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
    
    def fill_form_fields(self, page):
        """
        Automatically fill form fields in LinkedIn Easy Apply modal
        """
        print("[FORM] Detecting and filling fields...")
        
        try:
            # Wait for form to load
            time.sleep(1)
            
            # Get all input fields
            inputs = page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"]')
            
            filled_count = 0
            
            for input_field in inputs:
                try:
                    # Get field attributes
                    field_id = input_field.get_attribute('id') or ''
                    field_name = input_field.get_attribute('name') or ''
                    field_label = input_field.get_attribute('aria-label') or ''
                    field_placeholder = input_field.get_attribute('placeholder') or ''
                    
                    # Combine all attributes for matching
                    field_text = f"{field_id} {field_name} {field_label} {field_placeholder}".lower()
                    
                    # Determine field type and fill
                    value = None
                    
                    if 'first' in field_text and 'name' in field_text:
                        value = USER_DATA['first_name']
                    elif 'last' in field_text and 'name' in field_text:
                        value = USER_DATA['last_name']
                    elif 'email' in field_text:
                        value = USER_DATA['email']
                    elif 'phone' in field_text or 'mobile' in field_text:
                        value = USER_DATA['phone_alt']  # LinkedIn prefers without country code
                    elif 'city' in field_text:
                        value = USER_DATA['city']
                    elif 'linkedin' in field_text:
                        value = USER_DATA['linkedin']
                    elif 'website' in field_text or 'url' in field_text:
                        value = USER_DATA['website']
                    elif 'year' in field_text and 'experience' in field_text:
                        value = USER_DATA['years_experience']
                    
                    # Fill the field if we found a value
                    if value:
                        input_field.fill(value)
                        filled_count += 1
                        print(f"  [✓] Filled: {field_label or field_name or field_id}")
                        time.sleep(0.5)
                
                except Exception as e:
                    print(f"  [!] Error filling field: {e}")
                    continue
            
            print(f"[OK] Filled {filled_count} fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"[ERROR] Form filling failed: {e}")
            return False
    
    def update_job_status(self, job, status, notes=""):
        """
        Update job status in Google Sheets
        """
        try:
            # Get all jobs to find the row
            all_jobs = self.sheet_manager.get_all_jobs('registry')  # Correct method name
            created_at = job.get('CreatedAt', '')
            
            # Find row index (starts at 2 because row 1 is headers)
            row_id = None
            for idx, existing_job in enumerate(all_jobs, start=2):
                if existing_job.get('CreatedAt') == created_at:
                    row_id = idx
                    break
            
            if not row_id:
                print(f"[WARNING] Could not find job in sheets to update")
                return False
            
            # Prepare update data
            update_data = {
                'Status': status,
                'NextAction': 'Wait for response' if status == 'Applied' else notes,
                'Notes': f"Auto-applied on {datetime.now().strftime('%Y-%m-%d %H:%M')}. {notes}"
            }
            
            # Update using sheet manager
            self.sheet_manager.update_job(row_id, update_data)
            print(f"[SHEETS] Updated row {row_id} status to: {status}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to update Sheets: {e}")
            return False
    
    def apply_to_job(self, job, browser):
        """Apply to a single job with complete form filling"""
        company = job.get('Company', 'Unknown')
        role = job.get('Role', 'Unknown')
        apply_url = job.get('ApplyURL', '')
        fit_score = job.get('FitScore', 0)
        
        print(f"\n[APPLY] {company} - {role} (FIT: {fit_score}/10)")
        
        if not apply_url:
            print("[SKIP] No apply URL")
            return False
        
        try:
            page = browser.new_page()
            page.goto(apply_url, timeout=30000)
            
            # Wait for page load
            time.sleep(2)
            
            # Check if Easy Apply button exists
            easy_apply_button = page.query_selector('button:has-text("Easy Apply")')
            
            if easy_apply_button:
                print("[FOUND] Easy Apply button!")
                easy_apply_button.click()
                time.sleep(2)
                
                # Check if modal opened
                modal = page.query_selector('[role="dialog"]')
                if modal:
                    print("[OK] Application modal opened")
                    
                    # Fill form fields
                    filled = self.fill_form_fields(page)
                    
                    if filled:
                        print("[SUBMIT] Ready to submit application")
                        
                        # Look for Next button (multi-step form) or Submit button
                        next_button = page.query_selector('button:has-text("Next")')
                        submit_button = page.query_selector('button:has-text("Submit application")')
                        review_button = page.query_selector('button:has-text("Review")')
                        
                        if next_button:
                            print("[NEXT] Multi-step form detected, clicking Next...")
                            next_button.click()
                            time.sleep(2)
                            
                            # Try to fill next page
                            self.fill_form_fields(page)
                            
                            # Look for submit again
                            submit_button = page.query_selector('button:has-text("Submit application")')
                        
                        if review_button:
                            print("[REVIEW] Clicking Review button...")
                            review_button.click()
                            time.sleep(2)
                            submit_button = page.query_selector('button:has-text("Submit application")')
                        
                        if submit_button and not submit_button.is_disabled():
                            print("[SUBMIT] Submitting application...")
                            submit_button.click()
                            time.sleep(3)
                            
                            # Check for success
                            success = page.query_selector('text=Application sent') or \
                                     page.query_selector('text=Your application was sent')
                            
                            if success:
                                print("[SUCCESS] ✅ Application submitted successfully!")
                                self.update_job_status(job, 'Applied', 'Auto-applied via Easy Apply')
                                page.close()
                                return True
                            else:
                                print("[WARNING] Submit clicked but success message not found")
                                self.update_job_status(job, 'Attempted', 'Form submitted but confirmation unclear')
                                page.close()
                                return True
                        else:
                            print("[SKIP] Submit button not available or disabled")
                            page.close()
                            return False
                    else:
                        print("[SKIP] Could not fill required fields")
                        page.close()
                        return False
                        
                else:
                    print("[WARNING] Modal not found")
                    page.close()
                    return False
            else:
                print("[SKIP] Not an Easy Apply job")
                page.close()
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            try:
                page.close()
            except:
                pass
            return False
    
    def run(self, dry_run=True, max_applies=5):
        """
        Run auto-apply process
        
        Args:
            dry_run: If True, only lists jobs without applying
            max_applies: Maximum number of applications per run
        """
        print("\n" + "="*70)
        print("[AUTO-APPLY] LinkedIn Easy Apply")
        print("="*70 + "\n")
        
        # Get high FIT jobs
        jobs = self.get_high_fit_jobs(min_score=7)
        
        if not jobs:
            print("[INFO] No high-FIT jobs found. Nothing to do.")
            return
        
        print(f"\n[PLAN] Will apply to {min(len(jobs), max_applies)} jobs:")
        for i, job in enumerate(jobs[:max_applies], 1):
            print(f"  {i}. {job['Company']} - {job['Role']} (FIT: {job['FitScore']}/10)")
        
        if dry_run:
            print("\n[DRY-RUN] This is a test run. No actual applications will be sent.")
            print("Run with dry_run=False to actually apply.")
            return
        
        # Real apply
        print("\n[START] Starting browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Show browser
                user_data_dir="data/browser_data"  # Use saved session
            )
            
            applied_count = 0
            
            for job in jobs[:max_applies]:
                if self.apply_to_job(job, browser):
                    applied_count += 1
                
                time.sleep(3)  # Delay between applications
            
            browser.close()
        
        print(f"\n[DONE] Applied to {applied_count}/{max_applies} jobs")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Apply')
    parser.add_argument('--apply', action='store_true', help='Actually apply (default is dry-run)')
    parser.add_argument('--max', type=int, default=3, help='Max applications per run')
    parser.add_argument('--min-score', type=int, default=7, help='Minimum FIT score')
    
    args = parser.parse_args()
    
    auto_apply = LinkedInAutoApply()
    
    # Run with specified parameters
    auto_apply.run(dry_run=not args.apply, max_applies=args.max)
    
    # Usage examples:
    # py linkedin_auto_apply.py                    # Dry-run (list jobs)
    # py linkedin_auto_apply.py --apply            # Actually apply
    # py linkedin_auto_apply.py --apply --max 5    # Apply to 5 jobs
