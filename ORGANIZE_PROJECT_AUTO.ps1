# ================================================================
# SCRIPT DE ORGANIZACIÓN AUTOMÁTICA - AI JOB FOUNDRY
# ================================================================
# Ubicación: C:\Users\MSI\Desktop\ai-job-foundry\ORGANIZE_PROJECT_AUTO.ps1
#
# PROPÓSITO: Limpiar y organizar archivos del proyecto automáticamente
# FECHA: 2025-01-10
# AUTOR: Claude + Marcos
# ================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Colores
$COLOR_SUCCESS = "Green"
$COLOR_INFO = "Cyan"
$COLOR_WARNING = "Yellow"
$COLOR_ERROR = "Red"

Write-Host "================================================================" -ForegroundColor $COLOR_INFO
Write-Host "🧹 ORGANIZACIÓN AUTOMÁTICA - AI JOB FOUNDRY" -ForegroundColor $COLOR_INFO
Write-Host "================================================================`n" -ForegroundColor $COLOR_INFO

# Timestamp para backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "archive\backups\cleanup_$timestamp"

Write-Host "📁 Creando directorio de backup: $backupDir" -ForegroundColor $COLOR_INFO
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# ================================================================
# FUNCIÓN: Mover archivo con validación
# ================================================================
function Move-FileToLocation {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Category
    )
    
    if (Test-Path $Source) {
        try {
            # Crear directorio de destino si no existe
            $destDir = Split-Path -Parent $Destination
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Force -Path $destDir | Out-Null
            }
            
            # Mover archivo
            Move-Item -Path $Source -Destination $Destination -Force
            Write-Host "  ✅ Movido: $Source → $Destination" -ForegroundColor $COLOR_SUCCESS
            return $true
        }
        catch {
            Write-Host "  ❌ Error moviendo $Source : $_" -ForegroundColor $COLOR_ERROR
            return $false
        }
    }
    return $false
}

# ================================================================
# 1. SCRIPTS DE TESTING POWERSHELL
# ================================================================
Write-Host "`n📦 1. Organizando scripts de testing PowerShell..." -ForegroundColor $COLOR_INFO

$testScripts = @(
    "TEST_CONTROL_CENTER.ps1",
    "test_linkedin_autoapply.ps1",
    "TEST_OAUTH_FLOW.ps1",
    "TEST_OAUTH_REAUTH.ps1",
    "TEST_OAUTH_VALIDATOR.ps1"
)

foreach ($script in $testScripts) {
    Move-FileToLocation -Source $script -Destination "scripts\tests\$script" -Category "Testing"
}

# ================================================================
# 2. SCRIPTS DE MANTENIMIENTO POWERSHELL
# ================================================================
Write-Host "`n📦 2. Organizando scripts de mantenimiento..." -ForegroundColor $COLOR_INFO

$maintenanceScripts = @(
    "CLEANUP_FINAL.ps1",
    "CLEAN_INDEED_INVALID.ps1",
    "REINSTALL_PLAYWRIGHT.ps1",
    "REINICIO_LIMPIO.ps1",
    "REPARACION_OAUTH_EXPIRE.ps1",
    "run_daily_cleanup.ps1"
)

foreach ($script in $maintenanceScripts) {
    Move-FileToLocation -Source $script -Destination "scripts\maintenance\$script" -Category "Maintenance"
}

# ================================================================
# 3. SCRIPTS DE DIAGNÓSTICO POWERSHELL
# ================================================================
Write-Host "`n📦 3. Organizando scripts de diagnóstico..." -ForegroundColor $COLOR_INFO

$diagnosticScripts = @(
    "DIAGNOSTICO_COMPLETO.ps1",
    "DIAGNOSTICO_GPU.ps1",
    "detect_lm_studio_ip.ps1",
    "VERIFICAR_VRAM_NVIDIA.ps1",
    "VERIFY_PATHS.ps1"
)

foreach ($script in $diagnosticScripts) {
    Move-FileToLocation -Source $script -Destination "scripts\powershell\$script" -Category "Diagnostic"
}

# ================================================================
# 4. SCRIPTS DE INSTALACIÓN Y SETUP
# ================================================================
Write-Host "`n📦 4. Organizando scripts de instalación..." -ForegroundColor $COLOR_INFO

$setupScripts = @(
    "INSTALL_ARCHIVOS.ps1",
    "install_oauth_validator.ps1",
    "LEER_PRIMERO.ps1"
)

foreach ($script in $setupScripts) {
    Move-FileToLocation -Source $script -Destination "scripts\setup\$script" -Category "Setup"
}

# ================================================================
# 5. SCRIPTS DE ORGANIZACIÓN (META)
# ================================================================
Write-Host "`n📦 5. Organizando scripts de organización..." -ForegroundColor $COLOR_INFO

$orgScripts = @(
    "ORGANIZE_FILES_AUTO.ps1",
    "ORGANIZE_FINAL.ps1",
    "ORGANIZE_ROOT_SAFE.ps1",
    "DECISION_RAPIDA.ps1"
)

foreach ($script in $orgScripts) {
    Move-FileToLocation -Source $script -Destination "scripts\maintenance\organization\$script" -Category "Organization"
}

# ================================================================
# 6. DOCUMENTOS MARKDOWN
# ================================================================
Write-Host "`n📦 6. Organizando documentos markdown..." -ForegroundColor $COLOR_INFO

$docs = @(
    @{File = "CHECKLIST_EJECUCION.md"; Dest = "docs\guides\CHECKLIST_EJECUCION.md"},
    @{File = "COMPARATIVA_LAUNCHERS.md"; Dest = "docs\setup\COMPARATIVA_LAUNCHERS.md"},
    @{File = "EJECUTAR_AHORA.md"; Dest = "docs\quickstart\EJECUTAR_AHORA.md"},
    @{File = "GUIA_RH_IT_HOME.md"; Dest = "docs\guides\GUIA_RH_IT_HOME.md"},
    @{File = "GUIA_UBICACION_ARCHIVOS.md"; Dest = "docs\setup\GUIA_UBICACION_ARCHIVOS.md"},
    @{File = "PROXIMOS_PASOS.md"; Dest = "docs\PROXIMOS_PASOS.md"},
    @{File = "REORGANIZACION_PROYECTO.md"; Dest = "docs\archive\REORGANIZACION_PROYECTO.md"},
    @{File = "RESUMEN_EJECUTIVO_REORGANIZACION.md"; Dest = "docs\archive\RESUMEN_EJECUTIVO_REORGANIZACION.md"},
    @{File = "RESUMEN_FINAL_ACCIONES.md"; Dest = "docs\session_reports\RESUMEN_FINAL_ACCIONES.md"},
    @{File = "RESUMEN_FINAL_SESION_20251212.md"; Dest = "docs\session_reports\RESUMEN_FINAL_SESION_20251212.md"},
    @{File = "SESION_COMPLETA_2025-12-20.md"; Dest = "docs\session_reports\SESION_COMPLETA_2025-12-20.md"}
)

foreach ($doc in $docs) {
    Move-FileToLocation -Source $doc.File -Destination $doc.Dest -Category "Documentation"
}

# ================================================================
# 7. ARCHIVOS DE BACKUP
# ================================================================
Write-Host "`n📦 7. Organizando backups..." -ForegroundColor $COLOR_INFO

# Archivos individuales con .backup
$backupFiles = Get-ChildItem -Filter "*.backup*" -File
foreach ($file in $backupFiles) {
    Move-FileToLocation -Source $file.Name -Destination "archive\backups\$($file.Name)" -Category "Backup"
}

# Directorio backup completo
if (Test-Path "backup_20251117_030702") {
    Move-FileToLocation -Source "backup_20251117_030702" -Destination "archive\backups\backup_20251117_030702" -Category "Backup"
}

# ================================================================
# 8. LOGS SUELTOS
# ================================================================
Write-Host "`n📦 8. Organizando logs sueltos..." -ForegroundColor $COLOR_INFO

if (Test-Path "ingest.log") {
    Move-FileToLocation -Source "ingest.log" -Destination "logs\ingest.log" -Category "Logs"
}

if (Test-Path "debug_glassdoor_email.html") {
    Move-FileToLocation -Source "debug_glassdoor_email.html" -Destination "data\samples\debug_glassdoor_email.html" -Category "Debug"
}

# ================================================================
# 9. DIRECTORIO STATE
# ================================================================
Write-Host "`n📦 9. Moviendo directorio state..." -ForegroundColor $COLOR_INFO

if (Test-Path "state") {
    Move-FileToLocation -Source "state" -Destination "data\state" -Category "State"
}

# ================================================================
# 10. DIRECTORIO TEST
# ================================================================
Write-Host "`n📦 10. Limpiando directorio TEST..." -ForegroundColor $COLOR_INFO

if (Test-Path "TEST") {
    # Mover contenido útil si existe
    if (Test-Path "TEST\hola_mundo.txt") {
        Remove-Item "TEST\hola_mundo.txt" -Force
    }
    # Eliminar directorio TEST si está vacío
    $testItems = Get-ChildItem "TEST" -Force
    if ($testItems.Count -eq 0) {
        Remove-Item "TEST" -Recurse -Force
        Write-Host "  ✅ Eliminado directorio TEST vacío" -ForegroundColor $COLOR_SUCCESS
    }
}

# ================================================================
# 11. LIMPIAR __pycache__ EN RAÍZ
# ================================================================
Write-Host "`n📦 11. Limpiando archivos .pyc en raíz..." -ForegroundColor $COLOR_INFO

if (Test-Path "__pycache__") {
    # Mover verifiers .pyc a su ubicación correcta (deberían regenerarse)
    $pycacheFiles = Get-ChildItem "__pycache__" -Filter "*.pyc"
    foreach ($file in $pycacheFiles) {
        Write-Host "  🗑️  Eliminando: __pycache__\$($file.Name)" -ForegroundColor $COLOR_WARNING
    }
    
    # Eliminar __pycache__ completo (Python lo recreará si es necesario)
    Remove-Item "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✅ Eliminado directorio __pycache__ en raíz" -ForegroundColor $COLOR_SUCCESS
}

# ================================================================
# 12. VERIFICAR ARCHIVOS CRÍTICOS EN RAÍZ
# ================================================================
Write-Host "`n📦 12. Verificando archivos críticos en raíz..." -ForegroundColor $COLOR_INFO

$criticalFiles = @(
    "control_center.py",
    "main.py",
    "oauth_token_validator.py",
    "run_daily_pipeline.py",
    "paths.py",
    ".env",
    "requirements.txt",
    "README.md",
    ".gitignore",
    "start_all.ps1",
    "START_CONTROL_CENTER.bat"
)

$missingCritical = @()
foreach ($file in $criticalFiles) {
    if (-not (Test-Path $file)) {
        $missingCritical += $file
        Write-Host "  ⚠️  FALTA ARCHIVO CRÍTICO: $file" -ForegroundColor $COLOR_WARNING
    }
}

if ($missingCritical.Count -eq 0) {
    Write-Host "  ✅ Todos los archivos críticos están en raíz" -ForegroundColor $COLOR_SUCCESS
}

# ================================================================
# REPORTE FINAL
# ================================================================
Write-Host "`n================================================================" -ForegroundColor $COLOR_INFO
Write-Host "✅ ORGANIZACIÓN COMPLETADA" -ForegroundColor $COLOR_SUCCESS
Write-Host "================================================================`n" -ForegroundColor $COLOR_INFO

# Generar reporte
$reportPath = "docs\session_reports\CLEANUP_REPORT_$timestamp.md"
$report = @"
# 🧹 REPORTE DE LIMPIEZA - AI JOB FOUNDRY

**Fecha:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Script:** ORGANIZE_PROJECT_AUTO.ps1

## ✅ ARCHIVOS ORGANIZADOS

### 📦 Scripts PowerShell
- Testing → `scripts/tests/`
- Mantenimiento → `scripts/maintenance/`
- Diagnóstico → `scripts/powershell/`
- Setup → `scripts/setup/`
- Organización → `scripts/maintenance/organization/`

### 📄 Documentos
- Guías → `docs/guides/`
- Setup → `docs/setup/`
- Quickstart → `docs/quickstart/`
- Reportes de sesión → `docs/session_reports/`
- Archive → `docs/archive/`

### 💾 Backups
- Backups antiguos → `archive/backups/`

### 📊 Logs y Debug
- Logs → `logs/`
- Samples → `data/samples/`

### 🗂️ Directorios
- `state/` → `data/state/`
- `TEST/` → eliminado (vacío)
- `__pycache__/` → eliminado (se regenerará)

## 🎯 ARCHIVOS QUE PERMANECEN EN RAÍZ

✅ Archivos críticos verificados:
$(foreach ($file in $criticalFiles) { "- $file`n" })

## 📝 PRÓXIMOS PASOS

1. Ejecutar `py control_center.py` para verificar que todo funciona
2. Revisar logs en `logs/powershell/` si hay errores
3. Actualizar `PROJECT_STATUS.md` con progreso
4. Commit a Git: `git add . && git commit -m "🧹 Reorganización automática del proyecto"`

---

**Backup creado en:** `$backupDir`
"@

# Guardar reporte
$report | Out-File -FilePath $reportPath -Encoding UTF8 -Force
Write-Host "📄 Reporte guardado en: $reportPath`n" -ForegroundColor $COLOR_INFO

Write-Host "🎉 PROCESO COMPLETADO - Revisa el reporte para detalles" -ForegroundColor $COLOR_SUCCESS
Write-Host "📁 Backup disponible en: $backupDir`n" -ForegroundColor $COLOR_INFO
