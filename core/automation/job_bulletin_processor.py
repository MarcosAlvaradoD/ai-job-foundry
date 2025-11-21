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
        """Extract job listings from Glassdoor bulletin email"""
        jobs = []
        
        # Glassdoor URLs
        url_pattern = r'https://www\.glassdoor\.com[^\s"<>]+'
        urls = re.findall(url_pattern, html_content)
        
        # Job titles
        title_pattern = r'<a[^>]*>([^<]+(?:Manager|Director|Lead|Analyst|Engineer)[^<]*)</a>'
        titles = re.findall(title_pattern, html_content, re.IGNORECASE)
        
        for i, url in enumerate(urls):
            if 'job-listing' in url or 'partner/jobListing' in url:
                job = {
                    'Source': 'Glassdoor',
                    'ApplyURL': url,
                    'Role': titles[i] if i < len(titles) else 'Unknown Role',
                    'Company': 'Unknown',
                    'Location': 'Unknown',
                    'CreatedAt': datetime.now().isoformat(),
                    'Status': 'New'
                }
                jobs.append(job)
        
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
        
        return len(rows)
    
    def process_bulletins(self, max_emails: int = 50):
        """Main processing function"""
        print("\n" + "="*70)
        print("📧 JOB BULLETIN PROCESSOR")
        print("="*70)
        print("Processing job alert emails from LinkedIn, Indeed, and Glassdoor...")
        print("="*70 + "\n")
        
        # Get bulletins from JOBS/Inbound
        query = 'label:JOBS/Inbound newer_than:60d'
        results = self.gmail_service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_emails
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found in JOBS/Inbound")
            return
        
        print(f"Found {len(messages)} emails to check\n")
        
        # Load processed IDs
        processed_ids = self.get_processed_ids()
        
        total_jobs_found = 0
        bulletins_processed = 0
        
        for msg_ref in messages:
            msg_id = msg_ref['id']
            
            # Skip if already processed
            if msg_id in processed_ids:
                continue
            
            # Get full message
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=msg_id,
                format='raw'
            ).execute()
            
            # Parse email
            subject, sender, html_content, text_content = self.parse_email(message)
            
            # Detect bulletin type
            bulletin_type = self.detect_bulletin_type(sender, subject)
            
            if not bulletin_type:
                # Not a bulletin, skip
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
                
                # Save to Sheets
                saved = self.save_to_sheets(jobs, tab_name=bulletin_type.capitalize())
                print(f"   💾 Saved {saved} jobs to Sheets\n")
                
                total_jobs_found += len(jobs)
                bulletins_processed += 1
                
                # Mark as processed
                self.save_processed_id(msg_id)
            else:
                print(f"   ⚠️  No jobs extracted (may need better parsing)\n")
        
        print("="*70)
        print(f"📊 SUMMARY:")
        print(f"   Bulletins processed: {bulletins_processed}")
        print(f"   Total jobs found: {total_jobs_found}")
        print("="*70 + "\n")

def main():
    processor = JobBulletinProcessor()
    processor.process_bulletins(max_emails=50)

if __name__ == '__main__':
    main()
