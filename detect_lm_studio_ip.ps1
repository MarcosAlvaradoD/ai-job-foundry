# ============================================================================
# LM STUDIO CONFIG - Versión simplificada (IP fija = localhost)
# ============================================================================
# LM Studio corre en esta misma máquina → siempre localhost
# Puerto fijo: 1234 (LM Studio → Developer → Server Settings)
# Docker containers: host.docker.internal:1234
# Scripts Windows:   localhost:1234
# ============================================================================

$LM_PORT = 1234
$LM_URL  = "http://localhost:$LM_PORT/v1"

Write-Host "LM Studio URL: $LM_URL" -ForegroundColor Cyan

# Verificar que LM Studio está corriendo
try {
    $r = Invoke-WebRequest -Uri "http://localhost:$LM_PORT/v1/models" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "LM Studio OK" -ForegroundColor Green
} catch {
    Write-Host "AVISO: LM Studio no responde en :$LM_PORT — usando Claude API como fallback." -ForegroundColor Yellow
}

# Actualizar .env de ai-job-foundry
$envPath = Join-Path $PSScriptRoot ".env"
if (Test-Path $envPath) {
    $env = Get-Content $envPath -Raw
    $env = $env -replace "LM_STUDIO_URL=http://[^\r\n]+", "LM_STUDIO_URL=$LM_URL"
    $env = $env -replace "LLM_URL=http://[^\r\n]+",       "LLM_URL=http://localhost:$LM_PORT/v1/chat/completions"
    Set-Content -Path $envPath -Value $env -NoNewline
    Write-Host ".env actualizado: localhost:$LM_PORT" -ForegroundColor Green
}
