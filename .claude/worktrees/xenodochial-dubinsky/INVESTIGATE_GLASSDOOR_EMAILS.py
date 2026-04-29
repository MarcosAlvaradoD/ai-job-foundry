"""
Busca y analiza emails de Glassdoor
"""
import os
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import re

load_dotenv()

def main():
    print("\n" + "="*70)
    print("GLASSDOOR EMAIL INVESTIGATION")
    print("="*70 + "\n")
    
    # Setup Gmail API
    creds = Credentials.from_authorized_user_file(
        'data/credentials/token.json',
        ['https://www.googleapis.com/auth/gmail.readonly']
    )
    service = build('gmail', 'v1', credentials=creds)
    
    # Search for Glassdoor emails
    print("Searching for Glassdoor emails...")
    
    queries = [
        'from:glassdoor.com',
        'from:@glassdoor.com',
        'subject:glassdoor',
        'glassdoor job alert'
    ]
    
    all_messages = []
    for query in queries:
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            all_messages.extend(messages)
            print(f"  Found {len(messages)} with query: '{query}'")
        except Exception as e:
            print(f"  Error with query '{query}': {e}")
    
    # Remove duplicates
    unique_messages = {msg['id']: msg for msg in all_messages}
    all_messages = list(unique_messages.values())
    
    print(f"\nTotal unique Glassdoor emails: {len(all_messages)}\n")
    
    if not all_messages:
        print("No Glassdoor emails found!")
        return
    
    # Analyze first 5 emails
    print("="*70)
    print("ANALYZING FIRST 5 GLASSDOOR EMAILS")
    print("="*70)
    
    for i, msg in enumerate(all_messages[:5], 1):
        try:
            email = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            headers = email['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
            
            print(f"\n{i}. Email ID: {msg['id']}")
            print(f"   From: {from_email}")
            print(f"   Date: {date}")
            print(f"   Subject: {subject}")
            
            # Get body
            if 'parts' in email['payload']:
                for part in email['payload']['parts']:
                    if part['mimeType'] == 'text/html' or part['mimeType'] == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            
                            # Extract job info patterns
                            print(f"\n   Body excerpt (first 500 chars):")
                            print("   " + "-"*66)
                            # Clean HTML tags for readability
                            clean_body = re.sub(r'<[^>]+>', ' ', body[:500])
                            clean_body = re.sub(r'\s+', ' ', clean_body).strip()
                            print(f"   {clean_body}")
                            
                            # Look for URLs
                            urls = re.findall(r'https://[^\s<>"]+glassdoor[^\s<>"]+', body)
                            if urls:
                                print(f"\n   Found {len(urls)} Glassdoor URLs:")
                                for url in urls[:3]:
                                    print(f"   - {url[:80]}...")
                            break
            
            print("\n" + "-"*70)
            
        except Exception as e:
            print(f"\n   Error analyzing email: {e}")
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("1. Check if emails are bulletins (multiple jobs) or individual jobs")
    print("2. Identify correct parser to use (bulletin vs individual)")
    print("3. Fix gmail_jobs_monitor.py to extract Company/Role correctly")

if __name__ == "__main__":
    main()
