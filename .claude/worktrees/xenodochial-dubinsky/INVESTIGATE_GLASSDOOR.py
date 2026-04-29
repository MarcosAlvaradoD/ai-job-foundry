"""
Investiga el proceso de aplicacion de Glassdoor con Playwright
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
import time

def investigate_glassdoor_job(url):
    """
    Investiga una oferta de Glassdoor para entender el proceso de aplicacion
    """
    print("\n" + "="*70)
    print("GLASSDOOR JOB INVESTIGATION")
    print("="*70 + "\n")
    
    print(f"URL: {url[:80]}...\n")
    
    with sync_playwright() as p:
        # Launch browser (headful para que Marcos pueda ver)
        print("[1/5] Launching browser...")
        browser = p.firefox.launch(
            headless=False,  # Visible
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            # Navigate to job
            print("[2/5] Navigating to job...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Take screenshot
            print("[3/5] Taking screenshot...")
            page.screenshot(path='glassdoor_job_page.png', full_page=True)
            print("   Screenshot saved: glassdoor_job_page.png")
            
            # Check if job is expired
            print("[4/5] Checking job status...")
            page_content = page.content().lower()
            
            expired_markers = [
                'no longer accepting',
                'no esta disponible',
                'job has expired',
                'expired',
                'no longer available'
            ]
            
            is_expired = any(marker in page_content for marker in expired_markers)
            
            if is_expired:
                print("   [EXPIRED] Job is no longer available")
                browser.close()
                return False
            
            print("   [ACTIVE] Job appears to be active!")
            
            # Look for apply button
            print("[5/5] Analyzing apply process...")
            
            # Common Glassdoor selectors
            apply_selectors = [
                'button:has-text("Apply")',
                'button:has-text("Aplicar")',
                'a:has-text("Apply")',
                'a:has-text("Aplicar")',
                '[data-test="apply-button"]',
                '.apply-button',
                '#apply-button'
            ]
            
            apply_button = None
            for selector in apply_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        apply_button = page.locator(selector).first
                        print(f"   [+] Found apply button: {selector}")
                        break
                except Exception:
                    pass
            
            if not apply_button:
                print("   [!] No apply button found")
                print("   [!] Job might redirect to external site")
                
                # Look for external apply link
                external_links = page.locator('a[href*="apply"]').all()
                if external_links:
                    print(f"   [+] Found {len(external_links)} potential apply links")
                    for i, link in enumerate(external_links[:3]):
                        try:
                            href = link.get_attribute('href')
                            text = link.inner_text()
                            print(f"      {i+1}. {text}: {href[:50]}...")
                        except Exception:
                            pass
            
            # Get page title and company
            title = page.title()
            print(f"\n   Page Title: {title}")
            
            # Wait for user to see
            print("\n" + "="*70)
            print("Browser will stay open for 30 seconds for inspection...")
            print("="*70)
            time.sleep(30)
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return False

if __name__ == "__main__":
    # Infosys Technology Lead URL
    url = "https://www.glassdoor.com.mx/partner/jobListing.htm?cpc=01657B10174A43CF&jrtk=5-yul1-1-1j7mcrkmliue2800-1ec58aa0c55031da---6NYlbfkN0DFi1nmQQWK2fa3N4W3y7EUOEocZkWPqKP_f_xZ7ne8RaTQsSLh2dRP_6xckaebLvYU1yX8UHqcqZilPf0z9Uh_LpSExijevdhh0-gVKylfuNdcZ0ev9scdTHe6McOUEuzH3GB_wQ0xuho_JM04AgWpZ62da9AtQ40VyEfvFjz99x9tZqc93cMNWGQ1QBM98tJ0fxvlhzvxwg8tVpSSMYzsRQa1nBIbWncDj3rtXlbM5b0qQ71u188DIcy5BubLtkbrFSZgWZQoMAqkBIuzmeYr-SsmimmeSAkncrFHoaVts_0lLRGHZcm11X7qomZBFHRCtSDYPHt1kavv_w6I3YrbW-oceSCtPD5rt8QDuIm2fawz7YI9FvrxUO9gMMr2D9qau62zHHcIw54aDaJB1ouCsiRIgsNgoMqztnZAl5lmA7b5I67PEYpq17uiEFCfnQzQG-cMQmz2aeWcnoj5mnxhR1tVavDS-y341VQaRRHyWT0-x_-ZMnFKGD2zvd2NhzATrNvlwU_FkfGRHGEtIPtPrqSuv2LlEeIyZPsi-FXQf6is961CpPKO5RTd8d05akOXgKqxZwrO8pMbAQzpM1dFKSxjmlRBBLiBjpmHfGjZtHi8gtuNy7menKOZn3TAbn7COgMPDS6rRdX0Gg9OagP_J2GBIfgH7uk80c922NAGL5MQxBSed9hWhqcvqksOOFGK90ctRuPfc0PKSiEZhG_fmMDjBEGwAcu23-lGUJtXpBHQL7HfgmLeZ27KVSsMd2IonZAdjNL4mawvM1mMhdYM"
    
    result = investigate_glassdoor_job(url)
    
    if result:
        print("\n[SUCCESS] Investigation complete")
        print("Check screenshot: glassdoor_job_page.png")
    else:
        print("\n[FAILED] Could not investigate job")
