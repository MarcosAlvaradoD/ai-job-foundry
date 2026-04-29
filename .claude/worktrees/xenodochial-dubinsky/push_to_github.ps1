# ============================================================================
# 🚀 PUSH TO GITHUB - AUTOMATED SCRIPT
# ============================================================================
# Este script prepara y sube el proyecto a GitHub de forma segura
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🚀 AI JOB FOUNDRY - PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PASO 1: VERIFICAR GIT
# ============================================================================
Write-Host "📋 PASO 1: Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Git no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# ============================================================================
# PASO 2: VERIFICAR ARCHIVOS SENSIBLES
# ============================================================================
Write-Host "🔐 PASO 2: Verificando archivos sensibles..." -ForegroundColor Yellow

$sensitiveFiles = @(
    "data\credentials\credentials.json",
    "data\credentials\token.json",
    ".env",
    "data\linkedin_cookies.json",
    "data\state\seen_ids.json"
)

$foundSensitive = $false
foreach ($file in $sensitiveFiles) {
    if (Test-Path $file) {
        $inGitignore = Select-String -Path ".gitignore" -Pattern ([regex]::Escape($file.Replace("\", "/"))) -Quiet
        if (-not $inGitignore) {
            Write-Host "   ⚠️  ADVERTENCIA: $file existe pero NO está en .gitignore" -ForegroundColor Red
            $foundSensitive = $true
        } else {
            Write-Host "   ✅ $file protegido por .gitignore" -ForegroundColor Green
        }
    }
}

if ($foundSensitive) {
    Write-Host ""
    Write-Host "❌ ALTO: Archivos sensibles NO protegidos" -ForegroundColor Red
    Write-Host "   Revisa .gitignore antes de continuar" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Todos los archivos sensibles están protegidos" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PASO 3: INICIALIZAR GIT (si es necesario)
# ============================================================================
Write-Host "📦 PASO 3: Inicializando Git..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Repositorio Git inicializado" -ForegroundColor Green
} else {
    Write-Host "✅ Repositorio Git ya existe" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# PASO 4: CONFIGURAR GIT (si no está configurado)
# ============================================================================
Write-Host "⚙️  PASO 4: Configurando Git..." -ForegroundColor Yellow

$gitName = git config --global user.name 2>$null
$gitEmail = git config --global user.email 2>$null

if (-not $gitName) {
    Write-Host "   ℹ️  Ingresa tu nombre para Git:" -ForegroundColor Cyan
    $name = Read-Host "   Nombre"
    git config --global user.name "$name"
    Write-Host "   ✅ Nombre configurado: $name" -ForegroundColor Green
} else {
    Write-Host "   ✅ Nombre: $gitName" -ForegroundColor Green
}

if (-not $gitEmail) {
    Write-Host "   ℹ️  Ingresa tu email para Git:" -ForegroundColor Cyan
    $email = Read-Host "   Email"
    git config --global user.email "$email"
    Write-Host "   ✅ Email configurado: $email" -ForegroundColor Green
} else {
    Write-Host "   ✅ Email: $gitEmail" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# PASO 5: AGREGAR ARCHIVOS
# ============================================================================
Write-Host "➕ PASO 5: Agregando archivos..." -ForegroundColor Yellow
git add .
Write-Host "✅ Archivos agregados" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PASO 6: MOSTRAR STATUS
# ============================================================================
Write-Host "📊 PASO 6: Verificando archivos a subir..." -ForegroundColor Yellow
Write-Host ""
git status
Write-Host ""

# Verificar que NO haya archivos sensibles en staging
Write-Host "🔍 Verificando archivos en staging..." -ForegroundColor Yellow
$stagedFiles = git diff --name-only --cached

$sensitivePatternsRegex = @(
    "credentials\.json$",
    "token\.json$",
    "^\.env$",
    "linkedin_cookies\.json$",
    "seen_ids\.json$"
)

$foundInStaging = $false
foreach ($file in $stagedFiles) {
    foreach ($pattern in $sensitivePatternsRegex) {
        if ($file -match $pattern) {
            Write-Host "   ❌ ARCHIVO SENSIBLE EN STAGING: $file" -ForegroundColor Red
            $foundInStaging = $true
        }
    }
}

if ($foundInStaging) {
    Write-Host ""
    Write-Host "❌ ALTO: Se encontraron archivos sensibles en staging" -ForegroundColor Red
    Write-Host "   Ejecuta: git reset HEAD <archivo>" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ No se encontraron archivos sensibles en staging" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PASO 7: CONFIRMAR COMMIT
# ============================================================================
Write-Host "💾 PASO 7: ¿Hacer commit?" -ForegroundColor Yellow
Write-Host "   Archivos listos para commit" -ForegroundColor Cyan
$confirm = Read-Host "   ¿Continuar? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "❌ Cancelado por el usuario" -ForegroundColor Yellow
    exit 0
}

# ============================================================================
# PASO 8: COMMIT
# ============================================================================
Write-Host ""
Write-Host "💾 PASO 8: Haciendo commit..." -ForegroundColor Yellow

$commitMessage = @"
🚀 Initial commit - AI Job Foundry v1.0

✅ Features:
- Gmail email processing
- LinkedIn/Indeed/Glassdoor scrapers
- AI analysis with LM Studio (Qwen 2.5 14B)
- Smart URL verifiers (Playwright)
- Auto-apply LinkedIn Easy Apply
- Google Sheets integration
- Control Center menu
- Daily pipeline automation

📊 Status: Production ready
🔒 Security: All credentials excluded via .gitignore
"@

git commit -m "$commitMessage"
Write-Host "✅ Commit realizado" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PASO 9: INSTRUCCIONES PARA GITHUB
# ============================================================================
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🌐 PASO 9: CREAR REPOSITORIO EN GITHUB" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ahora necesitas crear el repositorio en GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Ve a: https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Repository name: ai-job-foundry" -ForegroundColor Cyan
Write-Host "3. Visibility: Private (recomendado)" -ForegroundColor Cyan
Write-Host "4. ❌ NO marques 'Initialize with README'" -ForegroundColor Red
Write-Host "5. Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Enter cuando hayas creado el repositorio..." -ForegroundColor Yellow
Read-Host

# ============================================================================
# PASO 10: CONECTAR CON GITHUB
# ============================================================================
Write-Host ""
Write-Host "🔗 PASO 10: Conectando con GitHub..." -ForegroundColor Yellow
Write-Host "   Ingresa tu username de GitHub:" -ForegroundColor Cyan
$githubUser = Read-Host "   Username"

$remoteUrl = "https://github.com/$githubUser/ai-job-foundry.git"

# Verificar si ya existe remote
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "   ℹ️  Remote 'origin' ya existe: $existingRemote" -ForegroundColor Yellow
    $updateRemote = Read-Host "   ¿Actualizar remote? (s/n)"
    if ($updateRemote -eq "s" -or $updateRemote -eq "S") {
        git remote set-url origin $remoteUrl
        Write-Host "   ✅ Remote actualizado" -ForegroundColor Green
    }
} else {
    git remote add origin $remoteUrl
    Write-Host "   ✅ Remote agregado: $remoteUrl" -ForegroundColor Green
}

# Renombrar branch a 'main'
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    git branch -M main
    Write-Host "   ✅ Branch renombrado a 'main'" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# PASO 11: PUSH
# ============================================================================
Write-Host "⬆️  PASO 11: Subiendo a GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   Ejecutando: git push -u origin main" -ForegroundColor Cyan
Write-Host "   (Puede pedir autenticación)" -ForegroundColor Yellow
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "✅ Push exitoso!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "⚠️  Error en push. Posibles causas:" -ForegroundColor Yellow
    Write-Host "   1. Necesitas autenticar con Personal Access Token" -ForegroundColor Cyan
    Write-Host "   2. El repositorio ya existe con contenido" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Genera PAT en: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "   Luego ejecuta: git push -u origin main" -ForegroundColor Cyan
}

# ============================================================================
# FINAL
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "✅ PROCESO COMPLETADO" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Tu repositorio: https://github.com/$githubUser/ai-job-foundry" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Próximos pasos:" -ForegroundColor Yellow
Write-Host "   1. Verifica en GitHub que todo se ve bien" -ForegroundColor Cyan
Write-Host "   2. Revisa que NO aparezcan archivos sensibles" -ForegroundColor Cyan
Write-Host "   3. Lee GIT_COMMANDS.md para comandos futuros" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 ¡Proyecto subido exitosamente!" -ForegroundColor Green
Write-Host ""
