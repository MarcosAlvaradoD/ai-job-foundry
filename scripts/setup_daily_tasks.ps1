# setup_daily_tasks.ps1
# Configura tareas automaticas de Windows para ai-job-foundry
# Ejecutar UNA SOLA VEZ en PowerShell como administrador:
#   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\scripts\setup_daily_tasks.ps1

$JobFoundryPath = "C:\Users\MSI\Desktop\ai-job-foundry"
$PythonPath     = (Get-Command py).Source

Write-Host "=== Configurando tareas automaticas ai-job-foundry ===" -ForegroundColor Cyan

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# --- Tarea 1: Morning Summary 8:00 AM (lunes-viernes) ---
$a = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument "scripts\maintenance\morning_summary.py" `
    -WorkingDirectory $JobFoundryPath
$t = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:00AM"
Register-ScheduledTask -TaskName "AiJobFoundry-MorningSummary" `
    -Action $a -Trigger $t -Settings $settings `
    -Description "Envia resumen matutino de vacantes a Telegram" -Force
Write-Host "[OK] MorningSummary (Lun-Vie 8:00 AM)" -ForegroundColor Green

# --- Tarea 2: Mantenimiento diario 8:30 AM (lunes-viernes) ---
# Orden: enrich → dedup → clean_closed → fit_scores
$a = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument "scripts\maintenance\run_maintenance.py" `
    -WorkingDirectory $JobFoundryPath
$t = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:30AM"
Register-ScheduledTask -TaskName "AiJobFoundry-DailyMaintenance" `
    -Action $a -Trigger $t -Settings $settings `
    -Description "Enrich + Dedup + CleanClosed + FitScores (pipeline completo)" -Force
Write-Host "[OK] DailyMaintenance (Lun-Vie 8:30 AM)" -ForegroundColor Green

# --- Tarea 3: FIT Scores standalone 9:00 AM (lunes-viernes) ---
# Por si se quiere correr solo sin el pipeline completo
$a = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument "scripts\maintenance\calculate_linkedin_fit_scores.py" `
    -WorkingDirectory $JobFoundryPath
$t = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "09:00AM"
Register-ScheduledTask -TaskName "AiJobFoundry-FitScores" `
    -Action $a -Trigger $t -Settings $settings `
    -Description "Calcula FIT scores de nuevas vacantes LinkedIn" -Force
Write-Host "[OK] FitScores standalone (Lun-Vie 9:00 AM)" -ForegroundColor Green

# --- Tarea 4: Mantenimiento semanal profundo (domingo 9:00 PM) ---
# Dedup + CleanClosed con límite extendido
$a = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument "scripts\maintenance\run_maintenance.py --deep" `
    -WorkingDirectory $JobFoundryPath
$t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "09:00PM"
Register-ScheduledTask -TaskName "AiJobFoundry-WeeklyDeepClean" `
    -Action $a -Trigger $t -Settings $settings `
    -Description "Limpieza semanal profunda del Sheet (dedup + cerradas + stale)" -Force
Write-Host "[OK] WeeklyDeepClean (Dom 9:00 PM)" -ForegroundColor Green

# --- Tarea 5: Clean expired jobs 10:00 PM (domingo) ---
$a = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument "scripts\maintenance\clean_expired_jobs.py" `
    -WorkingDirectory $JobFoundryPath
$t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "10:00PM"
Register-ScheduledTask -TaskName "AiJobFoundry-CleanExpired" `
    -Action $a -Trigger $t -Settings $settings `
    -Description "Limpia vacantes expiradas del Sheet" -Force
Write-Host "[OK] CleanExpired (Dom 10:00 PM)" -ForegroundColor Green

Write-Host ""
Write-Host "=== 5 tareas creadas exitosamente ===" -ForegroundColor Cyan
Write-Host "Ver en: Inicio > Task Scheduler > Task Scheduler Library"
Write-Host ""
Write-Host "Horario diario (Lun-Vie):"
Write-Host "  08:00  MorningSummary     -> Telegram con resumen de jobs"
Write-Host "  08:30  DailyMaintenance   -> enrich + dedup + clean_closed + fit_scores"
Write-Host "  09:00  FitScores          -> solo FIT scores (si se necesita standalone)"
Write-Host ""
Write-Host "Horario semanal (Domingo):"
Write-Host "  21:00  WeeklyDeepClean    -> limpieza profunda"
Write-Host "  22:00  CleanExpired       -> elimina expiradas"
