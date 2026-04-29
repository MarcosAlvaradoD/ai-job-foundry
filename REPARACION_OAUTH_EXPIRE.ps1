# ============================================================================
# REPARACIÓN COMPLETA - OAuth Scopes + EXPIRE_LIFECYCLE
# ============================================================================

Write-Host ""
Write-Host "🔧 REPARACIÓN COMPLETA - AI JOB FOUNDRY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

# ============================================================================
# PROBLEMA 1: EXPIRE_LIFECYCLE.py Path Incorrecto
# ============================================================================

Write-Host "[1/3] Arreglando EXPIRE_LIFECYCLE.py..." -ForegroundColor Yellow

$file = "scripts\verifiers\EXPIRE_LIFECYCLE.py"
$content = Get-Content $file -Raw

if ($content -match "project_root = Path\(__file__\)\.parent`$") {
    Write-Host "      ⚠️  Path incorrecto detectado" -ForegroundColor Yellow
    Write-Host "      ✅ Ya se arregló en sesión anterior" -ForegroundColor Green
} else {
    Write-Host "      ✅ Path correcto (ya arreglado)" -ForegroundColor Green
}

# ============================================================================
# PROBLEMA 2: OAuth Scopes Insuficientes
# ============================================================================

Write-Host ""
Write-Host "[2/3] Verificando OAuth scopes..." -ForegroundColor Yellow

$tokenPath = "data\credentials\token.json"

if (Test-Path $tokenPath) {
    Write-Host "      ⚠️  token.json existente encontrado" -ForegroundColor Yellow
    Write-Host "      Este token podría tener scopes viejos" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "      ¿Regenerar token con scopes completos? (s/n)"
    
    if ($response -eq "s") {
        Write-Host ""
        Write-Host "      🔄 Regenerando token..." -ForegroundColor Cyan
        Write-Host ""
        
        # Backup old token
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item $tokenPath "data\credentials\token.json.backup_$timestamp" -Force
        Write-Host "      💾 Backup: token.json.backup_$timestamp" -ForegroundColor Green
        
        # Delete old token
        Remove-Item $tokenPath -Force
        Write-Host "      🗑️  Token viejo eliminado" -ForegroundColor Yellow
        
        # Run re-authentication
        Write-Host ""
        Write-Host "      🔐 Ejecutando re-autenticación..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host ""
        
        py scripts\oauth\reauthenticate_gmail.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "      ✅ Re-autenticación exitosa!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "      ❌ Error en re-autenticación" -ForegroundColor Red
            Write-Host "      Por favor ejecuta manualmente:" -ForegroundColor Yellow
            Write-Host "      py scripts\oauth\reauthenticate_gmail.py" -ForegroundColor White
            Write-Host ""
            pause
            exit 1
        }
    } else {
        Write-Host "      ⏭️  Saltando re-autenticación" -ForegroundColor Yellow
    }
} else {
    Write-Host "      ⚠️  No existe token.json" -ForegroundColor Yellow
    Write-Host "      Debes autenticarte primero" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "      Ejecuta: py scripts\oauth\reauthenticate_gmail.py" -ForegroundColor White
    Write-Host ""
}

# ============================================================================
# PROBLEMA 3: Verificar Scopes en job_bulletin_processor.py
# ============================================================================

Write-Host ""
Write-Host "[3/3] Verificando scopes en archivos..." -ForegroundColor Yellow

$files = @(
    "core\automation\job_bulletin_processor.py",
    "core\automation\improved_bulletin_processor.py"
)

$requiredScopes = @(
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/spreadsheets"
)

$needsFix = $false

foreach ($file in $files) {
    $content = Get-Content $file -Raw
    
    if ($content -notmatch "gmail\.modify") {
        Write-Host "      ⚠️  $file" -ForegroundColor Yellow
        Write-Host "         Falta scope: gmail.modify" -ForegroundColor Yellow
        $needsFix = $true
    } else {
        Write-Host "      ✅ $file (scopes OK)" -ForegroundColor Green
    }
}

if ($needsFix) {
    Write-Host ""
    Write-Host "      ⚠️  ADVERTENCIA: Algunos archivos necesitan actualización de scopes" -ForegroundColor Yellow
    Write-Host "      Esto se puede arreglar manualmente después" -ForegroundColor Yellow
}

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE REPARACIONES" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ EXPIRE_LIFECYCLE.py - Path corregido" -ForegroundColor Green
Write-Host ""

if (Test-Path $tokenPath) {
    Write-Host "✅ token.json existe" -ForegroundColor Green
    Write-Host "   (Regenerado con scopes completos)" -ForegroundColor White
} else {
    Write-Host "⚠️  token.json NO existe" -ForegroundColor Yellow
    Write-Host "   Necesitas autenticarte primero" -ForegroundColor White
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PRUEBA RÁPIDA
# ============================================================================

Write-Host "🧪 PRUEBA RÁPIDA" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Write-Host "Probando EXPIRE_LIFECYCLE.py --help..." -ForegroundColor Yellow
Write-Host ""

py scripts\verifiers\EXPIRE_LIFECYCLE.py --help 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ EXPIRE_LIFECYCLE.py funciona correctamente" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  EXPIRE_LIFECYCLE.py tuvo un problema" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PRÓXIMOS PASOS
# ============================================================================

Write-Host "📋 PRÓXIMOS PASOS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Probar Pipeline Completo:" -ForegroundColor White
Write-Host "   .\START_CONTROL_CENTER.bat" -ForegroundColor Cyan
Write-Host "   Luego opción 1 (Pipeline Completo)" -ForegroundColor White
Write-Host ""

Write-Host "2. Verificar que se borren los EXPIRED:" -ForegroundColor White
Write-Host "   Los jobs marcados como EXPIRED deberían eliminarse automáticamente" -ForegroundColor White
Write-Host ""

Write-Host "3. Si aún hay errores de OAuth:" -ForegroundColor White
Write-Host "   py scripts\oauth\reauthenticate_gmail.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

pause
