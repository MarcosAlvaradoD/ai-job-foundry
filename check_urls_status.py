#!/usr/bin/env python3
"""
Quick check of URLs and Status in Google Sheets
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager

def main():
    print("\n" + "="*80)
    print("VERIFICACION RAPIDA - URLs y Status")
    print("="*80)
    
    sm = SheetManager()
    jobs = sm.get_all_jobs()
    
    print(f"\nTotal jobs en Sheets: {len(jobs)}")
    
    # Analyze URLs
    print("\nANALISIS DE URLs:")
    with_url = 0
    without_url = 0
    url_lengths = []
    
    for job in jobs:
        url = job.get('ApplyURL', '')
        if url and url != 'Unknown':
            with_url += 1
            url_lengths.append(len(url))
        else:
            without_url += 1
    
    print(f"  Con URL: {with_url}")
    print(f"  Sin URL: {without_url}")
    if url_lengths:
        print(f"  Longitud promedio URL: {sum(url_lengths)/len(url_lengths):.0f} caracteres")
        print(f"  URL mas corta: {min(url_lengths)} caracteres")
        print(f"  URL mas larga: {max(url_lengths)} caracteres")
    
    # Analyze Status
    print("\nANALISIS DE STATUS:")
    status_counts = {}
    for job in jobs:
        status = job.get('Status', '').strip()
        if not status:
            status = '(empty)'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status:15} : {count:3} jobs")
    
    # Show first 5 jobs with details
    print("\nPRIMEROS 5 JOBS (detalles):")
    print("="*80)
    for i, job in enumerate(jobs[:5], 1):
        company = job.get('Company', 'Unknown')
        role = job.get('Role', 'Unknown')
        url = job.get('ApplyURL', 'N/A')
        status = job.get('Status', 'N/A')
        fit = job.get('FitScore', 'N/A')
        
        print(f"\n{i}. {company} - {role}")
        print(f"   FIT: {fit}/10")
        print(f"   Status: {status}")
        print(f"   URL: {url}")
    
    print("\n" + "="*80)
    print("Verificacion completada")
    print("="*80)

if __name__ == "__main__":
    main()
