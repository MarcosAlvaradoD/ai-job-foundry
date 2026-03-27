@echo off
REM Quick Test - Verifica que los fixes funcionan

echo ================================================================
echo     AI JOB FOUNDRY - QUICK TEST
echo ================================================================
echo.

cd /d C:\Users\MSI\Desktop\ai-job-foundry

echo 1/2: Testing Email Processor (5 emails only)
echo ================================================================
py -c "from core.automation.job_bulletin_processor import JobBulletinProcessor; p = JobBulletinProcessor(); p.process_bulletins(max_emails=5)"

echo.
echo.
echo 2/2: Checking Google Sheets
echo ================================================================
start https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

echo.
echo ================================================================
echo TEST COMPLETE
echo ================================================================
echo.
echo What to look for:
echo   1. Should say "Processing email as USER_URLS" (not "Not a bulletin")
echo   2. Should extract URLs from emails
echo   3. Should show "Saved X NEW jobs to [Source]"
echo   4. Check Google Sheets to confirm jobs appear
echo.
pause
