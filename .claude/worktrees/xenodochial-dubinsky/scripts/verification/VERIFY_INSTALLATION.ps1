# =====================================================================
# AI JOB FOUNDRY - PRE-LAUNCH VERIFICATION SCRIPT
# Verifica que todos los archivos están en su lugar antes de ejecutar
# =====================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  AI JOB FOUNDRY - PRE-LAUNCH VERIFICATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# =====================================================================
# 1. VERIFICAR ARCHIVOS PRINCIPALES
# =====================================================================
Write-Host "[1/5] Verificando archivos principales..." -ForegroundColor Yellow
Write-Host ""

$requiredFiles = @(
    "unified_app\app.py",
    "unified_app\templates\index.html",
    "START_UNIFIED_APP.bat",
    "run_auto_apply.py",
    "core\automation\auto_apply_linkedin.py",
    "PROJECT_STATUS.md",
    "QUICK_START_UNIFIED.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""

# =====================================================================
# 2. VERIFICAR DEPENDENCIAS PYTHON
# =====================================================================
Write-Host "[2/5] Verificando dependencias Python..." -ForegroundColor Yellow
Write-Host ""

$pythonModules = @(
    "flask",
    "playwright",
    "gspread",
    "google-auth",
    "python-dotenv",
    "requests"
)

foreach ($module in $pythonModules) {
    $result = py -c "import $($module.Replace('-', '_'))" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $module installed" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $module not installed" -ForegroundColor Red
        Write-Host "         Run: pip install $module" -ForegroundColor Yellow
        $allGood = $false
    }
}

Write-Host ""

# =====================================================================
# 3. VERIFICAR ARCHIVOS DE CONFIGURACIÓN
# =====================================================================
Write-Host "[3/5] Verificando configuración..." -ForegroundColor Yellow
Write-Host ""

# Check .env
if (Test-Path ".env") {
    Write-Host "  [OK] .env file exists" -ForegroundColor Green
    
    # Check for critical env vars
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GOOGLE_SHEETS_ID") {
        Write-Host "  [OK] GOOGLE_SHEETS_ID configured" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] GOOGLE_SHEETS_ID not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [MISSING] .env file not found" -ForegroundColor Red
    $allGood = $false
}

# Check OAuth token
if (Test-Path "data\credentials\token.json") {
    Write-Host "  [OK] OAuth token exists" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] OAuth token not found - run reauthenticate_gmail_v2.py" -ForegroundColor Yellow
}

Write-Host ""

# =====================================================================
# 4. VERIFICAR LM STUDIO
# =====================================================================
Write-Host "[4/5] Verificando LM Studio..." -ForegroundColor Yellow
Write-Host ""

$lmUrls = @("http://localhost:11434", "http://172.23.0.1:11434")
$lmFound = $false

foreach ($url in $lmUrls) {
    try {
        $response = Invoke-WebRequest -Uri "$url/v1/models" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  [OK] LM Studio running at $url" -ForegroundColor Green
            $lmFound = $true
            break
        }
    } catch {
        # Silently continue
    }
}

if (-not $lmFound) {
    Write-Host "  [WARNING] LM Studio not detected" -ForegroundColor Yellow
    Write-Host "           Start LM Studio manually before running unified app" -ForegroundColor Yellow
}

Write-Host ""

# =====================================================================
# 5. VERIFICAR PUERTO 5555
# =====================================================================
Write-Host "[5/5] Verificando disponibilidad del puerto 5555..." -ForegroundColor Yellow
Write-Host ""

$portInUse = Get-NetTCPConnection -LocalPort 5555 -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host "  [WARNING] Port 5555 is in use" -ForegroundColor Yellow
    Write-Host "           Run this to free it:" -ForegroundColor Yellow
    Write-Host "           Get-Process -Id (Get-NetTCPConnection -LocalPort 5555).OwningProcess | Stop-Process -Force" -ForegroundColor Cyan
} else {
    Write-Host "  [OK] Port 5555 is available" -ForegroundColor Green
}

Write-Host ""

# =====================================================================
# RESUMEN FINAL
# =====================================================================
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "  [SUCCESS] All critical checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  You can now run:" -ForegroundColor White
    Write-Host "    START_UNIFIED_APP.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Or manually:" -ForegroundColor White
    Write-Host "    py unified_app\app.py" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "  [ERROR] Some critical checks failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please fix the issues above before running the app." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Wait for user
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
