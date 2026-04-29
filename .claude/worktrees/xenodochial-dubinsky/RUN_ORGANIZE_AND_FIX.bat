@echo off
REM AI Job Foundry - Organización y Fix de Auto-Apply
REM Este script ejecuta ambos procesos en secuencia

echo ========================================
echo AI JOB FOUNDRY - ORGANIZACION Y FIXES
echo ========================================
echo.

echo Paso 1: Organizando archivos del proyecto...
echo.
powershell.exe -ExecutionPolicy Bypass -File ".\ORGANIZE_PROJECT_AUTO.ps1"

echo.
echo ========================================
echo.
echo Paso 2: Aplicando fix de Auto-Apply...
echo.
py FIX_AUTO_APPLY_PIPELINE.py

echo.
echo ========================================
echo PROCESO COMPLETADO
echo ========================================
echo.
echo Siguiente paso: Probar el pipeline
echo Comando: py run_daily_pipeline.py --apply --dry-run
echo.

pause
