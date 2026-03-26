# ============================================================================
# DETECT & LOAD LM STUDIO MODEL - Auto-detecta IP y carga modelo
# ============================================================================
# Ubicacion: C:\Users\MSI\Desktop\ai-job-foundry\detect_lm_studio_ip.ps1
#
# Proposito:
# - Detecta automaticamente en que IP esta corriendo LM Studio
# - Verifica que el modelo este cargado
# - Si no hay modelo, muestra instrucciones para cargarlo
# - Actualiza el .env con la IP correcta
#
# Uso:
#   .\detect_lm_studio_ip.ps1
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DETECTING LM STUDIO IP & MODEL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# IPs comunes a probar (en orden de probabilidad)
$possibleIPs = @(
    "192.168.100.28",      # IP WSL/Red Local de Marcos (PRIORIDAD)
    "127.0.0.1",           # Localhost (fallback)
    "172.23.0.1",          # IP Docker común
    "192.168.100.42",      # IP WSL alternativa
    "192.168.1.100",       # Otra IP WSL posible
    "localhost"
)

$port = 11434
$foundIP = $null

# Probar cada IP
Write-Host "Testing possible LM Studio IPs..." -ForegroundColor Yellow
Write-Host ""

foreach ($ip in $possibleIPs) {
    $url = "http://${ip}:${port}/v1/models"
    
    Write-Host "   Testing ${ip}:${port}... " -NoNewline
    
    try {
        # Timeout de 2 segundos por IP
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host "FOUND!" -ForegroundColor Green
            $foundIP = $ip
            break
        }
    }
    catch {
        Write-Host "Not responding" -ForegroundColor Red
    }
}

if ($null -eq $foundIP) {
    Write-Host ""
    Write-Host "ERROR: LM Studio not found on any known IP!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Yellow
    Write-Host "   1. Make sure LM Studio is running" -ForegroundColor White
    Write-Host "   2. Check LM Studio server settings (should be on port 11434)" -ForegroundColor White
    Write-Host "   3. Manually check the IP in LM Studio interface" -ForegroundColor White
    Write-Host ""
    exit 1
}

# IP encontrada - actualizar .env
Write-Host ""
Write-Host "LM Studio found at: ${foundIP}:${port}" -ForegroundColor Green
Write-Host ""

$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found at: $envFile" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "Updating .env file..." -ForegroundColor Yellow
Write-Host ""

# Leer contenido actual
$envContent = Get-Content $envFile

# Nueva URL
$newLLMUrl = "http://${foundIP}:${port}/v1/chat/completions"

# Actualizar LLM_URL
$updated = $false
$newContent = @()

foreach ($line in $envContent) {
    if ($line -match "^LLM_URL=") {
        $newContent += "LLM_URL=$newLLMUrl"
        $updated = $true
        Write-Host "   Updated: LLM_URL=$newLLMUrl" -ForegroundColor Green
    }
    else {
        $newContent += $line
    }
}

# Si no existia LLM_URL, agregarlo
if (-not $updated) {
    $newContent += "LLM_URL=$newLLMUrl"
    Write-Host "   Added: LLM_URL=$newLLMUrl" -ForegroundColor Green
}

# Guardar archivo actualizado con retry logic
$maxRetries = 5
$retryCount = 0
$saved = $false

while (-not $saved -and $retryCount -lt $maxRetries) {
    try {
        $newContent | Set-Content $envFile -Encoding UTF8 -ErrorAction Stop
        $saved = $true
    }
    catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "   Warning: File is locked, retrying ($retryCount/$maxRetries)..." -ForegroundColor Yellow
            Start-Sleep -Milliseconds 500
        }
        else {
            Write-Host "   ERROR: Could not update .env after $maxRetries attempts" -ForegroundColor Red
            Write-Host "   Please close any programs that might have .env open (VSCode, editors)" -ForegroundColor Yellow
            exit 1
        }
    }
}

if ($saved) {
    Write-Host ""
    Write-Host ".env file updated successfully!" -ForegroundColor Green
    Write-Host ""
}

# Verificar que el modelo este cargado
Write-Host "Checking loaded models..." -ForegroundColor Yellow
Write-Host ""

$modelLoaded = $false
$requiredModel = "qwen2.5-14b-instruct"

try {
    $testUrl = "http://${foundIP}:${port}/v1/models"
    $response = Invoke-RestMethod -Uri $testUrl -TimeoutSec 5
    
    if ($response.data -and $response.data.Count -gt 0) {
        $modelCount = $response.data.Count
        Write-Host "   Found $modelCount models loaded:" -ForegroundColor Green
        
        foreach ($model in $response.data) {
            $modelName = $model.id
            Write-Host "      * $modelName" -ForegroundColor White
            
            # Verificar si es el modelo requerido
            if ($modelName -like "*qwen*" -and $modelName -like "*14b*") {
                $modelLoaded = $true
            }
        }
        Write-Host ""
    }
    else {
        Write-Host "   WARNING: No models loaded in LM Studio!" -ForegroundColor Yellow
        Write-Host ""
    }
}
catch {
    Write-Host "   WARNING: Could not check models list" -ForegroundColor Yellow
    Write-Host "   LM Studio might need a moment to fully load." -ForegroundColor Yellow
    Write-Host ""
}

# Si no hay modelo cargado, mostrar instrucciones
if (-not $modelLoaded) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "ACTION REQUIRED: Load Model in LM Studio" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The required model is NOT loaded. Please:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open LM Studio application" -ForegroundColor White
    Write-Host "2. Go to 'My Models' or 'Discover' tab" -ForegroundColor White
    Write-Host "3. Load model: Qwen 2.5 14B Instruct (GGUF)" -ForegroundColor White
    Write-Host "   Search for: 'qwen2.5-14b-instruct'" -ForegroundColor White
    Write-Host "4. Click 'Load to Server' button" -ForegroundColor White
    Write-Host "5. Wait until it shows 'Loaded' status" -ForegroundColor White
    Write-Host ""
    Write-Host "Once loaded, re-run this script or start_all.ps1" -ForegroundColor Cyan
    Write-Host ""
    
    # No exit, permitir continuar pero advertir
    Write-Host "Continuing anyway, but AI functions may fail..." -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 3
}
else {
    Write-Host "OK: Qwen model is loaded and ready!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LM Studio Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "LM Studio URL: $newLLMUrl" -ForegroundColor Yellow
Write-Host ""
