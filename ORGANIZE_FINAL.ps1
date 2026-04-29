# ==============================================================================
# AI JOB FOUNDRY - ORGANIZACION FINAL DEL PROYECTO
# ==============================================================================
# Este script organiza todos los archivos dispersos en root
# sin romper referencias en archivos principales
# ==============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  AI JOB FOUNDRY - ORGANIZACION FINAL" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# ==============================================================================
# CREAR ESTRUCTURA DE DIRECTORIOS
# ==============================================================================

$directories = @(
    "scripts\tests",
    "scripts\batch",
    "scripts\verifiers",
    "data\samples",
    "data\templates",
    "archive\backups",
    "archive\old_versions",
    "docs\guides",
    "docs\session_reports"
)

Write-Host "[1/7] Creando estructura de directorios..." -ForegroundColor Yellow

foreach ($dir in $directories) {
    $fullPath = Join-Path $projectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -Path $fullPath -ItemType Directory -Force | Out-Null
        Write-Host "  [OK] Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  [EXISTS] $dir" -ForegroundColor Gray
    }
}

Write-Host ""

# ==============================================================================
# MOVER ARCHIVOS DE TEST/DEBUG A scripts/tests
# ==============================================================================

Write-Host "[2/7] Organizando archivos de test y debug..." -ForegroundColor Yellow

$testFiles = @(
    "TEST_BULLETIN_FIX.py",
    "TEST_EMAIL_REAL.py",
    "TEST_GLASSDOOR_PARSER.py",
    "TEST_GLASSDOOR_PARSER_FINAL.py",
    "DEBUG_BULLETIN_PROCESSOR.py",
    "DEBUG_JOB_ID.py",
    "CHECK_ALL_SHEETS.py",
    "CHECK_GLASSDOOR_JOBS.py",
    "INVESTIGATE_GLASSDOOR.py",
    "INVESTIGATE_GLASSDOOR_EMAILS.py",
    "INVESTIGATE_UNKNOWN_JOBS.py",
    "VERIFY_GLASSDOOR_URL.py",
    "ANALIZAR_EMAIL_GLASSDOOR.py",
    "ANALIZAR_SAMPLES.py",
    "ADD_SOURCE_TYPE_COLUMN.py",
    "MANUAL_ADD_SOURCE_TYPE.py",
    "DESCARGAR_EMAIL_REAL.py",
    "DESCARGAR_SAMPLES_FUENTES.py",
    "VER_EMAILS_BULLETINS.py",
    "VER_FUENTES_BOLETINES.py",
    "FIND_BEST_GLASSDOOR.py",
    "FIND_BEST_NEW_GLASSDOOR.py",
    "FIX_OAUTH_TOKEN.py"
)

foreach ($file in $testFiles) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "scripts\tests\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> scripts\tests\" -ForegroundColor Green
    }
}

Write-Host ""

# ==============================================================================
# MOVER VERIFIERS A scripts/verifiers
# ==============================================================================

Write-Host "[3/7] Organizando verifiers..." -ForegroundColor Yellow

$verifierFiles = @(
    "LINKEDIN_SMART_VERIFIER.py",
    "LINKEDIN_SMART_VERIFIER_V3.py",
    "GLASSDOOR_SMART_VERIFIER.py",
    "GLASSDOOR_BULK_VERIFIER.py",
    "INDEED_SMART_VERIFIER.py",
    "UNIVERSAL_JOB_VERIFIER.py",
    "DELETE_EXPIRED_JOBS.py",
    "EXPIRE_LIFECYCLE.py",
    "FIX_VERIFICACION_JOBS.py"
)

foreach ($file in $verifierFiles) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "scripts\verifiers\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> scripts\verifiers\" -ForegroundColor Green
    }
}

Write-Host ""

# ==============================================================================
# MOVER SAMPLES A data/samples
# ==============================================================================

Write-Host "[4/7] Organizando archivos sample..." -ForegroundColor Yellow

$sampleFiles = @(
    "ADZUNA_SAMPLE.html",
    "COMPUTRABAJO_SAMPLE.html",
    "GLASSDOOR_EMAIL_REAL.html",
    "GLASSDOOR_EMAIL_SAMPLE.html",
    "MARKALVA_SAMPLE.html",
    "ZIPRECRUITER_SAMPLE.html"
)

foreach ($file in $sampleFiles) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "data\samples\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> data\samples\" -ForegroundColor Green
    }
}

Write-Host ""

# ==============================================================================
# MOVER ARCHIVOS BAT A scripts/batch
# ==============================================================================

Write-Host "[5/7] Organizando scripts batch..." -ForegroundColor Yellow

$batFiles = @(
    "AUTO_START.bat",
    "BUILD_EXE.bat",
    "CLEANUP_ALL_JOBS.bat",
    "FIX_DEPENDENCIES.bat",
    "FIX_OAUTH_TOKEN.bat",
    "INSTALL_COMPLETE.bat",
    "PROCESS_ALL_EMAILS.bat",
    "RUN_FULL_DIAGNOSTIC.bat",
    "RUN_ORGANIZE_AND_FIX.bat",
    "UPDATE_STATUS_FROM_EMAILS.bat"
)

# ESTOS SE QUEDAN EN ROOT (son launchers principales)
$keepInRoot = @(
    "START_CONTROL_CENTER.bat",
    "START_WEB_APP.bat",
    "START_UNIFIED_APP.bat"
)

foreach ($file in $batFiles) {
    if ($file -notin $keepInRoot) {
        $source = Join-Path $projectRoot $file
        $dest = Join-Path $projectRoot "scripts\batch\$file"
        
        if (Test-Path $source) {
            Move-Item -Path $source -Destination $dest -Force
            Write-Host "  [MOVED] $file -> scripts\batch\" -ForegroundColor Green
        }
    }
}

Write-Host ""

# ==============================================================================
# MOVER DOCUMENTACION A docs
# ==============================================================================

Write-Host "[6/7] Organizando documentacion..." -ForegroundColor Yellow

# Session reports
$sessionReports = @(
    "RESUMEN_EJECUTIVO.md",
    "RESUMEN_EJECUTIVO_FIX.txt",
    "RESUMEN_EJECUTIVO_VERIFICACION.md",
    "RESUMEN_INTEGRACION_CONTROL_CENTER.md",
    "RESUMEN_SESION_2025-12-04.txt",
    "RESUMEN_SESION_LINKEDIN_V3.md",
    "ANALISIS_BOLETINES_2025-12-04.txt",
    "AUDITORIA_PROYECTO_2025-12-03.txt",
    "AUDITORIA_VERIFICACION_JOBS.md",
    "COMPARACION_ANTES_DESPUES.md",
    "FIX_BOLETINES_2025-12-04.txt",
    "FIXES_SESION_2025-12-07.md",
    "PRUEBAS_CIERRE.md",
    "SCRAPERS_GIT_SEARCH_REPORT.txt"
)

foreach ($file in $sessionReports) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "docs\session_reports\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> docs\session_reports\" -ForegroundColor Green
    }
}

# Guides
$guides = @(
    "GUIA_RAPIDA_MANANA.txt",
    "GUIA_RECUPERAR_SCRAPERS.txt",
    "GUIA_USO_PROMPTS.md",
    "GUIA_VERIFICACION_MULTIPLATAFORMA.md",
    "QUICK_START_VERIFICACION.md",
    "LINKEDIN_VERIFIER_V3_QUICKSTART.md",
    "INDICE_ARCHIVOS_AUDITORIA.md",
    "SOLUCION_RAPIDA_OAUTH.md",
    "GIT_COMMANDS.md",
    "QUICK_GIT.md"
)

foreach ($file in $guides) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "docs\guides\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> docs\guides\" -ForegroundColor Green
    }
}

Write-Host ""

# ==============================================================================
# MOVER BACKUPS A archive/backups
# ==============================================================================

Write-Host "[7/7] Organizando backups y archivos obsoletos..." -ForegroundColor Yellow

$backupFiles = @(
    "run_daily_pipeline(1).py",
    "run_daily_pipeline.py.BEFORE_VERIFY_FIX",
    "run_daily_pipeline.py.backup_autoapply",
    "run_daily_pipeline_BACKUP.py",
    "control_center.py.backup",
    "startup_check_v2.ps1"
)

foreach ($file in $backupFiles) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "archive\backups\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> archive\backups\" -ForegroundColor Green
    }
}

# Mover scripts de organizacion obsoletos
$oldScripts = @(
    "ORGANIZE_PROJECT.ps1",
    "ORGANIZE_PROJECT_AUTO.ps1",
    "ORGANIZE_PROJECT_AUTO_FIXED.ps1",
    "BUSCAR_SCRAPERS_GIT.ps1",
    "CHECK_COMMITS.ps1"
)

foreach ($file in $oldScripts) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "archive\old_versions\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> archive\old_versions\" -ForegroundColor Green
    }
}

# Mover archivos VBS y specs
$miscFiles = @(
    "install_silent.vbs",
    "START_UNIFIED_APP_SILENT.vbs",
    "AIJobFoundry.spec"
)

foreach ($file in $miscFiles) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "archive\old_versions\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> archive\old_versions\" -ForegroundColor Green
    }
}

# Mover prompts viejos
$oldPrompts = @(
    "PROMPT_NUEVO_CHAT_2025-12-04.txt",
    "PROMPT_NUEVO_CHAT_OAUTH_FIX.md"
)

foreach ($file in $oldPrompts) {
    $source = Join-Path $projectRoot $file
    $dest = Join-Path $projectRoot "archive\old_versions\$file"
    
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "  [MOVED] $file -> archive\old_versions\" -ForegroundColor Green
    }
}

Write-Host ""

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  ORGANIZACION COMPLETADA" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ARCHIVOS PRINCIPALES EN ROOT:" -ForegroundColor Yellow
Write-Host "  - START_CONTROL_CENTER.bat (Control Center)" -ForegroundColor White
Write-Host "  - START_WEB_APP.bat (Web App simple)" -ForegroundColor White
Write-Host "  - START_UNIFIED_APP.bat (Unified App con publicidad)" -ForegroundColor White
Write-Host "  - control_center.py" -ForegroundColor White
Write-Host "  - run_daily_pipeline.py" -ForegroundColor White
Write-Host "  - run_daily_cleanup.ps1" -ForegroundColor White
Write-Host "  - push_to_github.ps1" -ForegroundColor White
Write-Host "  - PROMPT_COMPACTO.md" -ForegroundColor White
Write-Host "  - PROMPT_NUEVO_CHAT.md" -ForegroundColor White
Write-Host "  - PROJECT_STATUS.md" -ForegroundColor White
Write-Host "  - MASTER_FEATURE_ROADMAP.md" -ForegroundColor White
Write-Host "  - README.md" -ForegroundColor White
Write-Host "  - requirements.txt" -ForegroundColor White
Write-Host ""
Write-Host "NUEVA ESTRUCTURA:" -ForegroundColor Yellow
Write-Host "  - scripts/tests/ (archivos de test y debug)" -ForegroundColor White
Write-Host "  - scripts/verifiers/ (verificadores de jobs)" -ForegroundColor White
Write-Host "  - scripts/batch/ (scripts batch auxiliares)" -ForegroundColor White
Write-Host "  - data/samples/ (archivos HTML de ejemplo)" -ForegroundColor White
Write-Host "  - docs/guides/ (guias y documentacion)" -ForegroundColor White
Write-Host "  - docs/session_reports/ (reportes de sesiones)" -ForegroundColor White
Write-Host "  - archive/backups/ (backups de archivos)" -ForegroundColor White
Write-Host "  - archive/old_versions/ (versiones antiguas)" -ForegroundColor White
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
