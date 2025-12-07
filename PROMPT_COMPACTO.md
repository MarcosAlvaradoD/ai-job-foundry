# 🚀 PROMPT COMPACTO - AI JOB FOUNDRY (PARA COPIAR RÁPIDO)

## ⚠️ INSTRUCCIÓN CRÍTICA

**Lee PRIMERO antes de cualquier cambio:**
- `C:\Users\MSI\Desktop\ai-job-foundry\PROJECT_STATUS.md`
- `C:\Users\MSI\Desktop\ai-job-foundry\MASTER_FEATURE_ROADMAP.md`

**AL FINALIZAR CADA ITERACIÓN:**
- ✅ ACTUALIZA `PROJECT_STATUS.md` con fecha, versión y cambios
- ✅ NO rompas código que funciona sin razón fuerte

---

## 📋 CONTEXTO RÁPIDO

**AI Job Foundry** = Sistema automatizado búsqueda empleo

**Usuario:** Marcos Alvarado (Guadalajara, MX)  
**Roles:** PM/PO/BA/IT Manager (NO developer)  
**Prioridad:** Remote work (familia con bebé)

**Sistema:** v2.6 - 100% funcional ✅  
**Jobs:** 426 procesados (Glassdoor: 368/86%, LinkedIn: 47, Indeed: 11)

---

## 🎯 COMPONENTES FUNCIONANDO

✅ Email Processing (Gmail → Sheets)  
✅ AI Analysis (LM Studio + Gemini)  
✅ Auto-Apply LinkedIn (4 bugs resueltos)  
✅ Web App puerto 5555  
✅ Control Center  
✅ OAuth Management  

⏳ Auto-Apply Glassdoor (368 jobs esperando - **PRIORIDAD**)  
⏳ Dashboard Keywords Fix  
⏳ Indeed Scraper Freeze  

---

## 🔧 ARCHIVOS CLAVE

**Docs:** PROJECT_STATUS.md, MASTER_FEATURE_ROADMAP.md  
**Pipeline:** run_daily_pipeline.py, control_center.py  
**Auto-Apply:** core/automation/auto_apply_linkedin.py (**NO TOCAR** - recién arreglado)  
**Scraper:** core/ingestion/linkedin_scraper_V2.py (**ESTABLE**)  
**Tests:** scripts/tests/TEST_*.py  

---

## ⚡ PRINCIPIOS CRÍTICOS

### 🚫 NO ROMPER LO QUE FUNCIONA

**ANTES de modificar archivo funcional:**
1. Leer completo
2. Entender por qué funciona
3. PREGUNTAR si no estás seguro
4. Crear backup si cambio mayor
5. Probar después

**CREAR ARCHIVOS NUEVOS** > Modificar existentes

**EJEMPLO CORRECTO:**
```
Nuevo feature → Crear: core/automation/auto_apply_glassdoor.py (NUEVO)
               Reusa:  from core.sheets.sheet_manager import SheetManager
               Modifica: run_daily_pipeline.py (solo agregar llamada)
```

**EJEMPLO INCORRECTO:**
```
❌ Modificar auto_apply_linkedin.py para agregar Glassdoor
   (Riesgo: romper LinkedIn que funciona)
```

---

## 🐛 BUGS RESUELTOS (NO REINTRODUCIR)

1. **FitScore ValueError** - safe_fit_score() maneja '', None, '8/10'
2. **Auto-Apply AttributeError** - Método correcto: run() no process_jobs()
3. **Expire Check Import** - sys.path para scripts/maintenance/
4. **Auto-Apply TypeError** - _safe_fit_score() sanitiza FitScore

**NO CAMBIAR** estas funciones sin entender problema original

---

## 📈 PRÓXIMOS PASOS SUGERIDOS

### PRIORIDAD ALTA

**1. Glassdoor Auto-Apply** (30-45 min)
- 368 jobs (86%) sin automatizar
- Crear auto_apply_glassdoor.py (NUEVO)
- Test DRY RUN

**2. Filtros Gmail** (15 min)
- Labels: JOBS/LinkedIn, JOBS/Indeed, JOBS/Glassdoor
- Script existe: CREATE_GMAIL_FILTERS.py

**3. Fix Indeed Scraper** (30 min)
- Resolver Chromium freeze
- Retry logic
- NO romper LinkedIn scraper

---

## 🚀 COMANDOS ÚTILES

```powershell
# Pipeline
.\START_CONTROL_CENTER.bat

# Tests
py scripts\tests\TEST_PIPELINE_FIXES.py

# Ver estado
py scripts\view_current_sheets.py
Get-Content PROJECT_STATUS.md
```

---

## ⚠️ SEÑALES DE ALERTA

**DETENTE Y PREGUNTA SI:**
❌ "Voy a reescribir [archivo_funcional].py"  
❌ Modificar 5+ archivos simultáneamente  
❌ Cambios sin tests en funcionalidad crítica  

**✅ HACER EN CAMBIO:**
✅ Crear archivo NUEVO que usa funcionales  
✅ Cambios incrementales con tests  
✅ Leer código existente PRIMERO  

---

## 📝 ACTUALIZAR PROJECT_STATUS.md

```markdown
## 🆕 ÚLTIMA SESIÓN (YYYY-MM-DD HH:MM)

### Cambios Realizados
1. **[Feature/Fix]**
   - Descripción
   - Archivos: X, Y, Z
   - Test: ✅
   - Estado: ✅ FUNCIONAL

### Próximos Pasos
- [ ] Pendiente 1
```

---

## 🎯 PREGUNTA INICIAL

¡Hola Marcos! Sistema 100% funcional (v2.6).

**Oportunidad:** 368 jobs Glassdoor (86%) sin auto-apply.

**¿Qué hacemos?**
A) Glassdoor Auto-Apply (30-45 min)  
B) Filtros Gmail (15 min)  
C) Fix Indeed Scraper (30 min)  
D) Otra feature del Roadmap  
E) Continuar donde dejamos  

**Recuerda:** Todo se documenta en PROJECT_STATUS.md ✅

---

**Ruta proyecto:** C:\Users\MSI\Desktop\ai-job-foundry  
**Versión:** 2.6  
**Estado:** 100% funcional
