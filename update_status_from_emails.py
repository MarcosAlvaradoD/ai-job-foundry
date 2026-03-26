#!/usr/bin/env python3
"""
Update Status from Emails
Monitors Gmail for interview invitations, rejections, and updates Google Sheets status

Author: Marcos Alberto Alvarado
Date: 2026-02-02
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.automation.gmail_status_updater import GmailStatusUpdater

def main():
    print("\n" + "="*70)
    print("📧 UPDATE STATUS FROM EMAILS")
    print("="*70)
    print("Monitoring Gmail for:")
    print("  • Interview invitations")
    print("  • Job rejections")
    print("  • Application acknowledgments")
    print("="*70 + "\n")
    
    try:
        updater = GmailStatusUpdater()
        updater.process_status_emails()
        
        print("\n" + "="*70)
        print("✅ Status updates completed")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
