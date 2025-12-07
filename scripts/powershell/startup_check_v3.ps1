#!/usr/bin/env powershell
<#
.SYNOPSIS
    Verifica servicios necesarios para AI Job Foundry
.DESCRIPTION
    Chequea servicios críticos y opcionales
#>

$ErrorActionPreference = "Continue"

function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-ColorOutput Cyan "================================================================"
Write-ColorOutput Cyan "    AI JOB FOUNDRY - STARTUP CHECK"
Write-ColorOutput Cyan "================================================================"
Write-Host ""

$allOk = $true
$warnings = @()

# ============================================================================
# 1. LM STUDIO CHECK
# ============================================================================
Write-Host "Checking LM Studio..." -NoNewline

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/v1/models" -Method GET -TimeoutSec 3 -ErrorAction Stop
    Write-ColorOutput Green " OK"
} catch {
    try {
        $response = Invoke-RestMethod -Uri "http://172.23.0.1:11434/v1/models" -Method GET -TimeoutSec 3 -ErrorAction Stop
        Write-ColorOutput Green " OK (alternate IP)"
    } catch {
        Write-ColorOutput Yellow " WARNING - Will use Gemini fallback"
        $warnings += "LM Studio not available"
    }
}

# ============================================================================
# 2. OAUTH TOKEN CHECK
# ============================================================================
Write-Host "Checking OAuth Token..." -NoNewline

$tokenPath = "data\credentials\token.json"

if (Test-Path $tokenPath) {
    Write-ColorOutput Green " OK"
} else {
    Write-ColorOutput Red " MISSING"
    Write-ColorOutput Yellow "  Run: py setup_oauth_helper.py"
    $allOk = $false
}

# ============================================================================
# 3. GOOGLE SHEETS CHECK
# ============================================================================
Write-Host "Checking Google Sheets ID..." -NoNewline

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match 'GOOGLE_SHEETS_ID=[\w\-]+') {
        Write-ColorOutput Green " OK"
    } else {
        Write-ColorOutput Yellow " WARNING - Not configured"
        $warnings += "Google Sheets ID not set in .env"
    }
} else {
    Write-ColorOutput Red " MISSING"
    $warnings += ".env file not found"
    $allOk = $false
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host ""
Write-ColorOutput Cyan "================================================================"

if ($allOk -and $warnings.Count -eq 0) {
    Write-ColorOutput Green "ALL SERVICES READY"
    Write-Host ""
    exit 0
} else {
    if ($warnings.Count -gt 0) {
        Write-ColorOutput Yellow "WARNINGS:"
        foreach ($warning in $warnings) {
            Write-ColorOutput Yellow "  - $warning"
        }
    }
    
    Write-Host ""
    
    if ($allOk) {
        Write-ColorOutput Yellow "SYSTEM PARTIALLY FUNCTIONAL"
        Write-Host ""
        exit 0
    } else {
        Write-ColorOutput Red "CRITICAL ERRORS DETECTED"
        Write-Host ""
        Write-ColorOutput Yellow "RECOMMENDED FIXES:"
        Write-ColorOutput Cyan "  1. OAuth: py setup_oauth_helper.py"
        Write-ColorOutput Cyan "  2. LM Studio: Start manually"
        Write-ColorOutput Cyan "  3. .env: Add GOOGLE_SHEETS_ID"
        Write-Host ""
        exit 1
    }
}
