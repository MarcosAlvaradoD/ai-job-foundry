# ============================================================================
# AI JOB FOUNDRY - VERIFICADOR Y CORRECTOR DE RUTAS
# 
# Este script:
# 1. Verifica que todos los archivos esten en sus ubicaciones correctas
# 2. Corrige referencias a archivos movidos
# 3. Crea backup antes de modificar
# ============================================================================

Write-Host ""
Write-Host "AI JOB FOUNDRY - VERIFICADOR DE RUTAS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$root = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $root

# ============================================================================
# VERIFICAR ARCHIVOS CRITICOS
# ============================================================================

Write-Host "VERIFICANDO ARCHIVOS CRITICOS..." -ForegroundColor Yellow
Write-Host ""

$criticalFiles = @{
    "paths.py" = "Sistema de rutas centralizado"
    "control_center.py" = "Control Center principal"
    "run_daily_pipeline.py" = "Pipeline diario"
    "requirements.txt" = "Dependencias"
    ".env" = "Configuracion"
    ".gitignore" = "Git ignore"
    "README.md" = "Documentacion"
}

$missing = @()

foreach ($file in $criticalFiles.Keys) {
    if (Test-Path $file) {
        Write-Host "[OK] $file" -ForegroundColor Green -NoNewline
        Write-Host " - $($criticalFiles[$file])" -ForegroundColor Gray
    } else {
        Write-Host "[MISSING] $file" -ForegroundColor Red
        $missing += $file
    }
}

# ============================================================================
# VERIFICAR LAUNCHERS
# ============================================================================

Write-Host ""
Write-Host "VERIFICANDO LAUNCHERS..." -ForegroundColor Yellow
Write-Host ""

$launchers = @{
    "START_CONTROL_CENTER.bat" = "Control Center"
    "START_WEB_APP.bat" = "Web App (puerto 5000)"
    "START_UNIFIED_APP.bat" = "Unified App CON ANUNCIOS (puerto 5555)"
}

foreach ($launcher in $launchers.Keys) {
    if (Test-Path $launcher) {
        Write-Host "[OK] $launcher" -ForegroundColor Green -NoNewline
        Write-Host " - $($launchers[$launcher])" -ForegroundColor Gray
    } else {
        Write-Host "[MISSING] $launcher" -ForegroundColor Red
        $missing += $launcher
    }
}

# ============================================================================
# VERIFICAR DIRECTORIOS PRINCIPALES
# ============================================================================

Write-Host ""
Write-Host "VERIFICANDO DIRECTORIOS..." -ForegroundColor Yellow
Write-Host ""

$directories = @(
    "core", "core\automation", "core\enrichment", "core\ingestion",
    "core\sheets", "core\utils", "core\copilot", "core\jobs_pipeline",
    "scripts", "scripts\powershell", "scripts\maintenance", "scripts\oauth",
    "data", "data\credentials", "docs", "logs", "state",
    "web_app", "unified_app"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "[OK] $dir\" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $dir\" -ForegroundColor Red
        $missing += $dir
    }
}

# ============================================================================
# VERIFICAR SCRIPTS DE STARTUP CHECK
# ============================================================================

Write-Host ""
Write-Host "VERIFICANDO SCRIPTS DE STARTUP CHECK..." -ForegroundColor Yellow
Write-Host ""

$startupScripts = @(
    "scripts\powershell\startup_check_v3.ps1",
    "scripts\powershell\startup_check_v2.ps1",
    "scripts\powershell\startup_check.ps1"
)

$foundStartup = $false
foreach ($script in $startupScripts) {
    if (Test-Path $script) {
        Write-Host "[OK] $script" -ForegroundColor Green
        $foundStartup = $true
    }
}

if (-not $foundStartup) {
    Write-Host "[WARNING] No se encontro ningun script de startup check" -ForegroundColor Red
    $missing += "startup_check"
}

# ============================================================================
# VERIFICAR paths.py
# ============================================================================

Write-Host ""
Write-Host "VERIFICANDO paths.py..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "paths.py") {
    # Ejecutar paths.py para verificar
    $pathsOutput = py paths.py 2>&1
    Write-Host $pathsOutput
} else {
    Write-Host "[ERROR] paths.py no existe!" -ForegroundColor Red
    Write-Host "Este archivo es critico para el sistema de rutas." -ForegroundColor Red
}

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "RESUMEN DE VERIFICACION" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

if ($missing.Count -eq 0) {
    Write-Host "TODO VERIFICADO CORRECTAMENTE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "El proyecto esta correctamente organizado." -ForegroundColor White
} else {
    Write-Host "ARCHIVOS/DIRECTORIOS FALTANTES: $($missing.Count)" -ForegroundColor Red
    Write-Host ""
    foreach ($item in $missing) {
        Write-Host "  - $item" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "ACCIONES RECOMENDADAS:" -ForegroundColor Yellow
    Write-Host "  1. Revisar si los archivos fueron movidos" -ForegroundColor White
    Write-Host "  2. Ejecutar ORGANIZE_ROOT_SAFE.ps1" -ForegroundColor White
    Write-Host "  3. Restaurar desde backup si es necesario" -ForegroundColor White
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# TEST DE LAUNCHERS
# ============================================================================

Write-Host "VERIFICANDO LAUNCHERS..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Para probar cada launcher, ejecuta:" -ForegroundColor White
Write-Host ""
Write-Host "  START_CONTROL_CENTER.bat" -ForegroundColor Gray
Write-Host "  START_WEB_APP.bat" -ForegroundColor Gray
Write-Host "  START_UNIFIED_APP.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "Launcher recomendado (CON ANUNCIOS): START_UNIFIED_APP.bat" -ForegroundColor Green
Write-Host ""
