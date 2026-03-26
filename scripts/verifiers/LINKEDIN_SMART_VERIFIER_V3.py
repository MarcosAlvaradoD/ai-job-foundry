"""
LINKEDIN SMART VERIFIER V3 - FIXED LOGIN & DETECTION
Mejoras vs V2:
- Sin input() bloqueantes
- Cookies persistentes (login una vez)
- Más patrones de detección (ES/EN)
- Mejor manejo de checkpoints
- Logging detallado para debugging
"""
import os
import sys
import json
from pathlib import Path
# Fix: Point to project root (3 levels up from scripts/verifiers/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
from datetime import datetime

load_dotenv()

class LinkedInSmartVerifierV3:
    def __init__(self):
        self.manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        
        # LinkedIn credentials
        self.linkedin_email = os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        
        # Archivo para guardar cookies
        self.cookies_file = Path(project_root) / "data" / "linkedin_cookies.json"
        self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Patrones MEJORADOS de detección (más exhaustivos)
        self.expired_indicators = [
            # Inglés
            "no longer accepting applications",
            "this job is no longer available",
            "posting has been removed",
            "job posting not found",
            "the job you are trying to view",
            "oops! we can't find that job",
            "this job posting has expired",
            "application is no longer available",
            "this job posting is not accepting",
            "job has been closed",
            "position has been filled",
            "page not found",  # ✅ NEW
            "return to search",  # ✅ NEW: LinkedIn redirect pattern
            # ⚠️  REMOVED: "similar jobs" - LinkedIn shows this EVEN on active jobs
            # Español  
            "ya no acepta solicitudes",
            "este empleo ya no está disponible",
            "la publicación fue eliminada",
            "no se encontró el empleo",
            "esta oferta ya no está disponible",
            "el puesto ha sido cubierto",
            "no se aceptan más solicitudes",
            "página no encontrada",  # ✅ NEW
            # ⚠️  REMOVED: "empleos similares" - LinkedIn shows this EVEN on active jobs
        ]
        
        self.active_indicators = [
            # Inglés
            "easy apply",
            "apply now",
            "submit application",
            "apply on company website",
            "save job",
            "see more jobs",
            "report this job",
            "be an early applicant",
            "applicants",  # ✅ NEW: Shows count of applicants
            "posted",  # ✅ NEW: "Posted 2 days ago"
            "reposted",  # ✅ NEW: "Reposted 1 week ago"  
            "actively recruiting",  # ✅ NEW
            # Español
            "postularse fácilmente",
            "postular ahora",
            "postularse",
            "aplicar",
            "guardar empleo",
            "ver más empleos",
            "reportar este empleo",
            "sé de los primeros postulantes",
            "postulantes",  # ✅ NEW
            "publicado hace",  # ✅ NEW
            "republicado",  # ✅ NEW
            "buscando activamente"  # ✅ NEW
        ]
    
    def save_cookies(self, context):
        """Guarda las cookies de sesión para reutilizar"""
        try:
            cookies = context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            print(f"  💾 Cookies saved to {self.cookies_file.name}")
            return True
        except Exception as e:
            print(f"  ⚠️  Failed to save cookies: {e}")
            return False
    
    def load_cookies(self, context):
        """Carga cookies guardadas para evitar login"""
        try:
            if not self.cookies_file.exists():
                print("  ℹ️  No saved cookies found, will need to login")
                return False
            
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            context.add_cookies(cookies)
            print(f"  ✅ Loaded {len(cookies)} cookies from {self.cookies_file.name}")
            return True
        except Exception as e:
            print(f"  ⚠️  Failed to load cookies: {e}")
            return False
    
    def do_linkedin_login(self, page, context):
        """
        Login a LinkedIn con manejo MEJORADO de checkpoints
        - NO usa input() bloqueante
        - Da 30 segundos para resolver checkpoints visualmente
        - Guarda cookies al final
        """
        try:
            print("\n🔐 Attempting LinkedIn login...")
            
            # Navigate to login
            page.goto("https://www.linkedin.com/login", wait_until='domcontentloaded')
            time.sleep(2)
            
            # Fill credentials
            email_input = page.locator('#username')
            email_input.fill(self.linkedin_email)
            time.sleep(0.5)
            
            password_input = page.locator('#password')
            password_input.fill(self.linkedin_password)
            time.sleep(0.5)
            
            # Submit
            login_button = page.locator('button[type="submit"]')
            login_button.click()
            print("  📤 Login form submitted, waiting for response...")
            time.sleep(5)
            
            # Check result
            current_url = page.url
            
            # SUCCESS: Redirected to feed/jobs/mynetwork
            if any(x in current_url for x in ['feed', 'mynetwork', 'jobs']):
                print("  ✅ Login SUCCESSFUL!")
                self.save_cookies(context)
                return True
            
            # CHECKPOINT: Needs verification
            elif 'checkpoint' in current_url or 'challenge' in current_url:
                print("  ⚠️  CHECKPOINT DETECTED!")
                print("  ⏱️  Giving you 30 seconds to solve it VISUALLY in the browser...")
                print("  ⏱️  (Look at the Firefox window and complete the challenge)")
                
                # Wait 30 seconds for manual intervention
                for i in range(30, 0, -5):
                    print(f"  ⏱️  {i} seconds remaining...")
                    time.sleep(5)
                    
                    # Check if checkpoint was solved
                    current_url = page.url
                    if any(x in current_url for x in ['feed', 'mynetwork', 'jobs']):
                        print("  ✅ Checkpoint SOLVED! Login successful!")
                        self.save_cookies(context)
                        return True
                
                print("  ⚠️  Checkpoint not solved in 30 seconds")
                print("  ⚠️  Continuing anyway, results may be UNKNOWN")
                return False
            
            # FAILED: Unknown page
            else:
                print(f"  ❌ Login FAILED - unexpected URL: {current_url}")
                print("  ⚠️  Continuing anyway, results may be UNKNOWN")
                return False
                
        except Exception as e:
            print(f"  ❌ Login ERROR: {str(e)}")
            print("  ⚠️  Continuing without login, results may be UNKNOWN")
            return False
    
    def get_jobs_to_verify(self, status_filter=None, limit=None):
        """
        Obtiene jobs de LinkedIn para verificar
        - Si status_filter=None, verifica TODOS (excepto Applied/Rejected/Expired/Interview)
        - Si status_filter='New', solo verifica Status='New'
        """
        result = self.manager.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range="LinkedIn!A1:Z10000"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
        
        headers = values[0]
        rows = values[1:]
        
        # Column indices
        url_idx = headers.index('ApplyURL') if 'ApplyURL' in headers else -1
        status_idx = headers.index('Status') if 'Status' in headers else -1
        company_idx = headers.index('Company') if 'Company' in headers else -1
        role_idx = headers.index('Role') if 'Role' in headers else -1
        
        jobs = []
        for i, row in enumerate(rows, start=2):
            # Must have URL
            if url_idx < 0 or len(row) <= url_idx or not row[url_idx]:
                continue
            
            # Get status
            current_status = ''
            if status_idx >= 0 and len(row) > status_idx:
                current_status = row[status_idx] if row[status_idx] else ''
            
            # Filter logic
            if status_filter:
                # Specific filter: Must match exactly
                if current_status != status_filter:
                    continue
            else:
                # No filter: Skip only Applied/Rejected/Expired/Interview
                skip_statuses = ['Applied', 'Rejected', 'EXPIRED', 'Interview']
                if current_status in skip_statuses:
                    continue
            
            # Build job dict
            url = row[url_idx]
            company = row[company_idx] if company_idx >= 0 and len(row) > company_idx else "Unknown"
            role = row[role_idx] if role_idx >= 0 and len(row) > role_idx else "Unknown"
            
            jobs.append({
                'row': i,
                'url': url,
                'company': company,
                'role': role,
                'status': current_status
            })
            
            if limit and len(jobs) >= limit:
                break
        
        return jobs
    
    def verify_single_job(self, url, page, debug=False):
        """
        Verifica un job individual
        - debug=True muestra el HTML completo para debugging
        """
        try:
            # Navigate
            try:
                response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                if not response:
                    return {'status': 'ERROR', 'reason': 'No response'}
                
                if response.status == 404:
                    return {'status': 'EXPIRED', 'reason': 'HTTP 404'}
                elif response.status >= 400:
                    return {'status': 'EXPIRED', 'reason': f'HTTP {response.status}'}
                
                # Wait for dynamic content
                time.sleep(3)
                
                # Get full HTML
                full_html = page.content()
                full_text = full_html.lower()
                
                # DEBUG: Save HTML if unknown
                if debug:
                    debug_file = Path(project_root) / "logs" / f"linkedin_debug_{int(time.time())}.html"
                    debug_file.parent.mkdir(parents=True, exist_ok=True)
                    debug_file.write_text(full_html, encoding='utf-8')
                    print(f"  🐛 DEBUG: HTML saved to {debug_file.name}")
                
                # Check EXPIRED indicators
                for indicator in self.expired_indicators:
                    if indicator.lower() in full_text:
                        return {
                            'status': 'EXPIRED',
                            'reason': f'Found: "{indicator}"'
                        }
                
                # Check ACTIVE indicators
                for indicator in self.active_indicators:
                    if indicator.lower() in full_text:
                        return {
                            'status': 'ACTIVE',
                            'reason': f'Found: "{indicator}"'
                        }
                
                # Check title
                title = page.title().lower()
                if any(word in title for word in ['error', '404', 'not found', 'no encontrado']):
                    return {
                        'status': 'EXPIRED',
                        'reason': f'Title error: {title[:50]}'
                    }
                
                # UNKNOWN
                return {
                    'status': 'UNKNOWN',
                    'reason': 'No clear indicators (may need login or new patterns)'
                }
                
            except Exception as nav_error:
                error_msg = str(nav_error)
                if 'timeout' in error_msg.lower():
                    return {'status': 'ERROR', 'reason': 'Timeout (30s)'}
                else:
                    return {'status': 'ERROR', 'reason': f'Nav error: {error_msg[:50]}'}
            
        except Exception as e:
            return {'status': 'ERROR', 'reason': f'Error: {str(e)[:50]}'}
    
    def mark_job_status(self, row, new_status, reason):
        """Marca Status y Why en Google Sheets (LinkedIn tab)"""
        try:
            # Get headers
            result = self.manager.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range="LinkedIn!1:1"
            ).execute()
            
            headers = result.get('values', [[]])[0]
            status_idx = headers.index('Status') if 'Status' in headers else -1
            why_idx = headers.index('Why') if 'Why' in headers else -1
            
            if status_idx < 0:
                return False
            
            # Update Status
            status_cell = f"LinkedIn!{chr(65 + status_idx)}{row}"
            self.manager.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=status_cell,
                valueInputOption='RAW',
                body={'values': [[new_status]]}
            ).execute()
            
            # Update Why (if column exists)
            if why_idx >= 0:
                why_cell = f"LinkedIn!{chr(65 + why_idx)}{row}"
                self.manager.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=why_cell,
                    valueInputOption='RAW',
                    body={'values': [[reason]]}
                ).execute()
            
            return True
        except Exception as e:
            print(f"    ⚠️  Failed to update sheet: {e}")
            return False
    
    def verify_all(self, limit=None, mark_expired=True, delete_expired=False):
        """
        Verificación completa con:
        - Login automático con cookies
        - Sin input() bloqueantes
        - Debugging opcional para UNKNOWNs
        """
        print("\n" + "="*70)
        print("🔍 LINKEDIN SMART VERIFIER V3")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mark as EXPIRED: {'YES' if mark_expired else 'NO'}")
        print(f"Delete EXPIRED: {'YES' if delete_expired else 'NO'}")
        if limit:
            print(f"Limit: {limit} jobs")
        print("="*70 + "\n")
        
        # Check credentials
        if not self.linkedin_email or not self.linkedin_password:
            print("❌ ERROR: LinkedIn credentials not found in .env")
            print("   Required: LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
            return None
        
        # Get jobs
        print("📋 Fetching jobs from LinkedIn tab...")
        jobs = self.get_jobs_to_verify(status_filter=None, limit=limit)
        
        if not jobs:
            print("ℹ️  No jobs to verify (all are Applied/Rejected/EXPIRED/Interview)\n")
            return None
        
        print(f"✅ Found {len(jobs)} jobs to verify\n")
        print("="*70)
        print("🌐 Starting browser with cookies...")
        print("="*70 + "\n")
        
        results = {
            'expired': [],
            'active': [],
            'unknown': [],
            'error': []
        }
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.firefox.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Try loading cookies first
            cookies_loaded = self.load_cookies(context)
            
            if cookies_loaded:
                print("  ℹ️  Testing saved session...")
                page.goto("https://www.linkedin.com/feed", wait_until='domcontentloaded')
                time.sleep(3)
                
                # Check if still logged in
                if 'feed' in page.url:
                    print("  ✅ Session is still VALID! No need to login again.")
                else:
                    print("  ⚠️  Session EXPIRED, need to login again")
                    cookies_loaded = False
            
            # Login if needed
            if not cookies_loaded:
                login_success = self.do_linkedin_login(page, context)
                if not login_success:
                    print("\n⚠️  WARNING: Login did not complete successfully")
                    print("⚠️  Results may be UNKNOWN due to lack of authentication\n")
            
            print()  # Newline
            
            # Process jobs
            for i, job in enumerate(jobs, 1):
                print(f"[{i}/{len(jobs)}] Checking: {job['company']} - {job['role'][:50]}...")
                print(f"  URL: {job['url'][:70]}...")
                
                # Verify
                debug_mode = False  # Set to True for first few UNKNOWNs
                result = self.verify_single_job(job['url'], page, debug=debug_mode)
                status = result['status']
                reason = result['reason']
                
                # Print
                if status == 'EXPIRED':
                    print(f"  ❌ EXPIRED: {reason}")
                    results['expired'].append(job)
                elif status == 'ACTIVE':
                    print(f"  ✅ ACTIVE: {reason}")
                    results['active'].append(job)
                elif status == 'UNKNOWN':
                    print(f"  ❓ UNKNOWN: {reason}")
                    results['unknown'].append(job)
                else:  # ERROR
                    print(f"  ⚠️  ERROR: {reason}")
                    results['error'].append(job)
                
                # Mark in sheet
                if mark_expired and status == 'EXPIRED':
                    if self.mark_job_status(job['row'], 'EXPIRED', reason):
                        print(f"  📝 Marked as EXPIRED in sheet")
                
                print()
                
                # Rate limiting
                time.sleep(3)
            
            browser.close()
        
        # Summary
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        total = len(jobs)
        print(f"Total verified: {total}")
        print(f"  ❌ EXPIRED:   {len(results['expired'])} ({len(results['expired'])/total*100:.1f}%)")
        print(f"  ✅ ACTIVE:    {len(results['active'])} ({len(results['active'])/total*100:.1f}%)")
        print(f"  ❓ UNKNOWN:   {len(results['unknown'])} ({len(results['unknown'])/total*100:.1f}%)")
        print(f"  ⚠️  ERROR:     {len(results['error'])} ({len(results['error'])/total*100:.1f}%)")
        
        if results['unknown']:
            print(f"\nℹ️  {len(results['unknown'])} UNKNOWN results detected")
            print("   Possible causes:")
            print("   1. Login not successful (checkpoint not solved)")
            print("   2. New LinkedIn UI patterns (need to add more indicators)")
            print("   3. LinkedIn showing content behind modals/popups")
            print("\n   💡 Tip: Run with debug=True in verify_single_job to see HTML")
        
        print("="*70 + "\n")
        
        return results


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Smart Verifier V3')
    parser.add_argument('--limit', type=int, help='Limit number of jobs to verify')
    parser.add_argument('--no-mark', action='store_true', help='Do not mark as EXPIRED (report only)')
    
    args = parser.parse_args()
    
    verifier = LinkedInSmartVerifierV3()
    results = verifier.verify_all(
        limit=args.limit,
        mark_expired=not args.no_mark,
        delete_expired=False
    )
