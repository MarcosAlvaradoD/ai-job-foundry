#!/usr/bin/env powershell
<#
.SYNOPSIS
    Test completo del sistema después de OAuth fix
.DESCRIPTION
    Ejecuta todos los tests para verificar que OAuth funciona
.EXAMPLE
    .\test_all_fixes.ps1
#>

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
Write-ColorOutput Cyan "     🧪 AI JOB FOUNDRY - TEST COMPLETO DESPUÉS DE FIXES"
Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
Write-Host ""

$allPassed = $true

# ============================================================================
# 1. TEST OAUTH
# ============================================================================
Write-ColorOutput Cyan "📝 TEST 1: OAuth y Credenciales"
Write-Host "─────────────────────────────────────────────────────────"
Write-Host ""

try {
    py test_oauth.py
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "`n✅ TEST 1 PASSED - OAuth funcionando"
    }
    else {
        Write-ColorOutput Red "`n❌ TEST 1 FAILED - OAuth con problemas"
        $allPassed = $false
    }
}
catch {
    Write-ColorOutput Red "`n❌ TEST 1 ERROR: $_"
    $allPassed = $false
}

Write-Host ""
Write-Host ""

# ============================================================================
# 2. TEST EMAIL PROCESSING
# ============================================================================
Write-ColorOutput Cyan "📝 TEST 2: Procesamiento de Emails"
Write-Host "─────────────────────────────────────────────────────────"
Write-Host ""

$response = Read-Host "¿Ejecutar procesamiento de emails? (s/n)"
if ($response -eq 's' -or $response -eq 'S') {
    try {
        py core\jobs_pipeline\ingest_email_to_sheet_v2.py
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "`n✅ TEST 2 PASSED - Emails procesados"
        }
        else {
            Write-ColorOutput Red "`n❌ TEST 2 FAILED - Error procesando emails"
            $allPassed = $false
        }
    }
    catch {
        Write-ColorOutput Red "`n❌ TEST 2 ERROR: $_"
        $allPassed = $false
    }
}
else {
    Write-ColorOutput Yellow "⏭️  TEST 2 SKIPPED"
}

Write-Host ""
Write-Host ""

# ============================================================================
# 3. TEST BATCH UPDATES
# ============================================================================
Write-ColorOutput Cyan "📝 TEST 3: Optimización Batch Updates"
Write-Host "─────────────────────────────────────────────────────────"
Write-Host ""

$response = Read-Host "¿Ejecutar optimización de Sheets? (s/n)"
if ($response -eq 's' -or $response -eq 'S') {
    try {
        py optimize_batch_updates.py
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "`n✅ TEST 3 PASSED - Batch updates optimizados"
        }
        else {
            Write-ColorOutput Red "`n❌ TEST 3 FAILED - Error en batch updates"
            $allPassed = $false
        }
    }
    catch {
        Write-ColorOutput Red "`n❌ TEST 3 ERROR: $_"
        $allPassed = $false
    }
}
else {
    Write-ColorOutput Yellow "⏭️  TEST 3 SKIPPED"
}

Write-Host ""
Write-Host ""

# ============================================================================
# RESUMEN
# ============================================================================
Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"

if ($allPassed) {
    Write-ColorOutput Green "✅ TODOS LOS TESTS PASARON"
    Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
    Write-Host ""
    Write-ColorOutput Green "🎉 Sistema completamente funcional"
    Write-Host ""
    Write-ColorOutput Yellow "Próximos pasos:"
    Write-ColorOutput Cyan "  1. Probar Auto-Apply: py linkedin_auto_apply_v2.py"
    Write-ColorOutput Cyan "  2. Configurar Dashboard API Key"
    Write-ColorOutput Cyan "  3. Setup Task Scheduler"
    Write-Host ""
}
else {
    Write-ColorOutput Red "❌ ALGUNOS TESTS FALLARON"
    Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
    Write-Host ""
    Write-ColorOutput Yellow "Revisa los errores arriba y contacta soporte si necesitas ayuda."
    Write-Host ""
}
