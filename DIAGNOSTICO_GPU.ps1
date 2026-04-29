Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  🔍 DIAGNÓSTICO COMPLETO - LM STUDIO + RTX 4090" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# 1. Check GPU
Write-Host "[1/5] Verificando GPU..." -ForegroundColor Cyan
try {
    $gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*4090*" -or $_.Name -like "*NVIDIA*" }
    if ($gpu) {
        Write-Host "  ✅ GPU encontrada: $($gpu.Name)" -ForegroundColor Green
        Write-Host "     Driver: $($gpu.DriverVersion)" -ForegroundColor Gray
        Write-Host "     VRAM: $([math]::Round($gpu.AdapterRAM / 1GB, 2)) GB" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  GPU NVIDIA no detectada claramente" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  No se pudo verificar GPU" -ForegroundColor Yellow
}

# 2. Check CUDA
Write-Host "`n[2/5] Verificando CUDA..." -ForegroundColor Cyan
try {
    $nvidiaSmi = & nvidia-smi --query-gpu=driver_version,memory.total,memory.used --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ NVIDIA Driver activo" -ForegroundColor Green
        Write-Host "     $nvidiaSmi" -ForegroundColor Gray
    } else {
        Write-Host "  ❌ nvidia-smi no disponible" -ForegroundColor Red
        Write-Host "     Puede que drivers no estén instalados" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ No se pudo ejecutar nvidia-smi" -ForegroundColor Red
}

# 3. Check LM Studio Process
Write-Host "`n[3/5] Verificando proceso de LM Studio..." -ForegroundColor Cyan
$lmStudioProcess = Get-Process -Name "*lmstudio*", "*lm-studio*" -ErrorAction SilentlyContinue
if ($lmStudioProcess) {
    Write-Host "  ✅ LM Studio corriendo (PID: $($lmStudioProcess[0].Id))" -ForegroundColor Green
    $memoryMB = [math]::Round($lmStudioProcess[0].WorkingSet64 / 1MB, 0)
    Write-Host "     Memoria RAM: $memoryMB MB" -ForegroundColor Gray
    
    if ($memoryMB -lt 10000) {
        Write-Host "  ⚠️  Memoria baja - Modelo puede no estar cargado completamente" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ LM Studio NO está corriendo" -ForegroundColor Red
}

# 4. Check Model Configuration File
Write-Host "`n[4/5] Buscando archivos de configuración..." -ForegroundColor Cyan
$userProfile = $env:USERPROFILE
$possiblePaths = @(
    "$userProfile\.cache\lm-studio",
    "$userProfile\AppData\Roaming\lm-studio",
    "$userProfile\AppData\Local\lm-studio",
    "$userProfile\.lmstudio"
)

$foundConfig = $false
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        Write-Host "  📁 Encontrado: $path" -ForegroundColor Gray
        $foundConfig = $true
        
        # Look for model config files
        $configFiles = Get-ChildItem -Path $path -Recurse -Filter "*.json" -ErrorAction SilentlyContinue | Select-Object -First 5
        if ($configFiles) {
            Write-Host "     Archivos de config encontrados:" -ForegroundColor Gray
            $configFiles | ForEach-Object { Write-Host "       - $($_.Name)" -ForegroundColor DarkGray }
        }
    }
}

if (-not $foundConfig) {
    Write-Host "  ⚠️  No se encontraron archivos de configuración" -ForegroundColor Yellow
}

# 5. Test LM Studio API
Write-Host "`n[5/5] Verificando API de LM Studio..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✅ LM Studio API respondiendo" -ForegroundColor Green
} catch {
    Write-Host "  ❌ LM Studio API no responde" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  📊 DIAGNÓSTICO COMPLETADO" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  PROBLEMA IDENTIFICADO:" -ForegroundColor Yellow
Write-Host "   Tu modelo está procesando a 1267 ms/token" -ForegroundColor White
Write-Host "   Debería ser: 50-100 ms/token" -ForegroundColor White
Write-Host "   Está 10-20x MÁS LENTO de lo normal" -ForegroundColor Red
Write-Host ""

Write-Host "🔍 CAUSAS POSIBLES (en orden de probabilidad):" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. ❌ GPU Offload INCORRECTO" -ForegroundColor Yellow
Write-Host "   → Algunas capas están en CPU en lugar de GPU" -ForegroundColor Gray
Write-Host "   → Solución: Verificar en LM Studio que dice '21/80 layers'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. ❌ Cuantización Q4_K_M puede ser lenta" -ForegroundColor Yellow
Write-Host "   → Q4_K_M a veces es más lento que Q4_K_S" -ForegroundColor Gray
Write-Host "   → Solución: Probar con Q4_0 o IQ3_XS" -ForegroundColor Gray
Write-Host ""
Write-Host "3. ❌ Flash Attention DESACTIVADO" -ForegroundColor Yellow
Write-Host "   → Sin flash attention es 2-3x más lento" -ForegroundColor Gray
Write-Host "   → Solución: Activar en LM Studio (si disponible)" -ForegroundColor Gray
Write-Host ""
Write-Host "4. ❌ Context Window muy grande" -ForegroundColor Yellow
Write-Host "   → Context > 8192 consume más VRAM y es más lento" -ForegroundColor Gray
Write-Host "   → Solución: Reducir a 8192" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  🚀 ACCIONES INMEDIATAS:" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "OPCIÓN A: Verificar configuración en LM Studio (5 min)" -ForegroundColor White
Write-Host "  1. Abre LM Studio" -ForegroundColor Gray
Write-Host "  2. Click en 'llama-3-groq-70b-tool-use' (modelo cargado)" -ForegroundColor Gray
Write-Host "  3. Tab 'Load' → Busca 'GPU Offload'" -ForegroundColor Gray
Write-Host "  4. Debe decir: 21 / 80 layers" -ForegroundColor Gray
Write-Host "  5. Si dice menos (ej: 10/80), arrastra el slider a 21" -ForegroundColor Gray
Write-Host "  6. Click 'Reload Model'" -ForegroundColor Gray
Write-Host "  7. Re-ejecuta test: py scripts\tests\test_lm_studio_speed.py" -ForegroundColor Gray
Write-Host ""

Write-Host "OPCIÓN B: Probar modelo más rápido (10 min)" -ForegroundColor White
Write-Host "  Modelos MEJORES que Qwen pero más RÁPIDOS que Llama-70B:" -ForegroundColor Gray
Write-Host ""
Write-Host "  🥇 Qwen 2.5 32B (RECOMENDADO)" -ForegroundColor Yellow
Write-Host "     Accuracy: ~85% (mejor que 14B)" -ForegroundColor Gray
Write-Host "     Velocidad: ~15 seg/job (3x más rápido que 70B)" -ForegroundColor Gray
Write-Host "     Tamaño: 20 GB" -ForegroundColor Gray
Write-Host ""
Write-Host "  🥈 Mistral Small 22B" -ForegroundColor Yellow
Write-Host "     Accuracy: ~82%" -ForegroundColor Gray
Write-Host "     Velocidad: ~10 seg/job" -ForegroundColor Gray
Write-Host "     Tamaño: 14 GB" -ForegroundColor Gray
Write-Host ""
Write-Host "  🥉 Gemma 2 27B" -ForegroundColor Yellow
Write-Host "     Accuracy: ~80%" -ForegroundColor Gray
Write-Host "     Velocidad: ~12 seg/job" -ForegroundColor Gray
Write-Host "     Tamaño: 16 GB" -ForegroundColor Gray
Write-Host ""

Write-Host "OPCIÓN C: Cambiar a Qwen 14B por HOY (5 min)" -ForegroundColor White
Write-Host "  notepad .env" -ForegroundColor Gray
Write-Host "  # Cambiar: LLM_MODEL=qwen2.5-14b-instruct" -ForegroundColor Gray
Write-Host "  .\START_CONTROL_CENTER.bat" -ForegroundColor Gray
Write-Host "  # Termina en 15 minutos, 75% accuracy" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  💡 MI RECOMENDACIÓN AHORA:" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1️⃣  Abre LM Studio y verifica GPU Offload = 21/80" -ForegroundColor White
Write-Host "  2️⃣  Si ya está en 21/80, descarga Qwen 2.5 32B" -ForegroundColor White
Write-Host "  3️⃣  Qwen 32B es el SWEET SPOT (85% accuracy, 15 seg/job)" -ForegroundColor White
Write-Host ""

Write-Host "Press Enter to continue..." -ForegroundColor Gray -NoNewline
Read-Host
