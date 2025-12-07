"""
TEST RAPIDO - Verificar Fixes del Pipeline
===========================================
Verifica que los imports y metodos esten correctos
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("TESTING PIPELINE FIXES")
print("=" * 70)

# Test 1: verify_job_status import
print("\n[1/3] Testing verify_job_status import...")
try:
    # Add scripts/maintenance to path
    maintenance_path = project_root / "scripts" / "maintenance"
    sys.path.insert(0, str(maintenance_path))
    
    from verify_job_status import JobStatusVerifier
    print("    [OK] verify_job_status import OK")
except Exception as e:
    print(f"    [FAIL] {e}")

# Test 2: LinkedInAutoApplier has 'run' method
print("\n[2/3] Testing LinkedInAutoApplier.run() method...")
try:
    from core.automation.auto_apply_linkedin import LinkedInAutoApplier
    applier = LinkedInAutoApplier(dry_run=True)
    
    # Check if 'run' method exists
    if hasattr(applier, 'run'):
        print("    [OK] LinkedInAutoApplier.run() exists")
    else:
        print("    [FAIL] LinkedInAutoApplier has no 'run' method")
        print(f"    Available methods: {[m for m in dir(applier) if not m.startswith('_')]}")
    
    # Check that 'process_jobs' doesn't exist (old method)
    if not hasattr(applier, 'process_jobs'):
        print("    [OK] Old 'process_jobs' method correctly not found")
    else:
        print("    [WARNING] Old 'process_jobs' still exists")
        
except Exception as e:
    print(f"    [FAIL] {e}")

# Test 3: LinkedInAutoApplier._safe_fit_score() method
print("\n[3/3] Testing LinkedInAutoApplier._safe_fit_score()...")
try:
    from core.automation.auto_apply_linkedin import LinkedInAutoApplier
    applier = LinkedInAutoApplier(dry_run=True)
    
    # Test cases for FitScore parsing
    test_cases = [
        ('8/10', 8),
        ('7', 7),
        ('', 0),
        (None, 0),
        ('9/10', 9),
    ]
    
    all_passed = True
    for test_input, expected in test_cases:
        result = applier._safe_fit_score(test_input)
        if result == expected:
            print(f"    [OK] Input: {repr(test_input):10} Expected: {expected} Got: {result}")
        else:
            print(f"    [FAIL] Input: {repr(test_input):10} Expected: {expected} Got: {result}")
            all_passed = False
    
    if all_passed:
        print("    [OK] All FitScore parsing tests passed")
    else:
        print("    [FAIL] Some FitScore tests failed")
        
except Exception as e:
    print(f"    [FAIL] {e}")

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)
