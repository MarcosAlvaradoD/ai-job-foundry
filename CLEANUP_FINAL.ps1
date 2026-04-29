# AI JOB FOUNDRY - Limpieza Final
# Elimina duplicados y verifica archivos

Write-Host ""
Write-Host "AI JOB FOUNDRY - LIMPIEZA FINAL" -ForegroundColor Cyan
Write-Host ""

$root = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $root

# 1. Eliminar PROJECT_STATUS.md duplicado de raiz
if (Test-Path "PROJECT_STATUS.md") {
    Write-Host "[DELETE] PROJECT_STATUS.md (duplicado)" -ForegroundColor Yellow
    Remove-Item "PROJECT_STATUS.md" -Force
    Write-Host "         OK - Usar docs\PROJECT_STATUS.md" -ForegroundColor Green
}

# 2. Comparar PROMPT_NUEVO_CHAT.md
Write-Host ""
Write-Host "Comparando PROMPT_NUEVO_CHAT.md..." -ForegroundColor Cyan

if (Test-Path "PROMPT_NUEVO_CHAT.md") {
    $rootSize = (Get-Item "PROMPT_NUEVO_CHAT.md").Length
    $docsSize = (Get-Item "docs\prompts\PROMPT_NUEVO_CHAT.md").Length
    
    Write-Host "  Raiz: $rootSize bytes" -ForegroundColor Gray
    Write-Host "  Docs: $docsSize bytes" -ForegroundColor Gray
    
    if ($rootSize -ne $docsSize) {
        Write-Host ""
        Write-Host "[DECISION REQUERIDA]" -ForegroundColor Yellow
        Write-Host "Los archivos tienen diferente tamaño" -ForegroundColor Yellow
        Write-Host "Opciones:" -ForegroundColor White
        Write-Host "  1. Mantener raiz y eliminar docs/prompts/" -ForegroundColor Gray
        Write-Host "  2. Mantener docs/prompts/ y eliminar raiz" -ForegroundColor Gray
        Write-Host "  3. Dejar ambos por ahora" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Recomendacion: Opcion 2 (mantener en docs/prompts/)" -ForegroundColor Green
    }
}

# 3. Verificar estructura de directorios
Write-Host ""
Write-Host "ESTRUCTURA DE DIRECTORIOS:" -ForegroundColor Cyan
Write-Host ""

$dirs = @("core", "docs", "scripts", "data", "web_app", "unified_app")

foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "[OK] $dir\" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $dir\ NO ENCONTRADO" -ForegroundColor Red
    }
}

# 4. Listar archivos en raiz
Write-Host ""
Write-Host "ARCHIVOS EN RAIZ:" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem -File | Select-Object Name | Format-Table -AutoSize

Write-Host ""
Write-Host "LIMPIEZA COMPLETADA" -ForegroundColor Green
Write-Host ""
