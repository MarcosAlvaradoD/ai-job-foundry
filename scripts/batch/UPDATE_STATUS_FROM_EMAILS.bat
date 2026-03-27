@echo off
REM ===========================================================================
REM AI JOB FOUNDRY - Update Status from Emails
REM ===========================================================================

echo.
echo ========================================================================
echo   AI JOB FOUNDRY - EMAIL STATUS UPDATER
echo ========================================================================
echo.
echo Este script:
echo   1. Lee tus emails de Gmail
echo   2. Detecta cambios de status (entrevistas, rechazos, etc)
echo   3. Actualiza Google Sheets automaticamente
echo.
pause

echo.
echo Ejecutando...
echo.

py update_status_from_emails.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================================
    echo   EXITO - Status actualizado
    echo ========================================================================
    echo.
) else (
    echo.
    echo ========================================================================
    echo   ERROR - Revisar logs
    echo ========================================================================
    echo.
)

pause
