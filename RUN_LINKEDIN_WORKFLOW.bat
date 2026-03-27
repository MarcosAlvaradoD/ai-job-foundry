@echo off
REM ============================================================
REM LINKEDIN WORKFLOW - Quick Launcher
REM ============================================================
REM Author: Marcos Alberto Alvarado
REM Date: 2026-01-18
REM ============================================================

setlocal EnableDelayedExpansion

echo.
echo ================================================================
echo    LINKEDIN JOB SCRAPER - QUICK LAUNCHER
echo ================================================================
echo.
echo Select action:
echo.
echo   1. Test Scraper (scrape only - no analysis)
echo   2. Complete Workflow DRY RUN (scrape + analyze + test apply)
echo   3. Complete Workflow LIVE (scrape + analyze + REAL apply)
echo   4. Scrape Only
echo   5. Analyze Only (FIT scores)
echo   6. Apply Only DRY RUN
echo   7. Apply Only LIVE
echo   0. Exit
echo.
echo ================================================================

set /p choice="Select [0-7]: "

if "%choice%"=="1" (
    echo.
    echo [1] Running LinkedIn Notifications Test...
    echo ================================================================
    py test_linkedin_notifications.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo [2] Running Complete Workflow DRY RUN...
    echo ================================================================
    py run_linkedin_workflow.py --all
    goto end
)

if "%choice%"=="3" (
    echo.
    echo [3] Running Complete Workflow LIVE...
    echo ================================================================
    echo.
    echo WARNING: This will submit REAL applications!
    set /p confirm="Are you sure? (yes/no): "
    if /i "!confirm!"=="yes" (
        py run_linkedin_workflow.py --all --live
    ) else (
        echo Cancelled.
    )
    goto end
)

if "%choice%"=="4" (
    echo.
    echo [4] Scraping LinkedIn Notifications...
    echo ================================================================
    py run_linkedin_workflow.py --scrape-only
    goto end
)

if "%choice%"=="5" (
    echo.
    echo [5] Calculating FIT Scores...
    echo ================================================================
    py run_linkedin_workflow.py --analyze-only
    goto end
)

if "%choice%"=="6" (
    echo.
    echo [6] Auto-Apply DRY RUN...
    echo ================================================================
    py run_linkedin_workflow.py --apply-only
    goto end
)

if "%choice%"=="7" (
    echo.
    echo [7] Auto-Apply LIVE...
    echo ================================================================
    echo.
    echo WARNING: This will submit REAL applications!
    set /p confirm="Are you sure? (yes/no): "
    if /i "!confirm!"=="yes" (
        py run_linkedin_workflow.py --apply-only --live
    ) else (
        echo Cancelled.
    )
    goto end
)

if "%choice%"=="0" (
    echo Exiting...
    goto end
)

echo Invalid choice. Please select 0-7.

:end
echo.
echo ================================================================
echo Press any key to exit...
pause >nul
