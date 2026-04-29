# 🎯 GUÍA - NUEVO SISTEMA DE VERIFICACIÓN MULTI-PLATAFORMA

**Fecha:** 2025-12-06  
**Status:** ✅ IMPLEMENTADO  
**Archivos creados:** 3 nuevos verifiers + 1 pipeline modificado

---

## 📋 RESUMEN DE LO QUE SE HIZO

### ARCHIVOS NUEVOS CREADOS

1. **LINKEDIN_SMART_VERIFIER.py** (324 líneas)
   - Verifica jobs de LinkedIn con Playwright
   - Detecta 12 patrones de expiración (EN + ES)
   - Marca automático en pestaña "LinkedIn"

2. **INDEED_SMART_VERIFIER.py** (325 líneas)
   - Verifica jobs de Indeed con Playwright
   - Detecta 13 patrones de expiración (EN + ES)
   - Marca automático en pestaña "Indeed"

3. **run_daily_pipeline.py** (modificado)
   - Nueva función `check_expired_jobs()` con 4 pasos
   - Usa el flujo: Delete → Verify Glassdoor → Verify LinkedIn → Verify Indeed

---

## 🔄 FLUJO COMPLETO DEL SISTEMA

### CÓMO FUNCIONA AHORA

```
EJECUCIÓN 1 (py run_daily_pipeline.py --expire):
├─ [1/4] Delete EXPIRED existentes → Limpia 0 jobs (primera vez)
├─ [2/4] Verify Glassdoor → Marca 50 como EXPIRED
├─ [3/4] Verify LinkedIn → Marca 10 como EXPIRED
└─ [4/4] Verify Indeed → Marca 5 como EXPIRED

RESULTADO: 65 jobs marcados como EXPIRED

───────────────────────────────────────────────────────

EJECUCIÓN 2 (py run_daily_pipeline.py --expire):
├─ [1/4] Delete EXPIRED existentes → Borra 65 jobs ✅
├─ [2/4] Verify Glassdoor → Marca 30 nuevos EXPIRED
├─ [3/4] Verify LinkedIn → Marca 5 nuevos EXPIRED
└─ [4/4] Verify Indeed → Marca 2 nuevos EXPIRED

RESULTADO: 65 borrados + 37 nuevos marcados

───────────────────────────────────────────────────────

EJECUCIÓN 3 (py run_daily_pipeline.py --expire):
├─ [1/4] Delete EXPIRED existentes → Borra 37 jobs ✅
├─ [2/4] Verify Glassdoor → Marca nuevos EXPIRED
├─ [3/4] Verify LinkedIn → Marca nuevos EXPIRED
└─ [4/4] Verify Indeed → Marca nuevos EXPIRED

... y así sucesivamente (ciclo continuo)
```

---

## 🚀 CÓMO USAR EL SISTEMA

### OPCIÓN 1: Ejecutar Pipeline Completo

```bash
py run_daily_pipeline.py --expire
```

**Qué hace:**
- ✅ Borra jobs EXPIRED existentes
- ✅ Verifica Glassdoor con Playwright
- ✅ Verifica LinkedIn con Playwright
- ✅ Verifica Indeed con Playwright

**Tiempo:** ~15-30 minutos (depende de cuántos jobs haya)

---

### OPCIÓN 2: Ejecutar Verifiers Individualmente

#### Glassdoor

```bash
# Verificar todos
py GLASSDOOR_SMART_VERIFIER.py

# Verificar solo 50
py GLASSDOOR_SMART_VERIFIER.py --limit 50

# Verificar sin marcar (solo reporte)
py GLASSDOOR_SMART_VERIFIER.py --no-mark
```

#### LinkedIn

```bash
# Verificar todos
py LINKEDIN_SMART_VERIFIER.py

# Verificar solo 20
py LINKEDIN_SMART_VERIFIER.py --limit 20

# Verificar sin marcar
py LINKEDIN_SMART_VERIFIER.py --no-mark
```

#### Indeed

```bash
# Verificar todos
py INDEED_SMART_VERIFIER.py

# Verificar solo 10
py INDEED_SMART_VERIFIER.py --limit 10

# Verificar sin marcar
py INDEED_SMART_VERIFIER.py --no-mark
```

---

### OPCIÓN 3: Solo Borrar EXPIRED

```bash
py EXPIRE_LIFECYCLE.py --delete
```

**Qué hace:**
- ✅ Borra TODOS los jobs marcados como EXPIRED
- ✅ De todas las pestañas (Jobs, Registry, LinkedIn, Indeed, Glassdoor)
- ✅ Sin confirmación (directo)

---

## 📊 OUTPUT ESPERADO

### Ejecución Completa

```bash
$ py run_daily_pipeline.py --expire

STEP 4: Checking for expired jobs...

  [1/4] Deleting previously marked EXPIRED jobs...
    ✅ Deleted 133 EXPIRED jobs

  [2/4] Verifying Glassdoor jobs with Playwright...
    📋 Fetching jobs from Glassdoor tab...
    ✅ Found 87 jobs to verify
    
    [1/87] Checking: Acme Corp - Project Manager...
      ❌ EXPIRED: HTTP 404
      📝 Marked as EXPIRED in sheet
    
    [2/87] Checking: TechCo - Product Owner...
      ✅ ACTIVE: Found: "easy apply"
    
    ... (continúa con los 87)
    
    📊 VERIFICATION SUMMARY
    Total verified: 87
      ❌ EXPIRED:   25 (28.7%)
      ✅ ACTIVE:    60 (69.0%)
      ⚠️  ERROR:     2 (2.3%)
    
    ✅ Glassdoor: 25 expired, 60 active

  [3/4] Verifying LinkedIn jobs with Playwright...
    📋 Fetching jobs from LinkedIn tab...
    ✅ Found 31 jobs to verify
    
    ... (similar output)
    
    ✅ LinkedIn: 8 expired, 23 active

  [4/4] Verifying Indeed jobs with Playwright...
    📋 Fetching jobs from Indeed tab...
    ✅ Found 9 jobs to verify
    
    ... (similar output)
    
    ✅ Indeed: 2 expired, 7 active

  ✅ Expiration check completed

TOTAL: 35 jobs marcados como EXPIRED
PRÓXIMA EJECUCIÓN: Borrará estos 35 + marcará nuevos
```

---

## ⚙️ CONFIGURACIÓN DE CADA VERIFIER

### GLASSDOOR_SMART_VERIFIER.py

**Patrones detectados (18 total):**
- Español: "este empleo no está disponible", "ya no está disponible"
- Inglés: "this job is no longer available", "job has expired"

**Navegador:** Firefox (headless=False para ver)
**Rate limit:** 3 segundos entre requests
**Pestaña:** Glassdoor

---

### LINKEDIN_SMART_VERIFIER.py

**Patrones detectados (12 total):**
- Inglés: "no longer accepting applications", "posting has been removed"
- Español: "ya no acepta solicitudes", "la publicación fue eliminada"

**Navegador:** Firefox (headless=False)
**Rate limit:** 3 segundos
**Pestaña:** LinkedIn

---

### INDEED_SMART_VERIFIER.py

**Patrones detectados (13 total):**
- Inglés: "this job has expired", "job posting has expired"
- Español: "este empleo ha expirado", "la publicación expiró"

**Navegador:** Firefox (headless=False)
**Rate limit:** 3 segundos
**Pestaña:** Indeed

---

## 🎯 CASOS DE USO

### CASO 1: Limpieza completa semanal

```bash
# Domingo en la mañana
py run_daily_pipeline.py --expire
```

**Resultado:**
- Borra EXPIRED de la semana pasada
- Marca nuevos EXPIRED
- Hoja limpia para la semana

---

### CASO 2: Verificación rápida de Glassdoor

```bash
# Solo Glassdoor (la mayoría de tus jobs)
py GLASSDOOR_SMART_VERIFIER.py --limit 50
```

**Resultado:**
- Verifica solo 50 primeros
- Rápido (~5 minutos)
- Marca los que encuentra

---

### CASO 3: Debugging sin marcar

```bash
# Ver qué pasaría SIN marcar nada
py LINKEDIN_SMART_VERIFIER.py --no-mark
```

**Resultado:**
- Reporte completo
- NO marca como EXPIRED
- Solo informativo

---

## 🔍 TROUBLESHOOTING

### ERROR: "Module not found"

```bash
# Asegúrate de estar en el directorio correcto
cd C:\Users\MSI\Desktop\ai-job-foundry

# Verifica que los archivos existen
dir GLASSDOOR_SMART_VERIFIER.py
dir LINKEDIN_SMART_VERIFIER.py
dir INDEED_SMART_VERIFIER.py
```

---

### ERROR: "No jobs found with Status='New'"

**Causa:** Todos los jobs ya están marcados como EXPIRED/Applied/etc.

**Solución:**
```bash
# Ver estado actual en Sheets
py view_sheets_data.py

# Si es correcto, no hay nada que verificar
```

---

### ERROR: Playwright timeout

**Causa:** Job page tarda mucho en cargar

**Efecto:** Se marca como ERROR (no como EXPIRED)

**Normal:** 1-2 timeouts en 100 jobs es normal

---

### WARNING: Browser visible

**Normal:** Los verifiers usan `headless=False` para debugging

**Para ocultar:**
Editar cada verifier, cambiar línea:
```python
# ANTES:
browser = p.firefox.launch(headless=False)

# DESPUÉS:
browser = p.firefox.launch(headless=True)
```

---

## 📝 PASOS PARA EJECUTAR AHORA

### PASO 1: Verificar archivos creados

```bash
cd C:\Users\MSI\Desktop\ai-job-foundry

dir LINKEDIN_SMART_VERIFIER.py
dir INDEED_SMART_VERIFIER.py

# Deberías ver:
#   LINKEDIN_SMART_VERIFIER.py  (324 líneas)
#   INDEED_SMART_VERIFIER.py    (325 líneas)
```

---

### PASO 2: Test individual de cada verifier

```bash
# Test LinkedIn (debería haber ~31 jobs)
py LINKEDIN_SMART_VERIFIER.py --limit 5

# Espera ver:
#   Found X jobs to verify
#   [1/5] Checking: ...
```

```bash
# Test Indeed (debería haber ~9 jobs)
py INDEED_SMART_VERIFIER.py --limit 3

# Espera ver output similar
```

---

### PASO 3: Test del pipeline completo

```bash
# Ejecución completa
py run_daily_pipeline.py --expire

# Espera ver los 4 pasos:
#   [1/4] Deleting...
#   [2/4] Verifying Glassdoor...
#   [3/4] Verifying LinkedIn...
#   [4/4] Verifying Indeed...
```

---

### PASO 4: Validación en Google Sheets

1. Abre: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

2. Verifica pestaña **Glassdoor**:
   - Debería haber jobs con Status='EXPIRED'
   - Columna "Why" debe tener razón (ej: "HTTP 404")

3. Verifica pestaña **LinkedIn**:
   - Similar

4. Verifica pestaña **Indeed**:
   - Similar

---

## ✅ CHECKLIST DE VALIDACIÓN

Después de ejecutar todo, verifica:

- [ ] LINKEDIN_SMART_VERIFIER.py existe y funciona
- [ ] INDEED_SMART_VERIFIER.py existe y funciona
- [ ] run_daily_pipeline.py se modificó correctamente
- [ ] `py run_daily_pipeline.py --expire` ejecuta los 4 pasos
- [ ] PASO 1 borra EXPIRED existentes
- [ ] PASO 2 verifica Glassdoor con Playwright
- [ ] PASO 3 verifica LinkedIn con Playwright
- [ ] PASO 4 verifica Indeed con Playwright
- [ ] Google Sheets refleja los cambios
- [ ] Jobs EXPIRED tienen razón en columna "Why"

---

## 🎨 MEJORAS FUTURAS (OPCIONAL)

1. **Modo headless por defecto:**
   - Cambiar `headless=False` a `headless=True`
   - Verifiers más rápidos (sin UI)

2. **Logs detallados:**
   - Guardar resultados en archivo
   - Histórico de verificaciones

3. **Rate limit configurable:**
   - Cambiar 3 segundos por variable
   - Ajustar según tasa de éxito

4. **Notificaciones:**
   - Email cuando se borran >50 jobs
   - Slack cuando se marcan >20 nuevos

---

## 📞 ¿NECESITAS AYUDA?

**Si algo falla:**

1. Revisa output del comando
2. Busca línea con "ERROR:" o "⚠️ "
3. Copia error completo

**Si un verifier no funciona:**

```bash
# Test manual
py LINKEDIN_SMART_VERIFIER.py --limit 1 --no-mark

# Debería mostrar qué está pasando
```

**Si el pipeline se traba:**

```bash
# Ctrl+C para cancelar
# Revisar en qué paso se quedó
# Ejecutar ese paso solo
```

---

## 🎯 RESUMEN FINAL

**LO QUE TIENES AHORA:**

✅ Sistema de 3 verifiers (Glassdoor, LinkedIn, Indeed)  
✅ Detección con Playwright (contenido real)  
✅ Ciclo automático: Delete → Verify → Mark  
✅ Ejecución completa en un comando  
✅ Logs detallados de cada paso  

**CÓMO USARLO:**

```bash
# Semanal (recomendado)
py run_daily_pipeline.py --expire

# Diario (si tienes muchos jobs nuevos)
py run_daily_pipeline.py --expire
```

**PRÓXIMOS PASOS:**

1. Test los 3 verifiers individualmente
2. Test el pipeline completo
3. Valida en Google Sheets
4. Configura ejecución semanal/diaria

---

**¿Listo para probar?** 🚀

