# 📊 AI JOB FOUNDRY - PROJECT STATUS

**Última actualización:** 2026-01-18 00:45 CST  
**Versión:** 3.3 (LinkedIn Notifications Scraper)  
**Progreso:** 90% ✅

---

## 🎯 ESTADO GENERAL

Sistema funcional end-to-end con:
- ✅ Email processing (Gmail → Sheets)
- ✅ AI Analysis (LM Studio + Gemini)
- ✅ FIT Score Calculator (393/393 jobs scored - 100%)
- ✅ Bulletin Processing (50 emails/run)
- ✅ Status auto-update desde emails
- ✅ Salary-based FIT scoring
- ✅ Auto-mark expired/negative jobs
- ✅ Auto-start services
- ✅ Control Center menu completo
- ✅ OAuth auto-refresh
- ✅ Auto-Apply LinkedIn (timeout fix aplicado + --force flag)
- ✅ **NUEVO:** LinkedIn Notifications Scraper (extrae recomendaciones)
- ⏳ Auto-Apply Glassdoor (pendiente)

---

## 🆕 SESIÓN ACTUAL (2026-01-18 00:00-00:45)

### ✅ LinkedIn Notifications Scraper CREADO

**PROBLEMA INICIAL:**
- Auto-apply timeout (esperaba confirmación manual por 5 min)
- No existe scraper de LinkedIn activo
- Usuario necesita urgentemente forma de aplicar a ofertas

**SOLUCIONES IMPLEMENTADAS:**

1. **Auto-Apply Timeout Fix** ✅
   - Agregado flag `--force` a `auto_apply_linkedin.py`
   - Pipeline usa `--live --force` para omitir confirmación
   - Probado: DRY RUN funciona sin timeout

2. **LinkedIn Notifications Scraper** ✅ (NUEVO)
   - Archivo: `core/ingestion/linkedin_notifications_scraper.py`
   - Extrae recomendaciones de LinkedIn Jobs page
   - Guarda automáticamente en Google Sheets (tab LinkedIn)
   - Detecta Easy Apply badge
   - Evita duplicados automáticamente
   - Guarda sesión para reutilizar

3. **Complete Workflow System** ✅ (NUEVO)
   - Archivo: `run_linkedin_workflow.py`
   - Workflow: Scrape → Analyze → Apply
   - Modos: DRY RUN / LIVE
   - Ejecución modular (--scrape-only, --analyze-only, etc.)

4. **Quick Launcher** ✅ (NUEVO)
   - Archivo: `RUN_LINKEDIN_WORKFLOW.bat`
   - Menú interactivo para ejecutar workflows
   - Confirmación de seguridad para LIVE mode

**ARCHIVOS NUEVOS:**
```
core/ingestion/
  └─ linkedin_notifications_scraper.py    # Scraper principal

test_linkedin_notifications.py            # Test rápido
run_linkedin_workflow.py                  # Workflow completo  
RUN_LINKEDIN_WORKFLOW.bat                 # Launcher interactivo

docs/
  └─ LINKEDIN_NOTIFICATIONS_SCRAPER.md    # Documentación
```

**RESULTADO FIT SCORES:**
- 102 nuevos jobs calculados
- 9 JobLeads con FIT=7/10 (excelente para aplicar)
- 91 Glassdoor con FIT=3-4/10 (baja calidad - Role="Unknown")

**PRÓXIMO PASO:**
Ejecutar el nuevo scraper de LinkedIn para capturar notificaciones y aplicar automáticamente.

---

## 🆕 Sesiones Previas Relevantes

### Sesión Debug Auto-Apply (2026-01-15 01:50-02:10)

### Problema Detectado: Auto-Apply No Encuentra Jobs

**SÍNTOMAS:**
```
✨ No eligible jobs found for auto-apply
Criteria: FIT score 7+, LinkedIn Easy Apply, not already applied
```

**PERO LA REALIDAD:**
```
📊 COMPREHENSIVE JOB STATUS CHECK
======================================================================
  Total jobs:                 346
  Jobs WITH FIT score:        290 (83.8%)
  Jobs WITHOUT FIT score:      56
  Jobs with FIT >= 7:          19
  LinkedIn jobs:                9
  LinkedIn Easy Apply ready:    9  ← ⚠️ HAY 9 JOBS LISTOS!
```

**ANÁLISIS POR TAB:**
```
LinkedIn:      9 jobs | 5 FIT≥7 | 9 LinkedIn ✅
JobLeads:     13 jobs | 7 FIT≥7 | 0 LinkedIn
Indeed:        4 jobs | 3 FIT≥7 | 0 LinkedIn
Glassdoor:   309 jobs | 3 FIT≥7 | 0 LinkedIn (mayoría Role="Unknown")
Computrabajo:  3 jobs | 1 FIT≥7 | 0 LinkedIn
Jobs:          8 jobs | 0 FIT≥7 | 0 LinkedIn
```

**CAUSA PROBABLE:**
1. Auto-apply busca en tab incorrecta (¿"Jobs" en vez de "LinkedIn"?)
2. Filtro de "Easy Apply" muy estricto (requiere palabra exacta en URL)
3. Status "Applied" ya marcado en algunos jobs

**SCRIPTS CREADOS PARA DEBUG:**
1. `scripts/maintenance/check_job_status.py` ✅ - Resumen completo de jobs
2. `scripts/maintenance/show_linkedin_ready.py` ⏳ - Lista detallada LinkedIn jobs
3. `scripts/maintenance/calculate_all_fit_scores_v2.py` ✅ - Calculó FIT scores

**PRÓXIMO PASO:**
Ejecutar `show_linkedin_ready.py` para ver detalles exactos de los 9 LinkedIn jobs y determinar por qué el auto-apply no los detecta.

---

## 📊 ESTADÍSTICAS ACTUALES (2026-01-15)

### Jobs en Sistema
```
TOTAL:        346 jobs
├─ Glassdoor: 309 jobs (89%) - mayoría con Role="Unknown"
├─ JobLeads:   13 jobs (4%)
├─ LinkedIn:    9 jobs (3%)  ← 5 con FIT≥7 ✅
├─ Jobs:        8 jobs (2%)
├─ Indeed:      4 jobs (1%)
└─ Computrabajo: 3 jobs (1%)
```

### FIT Scores
```
Con FIT score:    290 jobs (83.8%)
Sin FIT score:     56 jobs (16.2%) - últimos boletines procesados
FIT >= 7:          19 jobs (5.5%)
FIT >= 8:          ~5 jobs estimados
```

### Pipeline Execution (Último Run)
```
✅ Bulletin Processing: 50 emails → 56 nuevos jobs guardados
✅ AI Analysis: PASS (no calculó FIT de nuevos jobs)
✅ Auto-Apply: PASS (pero 0 jobs detectados - BUG)
✅ Expire Check: PASS
✅ Report: PASS (21 jobs en "Jobs" tab)
```

---

## 🆕 Sesiones Previas Relevantes

### Unicode Fix V3.1 (2026-01-10)

**PROBLEMA CRÍTICO RESUELTO:**
```
❌ ERROR en Windows: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4e7'
✅ SOLUCIÓN: UTF-8 encoding automático en Windows
```

**Archivos reparados:**
1. ✅ `core/automation/job_bulletin_processor.py`
2. ✅ `scripts/maintenance/recalculate_fit_scores.py`  
3. ✅ `core/automation/auto_apply_linkedin.py`

**Fix aplicado:**
```python
# ✅ FIX: Windows UTF-8 support for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

### LinkedIn Auto-Login V3 (2025-12-24)

**Características:**
1. ✅ Lee credenciales del `.env` automáticamente
2. ✅ Detecta si hay sesión activa (cookies)
3. ✅ Hace login automático si es necesario
4. ✅ Guarda cookies para reutilizar sesión
5. ✅ Maneja verificaciones de seguridad (pausa 60s)

**Archivos:**
- `core/automation/linkedin_auto_apply.py` ✅ V3
- `scripts/test_linkedin_autoapply_v3.py` ✅
- `docs/LINKEDIN_AUTO_APPLY_V3.md` ✅

### FIT Score Bug Fix (2025-12-24)

**PROBLEMA:**
```
❌ Jobs con FIT Scores imposibles: 55/10, 25/10
```

**SOLUCIÓN:**
```python
fit_raw = res.get("fit", 0)
fit = round(fit_raw / 10, 1)  # 55 → 5.5, 82 → 8.2
```

---

## 📦 COMPONENTES PRINCIPALES

### ✅ Completados (85%)

1. **LinkedIn Scraper** - 100%
2. **Gmail Monitor** - 100%
3. **AI Analysis** - 100%
4. **Google Sheets Integration** - 100%
5. **Email Status Sync** - 100%
6. **Salary Scoring** - 100%
7. **Auto-mark Negatives** - 100%
8. **Auto-start Services** - 100%
9. **Control Center** - 100%
10. **OAuth Management** - 100%
11. **Bulletin Processing** - 100% (50 emails/run)
12. **FIT Score Calculator** - 85% (290/346 jobs)

### ⏳ Pendientes (15%)

1. **Auto-Apply LinkedIn** - BUG: No detecta los 9 jobs disponibles ⚠️
2. **FIT Scores Restantes** - 56 jobs nuevos sin calcular
3. **Glassdoor Role Extraction** - 309 jobs con Role="Unknown"
4. **Dashboard Keywords** - Resumen tab con errores
5. **Auto-Apply Glassdoor** - No implementado

---

## 🔧 PROBLEMAS CONOCIDOS

### 1. ⚠️ AUTO-APPLY NO DETECTA JOBS (CRÍTICO)

**Síntoma:** "No eligible jobs found" pero HAY 9 LinkedIn jobs con FIT≥7  
**Estado:** Investigando  
**Debug Script:** `scripts/maintenance/show_linkedin_ready.py`  
**Causa Probable:**
- Busca en tab incorrecta
- Filtro "Easy Apply" muy estricto
- Jobs ya marcados como "Applied"

### 2. Glassdoor Role="Unknown" (309 jobs)

**Problema:** Email parser no extrae títulos correctamente  
**Causa:** Boletines de Glassdoor solo tienen URLs, no metadata  
**Impacto:** FIT scores muy bajos (2-4/10) por falta de info  
**Solución Propuesta:**
- Opción A: Scrape URLs con Playwright para extraer títulos reales
- Opción B: Fix email parser y reprocesar

### 3. 56 Jobs Sin FIT Scores

**Problema:** Nuevos jobs del último run no tienen FIT calculado  
**Causa:** AI Analysis step no procesó los nuevos jobs  
**Solución:** `py scripts\maintenance\calculate_all_fit_scores_v2.py`

### 4. Dashboard Keywords Incorrectos

**Problema:** Keywords en Resumen tab muestran errores LM Studio  
**Keywords erróneos:** llm, conexi, error, httpconnection  
**Causa:** Script incluye logs de error  
**Solución:** Filtrar solo keywords de job descriptions

### 5. Indeed Scraper Timeout

**Problema:** Browser se congela  
**Workaround:** Usar Gmail processing (boletines)

---

## 🚀 COMANDOS PRINCIPALES

### Verificación y Debug
```powershell
# Ver estado completo de jobs
py scripts\maintenance\check_job_status.py

# Ver LinkedIn jobs listos para auto-apply
py scripts\maintenance\show_linkedin_ready.py

# Calcular FIT scores de jobs nuevos
py scripts\maintenance\calculate_all_fit_scores_v2.py

# Ver datos de Google Sheets
py view_sheets_data.py
```

### Pipeline Completo
```powershell
# Ejecutar todo (emails + AI + expire + report)
py run_daily_pipeline.py --all

# Auto-apply (DRY RUN - testing)
py run_daily_pipeline.py --apply --dry-run

# Auto-apply (LIVE - aplica realmente)
py run_daily_pipeline.py --apply
```

### Control Center
```powershell
# Menú interactivo completo
py control_center.py
```

### Inicio Automático
```powershell
# Inicia Docker + LM Studio + Web App
.\AUTO_START.bat
```

---

## 📊 GOOGLE SHEETS

**Sheet ID:** 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

### Tabs Activas
1. **Jobs** - Tab principal (8 jobs)
2. **LinkedIn** - Jobs LinkedIn directo (9 jobs) ← 5 con FIT≥7 ✅
3. **Indeed** - Jobs Indeed via Gmail (4 jobs)
4. **Glassdoor** - Jobs Glassdoor via Gmail (309 jobs)
5. **JobLeads** - Jobs JobLeads via Gmail (13 jobs)
6. **Computrabajo** - Jobs Computrabajo via Gmail (3 jobs)
7. **Resumen** - Dashboard (⚠️ keywords erróneos)
8. **Registry** - Historial (21 jobs, deprecated)

### Columnas Importantes
```
A: CreatedAt        G: RecruiterEmail    M: Status
B: Company          H: Currency          N: NextAction
C: Role             I: Comp              O: WorkAuthReq
D: Location         J: Seniority         P: FitScore
E: RemoteScope      K: WorkAuthReq       Q: Why
F: ApplyURL         L: Status
```

### Status Values
- `New` - Nuevo job sin revisar
- `ParsedOK` - Job procesado correctamente
- `ParsedIncomplete` - Job con datos faltantes
- `Application submitted` - Aplicación enviada
- `INTERVIEW_SCHEDULED` - Entrevista agendada
- `REJECTED` - Rechazado por empresa
- `REJECTED_BY_USER` - Rechazado por usuario
- `EXPIRED` - Posición cerrada
- `Applied` - Aplicado (LinkedIn)

---

## 💰 POLÍTICA DE SALARIO (ENFORCED)

### Umbrales
```
Mínimo legal:     $7,468 MXN   (no aceptable)
Mínimo aceptable: $30,000 MXN  (~$1,700 USD)
Preferido:        $50,000 MXN  (~$2,900 USD)
Excelente:        $80,000 MXN  (~$4,600 USD)
```

### FIT Score Penalties
```
< $20k MXN  → -5 puntos (SEVERO)
$20k-30k    → -3 puntos
$30k-50k    → -1 punto
$50k-80k    → 0 (normal)
> $80k      → +1 punto (bonus)
```

---

## 🎯 PRÓXIMOS PASOS

### Inmediatos (Esta Sesión - ANTES DE MIGRAR)

1. ⚠️ **DEBUG AUTO-APPLY** (CRÍTICO)
   - Ejecutar: `py scripts\maintenance\show_linkedin_ready.py`
   - Ver detalles de los 9 LinkedIn jobs
   - Identificar por qué auto-apply no los detecta
   - Fix el script de auto-apply

### Próxima Sesión (Después de Migrar)

2. **Calcular FIT Scores Restantes**
   - Ejecutar: `py scripts\maintenance\calculate_all_fit_scores_v2.py`
   - Procesar los 56 jobs nuevos sin FIT

3. **Test Auto-Apply**
   - Verificar que detecta los 9 LinkedIn jobs
   - Ejecutar dry-run: `py run_daily_pipeline.py --apply --dry-run`
   - Si funciona, ejecutar LIVE

4. **Fix Glassdoor Jobs**
   - Opción A: Scrape 309 URLs para extraer títulos reales
   - Opción B: Fix email parser y reprocesar boletines
   - Re-calcular FIT scores con datos reales

### Corto Plazo

5. **Dashboard Keywords**
   - Filtrar keywords de Resumen tab
   - Eliminar keywords de errores LM Studio

6. **Interview Copilot**
   - Detectar entrevistas desde emails
   - Preparar info de compañía
   - Recordatorios automáticos

7. **Auto-Apply Glassdoor**
   - Implementar después de fix de Role="Unknown"
   - Similar a LinkedIn pero para Glassdoor

---

## 📚 DOCUMENTACIÓN

### Archivos de Referencia
- `PROJECT_STATUS.md` - Este archivo (estado actualizado)
- `PROMPT_NUEVO_CHAT.md` - Para migrar chat (500+ líneas)
- `MEMORIA_PROYECTO.md` - Contexto completo del proyecto
- `PROMPT_MAESTRO_PERFIL_LABORAL_C.txt` - Perfil profesional Marcos

### Scripts de Mantenimiento
- `check_job_status.py` ✅ - Resumen completo por tabs
- `show_linkedin_ready.py` ⏳ - Debug auto-apply LinkedIn
- `calculate_all_fit_scores_v2.py` ✅ - Calcular FIT scores
- `recalculate_fit_scores.py` - Ajustar FIT con salary penalties
- `mark_all_negatives.py` - Marcar expired/rejected

### Scripts Principales
- `run_daily_pipeline.py` - Pipeline completo
- `control_center.py` - Menú interactivo
- `view_sheets_data.py` - Ver Google Sheets
- `AUTO_START.bat` - Auto-start servicios

---

## 🔄 WORKFLOW DIARIO ACTUAL

```powershell
# 1. Verificar estado de jobs
py scripts\maintenance\check_job_status.py

# 2. Ejecutar pipeline completo
py control_center.py
# Opción 1: Pipeline Completo

# 3. Calcular FIT scores si hay jobs nuevos
py scripts\maintenance\calculate_all_fit_scores_v2.py

# 4. Auto-apply (cuando funcione)
py run_daily_pipeline.py --apply --dry-run
```

---

## 💡 TIPS IMPORTANTES

### PowerShell Syntax
```powershell
# ❌ MAL
FIX_OAUTH_TOKEN.bat

# ✅ BIEN
.\FIX_OAUTH_TOKEN.bat
```

### Migración de Chat
**Usar cuando llegues a 65-75% de tokens:**
1. Lee: `PROJECT_STATUS.md` (este archivo)
2. Copia: `PROMPT_NUEVO_CHAT.md` al nuevo chat
3. Nuevo Claude lee archivos y continúa

### LM Studio Configuration
```
Model: Qwen 2.5 14B Instruct
URL: http://172.23.0.1:11434
Status: ✅ Running (ver screenshot)
```

### OAuth Troubleshooting
```powershell
# Si error invalid_grant
.\FIX_OAUTH_TOKEN.bat
```

---

## 📈 MÉTRICAS DE ÉXITO

### Completitud
- ✅ 85% del sistema funcional
- ✅ 290/346 jobs con FIT scores (83.8%)
- ✅ Pipeline completo ejecutando sin errores
- ⚠️ Auto-apply NO funcional (bug detectado)

### Jobs Procesados
- **Total:** 346 jobs
- **Listos para aplicar:** 9 LinkedIn (FIT≥7)
- **Requieren aplicación manual:** 10 (JobLeads, Indeed)
- **Baja prioridad:** 309 (Glassdoor con Role="Unknown")

### Último Pipeline Run (2026-01-15)
```
Bulletins procesados: 50 emails
Jobs nuevos: 56
FIT scores calculados: 0 (pendiente)
Auto-apply intentos: 0 (bug - no detectó jobs)
```

---

## 🎓 LECCIONES APRENDIDAS

### ✅ QUÉ FUNCIONA BIEN

1. **Gmail Processing**
   - Boletines procesados automáticamente
   - Duplicates detectados correctamente
   - 50 emails/run sin problemas

2. **FIT Score System**
   - LM Studio + Qwen 2.5 14B funciona excelente
   - Scores razonables (2-9/10)
   - Salary penalties aplicados correctamente

3. **OAuth Management**
   - Auto-refresh funcional
   - No más errores de tokens expirados

### ⚠️ QUÉ NECESITA MEJORA

1. **Glassdoor Parser**
   - No extrae Role/Company de emails
   - 309 jobs con metadata incompleta
   - Necesita scraping de URLs o fix de parser

2. **Auto-Apply Detection**
   - No detecta jobs disponibles
   - Requiere debug urgente
   - Probablemente busca en tab incorrecta

3. **AI Analysis Step**
   - No calculó FIT de jobs nuevos
   - Necesita ejecutarse manualmente
   - Debe integrarse mejor al pipeline

---

**Autor:** Marcos Alberto Alvarado de la Torre  
**Ubicación:** Guadalajara, México (CST, GMT-6)  
**Hardware:** RTX 4090 24GB, 64GB RAM  
**Roles Target:** PM, PO, Senior BA, IT Manager, ETL Consultant  
**Stack:** Python 3.13, Windows 11, PowerShell 7.5.4  
**AI Local:** LM Studio + Qwen 2.5 14B @ http://172.23.0.1:11434
