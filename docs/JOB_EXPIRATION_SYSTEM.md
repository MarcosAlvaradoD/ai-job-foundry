# 🚫 SISTEMA DE EXPIRACIÓN DE OFERTAS - AI JOB FOUNDRY

**Sistema Híbrido: Manual + Automático por Fecha + Verificación con Scraper**

---

## 📋 OVERVIEW

El sistema implementa **3 métodos complementarios** para determinar si una oferta sigue activa:

1. **MANUAL (Opción B)** - Tú marcas status en Google Sheets
2. **AUTO POR FECHA (Opción A)** - Script marca como expirada si >30 días
3. **VERIFICACIÓN URL (Opción C)** - Script visita URL y detecta si expiró

---

## 🎯 MÉTODO 1: MANUAL (Status en Sheets)

**Cómo funciona:**
- Tú actualizas columna `Status` en Google Sheets manualmente
- Opciones: New, Applied, Interview, Rejected, Expired

**Status que se ignoran en auto-apply:**
- Applied
- Rejected
- Expired
- Interview

**Uso:**
```
Abre Google Sheets → Edita columna Status → Guarda
```

**Ventaja:** Control total  
**Desventaja:** Requiere intervención manual

---

## 🎯 MÉTODO 2: AUTO POR FECHA (>30 días)

**Cómo funciona:**
- Script compara `CreatedAt` con fecha actual
- Si la oferta tiene >30 días → marca Status="Expired"
- Solo afecta ofertas con Status="New" o vacío

**Ejecución:**
```powershell
py run_daily_pipeline.py --expire
```

O como parte del pipeline completo:
```powershell
py run_daily_pipeline.py --all
```

**Configuración:**
- Umbral: 30 días (hardcoded en `run_daily_pipeline.py`)
- Para cambiar: editar línea 77

**Ventaja:** Automático, rápido  
**Desventaja:** Puede marcar ofertas que siguen activas

---

## 🎯 MÉTODO 3: VERIFICACIÓN CON SCRAPER (Opción C) ⭐

**Cómo funciona:**
- Script visita cada URL con Playwright headless
- Detecta patrones de expiración:
  - HTTP 404
  - "No longer accepting applications"
  - "This job has expired"
  - "Job posting not found"
  - Y ~10 patrones más
- Actualiza Status="Expired" en Sheets automáticamente

**Uso básico:**
```powershell
# Verificar todas las ofertas nuevas
py verify_job_status.py --all

# Solo ofertas con Status=New
py verify_job_status.py --new

# Solo ofertas con FIT >= 7
py verify_job_status.py --high-fit

# Limitar a 10 ofertas
py verify_job_status.py --all --limit 10

# Cambiar rate limiting (default 3 seg)
py verify_job_status.py --all --rate-limit 5
```

**Integrado en pipeline:**
```powershell
py run_daily_pipeline.py --expire
# Ejecuta date check + URL verification (5 ofertas high-fit)
```

**Características:**
- ✅ Headless browser (no abre ventanas)
- ✅ Rate limiting (evita blocks)
- ✅ Detecta LinkedIn, Indeed, Glassdoor
- ✅ Actualiza Sheets automáticamente
- ✅ Reporte detallado al final

**Ventaja:** Preciso, confirma estado real  
**Desventaja:** Más lento (3-5 seg por oferta)

---

## 🔄 FLUJO RECOMENDADO (Híbrido)

### **DIARIO (Automático):**
```powershell
py run_daily_pipeline.py --all
```

Esto ejecuta:
1. Procesa emails nuevos
2. AI analysis (FIT SCORES)
3. **Date check** - Marca >30 días como Expired
4. **URL verification** - Verifica 5 ofertas high-fit
5. Genera reporte

### **SEMANAL (Manual):**
```powershell
# Verificar todas las ofertas high-fit
py verify_job_status.py --high-fit --rate-limit 5
```

### **MANUAL (Cuando quieras):**
- Edita columna Status en Google Sheets
- Marca Applied cuando aplicas
- Marca Rejected cuando te rechazan
- Marca Interview cuando te llaman

---

## 📊 PATRONES DE EXPIRACIÓN DETECTADOS

### **LinkedIn:**
- "no longer accepting applications"
- "this job is no longer available"
- "posting has been removed"
- "job posting not found"
- "oops! we can't find that job"

### **Indeed:**
- "this job has expired"
- "job has been removed"
- "no longer available"
- "job posting has expired"

### **Glassdoor:**
- "job not found"
- "this job is no longer available"
- "posting has been removed"

---

## 🛡️ PROTECCIÓN CONTRA BLOCKS

**Rate Limiting:**
- Default: 3 segundos entre requests
- Configurable: `--rate-limit N`

**User Agent:**
- Simula navegador real: Chrome Windows

**Headless:**
- No abre ventanas visibles
- Menos detectable

**Timeouts:**
- 15 segundos por página
- Si timeout → asume activa (no marca expired)

---

## 📈 EJEMPLO DE REPORTE

```
======================================================================
📊 VERIFICATION SUMMARY
======================================================================
Total Checked:     10
  Still Active:    7
  Expired:         2
  Errors:          0
  Skipped:         3  (already Applied/Rejected)
======================================================================
```

---

## 🔧 TROUBLESHOOTING

### **Error: "Playwright not installed"**
```powershell
pip install playwright
py -m playwright install chromium
```

### **Error: "Can't update Sheets"**
- Verifica credentials en `data/credentials/`
- Re-autenticar: `py scripts\setup\reauthenticate_gmail.py`

### **Error: "Timeout on all pages"**
- Revisa conexión a internet
- Aumenta timeout en `verify_job_status.py` línea 60

### **Verificación muy lenta**
- Reduce cantidad: `--limit 5`
- Aumenta rate limit: `--rate-limit 10`

---

## 🎯 CONFIGURACIÓN AVANZADA

### **Cambiar umbral de días (30 → 45):**

Editar `run_daily_pipeline.py` línea 77:
```python
if days_old > 45:  # Era 30
```

### **Agregar nuevo patrón de expiración:**

Editar `verify_job_status.py` líneas 49-68:
```python
linkedin_expired_patterns = [
    'no longer accepting applications',
    'TU_NUEVO_PATRON_AQUI',
    # ...
]
```

### **Cambiar cantidad en pipeline automático:**

Editar `run_daily_pipeline.py` línea 99:
```python
verifier.verify_jobs(jobs_to_verify[:10], rate_limit_seconds=3)  # Era 5
```

---

## 📅 TASK SCHEDULER (Windows)

Para ejecutar automáticamente el pipeline diario:

```xml
Nombre: AI Job Foundry - Daily Pipeline
Trigger: Diario a las 8:00 AM
Acción: py C:\Users\MSI\Desktop\ai-job-foundry\run_daily_pipeline.py --all
Directorio: C:\Users\MSI\Desktop\ai-job-foundry
```

**Instrucciones:**
1. Abrir Task Scheduler
2. Create Basic Task
3. Nombre: "AI Job Foundry Daily"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
   - Program: `py`
   - Arguments: `run_daily_pipeline.py --all`
   - Start in: `C:\Users\MSI\Desktop\ai-job-foundry`
6. Finish

---

## 🎉 RESUMEN

**IMPLEMENTADO:**
- ✅ Opción B: Manual status (Google Sheets)
- ✅ Opción A: Auto-expiración por fecha (>30 días)
- ✅ Opción C: Verificación automática con scraper

**COMANDOS CLAVE:**
```powershell
# Pipeline completo (incluye verificación limitada)
py run_daily_pipeline.py --all

# Solo verificación de expiración
py run_daily_pipeline.py --expire

# Verificación completa de URLs
py verify_job_status.py --high-fit --limit 20

# Verificar todas las ofertas nuevas
py verify_job_status.py --new
```

**PRÓXIMO PASO:**
Configurar Task Scheduler para ejecución automática diaria.

---

**Última actualización:** 2025-11-19  
**Autor:** Claude + Marcos Alvarado
