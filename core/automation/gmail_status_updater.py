"""
Gmail Status Updater
Monitors Gmail for job application status updates and syncs with Google Sheets

Detects:
- Interview invitations
- Rejection emails  
- Application acknowledgments
- Offer letters

Author: Marcos Alberto Alvarado
Date: 2026-02-02
"""

import os
import re
import sys
import base64
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.sheets.sheet_manager import SheetManager

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailStatusUpdater:
    """Updates job status based on Gmail messages"""
    
    def __init__(self):
        self.sheets = SheetManager()
        
        # Use same credentials as SheetManager
        cred_dir = Path(__file__).parent.parent.parent / "data" / "credentials"
        token_path = cred_dir / "token.json"
        
        if not token_path.exists():
            raise FileNotFoundError(f"OAuth token not found: {token_path}")
        
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        
        # Status detection patterns
        self.patterns = {
            'interview': [
                r'interview.*(?:invitation|scheduled|invite)',
                r'would like to schedule',
                r'next step.*interview',
                r'invitation to interview',
                r'interview invitation'
            ],
            'rejected': [
                r'unfortunately|we regret|not selected|not moving forward',
                r'decided to pursue other candidates',
                r'position has been filled',
                r'not be moving forward',
                r'thank you for your interest'
            ],
            'offer': [
                r'offer.*(?:letter|employment)',
                r'we are pleased to offer',
                r'job offer',
                r'offer of employment'
            ],
            'acknowledged': [
                r'application received',
                r'thank you for applying',
                r'received your application'
            ]
        }
    
    def process_status_emails(self, days_back: int = 7):
        """
        Process recent emails for status updates
        
        Args:
            days_back: How many days back to check (default: 7)
        """
        print(f"📧 Checking emails from last {days_back} days...\n")
        
        # Get recent emails from job-related labels/folders
        query = f'newer_than:{days_back}d (from:noreply OR from:recruiting OR subject:interview OR subject:application)'
        messages = self.search_messages(query, max_results=100)
        
        print(f"✅ Found {len(messages)} potential status emails\n")
        
        updates_made = 0
        
        for msg in messages:
            email_id = msg['id']
            email_data = self.get_message(email_id)
            
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('from', '')
            
            # Detect status
            new_status = self.detect_status(subject, body)
            
            if not new_status:
                continue
            
            # Find matching job in sheets
            company = self.extract_company_from_email(sender, subject)
            
            if company:
                print(f"📝 {company}: {new_status}")
                
                # Update sheets
                if self.update_job_status_by_company(company, new_status):
                    updates_made += 1
        
        print(f"\n✅ Updated {updates_made} jobs\n")
    
    def search_messages(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search Gmail messages"""
        try:
            response = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = response.get('messages', [])
            return messages
            
        except Exception as e:
            print(f"Error searching Gmail: {e}")
            return []
    
    def get_message(self, msg_id: str) -> Dict:
        """Get message details"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            
            # Extract body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': sender,
                'body': body
            }
            
        except Exception as e:
            print(f"Error getting message {msg_id}: {e}")
            return {}
    
    def detect_status(self, subject: str, body: str) -> str:
        """
        Detect job status from email content
        
        Returns:
            Status string or empty if no match
        """
        text = (subject + " " + body).lower()
        
        # Priority order: offer > interview > rejected > acknowledged
        if any(re.search(pattern, text, re.I) for pattern in self.patterns['offer']):
            return 'Offer Received'
        
        if any(re.search(pattern, text, re.I) for pattern in self.patterns['interview']):
            return 'Interview Scheduled'
        
        if any(re.search(pattern, text, re.I) for pattern in self.patterns['rejected']):
            return 'Rejected'
        
        if any(re.search(pattern, text, re.I) for pattern in self.patterns['acknowledged']):
            return 'Application Received'
        
        return ''
    
    def extract_company_from_email(self, sender: str, subject: str) -> str:
        """
        Extract company name from email sender or subject
        
        Args:
            sender: Email from field
            subject: Email subject
            
        Returns:
            Company name or empty string
        """
        # Try to extract from sender domain
        if '@' in sender:
            domain = sender.split('@')[-1].lower()
            # Remove common email service domains
            if domain not in ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']:
                company = domain.split('.')[0]
                return company.title()
        
        # Try to extract from subject
        subject_lower = subject.lower()
        if 'from' in subject_lower:
            match = re.search(r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', subject)
            if match:
                return match.group(1)
        
        return ''
    
    def update_job_status_by_company(self, company: str, new_status: str) -> bool:
        """
        Update job status in Google Sheets by company name (searches all tabs).
        """
        ALL_TABS = ["linkedin", "glassdoor", "indeed", "computrabajo"]
        try:
            for tab in ALL_TABS:
                try:
                    jobs = self.sheets.get_all_jobs(tab=tab)
                except Exception:
                    continue

                for job in jobs:
                    job_company = job.get('Company', '').lower().strip()
                    if not job_company:
                        continue
                    if company.lower() in job_company or job_company in company.lower():
                        row_num = job.get('_row')
                        if row_num:
                            self.sheets.update_job(
                                row_id=row_num,
                                updates={'Status': new_status},
                                tab=tab
                            )
                            return True

            return False

        except Exception as e:
            print(f"⚠️  Error updating {company}: {e}")
            return False

if __name__ == '__main__':
    import argparse
    import sys as _sys

    if _sys.stdout.encoding and _sys.stdout.encoding.lower() != 'utf-8':
        _sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description='Gmail Job Status Updater')
    parser.add_argument('--days', type=int, default=14,
                        help='Cuántos días atrás revisar (default: 14)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Solo mostrar detecciones sin actualizar Sheets')
    args = parser.parse_args()

    print("=" * 60)
    print("  AI JOB FOUNDRY — Gmail Status Updater")
    print("=" * 60)

    try:
        updater = GmailStatusUpdater()
        if args.dry_run:
            print(f"\n🧪 MODO DRY-RUN — Revisando {args.days} días atrás...\n")
            # Mostrar sin actualizar
            query = f'newer_than:{args.days}d (from:noreply OR from:recruiting OR subject:interview OR subject:application OR subject:applicacion OR subject:entrevista)'
            messages = updater.search_messages(query, max_results=100)
            print(f"📧 {len(messages)} emails encontrados\n")
            for msg in messages:
                data = updater.get_message(msg['id'])
                status = updater.detect_status(data.get('subject', ''), data.get('body', ''))
                if status:
                    company = updater.extract_company_from_email(data.get('from', ''), data.get('subject', ''))
                    print(f"  [{status}] {company or '?'} — {data.get('subject', '')[:60]}")
        else:
            updater.process_status_emails(days_back=args.days)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Verifica que data/credentials/token.json exista y sea válido.")
