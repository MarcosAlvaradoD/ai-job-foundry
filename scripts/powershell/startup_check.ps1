#!/usr/bin/env powershell
<#
.SYNOPSIS
    Verifica que todos los servicios necesarios estén corriendo
.DESCRIPTION
    Chequea LM Studio, Docker, y OAuth antes de permitir usar Control Center
.EXAMPLE
    .\startup_check.ps1
#>

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "`n" -NoNewline
Write-ColorOutput Cyan "════════════════════════════════════════════════════════════════════"
Write-ColorOutput Cyan "           🚀 AI JOB FOUNDRY - STARTUP CHECK"
Write-ColorOutput Cyan "════════════════════════════════════════════════════════════════════"
Write-Host ""

$allOk = $true
$warnings = @()

# ============================================================================
# 1. VERIFICAR LM STUDIO
# ============================================================================
Write-Host "🤖 Verificando LM Studio..." -NoNewline

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/v1/models" -Method GET -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput Green " ✅ ONLINE"
        Write-Host "   └─ URL: http://127.0.0.1:11434" -ForegroundColor Gray
    }
} catch {
    Write-ColorOutput Red " ❌ OFFLINE"
    Write-ColorOutput Yellow "   └─ LM Studio no está corriendo o no responde"
    Write-ColorOutput Yellow "   └─ Por favor inicia LM Studio manualmente"
    Write-Host "   └─ Esperando 30 segundos para que inicies LM Studio..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
    
    # Retry
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/v1/models" -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput Green "   └─ ✅ ONLINE después de esperar"
        }
    } catch {
        Write-ColorOutput Red "   └─ ❌ Aún OFFLINE - Continuando sin AI local"
        $warnings += "⚠️  LM Studio no disponible - usará Gemini fallback"
        $allOk = $false
    }
}

# ============================================================================
# 2. VERIFICAR DOCKER (opcional - para n8n)
# ============================================================================
Write-Host "`n🐳 Verificando Docker..." -NoNewline

try {
    $dockerStatus = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green " ✅ CORRIENDO"
        
        # Check for n8n container
        $n8nRunning = docker ps --filter "name=n8n" --format "{{.Names}}" 2>$null
        if ($n8nRunning) {
            Write-Host "   └─ n8n: ✅ ONLINE" -ForegroundColor Gray
        } else {
            Write-Host "   └─ n8n: ⚠️  NO ENCONTRADO (opcional)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-ColorOutput Yellow " ⚠️  NO DISPONIBLE"
    Write-Host "   └─ Docker Desktop no está corriendo (opcional)" -ForegroundColor Gray
    $warnings += "⚠️  Docker no disponible - n8n workflows no funcionarán"
}

# ============================================================================
# 3. VERIFICAR OAUTH TOKEN
# ============================================================================
Write-Host "`n🔐 Verificando OAuth Token..." -NoNewline

$tokenPath = "data\credentials\token.json"
$credsPath = "data\credentials\credentials.json"

if (Test-Path $tokenPath) {
    try {
        $tokenContent = Get-Content $tokenPath -Raw | ConvertFrom-Json
        
        # Check if token has required fields
        if ($tokenContent.refresh_token -and $tokenContent.client_id) {
            Write-ColorOutput Green " ✅ VÁLIDO"
            Write-Host "   └─ Token encontrado en: $tokenPath" -ForegroundColor Gray
        } else {
            Write-ColorOutput Yellow " ⚠️  INCOMPLETO"
            Write-Host "   └─ Token parece inválido o corrupto" -ForegroundColor Yellow
            $warnings += "⚠️  Token OAuth puede estar corrupto"
        }
    } catch {
        Write-ColorOutput Yellow " ⚠️  ERROR AL LEER"
        Write-Host "   └─ No se pudo parsear token.json" -ForegroundColor Yellow
        $warnings += "⚠️  Token OAuth no se pudo leer"
    }
} else {
    Write-ColorOutput Red " ❌ NO ENCONTRADO"
    Write-Host "   └─ Token no existe en: $tokenPath" -ForegroundColor Red
    
    if (Test-Path $credsPath) {
        Write-ColorOutput Yellow "   └─ credentials.json encontrado - puedes re-autenticar"
        Write-Host ""
        Write-ColorOutput Yellow "   📝 EJECUTA AHORA:"
        Write-ColorOutput Cyan "      py reauthenticate_gmail.py"
        Write-Host ""
        $response = Read-Host "   ¿Ejecutar re-autenticación ahora? (s/n)"
        if ($response -eq 's' -or $response -eq 'S') {
            Write-Host ""
            py reauthenticate_gmail.py
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput Green "   └─ ✅ Re-autenticación exitosa"
            } else {
                Write-ColorOutput Red "   └─ ❌ Re-autenticación falló"
                $allOk = $false
            }
        } else {
            $warnings += "❌ OAuth no configurado - Gmail/Sheets NO funcionarán"
            $allOk = $false
        }
    } else {
        Write-ColorOutput Red "   └─ credentials.json tampoco encontrado"
        Write-Host "   └─ Necesitas configurar OAuth desde Google Cloud Console" -ForegroundColor Red
        $warnings += "❌ OAuth no configurado - Gmail/Sheets NO funcionarán"
        $allOk = $false
    }
}

# ============================================================================
# 4. VERIFICAR GOOGLE SHEETS ACCESS
# ============================================================================
Write-Host "`n📊 Verificando acceso a Google Sheets..." -NoNewline

# Check if .env has GOOGLE_SHEETS_ID
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match 'GOOGLE_SHEETS_ID=[\w\-]+') {
        Write-ColorOutput Green " ✅ CONFIGURADO"
        Write-Host "   └─ Sheet ID encontrado en .env" -ForegroundColor Gray
    } else {
        Write-ColorOutput Yellow " ⚠️  NO ENCONTRADO"
        Write-Host "   └─ GOOGLE_SHEETS_ID no está en .env" -ForegroundColor Yellow
        $warnings += "⚠️  Google Sheets ID no configurado"
    }
} else {
    Write-ColorOutput Red " ❌ .env NO ENCONTRADO"
    $warnings += "❌ Archivo .env no existe"
    $allOk = $false
}

# ============================================================================
# RESUMEN
# ============================================================================
Write-Host ""
Write-ColorOutput Cyan "════════════════════════════════════════════════════════════════════"

if ($allOk -and $warnings.Count -eq 0) {
    Write-ColorOutput Green "✅ TODOS LOS SERVICIOS ESTÁN LISTOS"
    Write-ColorOutput Cyan "════════════════════════════════════════════════════════════════════"
    Write-Host ""
    Write-ColorOutput Green "🚀 Puedes ejecutar Control Center:"
    Write-ColorOutput Cyan "   py control_center.py"
    Write-Host ""
    exit 0
} else {
    if ($warnings.Count -gt 0) {
        Write-ColorOutput Yellow "`n⚠️  ADVERTENCIAS:"
        foreach ($warning in $warnings) {
            Write-ColorOutput Yellow "   $warning"
        }
    }
    
    Write-ColorOutput Cyan "`n════════════════════════════════════════════════════════════════════"
    
    if ($allOk) {
        Write-ColorOutput Yellow "⚠️  SISTEMA PARCIALMENTE FUNCIONAL"
        Write-ColorOutput Cyan "════════════════════════════════════════════════════════════════════"
        Write-Host ""
        Write-ColorOutput Yellow "Puedes continuar pero algunas funciones pueden no funcionar."
        Write-Host ""
        $response = Read-Host "¿Continuar de todas formas? (s/n)"
        if ($response -eq 's' -or $response -eq 'S') {
            Write-Host ""
            Write-ColorOutput Cyan "🚀 Iniciando Control Center..."
            py control_center.py
        } else {
            Write-Host ""
            Write-ColorOutput Yellow "👋 Saliendo. Por favor arregla los problemas primero."
            Write-Host ""
        }
    } else {
        Write-ColorOutput Red "❌ SISTEMA NO FUNCIONAL"
        Write-ColorOutput Cyan "════════════════════════════════════════════════════════════════════"
        Write-Host ""
        Write-ColorOutput Red "Por favor arregla los errores críticos antes de continuar:"
        Write-Host ""
        Write-ColorOutput Yellow "1. Si OAuth falla:"
        Write-ColorOutput Cyan "   py reauthenticate_gmail.py"
        Write-Host ""
        Write-ColorOutput Yellow "2. Si LM Studio no inicia:"
        Write-ColorOutput Cyan "   Abre LM Studio manualmente y carga el modelo"
        Write-Host ""
        Write-ColorOutput Yellow "3. Si .env falta:"
        Write-ColorOutput Cyan "   Copia .env.example a .env y llénalo"
        Write-Host ""
        exit 1
    }
}
