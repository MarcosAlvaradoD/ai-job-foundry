# AI JOB FOUNDRY - Organizacion Segura
# Mueve documentacion de la raiz a sus ubicaciones correctas

Write-Host ""
Write-Host "AI JOB FOUNDRY - ORGANIZACION SEGURA" -ForegroundColor Cyan
Write-Host ""

$root = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $root

# Mover MASTER_FEATURE_ROADMAP.md a docs/
if (Test-Path "MASTER_FEATURE_ROADMAP.md") {
    Write-Host "[MOVE] MASTER_FEATURE_ROADMAP.md -> docs/" -ForegroundColor Yellow
    Move-Item "MASTER_FEATURE_ROADMAP.md" "docs\MASTER_FEATURE_ROADMAP.md" -Force
    Write-Host "       OK" -ForegroundColor Green
}

# Mover PROMPT_COMPACTO.md a docs/prompts/
if (Test-Path "PROMPT_COMPACTO.md") {
    Write-Host "[MOVE] PROMPT_COMPACTO.md -> docs\prompts\" -ForegroundColor Yellow
    Move-Item "PROMPT_COMPACTO.md" "docs\prompts\PROMPT_COMPACTO.md" -Force
    Write-Host "       OK" -ForegroundColor Green
}

# Comparar PROJECT_STATUS.md (duplicado)
if (Test-Path "PROJECT_STATUS.md") {
    $rootStatus = Get-Content "PROJECT_STATUS.md" -Raw
    $docsStatus = Get-Content "docs\PROJECT_STATUS.md" -Raw
    
    if ($rootStatus -eq $docsStatus) {
        Write-Host "[DELETE] PROJECT_STATUS.md (duplicado exacto)" -ForegroundColor Yellow
        Remove-Item "PROJECT_STATUS.md" -Force
        Write-Host "         OK" -ForegroundColor Green
    }
}

# Comparar PROMPT_NUEVO_CHAT.md (posible duplicado)
if (Test-Path "PROMPT_NUEVO_CHAT.md") {
    $rootPrompt = Get-Content "PROMPT_NUEVO_CHAT.md" -Raw
    $docsPrompt = Get-Content "docs\prompts\PROMPT_NUEVO_CHAT.md" -Raw
    
    if ($rootPrompt -eq $docsPrompt) {
        Write-Host "[DELETE] PROMPT_NUEVO_CHAT.md (duplicado exacto)" -ForegroundColor Yellow
        Remove-Item "PROMPT_NUEVO_CHAT.md" -Force
        Write-Host "         OK" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] PROMPT_NUEVO_CHAT.md (contenido diferente)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "VERIFICANDO LAUNCHERS..." -ForegroundColor Cyan
Write-Host ""

$launchers = @("START_CONTROL_CENTER.bat", "START_WEB_APP.bat", "START_UNIFIED_APP.bat")

foreach ($launcher in $launchers) {
    if (Test-Path $launcher) {
        Write-Host "[OK] $launcher" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $launcher NO ENCONTRADO" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "ORGANIZACION COMPLETADA" -ForegroundColor Green
Write-Host ""
