"""
Test LinkedIn Auto-Apply V3 - WITH AUTO-LOGIN
Quick test script to verify auto-login functionality
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.automation.linkedin_auto_apply import LinkedInAutoApplyV3

def main():
    print("\n" + "="*70)
    print("LINKEDIN AUTO-APPLY V3 - TEST WITH AUTO-LOGIN")
    print("="*70 + "\n")
    
    auto_apply = LinkedInAutoApplyV3()
    
    # Run dry-run with just 2 applications for testing
    auto_apply.run(
        dry_run=True,      # Safe mode - won't submit
        max_applies=2,     # Just 2 jobs for quick test
        min_score=7        # Only high FIT jobs
    )
    
    print("\n[DONE] Test completed!")
    print("[INFO] Check the output above for any errors")
    print("[INFO] If login worked, you should see cookies saved to data/linkedin_cookies.json")

if __name__ == "__main__":
    main()
