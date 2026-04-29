"""
TEST RÁPIDO - Verificar Fix de FitScore
=========================================
Prueba que el auto-apply maneja correctamente FitScores vacíos
"""

def safe_fit_score(fit_value):
    """Safely convert FitScore to int, handling empty strings and formats like '8/10'"""
    try:
        if not fit_value or fit_value == '':
            return 0
        fit_str = str(fit_value).strip()
        if '/' in fit_str:
            return int(fit_str.split('/')[0])
        return int(fit_str)
    except Exception:
        return 0

# Test cases
test_cases = [
    ('8/10', 8),
    ('7', 7),
    ('', 0),
    (None, 0),
    ('9/10', 9),
    ('  ', 0),
    ('invalid', 0),
]

print("\n" + "="*60)
print("TESTING SAFE_FIT_SCORE FUNCTION")
print("="*60)

all_passed = True
for test_input, expected in test_cases:
    result = safe_fit_score(test_input)
    status = "OK" if result == expected else "FAIL"
    if result != expected:
        all_passed = False
    print(f"{status} Input: {repr(test_input):15} Expected: {expected:2} Got: {result:2}")

print("="*60)
if all_passed:
    print("TODOS LOS TESTS PASARON")
else:
    print("ALGUNOS TESTS FALLARON")
print("="*60)
