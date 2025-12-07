# 🚀 AI JOB FOUNDRY - QUICK START GUIDE

**Fecha:** 2025-11-23  
**Estado:** 100% COMPLETO ✅  
**Tu entrevista:** Monday, November 24, 2025

---

## ⚡ INICIO ULTRA RÁPIDO (3 pasos)

### 1️⃣ Ejecutar Unified App (TODO EN UNO)
```powershell
# En la raíz del proyecto:
START_UNIFIED_APP.bat
```

**Esto hace:**
- ✅ Verifica todos los servicios
- ✅ Inicia LM Studio si es necesario
- ✅ Lanza unified web app (port 5555)
- ✅ Abre navegador automáticamente

**Acceso:** http://localhost:5555

### 2️⃣ Ver Dashboard y Jobs
Una vez en http://localhost:5555 verás:
- 📊 **Dashboard** con estadísticas en tiempo real
- 🎯 **16 jobs** monitoreados
- 💚 **3 high-fit matches** (FIT 7+)
- 🔧 **17 funciones** del Control Center

### 3️⃣ (Opcional) Auto-Apply
```powershell
# Test sin aplicar (RECOMENDADO PRIMERO)
py run_auto_apply.py --dry-run

# Aplicar realmente (SOLO SI ESTÁS SEGURO)
py run_auto_apply.py --live
```

---

## 📋 LO QUE ACABAMOS DE COMPLETAR

### ✅ UNIFIED WEB APP (100%)
**Ubicación:** `unified_app/`  
**Características:**
- Dashboard con Chart.js
- 17 funciones del Control Center via web
- 3 espacios de publicidad integrados
- System health monitoring
- Console output en tiempo real

**Archivos creados:**
- `unified_app/app.py` (481 líneas) - Backend Flask
- `unified_app/templates/index.html` (500 líneas) - Frontend
- `START_UNIFIED_APP.bat` (109 líneas) - Auto-starter

### ✅ AUTO-APPLY LINKEDIN (100%)
**Ubicación:** `core/automation/auto_apply_linkedin.py`  
**Características:**
- DRY RUN mode (testing)
- LIVE mode (aplicaciones reales)
- Filtro FIT score 7+
- Rate limiting (max 10/run)
- Stealth mode
- Google Sheets integration

**Archivos creados:**
- `core/automation/auto_apply_linkedin.py` (271 líneas)
- `run_auto_apply.py` (71 líneas) - Runner

### ✅ PROJECT STATUS ACTUALIZADO
**Ubicación:** `PROJECT_STATUS.md` (321 líneas)  
**Estado:** 100% completo

---

## 🎯 ESPACIOS DE PUBLICIDAD INTEGRADOS

Tu unified app tiene **3 espacios listos para monetizar:**

1. **Top Banner** - 728x90 pixels
2. **Sidebar** - 300x600 pixels  
3. **Bottom Banner** - 970x90 pixels

**Para activar Google AdSense:**
1. Registra tu sitio en https://adsense.google.com
2. Copia el código de anuncio
3. Reemplaza los div `.ad-container` en `index.html`

---

## 🔧 FUNCIONES DISPONIBLES EN WEB UI

### Pipeline Operations (2)
1. 🚀 Full Pipeline - Ejecuta todo (emails + AI + expire + report)
2. ⚡ Quick Pipeline - Solo emails + report

### Individual Operations (6)
3. 📧 Process Emails - Reclutadores directos
4. 📬 Process Bulletins - LinkedIn/Indeed/Glassdoor
5. 🤖 AI Analysis - Calcular FIT SCORES
6. 🚫 Check Expired - Verificar ofertas vencidas
7. 🔍 Verify URLs - Scraper automático
8. 📊 Generate Report - Reporte completo

### Web Scraping (2)
9. 🔗 LinkedIn Scraper - Buscar ofertas
10. 🔗 Indeed Scraper - Buscar ofertas

### Auto-Apply (2)
11. 🎯 DRY RUN - Test sin aplicar
12. 💼 LIVE - Aplicar realmente

### Utilities (5)
13. 📊 Dashboard - Esta página
14. 📄 Google Sheets - Abrir en navegador
15. 🩺 Health Check - Verificar sistema
16. 👁️ View Data - Ver datos en consola
17. 🔄 Refresh OAuth - Renovar autenticación

---

## ⚠️ IMPORTANTE ANTES DE EMPEZAR

### 1. Cambiar Modelo AI (RECOMENDADO)
Tu LM Studio usa **Qwen 2.5 14B** que tiene limitaciones.

**Modelo recomendado:** Llama-3-Groq-70B-Tool-Use Q4_K_M

**Cómo instalarlo:**
1. Abrir LM Studio
2. Buscar: `Llama-3-Groq-70B-Tool-Use`
3. Descargar: **Q4_K_M** (42GB)
4. Load model y probar

**Por qué:**
- 90.76% accuracy en tool use
- Tu hardware (RTX 4090 + 64GB RAM) lo soporta perfectamente
- Especializado en function calling/MCP tools

### 2. Verificar Google Sheets
```powershell
py view_current_sheets.py
```
Deberías ver tus 16 jobs con FIT scores.

### 3. Verificar OAuth
```powershell
py verify_oauth.py
```
Si hay error, ejecutar:
```powershell
py reauthenticate_gmail_v2.py
```

---

## 🧪 PROBAR AUTO-APPLY (DRY RUN)

**ANTES de aplicar realmente, PRUEBA:**

```powershell
py run_auto_apply.py --dry-run
```

**Esto hará:**
1. Buscar jobs con FIT 7+ en Google Sheets
2. Filtrar solo LinkedIn Easy Apply
3. Simular aplicación (NO aplica realmente)
4. Mostrar qué haría en modo LIVE

**Output esperado:**
```
🚀 AI JOB FOUNDRY - AUTO-APPLY LINKEDIN
Mode: DRY RUN (testing only)
FIT Score threshold: 7+
Max applications per run: 10

✅ Found 3 eligible jobs

[1/3] Processing job...
[DRY RUN] Applying to: Technical Product Owner at Svitla Systems
URL: https://linkedin.com/jobs/...
✅ [DRY RUN] Would apply to this job

...

📊 AUTO-APPLY SUMMARY
Jobs processed: 3
Applications (would be) submitted: 3
Errors: 0
```

---

## 🎯 WORKFLOW RECOMENDADO PARA HOY

### Antes de tu entrevista el lunes:

1. **Ejecutar unified app:**
   ```powershell
   START_UNIFIED_APP.bat
   ```

2. **Procesar emails nuevos:**
   - Click en "📧 Process Emails" en el dashboard
   - Ver output en consola

3. **Verificar FIT scores:**
   - Ver estadísticas en dashboard
   - Revisar gráfico de distribución

4. **Probar auto-apply (DRY RUN):**
   ```powershell
   py run_auto_apply.py --dry-run
   ```

5. **Si estás satisfecho, aplicar LIVE:**
   ```powershell
   py run_auto_apply.py --live
   ```
   ⚠️ CUIDADO: Esto aplica realmente a las ofertas

---

## 📊 VERIFICAR QUE TODO FUNCIONA

### Test 1: Health Check
```powershell
py core\jobs_pipeline\system_health_check.py
```

**Output esperado:**
```
✅ OAuth: Connected
✅ LM Studio: Running
✅ Google Sheets: Connected
✅ Files: All critical files present
```

### Test 2: Ver datos actuales
```powershell
py view_current_sheets.py
```

**Output esperado:**
```
Total jobs: 16
High-fit (7+): 3
Applied: X
Pending: Y
```

### Test 3: Unified app running
```powershell
START_UNIFIED_APP.bat
```

**Verificar:**
- ✅ Navegador abre en http://localhost:5555
- ✅ Dashboard muestra estadísticas
- ✅ System status muestra servicios conectados
- ✅ Botones responden al click

---

## 🐛 TROUBLESHOOTING RÁPIDO

### Error: "LM Studio offline"
```powershell
.\detect_lm_studio_ip.ps1
```

### Error: "OAuth not configured"
```powershell
py reauthenticate_gmail_v2.py
```

### Error: "Port 5555 in use"
```powershell
# En PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 5555).OwningProcess | Stop-Process -Force
```

### Error: "Google Sheets connection failed"
```powershell
py verify_oauth.py
```

---

## 📞 COMANDOS DE REFERENCIA RÁPIDA

```powershell
# === INICIO ===
START_UNIFIED_APP.bat              # Web app unificada (RECOMENDADO)
START_CONTROL_CENTER.bat           # CLI menu (alternativo)

# === AUTO-APPLY ===
py run_auto_apply.py --dry-run     # Test mode
py run_auto_apply.py --live        # Live mode (aplica realmente)

# === VERIFICACIÓN ===
py core\jobs_pipeline\system_health_check.py  # Health check completo
py view_current_sheets.py                      # Ver datos en Sheets
py verify_oauth.py                             # Verificar OAuth

# === PROCESAMIENTO ===
py scripts\test_email_processing.py  # Procesar emails
py process_bulletins.py              # Procesar boletines
py scripts\visual_test.py            # LinkedIn scraper

# === DEBUGGING ===
.\detect_lm_studio_ip.ps1            # Fix LM Studio IP
.\startup_check_v3.ps1               # Verificar servicios
py reauthenticate_gmail_v2.py        # Re-autenticar Gmail
```

---

## 🎉 ¡FELICIDADES!

Tu sistema AI Job Foundry está **100% completo** y listo para usar.

**Lo que tienes:**
- ✅ Sistema automatizado de búsqueda de empleo
- ✅ Dashboard web profesional
- ✅ Auto-apply functionality
- ✅ 3 espacios de publicidad para monetizar
- ✅ 16 jobs monitoreados
- ✅ 3 high-fit matches listos para aplicar

**Siguiente paso:**
```powershell
START_UNIFIED_APP.bat
```

**¡Buena suerte en tu entrevista del lunes! 🚀**

---

**Autor:** Marcos Alberto Alvarado de la Torre  
**Proyecto:** AI Job Foundry  
**Estado:** 100% Completo ✅  
**Fecha:** 2025-11-23
