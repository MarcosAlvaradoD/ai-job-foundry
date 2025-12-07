#!/usr/bin/env python3
"""
AI JOB FOUNDRY - SETUP WIZARD
Interactive setup for new users

This wizard helps configure:
- User profile (name, roles, experience)
- CV/Resume information
- Job preferences
- API keys (optional)
"""
import sys
from pathlib import Path
import json
import os

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
except:
    GREEN = CYAN = YELLOW = RED = BOLD = RESET = ''


def print_header():
    """Print wizard header"""
    print("\n" + "="*70)
    print(f"{CYAN}{BOLD}🚀 AI JOB FOUNDRY - SETUP WIZARD{RESET}")
    print("="*70)
    print(f"{YELLOW}Welcome! Let's configure your job search assistant.{RESET}")
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


def setup_user_profile():
    """Setup user profile"""
    print(f"\n{BOLD}👤 STEP 1: USER PROFILE{RESET}")
    print("-" * 70 + "\n")
    
    profile = {
        "full_name": get_input("Full name"),
        "location": get_input("Location (e.g., Guadalajara, Mexico)"),
        "timezone": get_input("Timezone", default="CST"),
    }
    
    return profile


def setup_professional_info():
    """Setup professional information"""
    print(f"\n{BOLD}💼 STEP 2: PROFESSIONAL INFORMATION{RESET}")
    print("-" * 70 + "\n")
    
    # Target roles
    print(f"\n{CYAN}What roles are you looking for?{RESET}")
    print("Examples: Project Manager, Product Owner, Business Analyst")
    roles_input = get_input("Target roles (comma-separated)")
    roles = [r.strip() for r in roles_input.split(",")]
    
    # Years of experience
    years_exp = get_input("Years of professional experience", default="5")
    
    # Key skills
    print(f"\n{CYAN}Key skills/technologies (comma-separated){RESET}")
    print("Examples: Python, SQL, Agile, Scrum, Power BI")
    skills_input = get_input("Skills")
    skills = [s.strip() for s in skills_input.split(",")]
    
    # Industries
    print(f"\n{CYAN}Industries you have experience in (comma-separated){RESET}")
    print("Examples: Finance, Healthcare, E-commerce, Manufacturing")
    industries_input = get_input("Industries", required=False)
    industries = [i.strip() for i in industries_input.split(",")] if industries_input else []
    
    return {
        "target_roles": roles,
        "years_experience": int(years_exp),
        "key_skills": skills,
        "industries": industries
    }


def setup_job_preferences():
    """Setup job search preferences"""
    print(f"\n{BOLD}🎯 STEP 3: JOB PREFERENCES{RESET}")
    print("-" * 70 + "\n")
    
    # Remote preference
    print(f"\n{CYAN}Work location preference:{RESET}")
    print("1. Remote only")
    print("2. Hybrid")
    print("3. On-site")
    print("4. Any")
    work_pref = get_input("Choose (1-4)", default="1")
    
    work_prefs = {
        "1": "Remote",
        "2": "Hybrid",
        "3": "On-site",
        "4": "Any"
    }
    
    # Minimum salary (optional)
    min_salary = get_input("Minimum salary (USD, optional)", required=False)
    
    # FIT score threshold
    print(f"\n{CYAN}Minimum FIT score for auto-apply (0-10){RESET}")
    print("Recommended: 7 for high-quality matches")
    fit_threshold = get_input("FIT threshold", default="7")
    
    return {
        "work_location": work_prefs.get(work_pref, "Remote"),
        "minimum_salary": int(min_salary) if min_salary else None,
        "fit_score_threshold": int(fit_threshold)
    }


def setup_cv_description():
    """Setup CV description"""
    print(f"\n{BOLD}📄 STEP 4: CV/RESUME DESCRIPTION{RESET}")
    print("-" * 70 + "\n")
    
    print(f"{YELLOW}This will be used by AI to analyze job matches.{RESET}")
    print(f"{YELLOW}Include your experience, achievements, and strengths.{RESET}\n")
    
    cv_description = get_multiline_input("Enter your professional summary:")
    
    return cv_description


def setup_api_keys():
    """Setup API keys (optional)"""
    print(f"\n{BOLD}🔑 STEP 5: API KEYS (OPTIONAL){RESET}")
    print("-" * 70 + "\n")
    
    print(f"{YELLOW}You can skip this and configure later in .env file{RESET}\n")
    
    # Gemini API
    gemini_key = get_input("Gemini API key (optional, for AI analysis)", required=False)
    
    return {
        "gemini_api_key": gemini_key if gemini_key else None
    }


def create_profile_files(profile_name, config):
    """Create profile files"""
    # Create profiles directory
    profiles_dir = Path("data/profiles")
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    # Create user profile directory
    user_dir = profiles_dir / profile_name
    user_dir.mkdir(exist_ok=True)
    
    # Save user config
    config_file = user_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Save CV description
    cv_file = user_dir / "cv_description.txt"
    with open(cv_file, 'w', encoding='utf-8') as f:
        f.write(config['cv_description'])
    
    # Create .env if API keys provided
    if config['api_keys'].get('gemini_api_key'):
        env_file = user_dir / ".env"
        with open(env_file, 'w') as f:
            f.write(f"GEMINI_API_KEY={config['api_keys']['gemini_api_key']}\n")
            f.write(f"GOOGLE_SHEETS_ID=\n")  # User will need to fill this
    
    # Set as active profile
    active_profile_file = Path("data/active_profile.txt")
    with open(active_profile_file, 'w') as f:
        f.write(profile_name)
    
    return user_dir


def print_summary(profile_name, config, profile_dir):
    """Print setup summary"""
    print("\n" + "="*70)
    print(f"{GREEN}{BOLD}✅ SETUP COMPLETE!{RESET}")
    print("="*70)
    print(f"\n{CYAN}Profile created:{RESET} {profile_name}")
    print(f"{CYAN}Location:{RESET} {profile_dir}")
    print(f"\n{CYAN}User:{RESET} {config['user_profile']['full_name']}")
    print(f"{CYAN}Target roles:{RESET} {', '.join(config['professional_info']['target_roles'])}")
    print(f"{CYAN}FIT threshold:{RESET} {config['job_preferences']['fit_score_threshold']}")
    
    print(f"\n{YELLOW}Next steps:{RESET}")
    print("1. Configure Google Sheets:")
    print(f"   Edit: {profile_dir}/.env")
    print("   Add: GOOGLE_SHEETS_ID=your_sheet_id")
    print("\n2. Setup OAuth:")
    print("   Run: py setup_oauth_helper.py")
    print("\n3. Start the app:")
    print("   Run: START_UNIFIED_APP.bat")
    print("\n" + "="*70 + "\n")


def main():
    """Main setup wizard"""
    print_header()
    
    # Get profile name
    print(f"{CYAN}Choose a profile name (e.g., 'marcos', 'john_smith'){RESET}")
    profile_name = get_input("Profile name").lower().replace(" ", "_")
    
    # Check if profile exists
    profile_dir = Path(f"data/profiles/{profile_name}")
    if profile_dir.exists():
        overwrite = get_input(f"Profile '{profile_name}' exists. Overwrite? (yes/no)", default="no")
        if overwrite.lower() != "yes":
            print(f"\n{YELLOW}Setup cancelled.{RESET}\n")
            return
    
    # Collect information
    config = {
        "user_profile": setup_user_profile(),
        "professional_info": setup_professional_info(),
        "job_preferences": setup_job_preferences(),
        "cv_description": setup_cv_description(),
        "api_keys": setup_api_keys()
    }
    
    # Create profile files
    user_dir = create_profile_files(profile_name, config)
    
    # Print summary
    print_summary(profile_name, config, user_dir)
    
    print(f"\n{GREEN}Profile '{profile_name}' is now active!{RESET}")
    print(f"{YELLOW}You can switch profiles later using: py switch_profile.py{RESET}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup cancelled by user.{RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Error during setup: {e}{RESET}\n")
        sys.exit(1)
