"""
Gmail Inbox Diagnostics - Find why emails aren't being processed
"""

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

def diagnose_gmail():
    """Diagnose Gmail label and email issues"""
    
    # Load environment
    base_dir = Path(__file__).parent.parent.parent
    load_dotenv(base_dir / '.env')
    
    # Load credentials
    token_path = base_dir / 'data' / 'credentials' / 'token.json'
    if not token_path.exists():
        print("❌ Token not found. Run: py scripts/oauth/regenerate_oauth_token.py")
        return
    
    creds = Credentials.from_authorized_user_file(str(token_path))
    service = build('gmail', 'v1', credentials=creds)
    
    print("\n" + "="*70)
    print("📧 GMAIL DIAGNOSTICS")
    print("="*70)
    
    # 1. List ALL labels
    print("\n1️⃣  ALL GMAIL LABELS:")
    print("-" * 70)
    try:
        labels_result = service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        job_related = []
        for label in labels:
            print(f"   • {label['name']} (ID: {label['id']})")
            if 'job' in label['name'].lower() or 'inbound' in label['name'].lower():
                job_related.append(label)
        
        if job_related:
            print(f"\n   🎯 Found {len(job_related)} JOB-RELATED labels:")
            for lbl in job_related:
                print(f"      → {lbl['name']} (ID: {lbl['id']})")
    
    except Exception as e:
        print(f"   ❌ Error listing labels: {e}")
    
    # 2. Try different label queries
    print("\n2️⃣  TESTING DIFFERENT LABEL QUERIES:")
    print("-" * 70)
    
    queries = [
        "label:JOBS/Inbound",
        "label:Inbound",
        "label:JOBS",
        "in:inbox",
        "from:jobalerts-noreply@linkedin.com",
        "from:glassdoor-noreply@glassdoor.com",
        "subject:job OR subject:empleo"
    ]
    
    for query in queries:
        try:
            result = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            count = result.get('resultSizeEstimate', 0)
            messages = result.get('messages', [])
            
            print(f"\n   Query: {query}")
            print(f"   Results: {count} emails")
            
            if messages:
                # Get first message details
                msg = service.users().messages().get(
                    userId='me',
                    id=messages[0]['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                print(f"   Sample: {headers.get('Subject', 'No subject')[:60]}...")
                print(f"          From: {headers.get('From', 'Unknown')}")
        
        except Exception as e:
            print(f"\n   Query: {query}")
            print(f"   ❌ Error: {e}")
    
    # 3. Check JOBS labels
    print("\n3️⃣  CHECKING JOBS LABELS:")
    print("-" * 70)
    
    try:
        jobs_labels = [l for l in labels if 'JOBS' in l['name'] or 'jobs' in l['name']]
        
        if jobs_labels:
            for label in jobs_labels:
                print(f"\n   Label: {label['name']}")
                print(f"   ID: {label['id']}")
                
                # Get message count
                result = service.users().messages().list(
                    userId='me',
                    labelIds=[label['id']],
                    maxResults=5
                ).execute()
                
                total = result.get('resultSizeEstimate', 0)
                messages = result.get('messages', [])
                
                print(f"   Messages: {total}")
                
                if messages:
                    print(f"   First message:")
                    msg = service.users().messages().get(
                        userId='me',
                        id=messages[0]['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                    print(f"      {headers.get('Subject', 'No subject')[:50]}...")
        else:
            print("   ❌ No JOBS labels found")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("📊 DIAGNOSIS COMPLETE")
    print("="*70)
    print("\n💡 NEXT STEPS:")
    print("   1. Note the correct label name and ID from above")
    print("   2. Update core/automation/gmail_jobs_monitor.py")
    print("   3. Run: py control_center.py → Option 4 (Process Bulletins)")
    print("="*70)

if __name__ == "__main__":
    diagnose_gmail()
