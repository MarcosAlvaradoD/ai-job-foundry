# ==============================================================================
# DIAGNÓSTICO COMPLETO - EXPIRE_LIFECYCLE + Nuevo Error
# ==============================================================================

Write-Host ""
Write-Host "🔍 DIAGNÓSTICO AI JOB FOUNDRY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

# ===============================
# TEST 1: Verificar EXPIRE_LIFECYCLE funciona
# ===============================
Write-Host "[1/5] Probando EXPIRE_LIFECYCLE.py directamente..." -ForegroundColor Yellow
Write-Host ""

try {
    $output = py scripts\verifiers\EXPIRE_LIFECYCLE.py --help 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Script ejecuta correctamente" -ForegroundColor Green
        Write-Host "     Output:" -ForegroundColor Gray
        Write-Host "     $($output[0..3] -join "`n     ")" -ForegroundColor Gray
    } else {
        Write-Host "  ❌ Error al ejecutar script:" -ForegroundColor Red
        Write-Host "     $output" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Excepción: $_" -ForegroundColor Red
}

Write-Host ""

# ===============================
# TEST 2: Ver qué jobs hay marcados EXPIRED
# ===============================
Write-Host "[2/5] Verificando jobs marcados como EXPIRED..." -ForegroundColor Yellow
Write-Host ""

$pythonCheck = @"
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path.cwd()
load_dotenv(project_root / '.env')

from core.sheets.sheet_manager import SheetManager

def check_expired_jobs():
    manager = SheetManager()
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    tabs = ['Glassdoor', 'LinkedIn', 'Indeed']
    total_expired = 0
    
    for tab in tabs:
        try:
            result = manager.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f'{tab}!A1:Z1000'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                continue
            
            headers = values[0]
            rows = values[1:]
            
            if 'Status' not in headers:
                print(f"{tab}: No Status column")
                continue
            
            status_idx = headers.index('Status')
            
            expired_count = 0
            for row in rows:
                if len(row) > status_idx and row[status_idx] == 'EXPIRED':
                    expired_count += 1
            
            print(f"{tab}: {expired_count} jobs marcados EXPIRED")
            total_expired += expired_count
            
        except Exception as e:
            print(f"{tab}: Error - {str(e)[:50]}")
    
    print(f"\nTOTAL: {total_expired} jobs EXPIRED esperando eliminación")
    return total_expired

if __name__ == '__main__':
    check_expired_jobs()
"@

$pythonCheck | Out-File -FilePath "temp_check_expired.py" -Encoding UTF8
py temp_check_expired.py
Remove-Item "temp_check_expired.py" -Force -ErrorAction SilentlyContinue

Write-Host ""

# ===============================
# TEST 3: Ejecutar --delete manualmente
# ===============================
Write-Host "[3/5] Ejecutando EXPIRE_LIFECYCLE --delete manualmente..." -ForegroundColor Yellow
Write-Host ""

try {
    $deleteOutput = py scripts\verifiers\EXPIRE_LIFECYCLE.py --delete 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Comando ejecutó sin errores" -ForegroundColor Green
        Write-Host ""
        Write-Host "     Output completo:" -ForegroundColor Gray
        Write-Host "     $($deleteOutput -join "`n     ")" -ForegroundColor Gray
    } else {
        Write-Host "  ❌ Comando falló con código: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "     $deleteOutput" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Excepción: $_" -ForegroundColor Red
}

Write-Host ""

# ===============================
# TEST 4: Verificar path en run_daily_pipeline.py
# ===============================
Write-Host "[4/5] Verificando path en run_daily_pipeline.py..." -ForegroundColor Yellow
Write-Host ""

$pipelineContent = Get-Content "run_daily_pipeline.py" -Raw

if ($pipelineContent -match "expire_script\s*=\s*project_root\s*/\s*'scripts'") {
    Write-Host "  ✅ Path usa project_root / 'scripts'" -ForegroundColor Green
} elseif ($pipelineContent -match "scripts/verifiers/EXPIRE_LIFECYCLE") {
    Write-Host "  ⚠️  Path usa forward slashes (puede fallar)" -ForegroundColor Yellow
} else {
    Write-Host "  ❓ No se encontró llamada a EXPIRE_LIFECYCLE" -ForegroundColor Gray
}

Write-Host ""

# ===============================
# TEST 5: Verificar último pipeline execution
# ===============================
Write-Host "[5/5] Buscando evidencia de último pipeline..." -ForegroundColor Yellow
Write-Host ""

# Buscar logs recientes
$recentLogs = Get-ChildItem "logs\powershell" -Filter "session_*.log" | 
              Sort-Object LastWriteTime -Descending | 
              Select-Object -First 3

if ($recentLogs) {
    Write-Host "  📋 Últimos 3 logs encontrados:" -ForegroundColor Cyan
    foreach ($log in $recentLogs) {
        $age = (Get-Date) - $log.LastWriteTime
        Write-Host "     - $($log.Name) ($($age.Days) días atrás)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "  🔍 Buscando 'EXPIRE_LIFECYCLE' en último log..." -ForegroundColor Cyan
    
    $lastLog = $recentLogs[0]
    $logContent = Get-Content $lastLog.FullName -Tail 100
    
    $expireLines = $logContent | Select-String -Pattern "EXPIRE|expire|Cleanup|cleanup"
    
    if ($expireLines) {
        Write-Host "     Encontrado:" -ForegroundColor Green
        $expireLines | ForEach-Object {
            Write-Host "     $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "     No se encontró referencia a EXPIRE_LIFECYCLE" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  No se encontraron logs recientes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 DIAGNÓSTICO COMPLETADO" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

pause
