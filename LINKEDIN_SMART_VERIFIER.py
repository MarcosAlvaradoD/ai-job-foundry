"""
LINKEDIN SMART VERIFIER V2 - Con LOGIN automático
Verifica jobs de LinkedIn leyendo REALMENTE el contenido
Usa credenciales de .env para hacer login automático
"""
import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
from datetime import datetime

load_dotenv()

class LinkedInSmartVerifier:
    def __init__(self):
        self.manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        
        # LinkedIn credentials
        self.linkedin_email = os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        
        # Textos que indican job expirado en LinkedIn
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
            # Español  
            "ya no acepta solicitudes",
            "este empleo ya no está disponible",
            "la publicación fue eliminada",
            "no se encontró el empleo"
        ]
        
        # Textos que indican job ACTIVO en LinkedIn
        self.active_indicators = [
            "easy apply",
            "apply",
            "save job",
            "guardar empleo",
            "postularse",
            "aplicar",
            "submit application",
            "see more jobs",
            "show more"
        ]
    
    def do_linkedin_login(self, page):
        """
        Hace login en LinkedIn usando credenciales de .env
        """
        try:
            print("\n🔐 Logging into LinkedIn...")
            
            # Navigate to LinkedIn login
            page.goto("https://www.linkedin.com/login", wait_until='domcontentloaded')
            time.sleep(2)
            
            # Fill email
            email_input = page.locator('#username')
            email_input.fill(self.linkedin_email)
            time.sleep(1)
            
            # Fill password
            password_input = page.locator('#password')
            password_input.fill(self.linkedin_password)
            time.sleep(1)
            
            # Click login button
            login_button = page.locator('button[type="submit"]')
            login_button.click()
            time.sleep(5)  # Wait for login to complete
            
            # Check if login was successful
            current_url = page.url
            if 'feed' in current_url or 'mynetwork' in current_url or 'jobs' in current_url:
                print("✅ Login successful!")
                return True
            elif 'checkpoint' in current_url or 'challenge' in current_url:
                print("⚠️  LinkedIn requires verification (checkpoint/challenge)")
                print("   Please complete verification manually in the browser")
                print("   Press Enter when done...")
                input()
                return True
            else:
                print(f"⚠️  Login may have failed. Current URL: {current_url}")
                print("   Press Enter to continue anyway...")
                input()
                return True
                
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            print("   Continuing without login (may get UNKNOWN results)")
            return False
    
    def get_jobs_to_verify(self, status_filter="New", limit=None):
        """
        Obtiene jobs de LinkedIn para verificar
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
        
        # Find column indices
        url_idx = headers.index('ApplyURL') if 'ApplyURL' in headers else -1
        status_idx = headers.index('Status') if 'Status' in headers else -1
        company_idx = headers.index('Company') if 'Company' in headers else -1
        role_idx = headers.index('Role') if 'Role' in headers else -1
        
        jobs = []
        for i, row in enumerate(rows, start=2):  # Row 2 is first data row
            # Skip if no URL
            if url_idx < 0 or len(row) <= url_idx or not row[url_idx]:
                continue
            
            # Filter by status
            if status_idx >= 0 and len(row) > status_idx:
                current_status = row[status_idx] if row[status_idx] else ''
                if status_filter and current_status != status_filter:
                    continue
            
            # Get job info
            url = row[url_idx]
            company = row[company_idx] if company_idx >= 0 and len(row) > company_idx else "Unknown"
            role = row[role_idx] if role_idx >= 0 and len(row) > role_idx else "Unknown"
            
            jobs.append({
                'row': i,
                'url': url,
                'company': company,
                'role': role,
                'current_status': current_status if status_idx >= 0 else ''
            })
            
            if limit and len(jobs) >= limit:
                break
        
        return jobs
    
    def verify_single_job(self, url, page):
        """
        Verifica si un job de LinkedIn está activo o expirado
        REQUIERE sesión activa (login previo)
        """
        try:
            # Navigate to URL
            try:
                response = page.goto(url, wait_until='domcontentloaded')
                
                if not response:
                    return {'status': 'ERROR', 'reason': 'No response from server'}
                
                if response.status >= 400:
                    return {'status': 'EXPIRED', 'reason': f'HTTP {response.status}'}
                
                # Wait for page to load
                time.sleep(3)  # LinkedIn needs time to load dynamic content
                
                # Get ALL text content from page
                full_text = page.content().lower()
                
                # Check for EXPIRED indicators
                for indicator in self.expired_indicators:
                    if indicator.lower() in full_text:
                        return {
                            'status': 'EXPIRED',
                            'reason': f'Found: "{indicator}"',
                            'method': 'content_scan'
                        }
                
                # Check for ACTIVE indicators
                for indicator in self.active_indicators:
                    if indicator.lower() in full_text:
                        return {
                            'status': 'ACTIVE',
                            'reason': f'Found: "{indicator}"',
                            'method': 'content_scan'
                        }
                
                # If no clear indicators, check title
                title = page.title().lower()
                if any(word in title for word in ['error', '404', 'not found']):
                    return {
                        'status': 'EXPIRED',
                        'reason': f'Title indicates error: {title}',
                        'method': 'title_check'
                    }
                
                # Default: UNKNOWN
                return {
                    'status': 'UNKNOWN',
                    'reason': 'No clear indicators found',
                    'method': 'default'
                }
                
            except Exception as nav_error:
                return {
                    'status': 'ERROR',
                    'reason': f'Navigation failed: {str(nav_error)}'
                }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'reason': f'Page error: {str(e)}'
            }
    
    def mark_job_status(self, row, new_status, reason):
        """
        Marca el status de un job en Google Sheets (LinkedIn tab)
        """
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
        
        # Update Why if column exists
        if why_idx >= 0:
            why_cell = f"LinkedIn!{chr(65 + why_idx)}{row}"
            self.manager.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=why_cell,
                valueInputOption='RAW',
                body={'values': [[reason]]}
            ).execute()
        
        return True
    
    def verify_all(self, limit=None, mark_expired=True, delete_expired=False):
        """
        Verifica TODOS los jobs de LinkedIn CON LOGIN
        """
        print("\n" + "="*70)
        print("🔍 LINKEDIN SMART VERIFIER V2 (with auto-login)")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mark as EXPIRED: {'YES' if mark_expired else 'NO'}")
        print(f"Delete EXPIRED: {'YES' if delete_expired else 'NO'}")
        if limit:
            print(f"Limit: {limit} jobs")
        print("="*70 + "\n")
        
        # Verify credentials
        if not self.linkedin_email or not self.linkedin_password:
            print("❌ ERROR: LinkedIn credentials not found in .env")
            print("   Required: LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
            return None
        
        # Get jobs
        print("📋 Fetching jobs from LinkedIn tab...")
        jobs = self.get_jobs_to_verify(status_filter="New", limit=limit)
        
        if not jobs:
            print("❌ No jobs found with Status='New'\n")
            return None
        
        print(f"✅ Found {len(jobs)} jobs to verify\n")
        print("="*70)
        print("🌐 Starting verification (with login)...")
        print("="*70 + "\n")
        
        results = {
            'expired': [],
            'active': [],
            'unknown': [],
            'error': []
        }
        
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)  # headless=False para ver
            page = browser.new_page()
            
            # PASO CRÍTICO: Login PRIMERO
            login_success = self.do_linkedin_login(page)
            
            if not login_success:
                print("⚠️  Login failed, results may be UNKNOWN")
            
            print()  # Newline before job verification
            
            for i, job in enumerate(jobs, 1):
                print(f"[{i}/{len(jobs)}] Checking: {job['company']} - {job['role'][:50]}...")
                print(f"  URL: {job['url'][:60]}...")
                
                # Verify
                result = self.verify_single_job(job['url'], page)
                status = result['status']
                reason = result['reason']
                
                # Print result
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
                    self.mark_job_status(job['row'], 'EXPIRED', reason)
                    print(f"  📝 Marked as EXPIRED in sheet")
                
                print()
                
                # Rate limit
                time.sleep(3)  # 3 seconds between requests
            
            browser.close()
        
        # Summary
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total verified: {len(jobs)}")
        print(f"  ❌ EXPIRED:   {len(results['expired'])} ({len(results['expired'])/len(jobs)*100:.1f}%)")
        print(f"  ✅ ACTIVE:    {len(results['active'])} ({len(results['active'])/len(jobs)*100:.1f}%)")
        print(f"  ❓ UNKNOWN:   {len(results['unknown'])} ({len(results['unknown'])/len(jobs)*100:.1f}%)")
        print(f"  ⚠️  ERROR:     {len(results['error'])} ({len(results['error'])/len(jobs)*100:.1f}%)")
        print("="*70 + "\n")
        
        if delete_expired and results['expired']:
            print("🗑️  Deleting EXPIRED jobs...")
            # TODO: Implement delete
            print("⚠️  Delete not implemented yet")
        
        return results

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, help='Max jobs to verify')
    parser.add_argument('--no-mark', action='store_true', help='Don\'t mark as EXPIRED')
    parser.add_argument('--delete', action='store_true', help='Delete EXPIRED jobs')
    args = parser.parse_args()
    
    verifier = LinkedInSmartVerifier()
    verifier.verify_all(
        limit=args.limit,
        mark_expired=not args.no_mark,
        delete_expired=args.delete
    )

if __name__ == "__main__":
    main()
