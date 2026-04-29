# ======================================================================
# AI JOB FOUNDRY - Project Organization Script
# ======================================================================
# Organiza archivos de la raíz a sus ubicaciones correctas
# Autor: Marcos Alberto Alvarado
# Fecha: 2026-01-18
# ======================================================================

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "  AI JOB FOUNDRY - PROJECT ORGANIZER" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the project root
if (-not (Test-Path "core")) {
    Write-Host "ERROR: Not in project root. Navigate to ai-job-foundry/" -ForegroundColor Red
    exit 1
}

$organized = 0
$skipped = 0

# ======================================================================
# CATEGORY 1: PowerShell Scripts → scripts/powershell/
# ======================================================================

Write-Host "`n[1] PowerShell Scripts..." -ForegroundColor Cyan

$psScripts = @(
    "CLEANUP_FINAL.ps1",
    "CLEAN_INDEED_INVALID.ps1",
    "DECISION_RAPIDA.ps1",
    "detect_lm_studio_ip.ps1",
    "DIAGNOSTICO_COMPLETO.ps1",
    "DIAGNOSTICO_GPU.ps1",
    "INSTALL_ARCHIVOS.ps1",
    "install_oauth_validator.ps1",
    "LEER_PRIMERO.ps1",
    "ORGANIZE_FILES_AUTO.ps1",
    "ORGANIZE_FINAL.ps1",
    "ORGANIZE_PROJECT_AUTO.ps1",
    "ORGANIZE_ROOT_SAFE.ps1",
    "push_to_github.ps1",
    "REINICIO_LIMPIO.ps1",
    "REPARACION_OAUTH_EXPIRE.ps1",
    "run_daily_cleanup.ps1",
    "start_all.ps1",
    "START_CONTROL_CENTER_BYPASS.ps1",
    "TEST_CONTROL_CENTER.ps1",
    "test_linkedin_autoapply.ps1",
    "TEST_OAUTH_FLOW.ps1",
    "TEST_OAUTH_REAUTH.ps1",
    "TEST_OAUTH_VALIDATOR.ps1",
    "TEST_PIPELINE_FIX.ps1",
    "VERIFICAR_VRAM_NVIDIA.ps1",
    "VERIFY_PATHS.ps1"
)

foreach ($script in $psScripts) {
    if (Test-Path $script) {
        Move-Item $script "scripts/powershell/" -Force
        Write-Host "  Moved: $script" -ForegroundColor Green
        $organized++
    }
}

# ======================================================================
# CATEGORY 2: Batch Scripts → scripts/batch/
# ======================================================================

Write-Host "`n[2] Batch Scripts..." -ForegroundColor Cyan

$batScripts = @(
    "auto_start_NO_PASSWORD.bat",
    "START_CONTROL_CENTER.bat",
    "START_UNIFIED_APP.bat",
    "START_UNIFIED_APP.bat.backup_20251208_015420",
    "START_WEB_APP.bat"
)

foreach ($script in $batScripts) {
    if (Test-Path $script) {
        Move-Item $script "scripts/batch/" -Force
        Write-Host "  Moved: $script" -ForegroundColor Green
        $organized++
    }
}

# ======================================================================
# CATEGORY 3: Documentation → docs/
# ======================================================================

Write-Host "`n[3] Documentation..." -ForegroundColor Cyan

$docs = @(
    "CHECKLIST_EJECUCION.md",
    "COMPARATIVA_LAUNCHERS.md",
    "EJECUTAR_AHORA.md",
    "FIX_RESUMEN.md",
    "GUIA_RH_IT_HOME.md",
    "GUIA_UBICACION_ARCHIVOS.md",
    "PROXIMOS_PASOS.md",
    "REORGANIZACION_PROYECTO.md",
    "RESUMEN_EJECUTIVO_REORGANIZACION.md",
    "RESUMEN_FINAL_ACCIONES.md",
    "RESUMEN_FINAL_SESION_20251212.md",
    "SESION_COMPLETA_2025-12-20.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Move-Item $doc "docs/" -Force
        Write-Host "  Moved: $doc" -ForegroundColor Green
        $organized++
    }
}

# ======================================================================
# CATEGORY 4: Backups → archive/backups/
# ======================================================================

Write-Host "`n[4] Backup Files..." -ForegroundColor Cyan

$backups = @(
    "control_center.py.backup_20251211_233644"
)

foreach ($backup in $backups) {
    if (Test-Path $backup) {
        Move-Item $backup "archive/backups/" -Force
        Write-Host "  Moved: $backup" -ForegroundColor Green
        $organized++
    }
}

# ======================================================================
# CATEGORY 5: Temporary/Debug Files → archive/temp/ (or delete)
# ======================================================================

Write-Host "`n[5] Temporary Files..." -ForegroundColor Cyan

# Create temp folder if not exists
if (-not (Test-Path "archive/temp")) {
    New-Item -ItemType Directory -Path "archive/temp" -Force | Out-Null
}

$tempFiles = @(
    "debug_glassdoor_email.html",
    "ingest.log"
)

foreach ($file in $tempFiles) {
    if (Test-Path $file) {
        Move-Item $file "archive/temp/" -Force
        Write-Host "  Moved: $file" -ForegroundColor Yellow
        $organized++
    }
}

# ======================================================================
# CATEGORY 6: Old Folders → archive/
# ======================================================================

Write-Host "`n[6] Old Directories..." -ForegroundColor Cyan

$oldDirs = @(
    "backup_20251117_030702",
    "build",
    "dist",
    "TEST",
    "fixes"
)

foreach ($dir in $oldDirs) {
    if (Test-Path $dir) {
        Move-Item $dir "archive/" -Force
        Write-Host "  Moved: $dir/" -ForegroundColor Yellow
        $organized++
    }
}

# ======================================================================
# SUMMARY
# ======================================================================

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "  ORGANIZATION COMPLETE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Files organized: $organized" -ForegroundColor Green
Write-Host "  Files skipped:   $skipped" -ForegroundColor Yellow
Write-Host ""

# ======================================================================
# REMAINING FILES IN ROOT (EXPECTED)
# ======================================================================

Write-Host "  Expected files remaining in root:" -ForegroundColor Cyan
Write-Host "    Core Python:" -ForegroundColor White
Write-Host "      - control_center.py" -ForegroundColor Gray
Write-Host "      - main.py" -ForegroundColor Gray
Write-Host "      - oauth_token_validator.py" -ForegroundColor Gray
Write-Host "      - paths.py" -ForegroundColor Gray
Write-Host "      - run_daily_pipeline.py" -ForegroundColor Gray
Write-Host "      - run_linkedin_workflow.py" -ForegroundColor Gray
Write-Host "      - test_linkedin_notifications.py" -ForegroundColor Gray
Write-Host ""
Write-Host "    Launchers:" -ForegroundColor White
Write-Host "      - RUN_LINKEDIN_WORKFLOW.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "    Documentation:" -ForegroundColor White
Write-Host "      - README.md" -ForegroundColor Gray
Write-Host "      - PROJECT_STATUS.md" -ForegroundColor Gray
Write-Host "      - PROMPT_NUEVO_CHAT.md" -ForegroundColor Gray
Write-Host "      - LINKEDIN_WORKFLOW_QUICKSTART.md" -ForegroundColor Gray
Write-Host ""
Write-Host "    Configuration:" -ForegroundColor White
Write-Host "      - .env" -ForegroundColor Gray
Write-Host "      - .gitignore" -ForegroundColor Gray
Write-Host "      - requirements.txt" -ForegroundColor Gray
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""
