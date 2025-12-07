#!/usr/bin/env python3
"""
Job Bulletin Email Processor
Processes emails from job boards that contain MULTIPLE job listings in a single email

Supported sources:
- LinkedIn Job Alerts
- Indeed Job Alerts  
- Glassdoor Job Alerts

These are different from individual recruiter emails - they're bulletins with many jobs.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import re
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email import policy
from email.parser import BytesParser

# Load environment
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/spreadsheets']

class JobBulletinProcessor:
    """Processes job bulletin emails with multiple listings"""
    
    def __init__(self):
        self.credentials = self._get_credentials()
        self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # Track processed emails
        self.processed_cache_file = Path(__file__).parent.parent.parent / 'data' / 'state' / 'processed_bulletins.txt'
        self.processed_cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Track emails to delete
        self.emails_to_delete = []
        
        # ✅ NUEVO: Cache de URLs existentes (para evitar rate limit)
        self.existing_urls_cache = {}
        
    def _get_credentials(self):
        """Get OAuth credentials"""
        creds = None
        token_path = "data/credentials/token.json"
        credentials_path = "data/credentials/credentials.json"
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def get_processed_ids(self) -> set:
        """Load processed bulletin IDs"""
        if self.processed_cache_file.exists():
            with open(self.processed_cache_file, 'r') as f:
                return set(line.strip() for line in f)
        return set()
    
    def save_processed_id(self, email_id: str):
        """Save processed bulletin ID"""
        with open(self.processed_cache_file, 'a') as f:
            f.write(f"{email_id}\n")
    
    def load_existing_urls(self, tab_name: str):
        """
        Carga TODAS las URLs existentes en el sheet UNA SOLA VEZ
        
        Args:
            tab_name: Nombre de la pestaña
        """
        if tab_name in self.existing_urls_cache:
            return  # Ya está cargado
        
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{tab_name}!F:F"  # Columna F = ApplyURL
            ).execute()
            
            values = result.get('values', [])
            
            # Convertir a set para búsqueda rápida
            self.existing_urls_cache[tab_name] = {row[0] for row in values if row}
            
            print(f"   📋 Loaded {len(self.existing_urls_cache[tab_name])} existing URLs from {tab_name}")
            
        except Exception as e:
            print(f"   ⚠️  Error loading URLs: {e}")
            self.existing_urls_cache[tab_name] = set()
    
    def check_job_exists_in_sheet(self, job_url: str, tab_name: str) -> bool:
        """
        Verifica si un job ya existe en el sheet comparando ApplyURL
        USA CACHE LOCAL para evitar rate limits
        
        Args:
            job_url: URL del job a verificar
            tab_name: Nombre de la pestaña
        
        Returns:
            True si el job ya existe, False si es nuevo
        """
        # Verificar contra cache (no API)
        if tab_name not in self.existing_urls_cache:
            return False  # Si no hay cache, asumir que es nuevo
        
        return job_url in self.existing_urls_cache[tab_name]
    
    def get_email_age_days(self, message: dict) -> int:
        """
        Obtiene la edad del email en días
        
        Args:
            message: Mensaje de Gmail API
        
        Returns:
            Edad del email en días
        """
        try:
            from email.utils import parsedate_to_datetime
            
            # Buscar header 'Date'
            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'].lower() == 'date':
                    email_date_str = header['value']
                    email_date = parsedate_to_datetime(email_date_str)
                    
                    # Calcular diferencia
                    now = datetime.now(email_date.tzinfo)
                    age_days = (now - email_date).days
                    
                    return age_days
            
            return 0  # Si no se encuentra fecha, asumir reciente
            
        except Exception as e:
            print(f"   ⚠️  Error getting email age: {e}")
            return 0
    
    def mark_email_for_deletion(self, email_id: str):
        """Marca un email para ser eliminado al final del proceso"""
        self.emails_to_delete.append(email_id)
    
    def delete_marked_emails(self):
        """Elimina todos los emails marcados para eliminación"""
        if not self.emails_to_delete:
            return
        
        print(f"\n🗑️  Eliminando {len(self.emails_to_delete)} emails procesados...")
        
        deleted_count = 0
        for email_id in self.emails_to_delete:
            try:
                self.gmail_service.users().messages().trash(
                    userId='me',
                    id=email_id
                ).execute()
                deleted_count += 1
            except Exception as e:
                print(f"   ⚠️  Error deleting email {email_id}: {e}")
        
        print(f"   ✅ {deleted_count}/{len(self.emails_to_delete)} emails movidos a papelera")
        
        # Limpiar lista
        self.emails_to_delete = []
    
    def extract_linkedin_jobs(self, html_content: str) -> List[Dict]:
        """Extract job listings from LinkedIn bulletin email"""
        jobs = []
        
        # LinkedIn pattern: Job title usually in <a> tags with specific classes
        # This is a simplified pattern - may need adjustment based on actual emails
        title_pattern = r'<a[^>]*>([^<]+(?:Manager|Director|Lead|Analyst|Engineer|Developer)[^<]*)</a>'
        company_pattern = r'<div[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</div>'
        location_pattern = r'<div[^>]*class="[^"]*location[^"]*"[^>]*>([^<]+)</div>'
        
        # Find job URLs
        url_pattern = r'https://www\.linkedin\.com/jobs/view/\d+'
        urls = re.findall(url_pattern, html_content)
        
        # Extract titles (simplified - adjust based on actual HTML)
        titles = re.findall(title_pattern, html_content, re.IGNORECASE)
        
        for i, url in enumerate(urls):
            job = {
                'Source': 'LinkedIn',
                'ApplyURL': url,
                'Role': titles[i] if i < len(titles) else 'Unknown Role',
                'Company': 'Unknown',  # Would need more parsing
                'Location': 'Unknown',
                'CreatedAt': datetime.now().isoformat(),
                'Status': 'New'
            }
            jobs.append(job)
        
        return jobs
    
    def extract_indeed_jobs(self, html_content: str, text_content: str) -> List[Dict]:
        """Extract job listings from Indeed bulletin email"""
        jobs = []
        
        # Indeed URLs
        url_pattern = r'https://www\.indeed\.com[^\s"<>]+'
        urls = re.findall(url_pattern, html_content)
        
        # Job titles from text (Indeed often has clean text format)
        # Pattern: Title followed by company
        lines = text_content.split('\n')
        
        current_job = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect job titles (usually have keywords)
            if any(keyword in line.lower() for keyword in ['manager', 'director', 'lead', 'analyst', 'engineer', 'developer', 'specialist']):
                if current_job and current_job.get('Role'):
                    jobs.append(current_job)
                current_job = {
                    'Source': 'Indeed',
                    'Role': line,
                    'Company': 'Unknown',
                    'Location': 'Unknown',
                    'CreatedAt': datetime.now().isoformat(),
                    'Status': 'New'
                }
        
        # Add last job
        if current_job and current_job.get('Role'):
            jobs.append(current_job)
        
        # Add URLs to jobs
        for i, job in enumerate(jobs):
            if i < len(urls):
                job['ApplyURL'] = urls[i]
        
        return jobs
    
    def extract_glassdoor_jobs(self, html_content: str) -> List[Dict]:
        """
        Extract job listings from Glassdoor bulletin email
        
        Glassdoor emails structure:
        - Job info in <table> elements
        - Title in <p> with font-weight:600 (14px)
        - Company in <p> before title
        - Location in <p> after title  
        - Salary in <p> with k$ pattern
        - job_listing_id in tracking pixel URL
        """
        jobs = []
        
        try:
            # Extract job_listing_id from tracking URL (Pattern 4 - works!)
            job_id_pattern = r'jobAlertAlert&amp;utm_content=ja-jobpos\d+-(\d+)'
            job_ids = re.findall(job_id_pattern, html_content)
            
            # Extract job titles (font-weight:600, 14px)
            title_pattern = r'<p style="font-size:14px;line-height:1\.4;margin:0;font-weight:600">([^<]+)</p>'
            titles = re.findall(title_pattern, html_content)
            
            # Extract companies (appears before title in table structure)
            company_pattern = r'<p style="font-size:12px;line-height:1\.33;margin:0;font-weight:400;white-space:normal">([^<]+)</p>'
            companies = re.findall(company_pattern, html_content)
            
            # Extract locations (simpler pattern)
            location_pattern = r'<p style="font-size:12px;line-height:1\.33;margin:0;margin-top:4px">([^<$]+)</p>'
            locations = re.findall(location_pattern, html_content)
            
            # Extract salaries (pattern with k$)
            salary_pattern = r'<p style="font-size:12px;line-height:1\.33;margin:0;margin-top:4px">(\d+\s*k\$[^<]*)</p>'
            salaries = re.findall(salary_pattern, html_content)
            
            # Build jobs from extracted data
            for i, title in enumerate(titles):
                # Construct URL from job_listing_id
                job_url = f"https://www.glassdoor.com/job-listing/JL_{job_ids[i]}.htm" if i < len(job_ids) else "Unknown"
                
                job = {
                    'Source': 'Glassdoor',
                    'ApplyURL': job_url,
                    'Role': title.strip(),
                    'Company': companies[i].strip() if i < len(companies) else 'Unknown',
                    'Location': locations[i].strip() if i < len(locations) else 'Unknown',
                    'Comp': salaries[i].strip() if i < len(salaries) else '',
                    'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': 'New'
                }
                jobs.append(job)
            
            print(f"   🔍 Extracted {len(titles)} titles, {len(companies)} companies, {len(job_ids)} job IDs")
            
        except Exception as e:
            print(f"   ⚠️  Error extracting Glassdoor jobs: {e}")
        
        return jobs
    
    def detect_bulletin_type(self, sender: str, subject: str) -> Optional[str]:
        """Detect if email is a job bulletin and which type"""
        sender_lower = sender.lower()
        subject_lower = subject.lower()
        
        if 'linkedin' in sender_lower or 'jobalerts-noreply@linkedin.com' in sender_lower:
            return 'linkedin'
        elif 'indeed' in sender_lower or 'alert@indeed.com' in sender_lower:
            return 'indeed'
        elif 'glassdoor' in sender_lower or 'noreply@glassdoor.com' in sender_lower:
            return 'glassdoor'
        
        return None
    
    def parse_email(self, email_data: dict) -> tuple:
        """Parse email and extract content"""
        try:
            msg_bytes = base64.urlsafe_b64decode(email_data['raw'])
            msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
            
            subject = msg.get('Subject', '')
            sender = msg.get('From', '')
            
            # Get HTML content
            html_content = ""
            text_content = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        html_content = part.get_content()
                    elif part.get_content_type() == 'text/plain':
                        text_content = part.get_content()
            else:
                content = msg.get_content()
                if msg.get_content_type() == 'text/html':
                    html_content = content
                else:
                    text_content = content
            
            return subject, sender, html_content, text_content
        except Exception as e:
            print(f"Error parsing email: {e}")
            return "", "", "", ""
    
    def save_to_sheets(self, jobs: List[Dict], tab_name: str = "Jobs"):
        """Save jobs to Google Sheets"""
        if not jobs:
            return 0
        
        # Get headers
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id,
            range=f"{tab_name}!A1:Z1"
        ).execute()
        
        headers = result.get('values', [[]])[0]
        
        if not headers:
            # Create headers if not exist
            headers = list(jobs[0].keys())
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f"{tab_name}!A1",
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
        
        # Prepare rows
        rows = []
        for job in jobs:
            row = [job.get(h, '') for h in headers]
            rows.append(row)
        
        # Append rows
        if rows:
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f"{tab_name}!A2",
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()
            
            # ✅ NUEVO: Actualizar cache con URLs guardadas
            if tab_name not in self.existing_urls_cache:
                self.existing_urls_cache[tab_name] = set()
            
            for job in jobs:
                url = job.get('ApplyURL', '')
                if url:
                    self.existing_urls_cache[tab_name].add(url)
        
        return len(rows)
    
    def process_bulletins(self, max_emails: int = 50):
        """Main processing function"""
        print("\n" + "="*70)
        print("📧 JOB BULLETIN PROCESSOR")
        print("="*70)
        print("Processing job alert emails from LinkedIn, Indeed, and Glassdoor...")
        print("="*70 + "\n")
        
        # Get bulletins - SOLO emails con ofertas de trabajo
        query = (
            'from:(noreply@glassdoor.com OR jobs-noreply@linkedin.com OR noreply@indeed.com) '
            'subject:(empleos OR jobs OR "nuevos empleos" OR "new jobs" OR postúlate OR apply) '
            'newer_than:7d'
        )
        results = self.gmail_service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_emails
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found in JOBS/Inbound")
            return
        
        # Load processed IDs
        processed_ids = self.get_processed_ids()
        
        print(f"Found {len(messages)} emails to check")
        print(f"Already processed: {len(processed_ids)} IDs\n")
        
        # ✅ NUEVO: Cargar URLs existentes UNA SOLA VEZ (evita rate limit)
        print("📋 Loading existing job URLs...")
        self.load_existing_urls('Glassdoor')
        self.load_existing_urls('LinkedIn')
        self.load_existing_urls('Indeed')
        print()
        
        total_jobs_found = 0
        bulletins_processed = 0
        
        for msg_ref in messages:
            msg_id = msg_ref['id']
            
            # Skip if already processed
            if msg_id in processed_ids:
                print(f"⏭️  Already processed: {msg_id[:16]}...")
                continue
            
            # Get full message
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=msg_id,
                format='raw'
            ).execute()
            
            # ✅ NUEVO: Verificar edad del email
            email_age = self.get_email_age_days(message)
            if email_age > 7:
                print(f"⏭️  Skipping old email ({email_age} days old)")
                self.save_processed_id(msg_id)  # Marcar para no reprocessar
                continue
            
            # Parse email
            subject, sender, html_content, text_content = self.parse_email(message)
            
            # Detect bulletin type
            bulletin_type = self.detect_bulletin_type(sender, subject)
            
            if not bulletin_type:
                # Not a bulletin, skip
                print(f"⏭️  Not a job bulletin: {subject[:50]}... (from: {sender[:30]}...)")
                continue
            
            print(f"📨 Processing {bulletin_type.upper()} bulletin:")
            print(f"   Subject: {subject[:60]}...")
            
            # Extract jobs based on type
            jobs = []
            if bulletin_type == 'linkedin':
                jobs = self.extract_linkedin_jobs(html_content)
            elif bulletin_type == 'indeed':
                jobs = self.extract_indeed_jobs(html_content, text_content)
            elif bulletin_type == 'glassdoor':
                jobs = self.extract_glassdoor_jobs(html_content)
            
            if jobs:
                print(f"   ✅ Found {len(jobs)} job listings")
                
                # ✅ NUEVO: Filtrar duplicados ANTES de guardar
                tab_name = bulletin_type.capitalize()
                unique_jobs = []
                duplicates_found = 0
                
                for job in jobs:
                    job_url = job.get('ApplyURL', '')
                    if job_url and self.check_job_exists_in_sheet(job_url, tab_name):
                        duplicates_found += 1
                    else:
                        unique_jobs.append(job)
                
                if duplicates_found > 0:
                    print(f"   ⚠️  Skipped {duplicates_found} duplicates")
                
                # Solo guardar jobs únicos
                if unique_jobs:
                    saved = self.save_to_sheets(unique_jobs, tab_name=tab_name)
                    print(f"   💾 Saved {saved} NEW jobs to Sheets")
                    total_jobs_found += saved
                else:
                    print(f"   ℹ️  No new jobs (all were duplicates)")
                
                bulletins_processed += 1
                
                # ✅ NUEVO: Marcar email para eliminación
                self.mark_email_for_deletion(msg_id)
                
                # Mark as processed
                self.save_processed_id(msg_id)
            else:
                print(f"   ⚠️  No jobs extracted (may need better parsing)\n")
        
        print("="*70)
        print(f"📊 SUMMARY:")
        print(f"   Bulletins processed: {bulletins_processed}")
        print(f"   Total jobs found: {total_jobs_found}")
        print("="*70 + "\n")
        
        # ✅ NUEVO: Eliminar emails procesados
        self.delete_marked_emails()

def main():
    processor = JobBulletinProcessor()
    processor.process_bulletins(max_emails=50)

if __name__ == '__main__':
    main()
