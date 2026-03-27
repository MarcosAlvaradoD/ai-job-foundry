@echo off
REM Process ALL emails and calculate FIT scores - SIMPLE VERSION

echo ================================================================
echo     AI JOB FOUNDRY - FULL PROCESSING
echo ================================================================
echo.

cd /d C:\Users\MSI\Desktop\ai-job-foundry

echo Step 1/2: Processing ALL emails from JOBS/Inbound
echo ================================================================
py -c "from core.automation.job_bulletin_processor import JobBulletinProcessor; p = JobBulletinProcessor(); p.process_bulletins(max_emails=200)"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Email processing failed!
    pause
    exit /b 1
)

echo.
echo.
echo Step 2/2: Calculating FIT Scores
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
echo ================================================================
echo     ✅ PROCESSING COMPLETE
echo ================================================================
echo.
echo Opening Google Sheets to verify...
start https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
echo.
echo Check Google Sheets for:
echo   1. New jobs in LinkedIn/Indeed/Glassdoor tabs
echo   2. FIT Scores calculated (not 0)
echo   3. Status = "New"
echo.
echo JOBS/Inbound should be empty (emails moved to TRASH)
echo.
pause
