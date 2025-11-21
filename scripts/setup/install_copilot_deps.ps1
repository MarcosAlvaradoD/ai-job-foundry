# ========================================================================
# INSTALACIÓN AUTOMÁTICA - INTERVIEW COPILOT SESSION RECORDER
# Instala todas las dependencias necesarias para Windows
# ========================================================================

Write-Host "=" * 70
Write-Host "🎤 INSTALANDO INTERVIEW COPILOT SESSION RECORDER" -ForegroundColor Cyan
Write-Host "=" * 70

# Verificar si estamos en admin mode
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`n[WARNING] No estás ejecutando como administrador" -ForegroundColor Yellow
    Write-Host "[INFO] Algunas funcionalidades (hotkeys) requieren permisos de admin" -ForegroundColor Yellow
    $continue = Read-Host "`n¿Continuar de todas formas? (y/n)"
    if ($continue -ne 'y') {
        exit
    }
}

Write-Host "`n[INFO] Verificando Python..." -ForegroundColor Green
py --version

Write-Host "`n[1/5] Instalando Whisper..." -ForegroundColor Cyan
pip install openai-whisper

Write-Host "`n[2/5] Instalando NumPy..." -ForegroundColor Cyan
pip install numpy

Write-Host "`n[3/5] Instalando keyboard..." -ForegroundColor Cyan
pip install keyboard

Write-Host "`n[4/5] Instalando wave (built-in, verificando)..." -ForegroundColor Cyan
py -c "import wave; print('[OK] wave disponible')"

Write-Host "`n[5/5] Instalando PyAudio (puede requerir pasos adicionales)..." -ForegroundColor Cyan
Write-Host "[INFO] Intentando instalación estándar..." -ForegroundColor Yellow

$pyaudioInstalled = $false

try {
    pip install pyaudio 2>&1 | Out-Null
    py -c "import pyaudio; print('[OK] PyAudio instalado')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $pyaudioInstalled = $true
        Write-Host "[OK] PyAudio instalado correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Instalación estándar de PyAudio falló" -ForegroundColor Yellow
}

if (-not $pyaudioInstalled) {
    Write-Host "`n[INFO] PyAudio requiere instalación manual en Windows" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPCIONES:" -ForegroundColor Cyan
    Write-Host "1. Descargar wheel pre-compilado:"
    Write-Host "   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio"
    Write-Host "   Busca: PyAudio-0.2.13-cp313-cp313-win_amd64.whl"
    Write-Host "   Instala: pip install PyAudio-0.2.13-cp313-cp313-win_amd64.whl"
    Write-Host ""
    Write-Host "2. Usar pipwin:"
    Write-Host "   pip install pipwin"
    Write-Host "   pipwin install pyaudio"
    Write-Host ""
    Write-Host "3. Si usas Anaconda:"
    Write-Host "   conda install pyaudio"
    Write-Host ""
}

Write-Host "`n" + "=" * 70
Write-Host "✅ VERIFICACIÓN FINAL" -ForegroundColor Cyan
Write-Host "=" * 70

Write-Host "`nVerificando dependencias..." -ForegroundColor Yellow

$allOk = $true

# Whisper
try {
    py -c "import whisper; print('✅ Whisper')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Whisper instalado" -ForegroundColor Green
    } else {
        Write-Host "❌ Whisper NO instalado" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ Whisper NO instalado" -ForegroundColor Red
    $allOk = $false
}

# NumPy
try {
    py -c "import numpy; print('✅ NumPy')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ NumPy instalado" -ForegroundColor Green
    } else {
        Write-Host "❌ NumPy NO instalado" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ NumPy NO instalado" -ForegroundColor Red
    $allOk = $false
}

# Keyboard
try {
    py -c "import keyboard; print('✅ keyboard')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ keyboard instalado" -ForegroundColor Green
    } else {
        Write-Host "❌ keyboard NO instalado" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ keyboard NO instalado" -ForegroundColor Red
    $allOk = $false
}

# PyAudio
try {
    py -c "import pyaudio; print('✅ PyAudio')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PyAudio instalado" -ForegroundColor Green
    } else {
        Write-Host "❌ PyAudio NO instalado (requiere instalación manual)" -ForegroundColor Red
        $allOk = $false
    }
} catch {
    Write-Host "❌ PyAudio NO instalado (requiere instalación manual)" -ForegroundColor Red
    $allOk = $false
}

Write-Host "`n" + "=" * 70

if ($allOk) {
    Write-Host "🎉 INSTALACIÓN COMPLETA - TODO OK" -ForegroundColor Green
    Write-Host ""
    Write-Host "PRÓXIMO PASO:" -ForegroundColor Cyan
    Write-Host "py interview_copilot_session_recorder.py"
} else {
    Write-Host "⚠️ INSTALACIÓN INCOMPLETA" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Revisa los errores arriba y sigue las instrucciones" -ForegroundColor Yellow
    Write-Host "Documentación completa: docs\INTERVIEW_COPILOT_SESSION_RECORDER.md"
}

Write-Host "=" * 70
