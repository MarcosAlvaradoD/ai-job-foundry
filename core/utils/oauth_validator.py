#!/usr/bin/env python3
"""
OAuth Token Validator
Validates and auto-refreshes Google OAuth tokens before API operations

This module provides centralized OAuth token validation for all components
that interact with Gmail API and Google Sheets API.

Usage:
    from core.utils.oauth_validator import ensure_valid_oauth_token
    
    # Call this BEFORE any Gmail/Sheets operation
    if not ensure_valid_oauth_token():
        print("OAuth validation failed")
        sys.exit(1)
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Optional

def get_token_path() -> Path:
    """Get path to OAuth token file"""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "data" / "credentials" / "token.json"

def get_credentials_path() -> Path:
    """Get path to OAuth credentials file"""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "data" / "credentials" / "credentials.json"

def get_reauth_script_path() -> Path:
    """Get path to re-authentication script"""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "scripts" / "oauth" / "reauthenticate_gmail_v2.py"

def check_token_validity() -> Tuple[bool, Optional[str]]:
    """
    Check if OAuth token exists and is valid
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    token_path = get_token_path()
    
    # Check if token file exists
    if not token_path.exists():
        return False, f"Token file not found at {token_path}"
    
    try:
        # Load token data
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        
        # Check if expiry field exists
        if 'expiry' not in token_data:
            return False, "Token missing expiry field"
        
        # Parse expiry datetime
        expiry_str = token_data['expiry']
        
        # Handle different datetime formats
        try:
            # Try ISO format with timezone
            if 'Z' in expiry_str:
                expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            elif '+' in expiry_str or expiry_str.count('-') > 2:
                expiry = datetime.fromisoformat(expiry_str)
            else:
                # Fallback: parse as naive datetime and make it timezone-aware
                expiry = datetime.fromisoformat(expiry_str).replace(tzinfo=timezone.utc)
        except ValueError as e:
            return False, f"Invalid expiry datetime format: {expiry_str} ({e})"
        
        # Get current time (timezone-aware)
        now = datetime.now(timezone.utc)
        
        # Check if token is expired (with 5 min buffer)
        if now >= expiry:
            return False, f"Token expired at {expiry}"
        
        # Check if token expires soon (within 5 minutes)
        time_until_expiry = (expiry - now).total_seconds()
        if time_until_expiry < 300:  # 5 minutes
            return False, f"Token expires in {int(time_until_expiry)} seconds"
        
        return True, None
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in token file: {e}"
    except Exception as e:
        return False, f"Error checking token: {e}"

def run_reauthentication() -> bool:
    """
    Execute re-authentication script to refresh OAuth token
    
    Returns:
        bool: True if re-authentication succeeded, False otherwise
    """
    reauth_script = get_reauth_script_path()
    
    if not reauth_script.exists():
        print(f"[ERROR] Re-authentication script not found: {reauth_script}")
        return False
    
    print(f"\n{'='*70}")
    print("🔐 OAUTH TOKEN RE-AUTHENTICATION")
    print(f"{'='*70}")
    print("Executing re-authentication script...")
    print(f"Script: {reauth_script}")
    print(f"{'='*70}\n")
    
    try:
        # Run re-authentication script
        result = subprocess.run(
            [sys.executable, str(reauth_script)],
            cwd=reauth_script.parent.parent.parent,  # Project root
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        # Check if successful
        if result.returncode == 0:
            print(f"\n{'='*70}")
            print("✅ RE-AUTHENTICATION SUCCESSFUL")
            print(f"{'='*70}\n")
            return True
        else:
            print(f"\n{'='*70}")
            print("❌ RE-AUTHENTICATION FAILED")
            print(f"{'='*70}")
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            print(f"{'='*70}\n")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n❌ Re-authentication timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"\n❌ Re-authentication error: {e}")
        return False

def ensure_valid_oauth_token(auto_refresh: bool = True) -> bool:
    """
    Ensure OAuth token is valid, auto-refresh if needed
    
    This is the main function to call before any Gmail/Sheets operation.
    
    Args:
        auto_refresh: If True, automatically run re-authentication if token is invalid
    
    Returns:
        bool: True if token is valid (or was successfully refreshed), False otherwise
    
    Example:
        from core.utils.oauth_validator import ensure_valid_oauth_token
        
        if not ensure_valid_oauth_token():
            print("OAuth validation failed")
            sys.exit(1)
        
        # Now safe to use Gmail/Sheets API
        from core.sheets.sheet_manager import SheetManager
        sheet_manager = SheetManager()
    """
    print(f"\n{'='*70}")
    print("🔍 OAUTH TOKEN VALIDATION")
    print(f"{'='*70}")
    
    # Check credentials.json exists
    creds_path = get_credentials_path()
    if not creds_path.exists():
        print(f"❌ ERROR: credentials.json not found at {creds_path}")
        print(f"\nSetup instructions:")
        print(f"1. Visit: https://console.cloud.google.com/")
        print(f"2. Create OAuth 2.0 credentials")
        print(f"3. Download and save as: {creds_path}")
        print(f"{'='*70}\n")
        return False
    
    # Check token validity
    is_valid, error_msg = check_token_validity()
    
    if is_valid:
        print(f"✅ OAuth token is VALID")
        print(f"{'='*70}\n")
        return True
    
    # Token is invalid
    print(f"⚠️  OAuth token is INVALID")
    print(f"Reason: {error_msg}")
    print(f"{'='*70}")
    
    if not auto_refresh:
        print(f"Auto-refresh disabled. Manual re-authentication required.")
        print(f"Run: py scripts/oauth/reauthenticate_gmail_v2.py")
        print(f"{'='*70}\n")
        return False
    
    # Auto-refresh
    print(f"🔄 Auto-refresh enabled. Running re-authentication...")
    print(f"{'='*70}\n")
    
    success = run_reauthentication()
    
    if success:
        # Verify token is now valid
        is_valid, error_msg = check_token_validity()
        if is_valid:
            print(f"✅ Token successfully refreshed and validated")
            return True
        else:
            print(f"❌ Token refresh succeeded but validation failed: {error_msg}")
            return False
    else:
        print(f"❌ Token refresh failed")
        return False

def main():
    """
    Standalone script to validate and refresh OAuth token
    
    Usage:
        py core/utils/oauth_validator.py
    """
    print(f"\n{'='*70}")
    print("OAUTH TOKEN VALIDATOR - Standalone Execution")
    print(f"{'='*70}\n")
    
    success = ensure_valid_oauth_token(auto_refresh=True)
    
    if success:
        print(f"\n{'='*70}")
        print("✅ SUCCESS: OAuth token is valid and ready to use")
        print(f"{'='*70}")
        print(f"You can now run:")
        print(f"  - py run_daily_pipeline.py --all")
        print(f"  - py control_center.py")
        print(f"  - Any script that uses Gmail/Sheets API")
        print(f"{'='*70}\n")
        sys.exit(0)
    else:
        print(f"\n{'='*70}")
        print("❌ FAILURE: OAuth token validation failed")
        print(f"{'='*70}")
        print(f"Manual steps required:")
        print(f"  1. py scripts/oauth/reauthenticate_gmail_v2.py")
        print(f"  2. Accept all OAuth permissions in browser")
        print(f"  3. Run this script again to verify")
        print(f"{'='*70}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
