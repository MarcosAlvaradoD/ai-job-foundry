#!/usr/bin/env python3
"""
AI JOB FOUNDRY - MENU TESTER
Prueba todas las opciones del control center para verificar que funcionan

Usage:
    py scripts/test_all_menu_options.py
"""

import subprocess
import sys
from pathlib import Path

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
END = '\033[0m'

def test_option(option_num: str, option_name: str, timeout: int = 10) -> bool:
    """Test a single menu option"""
    print(f"\n{'='*70}")
    print(f"{CYAN}Testing Option {option_num}: {option_name}{END}")
    print(f"{'='*70}")
    
    # Options that require user input - skip automated testing
    interactive_options = ['7', '9', '11', '12', '13', '14', '15', '16', '17', '20']
    
    if option_num in interactive_options:
        print(f"{YELLOW}⚠️  INTERACTIVE - Requires manual input - SKIPPED{END}")
        return None  # None = skipped
    
    # Command mapping
    commands = {
        '1': ['py', 'run_daily_pipeline.py', '--all'],
        '2': ['py', 'run_daily_pipeline.py', '--emails', '--report'],
        '3': ['py', 'run_daily_pipeline.py', '--emails'],
        '4': ['py', 'core/automation/job_bulletin_processor.py'],
        '5': ['py', 'run_daily_pipeline.py', '--analyze'],
        '6': ['py', 'run_daily_pipeline.py', '--expire'],
        '8': ['py', 'run_daily_pipeline.py', '--report'],
        '10': None,  # Indeed scraper - disabled
        '18': None,  # Not implemented yet
        '19': ['py', 'scripts/verifiers/EXPIRE_LIFECYCLE.py', '--mark']
    }
    
    cmd = commands.get(option_num)
    
    if cmd is None:
        if option_num == '10':
            print(f"{YELLOW}⚠️  Indeed Scraper - DISABLED (timeout issues){END}")
        elif option_num == '18':
            print(f"{YELLOW}⚠️  Email Status Update - NOT IMPLEMENTED YET{END}")
        return None
    
    try:
        print(f"{CYAN}Running: {' '.join(cmd)}{END}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',  # Force UTF-8 encoding
            errors='replace',   # Replace invalid chars instead of crashing
            timeout=timeout,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✅ PASS{END}")
            return True
        else:
            print(f"{RED}❌ FAIL - Exit code: {result.returncode}{END}")
            if result.stderr:
                print(f"{RED}Error: {result.stderr[:200]}{END}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ TIMEOUT - Exceeded {timeout}s{END}")
        return False
    except FileNotFoundError as e:
        print(f"{RED}❌ FILE NOT FOUND: {e}{END}")
        return False
    except Exception as e:
        print(f"{RED}❌ ERROR: {e}{END}")
        return False

def main():
    print(f"\n{CYAN}{'='*70}")
    print(f"🧪 AI JOB FOUNDRY - MENU OPTIONS TESTER")
    print(f"{'='*70}{END}\n")
    
    # Test cases: (option_num, option_name, timeout_seconds)
    tests = [
        ('1', 'Pipeline Completo', 120),
        ('2', 'Pipeline Rápido', 60),
        ('3', 'Procesar Emails Nuevos', 30),
        ('4', 'Procesar Boletines', 30),
        ('5', 'Análisis AI', 30),
        ('6', 'Verificar Ofertas Expiradas', 30),
        ('7', 'Verificar URLs (Interactive)', 10),
        ('8', 'Generar Reporte', 30),
        ('9', 'LinkedIn Scraper (Interactive)', 10),
        ('10', 'Indeed Scraper', 10),
        ('11', 'Auto-Apply DRY RUN (Interactive)', 10),
        ('12', 'Auto-Apply LIVE (Interactive)', 10),
        ('13', 'Dashboard (Interactive)', 10),
        ('14', 'Google Sheets (Interactive)', 10),
        ('15', 'Ver .env (Interactive)', 10),
        ('16', 'Ver Docs (Interactive)', 10),
        ('17', 'Interview Copilot (Interactive)', 10),
        ('18', 'Actualizar Status Emails', 10),
        ('19', 'Marcar Jobs Expirados', 30),
        ('20', 'Regenerar OAuth (Interactive)', 10)
    ]
    
    results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'details': []
    }
    
    for option_num, option_name, timeout in tests:
        result = test_option(option_num, option_name, timeout)
        
        if result is True:
            results['passed'] += 1
            results['details'].append(f"✅ Option {option_num}: {option_name}")
        elif result is False:
            results['failed'] += 1
            results['details'].append(f"❌ Option {option_num}: {option_name}")
        else:  # None = skipped
            results['skipped'] += 1
            results['details'].append(f"⚠️  Option {option_num}: {option_name} (skipped)")
    
    # Print summary
    print(f"\n{CYAN}{'='*70}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*70}{END}")
    print(f"{GREEN}✅ Passed: {results['passed']}{END}")
    print(f"{RED}❌ Failed: {results['failed']}{END}")
    print(f"{YELLOW}⚠️  Skipped: {results['skipped']}{END}")
    print(f"{'='*70}\n")
    
    print(f"{CYAN}DETAILS:{END}")
    for detail in results['details']:
        print(f"  {detail}")
    
    print(f"\n{CYAN}{'='*70}{END}\n")
    
    # Exit code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
