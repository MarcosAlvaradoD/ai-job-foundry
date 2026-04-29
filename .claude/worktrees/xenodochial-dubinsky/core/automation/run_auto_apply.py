#!/usr/bin/env python3
"""
AI JOB FOUNDRY - Auto-Apply Runner
Wrapper to launch LinkedIn auto-apply with proper argument handling

Usage:
    py run_auto_apply.py --dry-run    # Test mode (no real applications)
    py run_auto_apply.py --live       # Live mode (real applications)
"""
import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import auto-apply module
from core.automation.auto_apply_linkedin import LinkedInAutoApplier


async def main():
    """Main runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Apply Runner')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - no real applications submitted'
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Live mode - submit real applications'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.live:
        dry_run = False
        print("\n" + "="*70)
        print("⚠️ WARNING: LIVE MODE")
        print("="*70)
        print("Real applications will be submitted to LinkedIn!")
        print("Make sure you are logged into LinkedIn and ready to apply.")
        print("="*70 + "\n")
        
        response = input("Type 'YES' to confirm and continue: ")
        if response.upper() != 'YES':
            print("\n❌ Cancelled - No applications submitted\n")
            return
    else:
        dry_run = True
        print("\n" + "="*70)
        print("🧪 DRY RUN MODE")
        print("="*70)
        print("This is a test run - NO real applications will be submitted")
        print("="*70 + "\n")
    
    # Create and run auto-applier
    applier = LinkedInAutoApplier(dry_run=dry_run)
    await applier.run()
    
    print("\n✅ Auto-apply process completed\n")


if __name__ == '__main__':
    asyncio.run(main())
