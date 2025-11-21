# Git Clean History - Remove All Sensitive Data
# Creates fresh history without tokens

Write-Host "`n🔒 CLEANING GIT HISTORY`n" -ForegroundColor Cyan

cd C:\Users\MSI\Desktop\ai-job-foundry

# Step 1: Create orphan branch (no history)
Write-Host "📦 Creating clean branch..." -ForegroundColor Yellow
git checkout --orphan clean-main

# Step 2: Add all current files
Write-Host "📝 Adding all files..." -ForegroundColor Yellow
git add -A

# Step 3: Create single clean commit
Write-Host "💾 Creating clean commit..." -ForegroundColor Yellow
git commit -m "feat: AI Job Foundry - Complete System (82% functional)

FEATURES:
✅ Gmail Monitor V2 with URL extraction
✅ Deduplication system (cache + labels + sheets)
✅ LinkedIn scraper with anti-bot
✅ AI analysis (LM Studio + Qwen 2.5 14B)
✅ Google Sheets integration
✅ Dashboard UI with Tailwind CSS
✅ PowerShell automation scripts

STATS:
- 10 jobs processed successfully
- FIT SCORES: 2-9/10 range
- Avg: 5.1/10
- Deduplication: 100% working
- LM Studio: Fast responses

PROJECT: 82% Complete"

# Step 4: Delete old main
Write-Host "🗑️  Deleting old branch..." -ForegroundColor Yellow
git branch -D main

# Step 5: Rename clean-main to main
Write-Host "🔄 Renaming branch..." -ForegroundColor Yellow
git branch -m main

# Step 6: Force push to GitHub
Write-Host "🚀 Force pushing to GitHub..." -ForegroundColor Yellow
git push origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅✅ SUCCESS! Clean history pushed!" -ForegroundColor Green
    Write-Host "🔗 https://github.com/MarcosAlvaradoD/ai-job-foundry" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Push failed" -ForegroundColor Red
}
