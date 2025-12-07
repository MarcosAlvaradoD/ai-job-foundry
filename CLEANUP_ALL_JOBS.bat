@echo off
REM ===========================================================================
REM AI JOB FOUNDRY - Complete Job Cleanup
REM Marca expirados, recalcula FIT scores, actualiza desde emails
REM ===========================================================================

echo.
echo ========================================================================
echo   AI JOB FOUNDRY - COMPLETE JOB CLEANUP
echo ========================================================================
echo.
echo Este script ejecuta:
echo   1. Marcar jobs expirados (no longer accepting, payment too low)
echo   2. Re-calcular FIT scores (considera salario)
echo   3. Actualizar status desde emails (entrevistas, etc)
echo.
pause

echo.
echo ========================================================================
echo   PASO 1/3: Marcando jobs expirados...
echo ========================================================================
echo.

py mark_expired_jobs.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR en paso 1 - Continuando...
    echo.
)

echo.
echo ========================================================================
echo   PASO 2/3: Re-calculando FIT scores...
echo ========================================================================
echo.

py recalculate_fit_scores.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR en paso 2 - Continuando...
    echo.
)

echo.
echo ========================================================================
echo   PASO 3/3: Actualizando desde emails...
echo ========================================================================
echo.

py update_status_from_emails.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR en paso 3
    echo.
)

echo.
echo ========================================================================
echo   COMPLETADO
echo ========================================================================
echo.
echo Abre Google Sheets para ver los resultados:
echo https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
echo.

pause
