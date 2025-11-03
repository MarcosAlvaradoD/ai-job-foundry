# ============================================
# REORGANIZAR PROYECTO - AI Job Foundry
# ============================================

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "  ORGANIZACION DE PROYECTO" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

$desktop = "$env:USERPROFILE\Desktop"
$projectRoot = "$desktop\ai-job-foundry"

# Crear estructura nueva
Write-Host "[+] Creando estructura de carpetas..." -ForegroundColor Green

$folders = @(
    "$projectRoot\core",                    # Núcleo del sistema
    "$projectRoot\core\jobs_pipeline",      # Scripts de Jobs/
    "$projectRoot\core\dev_foundry",        # Scripts de dev/
    "$projectRoot\core\tracker",            # JobTracker nuevo
    "$projectRoot\workflows",               # n8n workflows
    "$projectRoot\data",                    # Datos locales
    "$projectRoot\data\credentials",        # OAuth tokens
    "$projectRoot\data\applications",       # Estado de aplicaciones
    "$projectRoot\data\interviews",         # Logs de entrevistas
    "$projectRoot\logs",                    # Logs del sistema
    "$projectRoot\config",                  # Configuraciones
    "$projectRoot\docs",                    # Documentación
    "$projectRoot\tests"                    # Pruebas
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  [OK] $($folder.Replace($projectRoot, '.'))" -ForegroundColor Gray
    }
}

# Copiar archivos existentes (sin mover, por seguridad)
Write-Host "`n[+] Copiando archivos de Jobs/..." -ForegroundColor Green
if (Test-Path "$desktop\Jobs") {
    Copy-Item -Path "$desktop\Jobs\*.py" -Destination "$projectRoot\core\jobs_pipeline\" -ErrorAction SilentlyContinue
    Copy-Item -Path "$desktop\Jobs\cv_descriptor.txt" -Destination "$projectRoot\data\" -ErrorAction SilentlyContinue
    Write-Host "  [OK] Scripts Python copiados" -ForegroundColor Gray
}

Write-Host "`n[+] Copiando archivos de dev/..." -ForegroundColor Green
if (Test-Path "$desktop\dev") {
    Copy-Item -Path "$desktop\dev\*.py" -Destination "$projectRoot\core\dev_foundry\" -ErrorAction SilentlyContinue
    Copy-Item -Path "$desktop\dev\*.yaml" -Destination "$projectRoot\config\" -ErrorAction SilentlyContinue
    Copy-Item -Path "$desktop\dev\*.yml" -Destination "$projectRoot\config\" -ErrorAction SilentlyContinue
    Write-Host "  [OK] Scripts de dev copiados" -ForegroundColor Gray
}

Write-Host "`n[+] Copiando workflows de job_apply_mvp_v4/..." -ForegroundColor Green
if (Test-Path "$desktop\job_apply_mvp_v4") {
    Copy-Item -Path "$desktop\job_apply_mvp_v4\*.json" -Destination "$projectRoot\workflows\" -ErrorAction SilentlyContinue
    Copy-Item -Path "$desktop\job_apply_mvp_v4\*.yaml" -Destination "$projectRoot\workflows\" -ErrorAction SilentlyContinue
    Write-Host "  [OK] Workflows copiados" -ForegroundColor Gray
}

# Crear archivo de índice
Write-Host "`n[+] Generando PROJECT_INDEX.md..." -ForegroundColor Green

$indexContent = @"
# AI JOB FOUNDRY - ÍNDICE DE PROYECTO

**Fecha de consolidación:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Autor:** Marcos Alvarado
**Repositorio:** https://github.com/MarcosAlvaradoD/ai-job-foundry

---

## 📁 ESTRUCTURA DEL PROYECTO

``````
ai-job-foundry/
├── core/                      # Código principal
│   ├── jobs_pipeline/         # Pipeline de vacantes (desde Jobs/)
│   ├── dev_foundry/           # Sistema de autoprogramación (desde dev/)
│   └── tracker/               # Sistema de seguimiento (NUEVO)
│       ├── job_tracker.py
│       ├── interview_copilot.py
│       └── project_auditor.py
│
├── workflows/                 # Workflows de n8n
│   └── *.json
│
├── data/                      # Datos locales (NO subir a Git)
│   ├── credentials/           # OAuth tokens
│   ├── applications/          # Estado de aplicaciones
│   └── cv_descriptor.txt      # Tu CV
│
├── config/                    # Configuraciones
│   ├── devfoundry.yaml
│   └── models_registry.json
│
├── logs/                      # Logs del sistema
├── docs/                      # Documentación
└── tests/                     # Pruebas
``````

---

## 🔧 SCRIPTS PRINCIPALES

### Jobs Pipeline (core/jobs_pipeline/)
$(Get-ChildItem "$projectRoot\core\jobs_pipeline\*.py" -ErrorAction SilentlyContinue | ForEach-Object { "- ``$($_.Name)``" })

### Dev Foundry (core/dev_foundry/)
$(Get-ChildItem "$projectRoot\core\dev_foundry\*.py" -ErrorAction SilentlyContinue | ForEach-Object { "- ``$($_.Name)``" })

### JobTracker (core/tracker/)
- ``job_tracker.py`` - Monitor de comunicaciones
- ``interview_copilot.py`` - Asistente de entrevistas
- ``project_auditor.py`` - Auditor de estructura

---

## 📦 DEPENDENCIAS

Ver ``requirements.txt`` para lista completa.

Principales:
- google-auth
- google-api-python-client
- pandas
- requests
- whisper (para interview copilot)

---

## 🚀 INICIO RÁPIDO

1. Instalar dependencias:
   ``````bash
   pip install -r requirements.txt
   ``````

2. Configurar credenciales de Google:
   - Descargar ``credentials.json`` desde Google Cloud Console
   - Colocar en ``data/credentials/``

3. Ejecutar pipeline de vacantes:
   ``````bash
   python core/jobs_pipeline/daily_job_harvest.py
   ``````

4. Iniciar monitor de seguimiento:
   ``````bash
   python core/tracker/job_tracker.py
   ``````

---

## 📄 LICENCIA

MIT License with Commercial Clause
Copyright (c) 2025 Marcos Alvarado

Uso personal: GRATIS
Uso comercial: Requiere permiso y compensación

Contacto: markalvati@gmail.com

"@

Set-Content -Path "$projectRoot\PROJECT_INDEX.md" -Value $indexContent -Encoding UTF8

# Crear requirements.txt consolidado
Write-Host "`n[+] Generando requirements.txt..." -ForegroundColor Green

$requirements = @"
# AI Job Foundry - Dependencies
# Generated: $(Get-Date -Format "yyyy-MM-dd")

# Google APIs
google-auth==2.23.0
google-auth-oauthlib==1.1.0
google-api-python-client==2.100.0

# Data processing
pandas==2.1.1
openpyxl==3.1.2
numpy==1.25.2

# HTTP requests
requests==2.31.0

# Audio processing (Interview Copilot)
sounddevice==0.4.6
whisper==1.1.10

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1

# Optional (si usas FastAPI para dashboard)
fastapi==0.103.1
uvicorn==0.23.2
"@

Set-Content -Path "$projectRoot\requirements.txt" -Value $requirements -Encoding UTF8

# Resumen
Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "  ORGANIZACION COMPLETADA" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

Write-Host "Archivos organizados en: $projectRoot`n" -ForegroundColor Green

Write-Host "Siguiente paso:" -ForegroundColor Yellow
Write-Host "1. Revisa la carpeta: $projectRoot"
Write-Host "2. Si todo se ve bien, MUEVE (no copies) tus credenciales:"
Write-Host "   move $desktop\Jobs\credentials.json $projectRoot\data\credentials\"
Write-Host "3. Ejecuta: cd $projectRoot"
Write-Host "4. Ejecuta: git init"
Write-Host "5. Ejecuta: git add ."
Write-Host "6. Ejecuta: git commit -m 'Initial commit'"
Write-Host "`n"

Read-Host "Presiona Enter para continuar"