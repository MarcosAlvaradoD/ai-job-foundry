#!/usr/bin/env python3
"""
Improved Job Bulletin Processor
Processes emails from Glassdoor, LinkedIn, Indeed that contain MULTIPLE job listings

Key improvements over V1:
- Better HTML parsing
- Salary extraction
- Location filtering
- Pre-filtering by salary
- Direct integration with Google Sheets

Author: Claude + Marcos
Version: 2.0
Date: 2025-11-30
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import re
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

# Load environment
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/spreadsheets']

# Salary thresholds (MXN monthly)
SALARY_THRESHOLDS = {
    "absolute_minimum": 20000,  # Hard blocker
    "acceptable": 30000,         # Penalty -1
    "target": 50000,             # Normal
    "excellent": 80000           # Bonus +1
}

class ImprovedBulletinProcessor:
    """Processes job bulletin emails with multiple listings"""
    
    def __init__(self):
        self.credentials = self._get_credentials()
        self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # Processed cache
        self.processed_cache = Path(__file__).parent.parent.parent / 'data' / 'state' / 'processed_bulletins.txt'
        self.processed_cache.parent.mkdir(parents=True, exist_ok=True)
        
        # Locations to prioritize (Marcos is in Guadalajara, accepts remote)
        self.priority_locations = [
            "guadalajara", "jalisco", "gdl",
            "remote", "remoto", "trabajo desde casa",
            "méxico", "mexico", "latam"
        ]
        
    def _get_credentials(self):
        """Get OAuth credentials"""
        creds = None
        token_path = "data/credentials/token.json"
        credentials_path = "data/credentials/credentials.json"
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def extract_glassdoor_jobs(self, html_content: str) -> List[Dict]:
        """
        Extract jobs from Glassdoor bulletin email
        
        Returns list of jobs with:
        - title
        - company
        - location
        - salary (if available)
        - url
        """
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all job containers (Glassdoor specific structure)
        # Pattern: Jobs are typically in <table> or <div> with specific classes
        
        # Method 1: Find by link patterns
        job_links = soup.find_all('a', href=re.compile(r'glassdoor\.com/job-listing'))
        
        for link in job_links:
            job_url = link.get('href', '')
            
            # Find parent container
            container = link.find_parent(['td', 'div', 'table'])
            if not container:
                continue
            
            # Extract title (usually in the link text or nearby)
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            
            # Extract company (usually near the title)
            company = self._find_nearby_text(container, title, max_distance=2)
            
            # Extract location
            location = self._extract_location(container.get_text())
            
            # Extract salary (if present)
            salary_text = self._extract_salary(container.get_text())
            salary_amount = self._parse_salary(salary_text) if salary_text else None
            
            # Pre-filter by salary
            if salary_amount and salary_amount < SALARY_THRESHOLDS["absolute_minimum"]:
                print(f"⏭️  Skipping {title} - Salary too low: ${salary_amount:,} MXN")
                continue
            
            # Check location priority
            location_priority = self._get_location_priority(location)
            
            job = {
                "title": title,
                "company": company or "Unknown",
                "location": location or "Unknown",
                "salary": salary_text,
                "salary_amount": salary_amount,
                "url": job_url,
                "source": "Glassdoor",
                "location_priority": location_priority,
                "extracted_at": datetime.now().isoformat()
            }
            
            jobs.append(job)
        
        return jobs
    
    def extract_linkedin_jobs(self, html_content: str) -> List[Dict]:
        """Extract jobs from LinkedIn bulletin email"""
        jobs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # LinkedIn job links
        job_links = soup.find_all('a', href=re.compile(r'linkedin\.com/jobs/view/\d+'))
        
        for link in job_links:
            job_url = link.get('href', '')
            
            # Extract job ID from URL
            job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else None
            
            # Find container
            container = link.find_parent(['td', 'div', 'table'])
            if not container:
                continue
            
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            
            # LinkedIn structure usually has company and location nearby
            text = container.get_text()
            company = self._find_company_linkedin(text, title)
            location = self._extract_location(text)
            salary_text = self._extract_salary(text)
            salary_amount = self._parse_salary(salary_text) if salary_text else None
            
            # Pre-filter
            if salary_amount and salary_amount < SALARY_THRESHOLDS["absolute_minimum"]:
                print(f"⏭️  Skipping {title} - Salary too low: ${salary_amount:,} MXN")
                continue
            
            location_priority = self._get_location_priority(location)
            
            job = {
                "title": title,
                "company": company or "Unknown",
                "location": location or "Unknown",
                "salary": salary_text,
                "salary_amount": salary_amount,
                "url": job_url,
                "job_id": job_id,
                "source": "LinkedIn",
                "location_priority": location_priority,
                "extracted_at": datetime.now().isoformat()
            }
            
            jobs.append(job)
        
        return jobs
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        # Common patterns
        patterns = [
            r'(Guadalajara|Zapopan|Tlaquepaque),?\s*Jalisco',
            r'(Ciudad de México|CDMX)',
            r'(Monterrey|Nuevo León)',
            r'(Remote|Remoto|Trabajo desde casa)',
            r'(México|Mexico)',
            r'(LATAM|Latin America)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_salary(self, text: str) -> Optional[str]:
        """Extract salary from text"""
        # Patterns for MXN salary
        patterns = [
            r'\$?\s*(\d{1,3}(?:,?\d{3})*)\s*(?:-|a|to)\s*\$?\s*(\d{1,3}(?:,?\d{3})*)\s*(?:MXN|pesos?|k\$)?',
            r'\$\s*(\d{1,3}(?:,?\d{3})*)\s*(?:MXN|k)',
            r'(\d{1,3})\s*k\$?\s*(?:-|a)\s*(\d{1,3})\s*k\$?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _parse_salary(self, salary_text: str) -> Optional[int]:
        """Parse salary text to get average monthly amount in MXN"""
        if not salary_text:
            return None
        
        # Extract numbers
        numbers = re.findall(r'(\d{1,3}(?:,?\d{3})*)', salary_text)
        if not numbers:
            return None
        
        # Convert to integers
        amounts = [int(n.replace(',', '')) for n in numbers]
        
        # Check if it's in thousands (k$)
        if 'k' in salary_text.lower():
            amounts = [a * 1000 for a in amounts]
        
        # Return average if range, otherwise single value
        return sum(amounts) // len(amounts)
    
    def _get_location_priority(self, location: str) -> int:
        """Get priority score for location (higher = better)"""
        if not location:
            return 0
        
        location_lower = location.lower()
        
        # Priority scores
        if any(p in location_lower for p in ["guadalajara", "gdl"]):
            return 10  # Local - BEST
        if any(p in location_lower for p in ["remote", "remoto", "trabajo desde casa"]):
            return 9   # Remote - EXCELLENT
        if any(p in location_lower for p in ["jalisco"]):
            return 8   # Same state
        if any(p in location_lower for p in ["méxico", "mexico", "latam"]):
            return 6   # Mexico/LATAM - OK
        
        return 3  # Other locations - LOW
    
    def _find_nearby_text(self, container, anchor_text: str, max_distance: int = 2) -> Optional[str]:
        """Find text near an anchor text within container"""
        # Simplified - just get next text after anchor
        text = container.get_text()
        idx = text.find(anchor_text)
        if idx == -1:
            return None
        
        # Get text after anchor
        after_text = text[idx + len(anchor_text):idx + len(anchor_text) + 100]
        
        # Find first substantial word (> 3 chars)
        words = after_text.split()
        for word in words:
            if len(word) > 3 and word.isalnum():
                return word
        
        return None
    
    def _find_company_linkedin(self, text: str, title: str) -> Optional[str]:
        """Extract company name from LinkedIn email text"""
        # LinkedIn usually has pattern: "Title at Company"
        patterns = [
            rf'{re.escape(title)}\s+(?:at|en)\s+([A-Z][A-Za-z0-9\s&.,-]+)',
            r'Company:\s*([A-Z][A-Za-z0-9\s&.,-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                # Clean up
                company = re.sub(r'\s{2,}', ' ', company)
                return company[:50]  # Limit length
        
        return None
    
    def save_to_sheets(self, jobs: List[Dict], tab_name: str = "Glassdoor_Bulletins"):
        """Save jobs to Google Sheets"""
        if not jobs:
            print("No jobs to save")
            return
        
        print(f"\n💾 Saving {len(jobs)} jobs to sheet '{tab_name}'...")
        
        # Prepare rows
        rows = []
        for job in jobs:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M"),  # CreatedAt
                job.get("company", "Unknown"),
                job.get("title", "Unknown"),
                job.get("location", "Unknown"),
                "Unknown",  # RemoteScope
                job.get("url", ""),  # ApplyURL
                job.get("source", "Bulletin"),
                "",  # RecruiterEmail
                "",  # Currency
                job.get("salary", ""),  # Comp
                "",  # Seniority
                "",  # WorkAuthReq
                "New",  # Status
                "Process with AI",  # NextAction
                "",  # Notes
                "",  # FitScore
                "",  # Why
                datetime.now().strftime("%Y-%m-%d"),  # SLA_Date
                ""  # Regio
            ]
            rows.append(row)
        
        # Append to sheet
        try:
            body = {'values': rows}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f"{tab_name}!A:S",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"✅ Saved {len(rows)} jobs to {tab_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to sheets: {e}")
            return False


# CLI
if __name__ == "__main__":
    print("=" * 80)
    print("IMPROVED BULLETIN PROCESSOR V2.0")
    print("=" * 80)
    
    processor = ImprovedBulletinProcessor()
    
    # Test with sample HTML
    sample_html = """
    <table>
        <tr>
            <td>
                <a href="https://www.glassdoor.com/job-listing/jl.htm?id=12345">
                    Gerente de Servicio TI
                </a>
                <div>aronnax</div>
                <div>Guadalajara, Jalisco</div>
                <div>$45,000 - $60,000 MXN</div>
            </td>
        </tr>
        <tr>
            <td>
                <a href="https://www.glassdoor.com/job-listing/jl.htm?id=67890">
                    IT Project Manager
                </a>
                <div>Tech Holding</div>
                <div>Guadalajara</div>
                <div>$50,000 MXN</div>
            </td>
        </tr>
    </table>
    """
    
    jobs = processor.extract_glassdoor_jobs(sample_html)
    
    print(f"\n✅ Extracted {len(jobs)} jobs\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']} (Priority: {job['location_priority']})")
        print(f"   Salary: {job['salary']} (Amount: ${job['salary_amount']:,} MXN)" if job['salary'] else "   Salary: Not specified")
        print(f"   URL: {job['url']}")
        print()
    
    print("=" * 80)
