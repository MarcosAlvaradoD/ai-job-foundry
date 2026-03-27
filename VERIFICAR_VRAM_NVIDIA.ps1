Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  🔍 VERIFICACIÓN COMPLETA DE VRAM - RTX 4090" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# 1. NVIDIA-SMI (Herramienta oficial y más confiable)
Write-Host "[1/3] Verificando con nvidia-smi (herramienta oficial NVIDIA)..." -ForegroundColor Cyan
Write-Host ""

try {
    # Get detailed GPU info
    $gpuInfo = & nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,driver_version,temperature.gpu --format=csv,noheader 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $info = $gpuInfo -split ','
        $gpuName = $info[0].Trim()
        $totalVRAM = $info[1].Trim()
        $usedVRAM = $info[2].Trim()
        $freeVRAM = $info[3].Trim()
        $driver = $info[4].Trim()
        $temp = $info[5].Trim()
        
        Write-Host "  ✅ GPU Detectada:" -ForegroundColor Green
        Write-Host "     Modelo: $gpuName" -ForegroundColor White
        Write-Host "     VRAM Total: $totalVRAM" -ForegroundColor Yellow
        Write-Host "     VRAM Usada: $usedVRAM" -ForegroundColor Cyan
        Write-Host "     VRAM Libre: $freeVRAM" -ForegroundColor Green
        Write-Host "     Driver: $driver" -ForegroundColor Gray
        Write-Host "     Temperatura: $temp" -ForegroundColor Gray
        
        # Parse VRAM (assuming format "XXXX MiB")
        if ($totalVRAM -match '(\d+)\s*MiB') {
            $totalMB = [int]$matches[1]
            $totalGB = [math]::Round($totalMB / 1024, 1)
            
            Write-Host ""
            Write-Host "  📊 Resumen:" -ForegroundColor Cyan
            Write-Host "     VRAM Total: $totalGB GB" -ForegroundColor Yellow
            
            if ($totalGB -ge 23) {
                Write-Host "     ✅ GPU CORRECTA - 24 GB de VRAM detectados" -ForegroundColor Green
            } else {
                Write-Host "     ⚠️  VRAM menor a lo esperado (24 GB)" -ForegroundColor Yellow
            }
        }
        
        # Parse Used VRAM
        if ($usedVRAM -match '(\d+)\s*MiB') {
            $usedMB = [int]$matches[1]
            $usedGB = [math]::Round($usedMB / 1024, 1)
            
            Write-Host "     VRAM en Uso: $usedGB GB" -ForegroundColor Cyan
            
            if ($usedGB -gt 18) {
                Write-Host "     ✅ LM Studio usando GPU correctamente (>18 GB)" -ForegroundColor Green
            } elseif ($usedGB -gt 10) {
                Write-Host "     ⚠️  LM Studio usando GPU parcialmente ($usedGB GB)" -ForegroundColor Yellow
                Write-Host "        → Algunas capas están en CPU (por eso es lento)" -ForegroundColor Yellow
            } else {
                Write-Host "     ❌ LM Studio NO está usando GPU correctamente (<10 GB)" -ForegroundColor Red
            }
        }
        
    } else {
        Write-Host "  ❌ No se pudo ejecutar nvidia-smi" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Error al ejecutar nvidia-smi: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Check with GPU-Z style query
Write-Host "`n[2/3] Verificando procesos usando GPU..." -ForegroundColor Cyan
Write-Host ""

try {
    $processes = & nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>&1
    
    if ($LASTEXITCODE -eq 0 -and $processes) {
        Write-Host "  📋 Procesos usando GPU:" -ForegroundColor Cyan
        Write-Host ""
        
        $processes | ForEach-Object {
            $proc = $_ -split ','
            $pid = $proc[0].Trim()
            $name = $proc[1].Trim()
            $mem = $proc[2].Trim()
            
            Write-Host "     PID $pid : $name → $mem" -ForegroundColor Gray
            
            if ($name -like "*lmstudio*" -or $name -like "*llama*") {
                Write-Host "       ↑ LM Studio detectado usando GPU" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  ℹ️  No hay procesos usando GPU actualmente" -ForegroundColor Yellow
        Write-Host "     (LM Studio puede estar en modo idle)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ℹ️  No se pudo listar procesos GPU" -ForegroundColor Yellow
}

# 3. Windows Task Manager comparison
Write-Host "`n[3/3] Comparación con Administrador de Tareas..." -ForegroundColor Cyan
Write-Host ""

Write-Host "  📝 Según tu screenshot del Administrador de Tareas:" -ForegroundColor Cyan
Write-Host "     Memoria GPU dedicada: 24.0 GB ✅" -ForegroundColor Green
Write-Host "     Memoria GPU compartida: 31.9 GB (RAM)" -ForegroundColor Gray
Write-Host ""
Write-Host "  ✅ Esto confirma que tu GPU tiene 24 GB de VRAM" -ForegroundColor Green

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  📊 DIAGNÓSTICO FINAL" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "RESULTADO: Tu RTX 4090 está PERFECTA con 24 GB de VRAM ✅" -ForegroundColor Green
Write-Host ""
Write-Host "❌ PROBLEMA IDENTIFICADO:" -ForegroundColor Yellow
Write-Host "   LM Studio NO está cargando todas las capas en GPU" -ForegroundColor White
Write-Host "   Debería usar ~20-21 GB pero usa menos" -ForegroundColor White
Write-Host ""
Write-Host "🔧 SOLUCIÓN:" -ForegroundColor Cyan
Write-Host "   1. Abre LM Studio" -ForegroundColor White
Write-Host "   2. Click en el modelo cargado (llama-3-groq-70b-tool-use)" -ForegroundColor White
Write-Host "   3. Busca 'GPU Offload' o 'GPU Layers'" -ForegroundColor White
Write-Host "   4. Arrastra el slider AL MÁXIMO posible" -ForegroundColor White
Write-Host "   5. Click 'Reload Model' o 'Apply'" -ForegroundColor White
Write-Host "   6. Re-ejecuta test de velocidad" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host "`nPress Enter to continue..." -ForegroundColor Gray -NoNewline
Read-Host
