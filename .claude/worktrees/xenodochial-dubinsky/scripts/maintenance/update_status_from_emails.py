#!/usr/bin/env python3
"""
AI JOB FOUNDRY - Email Status Updater
Revisa emails y actualiza status en Google Sheets automáticamente
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load environment
load_dotenv()

# Gmail API setup
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Status keywords mapping
STATUS_KEYWORDS = {
    'INTERVIEW_SCHEDULED': [
        'interview scheduled',
        'technical interview',
        'invitation to interview',
        'interview invitation',
        'schedule your interview',
        'confirmed interview',
        'interview confirmation'
    ],
    'REJECTED': [
        'no longer accepting applications',
        'position has been filled',
        'we have decided to move forward with other candidates',
        'not moving forward',
        'application was not selected',
        'regret to inform',
        'unfortunately',
        'not a match at this time'
    ],
    'ASSESSMENT': [
        'technical assessment',
        'complete the assessment',
        'coding challenge',
        'take-home assignment',
        'assessment link'
    ],
    'OFFER': [
        'offer letter',
        'job offer',
        'we would like to offer',
        'extend an offer',
        'congratulations'
    ],
    'PHONE_SCREEN': [
        'phone screen',
        'phone call',
        'initial call',
        'recruiter call'
    ]
}


class EmailStatusUpdater:
    def __init__(self):
        """Initialize Gmail and Sheets clients"""
        self.gmail_service = self._get_gmail_service()
        self.sheets_client = self._get_sheets_client()
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        if not self.sheet_id:
            raise ValueError("GOOGLE_SHEETS_ID not found in .env")
    
    def _get_gmail_service(self):
        """Get Gmail API service"""
        creds = Credentials.from_authorized_user_file(
            'data/credentials/token.json',
            SCOPES
        )
        return build('gmail', 'v1', credentials=creds)
    
    def _get_sheets_client(self):
        """Get Google Sheets client"""
        creds = Credentials.from_authorized_user_file(
            'data/credentials/token.json',
            SCOPES
        )
        return gspread.authorize(creds)
    
    def get_jobs_from_sheet(self, tab_name='Jobs'):
        """Get all jobs from Google Sheets"""
        print(f"\n📊 Reading jobs from '{tab_name}' tab...")
        
        try:
            spreadsheet = self.sheets_client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.worksheet(tab_name)
            
            # Get all data
            data = worksheet.get_all_records()
            
            print(f"✅ Found {len(data)} jobs")
            return data, worksheet
            
        except Exception as e:
            print(f"❌ Error reading sheet: {e}")
            return [], None
    
    def search_emails_for_company(self, company_name, days_back=30):
        """Search emails from specific company"""
        try:
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            
            # Search query
            query = f'from:({company_name}) after:{since_date}'
            
            # Execute search
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Get full message details
            email_data = []
            for msg in messages[:10]:  # Limit to 10 most recent
                message = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                email_data.append(message)
            
            return email_data
            
        except Exception as e:
            print(f"⚠️  Error searching emails for {company_name}: {e}")
            return []
    
    def extract_email_text(self, message):
        """Extract text from email message"""
        try:
            # Get payload
            payload = message.get('payload', {})
            
            # Get headers
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            
            # Get body
            body = ''
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        import base64
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            break
            else:
                import base64
                body_data = payload.get('body', {}).get('data', '')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            return subject, body
            
        except Exception as e:
            print(f"⚠️  Error extracting email text: {e}")
            return '', ''
    
    def detect_status_from_email(self, subject, body):
        """Detect job status from email content"""
        combined_text = (subject + ' ' + body).lower()
        
        # Check each status
        for status, keywords in STATUS_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    return status
        
        return None
    
    def update_job_status(self, worksheet, row_index, new_status, notes=''):
        """Update job status in Google Sheets"""
        try:
            # Columns: M = Status (13), N = NextAction (14)
            status_col = 13  # Column M
            notes_col = 14   # Column N
            
            # Update status
            worksheet.update_cell(row_index, status_col, new_status)
            
            # Update notes if provided
            if notes:
                current_notes = worksheet.cell(row_index, notes_col).value or ''
                timestamp = datetime.now().strftime('%Y-%m-%d')
                new_notes = f"[{timestamp}] {notes}"
                if current_notes:
                    new_notes = current_notes + ' | ' + new_notes
                worksheet.update_cell(row_index, notes_col, new_notes)
            
            print(f"  ✅ Updated row {row_index}: {new_status}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error updating row {row_index}: {e}")
            return False
    
    def mark_expired_jobs(self, worksheet, jobs):
        """Mark jobs with 'No longer accepting' as EXPIRED"""
        print(f"\n🚫 Checking for expired jobs...")
        
        expired_count = 0
        
        for idx, job in enumerate(jobs, start=2):  # Start at row 2 (after header)
            current_status = job.get('Status', '').strip()
            
            # Check if already marked or if status indicates rejection
            if current_status and 'no longer accepting' in current_status.lower():
                # Mark as EXPIRED
                self.update_job_status(
                    worksheet,
                    idx,
                    'EXPIRED',
                    'Position no longer accepting applications'
                )
                expired_count += 1
        
        print(f"✅ Marked {expired_count} jobs as EXPIRED")
        return expired_count
    
    def process_all_jobs(self, tab_name='Jobs'):
        """Process all jobs and update statuses"""
        print("\n" + "="*70)
        print("🔄 EMAIL STATUS UPDATER - Starting")
        print("="*70)
        
        # Get jobs
        jobs, worksheet = self.get_jobs_from_sheet(tab_name)
        
        if not jobs:
            print("❌ No jobs found")
            return
        
        # First, mark expired jobs
        self.mark_expired_jobs(worksheet, jobs)
        
        # Process each job
        updated_count = 0
        skipped_count = 0
        
        print(f"\n📧 Checking emails for status updates...")
        
        for idx, job in enumerate(jobs, start=2):  # Start at row 2
            company = job.get('Company', '').strip()
            current_status = job.get('Status', '').strip()
            
            # Skip if no company or already in final status
            if not company:
                continue
            
            if current_status in ['EXPIRED', 'REJECTED', 'OFFER_ACCEPTED', 'WITHDRAWN']:
                skipped_count += 1
                continue
            
            # Search emails
            print(f"\n  Checking: {company}...")
            emails = self.search_emails_for_company(company)
            
            if not emails:
                print(f"    No recent emails")
                continue
            
            print(f"    Found {len(emails)} emails")
            
            # Check each email
            for email in emails:
                subject, body = self.extract_email_text(email)
                detected_status = self.detect_status_from_email(subject, body)
                
                if detected_status:
                    print(f"    📨 Detected: {detected_status}")
                    print(f"       Subject: {subject[:60]}...")
                    
                    # Update if different from current
                    if detected_status != current_status:
                        self.update_job_status(
                            worksheet,
                            idx,
                            detected_status,
                            f'Updated from email: {subject[:50]}'
                        )
                        updated_count += 1
                        break  # Stop after first match
        
        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total jobs:       {len(jobs)}")
        print(f"Updated:          {updated_count}")
        print(f"Skipped (final):  {skipped_count}")
        print("="*70 + "\n")


def main():
    """Main execution"""
    try:
        updater = EmailStatusUpdater()
        updater.process_all_jobs()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
