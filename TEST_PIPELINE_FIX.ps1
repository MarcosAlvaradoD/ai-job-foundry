# ================================================================
# TEST DEL FIX DE ENCODING UTF-8 - RUN_DAILY_PIPELINE.PY
# ================================================================
# Ubicación: C:\Users\MSI\Desktop\ai-job-foundry\TEST_PIPELINE_FIX.ps1
#
# PROPÓSITO: Verificar que el fix de encoding UTF-8 funciona
# FECHA: 2025-01-10
# AUTOR: Claude + Marcos
# ================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🧪 TEST DEL FIX UTF-8 - RUN_DAILY_PIPELINE.PY" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# ================================================================
# TEST 1: Pipeline Rápido (solo bulletins + report)
# ================================================================
Write-Host "📋 TEST 1: Pipeline Rápido (--quick)" -ForegroundColor Yellow
Write-Host "   Prueba procesamiento de bulletins sin auto-apply`n" -ForegroundColor Gray

try {
    py run_daily_pipeline.py --quick
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ TEST 1 PASSED - Pipeline rápido funciona correctamente`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ TEST 1 FAILED - Exit code: $LASTEXITCODE`n" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "`n❌ TEST 1 FAILED - Error: $_`n" -ForegroundColor Red
    exit 1
}

# ================================================================
# TEST 2: Auto-Apply DRY RUN (no aplica real)
# ================================================================
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "📋 TEST 2: Auto-Apply DRY RUN (--apply --dry-run)" -ForegroundColor Yellow
Write-Host "   Prueba auto-apply sin aplicar realmente`n" -ForegroundColor Gray

try {
    py run_daily_pipeline.py --apply --dry-run
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ TEST 2 PASSED - Auto-apply DRY RUN funciona`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ TEST 2 FAILED - Exit code: $LASTEXITCODE`n" -ForegroundColor Red
        Write-Host "⚠️  Si el timeout fue el problema, el fix de encoding está OK" -ForegroundColor Yellow
        Write-Host "    Necesitamos investigar por qué auto-apply se queda colgado`n" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "`n❌ TEST 2 FAILED - Error: $_`n" -ForegroundColor Red
}

# ================================================================
# RESUMEN
# ================================================================
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE TESTS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "✅ FIX APLICADO:" -ForegroundColor Green
Write-Host "   - AI Analysis: encoding='utf-8' añadido" -ForegroundColor White
Write-Host "   - Auto-Apply: capture_output=False (output en tiempo real)" -ForegroundColor White
Write-Host "   - Auto-Apply: timeout reducido de 10min → 5min" -ForegroundColor White
Write-Host "   - Expire Check: encoding='utf-8' añadido`n" -ForegroundColor White

Write-Host "📝 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "   1. Si TEST 1 passed → Encoding fix funciona ✅" -ForegroundColor White
Write-Host "   2. Si TEST 2 failed por timeout → Investigar auto-apply script" -ForegroundColor White
Write-Host "   3. Si TEST 2 passed → TODO FUNCIONA PERFECTO 🎉`n" -ForegroundColor White

Write-Host "================================================================`n" -ForegroundColor Cyan
