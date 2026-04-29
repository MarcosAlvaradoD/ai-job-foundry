#!/usr/bin/env python3
"""
AI JOB FOUNDRY - OAuth Token Checker
Detecta si el token está expirado y ofrece arreglarlo
"""
import os
import json
from datetime import datetime
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except Exception:
    GREEN = RED = YELLOW = CYAN = RESET = ''

TOKEN_FILE = Path("data/credentials/token.json")
CREDENTIALS_FILE = Path("data/credentials/credentials.json")

def check_token_status():
    """Check OAuth token status"""
    print(f"\n{CYAN}🔐 Checking OAuth Token Status{RESET}\n")
    print("=" * 70)
    
    # Check credentials.json exists
    if not CREDENTIALS_FILE.exists():
        print(f"{RED}❌ credentials.json NOT FOUND{RESET}")
        print(f"\n{YELLOW}Location:{RESET} {CREDENTIALS_FILE}")
        print(f"\n{YELLOW}Solution:{RESET}")
        print("1. Go to Google Cloud Console")
        print("2. Download OAuth 2.0 credentials")
        print("3. Save as data/credentials/credentials.json")
        return False
    
    print(f"{GREEN}✅ credentials.json{RESET} - OK")
    
    # Check token.json exists
    if not TOKEN_FILE.exists():
        print(f"{RED}❌ token.json NOT FOUND{RESET}")
        print(f"\n{YELLOW}First time setup required{RESET}")
        print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat")
        return False
    
    print(f"{GREEN}✅ token.json{RESET} - Exists")
    
    # Read token
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
    except Exception as e:
        print(f"{RED}❌ token.json CORRUPTED{RESET}")
        print(f"\n{YELLOW}Error:{RESET} {e}")
        print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat")
        return False
    
    # Check required fields
    required_fields = ['token', 'refresh_token', 'token_uri', 'client_id']
    missing = [f for f in required_fields if f not in token_data]
    
    if missing:
        print(f"{RED}❌ token.json INCOMPLETE{RESET}")
        print(f"\n{YELLOW}Missing fields:{RESET} {', '.join(missing)}")
        print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat")
        return False
    
    print(f"{GREEN}✅ token.json{RESET} - Structure OK")
    
    # Check expiry
    if 'expiry' in token_data:
        try:
            expiry = datetime.fromisoformat(token_data['expiry'].replace('Z', '+00:00'))
            now = datetime.now(expiry.tzinfo)
            
            if now > expiry:
                print(f"{RED}❌ token.json EXPIRED{RESET}")
                print(f"\n{YELLOW}Expired:{RESET} {expiry.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{YELLOW}Now:{RESET}     {now.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat")
                return False
            else:
                time_left = expiry - now
                hours_left = int(time_left.total_seconds() / 3600)
                print(f"{GREEN}✅ token.json{RESET} - Valid ({hours_left}h remaining)")
        except Exception as e:
            print(f"{YELLOW}⚠️  Cannot parse expiry date{RESET}")
            print(f"   Will try to use anyway")
    
    # Check scopes
    if 'scopes' in token_data:
        scopes = token_data['scopes']
        required_scopes = [
            'spreadsheets',
            'gmail.readonly',
            'gmail.modify'
        ]
        
        has_all = all(any(req in scope for scope in scopes) for req in required_scopes)
        
        if has_all:
            print(f"{GREEN}✅ Scopes{RESET} - Complete")
        else:
            print(f"{YELLOW}⚠️  Scopes{RESET} - Some missing")
            print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat to update")
    
    print("=" * 70)
    print(f"\n{GREEN}🎉 OAuth Token is READY!{RESET}\n")
    return True


def test_token():
    """Test if token actually works"""
    print(f"\n{CYAN}🧪 Testing Token with Google APIs{RESET}\n")
    print("=" * 70)
    
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        # Load credentials
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
        
        # Try to access Sheets
        print("Testing Google Sheets API... ", end='')
        try:
            service = build('sheets', 'v4', credentials=creds)
            # Just build service, don't actually call it
            print(f"{GREEN}OK{RESET}")
        except HttpError as e:
            if 'invalid_grant' in str(e):
                print(f"{RED}EXPIRED{RESET}")
                print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat")
                return False
            else:
                print(f"{RED}ERROR: {e}{RESET}")
                return False
        
        # Try to access Gmail
        print("Testing Gmail API... ", end='')
        try:
            service = build('gmail', 'v1', credentials=creds)
            print(f"{GREEN}OK{RESET}")
        except HttpError as e:
            if 'invalid_grant' in str(e):
                print(f"{RED}EXPIRED{RESET}")
                print(f"\n{YELLOW}Run:{RESET} FIX_OAUTH_TOKEN.bat")
                return False
            else:
                print(f"{RED}ERROR: {e}{RESET}")
                return False
        
        print("=" * 70)
        print(f"\n{GREEN}🎉 Token works perfectly!{RESET}\n")
        return True
        
    except ImportError:
        print(f"{YELLOW}⚠️  Cannot test - missing google packages{RESET}")
        print("\nInstall: pip install google-auth google-auth-oauthlib google-api-python-client")
        return None
    except Exception as e:
        print(f"{RED}ERROR: {e}{RESET}")
        return False


def main():
    """Main check"""
    print("\n" + "=" * 70)
    print(f"{CYAN}🔐 AI JOB FOUNDRY - OAUTH TOKEN CHECKER{RESET}")
    print("=" * 70)
    
    # Check token file
    status_ok = check_token_status()
    
    if not status_ok:
        print(f"\n{RED}⚠️  OAuth setup required{RESET}")
        print(f"\n{CYAN}Run:{RESET} FIX_OAUTH_TOKEN.bat")
        print()
        return
    
    # Test token
    test_result = test_token()
    
    if test_result is False:
        print(f"\n{RED}⚠️  Token expired or invalid{RESET}")
        print(f"\n{CYAN}Run:{RESET} FIX_OAUTH_TOKEN.bat")
        print()
    elif test_result is None:
        print(f"\n{YELLOW}⚠️  Cannot test, but token looks OK{RESET}")
        print()
    else:
        print(f"{GREEN}✅ Everything ready!{RESET}")
        print(f"\n{CYAN}You can now run:{RESET} START_UNIFIED_APP.bat")
        print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Cancelled{RESET}\n")
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}\n")
        import traceback
        traceback.print_exc()
