################################################################################
# REVISAR COMMITS DE CORE/INGESTION
################################################################################

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host "🔍 REVISANDO COMMITS DE CORE/INGESTION" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host ""

$commits = @("4d9929a", "814b456")

foreach ($commit in $commits) {
    Write-Host "📝 Commit: " -NoNewline -ForegroundColor Cyan
    Write-Host $commit -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "📂 Archivos en core/ingestion/:" -ForegroundColor Cyan
    git show $commit --name-only | Select-String "core/ingestion" | ForEach-Object {
        Write-Host "   $_" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "---" -ForegroundColor DarkGray
    Write-Host ""
}

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host "✅ REVISIÓN COMPLETA" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host ""
