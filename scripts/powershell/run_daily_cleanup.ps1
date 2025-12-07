# AI JOB FOUNDRY - Daily Job Cleanup & Resumen Update
# Autor: Marcos Alvarado
# Fecha: 2025-11-21

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

# Colores
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

# Función para crear líneas
function Get-Line { "=" * 70 }

Write-Host ""
Write-Host (Get-Line) -ForegroundColor $ColorInfo
Write-Host "    AI JOB FOUNDRY - LIMPIEZA DIARIA" -ForegroundColor $ColorInfo
Write-Host (Get-Line) -ForegroundColor $ColorInfo
Write-Host ""
Write-Host "Fecha: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor $ColorInfo
Write-Host ""

# Verificar directorio
$ProjectPath = "C:\Users\MSI\Desktop\ai-job-foundry"

if (-not (Test-Path $ProjectPath)) {
    Write-Host "ERROR: No se encuentra el directorio del proyecto" -ForegroundColor $ColorError
    Write-Host "Esperado: $ProjectPath" -ForegroundColor $ColorError
    exit 1
}

Set-Location $ProjectPath
Write-Host "Directorio de trabajo: $ProjectPath" -ForegroundColor $ColorSuccess
Write-Host ""

# Crear directorio de logs
$LogDir = Join-Path $ProjectPath "logs\powershell"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir "daily_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Función para logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $Message
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
}

Write-Log "Inicio de limpieza diaria"
Write-Log "Log file: $LogFile"
Write-Host ""

# PASO 1: JOB CLEANER
Write-Host (Get-Line) -ForegroundColor $ColorInfo
Write-Host "PASO 1: Ejecutando Job Cleaner..." -ForegroundColor $ColorInfo
Write-Host (Get-Line) -ForegroundColor $ColorInfo
Write-Host ""

$JobCleanerScript = Join-Path $ProjectPath "core\jobs_pipeline\job_cleaner.py"

if (Test-Path $JobCleanerScript) {
    try {
        Write-Host "Ejecutando: py $JobCleanerScript --tab Jobs" -ForegroundColor $ColorInfo
        py $JobCleanerScript --tab Jobs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Job Cleaner completado exitosamente" "SUCCESS"
        } else {
            Write-Log "ADVERTENCIA: Job Cleaner terminó con código $LASTEXITCODE" "WARN"
        }
    } catch {
        Write-Log "ERROR ejecutando Job Cleaner: $_" "ERROR"
    }
} else {
    Write-Host "ADVERTENCIA: job_cleaner.py no encontrado" -ForegroundColor $ColorWarning
}


Write-Host ""
Write-Host (Get-Line) -ForegroundColor $ColorInfo
Write-Host "PASO 2: Actualizando pestaña Resumen..." -ForegroundColor $ColorInfo
Write-Host (Get-Line) -ForegroundColor $ColorInfo
Write-Host ""

$ResumenScript = Join-Path $ProjectPath "core\jobs_pipeline\update_resumen.py"

if (Test-Path $ResumenScript) {
    try {
        Write-Host "Ejecutando: py $ResumenScript" -ForegroundColor $ColorInfo
        py $ResumenScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Resumen actualizado exitosamente" "SUCCESS"
        } else {
            Write-Log "ADVERTENCIA: Resumen terminó con código $LASTEXITCODE" "WARN"
        }
    } catch {
        Write-Log "ERROR actualizando Resumen: $_" "ERROR"
    }
} else {
    Write-Host "ADVERTENCIA: update_resumen.py no encontrado" -ForegroundColor $ColorWarning
}

Write-Host ""
Write-Host (Get-Line) -ForegroundColor $ColorInfo

# REPORTE FINAL
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host ""
Write-Host (Get-Line) -ForegroundColor $ColorSuccess
Write-Host "    LIMPIEZA DIARIA COMPLETADA" -ForegroundColor $ColorSuccess
Write-Host (Get-Line) -ForegroundColor $ColorSuccess
Write-Host ""
Write-Host "Inicio:   $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor $ColorInfo
Write-Host "Fin:      $($EndTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor $ColorInfo
Write-Host "Duración: $([math]::Round($Duration.TotalSeconds, 2)) segundos" -ForegroundColor $ColorInfo
Write-Host ""
Write-Host "Log guardado en:" -ForegroundColor $ColorInfo
Write-Host "  $LogFile" -ForegroundColor $ColorSuccess
Write-Host ""

# Ver Google Sheets
$SheetsID = $env:GOOGLE_SHEETS_ID
if ($SheetsID) {
    Write-Host "Ver resultados en Google Sheets:" -ForegroundColor $ColorInfo
    Write-Host "  https://docs.google.com/spreadsheets/d/$SheetsID" -ForegroundColor $ColorCyan
}

Write-Host ""
Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor $ColorWarning
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
