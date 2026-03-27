@echo off
REM ============================================================================
REM AI JOB FOUNDRY - BUILD EXECUTABLE
REM Creates standalone EXE using PyInstaller
REM ============================================================================

echo.
echo ========================================================================
echo   AI JOB FOUNDRY - BUILD EXECUTABLE
echo ========================================================================
echo.

REM Check if PyInstaller is installed
echo [1/5] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] PyInstaller not found, installing...
    pip install pyinstaller
) else (
    echo [OK] PyInstaller is installed
)

echo.
echo [2/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo [3/5] Building executable...
echo This may take several minutes...
pyinstaller --name="AIJobFoundry" ^
    --onefile ^
    --console ^
    --add-data="unified_app/templates;unified_app/templates" ^
    --add-data="README.md;." ^
    --add-data="QUICK_START_UNIFIED.md;." ^
    --hidden-import=flask ^
    --hidden-import=gspread ^
    --hidden-import=google.auth ^
    --hidden-import=playwright ^
    --hidden-import=dotenv ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    unified_app/app.py

echo.
echo [4/5] Creating distribution package...
mkdir dist\AIJobFoundry 2>nul
copy dist\AIJobFoundry.exe dist\AIJobFoundry\ >nul
copy README.md dist\AIJobFoundry\ >nul
copy QUICK_START_UNIFIED.md dist\AIJobFoundry\ >nul
copy START_UNIFIED_APP.bat dist\AIJobFoundry\ >nul

REM Create data directories
mkdir dist\AIJobFoundry\data\credentials 2>nul
mkdir dist\AIJobFoundry\data\profiles 2>nul
mkdir dist\AIJobFoundry\data\state 2>nul

REM Copy setup scripts
copy setup_wizard_complete.py dist\AIJobFoundry\setup_wizard.py >nul
copy switch_profile.py dist\AIJobFoundry\ >nul

REM Copy silent launchers
copy install_silent.vbs dist\AIJobFoundry\ >nul
copy START_UNIFIED_APP_SILENT.vbs dist\AIJobFoundry\ >nul

echo.
echo [5/5] Creating installer...
echo @echo off > dist\AIJobFoundry\INSTALL.bat
echo echo ============================================ >> dist\AIJobFoundry\INSTALL.bat
echo echo   AI JOB FOUNDRY - INSTALLER >> dist\AIJobFoundry\INSTALL.bat
echo echo ============================================ >> dist\AIJobFoundry\INSTALL.bat
echo echo. >> dist\AIJobFoundry\INSTALL.bat
echo echo [1/3] Installing Python dependencies... >> dist\AIJobFoundry\INSTALL.bat
echo pip install -r requirements.txt >> dist\AIJobFoundry\INSTALL.bat
echo echo. >> dist\AIJobFoundry\INSTALL.bat
echo echo [2/3] Installing Playwright browsers... >> dist\AIJobFoundry\INSTALL.bat
echo playwright install chromium >> dist\AIJobFoundry\INSTALL.bat
echo echo. >> dist\AIJobFoundry\INSTALL.bat
echo echo [3/3] Running setup wizard... >> dist\AIJobFoundry\INSTALL.bat
echo py setup_wizard.py >> dist\AIJobFoundry\INSTALL.bat
echo pause >> dist\AIJobFoundry\INSTALL.bat

copy requirements.txt dist\AIJobFoundry\ >nul

echo.
echo ========================================================================
echo   BUILD COMPLETE!
echo ========================================================================
echo.
echo Executable location: dist\AIJobFoundry\AIJobFoundry.exe
echo Distribution folder: dist\AIJobFoundry\
echo.
echo To distribute:
echo   1. Copy the entire dist\AIJobFoundry\ folder
echo   2. User runs: INSTALL.bat
echo   3. User runs: AIJobFoundry.exe or START_UNIFIED_APP.bat
echo.
echo ========================================================================
echo.
pause
