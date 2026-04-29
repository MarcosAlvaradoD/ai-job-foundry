"""
UNIVERSAL JOB VERIFIER - Verifica jobs de TODAS las plataformas
LinkedIn, Indeed, Glassdoor - Todo en un solo script

Características:
- Lee REALMENTE el contenido de cada página
- Detecta textos específicos de "expired" por plataforma
- Marca en Google Sheets
- Opción de borrar después
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

class UniversalJobVerifier:
    def __init__(self):
        self.manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        
        # Platform-specific expired indicators
        self.expired_indicators = {
            'glassdoor': [
                "este empleo no esta disponible",
                "este empleo no está disponible",
                "no es posible acceder a su contenido",
                "ya no está disponible",
                "este empleo ha expirado",
                "no se encontró el empleo",
                "page not found",
                "this job is no longer available",
                "job has expired",
                "job posting has been removed",
                "listing is no longer active",
                "no longer available",
                "we couldn't find that job"
            ],
            'linkedin': [
                "no longer accepting applications",
                "this job is no longer available",
                "job posting has been removed",
                "listing expired",
                "position has been filled",
                "no longer available",
                "page not found",
                "404"
            ],
            'indeed': [
                "job has expired",
                "no longer available",
                "this job posting is no longer available",
                "position has been filled",
                "job expired",
                "listing has been removed",
                "page not found",
                "404"
            ]
        }
        
        # Active indicators (job still open)
        self.active_indicators = {
            'glassdoor': [
                "easy apply",
                "aplicar ahora",
                "apply now",
                "postúlate",
                "enviar solicitud"
            ],
            'linkedin': [
                "easy apply",
                "apply",
                "aplicar",
                "save job",
                "guardar empleo"
            ],
            'indeed': [
                "apply now",
                "aplicar ahora",
                "postularse",
                "submit application"
            ]
        }
    
    def detect_platform(self, url):
        """Detecta la plataforma del job"""
        url_lower = url.lower()
        if 'glassdoor' in url_lower:
            return 'glassdoor'
        elif 'linkedin' in url_lower:
            return 'linkedin'
        elif 'indeed' in url_lower:
            return 'indeed'
        return 'unknown'
    
    def get_jobs_to_verify(self, tab_name, status_filter="New", limit=None):
        """Obtiene jobs de una pestaña específica"""
        result = self.manager.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!A1:Z10000"
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
        for i, row in enumerate(rows, start=2):
            # Skip if no URL
            if url_idx < 0 or len(row) <= url_idx or not row[url_idx]:
                continue
            
            # Filter by status
            if status_idx >= 0 and len(row) > status_idx:
                current_status = row[status_idx] if row[status_idx] else ''
                if status_filter and current_status != status_filter:
                    continue
            
            url = row[url_idx]
            company = row[company_idx] if company_idx >= 0 and len(row) > company_idx else "Unknown"
            role = row[role_idx] if role_idx >= 0 and len(row) > role_idx else "Unknown"
            
            jobs.append({
                'row': i,
                'url': url,
                'company': company,
                'role': role,
                'tab': tab_name,
                'platform': self.detect_platform(url)
            })
            
            if limit and len(jobs) >= limit:
                break
        
        return jobs
    
    def verify_single_job(self, job, browser):
        """Verifica si un job está activo o expirado"""
        url = job['url']
        platform = job['platform']
        
        if platform == 'unknown':
            return {'status': 'UNKNOWN', 'reason': 'Platform not detected'}
        
        try:
            page = browser.new_page()
            page.set_default_timeout(30000)
            
            try:
                response = page.goto(url, wait_until='domcontentloaded')
                
                if not response or response.status >= 400:
                    return {
                        'status': 'EXPIRED',
                        'reason': f'HTTP {response.status if response else "no response"}',
                        'method': 'http_status'
                    }
                
                # Wait for content to load
                page.wait_for_timeout(2000)
                
                # Get page content
                full_text = page.content().lower()
                
                # Check EXPIRED indicators for this platform
                for indicator in self.expired_indicators.get(platform, []):
                    if indicator.lower() in full_text:
                        return {
                            'status': 'EXPIRED',
                            'reason': f'Found: "{indicator}"',
                            'method': 'content_scan',
                            'platform': platform
                        }
                
                # Check ACTIVE indicators
                for indicator in self.active_indicators.get(platform, []):
                    if indicator.lower() in full_text:
                        return {
                            'status': 'ACTIVE',
                            'reason': f'Found: "{indicator}"',
                            'method': 'content_scan',
                            'platform': platform
                        }
                
                # Check title
                title = page.title().lower()
                if any(word in title for word in ['error', '404', 'not found', 'expirado']):
                    return {
                        'status': 'EXPIRED',
                        'reason': f'Title indicates error',
                        'method': 'title_check',
                        'platform': platform
                    }
                
                return {
                    'status': 'UNKNOWN',
                    'reason': 'No clear indicators',
                    'method': 'default',
                    'platform': platform
                }
                
            except Exception as nav_error:
                return {
                    'status': 'ERROR',
                    'reason': f'Navigation failed: {str(nav_error)[:100]}'
                }
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'reason': f'Page error: {str(e)[:100]}'
            }
        finally:
            try:
                page.close()
            except Exception:
                pass
    
    def mark_job_status(self, job, new_status, reason):
        """Marca el status de un job"""
        tab = job['tab']
        row = job['row']
        
        # Get headers
        result = self.manager.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab}!1:1"
        ).execute()
        
        headers = result.get('values', [[]])[0]
        status_idx = headers.index('Status') if 'Status' in headers else -1
        why_idx = headers.index('Why') if 'Why' in headers else -1
        
        if status_idx < 0:
            return False
        
        # Update Status
        status_cell = f"{tab}!{chr(65 + status_idx)}{row}"
        self.manager.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=status_cell,
            valueInputOption='RAW',
            body={'values': [[new_status]]}
        ).execute()
        
        # Update Why if exists
        if why_idx >= 0:
            why_cell = f"{tab}!{chr(65 + why_idx)}{row}"
            self.manager.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=why_cell,
                valueInputOption='RAW',
                body={'values': [[reason[:200]]]}  # Limit to 200 chars
            ).execute()
        
        return True
    
    def verify_all_platforms(self, tabs=None, limit_per_tab=None, mark_expired=True):
        """Verifica jobs de todas las plataformas"""
        if tabs is None:
            tabs = ["LinkedIn", "Indeed", "Glassdoor"]
        
        print("\n" + "="*70)
        print("🔍 UNIVERSAL JOB VERIFIER")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tabs: {', '.join(tabs)}")
        print(f"Mark as EXPIRED: {'YES' if mark_expired else 'NO'}")
        if limit_per_tab:
            print(f"Limit per tab: {limit_per_tab}")
        print("="*70 + "\n")
        
        all_results = {
            'expired': [],
            'active': [],
            'unknown': [],
            'error': []
        }
        
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            
            for tab in tabs:
                print(f"\n{'='*70}")
                print(f"📂 PROCESSING TAB: {tab}")
                print(f"{'='*70}\n")
                
                jobs = self.get_jobs_to_verify(tab, status_filter="New", limit=limit_per_tab)
                
                if not jobs:
                    print(f"  No jobs found with Status='New'\n")
                    continue
                
                print(f"  Found {len(jobs)} jobs to verify\n")
                
                for i, job in enumerate(jobs, 1):
                    print(f"  [{i}/{len(jobs)}] {job['company'][:30]} - {job['role'][:40]}...")
                    print(f"    Platform: {job['platform'].upper()}")
                    
                    result = self.verify_single_job(job, browser)
                    status = result['status']
                    reason = result['reason']
                    
                    if status == 'EXPIRED':
                        print(f"    ❌ EXPIRED: {reason}")
                        all_results['expired'].append(job)
                        if mark_expired:
                            self.mark_job_status(job, 'EXPIRED', reason)
                    elif status == 'ACTIVE':
                        print(f"    ✅ ACTIVE: {reason}")
                        all_results['active'].append(job)
                    elif status == 'UNKNOWN':
                        print(f"    ❓ UNKNOWN: {reason}")
                        all_results['unknown'].append(job)
                    else:
                        print(f"    ⚠️  ERROR: {reason}")
                        all_results['error'].append(job)
                    
                    print()
                    time.sleep(3)  # Rate limit
            
            browser.close()
        
        # Summary
        total = sum(len(v) for v in all_results.values())
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"Total verified: {total}")
        print(f"  ❌ EXPIRED:   {len(all_results['expired'])} ({len(all_results['expired'])/total*100:.1f}%)")
        print(f"  ✅ ACTIVE:    {len(all_results['active'])} ({len(all_results['active'])/total*100:.1f}%)")
        print(f"  ❓ UNKNOWN:   {len(all_results['unknown'])} ({len(all_results['unknown'])/total*100:.1f}%)")
        print(f"  ⚠️  ERROR:     {len(all_results['error'])} ({len(all_results['error'])/total*100:.1f}%)")
        print("="*70 + "\n")
        
        return all_results

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tabs', nargs='+', help='Tabs to verify (default: all)')
    parser.add_argument('--limit', type=int, help='Max jobs per tab')
    parser.add_argument('--no-mark', action='store_true', help='Don\'t mark as EXPIRED')
    args = parser.parse_args()
    
    verifier = UniversalJobVerifier()
    verifier.verify_all_platforms(
        tabs=args.tabs,
        limit_per_tab=args.limit,
        mark_expired=not args.no_mark
    )

if __name__ == "__main__":
    main()
