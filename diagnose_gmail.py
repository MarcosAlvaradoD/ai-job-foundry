#!/usr/bin/env python3
"""
Quick diagnostic: Check Gmail folder and recent emails
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/spreadsheets'
]

def main():
    print("\n" + "="*70)
    print("GMAIL DIAGNOSTIC")
    print("="*70 + "\n")
    
    # Get credentials
    creds_dir = project_root / "data" / "credentials"
    token_path = creds_dir / "token.json"
    
    if not token_path.exists():
        print("[ERROR] No token.json found. Run reauthenticate_gmail_v2.py first")
        return
    
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    
    # Check JOBS/Inbound folder
    print("Checking folder: JOBS/Inbound")
    print("-" * 70)
    
    try:
        # Get label ID
        labels_result = service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        target_label = None
        for label in labels:
            if label['name'] == 'JOBS/Inbound':
                target_label = label['id']
                break
        
        if not target_label:
            print("[ERROR] Label 'JOBS/Inbound' not found!")
            print("\nAvailable labels:")
            for label in labels:
                if 'JOBS' in label['name']:
                    print(f"   - {label['name']} (ID: {label['id']})")
            return
        
        print(f"[OK] Label found: {target_label}")
        
        # Get messages in this label
        print("\nRecent messages (last 20):")
        print("-" * 70)
        
        results = service.users().messages().list(
            userId='me',
            labelIds=[target_label],
            maxResults=20
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("[WARNING] NO MESSAGES in JOBS/Inbound")
            print("\nPossible causes:")
            print("   1. Folder is empty")
            print("   2. Messages were already moved/deleted")
            print("   3. Gmail rule not working")
        else:
            print(f"Found {len(messages)} messages:\n")
            
            for i, msg in enumerate(messages[:10], 1):  # Show first 10
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg_data.get('payload', {}).get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                print(f"{i}. From: {from_email}")
                print(f"   Subject: {subject[:80]}...")
                print(f"   Date: {date_str}")
                print(f"   ID: {msg['id']}")
                print()
        
        # Also check JOBS label
        print("\n" + "=" * 70)
        print("Checking parent folder: JOBS")
        print("-" * 70)
        
        jobs_label = None
        for label in labels:
            if label['name'] == 'JOBS' and '/' not in label['name']:
                jobs_label = label['id']
                break
        
        if jobs_label:
            results2 = service.users().messages().list(
                userId='me',
                labelIds=[jobs_label],
                maxResults=5
            ).execute()
            
            messages2 = results2.get('messages', [])
            print(f"[OK] Found {len(messages2)} messages in JOBS (showing 5)")
            
            for i, msg in enumerate(messages2, 1):
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'Date']
                ).execute()
                
                headers = msg_data.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                print(f"{i}. {subject[:60]}... ({date_str})")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("[OK] Diagnostic complete")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
