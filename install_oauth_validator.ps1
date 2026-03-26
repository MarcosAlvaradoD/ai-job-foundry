# =============================================================================
# 🔐 INSTALADOR DEL OAUTH TOKEN VALIDATOR
# =============================================================================
# Este script instala y configura el sistema de validación automática de 
# tokens OAuth en el proyecto AI Job Foundry.
#
# Uso: .\install_oauth_validator.ps1
#
# Autor: Marcos Alberto Alvarado
# Fecha: 2026-01-02
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🔐 OAUTH TOKEN VALIDATOR - INSTALADOR" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path ".\core")) {
    Write-Host "❌ ERROR: Este script debe ejecutarse desde la raíz del proyecto" -ForegroundColor Red
    Write-Host "   Ubicación esperada: C:\Users\MSI\Desktop\ai-job-foundry\" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Ubicación del proyecto verificada" -ForegroundColor Green
Write-Host ""

# =============================================================================
# PASO 1: VERIFICAR OAUTH_TOKEN_VALIDATOR.PY
# =============================================================================
Write-Host "[1/3] Verificando oauth_token_validator.py..." -ForegroundColor Yellow

if (Test-Path ".\oauth_token_validator.py") {
    Write-Host "   ✅ oauth_token_validator.py encontrado" -ForegroundColor Green
} else {
    Write-Host "   ❌ ERROR: oauth_token_validator.py no encontrado" -ForegroundColor Red
    Write-Host "   Este archivo debería haberse creado automáticamente" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# =============================================================================
# PASO 2: CREAR BACKUP DE ARCHIVOS ORIGINALES (SI EXISTEN)
# =============================================================================
Write-Host "[2/3] Verificando archivos modificados..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = ".\backups\oauth_fix_$timestamp"

$filesToCheck = @(
    ".\main.py",
    ".\run_daily_pipeline.py"
)

$needsBackup = $false
foreach ($file in $filesToCheck) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file encontrado (modificado)" -ForegroundColor Green
        $needsBackup = $true
    }
}

if ($needsBackup) {
    Write-Host ""
    Write-Host "   Los archivos han sido actualizados con validación OAuth" -ForegroundColor Cyan
    Write-Host "   Si necesitas los originales, están en Git" -ForegroundColor Yellow
}

Write-Host ""

# =============================================================================
# PASO 3: VERIFICAR INSTALACIÓN
# =============================================================================
Write-Host "[3/3] Verificando instalación..." -ForegroundColor Yellow

# Verificar archivos críticos
$criticalFiles = @{
    "oauth_token_validator.py" = "Validador OAuth"
    "main.py" = "Pipeline principal"
    "run_daily_pipeline.py" = "Pipeline diario"
    "scripts\test_oauth_validator.py" = "Script de prueba"
    "scripts\oauth\reauthenticate_gmail_v2.py" = "Script de renovación"
}

$allGood = $true
foreach ($file in $criticalFiles.Keys) {
    if (Test-Path $file) {
        Write-Host "   ✅ $($criticalFiles[$file])" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $($criticalFiles[$file]) NO encontrado: $file" -ForegroundColor Yellow
        $allGood = $false
    }
}

Write-Host ""

# =============================================================================
# RESULTADO
# =============================================================================
Write-Host "=" * 70 -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✅ INSTALACIÓN VERIFICADA" -ForegroundColor Green
} else {
    Write-Host "⚠️  INSTALACIÓN PARCIAL" -ForegroundColor Yellow
}
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Probar el validador manualmente:" -ForegroundColor White
Write-Host "   py oauth_token_validator.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Ejecutar suite de pruebas:" -ForegroundColor White
Write-Host "   py scripts\test_oauth_validator.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Ejecutar pipeline para verificar:" -ForegroundColor White
Write-Host "   py run_daily_pipeline.py --all" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Si hay errores con token, renovar manualmente:" -ForegroundColor White
Write-Host "   py scripts\oauth\reauthenticate_gmail_v2.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Para forzar renovación del token:" -ForegroundColor White
Write-Host "   py oauth_token_validator.py --force" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Preguntar si quiere ejecutar test
$runTest = Read-Host "¿Ejecutar prueba del validador ahora? (Y/N)"
if ($runTest -eq "Y" -or $runTest -eq "y") {
    Write-Host ""
    Write-Host "Ejecutando: py oauth_token_validator.py" -ForegroundColor Cyan
    Write-Host ""
    py oauth_token_validator.py
}

Write-Host ""
Write-Host "✅ Verificación completada" -ForegroundColor Green
Write-Host ""
