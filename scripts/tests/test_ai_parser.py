"""
TEST AI EMAIL PARSER
Location: scripts/tests/test_ai_parser.py

Quick test to see if AI can extract job data from Glassdoor email
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env
env_path = project_root / ".env"
load_dotenv(env_path)

from core.automation.ai_email_parser import AIEmailParser

def main():
    print("\n" + "="*70)
    print("🧪 TESTING AI EMAIL PARSER")
    print("="*70)
    
    # Load HTML
    html_file = project_root / "debug_glassdoor_email.html"
    
    if not html_file.exists():
        print(f"❌ File not found: {html_file}")
        print("\n💡 Please ensure debug_glassdoor_email.html is in project root")
        return
    
    print(f"✅ Loading HTML from: {html_file}")
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"   File size: {len(html):,} characters")
    
    # Create parser
    print("\n🤖 Initializing AI parser...")
    
    # Let AIEmailParser read from .env (already loaded above)
    parser = AIEmailParser()
    
    print(f"   LLM URL: {parser.llm_url}")
    print(f"   Model: {parser.model}")
    
    # Parse email
    print("\n🔍 Parsing email with AI...")
    try:
        jobs = parser.parse_glassdoor_bulletin(html)
        
        print(f"\n✅ EXTRACTION COMPLETE!")
        print(f"   Total jobs found: {len(jobs)}")
        
        if jobs:
            print("\n📋 JOB DETAILS:")
            print("-" * 70)
            
            for i, job in enumerate(jobs, 1):
                print(f"\n[Job {i}]")
                print(f"  Title:    {job['Role']}")
                print(f"  Company:  {job['Company']}")
                print(f"  Location: {job['Location']}")
                print(f"  URL:      {job['ApplyURL']}")
                print(f"  Source:   {job['Source']}")
        else:
            print("\n⚠️  No jobs extracted")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
