# =====================================================
# ORGANIZADOR AUTOMÁTICO - AI JOB FOUNDRY
# =====================================================
# Organiza archivos sueltos en la raíz del proyecto

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ORGANIZANDO PROYECTO AI JOB FOUNDRY" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$raiz = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $raiz

# =====================================================
# CREAR CARPETAS SI NO EXISTEN
# =====================================================

$carpetas = @(
    "scripts\tests",
    "scripts\maintenance", 
    "docs\audit",
    "docs\session_reports"
)

foreach ($carpeta in $carpetas) {
    $path = Join-Path $raiz $carpeta
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "[+] Creada: $carpeta" -ForegroundColor Green
    }
}

# =====================================================
# MOVER ARCHIVOS - TESTS
# =====================================================

Write-Host ""
Write-Host ">>> Organizando TESTS..." -ForegroundColor Yellow

$tests = @(
    "TEST_FITSCORE_FIX.py",
    "DEBUG_SCRAPERS.py",
    "ANALYZE_SHEETS.py"
)

foreach ($file in $tests) {
    if (Test-Path $file) {
        Move-Item $file "scripts\tests\" -Force
        Write-Host "  [OK] $file -> scripts\tests\" -ForegroundColor Green
    }
}

# =====================================================
# MOVER ARCHIVOS - FIXES
# =====================================================

Write-Host ""
Write-Host ">>> Organizando FIXES..." -ForegroundColor Yellow

$fixFiles = @(
    "FIX_AUTO_APPLY_PIPELINE.py",
    "FIX_BULLETIN_QUERY.py", 
    "FIX_DASHBOARD_OPTION.py",
    "PATCH_CONTROL_CENTER.py",
    "RESTORE_SAFE.py"
)

foreach ($file in $fixFiles) {
    if (Test-Path $file) {
        Move-Item $file "fixes\" -Force
        Write-Host "  [OK] $file -> fixes\" -ForegroundColor Green
    }
}

# =====================================================
# MOVER ARCHIVOS - MAINTENANCE
# =====================================================

Write-Host ""
Write-Host ">>> Organizando MAINTENANCE..." -ForegroundColor Yellow

$maintenance = @(
    "mark_all_negatives.py",
    "mark_expired_jobs.py",
    "recalculate_fit_scores.py",
    "standardize_status.py",
    "standardize_status_v2.py",
    "standardize_status_v3.py",
    "update_status_from_emails.py",
    "verify_job_status.py",
    "check_oauth_token.py",
    "process_bulletins.py"
)

foreach ($file in $maintenance) {
    if (Test-Path $file) {
        Move-Item $file "scripts\maintenance\" -Force
        Write-Host "  [OK] $file -> scripts\maintenance\" -ForegroundColor Green
    }
}

# =====================================================
# MOVER ARCHIVOS - DOCUMENTATION
# =====================================================

Write-Host ""
Write-Host ">>> Organizando DOCUMENTATION..." -ForegroundColor Yellow

$docs = @(
    "AUDITORIA_COMPLETA.md",
    "AUDITORIA_PROYECTO_02DIC2025.md",
    "DIAGNOSTICO_COMPLETO_02DIC.md",
    "INDICE_AUDITORIA.txt",
    "INDICE_DIAGNOSTIC.txt",
    "RESUMEN_EJECUTIVO_AUDITORIA.md",
    "RESUMEN_EJECUTIVO_DIAGNOSTIC.md"
)

foreach ($file in $docs) {
    if (Test-Path $file) {
        Move-Item $file "docs\audit\" -Force
        Write-Host "  [OK] $file -> docs\audit\" -ForegroundColor Green
    }
}

# =====================================================
# MOVER ARCHIVOS - SESSION REPORTS
# =====================================================

Write-Host ""
Write-Host ">>> Organizando SESSION REPORTS..." -ForegroundColor Yellow

$reports = @(
    "RESUMEN_SESION_2025-12-02.md"
)

foreach ($file in $reports) {
    if (Test-Path $file) {
        Move-Item $file "docs\session_reports\" -Force
        Write-Host "  [OK] $file -> docs\session_reports\" -ForegroundColor Green
    }
}

# =====================================================
# ARCHIVOS QUE SE QUEDAN EN LA RAÍZ
# =====================================================

Write-Host ""
Write-Host ">>> Archivos que permanecen en RAÍZ:" -ForegroundColor Cyan
Write-Host "  [OK] PROJECT_STATUS.md (referencia principal)" -ForegroundColor Gray
Write-Host "  [OK] MASTER_FEATURE_ROADMAP.md (roadmap)" -ForegroundColor Gray
Write-Host "  [OK] README.md (documentación)" -ForegroundColor Gray
Write-Host "  [OK] requirements.txt (dependencias)" -ForegroundColor Gray
Write-Host "  [OK] control_center.py (launcher principal)" -ForegroundColor Gray
Write-Host "  [OK] run_daily_pipeline.py (pipeline principal)" -ForegroundColor Gray
Write-Host "  [OK] *.bat (scripts de inicio)" -ForegroundColor Gray
Write-Host "  [OK] .env, .gitignore, etc (config)" -ForegroundColor Gray

# =====================================================
# RESUMEN
# =====================================================

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ORGANIZACION COMPLETADA" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Nueva estructura:" -ForegroundColor Yellow
Write-Host "  scripts\tests\         - Scripts de prueba" -ForegroundColor White
Write-Host "  scripts\maintenance\   - Scripts de mantenimiento" -ForegroundColor White
Write-Host "  fixes\                 - Scripts de correccion" -ForegroundColor White
Write-Host "  docs\audit\            - Auditorias y diagnosticos" -ForegroundColor White
Write-Host "  docs\session_reports\  - Reportes de sesiones" -ForegroundColor White
Write-Host ""
