' ===========================================================================
' AI JOB FOUNDRY - SILENT LAUNCHER
' Starts unified app without showing console window
' ===========================================================================

Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get script directory
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to script directory
WshShell.CurrentDirectory = strScriptPath

' Start Python app silently (window hidden)
WshShell.Run "pythonw unified_app\app.py", 0, False

' Wait a bit
WScript.Sleep 3000

' Open browser
WshShell.Run "http://localhost:5555", 1, False

' Show notification (optional)
' WScript.Echo "AI Job Foundry started successfully!"
