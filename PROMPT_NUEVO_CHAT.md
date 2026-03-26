# 🔄 PROMPT PARA NUEVO CHAT - AI JOB FOUNDRY

**COPIAR ESTE CONTENIDO AL INICIAR NUEVO CHAT**

---

## 📋 CONTEXTO GENERAL DEL PROYECTO

Hola Claude. Soy **Marcos Alberto Alvarado de la Torre**, estoy desarrollando **AI Job Foundry**, un sistema automatizado de búsqueda de empleo que:

1. Scrapea ofertas de LinkedIn/Indeed/Glassdoor
2. Procesa emails de reclutadores y boletines de job boards
3. Analiza match con AI local (LM Studio + Qwen 2.5 14B)
4. Calcula FIT SCORES (0-10) con penalties de salario
5. Guarda todo en Google Sheets
6. Auto-aplica a ofertas calificadas (FIT >= 7)
7. Gestiona ofertas expiradas automáticamente

**Progreso actual:** 99% funcional ✅  
**Ubicación proyecto:** `C:\Users\MSI\Desktop\ai-job-foundry`

---

## 👤 SOBRE MÍ (MARCOS)

**Roles objetivo:**
- Project Manager
- Product Owner
- Senior Business Analyst
- IT Manager
- BI Lead

**NO busco:** Software Developer/Programmer positions

**Experiencia clave:**
- ERP migrations (10+ años)
- ETL & Data Migration (800+ TB procesados)
- IT Infrastructure (LATAM)
- BI/Power BI
- Business Analysis
- Project Management

**Prioridades:**
- Remote work (familia con bebé Máximo)
- Guadalajara, México (CST, GMT-6)
- Salario mínimo aceptable: $30,000 MXN/mes (~$1,700 USD)

---

## 💻 TECH STACK

**AI & ML:**
- **LM Studio** (local) - Qwen 2.5 14B Instruct (Q4_K_M, 8.99 GB)
  - URL: http://172.23.0.1:11434
  - Model: `qwen2.5-14b-instruct`
- **Gemini API** (fallback via LiteLLM)
- **Whisper** (transcription para Interview Copilot)

**Backend:**
- Python 3.13
- Google APIs (Sheets, Gmail, Calendar)
- OAuth 2.0 con auto-renewal ✅
- Flask (dashboard backend)

**Scraping:**
- Playwright (Firefox stealth mode)
- LinkedIn, Indeed scrapers

**Database:**
- Google Sheets como database principal
- Sheet ID: `1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg`

**Automation:**
- PowerShell scripts (Windows 11)
- n8n workflows (opcional)
- Task Scheduler (pendiente setup)

**Hardware:**
- RTX 4090 24GB
- 64GB RAM
- i9-14900K
- Windows 11

---

## 📂 ESTRUCTURA DEL PROYECTO

```
C:\Users\MSI\Desktop\ai-job-foundry\
│
├── 🎯 ARCHIVOS PRINCIPALES (RAÍZ)
│   ├── control_center.py          # ✅ Menú principal (19 opciones)
│   ├── run_daily_pipeline.py      # ✅ Pipeline diario (--all, --quick, etc)
│   ├── oauth_token_validator.py   # ✅ OAuth auto-renewal
│   ├── main.py                     # Redirector a control_center.py
│   ├── .env                        # Variables de entorno
│   ├── TEST_OAUTH_FLOW.ps1         # Test OAuth flow
│   └── *.ps1                       # PowerShell automation scripts
│
├── core/
│   ├── ingestion/
│   │   ├── linkedin_scraper_V2.py       # ✅ LinkedIn scraper (FINAL)
│   │   └── indeed_scraper.py            # ⚠️ Timeout issues
│   │
│   ├── enrichment/
│   │   ├── ai_analyzer.py               # ✅ AI FIT score analysis
│   │   └── cover_letter_gen.py          # 60% funcional
│   │
│   ├── sheets/
│   │   └── sheet_manager.py             # ✅ Google Sheets manager
│   │
│   ├── automation/
│   │   ├── job_bulletin_processor.py    # ✅ Procesa boletines (LinkedIn/Indeed/Glassdoor)
│   │   ├── auto_apply_linkedin.py       # ✅ LinkedIn auto-apply
│   │   └── gmail_monitor.py             # Monitoreo Gmail
│   │
│   ├── copilot/
│   │   └── interview_copilot_v2.py      # ✅ Interview assistant
│   │
│   └── utils/
│       ├── llm_client.py                # ✅ Multi-provider LLM client
│       └── oauth_validator.py           # ✅ OAuth utilities
│
├── scripts/
│   ├── oauth/
│   │   ├── reauthenticate_gmail_v2.py   # ✅ OAuth renewal (bug fix aplicado)
│   │   └── validate_oauth_v2.py         # ✅ OAuth validator
│   │
│   ├── verifiers/
│   │   ├── EXPIRE_LIFECYCLE.py          # ✅ Expire management (--mark, --delete, --full)
│   │   ├── LINKEDIN_SMART_VERIFIER_V3.py  # LinkedIn job verification
│   │   ├── INDEED_SMART_VERIFIER.py     # Indeed verification
│   │   └── GLASSDOOR_SMART_VERIFIER.py  # Glassdoor verification
│   │
│   ├── maintenance/
│   │   ├── recalculate_fit_scores.py    # ✅ FIT score recalc con salarios
│   │   ├── mark_expired_jobs.py         # Marca expirados
│   │   └── update_status_from_emails.py # Status updates
│   │
│   ├── powershell/
│   │   └── startup_check_v3.ps1         # ✅ Service verification
│   │
│   └── testing/
│       ├── test_email_processing.py
│       ├── visual_test.py
│       └── test_lm_studio_internet.py
│
├── data/
│   ├── credentials/
│   │   ├── token.json               # ✅ OAuth token (auto-renewed)
│   │   └── credentials.json         # OAuth client credentials
│   │
│   ├── cv/
│   │   └── cv_marcos.md             # Tu CV en markdown
│   │
│   └── cache/
│       └── processed_emails.json    # Cache de emails procesados
│
├── docs/
│   ├── PROJECT_STATUS.md            # ✅ Estado actual (99%)
│   ├── QUICKSTART_OAUTH_VALIDATOR.md  # Guía OAuth
│   ├── README_OAUTH_VALIDATOR.md
│   └── INTEGRACION_OAUTH_VALIDATOR.md
│
├── logs/
│   └── powershell/
│       └── session_*.log            # Logs de sesiones
│
└── web/
    └── dashboard_secure.html        # Dashboard frontend
```

---

## 🎯 ESTADO ACTUAL (99% FUNCIONAL)

### ✅ LO QUE FUNCIONA PERFECTO (99%)

#### 1. **OAuth Auto-Renewal** ✅ 100%
**Archivo:** `oauth_token_validator.py` (raíz)

**Flujo automático:**
```
Token expirado detectado
→ Ejecuta scripts/oauth/reauthenticate_gmail_v2.py
→ Abre navegador Google OAuth
→ Usuario autoriza (120 seg timeout)
→ Verifica token.json creado
→ Valida campos requeridos
→ Continúa pipeline automáticamente
```

**Características:**
- Detecta token expirado automáticamente
- Abre navegador sin intervención manual
- Espera autorización del usuario
- Verifica que el nuevo token funciona
- Continúa pipeline sin reiniciar
- **SIN ERRORES `invalid_grant` NUNCA MÁS**

#### 2. **Daily Pipeline** ✅ 100%
**Archivo:** `run_daily_pipeline.py` (raíz)

**Opciones funcionando:**
```powershell
py run_daily_pipeline.py --all         # Pipeline completo
py run_daily_pipeline.py --quick       # Bulletins + Report
py run_daily_pipeline.py --emails      # Solo bulletins
py run_daily_pipeline.py --analyze     # Solo AI FIT scores
py run_daily_pipeline.py --apply       # Auto-apply LIVE
py run_daily_pipeline.py --apply --dry-run  # DRY RUN
py run_daily_pipeline.py --expire      # Marcar expirados
py run_daily_pipeline.py --report      # Solo reporte
```

**Scripts que USA (subprocess, NO imports):**
```python
# STEP 1: Bulletin Processing
subprocess.run([sys.executable, 'core/automation/job_bulletin_processor.py'])

# STEP 2: AI Analysis (FIT Scores con salarios)
subprocess.run([sys.executable, 'scripts/maintenance/recalculate_fit_scores.py'])

# STEP 3: Auto-Apply
subprocess.run([sys.executable, 'core/automation/auto_apply_linkedin.py', '--dry-run'])

# STEP 4: Expire Check (marca jobs >30 días)
subprocess.run([sys.executable, 'scripts/verifiers/EXPIRE_LIFECYCLE.py', '--mark'])

# STEP 5: Report Generation
# Usa SheetManager para generar stats básicas
```

#### 3. **Control Center** ✅ 100%
**Archivo:** `control_center.py` (raíz)

Menú interactivo con 19 opciones:
- Pipeline completo/rápido
- Operaciones individuales (bulletins, AI, auto-apply, etc)
- Scraping (LinkedIn, Indeed)
- Visualización (Dashboard, Sheets)
- Utilidades (OAuth, Interview Copilot, etc)

#### 4. **Bulletin Processing** ✅ 100%
**Archivo:** `core/automation/job_bulletin_processor.py`

- Procesa boletines de LinkedIn, Indeed, Glassdoor
- Extrae múltiples jobs por email
- Deduplicación automática
- Guarda en Google Sheets
- Mueve emails a papelera después de procesar

**Última ejecución:**
- 1 boletín procesado (Glassdoor)
- 1 job nuevo guardado
- 0 errores

#### 5. **AI Analysis con Salarios** ✅ 100%
**Archivo:** `scripts/maintenance/recalculate_fit_scores.py`

**Lógica de penalties:**
```python
SALARY_MIN_ACCEPTABLE = 30000 MXN  # $1,700 USD
SALARY_PREFERRED = 50000 MXN       # $2,900 USD
SALARY_EXCELLENT = 80000 MXN       # $4,600 USD

< $20k MXN → Penalty -5 (extremely low)
< $30k MXN → Penalty -3 (below minimum)
< $50k MXN → Penalty -1 (below preferred)
< $80k MXN → No change (good range)
>= $80k MXN → Bonus +1 (excellent)
```

- Extrae salarios de texto (MXN/USD)
- Convierte USD a MXN (rate: 17)
- Recalcula FIT scores con penalties
- Actualiza Sheets automáticamente

#### 6. **Auto-Apply LinkedIn** ✅ 100%
**Archivo:** `core/automation/auto_apply_linkedin.py`

- LinkedIn Easy Apply automation
- DRY RUN mode (testing)
- LIVE mode (real applications)
- Form filling con Playwright
- Actualiza status en Sheets

**Uso:**
```powershell
py run_daily_pipeline.py --apply --dry-run  # Test
py run_daily_pipeline.py --apply            # LIVE
```

#### 7. **Expire Lifecycle** ✅ 100%
**Archivo:** `scripts/verifiers/EXPIRE_LIFECYCLE.py`

**Sistema de 2 pasos:**
```powershell
# PASO 1: Marca EXPIRED (jobs >30 días)
py scripts/verifiers/EXPIRE_LIFECYCLE.py --mark

# PASO 2: Borra jobs YA marcados como EXPIRED
py scripts/verifiers/EXPIRE_LIFECYCLE.py --delete

# Ambos pasos en una ejecución
py scripts/verifiers/EXPIRE_LIFECYCLE.py --full

# Custom threshold
py scripts/verifiers/EXPIRE_LIFECYCLE.py --mark --days 60
```

#### 8. **LinkedIn Scraper** ✅ 100%
**Archivo:** `core/ingestion/linkedin_scraper_V2.py`

- Scraping con Playwright
- Stealth mode
- Login automation
- Extrae jobs con metadata completa

#### 9. **Google Sheets Integration** ✅ 100%
**Archivo:** `core/sheets/sheet_manager.py`

**Sheet ID:** `1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg`

**Tabs:**
- Jobs (principal)
- Registry (histórico)
- LinkedIn
- Indeed
- Glassdoor
- Resumen

**Features:**
- Batch updates
- Deduplicación
- Status management
- FIT score tracking

#### 10. **Interview Copilot** ✅ 100%
**Archivo:** `core/copilot/interview_copilot_v2.py`

- Whisper transcription
- LM Studio/Gemini integration
- Job context loading
- Company research
- Push-to-talk (Ctrl+Shift+R)

---

### ⚠️ LO QUE FALTA (1%)

1. **Task Scheduler** - Windows Task Scheduler para ejecución diaria automática
2. **Glassdoor Scraper** - Opcional (boletines ya funcionan)
3. **Cover Letter Gen** - Mejoras (básico funciona)

---

## 🔧 PROBLEMAS CONOCIDOS Y SOLUCIONES

### 1. **OAuth Token Expirado** ✅ RESUELTO
**Síntoma:** `invalid_grant` error  
**Solución:** Sistema auto-renewal implementado
```powershell
# Valida automáticamente, si expira renueva solo
py oauth_token_validator.py
```

### 2. **LM Studio IP Cambia** ✅ RESUELTO
**Síntoma:** Cannot connect to LM Studio  
**Solución:** Script detecta IP automáticamente
```powershell
.\detect_lm_studio_ip.ps1
```

### 3. **Unicode Errors en Windows** ✅ RESUELTO
**Síntoma:** UnicodeDecodeError  
**Solución:** Fix encoding scripts
```powershell
.\fix_unicode_all.ps1
Get-Process python* | Stop-Process -Force
```

### 4. **Indeed Scraper Timeout** ⚠️ CONOCIDO
**Síntoma:** Browser freeze  
**Solución:** Usar LinkedIn (más confiable) y boletines
**Prioridad:** Baja (no crítico)

---

## ⚡ COMANDOS MÁS USADOS

### **Control Center (Recomendado)**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py control_center.py
```

### **Pipeline Completo**
```powershell
py run_daily_pipeline.py --all        # Todo (DRY RUN auto-apply)
py run_daily_pipeline.py --quick      # Bulletins + Report
```

### **Operaciones Individuales**
```powershell
py run_daily_pipeline.py --emails     # Bulletins
py run_daily_pipeline.py --analyze    # AI FIT scores
py run_daily_pipeline.py --apply --dry-run  # Auto-apply test
py run_daily_pipeline.py --expire     # Marcar expirados
py run_daily_pipeline.py --report     # Reporte
```

### **OAuth Management**
```powershell
py oauth_token_validator.py          # Validar token
py scripts/oauth/validate_oauth_v2.py # Verificar completo
py scripts/oauth/reauthenticate_gmail_v2.py  # Renovar manual
```

### **Verification Scripts**
```powershell
py view_sheets_data.py                # Ver datos en Sheets
py check_sheets_tabs.py               # Ver tabs
.\detect_lm_studio_ip.ps1             # Fix LM Studio IP
.\start_all.ps1                       # Inicio completo
```

### **Expire Management**
```powershell
# Marcar expirados (>30 días)
py scripts/verifiers/EXPIRE_LIFECYCLE.py --mark

# Borrar YA marcados
py scripts/verifiers/EXPIRE_LIFECYCLE.py --delete

# Ambos pasos
py scripts/verifiers/EXPIRE_LIFECYCLE.py --full

# Custom threshold (>60 días)
py scripts/verifiers/EXPIRE_LIFECYCLE.py --mark --days 60
```

---

## 📊 MÉTRICAS ACTUALES

**Google Sheets:**
- Jobs tracked: 157 (Glassdoor) + 10 (LinkedIn) + 5 (Indeed)
- Bulletins procesados: 339 históricos
- Último batch: 1 job nuevo
- Duplicados: 0 (deduplicación 100% efectiva)

**LM Studio:**
- Status: ✅ ONLINE
- URL: http://172.23.0.1:11434
- Model: Qwen 2.5 14B (8.99 GB)
- Formato: GGUF Q4_K_M

**OAuth:**
- Token válido: ✅
- Auto-renewal: ✅ FUNCIONA PERFECTO
- Última renovación: 2026-01-06 01:20 CST
- Expira en: ~59 minutos (se renueva automático)

**Pipeline:**
- Última ejecución: Exitosa ✅
- Bulletins: 1 procesado
- Jobs: 1 nuevo guardado
- Errores: 0

---

## 🎯 PRINCIPIOS DE DESARROLLO

### 1. **Local-First AI**
LM Studio > Gemini Cloud
- Privacidad
- Sin costo por uso
- Sin rate limits

### 2. **Functional > Perfect**
Entregar features funcionando, iterar después
- No refactorizar código que funciona
- Mejoras incrementales
- Testing exhaustivo antes de cambios

### 3. **Set it and Forget it**
Automatización máxima
- OAuth auto-renewal
- Pipeline diario automático
- Gestión automática de expirados
- Mínima intervención manual

### 4. **Windows-Optimized**
PowerShell scripts, paths absolutos
- Encoding UTF-8 forzado
- PowerShell como primera opción
- Paths con backslashes o forward slashes (normalizado automático)

### 5. **Comprehensive Logging**
Todo se loguea
- `logs/powershell/session_*.log`
- Debugging facilitado
- Troubleshooting rápido

---

## 🚨 REGLAS CRÍTICAS PARA CLAUDE

### ❌ NUNCA HAGAS ESTO:

1. **NO modificar código que funciona** sin razón fuerte
   - Si algo funciona, déjalo así
   - Consulta antes de refactorizar

2. **NO inventar imports o métodos** que no existen
   - Verifica que el archivo existe
   - Verifica que el método existe
   - Usa subprocess si no estás seguro

3. **NO asumir que main.py es el entry point**
   - El entry point es `control_center.py`
   - `main.py` solo redirige a control_center

4. **NO crear rutas o archivos sin verificar ubicación**
   - Siempre verifica estructura actual
   - Pregunta dónde crear archivos nuevos

5. **NO romper OAuth auto-renewal**
   - Es crítico que funcione siempre
   - Consulta antes de modificar oauth_token_validator.py

### ✅ SIEMPRE HAZLO ASÍ:

1. **Verifica estructura antes de codear**
   - Lista directorios
   - Confirma ubicación de archivos
   - Revisa imports existentes

2. **Usa subprocess para scripts externos**
   - No importes si no estás 100% seguro
   - subprocess.run() es más seguro
   - Captura output y errors

3. **Documenta cambios importantes**
   - Actualiza PROJECT_STATUS.md
   - Explica qué y por qué
   - Include examples de uso

4. **Testea antes de marcar como completo**
   - Ejecuta el script
   - Verifica output
   - Confirma que no rompe nada

5. **Pregunta si no estás seguro**
   - Mejor preguntar que romper algo
   - Usuario prefiere validar antes

---

## 📝 TAREAS COMUNES

### **Añadir nuevo script al pipeline**

1. Crear script en ubicación apropiada
2. Testear standalone
3. Añadir función en run_daily_pipeline.py usando subprocess:
```python
def run_new_feature():
    logger.info("ℹ️  STEP X: Running new feature...")
    try:
        result = subprocess.run(
            [sys.executable, 'path/to/script.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            logger.info("✅ New feature completed")
            return "PASS"
        else:
            logger.error(f"❌ Failed: {result.stderr[:200]}")
            return "FAIL"
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return "FAIL"
```

### **Debugging OAuth issues**

1. Verificar token:
```powershell
py oauth_token_validator.py
```

2. Ver detalles completos:
```powershell
py scripts/oauth/validate_oauth_v2.py
```

3. Renovar manualmente si necesario:
```powershell
py scripts/oauth/reauthenticate_gmail_v2.py
```

### **Ver datos en Google Sheets**

```powershell
py view_sheets_data.py              # Últimos 10 jobs
py check_sheets_tabs.py             # Ver tabs disponibles
```

### **Fix LM Studio connection**

```powershell
.\detect_lm_studio_ip.ps1           # Detecta y actualiza .env
# Verificar que LM Studio esté corriendo
# Verificar que el modelo esté cargado
```

---

## 🔄 WORKFLOW TÍPICO

### **Inicio del día:**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\start_all.ps1                     # Inicia servicios
py control_center.py                # Menú principal
# Opción 1: Pipeline completo
```

### **Debugging:**
```powershell
# Ver logs
Get-Content logs/powershell/session_*.log | Select-Object -Last 50

# Verificar OAuth
py oauth_token_validator.py

# Ver datos en Sheets
py view_sheets_data.py

# Fix LM Studio
.\detect_lm_studio_ip.ps1
```

### **Testing changes:**
```powershell
# Test script standalone
py path/to/script.py

# Test en pipeline
py run_daily_pipeline.py --quick

# Test completo
py run_daily_pipeline.py --all
```

---

## 📞 REFERENCIAS IMPORTANTES

### **Perfil profesional completo:**
Ver: `PROMPT_MAESTRO___PERFIL_LABORAL_C.txt`
- Experiencia PM/PO/BA/IT Manager
- ERP migrations, ETL, BI
- No busco developer positions
- Remote work prioritario

### **Google Sheets:**
URL: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

### **LM Studio:**
http://172.23.0.1:11434

### **Documentation:**
- `docs/PROJECT_STATUS.md` - Estado actual (99%)
- `docs/QUICKSTART_OAUTH_VALIDATOR.md` - OAuth guide
- `docs/README_OAUTH_VALIDATOR.md` - Technical docs
- `docs/INTEGRACION_OAUTH_VALIDATOR.md` - Integration guide

---

## 🎯 PRÓXIMOS PASOS SUGERIDOS

### **Inmediato:**
1. Test pipeline completo: `py run_daily_pipeline.py --all`
2. Procesar emails pendientes en carpeta JOBS/Inbound
3. Verificar que auto-apply funciona en DRY RUN

### **Esta semana:**
1. Configurar Task Scheduler para ejecución diaria
2. Mejorar cover letter generator
3. Analytics avanzado en dashboard

### **Meta final:**
- 100% automatización
- 0 intervención manual
- Pipeline diario automático
- Task Scheduler configurado

---

## 🚀 ESTADO FINAL

**Progreso:** 99% ✅  
**Última actualización:** 2026-01-06 01:30 CST

**Funciona perfecto:**
- ✅ OAuth auto-renewal
- ✅ Daily pipeline completo
- ✅ Bulletin processing
- ✅ AI analysis con salarios
- ✅ Auto-apply LinkedIn
- ✅ Expire lifecycle
- ✅ Google Sheets integration
- ✅ Control Center
- ✅ Interview Copilot
- ✅ PowerShell automation

**Falta 1%:**
- ⏳ Task Scheduler setup
- ⏳ Glassdoor scraper (opcional)
- ⏳ Cover letter polish

**Sistema production-ready:** ✅ SÍ

---

**FIN DEL PROMPT - LISTO PARA NUEVO CHAT** ✅

Usa este prompt completo al iniciar nuevo chat para mantener continuidad perfecta.
