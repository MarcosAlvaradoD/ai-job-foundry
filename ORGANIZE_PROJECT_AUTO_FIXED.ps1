# PowerShell Script - Organizacion Automatica del Proyecto
# AI Job Foundry - Limpieza y Reestructuracion

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI JOB FOUNDRY - ORGANIZACION AUTOMATICA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$movedCount = 0
$errorCount = 0

# Funcion para mover archivo con confirmacion
function Move-FileWithCheck($Source, $Destination) {
    if (Test-Path $Source) {
        try {
            # Crear carpeta destino si no existe
            $destDir = Split-Path $Destination -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                Write-Host "  Creada carpeta: $destDir" -ForegroundColor Green
            }
            
            # Mover archivo
            Move-Item -Path $Source -Destination $Destination -Force
            Write-Host "  Movido: $(Split-Path $Source -Leaf) -> $destDir" -ForegroundColor Green
            $script:movedCount++
        }
        catch {
            Write-Host "  Error moviendo $Source : $_" -ForegroundColor Red
            $script:errorCount++
        }
    }
    else {
        Write-Host "  No encontrado: $Source" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "PASO 1: Mover scripts de mantenimiento a scripts/maintenance/" -ForegroundColor Yellow
Write-Host ""

$maintenanceScripts = @(
    "check_oauth_token.py",
    "mark_all_negatives.py", 
    "mark_expired_jobs.py",
    "process_bulletins.py",
    "recalculate_fit_scores.py",
    "standardize_status.py",
    "standardize_status_v2.py",
    "standardize_status_v3.py",
    "update_status_from_emails.py"
)

foreach ($script in $maintenanceScripts) {
    Move-FileWithCheck -Source ".\$script" -Destination ".\scripts\maintenance\$script"
}

Write-Host ""
Write-Host "PASO 2: Mover verify_job_status.py a scripts/maintenance/" -ForegroundColor Yellow
Write-Host ""
Move-FileWithCheck -Source ".\verify_job_status.py" -Destination ".\scripts\maintenance\verify_job_status.py"

Write-Host ""
Write-Host "PASO 3: Mover scripts de fixes a docs/fixes/" -ForegroundColor Yellow
Write-Host ""

# Crear carpeta docs/fixes si no existe
if (-not (Test-Path ".\docs\fixes")) {
    New-Item -ItemType Directory -Path ".\docs\fixes" -Force | Out-Null
    Write-Host "  Creada carpeta: docs\fixes" -ForegroundColor Green
}

$fixScripts = @(
    "FIX_DASHBOARD_OPTION.py",
    "PATCH_CONTROL_CENTER.py",
    "RESTORE_SAFE.py"
)

foreach ($script in $fixScripts) {
    Move-FileWithCheck -Source ".\$script" -Destination ".\docs\fixes\$script"
}

Write-Host ""
Write-Host "PASO 4: Mover backup a archive/backups/" -ForegroundColor Yellow
Write-Host ""

# Crear carpeta archive/backups si no existe
if (-not (Test-Path ".\archive\backups")) {
    New-Item -ItemType Directory -Path ".\archive\backups" -Force | Out-Null
    Write-Host "  Creada carpeta: archive\backups" -ForegroundColor Green
}

if (Test-Path ".\backup_20251117_030702") {
    Move-FileWithCheck -Source ".\backup_20251117_030702" -Destination ".\archive\backups\backup_20251117_030702"
}

Write-Host ""
Write-Host "PASO 5: Limpiar carpeta TEST/" -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".\TEST\hola_mundo.txt") {
    try {
        Remove-Item -Path ".\TEST\hola_mundo.txt" -Force
        Write-Host "  Eliminado: TEST\hola_mundo.txt" -ForegroundColor Green
        
        # Intentar eliminar carpeta TEST si esta vacia
        if ((Get-ChildItem ".\TEST" | Measure-Object).Count -eq 0) {
            Remove-Item -Path ".\TEST" -Force
            Write-Host "  Eliminada carpeta vacia: TEST\" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  No se pudo limpiar TEST/: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "PASO 6: Consolidar carpeta fixes/ vacia" -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".\fixes") {
    try {
        if ((Get-ChildItem ".\fixes" | Measure-Object).Count -eq 0) {
            Remove-Item -Path ".\fixes" -Force
            Write-Host "  Eliminada carpeta vacia: fixes\" -ForegroundColor Green
        }
        else {
            Write-Host "  fixes\ no esta vacia, revisar manualmente" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  No se pudo eliminar fixes/: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMEN DE ORGANIZACION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Archivos movidos:  $movedCount" -ForegroundColor Green
Write-Host "Errores:           $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errorCount -eq 0) {
    Write-Host "Organizacion completada exitosamente!" -ForegroundColor Green
}
else {
    Write-Host "Organizacion completada con algunos errores" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Siguiente paso: Revisar Gmail y Google Sheets" -ForegroundColor Cyan
Write-Host ""
