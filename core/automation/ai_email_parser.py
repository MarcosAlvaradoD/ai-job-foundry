"""
AI-POWERED EMAIL PARSER - Uses LM Studio to intelligently parse job bulletins

This replaces brittle regex patterns with AI that can:
- Understand HTML structure dynamically
- Extract job data even when format changes
- Learn from examples

Location: core/automation/ai_email_parser.py
"""

import os
import re
import json
from typing import List, Dict, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class AIEmailParser:
    """
    Parse job bulletin emails using AI instead of rigid regex
    
    Benefits:
    - Adapts to format changes automatically
    - Understands context better than regex
    - Can handle multiple email formats
    """
    
    def __init__(self, llm_url: str = None, model: str = None):
        """
        Initialize AI parser
        
        Args:
            llm_url: LM Studio URL (default from env)
            model: Model name (default from env)
        """
        self.llm_url = llm_url or os.getenv('LLM_URL', 'http://127.0.0.1:11434/v1/chat/completions')
        self.model = model or os.getenv('LLM_MODEL', 'qwen2.5-14b-instruct')
    
    def parse_glassdoor_bulletin(self, html_content: str) -> List[Dict]:
        """
        Parse Glassdoor bulletin email using AI
        
        Args:
            html_content: Raw HTML from email
            
        Returns:
            List of job dictionaries with: title, company, location, url
        """
        
        # Step 1: Extract job_listing_ids with regex (this still works)
        job_ids = self._extract_job_ids(html_content)
        
        if not job_ids:
            print("   ⚠️  No job IDs found in email")
            return []
        
        print(f"   🔍 Found {len(job_ids)} job IDs, analyzing with AI...")
        
        # Step 2: Use AI to extract job details from HTML
        jobs = self._ai_extract_job_details(html_content, job_ids)
        
        return jobs
    
    def _extract_job_ids(self, html_content: str) -> List[str]:
        """
        Extract job_listing_id from tracking pixels
        
        These are in URLs like:
        utm_content=ja-jobpos1-age5d-1009965617382
        """
        
        # Pattern: job ID in tracking pixel (starts with 1009)
        pattern = r'utm_content=ja-jobpos\d+-[^-]+-(\d{13})'
        ids = re.findall(pattern, html_content)
        
        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(ids))
        
        return unique_ids
    
    def _ai_extract_job_details(self, html_content: str, job_ids: List[str]) -> List[Dict]:
        """
        Use AI to extract job titles, companies, and locations from HTML
        
        STRATEGY: Instead of processing entire HTML at once, we:
        1. Find each job_id position in HTML
        2. Extract a small chunk (500 chars context)
        3. Let AI analyze just that chunk
        4. This works for ANY email size!
        """
        
        jobs = []
        
        print(f"   🤖 Processing {len(job_ids)} jobs with AI chunking...")
        
        for i, job_id in enumerate(job_ids, 1):
            try:
                # Find context around this job ID
                chunk = self._extract_job_context(html_content, job_id)
                
                if not chunk:
                    print(f"   ⚠️  [{i}/{len(job_ids)}] No context found for {job_id}")
                    jobs.append(self._create_minimal_job(job_id))
                    continue
                
                # Process this single job with AI
                job = self._ai_extract_single_job(chunk, job_id, i, len(job_ids))
                jobs.append(job)
                
            except Exception as e:
                print(f"   ⚠️  [{i}/{len(job_ids)}] Failed: {e}")
                jobs.append(self._create_minimal_job(job_id))
        
        return jobs
    
    def parse_generic_bulletin(self, html_content: str, source: str = 'Unknown') -> List[Dict]:
        """
        Parse generic job bulletin email using AI (for Adzuna, ComputraBajo, JobLeads, etc)
        
        This method uses AI to extract job listings from HTML without relying on 
        provider-specific patterns or IDs.
        
        Args:
            html_content: Raw HTML from email
            source: Job board name (e.g., 'Adzuna', 'ComputraBajo', 'JobLeads')
            
        Returns:
            List of job dictionaries with: Role, Company, Location, ApplyURL, etc
        """
        print(f"   🤖 Using AI to parse {source} bulletin...")
        
        try:
            # Clean HTML for AI processing
            cleaned_html = self._clean_html_for_ai(html_content)
            
            # Build AI prompt
            prompt = f"""Extract ALL job listings from this {source} email HTML.

Return a JSON array with this structure:
[
  {{
    "title": "Job Title",
    "company": "Company Name", 
    "location": "Location",
    "url": "https://..."
  }}
]

HTML:
{cleaned_html[:8000]}

IMPORTANT:
- Extract EVERY job listing you find
- URLs must be complete and valid
- If any field is missing, use "Unknown"
- Return ONLY the JSON array, no other text"""
            
            # Call LLM
            response = self._call_llm(prompt, timeout=30)
            
            # Parse response
            jobs = self._parse_generic_ai_response(response, source)
            
            if jobs:
                print(f"   ✅ AI extracted {len(jobs)} jobs from {source}")
                return jobs
            else:
                print(f"   ⚠️  AI returned 0 jobs from {source}")
                return []
                
        except Exception as e:
            print(f"   ❌ AI parsing failed for {source}: {e}")
            return []
    
    def _parse_generic_ai_response(self, ai_response: str, source: str) -> List[Dict]:
        """
        Parse AI response for generic bulletin parsing
        
        Args:
            ai_response: Raw AI response (should be JSON)
            source: Job board name
            
        Returns:
            List of job dictionaries
        """
        try:
            # Clean response
            response = ai_response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
                response = response.strip()
            
            # Parse JSON
            jobs_data = json.loads(response)
            
            if not isinstance(jobs_data, list):
                print(f"   ⚠️  AI response is not a list")
                return []
            
            # Convert to our format
            jobs = []
            for job_data in jobs_data:
                job = {
                    'Source': source,
                    'Role': job_data.get('title', 'Unknown'),
                    'Company': job_data.get('company', 'Unknown'),
                    'Location': job_data.get('location', 'Unknown'),
                    'ApplyURL': job_data.get('url', ''),
                    'Comp': '',
                    'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': 'New'
                }
                
                # Only add if we have at least a URL
                if job['ApplyURL']:
                    jobs.append(job)
            
            return jobs
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse AI JSON response: {e}")
            print(f"   📄 Raw response: {ai_response[:200]}...")
            return []
        except Exception as e:
            print(f"   ⚠️  Error parsing AI response: {e}")
            return []
    
    def _extract_job_context(self, html_content: str, job_id: str) -> str:
        """
        Extract a chunk of HTML around a specific job_id
        
        NEW STRATEGY (2025-12-17):
        The job_id appears in tracking pixels (utm_content=ja-jobpos1-age5d-1009965617382)
        But the job title/company appear in a DIFFERENT part of the HTML structure.
        
        Solution: Search for job listing patterns near any mention of the job_id,
        including in links and tracking URLs.
        
        Returns ~2000 characters of context for better extraction
        """
        
        # Strategy 1: Find the job_id in ANY URL parameter
        # Pattern: job_id in various formats
        patterns = [
            rf'utm_content=ja-jobpos\d+-[^-]+-{job_id}',  # Tracking pixel
            rf'jobListingId={job_id}',                     # Direct parameter
            rf'job-listing/JL_{job_id}',                   # Direct link
        ]
        
        best_idx = -1
        for pattern in patterns:
            import re
            match = re.search(pattern, html_content)
            if match:
                best_idx = match.start()
                break
        
        if best_idx == -1:
            # Fallback: search for raw job_id
            best_idx = html_content.find(job_id)
        
        if best_idx == -1:
            return ""
        
        # Extract LARGER context (1000 chars before and after)
        # This increases chance of capturing job details
        context_size = 1000
        start = max(0, best_idx - context_size)
        end = min(len(html_content), best_idx + context_size)
        
        chunk = html_content[start:end]
        
        return chunk
    
    def _ai_extract_single_job(self, html_chunk: str, job_id: str, current: int, total: int) -> Dict:
        """
        Use AI to extract details for a SINGLE job from a small HTML chunk
        
        This is fast (1-2 seconds) because the chunk is tiny
        
        UPDATED (2025-12-17): Better error logging and longer timeout
        """
        
        # Build prompt for this single job
        prompt = f"""Extract job information from this HTML snippet.

This is job ID: {job_id}

HTML SNIPPET:
```
{html_chunk[:1500]}
```

Find:
1. Job title (look for <p>, <h2>, <strong> tags with job names)
2. Company name (usually appears before or after title)
3. Location (city, state/country)

Respond with ONLY valid JSON (no markdown, no code fences):
{{
  "title": "exact job title",
  "company": "company name",
  "location": "city, state/country"
}}

If you can't find a field, use "Unknown"."""
        
        try:
            # Call LLM with LONGER timeout (20s to account for model loading)
            response = self._call_llm(prompt, timeout=20)
            
            # Debug: Print response to see what we got
            # print(f"   🔍 RAW AI Response: {response[:200]}")
            
            # Parse response
            clean_response = response.strip().replace('```json', '').replace('```', '')
            job_data = json.loads(clean_response)
            
            title = job_data.get('title', 'Unknown')
            company = job_data.get('company', 'Unknown')
            location = job_data.get('location', 'Unknown')
            
            # Show extracted info (truncated)
            display_title = title[:40] + "..." if len(title) > 40 else title
            print(f"   ✅ [{current}/{total}] {display_title}")
            
            return {
                'Source': 'Glassdoor',
                'ApplyURL': f"https://www.glassdoor.com/job-listing/JL_{job_id}.htm",
                'Role': title,
                'Company': company,
                'Location': location,
                'Comp': '',
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Status': 'New'
            }
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  [{current}/{total}] JSON parse failed: {e}")
            print(f"       Response was: {response[:200] if 'response' in locals() else 'N/A'}")
            return self._create_minimal_job(job_id)
        except requests.exceptions.Timeout:
            print(f"   ⚠️  [{current}/{total}] Timeout (20s exceeded)")
            return self._create_minimal_job(job_id)
        except Exception as e:
            print(f"   ⚠️  [{current}/{total}] Error: {type(e).__name__}: {e}")
            return self._create_minimal_job(job_id)
        
        # Call LM Studio
        try:
            response = self._call_llm(prompt)
            
            # Parse AI response (should be JSON)
            jobs_data = self._parse_ai_response(response, job_ids)
            
            return jobs_data
            
        except Exception as e:
            print(f"   ⚠️  AI extraction failed: {e}")
            # Fallback: Create jobs with just IDs
            return self._create_minimal_jobs(job_ids)
    
    def _clean_html_for_ai(self, html: str) -> str:
        """
        Simplify HTML for AI processing
        
        - Remove scripts and styles
        - Keep only content-bearing tags
        - Limit size to fit in context
        """
        
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
        
        # Remove tracking pixels and images
        html = re.sub(r'<img[^>]*>', '', html)
        
        # Keep only semantic HTML
        # Extract text content from divs, spans, tds, etc
        
        # For now, just limit size
        max_size = 15000  # characters
        if len(html) > max_size:
            # Take first part (usually has job listings)
            html = html[:max_size]
        
        return html
    
    def _build_extraction_prompt(self, html_snippet: str, job_ids: List[str]) -> str:
        """
        Build prompt for AI to extract job data
        """
        
        prompt = f"""You are an expert at parsing job bulletin emails. Extract job information from this Glassdoor email HTML.

The email contains {len(job_ids)} jobs with these IDs: {', '.join(job_ids[:5])}{'...' if len(job_ids) > 5 else ''}

For each job, find:
1. Job title
2. Company name  
3. Location (city, state/country)

HTML SNIPPET:
```
{html_snippet[:8000]}
```

Respond with ONLY valid JSON in this exact format:
{{
  "jobs": [
    {{
      "job_id": "1009965617382",
      "title": "Analista con experiencia en master data de SAP",
      "company": "Interax",
      "location": "Guadalajara, Jalisco"
    }}
  ]
}}

CRITICAL RULES:
- Extract ALL jobs you can find
- If you can't find a field, use "Unknown"
- Respond with ONLY the JSON, no explanations
- Do NOT include any markdown code fences
"""
        
        return prompt
    
    def _call_llm(self, prompt: str, timeout: int = 30) -> str:
        """Call LM Studio API with configurable timeout"""
        
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,  # Low temperature for consistency
                    "max_tokens": 1000   # Reduced for faster responses
                },
                timeout=timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content from response
            content = data['choices'][0]['message']['content']
            
            return content
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM API error: {e}")
    
    def _parse_ai_response(self, ai_response: str, job_ids: List[str]) -> List[Dict]:
        """
        Parse AI response into job dictionaries
        """
        
        try:
            # Clean response (remove markdown fences if present)
            clean_response = ai_response.strip()
            clean_response = re.sub(r'^```json\s*', '', clean_response)
            clean_response = re.sub(r'\s*```$', '', clean_response)
            
            # Parse JSON
            data = json.loads(clean_response)
            
            jobs = []
            for job_data in data.get('jobs', []):
                job_id = job_data.get('job_id', 'Unknown')
                
                # Create job dictionary
                job = {
                    'Source': 'Glassdoor',
                    'ApplyURL': f"https://www.glassdoor.com/job-listing/JL_{job_id}.htm" if job_id != 'Unknown' else 'Unknown',
                    'Role': job_data.get('title', 'Unknown'),
                    'Company': job_data.get('company', 'Unknown'),
                    'Location': job_data.get('location', 'Unknown'),
                    'Comp': '',
                    'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': 'New'
                }
                jobs.append(job)
            
            # If AI found fewer jobs than IDs, fill in the rest
            if len(jobs) < len(job_ids):
                print(f"   ⚠️  AI found {len(jobs)}/{len(job_ids)} jobs, creating placeholders for rest")
                for i in range(len(jobs), len(job_ids)):
                    jobs.append(self._create_minimal_job(job_ids[i]))
            
            return jobs
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse AI response as JSON: {e}")
            print(f"   Response was: {ai_response[:200]}...")
            # Fallback
            return self._create_minimal_jobs(job_ids)
    
    def _create_minimal_jobs(self, job_ids: List[str]) -> List[Dict]:
        """Create job entries with just IDs when AI fails"""
        return [self._create_minimal_job(job_id) for job_id in job_ids]
    
    def _create_minimal_job(self, job_id: str) -> Dict:
        """Create single job entry with just ID"""
        return {
            'Source': 'Glassdoor',
            'ApplyURL': f"https://www.glassdoor.com/job-listing/JL_{job_id}.htm",
            'Role': 'Unknown - Pending AI Analysis',
            'Company': 'Unknown',
            'Location': 'Unknown',
            'Comp': '',
            'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Status': 'New'
        }


def test_ai_parser():
    """Test the AI parser with sample HTML"""
    
    print("\n" + "="*70)
    print("TESTING AI EMAIL PARSER")
    print("="*70)
    
    # Load the debug HTML
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    debug_file = project_root / "debug_glassdoor_email.html"
    
    if not debug_file.exists():
        print(f"❌ Debug file not found: {debug_file}")
        return
    
    with open(debug_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"✅ Loaded HTML: {len(html)} characters")
    
    # Create parser
    parser = AIEmailParser()
    
    # Parse
    jobs = parser.parse_glassdoor_bulletin(html)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total jobs extracted: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}] {job['Role']}")
        print(f"    Company: {job['Company']}")
        print(f"    Location: {job['Location']}")
        print(f"    URL: {job['ApplyURL']}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_ai_parser()
