# 🆕 NUEVOS SCRIPTS - GUÍA RÁPIDA

**Creados:** 2026-02-20  
**Status:** BETA - En testing

---

## 🎯 PROPÓSITO

Estos scripts **NO reemplazan** el código existente. Son **NUEVOS procesos separados** para:

1. ✅ Limpiar jobs expirados
2. ✅ Scrapear LinkedIn activamente
3. ✅ Mejorar detection de Easy Apply (próximamente)

---

## 📁 ARCHIVOS NUEVOS

### 1. `scripts/maintenance/clean_expired_jobs.py`

**Qué hace:**
- Lee Google Sheets (LinkedIn, Indeed, Glassdoor tabs)
- Encuentra jobs con Status='Expired'
- Los mueve a pestaña Archive (o los marca)
- Limpia los datos activos

**Uso:**
```powershell
# Ver qué se movería (DRY RUN)
py scripts\maintenance\clean_expired_jobs.py --dry-run

# Mover realmente (LIVE)
py scripts\maintenance\clean_expired_jobs.py --live
```

**Salida esperada:**
```
🧹 EXPIRED JOBS CLEANER
======================================================================
Mode: DRY RUN

Checking LinkedIn tab...
  Total jobs: 21
  Expired: 9
  
  Expired jobs to move:
    1. Project Manager at Company A (created: 2025-10-16)
    2. Product Owner at Company B (created: 2025-10-18)
    ... and 7 more

  [DRY RUN] Would move 9 jobs to Archive

📊 SUMMARY
======================================================================
  LinkedIn: 9 expired
  Total expired jobs found: 9
  
  [DRY RUN] No changes made
  Run with --live to actually move jobs
```

**Importante:**
- ⚠️ Hace un DRY RUN por defecto (seguro)
- ⚠️ Usa `--live` solo si estás seguro
- ✅ NO elimina datos, solo los mueve/marca

---

### 2. `core/ingestion/linkedin_search_scraper_v3.py`

**Qué hace:**
- Login a LinkedIn
- Busca activamente por keywords:
  - "Project Manager remote"
  - "Product Owner remote"
  - "Senior Business Analyst remote"
  - "IT Manager remote"
  - "ETL Consultant remote"
- Extrae primeros 20 results por búsqueda (100 total)
- Filtra duplicados
- Guarda en Google Sheets

**Uso:**
```powershell
# Test mode (DRY RUN)
py core\ingestion\linkedin_search_scraper_v3.py --dry-run

# Guardar a Sheets (LIVE)
py core\ingestion\linkedin_search_scraper_v3.py --live
```

**Salida esperada:**
```
🔍 LINKEDIN SEARCH SCRAPER V3
======================================================================
Mode: DRY RUN

🌐 Launching browser...
🔐 Logging in to LinkedIn...
✅ Logged in successfully

======================================================================
🔎 Searching: Project Manager remote
======================================================================
  Opening: https://www.linkedin.com/jobs/search/...
  Found 25 job cards
    1. Senior Project Manager at Microsoft
    2. Technical Project Manager at Google
    3. Project Manager - Remote at Amazon
    ...
  ✅ Found 20 jobs

[Repite para cada búsqueda]

📊 SCRAPING SUMMARY
======================================================================
  Total jobs found: 87
  
  By search query:
    • Project Manager remote: 20
    • Product Owner remote: 18
    • Senior Business Analyst remote: 17
    • IT Manager remote: 16
    • ETL Consultant remote: 16
  
  Sample jobs (first 10):
    1. Senior Project Manager at Microsoft
    2. Product Owner - AI Products at Google
    ...
```

**En modo LIVE:**
```
💾 Saving to Google Sheets...
  Total scraped: 87
  Duplicates: 5
  New jobs: 82
  ✅ Saved 82/82 jobs
```

**Importante:**
- ⚠️ Abre navegador visible (headless=False) para debugging
- ⚠️ Requiere credenciales de LinkedIn
- ✅ Filtra duplicados automáticamente
- ✅ Solo guarda jobs remote

---

## 🚀 WORKFLOW RECOMENDADO

### Paso 1: Limpiar jobs expirados

```powershell
# 1. Ver qué se limpiaría
py scripts\maintenance\clean_expired_jobs.py --dry-run

# 2. Si estás de acuerdo, ejecutar
py scripts\maintenance\clean_expired_jobs.py --live
```

**Resultado esperado:**
- Antes: Total Jobs: 21, Expired: 9
- Después: Total Jobs: 12, Expired: 0

---

### Paso 2: Scrapear jobs nuevos

```powershell
# 1. Test primero
py core\ingestion\linkedin_search_scraper_v3.py --dry-run

# 2. Si funciona bien, guardar
py core\ingestion\linkedin_search_scraper_v3.py --live
```

**Resultado esperado:**
- Jobs nuevos: +80 aproximadamente
- Total Jobs: 12 → 92
- With FIT Score: 12 → necesita AI analysis

---

### Paso 3: Analizar con AI

```powershell
py control_center.py
# Seleccionar opción 5: Análisis AI
```

**Resultado esperado:**
- With FIT Score: 12 → 92
- Jobs con FIT >= 7: +40 nuevos

---

### Paso 4: Revisar resultados

```powershell
py control_center.py
# Seleccionar opción 8: Generar Reporte
```

**Resultado esperado:**
```
📊 DAILY REPORT
======================================================================
Total Jobs:       92       ← Antes: 21
With FIT Score:   92       ← Antes: 21
Applied:          0        ← Aún 0 (detection roto)
Expired:          0        ← Antes: 9 ✅ LIMPIO
```

---

## ⚠️ PROBLEMAS CONOCIDOS

### Clean Expired Jobs

**Problema:** SheetManager puede no tener método `delete_row()` o `move_to_archive()`

**Workaround actual:**
- Marca jobs como "Archived from [tab]"
- NO elimina físicamente (más seguro)

**Fix futuro:**
- Agregar `delete_row()` a SheetManager
- O crear tab "Archive" real

---

### LinkedIn Search Scraper

**Problema 1:** LinkedIn puede pedir verificación

**Solución:**
- Script abre navegador visible
- Usuario verifica manualmente si es necesario
- Script continúa después

**Problema 2:** Rate limiting

**Solución:**
- Script espera 3 segundos entre búsquedas
- Solo 5 búsquedas por ejecución
- No correr más de 2 veces al día

**Problema 3:** Selectores cambian

**Solución:**
- Usa selectores genéricos (`div.job-search-card`)
- Fallback a "Unknown" si no encuentra
- No falla, solo extrae lo que puede

---

## 🔧 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'core'"

**Solución:**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py scripts\maintenance\clean_expired_jobs.py --dry-run
```

Asegúrate de estar en la raíz del proyecto.

---

### Error: "LinkedIn login failed"

**Solución:**
1. Verifica credenciales en `data/credentials/.linkedin_credentials`
2. Intenta login manual primero en navegador
3. LinkedIn puede haber cambiado la página de login

---

### Error: "No jobs found"

**Posibles causas:**
1. LinkedIn cambió selectores CSS
2. No hay jobs remote para esas keywords
3. Problema de red/timeout

**Debug:**
- Agrega `headless=False` (ya está)
- Ve qué muestra el navegador
- Screenshot del HTML

---

## 📈 MÉTRICAS DE ÉXITO

### Antes de usar scripts nuevos

```
Total Jobs: 21
New this week: 0
Expired: 9
Applied: 0
```

### Después de Paso 1 (Clean expired)

```
Total Jobs: 12
New this week: 0
Expired: 0 ✅
Applied: 0
```

### Después de Paso 2 (Scraping)

```
Total Jobs: 92
New this week: 80 ✅
Expired: 0
Applied: 0
```

### Después de Paso 3 (AI Analysis)

```
Total Jobs: 92
With FIT >= 7: 45 ✅
Expired: 0
Applied: 0 (detection aún roto)
```

---

## 🔜 PRÓXIMOS PASOS

### Auto-Apply Detection Fix

**Archivo a crear:** `core/automation/auto_apply_linkedin_v2.py`

**Plan:**
1. Tomar screenshot del HTML de job page
2. Analizar selectores reales
3. Crear detection basado en estructura real
4. Test con 10 jobs conocidos
5. Integrar cuando funcione 80%+

**Status:** Pendiente (Fase 3)

---

## ❓ PREGUNTAS FRECUENTES

### ¿Estos scripts reemplazan el código viejo?

**NO.** Son procesos **separados** que:
- Se pueden ejecutar independientemente
- NO modifican código existente
- Eventualmente se integrarán al Control Center

---

### ¿Es seguro usar --live?

**Sí, pero:**
- Siempre corre `--dry-run` primero
- Revisa qué va a cambiar
- Backup de Sheets si tienes dudas

---

### ¿Cuándo se integrarán al Control Center?

Después de:
1. ✅ Testing exhaustivo
2. ✅ Confirmación del usuario
3. ✅ Documentación completa
4. ✅ Agregar opciones al menú

**Estimado:** 1-2 días después de validación

---

## 📞 SOPORTE

Si algo falla:

1. **Copia el error completo**
2. **Indica qué comando usaste**
3. **Comparte el output**
4. **Screenshot si es error visual**

Y lo arreglaremos juntos.

---

**Última actualización:** 2026-02-20  
**Status:** BETA - En testing  
**Próxima revisión:** Después de primera ejecución LIVE
