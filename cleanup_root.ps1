#!/usr/bin/env powershell
<#
.SYNOPSIS
    Organiza archivos obsoletos/fuera de lugar en la raíz del proyecto
.DESCRIPTION
    Mueve archivos a archive/ y logs/ según corresponda
.EXAMPLE
    .\cleanup_root.ps1
#>

$ErrorActionPreference = "Stop"
Write-Host "`n🧹 LIMPIEZA DE RAÍZ DEL PROYECTO" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host ("="*50) -ForegroundColor Cyan

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path "control_center.py")) {
    Write-Host "❌ ERROR: No estás en la raíz de ai-job-foundry" -ForegroundColor Red
    exit 1
}

# Crear directorios si no existen
$archiveDir = "archive\old_configs"
$logsDir = "logs"

if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    Write-Host "📁 Creado: $archiveDir" -ForegroundColor Green
}

# Archivos a mover
$filesToMove = @(
    @{
        Source = "config.json"
        Dest = "$archiveDir\config.json.backup"
        Reason = "Configuración obsoleta (usa config\devfoundry.yaml)"
    },
    @{
        Source = "PLANE_SETUP_PROMPT.md"
        Dest = "archive\PLANE_SETUP_PROMPT.md"
        Reason = "No relacionado con AI Job Foundry"
    },
    @{
        Source = "ingest.log"
        Dest = "$logsDir\ingest.log"
        Reason = "Log debe estar en logs/"
    }
)

Write-Host "`n📦 ARCHIVOS A PROCESAR:" -ForegroundColor Yellow
Write-Host ""

$moved = 0
$skipped = 0

foreach ($file in $filesToMove) {
    $source = $file.Source
    $dest = $file.Dest
    $reason = $file.Reason
    
    if (Test-Path $source) {
        Write-Host "🔄 Moviendo: $source" -ForegroundColor Cyan
        Write-Host "   → $dest" -ForegroundColor Gray
        Write-Host "   Razón: $reason" -ForegroundColor Gray
        
        # Crear directorio destino si no existe
        $destDir = Split-Path $dest -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        # Mover archivo
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "   ✅ Movido" -ForegroundColor Green
        $moved++
    }
    else {
        Write-Host "⏭️  Saltado: $source (no existe)" -ForegroundColor Yellow
        $skipped++
    }
    Write-Host ""
}

Write-Host "`n📊 RESUMEN:" -ForegroundColor Cyan
Write-Host "   Archivos movidos: $moved" -ForegroundColor Green
Write-Host "   Archivos saltados: $skipped" -ForegroundColor Yellow

Write-Host "`n✅ LIMPIEZA COMPLETA" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host ("="*50) -ForegroundColor Cyan

Write-Host "`n💡 TIP: Los archivos movidos se pueden recuperar de archive/" -ForegroundColor Gray
Write-Host ""
