@echo off
REM ============================================================================
REM AI JOB FOUNDRY - FIX DEPENDENCIES
REM Instala todas las dependencias faltantes
REM ============================================================================

echo.
echo ========================================================================
echo   AI JOB FOUNDRY - INSTALANDO DEPENDENCIAS FALTANTES
echo ========================================================================
echo.

echo [1/2] Instalando google-auth...
pip install google-auth google-auth-oauthlib google-auth-httplib2

echo.
echo [2/2] Instalando python-dotenv...
pip install python-dotenv

echo.
echo ========================================================================
echo   INSTALACION COMPLETA
echo ========================================================================
echo.
echo Ahora puedes ejecutar: START_UNIFIED_APP.bat
echo.
pause
