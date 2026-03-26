"""
EMERGENCY URL RECOVERY - Recupera URLs de Glassdoor desde emails en papelera

Este script:
1. Lee emails de Glassdoor desde Gmail (incluye papelera)
2. Extrae las URLs correctamente usando TODOS los patrones posibles
3. Actualiza Google Sheets con las URLs reales

Usage:
    py scripts/maintenance/recover_bulletin_urls.py
"""

import os
import sys
import re
import base64
from pathlib import Path
from email import policy
from email.parser import BytesParser
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

class URLRecovery:
    def __init__(self):
        self.gmail_service = self._get_gmail_service()
        self.sheet_manager = SheetManager()
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
    def _get_gmail_service(self):
        """Initialize Gmail API service"""
        creds_path = project_root / "data" / "credentials" / "credentials.json"
        token_path = project_root / "data" / "credentials" / "token.json"
        
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def extract_all_glassdoor_urls(self, html_content: str) -> list:
        """
        Extract Glassdoor URLs using MULTIPLE patterns
        Returns list of URLs found
        """
        urls = []
        
        # Pattern 1: Direct job listing URL
        pattern1 = r'https://www\.glassdoor\.com/job-listing/JL_\d+\.htm[^"\s<>]*'
        urls.extend(re.findall(pattern1, html_content))
        
        # Pattern 2: From tracking URL with job_listing_id
        pattern2 = r'jobAlertAlert&amp;utm_content=ja-jobpos\d+-(\d+)'
        job_ids = re.findall(pattern2, html_content)
        for job_id in job_ids:
            urls.append(f"https://www.glassdoor.com/job-listing/JL_{job_id}.htm")
        
        # Pattern 3: Alternative tracking pattern
        pattern3 = r'job_listing_id=(\d+)'
        job_ids3 = re.findall(pattern3, html_content)
        for job_id in job_ids3:
            urls.append(f"https://www.glassdoor.com/job-listing/JL_{job_id}.htm")
        
        # Pattern 4: From partner-job-link parameter
        pattern4 = r'partner-job-link[^"]*https://www\.glassdoor\.com/[^"<>\s]+'
        urls.extend(re.findall(pattern4, html_content))
        
        # Pattern 5: Any glassdoor.com URL
        pattern5 = r'https://www\.glassdoor\.com/[^\s"<>]+'
        urls.extend(re.findall(pattern5, html_content))
        
        # Remove duplicates and filter valid job URLs
        valid_urls = []
        seen = set()
        for url in urls:
            # Clean URL
            url = url.split('&amp;')[0].split('?')[0]
            if 'job-listing' in url and url not in seen:
                valid_urls.append(url)
                seen.add(url)
        
        return valid_urls
    
    def extract_job_titles(self, html_content: str) -> list:
        """Extract job titles from Glassdoor email"""
        title_pattern = r'<p style="font-size:14px;line-height:1\.4;margin:0;font-weight:600">([^<]+)</p>'
        return re.findall(title_pattern, html_content)
    
    def get_glassdoor_emails(self, max_emails=50):
        """Fetch Glassdoor bulletin emails (including trash)"""
        print("\n" + "="*70)
        print("FETCHING GLASSDOOR EMAILS FROM GMAIL")
        print("="*70)
        
        # Query for Glassdoor emails from last 30 days
        query = 'from:noreply@glassdoor.com newer_than:30d'
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            print(f"✅ Found {len(messages)} Glassdoor emails\n")
            
            return messages
            
        except HttpError as error:
            print(f'❌ Error fetching emails: {error}')
            return []
    
    def process_email(self, message_id: str):
        """Process single email and extract URLs"""
        try:
            # Get full message
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='raw'
            ).execute()
            
            # Parse email
            msg_bytes = base64.urlsafe_b64decode(message['raw'])
            msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
            
            subject = msg.get('Subject', '')
            
            # Get HTML content
            html_content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        html_content = part.get_content()
                        break
            else:
                if msg.get_content_type() == 'text/html':
                    html_content = msg.get_content()
            
            if not html_content:
                return []
            
            # Extract URLs and titles
            urls = self.extract_all_glassdoor_urls(html_content)
            titles = self.extract_job_titles(html_content)
            
            # Match URLs to titles
            jobs = []
            for i, url in enumerate(urls):
                jobs.append({
                    'url': url,
                    'title': titles[i] if i < len(titles) else 'Unknown',
                    'subject': subject
                })
            
            return jobs
            
        except Exception as e:
            print(f"   ⚠️  Error processing email {message_id}: {e}")
            return []
    
    def update_sheet_urls(self, jobs_data: list):
        """Update Google Sheets with recovered URLs"""
        print("\n" + "="*70)
        print("UPDATING GOOGLE SHEETS")
        print("="*70)
        
        try:
            # Get current Glassdoor tab data
            result = self.sheet_manager.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='Glassdoor!A1:Z1000'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("❌ No data in Glassdoor tab")
                return
            
            headers = values[0]
            rows = values[1:]
            
            # Find columns
            role_idx = headers.index('Role') if 'Role' in headers else -1
            url_idx = headers.index('ApplyURL') if 'ApplyURL' in headers else -1
            company_idx = headers.index('Company') if 'Company' in headers else -1
            
            if role_idx == -1 or url_idx == -1:
                print("❌ Missing Role or ApplyURL column")
                return
            
            # Match jobs and update URLs
            updates = []
            for row_num, row in enumerate(rows, start=2):
                if len(row) <= url_idx:
                    row.extend([''] * (url_idx - len(row) + 1))
                
                current_url = row[url_idx] if url_idx < len(row) else ''
                role = row[role_idx] if role_idx < len(row) else ''
                company = row[company_idx] if company_idx < len(row) else ''
                
                # If URL is missing or "Unknown"
                if not current_url or current_url == 'Unknown':
                    # Try to match with recovered jobs
                    for job in jobs_data:
                        if role and role.lower() in job['title'].lower():
                            updates.append({
                                'row': row_num,
                                'url': job['url'],
                                'role': role,
                                'company': company
                            })
                            break
            
            # Apply updates
            if updates:
                print(f"\n📝 Updating {len(updates)} rows with recovered URLs...\n")
                
                for update in updates:
                    # Update cell
                    col_letter = chr(65 + url_idx)  # A=65
                    range_name = f"Glassdoor!{col_letter}{update['row']}"
                    
                    self.sheet_manager.service.spreadsheets().values().update(
                        spreadsheetId=self.sheet_id,
                        range=range_name,
                        valueInputOption='RAW',
                        body={'values': [[update['url']]]}
                    ).execute()
                    
                    print(f"   ✅ Row {update['row']}: {update['role'][:50]}...")
                    print(f"      URL: {update['url']}")
                
                print(f"\n✅ Updated {len(updates)} jobs with URLs")
            else:
                print("ℹ️  No jobs found that need URL updates")
                
        except Exception as e:
            print(f"❌ Error updating sheet: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Main recovery process"""
        print("\n" + "="*70)
        print("🚀 GLASSDOOR URL RECOVERY TOOL")
        print("="*70)
        print("This will:")
        print("  1. Read Glassdoor emails from Gmail (last 30 days)")
        print("  2. Extract all job URLs using multiple patterns")
        print("  3. Update Google Sheets with recovered URLs")
        print("="*70)
        
        input("\nPress Enter to continue...")
        
        # Get emails
        messages = self.get_glassdoor_emails(max_emails=50)
        
        if not messages:
            print("❌ No Glassdoor emails found")
            return
        
        # Process each email
        all_jobs = []
        print("📧 Processing emails...\n")
        
        for i, message in enumerate(messages, 1):
            print(f"[{i}/{len(messages)}] Processing email {message['id'][:10]}...")
            jobs = self.process_email(message['id'])
            
            if jobs:
                print(f"   ✅ Found {len(jobs)} jobs with URLs")
                all_jobs.extend(jobs)
            else:
                print(f"   ℹ️  No jobs found")
        
        print(f"\n📊 TOTAL: Extracted {len(all_jobs)} jobs with URLs from {len(messages)} emails")
        
        # Update sheet
        if all_jobs:
            self.update_sheet_urls(all_jobs)
        
        print("\n" + "="*70)
        print("✅ RECOVERY COMPLETE")
        print("="*70)

if __name__ == "__main__":
    recovery = URLRecovery()
    recovery.run()
