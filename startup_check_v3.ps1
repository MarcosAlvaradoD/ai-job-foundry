#!/usr/bin/env powershell
<#
.SYNOPSIS
    Verifica servicios necesarios - VERSIÓN MEJORADA
.DESCRIPTION
    Chequea LM Studio, Docker, y OAuth con mejor error handling
.EXAMPLE
    .\startup_check_v3.ps1
#>

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "`n"
Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
Write-ColorOutput Cyan "       🚀 AI JOB FOUNDRY - STARTUP CHECK V3"
Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
Write-Host ""

$allOk = $true
$warnings = @()

# ============================================================================
# 1. LM STUDIO CHECK
# ============================================================================
Write-Host "🤖 Verificando LM Studio..." -NoNewline

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/v1/models" -Method GET -TimeoutSec 3 -ErrorAction Stop
    Write-ColorOutput Green " ✅ ONLINE"
    Write-Host "   └─ URL: http://127.0.0.1:11434" -ForegroundColor Gray
}
catch {
    Write-ColorOutput Red " ❌ OFFLINE"
    $warnings += "⚠️  LM Studio no disponible - usará Gemini fallback"
}

# ============================================================================
# 2. DOCKER CHECK
# ============================================================================
Write-Host "`n🐳 Verificando Docker..." -NoNewline

try {
    $null = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green " ✅ CORRIENDO"
        
        $n8nRunning = docker ps --filter "name=n8n" --format "{{.Names}}" 2>$null
        if ($n8nRunning) {
            Write-Host "   └─ n8n: ✅ ONLINE" -ForegroundColor Gray
        }
    }
}
catch {
    Write-ColorOutput Yellow " ⚠️  NO DISPONIBLE"
    $warnings += "⚠️  Docker no disponible (opcional)"
}

# ============================================================================
# 3. OAUTH TOKEN CHECK
# ============================================================================
Write-Host "`n🔐 Verificando OAuth Token..." -NoNewline

$tokenPath = "data\credentials\token.json"

if (Test-Path $tokenPath) {
    try {
        $tokenContent = Get-Content $tokenPath -Raw | ConvertFrom-Json
        
        if ($tokenContent.refresh_token -and $tokenContent.client_id) {
            Write-ColorOutput Green " ✅ VÁLIDO"
        }
        else {
            Write-ColorOutput Yellow " ⚠️  INCOMPLETO"
            $warnings += "⚠️  Token OAuth puede estar corrupto"
        }
    }
    catch {
        Write-ColorOutput Yellow " ⚠️  ERROR AL LEER"
        $warnings += "⚠️  Token OAuth no se pudo leer"
    }
}
else {
    Write-ColorOutput Red " ❌ NO ENCONTRADO"
    Write-Host ""
    Write-ColorOutput Yellow "   📝 EJECUTA AHORA:"
    Write-ColorOutput Cyan "      py fix_oauth_complete.py"
    Write-Host ""
    $warnings += "❌ OAuth no configurado - Gmail/Sheets NO funcionarán"
    $allOk = $false
}

# ============================================================================
# 4. GOOGLE SHEETS CHECK
# ============================================================================
Write-Host "`n📊 Verificando Google Sheets ID..." -NoNewline

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match 'GOOGLE_SHEETS_ID=[\w\-]+') {
        Write-ColorOutput Green " ✅ CONFIGURADO"
    }
    else {
        Write-ColorOutput Yellow " ⚠️  NO ENCONTRADO"
        $warnings += "⚠️  Google Sheets ID no configurado en .env"
    }
}
else {
    Write-ColorOutput Red " ❌ .env NO ENCONTRADO"
    $warnings += "❌ Archivo .env no existe"
    $allOk = $false
}

# ============================================================================
# RESUMEN
# ============================================================================
Write-Host ""
Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"

if ($allOk -and $warnings.Count -eq 0) {
    Write-ColorOutput Green "✅ TODOS LOS SERVICIOS ESTÁN LISTOS"
    Write-ColorOutput Cyan "═══════════════════════════════════════════════════════════"
    Write-Host ""
    Write-ColorOutput Green "🚀 Puedes ejecutar:"
    Write-ColorOutput Cyan "   py control_center.py"
    Write-Host ""
    exit 0
}
else {
    if ($warnings.Count -gt 0) {
        Write-ColorOutput Yellow "`n⚠️  ADVERTENCIAS:"
        foreach ($warning in $warnings) {
            Write-ColorOutput Yellow "   $warning"
        }
    }
    
    Write-ColorOutput Cyan "`n═══════════════════════════════════════════════════════════"
    
    if ($allOk) {
        Write-ColorOutput Yellow "⚠️  SISTEMA PARCIALMENTE FUNCIONAL"
        Write-Host ""
        Write-ColorOutput Yellow "Algunas funciones pueden no funcionar."
        Write-Host ""
    }
    else {
        Write-ColorOutput Red "❌ ERRORES CRÍTICOS DETECTADOS"
        Write-Host ""
        Write-ColorOutput Yellow "FIXES RECOMENDADOS:"
        Write-ColorOutput Cyan "   1. OAuth: py fix_oauth_complete.py"
        Write-ColorOutput Cyan "   2. LM Studio: Abrir manualmente"
        Write-ColorOutput Cyan "   3. .env: Copiar de .env.example"
        Write-Host ""
        exit 1
    }
}
