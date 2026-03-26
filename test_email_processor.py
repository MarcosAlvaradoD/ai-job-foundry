#!/usr/bin/env python3
"""
Test Email Bulletin Processor
Quick test to verify email detection and processing
"""

import sys
from pathlib import Path

# Add project root to path BEFORE any other imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Test bulletin processor with current inbox"""
    
    print("\n" + "="*70)
    print("🧪 TESTING EMAIL BULLETIN PROCESSOR")
    print("="*70)
    print("Testing improved email detection...")
    print("="*70 + "\n")
    
    try:
        # Import AFTER adding to path and setting up encoding
        from core.automation.job_bulletin_processor import JobBulletinProcessor
        
        processor = JobBulletinProcessor()
        
        # Process max 10 emails for testing
        processor.process_bulletins(max_emails=10)
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED")
        print("="*70)
        print("\nIf you see 'USER_URLS bulletin' above, the fix worked!")
        print("If you see 'Not a job bulletin' still, we need to debug further.")
        print("\nNext: Run full processing:")
        print("  py control_center.py → Option 4 (Process Bulletins)")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
