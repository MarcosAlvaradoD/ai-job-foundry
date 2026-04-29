# ============================================================================
# TEST RÁPIDO - Reauthenticate Gmail con Path Corregido
# ============================================================================

Write-Host ""
Write-Host "🔐 TEST DE RE-AUTENTICACIÓN GMAIL" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

# Verificar que credentials.json existe
Write-Host "[1/3] Verificando credentials.json..." -ForegroundColor Yellow

if (Test-Path "data\credentials\credentials.json") {
    Write-Host "      ✅ credentials.json encontrado en data\credentials\" -ForegroundColor Green
} else {
    Write-Host "      ❌ credentials.json NO encontrado" -ForegroundColor Red
    Write-Host "      Ubicación esperada: data\credentials\credentials.json" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Verificar si existe token.json
Write-Host ""
Write-Host "[2/3] Verificando token.json..." -ForegroundColor Yellow

if (Test-Path "data\credentials\token.json") {
    Write-Host "      ⚠️  token.json existente encontrado" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "      ¿Regenerar token.json? (s/n)"
    
    if ($response -eq "s") {
        # Backup
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item "data\credentials\token.json" "data\credentials\token.json.backup_$timestamp" -Force
        Write-Host "      💾 Backup: token.json.backup_$timestamp" -ForegroundColor Green
        
        # Eliminar
        Remove-Item "data\credentials\token.json" -Force
        Write-Host "      🗑️  token.json eliminado" -ForegroundColor Yellow
    } else {
        Write-Host "      ⏭️  Manteniendo token.json existente" -ForegroundColor Yellow
        Write-Host ""
        pause
        exit 0
    }
} else {
    Write-Host "      ℹ️  No existe token.json (se creará nuevo)" -ForegroundColor Cyan
}

# Ejecutar re-autenticación
Write-Host ""
Write-Host "[3/3] Ejecutando re-autenticación..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 INSTRUCCIONES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Se abrirá tu navegador automáticamente" -ForegroundColor White
Write-Host "2. Selecciona la cuenta: markalvati@gmail.com" -ForegroundColor White
Write-Host "3. Acepta los permisos (Gmail + Sheets)" -ForegroundColor White
Write-Host "4. Espera el mensaje de éxito" -ForegroundColor White
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "¿Listo para continuar? (Enter para continuar)"

Write-Host ""
Write-Host "🚀 Iniciando autenticación..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar script corregido
py scripts\oauth\reauthenticate_gmail.py

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "✅ RE-AUTENTICACIÓN EXITOSA!" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    
    if (Test-Path "data\credentials\token.json") {
        Write-Host "✅ token.json generado correctamente" -ForegroundColor Green
        
        # Mostrar tamaño
        $fileInfo = Get-Item "data\credentials\token.json"
        Write-Host "   Tamaño: $($fileInfo.Length) bytes" -ForegroundColor White
        Write-Host "   Fecha: $($fileInfo.LastWriteTime)" -ForegroundColor White
    } else {
        Write-Host "⚠️  token.json NO se generó" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "📋 PRÓXIMO PASO:" -ForegroundColor Cyan
    Write-Host "   .\START_CONTROL_CENTER.bat" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host "❌ ERROR EN RE-AUTENTICACIÓN" -ForegroundColor Red
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifica:" -ForegroundColor Yellow
    Write-Host "  1. Que credentials.json sea válido" -ForegroundColor White
    Write-Host "  2. Que hayas aceptado los permisos en el navegador" -ForegroundColor White
    Write-Host "  3. Que uses la cuenta correcta: markalvati@gmail.com" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
pause
