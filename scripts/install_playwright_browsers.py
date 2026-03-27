"""
Install Playwright Browsers
Installs Chromium for auto-apply functionality

Author: Marcos Alberto Alvarado
Date: 2026-01-27
"""

import subprocess
import sys

print("🔧 Installing Playwright Browsers")
print("="*60)
print("\nThis will install Chromium for browser automation")
print("Size: ~150MB download\n")

response = input("Continue? (y/n): ").strip().lower()

if response != 'y':
    print("❌ Installation cancelled")
    sys.exit(0)

print("\n📥 Installing Playwright browsers...")
print("This may take a few minutes...\n")

try:
    # Install playwright browsers
    result = subprocess.run(
        ['playwright', 'install', 'chromium'],
        check=True,
        capture_output=False
    )
    
    print("\n✅ Playwright browsers installed successfully!")
    print("\n💡 You can now run:")
    print("   py control_center.py")
    print("   Select option 12a (DRY RUN)\n")
    
except subprocess.CalledProcessError as e:
    print(f"\n❌ Installation failed: {e}")
    print("\n💡 Try manual install:")
    print("   playwright install chromium")
    sys.exit(1)
    
except FileNotFoundError:
    print("\n❌ Playwright command not found")
    print("\n💡 Install Playwright first:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)
