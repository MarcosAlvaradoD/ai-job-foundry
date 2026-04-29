# PowerShell Script - Organización Automática del Proyecto
# AI Job Foundry - Limpieza y Reestructuración

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI JOB FOUNDRY - ORGANIZACIÓN AUTOMÁTICA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$movedCount = 0
$errorCount = 0

# Función para mover archivo con confirmación
function Move-FileWithCheck {
    param($Source, $Destination)
    
    if (Test-Path $Source) {
        try {
            # Crear carpeta destino si no existe
            $destDir = Split-Path $Destination -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                Write-Host "  📁 Creada carpeta: $destDir" -ForegroundColor Green
            }
            
            # Mover archivo
            Move-Item -Path $Source -Destination $Destination -Force
            Write-Host "  ✅ Movido: $(Split-Path $Source -Leaf) → $destDir" -ForegroundColor Green
            $script:movedCount++
        }
        catch {
            Write-Host "  ❌ Error moviendo $Source : $_" -ForegroundColor Red
            $script:errorCount++
        }
    }
    else {
        Write-Host "  ⚠️  No encontrado: $Source" -ForegroundColor Yellow
    }
}

Write-Host "🔧 PASO 1: Mover scripts de mantenimiento a scripts/maintenance/`n" -ForegroundColor Yellow

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

Write-Host "`n🔧 PASO 2: Mover verify_job_status.py a scripts/maintenance/`n" -ForegroundColor Yellow
Move-FileWithCheck -Source ".\verify_job_status.py" -Destination ".\scripts\maintenance\verify_job_status.py"

Write-Host "`n🔧 PASO 3: Mover scripts de fixes a docs/fixes/`n" -ForegroundColor Yellow

# Crear carpeta docs/fixes si no existe
if (-not (Test-Path ".\docs\fixes")) {
    New-Item -ItemType Directory -Path ".\docs\fixes" -Force | Out-Null
    Write-Host "  📁 Creada carpeta: docs\fixes" -ForegroundColor Green
}

$fixScripts = @(
    "FIX_DASHBOARD_OPTION.py",
    "PATCH_CONTROL_CENTER.py",
    "RESTORE_SAFE.py"
)

foreach ($script in $fixScripts) {
    Move-FileWithCheck -Source ".\$script" -Destination ".\docs\fixes\$script"
}

Write-Host "`n🔧 PASO 4: Mover backup a archive/backups/`n" -ForegroundColor Yellow

# Crear carpeta archive/backups si no existe
if (-not (Test-Path ".\archive\backups")) {
    New-Item -ItemType Directory -Path ".\archive\backups" -Force | Out-Null
    Write-Host "  📁 Creada carpeta: archive\backups" -ForegroundColor Green
}

if (Test-Path ".\backup_20251117_030702") {
    Move-FileWithCheck -Source ".\backup_20251117_030702" -Destination ".\archive\backups\backup_20251117_030702"
}

Write-Host "`n🔧 PASO 5: Limpiar carpeta TEST/`n" -ForegroundColor Yellow

if (Test-Path ".\TEST\hola_mundo.txt") {
    try {
        Remove-Item -Path ".\TEST\hola_mundo.txt" -Force
        Write-Host "  🗑️  Eliminado: TEST\hola_mundo.txt" -ForegroundColor Green
        
        # Intentar eliminar carpeta TEST si está vacía
        if ((Get-ChildItem ".\TEST" | Measure-Object).Count -eq 0) {
            Remove-Item -Path ".\TEST" -Force
            Write-Host "  🗑️  Eliminada carpeta vacía: TEST\" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ⚠️  No se pudo limpiar TEST/: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n🔧 PASO 6: Consolidar carpeta fixes/ vacía`n" -ForegroundColor Yellow

if (Test-Path ".\fixes") {
    try {
        if ((Get-ChildItem ".\fixes" | Measure-Object).Count -eq 0) {
            Remove-Item -Path ".\fixes" -Force
            Write-Host "  🗑️  Eliminada carpeta vacía: fixes\" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚠️  fixes\ no está vacía, revisar manualmente" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ⚠️  No se pudo eliminar fixes/: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE ORGANIZACIÓN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Archivos movidos:  $movedCount" -ForegroundColor Green
Write-Host "Errores:           $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })
Write-Host "========================================`n" -ForegroundColor Cyan

if ($errorCount -eq 0) {
    Write-Host "✅ ¡Organización completada exitosamente!" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Organización completada con algunos errores" -ForegroundColor Yellow
}

Write-Host "`n💡 Siguiente paso: Ejecutar el fix para conectar Auto-Apply" -ForegroundColor Cyan
Write-Host "   Comando: py FIX_AUTO_APPLY_PIPELINE.py`n" -ForegroundColor White
