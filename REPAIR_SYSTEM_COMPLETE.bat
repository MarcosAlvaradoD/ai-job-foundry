@echo off
REM COMPLETE SYSTEM REPAIR - OAuth + LM Studio + Processing

echo ================================================================
echo     AI JOB FOUNDRY - COMPLETE SYSTEM REPAIR
echo ================================================================
echo.
echo This will:
echo   1. Regenerate OAuth token (fixes invalid_scope)
echo   2. Detect LM Studio IP (updates .env)
echo   3. Process ALL emails
echo   4. Calculate FIT scores
echo.
echo Press Ctrl+C to cancel, or
pause

cd /d C:\Users\MSI\Desktop\ai-job-foundry

REM Step 1: Close any blocking processes
echo.
echo Step 1/5: Closing blocking processes...
echo ================================================================
powershell -Command "Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force"
timeout /t 2 /nobreak >nul

REM Step 2: Regenerate OAuth Token
echo.
echo Step 2/5: Regenerating OAuth Token...
echo ================================================================
echo This will open your browser for authentication.
echo.
py scripts\oauth\regenerate_oauth_token.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ OAuth regeneration failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ OAuth token regenerated successfully!
timeout /t 2 /nobreak >nul

REM Step 3: Detect LM Studio IP
echo.
echo Step 3/5: Detecting LM Studio IP...
echo ================================================================
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "detect_lm_studio_ip.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ LM Studio detection failed!
    echo Please make sure LM Studio is running.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ LM Studio configured successfully!
timeout /t 2 /nobreak >nul

REM Step 4: Process ALL emails
echo.
echo Step 4/5: Processing ALL emails from JOBS/Inbound...
echo ================================================================
py -c "from core.automation.job_bulletin_processor import JobBulletinProcessor; p = JobBulletinProcessor(); p.process_bulletins(max_emails=200)"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Email processing failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Emails processed successfully!
timeout /t 2 /nobreak >nul

REM Step 5: Calculate FIT Scores
echo.
echo Step 5/5: Calculating FIT Scores with AI...
echo ================================================================
py force_analyze_all.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ FIT score calculation failed!
    echo.
    pause
    exit /b 1
)

echo.
echo.
echo ================================================================
echo     ✅✅✅ SYSTEM FULLY REPAIRED ✅✅✅
echo ================================================================
echo.
echo All systems are now operational!
echo.
echo Opening Google Sheets to verify...
start https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
echo.
echo What to check:
echo   1. New jobs in LinkedIn/Indeed/Glassdoor tabs
echo   2. FIT Scores calculated (not 0)
echo   3. Status = "New"
echo   4. JOBS/Inbound folder empty (emails in TRASH)
echo.
echo Next step: Run auto-apply on jobs with FIT 7+
echo   Command: py control_center.py (Option 11 or 12)
echo.
pause
