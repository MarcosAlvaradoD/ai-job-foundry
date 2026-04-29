Set WshShell = CreateObject("WScript.Shell")

' Install dependencies silently
WshShell.Run "cmd /c pip install flask playwright gspread google-auth python-dotenv requests beautifulsoup4 colorama > nul 2>&1", 0, True

' Install Playwright browsers silently
WshShell.Run "cmd /c playwright install chromium > nul 2>&1", 0, True

' Show completion message
WScript.Echo "Dependencies installed successfully!"
