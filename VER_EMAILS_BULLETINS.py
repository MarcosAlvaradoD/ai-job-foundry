#!/usr/bin/env python3
"""
VER EMAILS DISPONIBLES EN BULLETINS
Lista todos los emails para identificar cuáles son boletines reales de jobs
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email import policy
from email.parser import BytesParser

def get_gmail_service():
    """Initialize Gmail API service"""
    creds = None
    if os.path.exists('data/credentials/token.json'):
        creds = Credentials.from_authorized_user_file('data/credentials/token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return build('gmail', 'v1', credentials=creds)

def main():
    service = get_gmail_service()
    
    # Query for bulletin emails
    query = 'label:"JOBS/Bulletins" newer_than:7d'
    
    print("\n" + "="*70)
    print("📧 EMAILS EN JOBS/Bulletins (últimos 7 días)")
    print("="*70 + "\n")
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=20
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No hay emails en JOBS/Bulletins")
        return
    
    print(f"📊 Total: {len(messages)} emails\n")
    
    for i, msg_ref in enumerate(messages, 1):
        msg_id = msg_ref['id']
        
        # Get message
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
        date = msg.get('Date', '')
        
        # Detect type
        sender_lower = sender.lower()
        if 'glassdoor' in sender_lower:
            type_icon = "🔵 GLASSDOOR"
        elif 'linkedin' in sender_lower:
            type_icon = "🔷 LINKEDIN"
        elif 'indeed' in sender_lower:
            type_icon = "🟦 INDEED"
        else:
            type_icon = "❓ OTHER"
        
        print(f"{i}. {type_icon}")
        print(f"   From: {sender}")
        print(f"   Subject: {subject[:80]}")
        print(f"   Date: {date}")
        print(f"   ID: {msg_id}")
        print()

if __name__ == '__main__':
    main()
