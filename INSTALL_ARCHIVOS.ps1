# ============================================================================
# AI JOB FOUNDRY - INSTALACION AUTOMATICA DE ARCHIVOS
# 
# Este script copia automaticamente todos los archivos descargados
# a sus ubicaciones correctas en el proyecto
# ============================================================================

Write-Host ""
Write-Host "AI JOB FOUNDRY - INSTALACION AUTOMATICA" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$downloads = "$env:USERPROFILE\Downloads"
$project = "C:\Users\MSI\Desktop\ai-job-foundry"

# Verificar que estamos en el proyecto
if (-not (Test-Path "$project\paths.py")) {
    Write-Host "[ERROR] No se encuentra paths.py en $project" -ForegroundColor Red
    Write-Host "        Asegurate de estar en la raiz del proyecto." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Proyecto encontrado: $project" -ForegroundColor Green
Write-Host ""

# ============================================================================
# ARCHIVOS A COPIAR
# ============================================================================

$files = @(
    @{
        Source = "$downloads\CLEANUP_FINAL.ps1"
        Dest = "$project\CLEANUP_FINAL.ps1"
        Name = "CLEANUP_FINAL.ps1"
    },
    @{
        Source = "$downloads\VERIFY_PATHS.ps1"
        Dest = "$project\VERIFY_PATHS.ps1"
        Name = "VERIFY_PATHS.ps1"
    },
    @{
        Source = "$downloads\COMPARATIVA_LAUNCHERS.md"
        Dest = "$project\docs\COMPARATIVA_LAUNCHERS.md"
        Name = "COMPARATIVA_LAUNCHERS.md"
    },
    @{
        Source = "$downloads\GUIA_UBICACION_ARCHIVOS.md"
        Dest = "$project\docs\GUIA_UBICACION_ARCHIVOS.md"
        Name = "GUIA_UBICACION_ARCHIVOS.md"
    },
    @{
        Source = "$downloads\REORGANIZACION_PROYECTO.md"
        Dest = "$project\docs\REORGANIZACION_PROYECTO.md"
        Name = "REORGANIZACION_PROYECTO.md"
    },
    @{
        Source = "$downloads\RESUMEN_EJECUTIVO_REORGANIZACION.md"
        Dest = "$project\docs\RESUMEN_EJECUTIVO_REORGANIZACION.md"
        Name = "RESUMEN_EJECUTIVO_REORGANIZACION.md"
    },
    @{
        Source = "$downloads\RESUMEN_FINAL_ACCIONES.md"
        Dest = "$project\docs\RESUMEN_FINAL_ACCIONES.md"
        Name = "RESUMEN_FINAL_ACCIONES.md"
    }
)

# ============================================================================
# COPIAR ARCHIVOS
# ============================================================================

Write-Host "Copiando archivos..." -ForegroundColor Yellow
Write-Host ""

$copied = 0
$failed = 0

foreach ($file in $files) {
    if (Test-Path $file.Source) {
        try {
            Copy-Item $file.Source $file.Dest -Force
            Write-Host "[OK] $($file.Name)" -ForegroundColor Green
            $copied++
        } catch {
            Write-Host "[ERROR] $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "[SKIP] $($file.Name) - No encontrado en Downloads" -ForegroundColor Yellow
    }
}

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Write-Host "Archivos copiados: $copied" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Archivos fallidos: $failed" -ForegroundColor Red
}

Write-Host ""

if ($copied -gt 0) {
    Write-Host "INSTALACION COMPLETADA!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Ejecutar: .\VERIFY_PATHS.ps1" -ForegroundColor White
    Write-Host "  2. Probar:   .\START_UNIFIED_APP.bat" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "No se copiaron archivos." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Asegurate de haber descargado los archivos del chat" -ForegroundColor White
    Write-Host "y que esten en: $downloads" -ForegroundColor White
    Write-Host ""
}

pause
