"""
Verifica si una URL de Glassdoor esta activa
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import requests
from time import sleep

def check_url(url):
    """Verifica si una URL de Glassdoor esta activa"""
    print(f"\nVerificando URL...")
    print(f"URL: {url[:80]}...\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url[:80]}...")
        
        # Check if job is expired
        content = response.text.lower()
        
        expired_markers = [
            'no longer accepting',
            'no est� disponible',
            'job has expired',
            'expired',
            'no longer available'
        ]
        
        is_expired = any(marker in content for marker in expired_markers)
        
        if is_expired:
            print("\n[EXPIRED] Job is no longer available")
            return False
        elif response.status_code == 200:
            print("\n[ACTIVE] Job appears to be active!")
            
            # Try to detect apply button
            if 'apply' in content or 'aplicar' in content:
                print("[+] Apply button detected")
            
            return True
        else:
            print(f"\n[ERROR] Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

if __name__ == "__main__":
    # Infosys Technology Lead URL
    url = "https://www.glassdoor.com.mx/partner/jobListing.htm?cpc=01657B10174A43CF&jrtk=5-yul1-1-1j7mcrkmliue2800-1ec58aa0c55031da---6NYlbfkN0DFi1nmQQWK2fa3N4W3y7EUOEocZkWPqKP_f_xZ7ne8RaTQsSLh2dRP_6xckaebLvYU1yX8UHqcqZilPf0z9Uh_LpSExijevdhh0-gVKylfuNdcZ0ev9scdTHe6McOUEuzH3GB_wQ0xuho_JM04AgWpZ62da9AtQ40VyEfvFjz99x9tZqc93cMNWGQ1QBM98tJ0fxvlhzvxwg8tVpSSMYzsRQa1nBIbWncDj3rtXlbM5b0qQ71u188DIcy5BubLtkbrFSZgWZQoMAqkBIuzmeYr-SsmimmeSAkncrFHoaVts_0lLRGHZcm11X7qomZBFHRCtSDYPHt1kavv_w6I3YrbW-oceSCtPD5rt8QDuIm2fawz7YI9FvrxUO9gMMr2D9qau62zHHcIw54aDaJB1ouCsiRIgsNgoMqztnZAl5lmA7b5I67PEYpq17uiEFCfnQzQG-cMQmz2aeWcnoj5mnxhR1tVavDS-y341VQaRRHyWT0-x_-ZMnFKGD2zvd2NhzATrNvlwU_FkfGRHGEtIPtPrqSuv2LlEeIyZPsi-FXQf6is961CpPKO5RTd8d05akOXgKqxZwrO8pMbAQzpM1dFKSxjmlRBBLiBjpmHfGjZtHi8gtuNy7menKOZn3TAbn7COgMPDS6rRdX0Gg9OagP_J2GBIfgH7uk80c922NAGL5MQxBSed9hWhqcvqksOOFGK90ctRuPfc0PKSiEZhG_fmMDjBEGwAcu23-lGUJtXpBHQL7HfgmLeZ27KVSsMd2IonZAdjNL4mawvM1mMhdYM"
    
    result = check_url(url)
    
    if result:
        print("\n" + "="*70)
        print("NEXT STEP: Open this URL in browser to analyze apply process")
        print("="*70)
        print(f"\n{url}")
