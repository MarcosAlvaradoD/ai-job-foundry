@echo off
REM FIX_OAUTH_TOKEN.bat
REM Regenera el token de Google OAuth usando la ruta CORRECTA

echo.
echo ======================================================================
echo   FIX OAUTH TOKEN - AI JOB FOUNDRY
echo ======================================================================
echo.
echo IMPORTANTE: 
echo - Se abrira tu navegador
echo - Inicia sesion con: markalvati@gmail.com
echo - Autoriza Gmail API + Google Sheets API
echo.
pause

py FIX_OAUTH_TOKEN.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo   TOKEN REGENERADO EXITOSAMENTE
    echo ======================================================================
    echo.
    echo Ahora puedes ejecutar:
    echo   py control_center.py
    echo.
) else (
    echo.
    echo ======================================================================
    echo   ERROR AL REGENERAR TOKEN
    echo ======================================================================
    echo.
    echo Verifica que tienes internet y que credentials.json existe
    echo.
)

pause
