@echo off
REM AI Job Foundry - Complete System Fix
REM Fixes email processing + FIT scores

echo ================================================================
echo     AI JOB FOUNDRY - COMPLETE SYSTEM FIX
echo ================================================================
echo.

cd /d C:\Users\MSI\Desktop\ai-job-foundry

echo.
echo 🔧 STEP 1/3: Testing Email Processor (improved detection)
echo ================================================================
py test_email_processor.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Email processor test failed!
    pause
    exit /b 1
)

echo.
echo.
echo 🤖 STEP 2/3: Calculating FIT Scores for ALL pending jobs
echo ================================================================
py force_analyze_all.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ FIT score calculation failed!
    pause
    exit /b 1
)

echo.
echo.
echo 📊 STEP 3/3: Opening Google Sheets to verify
echo ================================================================
start https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

echo.
echo ================================================================
echo     ✅ SYSTEM FIX COMPLETE
echo ================================================================
echo.
echo What to check in Google Sheets:
echo   1. LinkedIn tab: Should have FIT scores calculated
echo   2. New jobs should appear with FIT scores
echo   3. Status column should be updated
echo.
echo Next steps:
echo   1. Review jobs with FIT score 7+
echo   2. Run auto-apply: py control_center.py -^> Option 11 (DRY RUN)
echo   3. If satisfied, run: Option 12 (LIVE)
echo.
pause
