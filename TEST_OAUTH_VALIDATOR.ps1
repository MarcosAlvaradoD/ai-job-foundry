# ================================================================
# TEST OAUTH VALIDATOR
# ================================================================
# Tests the OAuth validation module before running the pipeline
# Usage: .\TEST_OAUTH_VALIDATOR.ps1
# ================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  TESTING OAUTH VALIDATOR MODULE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check Python
Write-Host "Checking Python..." -NoNewline
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " OK ($pythonVersion)" -ForegroundColor Green
} else {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "Python not found. Please install Python 3.13+" -ForegroundColor Red
    exit 1
}

# Test 2: Run OAuth validator test
Write-Host ""
Write-Host "Running OAuth validator test..." -ForegroundColor Yellow
Write-Host ""

py scripts\tests\test_oauth_validator.py

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "  ✅ TEST COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host ""
    Write-Host "  OAuth validator is ready to use." -ForegroundColor Green
    Write-Host "  You can now run: .\start_all.ps1" -ForegroundColor Green
} else {
    Write-Host "  ❌ TEST FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "  OAuth token needs manual refresh." -ForegroundColor Yellow
    Write-Host "  Run: py scripts\oauth\reauthenticate_gmail_v2.py" -ForegroundColor Yellow
}
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
