# =============================================================================
# 🧪 TEST RÁPIDO - OAuth Token Validator (Flujo Automático)
# =============================================================================
# Este script prueba el flujo automático completo:
# 1. Detecta token expirado
# 2. Abre navegador automáticamente
# 3. Espera que autorices
# 4. Verifica que funciona
# 5. Continúa solo si todo OK
#
# Uso: .\TEST_OAUTH_FLOW.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🧪 TEST - OAuth Token Validator (Flujo Automático)" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Write-Host "Este test simula el flujo completo del pipeline:" -ForegroundColor Yellow
Write-Host "1. Detecta si el token está expirado" -ForegroundColor White
Write-Host "2. Si está expirado → Abre navegador AUTOMÁTICAMENTE" -ForegroundColor White
Write-Host "3. Espera que completes la autorización" -ForegroundColor White
Write-Host "4. Verifica que el nuevo token funciona" -ForegroundColor White
Write-Host "5. Solo entonces continúa" -ForegroundColor White
Write-Host ""

$response = Read-Host "¿Continuar con el test? (Y/N)"
if ($response -ne "Y" -and $response -ne "y") {
    Write-Host "Test cancelado" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "PASO 1: Validar Token OAuth" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Ejecutar validador
py oauth_token_validator.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "✅ TOKEN VALIDADO CORRECTAMENTE" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 El sistema está listo para ejecutar el pipeline" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "1. Ejecuta: py main.py" -ForegroundColor Cyan
    Write-Host "2. O usa: py control_center.py (Opción 1)" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host "❌ VALIDACIÓN FALLÓ" -ForegroundColor Red
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Posibles soluciones:" -ForegroundColor Yellow
    Write-Host "1. Ejecuta manualmente: py scripts\oauth\reauthenticate_gmail_v2.py" -ForegroundColor White
    Write-Host "2. Verifica que credentials.json existe en data\credentials\" -ForegroundColor White
    Write-Host "3. Asegúrate de completar la autorización en el navegador" -ForegroundColor White
    Write-Host ""
}
