# Fix Git Rebase - AI Job Foundry
# Limpia archivos de cache y completa el rebase

Write-Host "`n🔧 FIXING GIT REBASE...`n" -ForegroundColor Cyan

$projectRoot = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $projectRoot

# 1. Reset archivos no deseados
Write-Host "📦 Step 1: Resetting browser cache files..." -ForegroundColor Yellow
git reset HEAD data/browser_data/ 2>$null
git reset HEAD data/credentials/token.json 2>$null
git reset HEAD mcp-servers/ 2>$null

# 2. Limpiar archivos no rastreados de cache
Write-Host "🗑️  Step 2: Cleaning untracked cache files..." -ForegroundColor Yellow
if (Test-Path "data\browser_data\Default\Cache") {
    Remove-Item "data\browser_data\Default\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
}

# 3. Verificar archivos importantes staged
Write-Host "`n✅ Step 3: Important files ready to commit:" -ForegroundColor Green
git status --short | Select-String "^M\s+core/automation/gmail_jobs_monitor_v2.py"
git status --short | Select-String "^A\s+core/utils/email_url_extractor_v2.py"
git status --short | Select-String "^M\s+dashboard.html"

# 4. Agregar gitignore actualizado
Write-Host "`n📝 Step 4: Adding updated .gitignore..." -ForegroundColor Yellow
git add .gitignore

# 5. Continuar rebase
Write-Host "`n🚀 Step 5: Continuing rebase..." -ForegroundColor Yellow
Write-Host "This will commit the staged changes and continue..." -ForegroundColor Gray

$continue = Read-Host "`nReady to continue rebase? (y/n)"

if ($continue -eq "y") {
    git rebase --continue
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ REBASE COMPLETED!" -ForegroundColor Green
        Write-Host "Ready to push to GitHub" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠️  Rebase needs manual intervention" -ForegroundColor Yellow
        Write-Host "Run: git status" -ForegroundColor Gray
    }
} else {
    Write-Host "`n⏸️  Rebase paused. Run this script again when ready." -ForegroundColor Yellow
}

Write-Host "`n================================`n" -ForegroundColor Cyan
