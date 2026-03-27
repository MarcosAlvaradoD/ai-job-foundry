# LinkedIn Auto-Apply V3 - Quick Test
# Tests auto-login and applies to high-FIT jobs (dry-run mode)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  LINKEDIN AUTO-APPLY V3 - TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "[INFO] Create .env with LINKEDIN_EMAIL and LINKEDIN_PASSWORD" -ForegroundColor Yellow
    exit 1
}

# Check credentials
Write-Host "[CHECK] Verifying LinkedIn credentials..." -ForegroundColor Yellow
$envContent = Get-Content ".env" -Raw

if ($envContent -match "LINKEDIN_EMAIL=(.+)") {
    $email = $matches[1].Trim()
    Write-Host "[OK] Email: $email" -ForegroundColor Green
} else {
    Write-Host "[ERROR] LINKEDIN_EMAIL not found in .env" -ForegroundColor Red
    exit 1
}

if ($envContent -match "LINKEDIN_PASSWORD=(.+)") {
    Write-Host "[OK] Password: ***********" -ForegroundColor Green
} else {
    Write-Host "[ERROR] LINKEDIN_PASSWORD not found in .env" -ForegroundColor Red
    exit 1
}

# Create data directory if it doesn't exist
if (-not (Test-Path "data")) {
    Write-Host "[CREATE] Creating data/ directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" | Out-Null
}

Write-Host "`n[START] Running LinkedIn Auto-Apply V3..." -ForegroundColor Cyan
Write-Host "[INFO] This is a DRY-RUN - no applications will be submitted`n" -ForegroundColor Yellow

# Run the test script
py scripts\test_linkedin_autoapply_v3.py

$exitCode = $LASTEXITCODE

Write-Host "`n========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] Test completed!" -ForegroundColor Green
    
    # Check if cookies were saved
    if (Test-Path "data\linkedin_cookies.json") {
        Write-Host "[OK] Cookies saved - next run will be faster!" -ForegroundColor Green
    }
    
    Write-Host "`n[NEXT STEPS]" -ForegroundColor Yellow
    Write-Host "1. Review the output above" -ForegroundColor White
    Write-Host "2. If login worked, edit scripts\test_linkedin_autoapply_v3.py" -ForegroundColor White
    Write-Host "3. Change dry_run=False for live applications" -ForegroundColor White
    Write-Host "4. Run again with: .\test_linkedin_autoapply.ps1`n" -ForegroundColor White
} else {
    Write-Host "[ERROR] Test failed - check output above" -ForegroundColor Red
    Write-Host "[HELP] Common issues:" -ForegroundColor Yellow
    Write-Host "  - Verify credentials in .env" -ForegroundColor White
    Write-Host "  - Check if LinkedIn requires verification" -ForegroundColor White
    Write-Host "  - Ensure you have jobs with FIT >= 7 in Sheets`n" -ForegroundColor White
}
Write-Host "========================================`n" -ForegroundColor Cyan

exit $exitCode
