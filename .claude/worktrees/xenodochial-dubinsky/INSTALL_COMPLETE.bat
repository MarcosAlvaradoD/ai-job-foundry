@echo off
REM ============================================================================
REM AI JOB FOUNDRY - COMPLETE INSTALLATION
REM Fixes all dependencies and sets up the system
REM ============================================================================

echo.
echo ========================================================================
echo   AI JOB FOUNDRY - COMPLETE INSTALLATION
echo ========================================================================
echo.
echo This will:
echo   1. Install ALL Python dependencies
echo   2. Install Playwright browsers
echo   3. Create necessary directories
echo   4. Run setup wizard for your profile
echo.
pause

cd /d "%~dp0"

echo.
echo ========================================================================
echo   STEP 1: Installing Python Dependencies
echo ========================================================================
echo.

pip install --upgrade pip

pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install playwright==1.40.0
pip install beautifulsoup4==4.12.2
pip install selenium==4.15.2
pip install requests==2.31.0
pip install lxml==4.9.3
pip install gspread==5.12.0
pip install google-auth==2.23.4
pip install google-auth-oauthlib==1.1.0
pip install google-auth-httplib2==0.1.1
pip install google-api-python-client==2.108.0
pip install openai==1.3.7
pip install litellm==1.0.3
pip install pandas==2.1.3
pip install numpy==1.26.2
pip install openpyxl==3.1.2
pip install python-dotenv==1.0.0
pip install pyyaml==6.0.1
pip install colorama==0.4.6
pip install tqdm==4.66.1
pip install python-dateutil==2.8.2
pip install pytz==2023.3

echo.
echo ========================================================================
echo   STEP 2: Installing Playwright Browsers
echo ========================================================================
echo.

playwright install chromium

echo.
echo ========================================================================
echo   STEP 3: Creating Directories
echo ========================================================================
echo.

if not exist "data\profiles" mkdir data\profiles
if not exist "data\credentials" mkdir data\credentials
if not exist "data\state" mkdir data\state
if not exist "logs\powershell" mkdir logs\powershell

echo [OK] Directories created

echo.
echo ========================================================================
echo   STEP 4: Verification
echo ========================================================================
echo.

echo Running verification script...
powershell.exe -ExecutionPolicy Bypass -File "VERIFY_INSTALLATION.ps1"

echo.
echo ========================================================================
echo   STEP 5: User Profile Setup
echo ========================================================================
echo.

echo Now we'll create your user profile...
echo.
pause

py setup_wizard.py

echo.
echo ========================================================================
echo   INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo Next steps:
echo   1. Configure Google Sheets ID in your profile's .env file
echo   2. Run OAuth setup: py setup_oauth_helper.py
echo   3. Start the app: START_UNIFIED_APP.bat
echo.
echo ========================================================================
echo.
pause
