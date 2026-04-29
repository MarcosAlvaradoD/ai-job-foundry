"""
GLASSDOOR BULK VERIFIER - Verifica status de todos los jobs
Version 1.0 - Usa Playwright para verificar si jobs estan activos
"""
import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

class GlassdoorVerifier:
    def __init__(self):
        self.manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.results = {
            'active': 0,
            'expired': 0,
            'error': 0,
            'total': 0
        }
    
    def check_job_status(self, url, browser):
        """
        Verifica si un job esta activo o expirado
        Returns: 'ACTIVE', 'EXPIRED', or 'ERROR'
        """
        try:
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Navigate
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            time.sleep(2)  # Wait for dynamic content
            
            # Get page content
            content = page.content().lower()
            
            # Check for expired markers
            expired_markers = [
                'este empleo no esta disponible',
                'este empleo no está disponible',
                'this job is no longer available',
                'job has expired',
                'no longer accepting applications',
                'no es posible acceder a su contenido'
            ]
            
            is_expired = any(marker in content for marker in expired_markers)
            
            context.close()
            
            if is_expired:
                return 'EXPIRED'
            else:
                return 'ACTIVE'
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:50]}")
            return 'ERROR'
    
    def verify_all_jobs(self, max_jobs=None, start_from=0):
        """
        Verifica todos los jobs de Glassdoor con Status=New
        """
        print("\n" + "="*70)
        print("GLASSDOOR BULK VERIFIER")
        print("="*70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Get all Glassdoor jobs
        result = self.manager.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range="Glassdoor!A1:Z1000"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found")
            return
        
        headers = values[0]
        rows = values[1:]
        
        col_map = {header: idx for idx, header in enumerate(headers)}
        
        # Filter only "New" jobs
        jobs_to_check = []
        for i, row in enumerate(rows, start=2):
            status = row[col_map['Status']] if len(row) > col_map.get('Status', 999) else ""
            if status == "New":
                url = row[col_map['ApplyURL']] if len(row) > col_map.get('ApplyURL', 999) else ""
                company = row[col_map['Company']] if len(row) > col_map.get('Company', 999) else "?"
                role = row[col_map['Role']] if len(row) > col_map.get('Role', 999) else "?"
                
                if url:
                    jobs_to_check.append({
                        'row': i,
                        'url': url,
                        'company': company,
                        'role': role
                    })
        
        total = len(jobs_to_check)
        print(f"Found {total} jobs with Status=New")
        
        # Apply limits
        if start_from > 0:
            jobs_to_check = jobs_to_check[start_from:]
            print(f"Starting from job #{start_from+1}")
        
        if max_jobs:
            jobs_to_check = jobs_to_check[:max_jobs]
            print(f"Limiting to {max_jobs} jobs")
        
        print(f"\nVerifying {len(jobs_to_check)} jobs...")
        print("="*70 + "\n")
        
        # Launch browser once
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            
            updates_batch = []
            
            for i, job in enumerate(jobs_to_check, 1):
                self.results['total'] += 1
                
                print(f"[{i}/{len(jobs_to_check)}] {job['company']} - {job['role'][:40]}")
                
                # Check status
                status = self.check_job_status(job['url'], browser)
                
                if status == 'ACTIVE':
                    print(f"   [ACTIVE] Job is available")
                    self.results['active'] += 1
                elif status == 'EXPIRED':
                    print(f"   [EXPIRED] Marking as expired")
                    self.results['expired'] += 1
                    
                    # Prepare batch update
                    updates_batch.append({
                        'row': job['row'],
                        'status': 'EXPIRED',
                        'next_action': f"[{datetime.now().strftime('%Y-%m-%d')}] Auto-verified: Job no longer available"
                    })
                else:
                    print(f"   [ERROR] Could not verify")
                    self.results['error'] += 1
                
                print()  # New line
                
                # Update Sheets every 10 jobs
                if len(updates_batch) >= 10:
                    self._update_sheets_batch(updates_batch)
                    updates_batch = []
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            # Update remaining jobs
            if updates_batch:
                self._update_sheets_batch(updates_batch)
            
            browser.close()
        
        # Print summary
        self._print_summary()
    
    def _update_sheets_batch(self, updates):
        """Update Google Sheets with batch of status changes"""
        if not updates:
            return
        
        print(f"\n   [UPDATING] Saving {len(updates)} changes to Sheets...")
        
        try:
            col_map = self._get_column_map()
            status_col = self._col_index_to_letter(col_map['Status'])
            next_action_col = self._col_index_to_letter(col_map['NextAction'])
            
            batch_data = []
            for update in updates:
                # Status update
                batch_data.append({
                    'range': f'Glassdoor!{status_col}{update["row"]}',
                    'values': [[update['status']]]
                })
                # NextAction update
                batch_data.append({
                    'range': f'Glassdoor!{next_action_col}{update["row"]}',
                    'values': [[update['next_action']]]
                })
            
            body = {'data': batch_data, 'valueInputOption': 'RAW'}
            self.manager.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            print(f"   [SUCCESS] Updated {len(updates)} jobs\n")
            
        except Exception as e:
            print(f"   [ERROR] Failed to update Sheets: {e}\n")
    
    def _get_column_map(self):
        """Get column indices"""
        result = self.manager.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range="Glassdoor!A1:Z1"
        ).execute()
        headers = result.get('values', [[]])[0]
        return {header: idx for idx, header in enumerate(headers)}
    
    def _col_index_to_letter(self, idx):
        """Convert 0-based index to Excel column letter (A, B, C, ...)"""
        result = ""
        idx += 1  # Convert to 1-based
        while idx > 0:
            idx -= 1
            result = chr(65 + (idx % 26)) + result
            idx //= 26
        return result
    
    def _print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total Verified: {self.results['total']}")
        print(f"Active:         {self.results['active']} ({self.results['active']/max(self.results['total'],1)*100:.1f}%)")
        print(f"Expired:        {self.results['expired']} ({self.results['expired']/max(self.results['total'],1)*100:.1f}%)")
        print(f"Errors:         {self.results['error']}")
        print("="*70)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def main():
    verifier = GlassdoorVerifier()
    
    # Test mode: verify first 50 jobs
    print("MODE: EXTENDED TEST (first 50 jobs)")
    print("To verify all jobs, edit script and change max_jobs=None\n")
    
    verifier.verify_all_jobs(max_jobs=50, start_from=0)
    
    print("\n[INFO] To run full verification of all 361 jobs:")
    print("       Edit this file and change max_jobs=10 to max_jobs=None")

if __name__ == "__main__":
    main()
