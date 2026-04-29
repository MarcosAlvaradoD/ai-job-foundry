#!/usr/bin/env python3
"""
Verify LinkedIn job applications status
Check each job URL to see if they're still accepting applications
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from core.sheets.sheet_manager import SheetManager
from core.utils.linkedin_credentials import get_linkedin_credentials
from dotenv import load_dotenv

load_dotenv()

async def check_job_status(page, url: str) -> dict:
    """
    Check if a job is still accepting applications
    
    Returns:
        {
            'url': str,
            'accepting': bool,
            'error_text': str (if not accepting)
        }
    """
    try:
        # Remove trailing slash for consistency
        url = url.rstrip('/')
        
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)
        
        # Look for "No longer accepting" or similar messages in RED
        page_content = await page.content()
        
        # Common rejection messages in LinkedIn
        rejection_phrases = [
            "no longer accepting",
            "no se aceptan solicitudes",
            "no se aceptan aplicaciones",
            "not accepting applications",
            "ya no aceptan",
            "position filled",
            "puesto cubierto"
        ]
        
        # Check if any rejection phrase is in the page
        content_lower = page_content.lower()
        for phrase in rejection_phrases:
            if phrase in content_lower:
                return {
                    'url': url,
                    'accepting': False,
                    'error_text': phrase,
                    'status': 'REJECTED'
                }
        
        # Check if there's an "Easy Apply" button
        try:
            easy_apply_button = page.locator('button:has-text("Easy Apply"), button:has-text("Solicitar")').first
            is_visible = await easy_apply_button.is_visible(timeout=2000)
            if is_visible:
                return {
                    'url': url,
                    'accepting': True,
                    'error_text': None,
                    'status': 'ACTIVE'
                }
        except Exception:
            pass
        
        try:
            easy_apply_button2 = page.locator('button[aria-label*="Easy Apply"]').first
            is_visible2 = await easy_apply_button2.is_visible(timeout=1000)
            if is_visible2:
                return {
                    'url': url,
                    'accepting': True,
                    'error_text': None,
                    'status': 'ACTIVE'
                }
        except Exception:
            pass
        
        return {
            'url': url,
            'accepting': True,  # Assume accepting if we don't see rejection
            'error_text': None,
            'status': 'ACTIVE'
        }
        
    except Exception as e:
        return {
            'url': url,
            'accepting': None,
            'error_text': str(e),
            'status': 'ERROR'
        }

async def verify_all_jobs():
    """Verify all jobs in the list"""
    sm = SheetManager()
    jobs = sm.get_all_jobs('linkedin')
    
    valid_jobs = [j for j in jobs 
                  if (j.get('Status', '').lower() != 'expired' and 
                      j.get('ApplyURL', '').strip() and 
                      j.get('FitScore', '') and 
                      str(j.get('FitScore', '')).replace('.', '').isdigit() and
                      float(j.get('FitScore', '0')) >= 7)]
    
    valid_jobs.sort(key=lambda x: (float(x.get('FitScore', '0')), x.get('CreatedAt', '')), reverse=True)
    
    email, password = get_linkedin_credentials()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        print("🔐 Logging in...")
        await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        await asyncio.sleep(5)
        
        print(f"\n✅ Checking {len(valid_jobs[:13])} job offers...\n")
        print("="*80)
        
        results = {
            'active': [],
            'rejected': [],
            'errors': []
        }
        
        for i, job in enumerate(valid_jobs[:13], 1):
            url = job.get('ApplyURL', '')
            role = job.get('Role', 'Unknown')[:35]
            fit = job.get('FitScore')
            row = job.get('_row')
            
            print(f"\n{i:2}. Row {row:3} | FIT {fit:4} | Checking...")
            print(f"    Role: {role}")
            print(f"    URL: {url}")
            
            result = await check_job_status(page, url)
            
            if result['accepting']:
                print(f"    ✅ {result['status']} - ACCEPTING APPLICATIONS")
                results['active'].append({
                    'url': url,
                    'role': role,
                    'fit': fit,
                    'row': row,
                    'job': job
                })
            else:
                print(f"    ❌ REJECTED - {result['error_text']}")
                results['rejected'].append({
                    'url': url,
                    'reason': result['error_text'],
                    'row': row
                })
            
            await asyncio.sleep(3)
        
        await browser.close()
        
        print("\n" + "="*80)
        print(f"\n📊 VERIFICATION RESULTS:")
        print(f"   ✅ Active (Ready to apply): {len(results['active'])}")
        print(f"   ❌ Rejected (Need to remove): {len(results['rejected'])}")
        print(f"   ⚠️  Errors: {len(results['errors'])}")
        
        if results['rejected']:
            print(f"\n🗑️  Rejected Offers to DELETE:")
            for r in results['rejected']:
                print(f"   Row {r['row']}: {r['reason']}")
        
        print(f"\n✅ Active Offers (Ready for auto-apply):")
        for i, r in enumerate(results['active'], 1):
            print(f"   {i:2}. FIT {r['fit']:4} | Row {r['row']:3} | {r['role']}")
        
        return results

if __name__ == "__main__":
    print("="*80)
    print("🔍 VERIFY LINKEDIN JOB APPLICATIONS STATUS")
    print("="*80)
    
    results = asyncio.run(verify_all_jobs())
