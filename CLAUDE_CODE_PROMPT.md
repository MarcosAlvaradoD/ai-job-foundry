# 🚀 CLAUDE CODE - PROMPT PARA CONTINUAR AI JOB FOUNDRY

**Proyecto:** AI Job Foundry (Automated Job Search System)  
**Estado actual:** 94% completitud  
**Última sesión:** 19 Nov 2025 22:00 CST  
**Usuario:** Marcos Alvarado (PM/PO/BA, remote jobs, Guadalajara MX)

---

## 📋 CONTEXTO INMEDIATO

Acabo de resolver el problema de OAuth que bloqueaba Gmail y Google Sheets.  
**NUEVO PROBLEMA CRÍTICO descubierto:** 87.5% de jobs (14 de 16) no tienen URLs.

### ✅ Lo que YA funciona:
- OAuth completamente restaurado
- LinkedIn scraper (extrae URLs correctamente)
- URL verifier (funciona perfecto con las 2 URLs que tenemos)
- Control Center (17 opciones)
- Interview Copilot Session Recorder
- Dashboard, PowerShell scripts, deduplicación

### ❌ Problema URGENTE:
- Solo 2 de 16 jobs tienen URLs (12.5%)
- Sin URLs no puedo:
  - Verificar expiración automáticamente
  - Auto-aplicar a ofertas
  - Trackear correctamente

---

## 🎯 TU MISIÓN

**OBJETIVO 1 (CRÍTICO):** Investigar y solucionar por qué el 87.5% de jobs no tiene URLs

**OBJETIVO 2:** Fix standardize_status.py (método incorrecto)

**OBJETIVO 3:** Continuar con auto-apply básico (cuando URLs estén fixeadas)

---

## 📂 ARCHIVOS CLAVE CREADOS PARA TI

### 1. investigate_urls.py
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\investigate_urls.py`

**Qué hace:**
- Analiza jobs por source (LinkedIn, Gmail, etc.)
- Muestra cuáles tienen URLs y cuáles no
- Identifica patrones
- Sugiere causas probables

**Ejecutar:**
```bash
cd ~/Desktop/ai-job-foundry
python investigate_urls.py
```

---

### 2. standardize_status_v2.py
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\standardize_status_v2.py`

**Qué hace:**
- Estandariza valores de Status en Sheets
- "ParsedOK" → "New"
- "Ya no" / "No" → "Expired"
- Versión FIXEADA con métodos correctos

**Ejecutar:**
```bash
python standardize_status_v2.py
```

---

### 3. check_urls_status.py
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\check_urls_status.py`

**Qué hace:**
- Diagnóstico rápido de estado actual
- Muestra estadísticas de URLs
- Analiza Status values
- Verifica integridad de datos

**Ya ejecutado, resultados:**
- Total: 16 jobs
- Con URL: 2
- Sin URL: 14
- Status: 14 "ParsedOK", 2 "(empty)"

---

## 🔍 ARCHIVOS A INVESTIGAR

### Prioridad ALTA:

**1. core/automation/gmail_jobs_monitor_v2.py**
- Este procesa emails de reclutadores
- Debería extraer URLs pero no lo está haciendo
- **ACCIÓN:** Revisar método de extracción de URLs
- Buscar regex o parsing de enlaces
- Ver por qué falla

**2. core/automation/job_bulletin_processor.py**
- Procesa boletines con múltiples ofertas
- Debería extraer URLs individuales
- **ACCIÓN:** Verificar si extrae URLs correctamente

**3. core/ingestion/linkedin_scraper_V2.py**
- Este SÍ funciona (los 2 jobs con URLs son de aquí)
- **ACCIÓN:** Comparar con email processor
- Ver qué hace diferente

---

## 🚨 PROBLEMAS CONOCIDOS

### 1. Método Inexistente en standardize_status.py
**Error:**
```python
'SheetManager' object has no attribute 'get_all_jobs_from_tab'
```

**Método correcto:**
```python
jobs = sheet_manager.get_all_jobs(tab="registry")
```

**Status:** YA FIXEADO en standardize_status_v2.py

---

### 2. URLs Faltantes (87.5%)
**Causas probables:**
1. Email processor no tiene regex de extracción
2. Emails son plain text sin links clickeables
3. Bulletin processor no separa URLs individuales
4. Regex demasiado estricto

**Necesita:** Investigación profunda del código

---

### 3. Datos Posiblemente Corruptos
**Síntomas:**
- Jobs muestran "Registry - OK" como Company/Role
- Parecen ser entries de prueba o mal parseadas

**Acción:** Verificar con `investigate_urls.py`

---

## 📝 PLAN DE TRABAJO SUGERIDO

### FASE 1: Investigación (30 min)

```bash
# 1. Ejecutar investigación
cd ~/Desktop/ai-job-foundry
python investigate_urls.py

# 2. Revisar gmail_jobs_monitor_v2.py
# Buscar:
# - Métodos que extraen URLs
# - Regex patterns
# - Email parsing

# 3. Revisar job_bulletin_processor.py
# Verificar extracción de URLs de boletines
```

**Objetivo:** Identificar exactamente DÓNDE falla la extracción

---

### FASE 2: Fix Email Processor (1 hora)

**Ubicación:** `core/automation/gmail_jobs_monitor_v2.py`

**Tareas:**
1. Agregar/mejorar regex de extracción de URLs
2. Probar con emails HTML y plain text
3. Manejar diferentes formatos de links
4. Logging detallado de URLs encontradas

**Regex sugeridos a probar:**
```python
# URLs completas
r'https?://[^\s<>"{}|\\^`\[\]]+'

# LinkedIn específico
r'https?://(?:www\.)?linkedin\.com/jobs/view/\d+'

# Indeed específico  
r'https?://(?:www\.)?indeed\.com/[^\s<>"{}|\\^`\[\]]+'

# Glassdoor específico
r'https?://(?:www\.)?glassdoor\.com/[^\s<>"{}|\\^`\[\]]+'
```

---

### FASE 3: Testing (30 min)

```bash
# 1. Procesar 1 email de prueba
python -c "from core.automation.gmail_jobs_monitor_v2 import process_single_email; process_single_email('MENSAJE_ID')"

# 2. Verificar que extrae URL
python check_urls_status.py

# 3. Si funciona, re-procesar todos
python control_center.py
# Opción 3 (Procesar Emails)
```

---

### FASE 4: Estandarizar Status (5 min)

```bash
python standardize_status_v2.py
# Responder 's' cuando pregunte
```

---

### FASE 5: Verificación Final (10 min)

```bash
# 1. Ver stats actualizadas
python check_urls_status.py

# 2. Verificar URLs de high-fit
python verify_job_status.py --high-fit

# 3. Abrir Google Sheets
python control_center.py
# Opción 14
```

---

## 💡 TIPS IMPORTANTES

### Para debugging:
1. **Logs:** Todo va a `logs/powershell/session_*.log`
2. **Testing:** Usa 1 email primero, no re-proceses todos
3. **Backup:** Google Sheets guarda historial automático

### SheetManager API:
```python
sm = SheetManager()

# Obtener jobs
jobs = sm.get_all_jobs(tab="registry")  # NOT get_all_jobs_from_tab!

# Actualizar status
sm.update_job_status(row_index=2, new_status="New", tab="registry")

# Los rows empiezan en 2 (row 1 = headers)
```

### Testing email processor:
```python
# Importar
from core.automation.gmail_jobs_monitor_v2 import EmailProcessor

# Instanciar
processor = EmailProcessor()

# Procesar 1 email
result = processor.process_email(message_id="XXXX")
print(result.get('url', 'No URL found'))
```

---

## 🎯 CRITERIOS DE ÉXITO

### Objetivo 1 (URLs):
- [ ] Identificar causa root de URLs faltantes
- [ ] Implementar fix en email processor
- [ ] Re-procesar emails y verificar extracción
- [ ] Aumentar de 12.5% a >90% jobs con URLs

### Objetivo 2 (Status):
- [ ] Ejecutar standardize_status_v2.py
- [ ] Verificar que todos tienen valores estándar
- [ ] Confirmar en Google Sheets

### Objetivo 3 (Auto-apply):
- [ ] Detectar LinkedIn Easy Apply buttons
- [ ] Map campos de formulario
- [ ] Auto-fill con datos de CV
- [ ] Submit con confirmación

---

## 📊 ESTADO FINAL ESPERADO

```
Total jobs: 16+
Con URLs: >90% (14+)
Status estandarizado: 100%
Auto-apply ready: True
Pipeline funcionando: 100%
```

---

## 🔗 REFERENCIAS

**Google Sheets:**  
https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

**Documentación actualizada:**
- `docs/PROJECT_STATUS.md` - Estado completo (recién actualizado)
- `docs/CONTROL_CENTER_GUIDE.md` - Guía del control center
- `docs/SOLUCION_DUPLICADOS.md` - Sistema de deduplicación

**Scripts útiles:**
- `control_center.py` - Interface principal
- `investigate_urls.py` - Investiga problema URLs
- `standardize_status_v2.py` - Fix status values
- `check_urls_status.py` - Diagnóstico rápido
- `verify_job_status.py` - Verifica URLs activas

---

## ⚡ COMANDO INICIAL RECOMENDADO

```bash
cd ~/Desktop/ai-job-foundry && python investigate_urls.py
```

Esto te mostrará:
- Qué sources tienen URLs
- Qué sources NO tienen URLs
- Patrones identificados
- Próximos pasos sugeridos

---

## 🚀 ¡ADELANTE!

Tienes TODO listo para continuar:
- ✅ OAuth funcionando
- ✅ Scripts de diagnóstico listos
- ✅ Documentación actualizada
- ✅ Plan de trabajo claro

**Prioridad #1:** Resolver problema de URLs (87.5% faltantes)  
**Tiempo estimado:** 2-3 horas para fix completo  
**Impacto:** Desbloquea auto-apply y verificación automática

¡Buena suerte! 🎯
