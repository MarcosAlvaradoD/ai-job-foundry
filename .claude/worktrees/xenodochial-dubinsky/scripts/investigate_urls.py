#!/usr/bin/env python3
"""
URL Investigation Script
Investigates why 87.5% of jobs don't have URLs

Checks:
1. Which sources have URLs (scrapers vs email)
2. Email processing logs
3. URL extraction method
4. Sample email analysis

Usage:
    py investigate_urls.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager

def main():
    print("\n" + "="*80)
    print("URL INVESTIGATION - Why 87.5% of jobs have no URLs?")
    print("="*80)
    
    sm = SheetManager()
    
    # Get all jobs
    jobs = sm.get_all_jobs(tab="registry")
    
    print(f"\nTotal jobs analyzed: {len(jobs)}")
    
    # Analyze by source
    print("\n" + "="*80)
    print("ANALYSIS BY SOURCE:")
    print("="*80)
    
    sources = {}
    for job in jobs:
        source = job.get('Source', 'Unknown')
        has_url = bool(job.get('ApplyURL', '').strip() and job.get('ApplyURL') != 'Unknown')
        
        if source not in sources:
            sources[source] = {'total': 0, 'with_url': 0, 'without_url': 0}
        
        sources[source]['total'] += 1
        if has_url:
            sources[source]['with_url'] += 1
        else:
            sources[source]['without_url'] += 1
    
    for source, stats in sorted(sources.items()):
        pct_with_url = (stats['with_url'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"\n{source}:")
        print(f"  Total: {stats['total']}")
        print(f"  With URL: {stats['with_url']} ({pct_with_url:.1f}%)")
        print(f"  Without URL: {stats['without_url']}")
    
    # Analyze jobs with URLs
    print("\n" + "="*80)
    print("JOBS WITH URLS (detailed):")
    print("="*80)
    
    jobs_with_urls = [j for j in jobs if j.get('ApplyURL', '').strip() and j.get('ApplyURL') != 'Unknown']
    
    for i, job in enumerate(jobs_with_urls, 1):
        company = job.get('Company', 'Unknown')
        role = job.get('Role', 'Unknown')
        source = job.get('Source', 'Unknown')
        url = job.get('ApplyURL', 'N/A')
        
        print(f"\n{i}. {company} - {role}")
        print(f"   Source: {source}")
        print(f"   URL: {url}")
        print(f"   URL Length: {len(url)} chars")
    
    # Analyze jobs WITHOUT URLs
    print("\n" + "="*80)
    print("JOBS WITHOUT URLS (sample):")
    print("="*80)
    
    jobs_without_urls = [j for j in jobs if not j.get('ApplyURL', '').strip() or j.get('ApplyURL') == 'Unknown']
    
    for i, job in enumerate(jobs_without_urls[:5], 1):  # First 5 only
        company = job.get('Company', 'Unknown')
        role = job.get('Role', 'Unknown')
        source = job.get('Source', 'Unknown')
        created = job.get('CreatedAt', 'Unknown')
        
        print(f"\n{i}. {company} - {role}")
        print(f"   Source: {source}")
        print(f"   Created: {created}")
        print(f"   Has Company: {company != 'Unknown' and company != 'Registry'}")
        print(f"   Has Role: {role != 'Unknown' and role != 'OK'}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY & RECOMMENDATIONS:")
    print("="*80)
    
    total_with = len(jobs_with_urls)
    total_without = len(jobs_without_urls)
    pct_with = (total_with / len(jobs) * 100) if jobs else 0
    
    print(f"\nWith URLs: {total_with} ({pct_with:.1f}%)")
    print(f"Without URLs: {total_without} ({100-pct_with:.1f}%)")
    
    print("\nPOSSIBLE CAUSES:")
    print("  1. Email processor (gmail_jobs_monitor_v2.py) not extracting URLs")
    print("  2. Emails don't contain clickable URLs (plain text)")
    print("  3. URL extraction regex is too strict")
    print("  4. Bulletin processor not extracting individual URLs")
    
    print("\nRECOMMENDED ACTIONS:")
    print("  1. Test email processor with 1 sample email")
    print("  2. Check gmail_jobs_monitor_v2.py URL extraction code")
    print("  3. Verify email format (HTML vs plain text)")
    print("  4. Re-process emails with improved URL extraction")
    
    print("\nNEXT STEPS:")
    print("  1. py -c \"from core.automation import gmail_jobs_monitor_v2\"")
    print("  2. Review URL extraction method in that file")
    print("  3. Test with sample email")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
