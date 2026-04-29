#!/usr/bin/env python3
"""
AI JOB FOUNDRY - PROFILE SWITCHER
Switch between different user profiles
"""
import sys
from pathlib import Path
import json

# Color support
try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL
except Exception:
    GREEN = CYAN = YELLOW = RED = BOLD = RESET = ''


def get_profiles():
    """Get list of available profiles"""
    profiles_dir = Path("data/profiles")
    if not profiles_dir.exists():
        return []
    
    profiles = []
    for profile_dir in profiles_dir.iterdir():
        if profile_dir.is_dir():
            config_file = profile_dir / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    profiles.append({
                        'name': profile_dir.name,
                        'full_name': config['user_profile']['full_name'],
                        'roles': config['professional_info']['target_roles']
                    })
                except Exception:
                    profiles.append({
                        'name': profile_dir.name,
                        'full_name': 'Unknown',
                        'roles': []
                    })
    
    return profiles


def get_active_profile():
    """Get currently active profile"""
    active_file = Path("data/active_profile.txt")
    if not active_file.exists():
        return None
    
    with open(active_file, 'r') as f:
        return f.read().strip()


def set_active_profile(profile_name):
    """Set active profile"""
    active_file = Path("data/active_profile.txt")
    active_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(active_file, 'w') as f:
        f.write(profile_name)


def main():
    """Main profile switcher"""
    print("\n" + "="*70)
    print(f"{CYAN}{BOLD}🔄 AI JOB FOUNDRY - PROFILE SWITCHER{RESET}")
    print("="*70 + "\n")
    
    # Get profiles
    profiles = get_profiles()
    
    if not profiles:
        print(f"{YELLOW}No profiles found.{RESET}")
        print(f"{CYAN}Run setup wizard to create a profile:{RESET}")
        print("  py setup_wizard.py\n")
        return
    
    # Get active profile
    active = get_active_profile()
    
    # Display profiles
    print(f"{CYAN}Available profiles:{RESET}\n")
    for i, profile in enumerate(profiles, 1):
        is_active = " [ACTIVE]" if profile['name'] == active else ""
        roles_str = ", ".join(profile['roles'][:2])
        if len(profile['roles']) > 2:
            roles_str += f", +{len(profile['roles']) - 2} more"
        
        print(f"  {i}. {GREEN if is_active else ''}{profile['full_name']}{RESET}{is_active}")
        print(f"     Profile: {profile['name']}")
        print(f"     Roles: {roles_str}")
        print()
    
    # Get choice
    print(f"{CYAN}Select profile number (or 0 to cancel):{RESET}")
    try:
        choice = int(input("> ").strip())
    except ValueError:
        print(f"{RED}Invalid input{RESET}\n")
        return
    
    if choice == 0:
        print(f"{YELLOW}Cancelled{RESET}\n")
        return
    
    if choice < 1 or choice > len(profiles):
        print(f"{RED}Invalid profile number{RESET}\n")
        return
    
    # Switch profile
    selected = profiles[choice - 1]
    set_active_profile(selected['name'])
    
    print(f"\n{GREEN}✅ Switched to profile: {selected['full_name']}{RESET}")
    print(f"{YELLOW}Restart the application for changes to take effect.{RESET}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Cancelled{RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}\n")
        sys.exit(1)
