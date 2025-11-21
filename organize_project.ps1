# Organize Project Structure - AI Job Foundry
# Moves files to proper directories

Write-Host "`n📁 ORGANIZANDO PROYECTO...`n" -ForegroundColor Cyan

$root = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $root

# Create necessary directories
$dirs = @(
    "scripts\git",
    "scripts\setup",
    "core\copilot",
    "archive\migrations",
    "archive\old_scripts"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📂 Created: $dir" -ForegroundColor Green
    }
}

# Move Git scripts
$gitScripts = @("fix_git_rebase.ps1", "git_clean_commit.ps1", "git_clean_history.ps1", "git_force_commit.ps1")
foreach ($file in $gitScripts) {
    if (Test-Path $file) {
        Move-Item $file "scripts\git\" -Force
        Write-Host "✅ Moved $file → scripts\git\" -ForegroundColor Green
    }
}

# Move test files
$testFiles = @("test_ai_workbenches.py", "test_gmail_connection.py")
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item $file "scripts\" -Force
        Write-Host "✅ Moved $file → scripts\" -ForegroundColor Green
    }
}

# Move interview copilot files
$copilotFiles = @("interview_copilot_session_recorder.py", "interview_copilot_simple.py")
foreach ($file in $copilotFiles) {
    if (Test-Path $file) {
        Move-Item $file "core\copilot\" -Force
        Write-Host "✅ Moved $file → core\copilot\" -ForegroundColor Green
    }
}

# Move migration files
$migrationFiles = @("migrate_from_jobs.py", "migration_log_20251106_021245.txt")
foreach ($file in $migrationFiles) {
    if (Test-Path $file) {
        Move-Item $file "archive\migrations\" -Force
        Write-Host "✅ Moved $file → archive\migrations\" -ForegroundColor Green
    }
}

# Move old scripts
$oldScripts = @("sync_with_sheets.py", "sync_with_sheets1.py", "register_from_sheets.py", "job_tracker.py")
foreach ($file in $oldScripts) {
    if (Test-Path $file) {
        Move-Item $file "archive\old_scripts\" -Force
        Write-Host "✅ Moved $file → archive\old_scripts\" -ForegroundColor Green
    }
}

# Move setup files
$setupFiles = @("setup_git_repo.cmd", "install_copilot_deps.ps1", "reauthenticate_gmail.py", "fix_oauth_scope.py", "fix_sheets_import.py")
foreach ($file in $setupFiles) {
    if (Test-Path $file) {
        Move-Item $file "scripts\setup\" -Force
        Write-Host "✅ Moved $file → scripts\setup\" -ForegroundColor Green
    }
}

# Move resume files
$resumeFiles = @("RESUMEN_FINAL_18NOV.txt", "RESUMEN_FIXES_FINAL.txt")
foreach ($file in $resumeFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\" -Force
        Write-Host "✅ Moved $file → docs\" -ForegroundColor Green
    }
}

Write-Host "`n✅ ORGANIZACIÓN COMPLETADA!`n" -ForegroundColor Green
Write-Host "📊 Estructura del proyecto:" -ForegroundColor Cyan
Write-Host "  scripts/git/          - Scripts de Git" -ForegroundColor Gray
Write-Host "  scripts/setup/        - Scripts de configuración" -ForegroundColor Gray
Write-Host "  scripts/              - Scripts de testing" -ForegroundColor Gray
Write-Host "  core/copilot/         - Interview copilot" -ForegroundColor Gray
Write-Host "  archive/migrations/   - Archivos de migración" -ForegroundColor Gray
Write-Host "  archive/old_scripts/  - Scripts deprecados" -ForegroundColor Gray
Write-Host "  docs/                 - Documentación" -ForegroundColor Gray

Write-Host "`n================================`n" -ForegroundColor Cyan
