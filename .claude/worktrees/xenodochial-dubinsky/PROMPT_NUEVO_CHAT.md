# 🚀 PROMPT PARA NUEVO CHAT - AI JOB FOUNDRY

## ⚠️ INSTRUCCIÓN CRÍTICA PARA LA IA

**ANTES DE CUALQUIER CAMBIO, LEE COMPLETAMENTE:**

1. **`PROJECT_STATUS.md`** - Estado actual del sistema
2. **`MASTER_FEATURE_ROADMAP.md`** - Features planificadas (100+)
3. **Este prompt completo** - Contexto y principios

**AL FINALIZAR CADA ITERACIÓN:**
- ✅ ACTUALIZA `PROJECT_STATUS.md` con cambios realizados
- ✅ Documenta bugs resueltos
- ✅ Actualiza fecha y versión
- ✅ Registra archivos modificados

---

## 📋 CONTEXTO DEL PROYECTO

### Resumen Ejecutivo
**AI Job Foundry** es un sistema automatizado de búsqueda de empleo que:
- Scrapea ofertas (LinkedIn, Indeed, Glassdoor)
- Procesa emails de reclutadores y boletines
- Analiza match con IA local (LM Studio + Qwen 2.5 14B)
- Calcula FIT SCORES (0-10) con penalidades por salario bajo
- Guarda en Google Sheets organizadas por fuente
- Auto-aplica a ofertas high-fit (en desarrollo)

### Usuario
**Nombre:** Marcos Alberto Alvarado de la Torre  
**Ubicación:** Guadalajara, México (CST, GMT-6)  
**Roles objetivo:** Project Manager, Product Owner, Senior Business Analyst, IT Manager, ETL Consultant  
**NO busca:** Software Developer/Programmer  
**Prioridad:** Remote work (familia con bebé Máximo)

### Experiencia Clave
- 10+ años en ERP migrations (Intelisis → Dynamics AX)
- ETL masivo (800+ TB procesados en Toyota Financial)
- BI/Power BI, IT Infrastructure (LATAM)
- Proyectos multinacionales (México, Colombia, Chile, Brasil, Suecia)

---

## 🎯 ESTADO ACTUAL DEL SISTEMA

### Versión: 2.6 (2025-12-02 23:50 CST)
**Progreso:** 100% funcional ✅

### Componentes Funcionando
✅ Email Processing (Gmail → Sheets) - 100%  
✅ AI Analysis (LM Studio + Gemini fallback) - 100%  
✅ Status Auto-Update desde emails - 100%  
✅ Salary-based FIT Scoring - 100%  
✅ Auto-mark Expired/Negative Jobs - 100%  
✅ Auto-start Services - 100%  
✅ Web App Unificada (puerto 5555) - 100%  
✅ Auto-Apply LinkedIn (4 bugs resueltos) - 100%  
✅ Expire Check (URL verification) - 100%  
✅ Control Center - 95%  
✅ OAuth Management - 100%

### Pendientes
⏳ Auto-Apply Glassdoor (368 jobs esperando - 86% del total)  
⏳ Dashboard Keywords Fix (LM Studio error en tab Resumen)  
⏳ Indeed Scraper Freeze (Chromium timeout)

---

## 📊 ESTADÍSTICAS ACTUALES

**Total Jobs Procesados:** 426
- Glassdoor: 368 (86%) ← **PRIORIDAD MÁXIMA**
- LinkedIn: 47 (11%)
- Indeed: 11 (3%)

**Status Actual:**
- New: 16
- Applied: 0
- Interview: 0
- Rejected: 0
- Expired: 1
- High Fit (7+): 2

---

## 🛠️ TECH STACK

### IA Local
- **LM Studio:** http://172.23.0.1:11434 o http://127.0.0.1:11434
- **Modelo:** Qwen 2.5 14B Instruct (tool-use trained)
- **Fallback:** Gemini API (si LM Studio no responde)

### Storage & APIs
- **Google Sheets ID:** 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
- **Gmail API:** OAuth tokens en `data/credentials/`
- **Scrapers:** Playwright (LinkedIn, Indeed)

### Automation
- **Pipeline:** run_daily_pipeline.py
- **Control Center:** control_center.py
- **Web App:** unified_app/app.py (puerto 5555)
- **PowerShell Scripts:** Auto-start, cleanup, fixes

---

## 🔧 ARCHIVOS CLAVE

### Documentación (SIEMPRE LEER PRIMERO)
```
PROJECT_STATUS.md              # Estado actual - ACTUALIZAR EN CADA ITERACIÓN
MASTER_FEATURE_ROADMAP.md      # 100+ features planificadas
docs/session_reports/          # Reportes de sesiones anteriores
```

### Código Principal
```
run_daily_pipeline.py          # Pipeline completo
control_center.py              # Menú principal
core/automation/auto_apply_linkedin.py  # Auto-apply (FUNCIONAL)
core/ingestion/linkedin_scraper_V2.py   # LinkedIn scraper (FINAL)
core/enrichment/ai_analyzer.py          # AI analysis
```

### Scripts de Mantenimiento
```
scripts/maintenance/mark_all_negatives.py       # Marca jobs rechazados
scripts/maintenance/recalculate_fit_scores.py   # Recalcula FIT
scripts/maintenance/update_status_from_emails.py # Sync email→sheets
scripts/maintenance/verify_job_status.py        # Verifica URLs
```

### Tests
```
scripts/tests/TEST_FITSCORE_FIX.py      # Test FitScore parsing
scripts/tests/TEST_PIPELINE_FIXES.py    # Test imports y métodos
```

---

## ⚡ PRINCIPIOS CRÍTICOS DE DESARROLLO

### 🚫 NO ROMPER LO QUE FUNCIONA

**REGLA DE ORO:** Antes de modificar cualquier archivo que FUNCIONA:

1. **LEE el archivo completo primero**
2. **ENTIENDE qué hace y por qué**
3. **PREGUNTA al usuario si no estás seguro**
4. **CREA un backup si es cambio mayor**
5. **PRUEBA después de cada cambio**

### ✅ Código que NO se debe tocar (sin razón fuerte)

```
✅ core/automation/auto_apply_linkedin.py  # Recién arreglado (4 bugs)
✅ run_daily_pipeline.py                    # Pipeline funcional
✅ core/ingestion/linkedin_scraper_V2.py    # Scraper estable
✅ core/enrichment/ai_analyzer.py           # AI analysis OK
✅ core/sheets/sheet_manager.py             # Sheets OK
✅ unified_app/app.py                       # Web app funcional
```

**Excepción:** Si usuario pide explícitamente o encuentras un bug CRÍTICO

### 🎯 Cuando agregar nueva funcionalidad

**BUENAS PRÁCTICAS:**
1. **Crea archivos NUEVOS** en vez de modificar existentes
2. **Usa imports** de código existente
3. **No duplicar lógica** - reutiliza funciones
4. **Tests primero** para funcionalidad crítica
5. **Documenta en PROJECT_STATUS.md**

**EJEMPLO CORRECTO:**
```
# Quieres agregar Glassdoor auto-apply
1. Crea: core/automation/auto_apply_glassdoor.py (NUEVO)
2. Importa: from core.sheets.sheet_manager import SheetManager (REUSA)
3. Modifica: run_daily_pipeline.py (solo agregar llamada)
4. Test: scripts/tests/TEST_GLASSDOOR_APPLY.py (NUEVO)
5. Actualiza: PROJECT_STATUS.md
```

**EJEMPLO INCORRECTO:**
```
❌ Modificar auto_apply_linkedin.py para soportar Glassdoor
   (Riesgo: romper LinkedIn que YA funciona)
```

---

## 🐛 BUGS RECIENTEMENTE RESUELTOS (NO REINTRODUCIR)

### Bug #1: FitScore ValueError
**Error:** `ValueError: invalid literal for int() with base 10: ''`  
**Solución:** Función `safe_fit_score()` maneja '', None, '8/10', etc  
**Ubicación:** run_daily_pipeline.py  
**NO CAMBIAR** esta función sin entender el problema original

### Bug #2: Auto-Apply AttributeError
**Error:** `'LinkedInAutoApplier' object has no attribute 'process_jobs'`  
**Solución:** Método correcto es `run()` no `process_jobs()`  
**NO CAMBIAR** llamadas a applier.run()

### Bug #3: Expire Check ModuleNotFoundError
**Error:** `No module named 'verify_job_status'`  
**Solución:** sys.path agregado para import desde scripts/maintenance/  
**NO CAMBIAR** este import sin verificar paths

### Bug #4: Auto-Apply FitScore TypeError
**Error:** `'>=' not supported between instances of 'str' and 'int'`  
**Solución:** Función `_safe_fit_score()` en LinkedInAutoApplier  
**NO CAMBIAR** comparaciones de FitScore sin sanitizar primero

---

## 📈 PRÓXIMOS PASOS SUGERIDOS

### PRIORIDAD ALTA (Máximo Impacto)

#### 1. Glassdoor Auto-Apply (30-45 min)
**Por qué:** 368 jobs (86% del total) sin automatizar  
**Qué hacer:**
- Investigar proceso de aplicación Glassdoor
- Crear `auto_apply_glassdoor.py` (NUEVO archivo)
- Modificar pipeline para incluirlo
- Test DRY RUN

**Archivos nuevos:**
- `core/automation/auto_apply_glassdoor.py`
- `scripts/tests/TEST_GLASSDOOR_APPLY.py`

**Archivos modificar:**
- `run_daily_pipeline.py` (agregar llamada)
- `PROJECT_STATUS.md` (documentar)

#### 2. Filtros Gmail Automáticos (15 min)
**Por qué:** Organización automática de emails  
**Qué hacer:**
- Script ya existe: CREATE_GMAIL_FILTERS.py (en archive/)
- Crear labels: JOBS/LinkedIn, JOBS/Indeed, JOBS/Glassdoor
- Filtros por remitente

**Impacto:** Email processing más eficiente

#### 3. Fix Indeed Scraper Freeze (30 min)
**Por qué:** Indeed scraper se congela (Chromium timeout)  
**Qué hacer:**
- Investigar por qué Chromium deja de responder
- Agregar retry logic
- Usar múltiples browsers en paralelo
- Headless mode optimizado

**NO ROMPER:** LinkedIn scraper que funciona perfecto

### PRIORIDAD MEDIA

#### 4. Dashboard Keywords Fix (15 min)
**Problema:** Tab Resumen tiene errores LM Studio  
**Qué hacer:**
- Investigar query a LM Studio que falla
- Agregar error handling
- Fallback a Gemini si LM Studio no responde

#### 5. Notificaciones Multi-Canal (30 min)
**Features:**
- Email notifications (high-fit jobs, interviews)
- Telegram bot (opcional)
- Discord webhook (opcional)

---

## 💡 FILOSOFÍA DE DESARROLLO

### "Set it and Forget it"
- Automatización máxima
- Mínima intervención diaria
- Logging completo para debugging
- Procesos idempotentes (pueden ejecutarse N veces sin problema)

### Windows-First
- PowerShell scripts (no bash)
- Paths absolutos (no relativos)
- `py` command (no `python`)
- Manejo de encoding Windows (UTF-8 con BOM)

### Local-First AI
- LM Studio > Cloud APIs (privacidad + costo)
- Gemini como fallback (no primary)
- Modelos tool-use trained (Qwen 2.5 14B)

### Functional > Perfect
- Entregar features funcionando, iterar después
- 80% working > 100% perfect pero incompleto
- Tests para funciones críticas, no para todo

---

## 🚀 COMANDOS ÚTILES

### Ver Estado Actual
```powershell
py scripts/view_current_sheets.py          # Ver Google Sheets
Get-Content PROJECT_STATUS.md              # Estado proyecto
Get-Content logs/powershell/session_*.log  # Logs recientes
```

### Ejecutar Pipeline
```powershell
.\START_CONTROL_CENTER.bat    # Menú interactivo
py run_daily_pipeline.py --all        # Pipeline completo
py run_daily_pipeline.py --emails     # Solo emails
py run_daily_pipeline.py --analyze    # Solo AI analysis
```

### Tests
```powershell
py scripts/tests/TEST_FITSCORE_FIX.py      # Test FitScore
py scripts/tests/TEST_PIPELINE_FIXES.py    # Test pipeline
```

### Mantenimiento
```powershell
.\CLEANUP_ALL_JOBS.bat                     # Limpieza completa
py scripts/maintenance/mark_all_negatives.py    # Marca negativos
py scripts/maintenance/recalculate_fit_scores.py # Recalcula FIT
```

---

## 📝 ACTUALIZAR PROJECT_STATUS.md

### Template de Actualización

Al finalizar cada iteración, agregar al inicio de PROJECT_STATUS.md:

```markdown
## 🆕 ÚLTIMA SESIÓN (YYYY-MM-DD HH:MM)

### Cambios Realizados

1. **[Nombre del Feature/Fix]**
   - Descripción breve
   - Archivos modificados: X, Y, Z
   - Test: ✅/⏳
   - Estado: ✅ FUNCIONAL / ⚠️ PARCIAL / ❌ FALLIDO

### Archivos Nuevos
- archivo1.py (N líneas) - Propósito
- archivo2.md - Documentación de X

### Archivos Modificados
- archivo3.py (líneas X-Y) - Cambio Z
- PROJECT_STATUS.md - Actualización sesión

### Próximos Pasos
- [ ] Tarea 1 pendiente
- [ ] Tarea 2 pendiente

---
```

---

## ⚠️ SEÑALES DE ALERTA

**SI VES ESTO, DETENTE Y PREGUNTA:**

❌ "Voy a reescribir [archivo_funcional].py"  
❌ "Mejor simplificar este código que funciona"  
❌ "Este patrón es mejor" (sin probar)  
❌ Modificar 5+ archivos simultáneamente  
❌ Cambios sin tests en funcionalidad crítica  
❌ Imports que fallan sin verificar paths  

**✅ HACER EN CAMBIO:**

✅ "Voy a crear [nuevo_archivo].py que usa [funcional].py"  
✅ "Voy a agregar feature X sin modificar Y que funciona"  
✅ "Voy a hacer backup antes de cambio mayor"  
✅ Cambios incrementales con tests  
✅ Un archivo a la vez, verificar que funciona  
✅ Leer código existente PRIMERO  

---

## 🎯 OBJETIVO DE ESTA SESIÓN

**ENFOQUE:** Avanzar en el proyecto SIN romper lo que funciona

**PRIORIDADES:**
1. **Glassdoor Auto-Apply** (368 jobs esperando - 86%)
2. **Filtros Gmail** (organización automática)
3. **Indeed Scraper Fix** (resolver freeze)
4. **Features del Roadmap** (según usuario elija)

**PROHIBIDO:**
- Modificar archivos que funcionan sin razón fuerte
- Cambios masivos sin tests
- "Mejorar" código funcional sin solicitud explícita

---

## 📞 RECURSOS EXTERNOS

### Google Sheets
https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

### LM Studio
- URL local: http://127.0.0.1:11434 o http://172.23.0.1:11434
- Model: qwen2.5-14b-instruct
- Debe estar RUNNING para AI analysis

### Documentación Proyecto
- Perfil profesional: `__PROMPT_MAESTRO___PERFIL_LABORAL_C.txt`
- Memoria proyecto: `MEMORIA_PROYECTO.md`

---

## ✅ CHECKLIST ANTES DE EMPEZAR

**ESTA SESIÓN, VOY A:**

- [ ] Leer PROJECT_STATUS.md completo
- [ ] Leer MASTER_FEATURE_ROADMAP.md
- [ ] Entender qué funciona y qué no
- [ ] Identificar archivos que NO debo tocar
- [ ] Crear archivos NUEVOS en vez de modificar funcionales
- [ ] Hacer tests antes de cambios críticos
- [ ] Actualizar PROJECT_STATUS.md al finalizar

---

## 🚀 ¡AHORA SÍ, EMPECEMOS!

**PREGUNTA INICIAL PARA EL USUARIO:**

"¡Hola Marcos! He leído todo el contexto del proyecto AI Job Foundry. 

**Estado actual:** Sistema 100% funcional (v2.6) con 426 jobs procesados.

**Oportunidad detectada:** Tienes 368 jobs de Glassdoor (86% del total) sin auto-apply.

**¿Qué prefieres hacer en esta sesión?**

A) Crear Glassdoor Auto-Apply (30-45 min) - Aprovecha el 86% de oportunidades
B) Implementar Filtros Gmail automáticos (15 min) - Mejor organización  
C) Fix Indeed Scraper freeze (30 min) - Resolver timeout de Chromium
D) Otra feature del Roadmap - Dime cuál
E) Continuar donde lo dejamos - Revisar logs y decidir

**Recuerda:** Todo cambio se documentará en PROJECT_STATUS.md ✅"

---

**Fecha creación prompt:** 2025-12-03 00:00 CST  
**Versión sistema:** 2.6  
**Progreso:** 100% funcional  
**Siguiente hito:** Glassdoor Auto-Apply o Features del Roadmap
