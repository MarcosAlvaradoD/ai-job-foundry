#!/usr/bin/env python3
"""
Install BeautifulSoup4 for HTML email parsing
Quick installer script

Usage:
    py install_bs4.py
"""
import subprocess
import sys

def main():
    print("\n" + "="*70)
    print("INSTALLING BEAUTIFULSOUP4")
    print("="*70)
    
    print("\n[INFO] Installing beautifulsoup4...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "beautifulsoup4", "--break-system-packages"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[OK] BeautifulSoup4 installed successfully")
            print("\n[NEXT] Run: py test_email_url_fix.py")
        else:
            print(f"[ERROR] Installation failed:")
            print(result.stderr)
            print("\n[TRY] Manual install:")
            print("   pip install beautifulsoup4 --break-system-packages")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[TRY] Manual install:")
        print("   pip install beautifulsoup4 --break-system-packages")
    
    print("="*70)

if __name__ == "__main__":
    main()
