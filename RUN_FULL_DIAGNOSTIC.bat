@echo off
REM AI Job Foundry - Diagnóstico Completo y Fixes
REM Ejecuta todos los análisis y correcciones necesarias

echo ========================================
echo AI JOB FOUNDRY - DIAGNOSTICO COMPLETO
echo ========================================
echo.

echo Paso 1: Analizando Google Sheets...
echo ========================================
py ANALYZE_SHEETS.py
echo.

echo Paso 2: Debuggeando Scrapers...
echo ========================================
py DEBUG_SCRAPERS.py
echo.

echo Paso 3: Aplicando fix de boletines...
echo ========================================
py FIX_BULLETIN_QUERY.py
echo.

echo Paso 4: Probando processor de boletines...
echo ========================================
py core\automation\job_bulletin_processor.py
echo.

echo ========================================
echo DIAGNOSTICO COMPLETADO
echo ========================================
echo.
echo Revisa los resultados arriba para identificar problemas.
echo.
echo Siguiente paso:
echo   - Si hay scrapers fallando: Revisar logs
echo   - Si boletines no se procesan: Verificar Gmail labels
echo   - Si faltan columnas: Actualizar sheet_manager.py
echo.

pause
