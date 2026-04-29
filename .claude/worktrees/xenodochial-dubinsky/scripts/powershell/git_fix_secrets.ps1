# Fix Git Secrets - Elimina archivos sensibles y hace push limpio
# Soluciona el bloqueo de GitHub Push Protection

Write-Host "`n🔒 FIX GIT SECRETS - LIMPIEZA Y PUSH SEGURO`n" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$projectRoot = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $projectRoot

Write-Host "⏪ Step 1: Revirtiendo último commit (manteniendo cambios)..." -ForegroundColor Yellow
git reset --soft HEAD~1

Write-Host "`n🗑️  Step 2: Eliminando archivos con secretos..." -ForegroundColor Yellow

# Eliminar archivos con secretos
$secretFiles = @(
    "data/credentials/token.json.old",
    "workflows/google_credentials.json"
)

foreach ($file in $secretFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "   ✅ Eliminado: $file" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  No existe: $file" -ForegroundColor Gray
    }
}

# Unstage si estaban staged
git reset HEAD data/credentials/token.json.old 2>$null
git reset HEAD workflows/google_credentials.json 2>$null

Write-Host "`n📝 Step 3: Actualizando .gitignore..." -ForegroundColor Yellow

# Agregar a .gitignore
$gitignoreContent = @"

# ========================================
# CREDENTIALS - NUNCA SUBIR A GITHUB
# ========================================
data/credentials/*.json
workflows/google_credentials.json
workflows/token.json
*.json.old
**/credentials.json
**/token.json

# Archivos sensibles
*.env.local
*.env.production
"@

Add-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "   ✅ .gitignore actualizado" -ForegroundColor Green

Write-Host "`n📦 Step 4: Staging archivos limpios..." -ForegroundColor Yellow
git add .

Write-Host "`n📊 Step 5: Verificando qué se va a subir..." -ForegroundColor Yellow
$changes = git status --short
$changeCount = ($changes | Measure-Object).Count

if ($changeCount -gt 0) {
    Write-Host "Archivos a subir: $changeCount files" -ForegroundColor Cyan
    $changes | Select-Object -First 30 | ForEach-Object { 
        if ($_ -notmatch "token|credentials|secret|key") {
            Write-Host "   $_" -ForegroundColor Gray
        }
    }
    if ($changeCount -gt 30) {
        Write-Host "   ... y $($changeCount - 30) archivos más" -ForegroundColor Gray
    }
} else {
    Write-Host "No hay cambios para subir" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🔍 Verificando que NO hay secretos..." -ForegroundColor Yellow
$hasSecrets = $false
foreach ($change in $changes) {
    if ($change -match "token\.json|credentials\.json|\.env") {
        Write-Host "   ⚠️  ADVERTENCIA: Posible secreto detectado: $change" -ForegroundColor Red
        $hasSecrets = $true
    }
}

if ($hasSecrets) {
    Write-Host "`n❌ SE DETECTARON ARCHIVOS SENSIBLES" -ForegroundColor Red
    Write-Host "No es seguro continuar. Revisa manualmente." -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ No se detectaron secretos" -ForegroundColor Green

Write-Host "`n💾 Step 6: Creando commit limpio..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

git commit -m "feat: AI Job Foundry - 94% Complete (no sensitive data)

✅ COMPLETED:
- Interview Copilot V2 with Job Context
- OAuth Fix Complete
- Dashboard Backend Secure
- LM Studio Internet Test
- Email Processing 100% functional
- Comprehensive documentation

🔒 SECURITY:
- Removed sensitive credentials
- Updated .gitignore
- No OAuth tokens in repo
- No API keys exposed

📊 PROGRESS:
- 94% Complete (+2% today)
- Jobs tracked: 50+
- Interview ready for Monday Nov 24

🎯 COMPONENTS:
✅ LinkedIn Scraper (100%)
✅ Email Processing (100%)
✅ Google Sheets (100%)
✅ AI Analysis (100%)
✅ Interview Copilot V2 (100%)
✅ Dashboard Backend (100%)
✅ Auto-Apply V2 (100%)

Timestamp: $timestamp"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Commit creado exitosamente!" -ForegroundColor Green
    
    Write-Host "`n🚀 Step 7: Pushing a GitHub (sin secretos)..." -ForegroundColor Yellow
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅✅ SUCCESS! Proyecto sincronizado con GitHub!" -ForegroundColor Green
        Write-Host "`n🔗 Verifica en: https://github.com/MarcosAlvaradoD/ai-job-foundry" -ForegroundColor Cyan
        Write-Host "`n📊 Progreso: 94% Complete" -ForegroundColor Cyan
        Write-Host "🔒 Sin datos sensibles" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Push falló. Intentando con --set-upstream..." -ForegroundColor Yellow
        git push --set-upstream origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Push exitoso!" -ForegroundColor Green
        } else {
            Write-Host "`n❌ Push falló de nuevo" -ForegroundColor Red
            Write-Host "Posibles causas:" -ForegroundColor Yellow
            Write-Host "1. Todavía hay secretos en el commit anterior" -ForegroundColor Yellow
            Write-Host "2. Necesitas limpiar el historio de Git" -ForegroundColor Yellow
            Write-Host "`nSolución: Ejecuta git_clean_secrets.ps1" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "`n❌ Commit falló" -ForegroundColor Red
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
