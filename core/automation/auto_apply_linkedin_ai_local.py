"""
LinkedIn Auto-Applier with LOCAL AI (100% FREE)
No API costs - Uses EasyOCR + LM Studio (Qwen 2.5 14B)

Hybrid approach:
1. Playwright Smart Locators (priority)
2. OCR + Local AI fallback
3. Adaptive form filling

Author: Marcos Alberto Alvarado
Project: AI Job Foundry
Date: 2026-01-27
"""

import asyncio
import os
import sys
import json
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.sheets.sheet_manager import SheetManager
from core.automation.linkedin_ocr_helper import LinkedInOCRHelper


# CV Data - Used for form filling and screening questions
CV_DATA = {
    # Basic info
    "name": "Marcos Alberto Alvarado de la Torre",
    "first_name": "Marcos",
    "last_name": "Alvarado",
    "email": "markalvati@gmail.com",
    "phone": "3323320358",
    "phone_country_code": "+52",
    "location": "Guadalajara, Jalisco, Mexico",
    "city": "Guadalajara",
    "state": "Jalisco",
    "country": "Mexico",
    
    # Professional info
    "years_experience": "10",
    "current_role": "Senior Project Manager / Product Owner / Business Analyst",
    "linkedin": "https://www.linkedin.com/in/marcosalvarado-it",
    "current_company": "Available immediately",
    
    # Skills
    "skills": "Project Management, Product Owner, Business Analysis, ERP Migration, ETL, Data Analysis, BI, Power BI",
    
    # Screening questions - Standard responses
    "screening_responses": {
        # Language proficiency
        "english": "Professional",
        "spanish": "Native",
        
        # Work authorization
        "work_authorization": "Yes",
        "visa_sponsorship": "No",
        
        # Availability
        "available_start": "2 weeks",
        "notice_period": "2 weeks",
        
        # Work preferences
        "remote_work": "Yes",
        "willing_to_relocate": "No",
        "travel_availability": "Yes",
        
        # Salary (adjust per position)
        "salary_expectation_mxn": "50000",  # Monthly in MXN
        "salary_expectation_usd": "3000",    # Monthly in USD
        
        # Technical skills
        "python": "Intermediate",
        "sql": "Advanced",
        "agile": "Expert",
        "scrum": "Advanced",
        "jira": "Advanced",
        "excel": "Advanced",
        "power_bi": "Advanced",
        
        # Industry experience
        "erp_experience": "Yes",
        "banking": "Yes",
        "healthcare": "Yes",
        "manufacturing": "Yes",
        "telecom": "Yes",
        
        # Certifications (in progress)
        "scrum_master": "In progress",
        "pmp": "In progress",
        "six_sigma": "Green Belt completed"
    }
}


class LinkedInAutoApplierLocal:
    """
    Auto-apply to LinkedIn jobs using LOCAL AI (LM Studio) + OCR (EasyOCR)
    100% FREE - No paid APIs required
    """
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize auto-applier
        
        Args:
            dry_run: If True, simulate applications without actually applying
        """
        load_dotenv()
        
        self.dry_run = dry_run
        
        # Google Sheets
        self.sheet_manager = SheetManager()
        
        # OCR Helper
        self.ocr_helper = LinkedInOCRHelper(languages=['en', 'es'], gpu=True)
        
        # LM Studio config (LOCAL, FREE)
        self.llm_url = os.getenv('LLM_URL', 'http://127.0.0.1:11434/v1/chat/completions')
        self.llm_model = os.getenv('LLM_MODEL', 'qwen2.5-14b-instruct')
        
        # CV data
        self.cv_data = CV_DATA
        
        # Stats
        self.applications_submitted = 0
        self.errors = []
        
        print(f"\n{'='*60}")
        print(f"LinkedIn Auto-Applier with LOCAL AI")
        print(f"Mode: {'DRY RUN (Simulation)' if dry_run else 'LIVE (Real Applications)'}")
        print(f"LLM: {self.llm_model} @ {self.llm_url}")
        print(f"OCR: EasyOCR (en, es)")
        print(f"{'='*60}\n")
    
    async def ask_local_ai(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Ask LM Studio (Qwen) for analysis
        
        Args:
            prompt: Question/task for AI
            max_tokens: Max response length
            
        Returns:
            AI response as string, or None if failed
        """
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                
                # Clean JSON markers if present
                content = content.replace('```json', '').replace('```', '').strip()
                
                return content
            else:
                print(f"   ⚠️ LM Studio returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ⚠️ LM Studio error: {e}")
            return None

    async def analyze_page(self, page: Page, screenshot_path: str) -> Dict:
        """
        Analyze LinkedIn page using OCR + Local AI
        
        Returns decision dict:
        {
            "action": "click_easy_apply" | "fill_form" | "click_next" | "submit" | "complete" | "error",
            "reasoning": "why this action",
            "target": {"text": "...", "x": 100, "y": 200},
            "fields_to_fill": [
                {"label": "First Name", "value": "Marcos", "method": "label"}
            ]
        }
        """
        # 1. Extract text elements with OCR
        elements = self.ocr_helper.extract_text_elements(screenshot_path, min_confidence=0.5)
        
        if not elements:
            return {
                "action": "error",
                "reasoning": "No text elements detected by OCR"
            }
        
        # 2. Get element summary for AI
        elements_summary = self.ocr_helper.get_element_summary(elements, max_elements=50)
        
        # 3. Prepare prompt for LM Studio
        prompt = f"""You are analyzing a LinkedIn job application page to help automate the application process.

TEXT ELEMENTS DETECTED (with coordinates):
{elements_summary}

CANDIDATE INFORMATION:
Name: {self.cv_data['name']}
Email: {self.cv_data['email']}
Phone: {self.cv_data['phone']}
Location: {self.cv_data['location']}
Experience: {self.cv_data['years_experience']} years
Current Role: {self.cv_data['current_role']}
Skills: {self.cv_data['skills']}

YOUR TASK:
Analyze the detected text and decide the next action to take.

RESPOND IN JSON FORMAT ONLY (no markdown, no extra text):
{{
    "action": "<one of: click_easy_apply | fill_form | click_next | submit | complete | error>",
    "reasoning": "<brief explanation of why this action>",
    "target": {{
        "text": "<button/link text to click>",
        "x": <x coordinate>,
        "y": <y coordinate>
    }},
    "fields_to_fill": [
        {{"label": "<field label>", "value": "<value from CV>", "method": "label"}}
    ]
}}

PRIORITY ORDER:
1. If you see "Easy Apply", "Solicitar fácil", "Quick Apply" → action: "click_easy_apply"
2. If you see form fields (Name, Email, Phone, etc.) → action: "fill_form"
3. If you see "Next", "Continue", "Siguiente" → action: "click_next"
4. If you see "Submit", "Enviar", "Submit Application" → action: "submit"
5. If you see "Application submitted", "Success" → action: "complete"
6. If confused or can't proceed → action: "error"

IMPORTANT:
- Only fill fields that you can match from the CV data
- For target coordinates, use the center point (x, y) of the button/link
- Be conservative: if not sure, return "error" with reasoning
"""
        
        # 4. Ask LM Studio
        response = await self.ask_local_ai(prompt, max_tokens=1500)
        
        if not response:
            return {
                "action": "error",
                "reasoning": "AI analysis failed - LM Studio not responding"
            }
        
        # 5. Parse JSON response
        try:
            decision = json.loads(response)
            
            # Validate required fields
            if 'action' not in decision:
                return {
                    "action": "error",
                    "reasoning": "AI response missing 'action' field"
                }
            
            return decision
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️ Failed to parse AI response as JSON: {e}")
            print(f"   Raw response: {response[:200]}...")
            return {
                "action": "error",
                "reasoning": f"JSON parse error: {str(e)}"
            }
    
    async def fill_field_smart(self, page: Page, field_info: Dict) -> bool:
        """
        Smart field filling using Playwright locators
        
        Tries multiple strategies:
        1. By label (most reliable)
        2. By placeholder
        3. By name attribute
        
        Args:
            page: Playwright page
            field_info: {"label": "...", "value": "...", "method": "..."}
            
        Returns:
            True if filled successfully
        """
        label = field_info.get('label', '')
        value = field_info.get('value', '')
        
        if not label or not value:
            return False
        
        # Strategy 1: By label
        try:
            field = page.get_by_label(re.compile(label, re.I))
            if await field.is_visible(timeout=2000):
                await field.fill(value)
                print(f"      ✅ Filled '{label}' = '{value}' (by label)")
                await asyncio.sleep(0.5)
                return True
        except Exception as e:
            pass
        
        # Strategy 2: By placeholder
        try:
            field = page.get_by_placeholder(re.compile(label, re.I))
            if await field.is_visible(timeout=2000):
                await field.fill(value)
                print(f"      ✅ Filled '{label}' = '{value}' (by placeholder)")
                await asyncio.sleep(0.5)
                return True
        except Exception as e:
            pass
        
        # Strategy 3: By name attribute
        try:
            field = page.locator(f"input[name*='{label}' i]").first
            if await field.is_visible(timeout=2000):
                await field.fill(value)
                print(f"      ✅ Filled '{label}' = '{value}' (by name)")
                await asyncio.sleep(0.5)
                return True
        except Exception as e:
            pass
        
        print(f"      ⚠️ Could not fill field: '{label}'")
        return False

    async def apply_with_hybrid_approach(self, job: Dict, page: Page) -> bool:
        """
        Hybrid application approach:
        1. Try Playwright smart locators first (fastest, most reliable)
        2. Fallback to OCR + AI if locators fail
        
        Args:
            job: Job dict from Sheets
            page: Playwright page
            
        Returns:
            True if application successful
        """
        url = job.get('ApplyURL', '')
        role = job.get('Role', 'Unknown')
        
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}📋 Applying to: {role}")
        print(f"   URL: {url}")
        
        # Navigate to job page (even in DRY RUN to test detection)
        try:
            print(f"   🌐 Navigating to job page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)  # Let page stabilize
            print(f"   ✅ Page loaded successfully")
        except Exception as e:
            print(f"   ❌ Navigation failed: {e}")
            return False
        
        # Multi-step application process
        max_steps = 10
        for step in range(max_steps):
            print(f"\n   🔄 Step {step+1}/{max_steps}: Analyzing page...")
            
            # PRIORITY 1: Try Playwright smart locators (no OCR needed)
            try:
                # Look for Easy Apply button
                easy_apply_button = page.get_by_role(
                    'button',
                    name=re.compile(r'easy apply|solicitar.*fácil|quick apply|apply', re.I)
                )
                
                if await easy_apply_button.is_visible(timeout=2000):
                    print(f"      ✅ Found 'Easy Apply' button (Playwright locator)")
                    
                    if self.dry_run:
                        print(f"      📝 [DRY RUN] Would click 'Easy Apply' button")
                        # Take screenshot to show what was detected
                        screenshot_path = f"dry_run_detected_apply.png"
                        await page.screenshot(path=screenshot_path)
                        print(f"      📸 Screenshot saved: {screenshot_path}")
                        print(f"      ✅ [DRY RUN] Detection successful - button is clickable")
                        return True  # Success in DRY RUN
                    else:
                        await easy_apply_button.click()
                        print(f"      ✅ Clicked 'Easy Apply' button")
                        await asyncio.sleep(3)
                        continue
            except Exception as e:
                pass  # Fall through to OCR
            
            # PRIORITY 2: OCR + AI fallback
            screenshot_path = f"temp_screenshot_step{step}.png"
            try:
                await page.screenshot(path=screenshot_path, full_page=False)
                
                # Analyze with AI
                ai_decision = await self.analyze_page(page, screenshot_path)
                
                print(f"      🤖 AI Decision: {ai_decision['action']}")
                print(f"         Reasoning: {ai_decision.get('reasoning', 'N/A')}")
                
                # Execute action based on AI decision
                action = ai_decision['action']
                
                if action == 'click_easy_apply':
                    target = ai_decision.get('target', {})
                    if target.get('x') and target.get('y'):
                        if self.dry_run:
                            print(f"      📝 [DRY RUN] Would click: '{target.get('text')}' at ({target['x']}, {target['y']})")
                        else:
                            await page.mouse.click(target['x'], target['y'])
                            print(f"      ✅ Clicked: '{target.get('text')}' at ({target['x']}, {target['y']})")
                            await asyncio.sleep(3)
                    else:
                        print(f"      ⚠️ No coordinates provided for click")
                
                elif action == 'fill_form':
                    fields = ai_decision.get('fields_to_fill', [])
                    if fields:
                        print(f"      📝 {'[DRY RUN] Would fill' if self.dry_run else 'Filling'} {len(fields)} fields...")
                        if not self.dry_run:
                            for field in fields:
                                await self.fill_field_smart(page, field)
                        else:
                            for field in fields:
                                print(f"         - {field.get('label')}: {field.get('value')}")
                    else:
                        print(f"      ⚠️ No fields specified to fill")
                
                elif action in ['click_next', 'submit']:
                    if self.dry_run:
                        print(f"      📝 [DRY RUN] Would click '{action}' button")
                        return True  # Exit DRY RUN here as we've shown intent
                    
                    # Try Playwright locator first
                    try:
                        button = page.get_by_role(
                            'button',
                            name=re.compile(r'next|continue|submit|enviar|siguiente', re.I)
                        )
                        if await button.is_visible(timeout=2000):
                            await button.click()
                            print(f"      ✅ Clicked '{action}' button (Playwright locator)")
                            await asyncio.sleep(3)
                            continue
                    except Exception:
                        # Fallback to OCR coordinates
                        target = ai_decision.get('target', {})
                        if target.get('x') and target.get('y'):
                            await page.mouse.click(target['x'], target['y'])
                            print(f"      ✅ Clicked: '{target.get('text')}' at ({target['x']}, {target['y']})")
                            await asyncio.sleep(3)
                
                elif action == 'complete':
                    if self.dry_run:
                        print(f"      ✅ [DRY RUN] Application would be submitted successfully!")
                        return True
                    print(f"      ✅ Application submitted successfully!")
                    return True
                
                elif action == 'error':
                    print(f"      ❌ AI reported error: {ai_decision.get('reasoning')}")
                    return False
                
                else:
                    print(f"      ⚠️ Unknown action: {action}")
                    return False
                
            except Exception as e:
                print(f"      ❌ Step {step+1} failed: {e}")
            
            finally:
                # Clean up screenshot
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
        
        print(f"   ⚠️ Max steps ({max_steps}) reached without completion")
        return False

    async def linkedin_login(self, page: Page) -> bool:
        """
        Login to LinkedIn using credentials from .env
        
        Returns:
            True if login successful
        """
        linkedin_email = os.getenv('LINKEDIN_EMAIL')
        linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        
        if not linkedin_email or not linkedin_password:
            print("❌ LinkedIn credentials not found in .env")
            return False
        
        print("🔐 Logging into LinkedIn...")
        
        try:
            await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            # Fill email
            await page.fill('input[name="session_key"]', linkedin_email)
            await asyncio.sleep(0.5)
            
            # Fill password
            await page.fill('input[name="session_password"]', linkedin_password)
            await asyncio.sleep(0.5)
            
            # Click sign in
            await page.click('button[type="submit"]')
            await asyncio.sleep(5)
            
            # Check if login successful
            current_url = page.url
            if 'feed' in current_url or 'mynetwork' in current_url:
                print("✅ LinkedIn login successful")
                return True
            else:
                print(f"⚠️ Login may have failed - current URL: {current_url}")
                return False
            
        except Exception as e:
            print(f"❌ LinkedIn login failed: {e}")
            return False
    
    def get_eligible_jobs(self, min_fit: int = 7, max_jobs: int = 10) -> List[Dict]:
        """
        Get jobs from LinkedIn sheet that are eligible for auto-apply
        
        Args:
            min_fit: Minimum FIT score (0-10)
            max_jobs: Maximum number of jobs to process
            
        Returns:
            List of job dicts with _row attribute
        """
        print(f"📊 Fetching jobs from Google Sheets (LinkedIn tab)...")
        
        try:
            all_jobs = self.sheet_manager.get_all_jobs(tab='linkedin')
            
            # Add row numbers (starts at 2 because row 1 is header)
            for i, job in enumerate(all_jobs, start=2):
                job['_row'] = i
            
            # Filter eligible jobs
            eligible = []
            for job in all_jobs:
                # Check if already applied
                status = job.get('Status', '').lower()
                if 'applied' in status:
                    continue
                
                # Check FIT score
                fit_score = job.get('FitScore', 0)
                if isinstance(fit_score, str):
                    try:
                        fit_score = int(fit_score)
                    except Exception:
                        continue
                
                if fit_score >= min_fit:
                    # Check if has ApplyURL
                    if job.get('ApplyURL'):
                        eligible.append(job)
                
                if len(eligible) >= max_jobs:
                    break
            
            print(f"✅ Found {len(eligible)} eligible jobs (FIT >= {min_fit}, not applied, with URL)")
            return eligible
            
        except Exception as e:
            print(f"❌ Error fetching jobs: {e}")
            return []
    
    async def update_job_status(self, job: Dict, applied: bool, notes: str = "") -> bool:
        """
        Update job status in Google Sheets
        
        Args:
            job: Job dict with _row attribute
            applied: Whether application was successful
            notes: Additional notes
            
        Returns:
            True if update successful
        """
        if self.dry_run:
            print(f"   📝 [DRY RUN] Would update Sheets: Status={'Applied' if applied else 'Error'}")
            return True
        
        try:
            row = job.get('_row')
            if not row:
                print(f"   ⚠️ Job missing _row attribute, cannot update")
                return False
            
            updates = {
                'Status': 'Applied' if applied else 'Error',
                'NextAction': f'Auto-applied via AI {datetime.now().strftime("%Y-%m-%d")}' if applied else f'Auto-apply failed: {notes}',
            }
            
            self.sheet_manager.update_job(row, updates, tab='linkedin')
            print(f"   ✅ Updated Google Sheets row {row}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to update Sheets: {e}")
            return False

    async def run(self, min_fit: int = 7, max_jobs: int = 10):
        """
        Main execution method
        
        Args:
            min_fit: Minimum FIT score
            max_jobs: Maximum jobs to process
        """
        print(f"\n{'='*60}")
        print(f"Starting Auto-Apply Process")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Min FIT: {min_fit}, Max Jobs: {max_jobs}")
        print(f"{'='*60}\n")
        
        # 1. Get eligible jobs
        jobs = self.get_eligible_jobs(min_fit=min_fit, max_jobs=max_jobs)
        
        if not jobs:
            print("❌ No eligible jobs found")
            return
        
        print(f"\n📋 Processing {len(jobs)} jobs...\n")
        
        # 2. Start browser (using Chromium for better stability)
        async with async_playwright() as p:
            print("🌐 Launching browser (Chromium)...")
            try:
                browser = await p.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ],
                    timeout=30000  # 30 second timeout
                )
                
                print("✅ Browser launched successfully")
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    ignore_https_errors=True
                )
                
                print("📄 Creating new page...")
                page = await context.new_page()
                print("✅ Page created successfully")
                
            except Exception as e:
                print(f"❌ Failed to launch browser: {e}")
                print("\n💡 Try running: playwright install chromium")
                return
            
            # 3. Login to LinkedIn
            if not self.dry_run:
                login_success = await self.linkedin_login(page)
                if not login_success:
                    print("❌ LinkedIn login failed, aborting")
                    await browser.close()
                    return
            
            # 4. Process each job
            for i, job in enumerate(jobs, 1):
                print(f"\n{'='*60}")
                print(f"Job {i}/{len(jobs)}")
                print(f"{'='*60}")
                
                try:
                    # Apply to job
                    success = await self.apply_with_hybrid_approach(job, page)
                    
                    if success:
                        self.applications_submitted += 1
                        await self.update_job_status(job, applied=True)
                    else:
                        await self.update_job_status(job, applied=False, notes="Application process failed")
                    
                except Exception as e:
                    print(f"   ❌ Error processing job: {e}")
                    self.errors.append({
                        'job': job.get('Role', 'Unknown'),
                        'error': str(e)
                    })
                    await self.update_job_status(job, applied=False, notes=str(e))
                
                # Small delay between applications
                await asyncio.sleep(5)
            
            # 5. Close browser
            await browser.close()
        
        # 6. Print summary
        print(f"\n{'='*60}")
        print(f"AUTO-APPLY SUMMARY")
        print(f"{'='*60}")
        print(f"Jobs processed: {len(jobs)}")
        print(f"Applications submitted: {self.applications_submitted}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\nErrors:")
            for err in self.errors:
                print(f"  - {err['job']}: {err['error']}")
        
        print(f"{'='*60}\n")


# Main execution
async def main():
    """
    Main entry point for testing
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Applier with Local AI')
    parser.add_argument('--live', action='store_true', help='Run in LIVE mode (default: DRY RUN)')
    parser.add_argument('--min-fit', type=int, default=7, help='Minimum FIT score (default: 7)')
    parser.add_argument('--max-jobs', type=int, default=10, help='Maximum jobs to process (default: 10)')
    
    args = parser.parse_args()
    
    applier = LinkedInAutoApplierLocal(dry_run=not args.live)
    await applier.run(min_fit=args.min_fit, max_jobs=args.max_jobs)


if __name__ == "__main__":
    asyncio.run(main())
