#!/usr/bin/env python3
"""
Test LinkedIn Notifications Scraper
Quick test to extract jobs from LinkedIn recommendations
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.ingestion.linkedin_notifications_scraper import LinkedInNotificationsScraper


async def main():
    print("\n" + "="*70)
    print("🧪 TESTING LINKEDIN NOTIFICATIONS SCRAPER")
    print("="*70 + "\n")
    
    scraper = LinkedInNotificationsScraper()
    await scraper.run()
    
    print("\n✅ Test complete!")
    print("\nNext steps:")
    print("1. Check Google Sheets (LinkedIn tab) for new jobs")
    print("2. Run FIT score calculator:")
    print("   py scripts\\maintenance\\calculate_all_fit_scores_v2.py")
    print("3. Run auto-apply:")
    print("   py core\\automation\\auto_apply_linkedin.py --dry-run")


if __name__ == '__main__':
    asyncio.run(main())
