#!/usr/bin/env python3
"""
DEBUG BULLETIN PROCESSOR
Ver por qué no procesa los emails
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email import policy
from email.parser import BytesParser
from datetime import datetime
from email.utils import parsedate_to_datetime

def get_gmail_service():
    creds = None
    if os.path.exists('data/credentials/token.json'):
        creds = Credentials.from_authorized_user_file('data/credentials/token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return build('gmail', 'v1', credentials=creds)

def get_email_age_days(message):
    """Calculate email age in days"""
    try:
        msg_bytes = base64.urlsafe_b64decode(message['raw'])
        msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
        
        date_str = msg.get('Date', '')
        if date_str:
            email_date = parsedate_to_datetime(date_str)
            now = datetime.now(email_date.tzinfo)
            age = (now - email_date).days
            return age
    except:
        return 999
    
    return 999

def detect_bulletin_type(sender, subject):
    sender_lower = sender.lower()
    subject_lower = subject.lower()
    
    if 'glassdoor' in sender_lower or 'noreply@glassdoor.com' in sender_lower:
        return 'glassdoor'
    elif 'linkedin' in sender_lower or 'jobalerts-noreply@linkedin.com' in sender_lower:
        return 'linkedin'
    elif 'indeed' in sender_lower or 'alert@indeed.com' in sender_lower:
        return 'indeed'
    
    return None

def get_processed_ids():
    if os.path.exists('processed_bulletins.txt'):
        with open('processed_bulletins.txt', 'r') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def main():
    service = get_gmail_service()
    
    # Mismo query que usa el processor
    query = (
        'from:(noreply@glassdoor.com OR jobs-noreply@linkedin.com OR noreply@indeed.com) '
        'subject:(empleos OR jobs OR "nuevos empleos" OR "new jobs" OR postúlate OR apply) '
        'newer_than:7d'
    )
    
    print("\n" + "="*70)
    print("🔍 DEBUG BULLETIN PROCESSOR")
    print("="*70 + "\n")
    
    print(f"Query: {query}\n")
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=10  # Solo primeros 10 para debug
    ).execute()
    
    messages = results.get('messages', [])
    processed_ids = get_processed_ids()
    
    print(f"📊 Encontrados: {len(messages)} emails")
    print(f"📋 Ya procesados: {len(processed_ids)} IDs en archivo\n")
    
    for i, msg_ref in enumerate(messages, 1):
        msg_id = msg_ref['id']
        
        # Get full message
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='raw'
        ).execute()
        
        # Parse
        msg_bytes = base64.urlsafe_b64decode(message['raw'])
        msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
        
        subject = msg.get('Subject', '')
        sender = msg.get('From', '')
        date_str = msg.get('Date', '')
        
        # Get age
        age = get_email_age_days(message)
        
        # Check if processed
        is_processed = msg_id in processed_ids
        
        # Detect type
        bulletin_type = detect_bulletin_type(sender, subject)
        
        print(f"{i}. Subject: {subject[:60]}")
        print(f"   From: {sender}")
        print(f"   Date: {date_str}")
        print(f"   Age: {age} days")
        print(f"   Type: {bulletin_type if bulletin_type else '❌ NO DETECTADO'}")
        print(f"   Processed: {'✅ YA PROCESADO' if is_processed else '❌ NO'}")
        print(f"   Age filter: {'✅ PASS (<7)' if age <= 7 else '❌ FAIL (>7)'}")
        print()
        
        if not is_processed and age <= 7 and bulletin_type:
            print(f"   ➡️  ESTE EMAIL DEBERÍA SER PROCESADO")
            print()

if __name__ == '__main__':
    main()
