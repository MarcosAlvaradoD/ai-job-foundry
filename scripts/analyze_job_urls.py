#!/usr/bin/env python3
"""
AI JOB FOUNDRY - URL JOB ANALYZER
Analiza vacantes desde URLs usando Playwright + LM Studio

Este script:
1. Toma URLs de vacantes (cualquier sitio)
2. Usa Playwright para extraer contenido completo
3. Analiza con IA (LM Studio) para calcular FIT score
4. Guarda resultados en Google Sheets

Uso:
    py scripts\analyze_job_urls.py --urls "url1,url2,url3"
    py scripts\analyze_job_urls.py --file urls.txt
    py scripts\analyze_job_urls.py --range 260-265  # Para RH-IT Home consecutivas
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import argparse
import json
from core.enrichment.ai_analyzer import AIAnalyzer
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
import os

load_dotenv()


class URLJobAnalyzer:
    """Analiza vacantes desde URLs usando Playwright + IA"""
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.sheet_manager = SheetManager()
    
    async def extract_job_content(self, url: str) -> dict:
        """
        Extrae contenido de una vacante usando Playwright
        
        Returns:
            {
                'url': str,
                'title': str,
                'company': str,
                'location': str,
                'description': str,
                'requirements': str,
                'full_text': str
            }
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print(f"\n🔍 Analyzing: {url}")
                
                # Navigate
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                
                # Extract text content
                full_text = await page.inner_text('body')
                
                # Try to extract structured data
                title = "Unknown"
                company = "Unknown"
                location = "Unknown"
                
                # Common selectors (adapt based on site)
                title_selectors = [
                    'h1', 
                    '.job-title', 
                    '[class*="title"]',
                    '[class*="puesto"]',
                    '[class*="vacante"]'
                ]
                
                for selector in title_selectors:
                    try:
                        title_elem = await page.query_selector(selector)
                        if title_elem:
                            title = await title_elem.inner_text()
                            title = title.strip()
                            if title and len(title) > 3:
                                break
                    except:
                        continue
                
                # Extract company
                company_selectors = [
                    '.company',
                    '[class*="empresa"]',
                    '[class*="company"]'
                ]
                
                for selector in company_selectors:
                    try:
                        company_elem = await page.query_selector(selector)
                        if company_elem:
                            company = await company_elem.inner_text()
                            company = company.strip()
                            if company and len(company) > 2:
                                break
                    except:
                        continue
                
                # Extract location
                location_selectors = [
                    '.location',
                    '[class*="ubicacion"]',
                    '[class*="location"]',
                    '[class*="lugar"]'
                ]
                
                for selector in location_selectors:
                    try:
                        location_elem = await page.query_selector(selector)
                        if location_elem:
                            location = await location_elem.inner_text()
                            location = location.strip()
                            if location and len(location) > 2:
                                break
                    except:
                        continue
                
                await browser.close()
                
                return {
                    'url': url,
                    'title': title,
                    'company': company,
                    'location': location,
                    'full_text': full_text[:5000],  # Limit to 5000 chars
                    'extracted_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"  ❌ Error extracting from {url}: {e}")
                await browser.close()
                return None
    
    def analyze_with_ai(self, job_content: dict) -> dict:
        """
        Analiza el contenido con IA para calcular FIT score
        
        Returns:
            {
                'fit_score': int,
                'why': str,
                'role': str,
                'company': str,
                'location': str,
                'remote_scope': str,
                'seniority': str
            }
        """
        print(f"  🤖 Analyzing with AI...")
        
        # Prepare analysis request
        job_data = {
            'Role': job_content.get('title', 'Unknown'),
            'Company': job_content.get('company', 'Unknown'),
            'Location': job_content.get('location', 'Unknown'),
            'ApplyURL': job_content.get('url', ''),
            'full_description': job_content.get('full_text', '')
        }
        
        # Use AI analyzer
        result = self.ai_analyzer.analyze_job(job_data)
        
        return {
            'fit_score': result.get('fit_score', 0),
            'why': result.get('why', ''),
            'role': result.get('role', job_content.get('title', 'Unknown')),
            'company': result.get('company', job_content.get('company', 'Unknown')),
            'location': result.get('location', job_content.get('location', 'Unknown')),
            'remote_scope': result.get('remote_scope', 'Unknown'),
            'seniority': result.get('seniority', 'Unknown')
        }
    
    async def process_url(self, url: str) -> dict:
        """Process a single URL: extract + analyze"""
        # Extract content
        content = await self.extract_job_content(url)
        
        if not content:
            return None
        
        # Analyze with AI
        analysis = self.analyze_with_ai(content)
        
        # Combine results
        result = {
            'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'Company': analysis['company'],
            'Role': analysis['role'],
            'Location': analysis['location'],
            'RemoteScope': analysis['remote_scope'],
            'ApplyURL': url,
            'Source': 'URL_Analyzer',
            'Seniority': analysis['seniority'],
            'Status': 'Pending',
            'NextAction': 'Review FIT score',
            'FitScore': analysis['fit_score'],
            'Why': analysis['why']
        }
        
        print(f"  ✅ FIT SCORE: {analysis['fit_score']}/10")
        print(f"  📋 {analysis['role']} at {analysis['company']}")
        
        return result
    
    async def process_urls(self, urls: list) -> list:
        """Process multiple URLs"""
        results = []
        
        for url in urls:
            result = await self.process_url(url)
            if result:
                results.append(result)
            
            # Delay between requests
            await asyncio.sleep(3)
        
        return results
    
    def save_to_sheets(self, jobs: list, tab: str = 'Jobs'):
        """Save analyzed jobs to Google Sheets"""
        if not jobs:
            print("\n⚠️  No jobs to save")
            return
        
        print(f"\n💾 Saving {len(jobs)} jobs to Google Sheets...")
        
        # Convert to rows
        rows = []
        for job in jobs:
            row = [
                job.get('CreatedAt', ''),
                job.get('Company', ''),
                job.get('Role', ''),
                job.get('Location', ''),
                job.get('RemoteScope', ''),
                job.get('ApplyURL', ''),
                job.get('Source', ''),
                job.get('RecruiterEmail', ''),
                job.get('Currency', ''),
                job.get('Comp', ''),
                job.get('Seniority', ''),
                job.get('WorkAuthReq', ''),
                job.get('Status', ''),
                job.get('NextAction', ''),
                job.get('Notes', ''),
                job.get('FitScore', ''),
                job.get('Why', ''),
                job.get('SLA_Date', ''),
                job.get('Regio', '')
            ]
            rows.append(row)
        
        # Append to sheet
        success = self.sheet_manager.append_rows(tab, rows)
        
        if success:
            print(f"  ✅ Saved {len(rows)} jobs to {tab} tab")
        else:
            print(f"  ❌ Failed to save to Sheets")


async def main():
    parser = argparse.ArgumentParser(description='Analyze job URLs with Playwright + AI')
    parser.add_argument('--urls', help='Comma-separated URLs')
    parser.add_argument('--file', help='File with URLs (one per line)')
    parser.add_argument('--range', help='Range for consecutive URLs (e.g., 260-265 for RH-IT Home)')
    parser.add_argument('--base-url', default='https://vacantes.rh-itchome.com/vacante/', 
                       help='Base URL for range mode')
    parser.add_argument('--tab', default='Jobs', help='Google Sheets tab to save to')
    
    args = parser.parse_args()
    
    # Collect URLs
    urls = []
    
    if args.urls:
        urls = [u.strip() for u in args.urls.split(',')]
    
    elif args.file:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    
    elif args.range:
        # Parse range (e.g., "260-265")
        start, end = map(int, args.range.split('-'))
        urls = [f"{args.base_url}{i}" for i in range(start, end + 1)]
    
    else:
        print("❌ Error: Must provide --urls, --file, or --range")
        return
    
    print("\n" + "="*70)
    print("🎯 AI JOB FOUNDRY - URL JOB ANALYZER")
    print("="*70)
    print(f"\n📋 URLs to analyze: {len(urls)}")
    for url in urls:
        print(f"  - {url}")
    print()
    
    # Process
    analyzer = URLJobAnalyzer()
    jobs = await analyzer.process_urls(urls)
    
    # Save
    analyzer.save_to_sheets(jobs, tab=args.tab)
    
    print("\n" + "="*70)
    print(f"✅ DONE! Analyzed {len(jobs)} jobs")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
