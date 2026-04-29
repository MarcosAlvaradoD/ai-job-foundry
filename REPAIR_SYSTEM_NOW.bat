@echo off
REM AI Job Foundry - Emergency Repair Script
REM Fixes OAuth and Gmail processing issues

echo ================================================================
echo     AI JOB FOUNDRY - EMERGENCY REPAIR
echo ================================================================
echo.

cd /d C:\Users\MSI\Desktop\ai-job-foundry

echo.
echo 1/3: Regenerating OAuth token with correct scopes...
echo ----------------------------------------------------------------
py scripts\oauth\regenerate_oauth_token.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ OAuth regeneration failed!
    echo    Make sure credentials.json exists in data/credentials/
    pause
    exit /b 1
)

echo.
echo 2/3: Diagnosing Gmail configuration...
echo ----------------------------------------------------------------
py scripts\diagnostics\diagnose_gmail.py

echo.
echo 3/3: Testing email processing...
echo ----------------------------------------------------------------
py core\automation\job_bulletin_processor.py

echo.
echo ================================================================
echo     REPAIR COMPLETE
echo ================================================================
echo.
echo Next step: Run Control Center and test
echo Command: py control_center.py
echo.
pause
