#!/usr/bin/env powershell
# AI Job Foundry - Startup Check (Simplified)
# Verifica servicios necesarios

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  AI JOB FOUNDRY - STARTUP CHECK" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$allOk = $true

# Check LM Studio
Write-Host "Checking LM Studio..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/v1/models" -Method GET -TimeoutSec 3
    if ($response.StatusCode -eq 200) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " OFFLINE" -ForegroundColor Yellow
        $allOk = $false
    }
} catch {
    Write-Host " OFFLINE" -ForegroundColor Yellow
    $allOk = $false
}

# Check OAuth
Write-Host "Checking OAuth token..." -NoNewline
if (Test-Path "data\credentials\token.json") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " MISSING" -ForegroundColor Red
    Write-Host "  Run: py fix_oauth_scopes.py" -ForegroundColor Yellow
    $allOk = $false
}

# Check Docker (optional)
Write-Host "Checking Docker..." -NoNewline
try {
    $dockerStatus = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " OFFLINE (optional)" -ForegroundColor Gray
    }
} catch {
    Write-Host " OFFLINE (optional)" -ForegroundColor Gray
}

Write-Host "`n================================================================" -ForegroundColor Cyan

if (-not $allOk) {
    Write-Host "WARNING: Some services are not available" -ForegroundColor Yellow
    Write-Host "Continue anyway? (y/n): " -NoNewline
    $continue = Read-Host
    if ($continue -ne 'y') {
        exit 1
    }
}

Write-Host "Startup check completed`n" -ForegroundColor Green
exit 0
