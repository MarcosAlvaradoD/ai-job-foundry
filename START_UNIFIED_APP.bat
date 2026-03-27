@echo off
REM ==============================================================================
REM AI JOB FOUNDRY - UNIFIED APP AUTO-STARTER (FIXED)
REM 
REM This script:
REM 1. Runs system health checks
REM 2. Starts LM Studio if not running
REM 3. Launches unified web app
REM 4. Opens browser automatically
REM
REM Usage: Double-click this file
REM ==============================================================================

echo.
echo ========================================================================
echo      AI JOB FOUNDRY - UNIFIED APP STARTER
echo ========================================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM ============================================================================
REM STEP 1: Run System Health Check
REM ============================================================================
echo [1/4] Running system health check...
echo.

REM Check which startup script exists
if exist "scripts\powershell\startup_check_v3.ps1" (
    powershell.exe -ExecutionPolicy Bypass -File "scripts\powershell\startup_check_v3.ps1"
) else if exist "scripts\powershell\startup_check_v2.ps1" (
    echo [INFO] Using startup_check_v2.ps1
    powershell.exe -ExecutionPolicy Bypass -File "scripts\powershell\startup_check_v2.ps1"
) else if exist "scripts\powershell\startup_check.ps1" (
    echo [INFO] Using startup_check.ps1
    powershell.exe -ExecutionPolicy Bypass -File "scripts\powershell\startup_check.ps1"
) else (
    echo [WARNING] No startup check script found, skipping...
    goto :continue_anyway
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Startup check found issues!
    echo.
    choice /C SN /M "Do you want to [S]top or [N]continue anyway"
    if errorlevel 2 goto :continue_anyway
    if errorlevel 1 goto :exit_script
)

:continue_anyway
echo.
echo [OK] System checks passed (or skipped)
echo.

REM ============================================================================
REM STEP 2: Check if LM Studio is running
REM ============================================================================
echo [2/4] Checking LM Studio status...
echo.

REM Try to ping LM Studio (check if port 11434 responds)
powershell -Command "$result = Test-NetConnection -ComputerName localhost -Port 11434 -InformationLevel Quiet; exit ($result -eq $false)"

if %ERRORLEVEL% EQU 0 (
    echo [OK] LM Studio is already running
) else (
    echo [INFO] LM Studio not detected
    echo [ACTION] Please start LM Studio manually if needed
    echo.
    echo Press any key to continue...
    pause > nul
)

echo.

REM ============================================================================
REM STEP 3: Start Unified Web App
REM ============================================================================
echo [3/4] Starting Unified Web App...
echo.

REM Kill any existing Flask processes on port 5555
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5555"') do (
    echo [INFO] Stopping existing process on port 5555...
    taskkill /F /PID %%a > nul 2>&1
)

REM Start the unified app
echo [LAUNCHING] py unified_app/app.py
echo.
echo ========================================================================
echo.
echo   Unified Web App starting on http://localhost:5555
echo.
echo   Features:
echo   - 17 Control Center functions
echo   - Real-time dashboard
echo   - 3 advertising zones integrated
echo.
echo   Browser will open automatically in 3 seconds...
echo.
echo ========================================================================
echo.

REM Start Python app (will auto-open browser)
py unified_app\app.py

REM ============================================================================
REM STEP 4: Cleanup on exit
REM ============================================================================
:exit_script
echo.
echo ========================================================================
echo   Unified App stopped
echo ========================================================================
echo.
pause
exit /b
