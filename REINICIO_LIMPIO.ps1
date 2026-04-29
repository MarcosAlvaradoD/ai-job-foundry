# ============================================================================
# REINICIO LIMPIO - Control Center
# Mata procesos Python y ejecuta limpio
# ============================================================================

Write-Host ""
Write-Host "REINICIO LIMPIO - AI JOB FOUNDRY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

# 1. Matar todos los procesos Python
Write-Host "[1/4] Cerrando procesos Python existentes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python*, py* -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "      Encontrados $($pythonProcesses.Count) procesos Python" -ForegroundColor White
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    Write-Host "      OK - Procesos cerrados" -ForegroundColor Green
} else {
    Write-Host "      OK - No hay procesos Python ejecutando" -ForegroundColor Green
}

# 2. Limpiar cache de Python
Write-Host ""
Write-Host "[2/4] Limpiando cache de Python..." -ForegroundColor Yellow

# Limpiar __pycache__
$pycacheDirs = Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
if ($pycacheDirs) {
    $pycacheDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      OK - Cache limpiado ($($pycacheDirs.Count) directorios)" -ForegroundColor Green
} else {
    Write-Host "      OK - No hay cache que limpiar" -ForegroundColor Green
}

# Limpiar .pyc files
$pycFiles = Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
if ($pycFiles) {
    $pycFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "      OK - Archivos .pyc eliminados ($($pycFiles.Count) archivos)" -ForegroundColor Green
}

# 3. Verificar que control_center.py esta actualizado
Write-Host ""
Write-Host "[3/4] Verificando control_center.py..." -ForegroundColor Yellow
$content = Get-Content "control_center.py" -Raw

if ($content -match "from paths import get_startup_check_script") {
    Write-Host "      OK - control_center.py usa paths.py" -ForegroundColor Green
} else {
    Write-Host "      ERROR - control_center.py NO usa paths.py" -ForegroundColor Red
    Write-Host "      Por favor ejecuta TEST_CONTROL_CENTER.ps1 primero" -ForegroundColor Yellow
    pause
    exit 1
}

# 4. Ejecutar Control Center limpio
Write-Host ""
Write-Host "[4/4] Iniciando Control Center (version limpia)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Ejecutar directamente (sin .bat para evitar cache)
py control_center.py

# Si falla
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR AL EJECUTAR CONTROL CENTER" -ForegroundColor Red
    Write-Host ""
    Write-Host "Intenta manualmente:" -ForegroundColor Yellow
    Write-Host "  py control_center.py" -ForegroundColor White
    Write-Host ""
}

pause
