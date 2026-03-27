@echo off
REM ============================================================================
REM PROCESS ALL EMAILS - Unified email processing pipeline
REM Uses new email classifier + bulletin processor
REM ============================================================================

echo.
echo ========================================
echo   EMAIL PROCESSING V2.0
echo ========================================
echo.

REM Set working directory
cd /d "%~dp0"

echo [Step 1/6] Classifying and processing emails...
py core\automation\unified_email_processor.py --max 50

echo.
echo [Step 2/6] Processing job bulletins...
py core\automation\job_bulletin_processor.py

echo.
echo [Step 3/6] Syncing interview status...
py update_status_from_emails.py

echo.
echo [Step 4/6] Marking negative jobs...
py mark_all_negatives.py

echo.
echo [Step 5/6] Recalculating FIT scores...
py recalculate_fit_scores.py

echo.
echo [Step 6/6] Generating summary...
py scripts\maintenance\verify_job_status.py

echo.
echo ========================================
echo   ✅ EMAIL PROCESSING COMPLETE
echo ========================================
echo.
echo Check Google Sheets for new jobs
echo.

pause
