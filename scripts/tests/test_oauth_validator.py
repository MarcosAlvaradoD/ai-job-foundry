#!/usr/bin/env python3
"""
Test script for OAuth Validator module

Tests the oauth_validator module to ensure it works correctly
before integrating into the main pipeline.

Usage:
    py scripts/tests/test_oauth_validator.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.oauth_validator import (
    ensure_valid_oauth_token,
    check_token_validity,
    get_token_path,
    get_credentials_path
)

def main():
    print("\n" + "="*70)
    print("🧪 OAUTH VALIDATOR TEST SUITE")
    print("="*70 + "\n")
    
    # Test 1: Check paths
    print("Test 1: Checking file paths...")
    token_path = get_token_path()
    creds_path = get_credentials_path()
    
    print(f"  Token path: {token_path}")
    print(f"  Token exists: {token_path.exists()}")
    print(f"  Credentials path: {creds_path}")
    print(f"  Credentials exists: {creds_path.exists()}")
    print()
    
    # Test 2: Check token validity
    print("Test 2: Checking token validity...")
    is_valid, error_msg = check_token_validity()
    print(f"  Is valid: {is_valid}")
    if not is_valid:
        print(f"  Error: {error_msg}")
    print()
    
    # Test 3: Full validation with auto-refresh
    print("Test 3: Running full validation (with auto-refresh)...")
    success = ensure_valid_oauth_token(auto_refresh=True)
    print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
    print()
    
    # Final result
    print("="*70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("OAuth validator is ready for production use")
    else:
        print("❌ TESTS FAILED")
        print("OAuth validator needs manual intervention")
    print("="*70 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
