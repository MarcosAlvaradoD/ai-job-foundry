"""
DEBUG SCRIPT - Extract and show ALL URLs from one Glassdoor email
"""

import os
import sys
import re
import base64
from pathlib import Path
from email import policy
from email.parser import BytesParser

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def get_gmail_service():
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

def test_all_patterns(html_content: str):
    """Test ALL URL extraction patterns"""
    
    print("\n" + "="*70)
    print("TESTING ALL URL EXTRACTION PATTERNS")
    print("="*70)
    
    all_urls = []
    
    # Pattern 1: Direct job listing URL
    print("\n[Pattern 1] Direct job-listing URLs:")
    pattern1 = r'https://www\.glassdoor\.com/job-listing/JL_(\d+)\.htm'
    urls1 = re.findall(pattern1, html_content)
    print(f"  Found: {len(urls1)} URLs")
    for url_id in urls1[:5]:
        url = f"https://www.glassdoor.com/job-listing/JL_{url_id}.htm"
        print(f"    - {url}")
        all_urls.append(url)
    
    # Pattern 2: From tracking URL with job_listing_id
    print("\n[Pattern 2] Tracking pixel URLs (utm_content=ja-jobpos):")
    pattern2 = r'jobAlertAlert&amp;utm_content=ja-jobpos\d+-(\d+)'
    urls2 = re.findall(pattern2, html_content)
    print(f"  Found: {len(urls2)} IDs")
    for url_id in urls2[:5]:
        url = f"https://www.glassdoor.com/job-listing/JL_{url_id}.htm"
        print(f"    - {url}")
        all_urls.append(url)
    
    # Pattern 3: Alternative tracking pattern
    print("\n[Pattern 3] job_listing_id parameter:")
    pattern3 = r'job_listing_id=(\d+)'
    urls3 = re.findall(pattern3, html_content)
    print(f"  Found: {len(urls3)} IDs")
    for url_id in urls3[:5]:
        url = f"https://www.glassdoor.com/job-listing/JL_{url_id}.htm"
        print(f"    - {url}")
        all_urls.append(url)
    
    # Pattern 4: From partner-job-link parameter
    print("\n[Pattern 4] Encoded jobListingId:")
    pattern4 = r'jobListingId%3D(\d+)'
    urls4 = re.findall(pattern4, html_content)
    print(f"  Found: {len(urls4)} IDs")
    for url_id in urls4[:5]:
        url = f"https://www.glassdoor.com/job-listing/JL_{url_id}.htm"
        print(f"    - {url}")
        all_urls.append(url)
    
    # Pattern 5: Any glassdoor.com job URL
    print("\n[Pattern 5] Generic glassdoor URLs with 10+ digit IDs:")
    pattern5 = r'glassdoor\.com/[^"]*?(\d{10,})'
    urls5 = re.findall(pattern5, html_content)
    print(f"  Found: {len(urls5)} IDs")
    for url_id in urls5[:5]:
        print(f"    - ID: {url_id}")
        all_urls.append(f"https://www.glassdoor.com/job-listing/JL_{url_id}.htm")
    
    # Pattern 6: SUPER AGGRESSIVE - ALL glassdoor.com URLs
    print("\n[Pattern 6] ALL glassdoor.com URLs (any format):")
    pattern6 = r'https://[^"<>\s]*glassdoor\.com[^"<>\s]*'
    urls6 = re.findall(pattern6, html_content)
    print(f"  Found: {len(urls6)} URLs")
    for url in urls6[:10]:
        print(f"    - {url[:100]}...")
    
    # Extract titles for comparison
    print("\n[TITLES] Job titles found:")
    title_pattern = r'<p style="font-size:14px;line-height:1\.4;margin:0;font-weight:600">([^<]+)</p>'
    titles = re.findall(title_pattern, html_content)
    print(f"  Found: {len(titles)} titles")
    for i, title in enumerate(titles[:10], 1):
        print(f"    {i}. {title}")
    
    print("\n" + "="*70)
    print(f"SUMMARY:")
    print(f"  Titles: {len(titles)}")
    print(f"  Pattern 1: {len(urls1)} URLs")
    print(f"  Pattern 2: {len(urls2)} IDs")
    print(f"  Pattern 3: {len(urls3)} IDs")
    print(f"  Pattern 4: {len(urls4)} IDs")
    print(f"  Pattern 5: {len(urls5)} IDs")
    print(f"  Pattern 6: {len(urls6)} ALL URLs")
    print("="*70)
    
    # Save HTML for manual inspection
    output_file = project_root / "debug_glassdoor_email.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n✅ HTML saved to: {output_file}")
    print("   Open this file to manually inspect the email structure")

def main():
    print("\n" + "="*70)
    print("GLASSDOOR EMAIL DEBUG TOOL")
    print("="*70)
    
    service = get_gmail_service()
    
    # Get ONE recent Glassdoor email
    query = 'from:noreply@glassdoor.com newer_than:7d'
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=1
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No Glassdoor emails found in last 7 days")
        return
    
    msg_id = messages[0]['id']
    print(f"\n📧 Fetching email {msg_id}...")
    
    # Get full message
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='raw'
    ).execute()
    
    # Parse email
    msg_bytes = base64.urlsafe_b64decode(message['raw'])
    msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
    
    subject = msg.get('Subject', '')
    print(f"Subject: {subject}")
    
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
        print("❌ No HTML content found")
        return
    
    print(f"✅ HTML content: {len(html_content)} characters")
    
    # Test all patterns
    test_all_patterns(html_content)

if __name__ == "__main__":
    main()
