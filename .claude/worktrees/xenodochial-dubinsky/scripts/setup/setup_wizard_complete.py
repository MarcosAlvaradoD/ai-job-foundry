#!/usr/bin/env python3
"""
AI JOB FOUNDRY - COMPLETE SETUP WIZARD FOR EXE DISTRIBUTION
Asks for EVERYTHING: CV, API keys, LM Studio, Gmail, Playwright, etc.
"""
import sys
from pathlib import Path
import json
import os
import subprocess

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


def print_header():
    """Print wizard header"""
    print("\n" + "="*70)
    print(f"{CYAN}{BOLD}🚀 AI JOB FOUNDRY - COMPLETE SETUP WIZARD{RESET}")
    print("="*70)
    print(f"{YELLOW}This wizard will configure EVERYTHING you need.{RESET}")
    print("="*70 + "\n")


def get_input(prompt, default=None, required=True):
    """Get user input with validation"""
    while True:
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        value = input(full_prompt).strip()
        
        if not value and default:
            return default
        elif not value and not required:
            return ""
        elif not value and required:
            print(f"{RED}This field is required. Please enter a value.{RESET}")
            continue
        else:
            return value


def get_multiline_input(prompt):
    """Get multiline input"""
    print(f"\n{prompt}")
    print(f"{YELLOW}(Enter a blank line to finish){RESET}")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)


def yes_no(prompt, default="yes"):
    """Ask yes/no question"""
    while True:
        answer = get_input(f"{prompt} (yes/no)", default=default).lower()
        if answer in ['yes', 'y']:
            return True
        elif answer in ['no', 'n']:
            return False
        else:
            print(f"{RED}Please answer 'yes' or 'no'{RESET}")


# ============================================================================
# STEP 1: USER PROFILE
# ============================================================================
def setup_user_profile():
    """Setup user profile"""
    print(f"\n{BOLD}👤 STEP 1/7: USER PROFILE{RESET}")
    print("-" * 70 + "\n")
    
    profile = {
        "full_name": get_input("Full name"),
        "location": get_input("Location (e.g., Guadalajara, Mexico)"),
        "timezone": get_input("Timezone", default="CST"),
    }
    
    return profile


# ============================================================================
# STEP 2: PROFESSIONAL INFO
# ============================================================================
def setup_professional_info():
    """Setup professional information"""
    print(f"\n{BOLD}💼 STEP 2/7: PROFESSIONAL INFORMATION{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{CYAN}What roles are you looking for?{RESET}")
    print("Examples: Project Manager, Product Owner, Business Analyst")
    roles_input = get_input("Target roles (comma-separated)")
    roles = [r.strip() for r in roles_input.split(",")]
    
    years_exp = get_input("Years of professional experience", default="5")
    
    print(f"\n{CYAN}Key skills/technologies (comma-separated){RESET}")
    skills_input = get_input("Skills")
    skills = [s.strip() for s in skills_input.split(",")]
    
    print(f"\n{CYAN}Industries (comma-separated, optional){RESET}")
    industries_input = get_input("Industries", required=False)
    industries = [i.strip() for i in industries_input.split(",")] if industries_input else []
    
    return {
        "target_roles": roles,
        "years_experience": int(years_exp),
        "key_skills": skills,
        "industries": industries
    }


# ============================================================================
# STEP 3: JOB PREFERENCES
# ============================================================================
def setup_job_preferences():
    """Setup job search preferences"""
    print(f"\n{BOLD}🎯 STEP 3/7: JOB PREFERENCES{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{CYAN}Work location preference:{RESET}")
    print("1. Remote only")
    print("2. Hybrid")
    print("3. On-site")
    print("4. Any")
    work_pref = get_input("Choose (1-4)", default="1")
    
    work_prefs = {"1": "Remote", "2": "Hybrid", "3": "On-site", "4": "Any"}
    
    min_salary = get_input("Minimum salary USD (optional)", required=False)
    
    print(f"\n{CYAN}Minimum FIT score for auto-apply (0-10){RESET}")
    print("Recommended: 7 for high-quality matches")
    fit_threshold = get_input("FIT threshold", default="7")
    
    return {
        "work_location": work_prefs.get(work_pref, "Remote"),
        "minimum_salary": int(min_salary) if min_salary else None,
        "fit_score_threshold": int(fit_threshold)
    }


# ============================================================================
# STEP 4: CV/RESUME
# ============================================================================
def setup_cv_description():
    """Setup CV description"""
    print(f"\n{BOLD}📄 STEP 4/7: CV/RESUME DESCRIPTION{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{YELLOW}AI will use this to analyze job matches.{RESET}")
    print(f"{YELLOW}Include experience, achievements, and strengths.{RESET}\n")
    
    cv_description = get_multiline_input("Enter your professional summary:")
    
    return cv_description


# ============================================================================
# STEP 5: API KEYS & SERVICES
# ============================================================================
def setup_api_keys():
    """Setup API keys and services"""
    print(f"\n{BOLD}🔑 STEP 5/7: API KEYS & SERVICES{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{CYAN}Google Sheets ID{RESET}")
    print("This is where your jobs will be tracked.")
    print("Format: 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg")
    sheets_id = get_input("Google Sheets ID", required=False)
    
    print(f"\n{CYAN}Gemini API Key (optional){RESET}")
    print("Used for AI analysis when LM Studio is offline.")
    print("Get it from: https://makersuite.google.com/app/apikey")
    gemini_key = get_input("Gemini API key", required=False)
    
    return {
        "google_sheets_id": sheets_id if sheets_id else None,
        "gemini_api_key": gemini_key if gemini_key else None
    }


# ============================================================================
# STEP 6: LM STUDIO CONFIGURATION
# ============================================================================
def setup_lm_studio():
    """Setup LM Studio configuration"""
    print(f"\n{BOLD}🤖 STEP 6/7: LM STUDIO CONFIGURATION{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{YELLOW}LM Studio is for local AI processing.{RESET}")
    
    has_lm_studio = yes_no("Do you have LM Studio installed?", default="yes")
    
    if has_lm_studio:
        print(f"\n{CYAN}LM Studio IP Address{RESET}")
        print("Usually: 127.0.0.1 or localhost")
        lm_ip = get_input("LM Studio IP", default="127.0.0.1")
        
        print(f"\n{CYAN}LM Studio Port{RESET}")
        lm_port = get_input("LM Studio Port", default="11434")
        
        return {
            "enabled": True,
            "ip": lm_ip,
            "port": lm_port,
            "url": f"http://{lm_ip}:{lm_port}"
        }
    else:
        print(f"\n{YELLOW}No problem! System will use Gemini API.{RESET}")
        return {"enabled": False}


# ============================================================================
# STEP 7: DEPENDENCIES CHECK
# ============================================================================
def check_dependencies():
    """Check if dependencies are installed"""
    print(f"\n{BOLD}📦 STEP 7/7: DEPENDENCIES CHECK{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{CYAN}Checking Python packages...{RESET}")
    
    required_packages = [
        'flask', 'playwright', 'gspread', 'google-auth',
        'python-dotenv', 'requests', 'beautifulsoup4', 'colorama'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n{YELLOW}Missing packages detected.{RESET}")
        install = yes_no("Install missing packages now?", default="yes")
        
        if install:
            print(f"\n{CYAN}Installing packages...{RESET}")
            for package in missing:
                subprocess.run([sys.executable, "-m", "pip", "install", package])
            print(f"\n{GREEN}✅ Packages installed{RESET}")
        else:
            print(f"\n{YELLOW}⚠️  Some features may not work without these packages.{RESET}")
    
    # Check Playwright browsers
    print(f"\n{CYAN}Checking Playwright browsers...{RESET}")
    if yes_no("Install Playwright Chromium browser?", default="yes"):
        print(f"{CYAN}Installing...{RESET}")
        subprocess.run(["playwright", "install", "chromium"])
        print(f"{GREEN}✅ Playwright browser installed{RESET}")


# ============================================================================
# CREATE PROFILE FILES
# ============================================================================
def create_profile_files(profile_name, config):
    """Create all profile files"""
    # Create profiles directory
    profiles_dir = Path("data/profiles")
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    user_dir = profiles_dir / profile_name
    user_dir.mkdir(exist_ok=True)
    
    # Save config
    config_file = user_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Save CV
    cv_file = user_dir / "cv_description.txt"
    with open(cv_file, 'w', encoding='utf-8') as f:
        f.write(config['cv_description'])
    
    # Create .env file
    env_file = user_dir / ".env"
    with open(env_file, 'w') as f:
        if config['api_keys'].get('google_sheets_id'):
            f.write(f"GOOGLE_SHEETS_ID={config['api_keys']['google_sheets_id']}\n")
        else:
            f.write("GOOGLE_SHEETS_ID=\n")
        
        if config['api_keys'].get('gemini_api_key'):
            f.write(f"GEMINI_API_KEY={config['api_keys']['gemini_api_key']}\n")
        
        if config['lm_studio']['enabled']:
            f.write(f"LM_STUDIO_URL={config['lm_studio']['url']}\n")
    
    # Set active profile
    active_file = Path("data/active_profile.txt")
    with open(active_file, 'w') as f:
        f.write(profile_name)
    
    return user_dir


# ============================================================================
# PRINT SUMMARY
# ============================================================================
def print_summary(profile_name, config, profile_dir):
    """Print setup summary"""
    print("\n" + "="*70)
    print(f"{GREEN}{BOLD}✅ SETUP COMPLETE!{RESET}")
    print("="*70)
    print(f"\n{CYAN}Profile:{RESET} {profile_name}")
    print(f"{CYAN}Location:{RESET} {profile_dir}")
    print(f"{CYAN}User:{RESET} {config['user_profile']['full_name']}")
    print(f"{CYAN}Roles:{RESET} {', '.join(config['professional_info']['target_roles'])}")
    
    if config['api_keys'].get('google_sheets_id'):
        print(f"{CYAN}Google Sheets:{RESET} Configured ✅")
    else:
        print(f"{YELLOW}Google Sheets:{RESET} Not configured (add to .env later)")
    
    if config['lm_studio']['enabled']:
        print(f"{CYAN}LM Studio:{RESET} {config['lm_studio']['url']}")
    else:
        print(f"{YELLOW}LM Studio:{RESET} Disabled (using Gemini)")
    
    print(f"\n{YELLOW}Next steps:{RESET}")
    print("1. Setup OAuth for Gmail/Sheets:")
    print("   Run: py setup_oauth_helper.py")
    print("\n2. Start the application:")
    print("   Run: START_UNIFIED_APP.bat")
    print("\n3. (Optional) Configure LM Studio:")
    print("   Download: https://lmstudio.ai")
    print("   Load model: Llama-3-Groq-70B-Tool-Use Q4_K_M")
    print("\n" + "="*70 + "\n")


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Main wizard"""
    print_header()
    
    # Get profile name
    print(f"{CYAN}Choose a profile name (e.g., 'marcos', 'john'){RESET}")
    profile_name = get_input("Profile name").lower().replace(" ", "_")
    
    # Check if exists
    profile_dir = Path(f"data/profiles/{profile_name}")
    if profile_dir.exists():
        overwrite = yes_no(f"Profile '{profile_name}' exists. Overwrite?", default="no")
        if not overwrite:
            print(f"\n{YELLOW}Setup cancelled.{RESET}\n")
            return
    
    # Collect info
    config = {
        "user_profile": setup_user_profile(),
        "professional_info": setup_professional_info(),
        "job_preferences": setup_job_preferences(),
        "cv_description": setup_cv_description(),
        "api_keys": setup_api_keys(),
        "lm_studio": setup_lm_studio()
    }
    
    # Check dependencies
    check_dependencies()
    
    # Create files
    user_dir = create_profile_files(profile_name, config)
    
    # Print summary
    print_summary(profile_name, config, user_dir)
    
    print(f"{GREEN}Profile '{profile_name}' is now active!{RESET}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup cancelled.{RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
