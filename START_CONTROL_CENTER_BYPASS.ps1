# ============================================================================
# START CONTROL CENTER - BYPASS CHECKS
# Para testing rapido - continua sin importar errores de startup check
# ============================================================================

Write-Host ""
Write-Host "AI JOB FOUNDRY - CONTROL CENTER (BYPASS MODE)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTA: Este launcher ignora errores de startup check" -ForegroundColor Yellow
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
py --version >$null 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Python disponible" -ForegroundColor Green
} else {
    Write-Host "ERROR - Python no encontrado" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Iniciando Control Center..." -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Ejecutar control center directamente (Python ya no usa cache si reiniciamos el proceso)
py control_center.py

pause
