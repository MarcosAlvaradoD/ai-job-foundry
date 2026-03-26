"""
Fix Unicode Errors in EXPIRE_LIFECYCLE.py

Replaces all Unicode emojis with ASCII equivalents for Windows PowerShell compatibility.

Usage:
    py scripts\\maintenance\\fix_unicode_expire.py
"""

import re
from pathlib import Path

def fix_unicode_in_file(file_path: Path):
    """Remove Unicode emojis and replace with ASCII."""
    
    print(f"\n🔧 Fixing Unicode in {file_path.name}...")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup original
    backup_path = file_path.with_suffix('.py.unicode_backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✅ Backup created: {backup_path.name}")
    
    # Replace Unicode escapes with ASCII
    replacements = {
        r'\\U0001f5d1\\ufe0f': '[DELETE]',  # 🗑️
        r'\\u2705': '[OK]',                 # ✅
        r'\\u274c': '[ERROR]',              # ❌
        r'\\u26a0\\ufe0f': '[WARNING]',     # ⚠️
        r'\\U0001f4cb': '[INFO]',           # 📋
        r'\\U0001f4ca': '[STATS]',          # 📊
        r'\\u2139\\ufe0f': '[INFO]',        # ℹ️
        r'\\U0001f4c5': '[DATE]',           # 📅
        r'\\U0001f4dd': '[NOTE]',           # 📝
    }
    
    # Also replace direct Unicode characters
    direct_replacements = {
        '🗑️': '[DELETE]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '📋': '[INFO]',
        '📊': '[STATS]',
        'ℹ️': '[INFO]',
        '📅': '[DATE]',
        '📝': '[NOTE]',
    }
    
    # Apply replacements
    modified = content
    for old, new in replacements.items():
        if old in modified:
            modified = re.sub(old, new, modified)
            print(f"   🔄 Replaced: {old} → {new}")
    
    for old, new in direct_replacements.items():
        if old in modified:
            modified = modified.replace(old, new)
            print(f"   🔄 Replaced: {old} → {new}")
    
    # Write fixed file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified)
    
    print(f"   ✅ Fixed file written")
    
    if content == modified:
        print(f"   ℹ️  No changes needed (no Unicode emojis found)")
        return False
    else:
        print(f"   🎉 Unicode fixed successfully!")
        return True


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    expire_script = project_root / "scripts" / "verifiers" / "EXPIRE_LIFECYCLE.py"
    
    if not expire_script.exists():
        print(f"❌ ERROR: File not found: {expire_script}")
        print(f"   Expected location: {expire_script}")
        exit(1)
    
    print("\n" + "=" * 80)
    print("🔧 FIX UNICODE ERRORS - EXPIRE_LIFECYCLE")
    print("=" * 80)
    
    success = fix_unicode_in_file(expire_script)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ FIX COMPLETED")
        print("\nNext steps:")
        print("  1. Run: .\\DIAGNOSTICO_COMPLETO.ps1")
        print("  2. Verify: Step 3 should now show '[DELETE] DELETING EXPIRED JOBS'")
        print("  3. Run: .\\START_CONTROL_CENTER.bat")
        print("  4. Select: Option 1 (Full Pipeline)")
    else:
        print("ℹ️  NO CHANGES NEEDED")
    print("=" * 80)
