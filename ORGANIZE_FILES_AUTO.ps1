Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ORGANIZACIÓN AUTOMÁTICA DE ARCHIVOS - AI JOB FOUNDRY" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\MSI\Desktop\ai-job-foundry"

# Function to move file safely
function Move-FileSafely {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (Test-Path $Source) {
        $destDir = Split-Path -Parent $Destination
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            Write-Host "  📁 Created directory: $destDir" -ForegroundColor Yellow
        }
        
        if (Test-Path $Destination) {
            Write-Host "  ⚠️  File already exists: $(Split-Path -Leaf $Destination)" -ForegroundColor Yellow
            Write-Host "     Skipping..." -ForegroundColor Gray
        } else {
            Move-Item -Path $Source -Destination $Destination -Force
            Write-Host "  ✅ Moved: $(Split-Path -Leaf $Source) → $destDir" -ForegroundColor Green
        }
    } else {
        Write-Host "  ℹ️  Source not found: $(Split-Path -Leaf $Source)" -ForegroundColor Gray
    }
}

# Create necessary directories
Write-Host "[1/3] Creating necessary directories..." -ForegroundColor Cyan
$directories = @(
    "$ProjectRoot\docs\research",
    "$ProjectRoot\scripts\maintenance",
    "$ProjectRoot\scripts\tests",
    "$ProjectRoot\archive\backups"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Already exists: $dir" -ForegroundColor Gray
    }
}

# Move files to correct locations
Write-Host "`n[2/3] Moving files to correct locations..." -ForegroundColor Cyan

# Research documents
Write-Host "`n📚 Research Documents:" -ForegroundColor White
Move-FileSafely -Source "$ProjectRoot\ANALISIS_MODELOS_NUEVOS_DIC2025.md" -Destination "$ProjectRoot\docs\research\ANALISIS_MODELOS_NUEVOS_DIC2025.md"
Move-FileSafely -Source "$ProjectRoot\GUIA_CAMBIO_MODELO_LLAMA3GROQ.md" -Destination "$ProjectRoot\docs\research\GUIA_CAMBIO_MODELO_LLAMA3GROQ.md"
Move-FileSafely -Source "$ProjectRoot\RESUMEN_EJECUTIVO_CAMBIO_MODELO.md" -Destination "$ProjectRoot\docs\research\RESUMEN_EJECUTIVO_CAMBIO_MODELO.md"

# Fix documents
Write-Host "`n🔧 Fix Documents:" -ForegroundColor White
Move-FileSafely -Source "$ProjectRoot\FIX_OAUTH_SCOPES.md" -Destination "$ProjectRoot\docs\FIX_OAUTH_SCOPES.md"
Move-FileSafely -Source "$ProjectRoot\FIX_UNICODE_EXPIRE.md" -Destination "$ProjectRoot\docs\FIX_UNICODE_EXPIRE.md"
Move-FileSafely -Source "$ProjectRoot\ESTRUCTURA_ARCHIVOS_DEFINITIVA.md" -Destination "$ProjectRoot\docs\ESTRUCTURA_ARCHIVOS_DEFINITIVA.md"

# Maintenance scripts
Write-Host "`n🔧 Maintenance Scripts:" -ForegroundColor White
Move-FileSafely -Source "$ProjectRoot\fix_unicode_expire.py" -Destination "$ProjectRoot\scripts\maintenance\fix_unicode_expire.py"

# Test scripts
Write-Host "`n🧪 Test Scripts:" -ForegroundColor White
Move-FileSafely -Source "$ProjectRoot\test_single_job.py" -Destination "$ProjectRoot\scripts\tests\test_single_job.py"

# Old/backup files
Write-Host "`n📦 Backup Files:" -ForegroundColor White
Move-FileSafely -Source "$ProjectRoot\RESUMEN_FINAL_SESION.md" -Destination "$ProjectRoot\archive\backups\RESUMEN_FINAL_SESION_$(Get-Date -Format 'yyyyMMdd').md"
Move-FileSafely -Source "$ProjectRoot\SEGURIDAD_CREDENCIALES.md" -Destination "$ProjectRoot\docs\SEGURIDAD_CREDENCIALES.md"

# Verify critical files exist
Write-Host "`n[3/3] Verifying critical files..." -ForegroundColor Cyan

$criticalFiles = @{
    ".env" = "$ProjectRoot\.env"
    "PROJECT_STATUS.md" = "$ProjectRoot\PROJECT_STATUS.md"
    "control_center.py" = "$ProjectRoot\control_center.py"
    "run_daily_pipeline.py" = "$ProjectRoot\run_daily_pipeline.py"
}

$allPresent = $true
foreach ($file in $criticalFiles.GetEnumerator()) {
    if (Test-Path $file.Value) {
        Write-Host "  ✅ $($file.Key)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ MISSING: $($file.Key)" -ForegroundColor Red
        $allPresent = $false
    }
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
if ($allPresent) {
    Write-Host "  ✅ ORGANIZACIÓN COMPLETADA" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  ORGANIZACIÓN COMPLETADA CON ADVERTENCIAS" -ForegroundColor Yellow
}
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host "`nArchivos ahora en:" -ForegroundColor White
Write-Host "  📁 docs\research\               - Análisis de modelos" -ForegroundColor Gray
Write-Host "  📁 docs\                        - Guías de fix" -ForegroundColor Gray
Write-Host "  📁 scripts\maintenance\         - Scripts de mantenimiento" -ForegroundColor Gray
Write-Host "  📁 scripts\tests\               - Scripts de testing" -ForegroundColor Gray
Write-Host "  📁 archive\backups\             - Backups antiguos" -ForegroundColor Gray

Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Lee: docs\research\RESUMEN_EJECUTIVO_CAMBIO_MODELO.md" -ForegroundColor White
Write-Host "  2. Fix OAuth: py scripts\oauth\reauthenticate_gmail.py" -ForegroundColor White
Write-Host "  3. Fix Unicode: py scripts\maintenance\fix_unicode_expire.py" -ForegroundColor White
Write-Host "  4. Test modelo: py scripts\tests\test_single_job.py" -ForegroundColor White

Write-Host "`nPress Enter to continue..." -ForegroundColor Gray -NoNewline
Read-Host
