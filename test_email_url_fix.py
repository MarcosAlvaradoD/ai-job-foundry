#!/usr/bin/env python3
"""
Test Email URL Extraction Fix
Tests the new HTML parsing capability

Usage:
    py test_email_url_fix.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.ingestion.ingest_email_to_sheet_v2 import parse_email_raw, extract_job_url
import base64

def create_test_html_email():
    """Create a test HTML-only email (like recruiters send)"""
    html_content = """
From: recruiter@company.com
Subject: Great PM opportunity at TechCorp
Content-Type: text/html

<html>
<body>
    <h1>Product Manager Position</h1>
    <p>Hi, I found your profile interesting for this role:</p>
    <ul>
        <li>Company: TechCorp</li>
        <li>Location: Remote</li>
        <li>Salary: $120k-$140k</li>
    </ul>
    <a href="https://www.linkedin.com/jobs/view/1234567890">Apply Now</a>
    <p>Best regards,<br>Jane Recruiter</p>
    <a href="https://company.com/unsubscribe">Unsubscribe</a>
</body>
</html>
    """
    return base64.urlsafe_b64encode(html_content.encode()).decode()

def create_test_plain_email():
    """Create a test plain text email"""
    plain_content = """
From: recruiter@company.com
Subject: Backend Engineer at StartupX
Content-Type: text/plain

Hey,

Check out this backend engineer role:
Company: StartupX
Location: San Francisco
Apply: https://www.indeed.com/viewjob?jk=abc123xyz

Thanks!
    """
    return base64.urlsafe_b64encode(plain_content.encode()).decode()

def main():
    print("\n" + "="*70)
    print("TESTING EMAIL URL EXTRACTION FIX")
    print("="*70)
    
    # Test 1: HTML-only email (most recruiter emails)
    print("\n[TEST 1] HTML-only Email (Recruiter Style)")
    print("-" * 70)
    
    html_b64 = create_test_html_email()
    subject, sender, body = parse_email_raw(html_b64)
    
    print(f"Subject: {subject}")
    print(f"Sender: {sender}")
    print(f"Body length: {len(body)} chars")
    print(f"Body preview: {body[:200]}...")
    
    url = extract_job_url(body)
    print(f"\nExtracted URL: {url}")
    
    if "linkedin.com/jobs/view" in url:
        print("[OK] Successfully extracted LinkedIn URL from HTML email")
    else:
        print("[FAILED] Could not extract URL from HTML email")
    
    # Test 2: Plain text email
    print("\n[TEST 2] Plain Text Email")
    print("-" * 70)
    
    plain_b64 = create_test_plain_email()
    subject, sender, body = parse_email_raw(plain_b64)
    
    print(f"Subject: {subject}")
    print(f"Sender: {sender}")
    print(f"Body length: {len(body)} chars")
    
    url = extract_job_url(body)
    print(f"\nExtracted URL: {url}")
    
    if "indeed.com" in url:
        print("[OK] Successfully extracted Indeed URL from plain text email")
    else:
        print("[FAILED] Could not extract URL from plain text email")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("[INFO] If both tests passed, the fix is working")
    print("[INFO] Now run: py control_center.py -> Option 3 (Process Emails)")
    print("[INFO] This will re-process emails with new HTML extraction")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        if "beautifulsoup4" in str(e) or "bs4" in str(e):
            print("\n[ERROR] BeautifulSoup not installed")
            print("[FIX] Run: pip install beautifulsoup4 --break-system-packages")
            print("[OR] Run: pip install -r requirements.txt --break-system-packages")
        else:
            raise
