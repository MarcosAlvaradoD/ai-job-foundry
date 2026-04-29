# Git Clean Commit - AI Job Foundry
# Aborta rebase y hace commit limpio

Write-Host "`n🔄 CLEAN GIT COMMIT - FINAL FIX`n" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$projectRoot = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $projectRoot

Write-Host "📦 Step 1: Aborting problematic rebase..." -ForegroundColor Yellow
git rebase --abort

Write-Host "`n🗑️  Step 2: Cleaning workspace..." -ForegroundColor Yellow
git reset HEAD .

Write-Host "`n📝 Step 3: Adding important files only..." -ForegroundColor Yellow
git add .gitignore
git add core/automation/gmail_jobs_monitor_v2.py
git add core/utils/email_url_extractor_v2.py
git add dashboard.html
git add docs/PROJECT_STATUS.md

Write-Host "`n💾 Step 4: Creating commit..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "feat: Enhanced URL extraction + deduplication system + dashboard UI

- Gmail Monitor V2: Enhanced URL extractor for LinkedIn/Indeed/Glassdoor
- Deduplication: 3-level system (cache + labels + sheets)
- Dashboard: Complete UI with charts (pending API integration)
- PROJECT_STATUS.md: Updated to 82% completion
- Updated gitignore: Exclude browser_data and credentials

Timestamp: $timestamp"

Write-Host "`n✅ Step 5: Verifying commit..." -ForegroundColor Green
git log -1 --oneline

Write-Host "`n🚀 Step 6: Pushing to GitHub..." -ForegroundColor Yellow
git push

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS! Changes pushed to GitHub!" -ForegroundColor Green
    Write-Host "`n🔗 Check: https://github.com/MarcosAlvaradoD/ai-job-foundry" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠️  Push failed. May need: git push --force" -ForegroundColor Yellow
    Write-Host "Run: git push --force-with-lease" -ForegroundColor Gray
}

Write-Host "`n================================`n" -ForegroundColor Cyan
