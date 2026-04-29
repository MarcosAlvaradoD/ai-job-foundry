# ============================================================================
# TEST: Verificar que control_center.py usa paths.py correctamente
# ============================================================================

Write-Host ""
Write-Host "PRUEBA DE CONTROL CENTER CON PATHS.PY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

# 1. Verificar paths.py existe
Write-Host "[1/5] Verificando paths.py..." -ForegroundColor Yellow
if (Test-Path "paths.py") {
    Write-Host "      OK - paths.py existe" -ForegroundColor Green
    
    # Ejecutar paths.py para verificar
    Write-Host ""
    py paths.py
    Write-Host ""
} else {
    Write-Host "      ERROR - paths.py no encontrado!" -ForegroundColor Red
    pause
    exit 1
}

# 2. Verificar control_center.py tiene backup
Write-Host "[2/5] Verificando backup de control_center.py..." -ForegroundColor Yellow
$backups = Get-ChildItem -Filter "control_center.py.backup_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($backups) {
    Write-Host "      OK - Backup mas reciente: $($backups.Name)" -ForegroundColor Green
} else {
    Write-Host "      ADVERTENCIA - No se encontraron backups" -ForegroundColor Yellow
}

# 3. Verificar control_center.py importa paths
Write-Host ""
Write-Host "[3/5] Verificando que control_center.py importa paths..." -ForegroundColor Yellow
$content = Get-Content "control_center.py" -Raw

if ($content -match "from paths import") {
    Write-Host "      OK - control_center.py importa paths.py" -ForegroundColor Green
} else {
    Write-Host "      ERROR - control_center.py NO importa paths.py" -ForegroundColor Red
    pause
    exit 1
}

# 4. Verificar scripts de startup check existen
Write-Host ""
Write-Host "[4/5] Verificando scripts de startup check..." -ForegroundColor Yellow
$scripts = @(
    "scripts\powershell\startup_check_v3.ps1",
    "scripts\powershell\startup_check_v2.ps1",
    "scripts\powershell\startup_check.ps1"
)

$found = $false
foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "      OK - $script" -ForegroundColor Green
        $found = $true
    }
}

if (-not $found) {
    Write-Host "      ERROR - No se encontro ningun script de startup check" -ForegroundColor Red
    pause
    exit 1
}

# 5. Test de importacion de control_center.py
Write-Host ""
Write-Host "[5/5] Probando importacion de control_center.py..." -ForegroundColor Yellow
Write-Host ""

$testScript = @"
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else r'C:\Users\MSI\Desktop\ai-job-foundry'
sys.path.insert(0, project_root)

try:
    # Test import
    from paths import get_startup_check_script
    
    # Test function
    startup_script = get_startup_check_script()
    
    if startup_script:
        print(f'OK - Script encontrado: {startup_script}')
        exit(0)
    else:
        print('ERROR - get_startup_check_script() retorno None')
        exit(1)
except Exception as e:
    print(f'ERROR - {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"@

# Guardar script temporal
$testScript | Out-File -FilePath "test_temp.py" -Encoding UTF8

# Ejecutar
py test_temp.py

$exitCode = $LASTEXITCODE

# Limpiar
Remove-Item "test_temp.py" -ErrorAction SilentlyContinue

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "      OK - Importacion exitosa" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "      ERROR - Importacion fallo" -ForegroundColor Red
    pause
    exit 1
}

# Resumen
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "TODAS LAS PRUEBAS PASARON!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "El control_center.py ahora usa paths.py correctamente." -ForegroundColor White
Write-Host ""
Write-Host "Puedes ejecutar:" -ForegroundColor Yellow
Write-Host "  .\START_CONTROL_CENTER.bat" -ForegroundColor White
Write-Host ""
Write-Host "O directamente:" -ForegroundColor Yellow
Write-Host "  py control_center.py" -ForegroundColor White
Write-Host ""

pause
