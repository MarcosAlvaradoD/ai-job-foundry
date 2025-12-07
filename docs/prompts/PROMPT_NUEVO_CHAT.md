# 🚀 PROMPT PARA NUEVO CHAT - AI JOB FOUNDRY

**Copia esto en el nuevo chat con Claude:**

---

```
Lee el archivo PROMPT_NUEVO_CHAT.md en C:\Users\MSI\Desktop\ai-job-foundry para contexto completo.

RESUMEN RÁPIDO:
- Proyecto: AI Job Foundry (sistema automatizado búsqueda empleo)
- Versión: 2.3 (Web App Fixed + Email Sync + Salary Scoring)
- Progreso: 98%
- Usuario: Marcos Alvarado (Guadalajara, MX)
- Roles target: PM/PO/BA/IT Manager (NO Developer)

ÚLTIMA SESIÓN (2025-11-30):
✅ Arreglado Web App (dashboard mostraba 0, botones "undefined")
✅ Email → Sheets sync automático
✅ Salary-based FIT scoring (penalties por salario bajo)
✅ Auto-mark negatives en todas las tabs
✅ Auto-start servicios (Docker + LM Studio)

PENDIENTE:
1. Fix dashboard keywords (Resumen tab muestra errores LM Studio)
2. Integrar nuevas funciones al Control Center menu
3. Decidir uso de Registry tab
4. Completar auto-apply testing

Archivos clave:
- PROJECT_STATUS.md (308 líneas) - Estado completo
- WEB_APP_ERRORS_FIXED.md (236 líneas) - Fixes recientes
- COMANDOS_CORRECTOS.md (217 líneas) - PowerShell syntax

Ubicación: C:\Users\MSI\Desktop\ai-job-foundry
```

---

# 📋 CONTEXTO COMPLETO (Si Claude necesita más detalles)

## 👤 USUARIO

**Nombre:** Marcos Alberto Alvarado de la Torre  
**Ubicación:** Guadalajara, México (CST, GMT-6)  
**Hardware:** RTX 4090 24GB VRAM, 64GB RAM  
**OS:** Windows 11  
**Python:** 3.13  
**PowerShell:** 7.5.4

**Roles objetivo:**
- Project Manager
- Product Owner  
- Senior Business Analyst
- IT Manager

**NO busca:** Software Developer/Programmer roles

**Experiencia:**
- ERP migrations (Intelisis → Dynamics AX)
- ETL (800+ TB procesados)
- IT Infrastructure (LAN/WAN, Meraki)
- BI/Power BI
- Multinational teams (México, Suecia)

---

## 🎯 PROYECTO: AI JOB FOUNDRY

**Objetivo:** Sistema "set it and forget it" para búsqueda automatizada de empleo

**Funcionalidades:**
1. Scrapea LinkedIn (100% funcional)
2. Procesa emails de Indeed/Glassdoor (100%)
3. Analiza match con AI local (LM Studio + Gemini fallback)
4. Calcula FIT scores 0-10 (ahora con salary penalties)
5. Guarda en Google Sheets
6. Auto-marca expired/rejected
7. Web app dashboard (FIXED v2.3)

**Progreso:** 98% completo

---

## 🆕 ÚLTIMA SESIÓN (2025-11-30) - LO MÁS IMPORTANTE

### 1. WEB APP ARREGLADO (v2.3)

**Problemas que tenía:**
- Dashboard mostraba todos 0 (Total Jobs: 0, High Fit: 0)
- Todos los botones → ERROR: undefined
- Solo "Verify URLs" funcionaba

**Causa raíz:**
- Rutas de scripts incorrectas en subprocess calls
- FIT score parsing malo (`"8/10"` → esperaba `int`)
- Scripts que no existían

**Solución:**
- `unified_app/app.py` reescrito completo (293 líneas)
- Todas las rutas corregidas
- FIT score parsing arreglado
- Helper function `run_script()` creado

**Ahora funciona:**
✅ Dashboard muestra números reales (78+ jobs)
✅ Todos los botones ejecutan scripts correctos
✅ Publicidad visible (3 zonas)

### 2. EMAIL → SHEETS SYNC

**Script:** `update_status_from_emails.py` (331 líneas)

**Qué hace:**
- Lee emails de empresas (últimos 30 días)
- Detecta keywords:
  - INTERVIEW_SCHEDULED: "technical interview", "interview scheduled"
  - REJECTED: "no longer accepting", "position filled"
  - OFFER: "job offer", "offer letter"
  - ASSESSMENT: "technical assessment", "coding challenge"
- Actualiza columna Status automáticamente
- Añade nota con timestamp en NextAction

**Ejemplo real:**
- Email de EPAM: "Technical Interview: Friday, Nov 28"
- Status actualiza: `Application submitted` → `INTERVIEW_SCHEDULED`

### 3. SALARY-BASED FIT SCORING

**Script:** `recalculate_fit_scores.py` (264 líneas)

**Penalties:**
- < $20k MXN → -5 puntos (SEVERO)
- $20k-30k MXN → -3 puntos
- $30k-50k MXN → -1 punto
- $50k-80k MXN → 0 (normal)
- > $80k MXN → +1 punto (bonus)

**Caso real:**
- Job con salario $17,000 MXN
- FIT original: 8/10
- Penalty aplicado: -5
- FIT final: 3/10
- Why: "[Salary: $17,000 MXN] Below minimum (penalty -5)"

### 4. MARK NEGATIVES EN TODAS LAS TABS

**Script:** `mark_all_negatives.py` (180 líneas)

**Qué hace:**
- Procesa: Jobs, LinkedIn, Indeed, Glassdoor
- Detecta keywords negativos (español + inglés):
  - "no longer accepting applications"
  - "este empleo no está disponible"
  - "position has been filled"
  - "payment is too low"
- Marca como `EXPIRED` o `REJECTED_BY_USER`

### 5. AUTO-START SERVICIOS

**Script:** `AUTO_START.bat` (49 líneas)

**Inicia automáticamente:**
1. Docker Desktop
2. LM Studio
3. Control Center / Web App

### 6. OAUTH TOKEN FIX

**Scripts:**
- `FIX_OAUTH_TOKEN.bat` (55 líneas)
- `check_oauth_token.py` (210 líneas)
- `OAUTH_TOKEN_EXPIRADO.md` (317 líneas)

**Problema:** Token expira cada 7-30 días  
**Solución:** Re-autenticación automática con Google

---

## 📂 ESTRUCTURA ARCHIVOS

```
ai-job-foundry/
├── unified_app/
│   ├── app.py (293 líneas) ← REESCRITO v2.3
│   └── templates/
│       └── index.html
├── core/
│   ├── ingestion/
│   │   └── ingest_email_to_sheet_v2.py
│   ├── enrichment/
│   │   └── enrich_sheet_with_llm_v3.py
│   ├── automation/
│   │   ├── job_bulletin_processor.py
│   │   └── linkedin_auto_apply.py
│   ├── sheets/
│   │   └── sheet_manager.py
│   └── jobs_pipeline/
│       ├── job_cleaner.py
│       ├── sheet_summary.py
│       └── system_health_check.py
├── scripts/
│   └── visual_test.py (LinkedIn scraper)
├── data/
│   └── credentials/
│       ├── token.json
│       └── credentials.json
├── AUTO_START.bat ← NUEVO
├── CLEANUP_ALL_JOBS.bat ← NUEVO
├── FIX_OAUTH_TOKEN.bat ← NUEVO
├── START_UNIFIED_APP.bat
├── control_center.py
├── mark_all_negatives.py ← NUEVO
├── recalculate_fit_scores.py ← NUEVO
├── update_status_from_emails.py ← NUEVO
├── check_oauth_token.py ← NUEVO
├── PROJECT_STATUS.md (308 líneas) ← ACTUALIZADO
├── WEB_APP_ERRORS_FIXED.md (236 líneas) ← NUEVO
├── COMANDOS_CORRECTOS.md (217 líneas) ← NUEVO
├── SOLUCION_EMAIL_SYNC.md (352 líneas) ← NUEVO
└── OAUTH_TOKEN_EXPIRADO.md (317 líneas) ← NUEVO
```

---

## 🚀 COMANDOS FRECUENTES

### Inicio Rápido
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\AUTO_START.bat
```

### Web App
```powershell
.\START_UNIFIED_APP.bat
# Abre: http://localhost:5555
```

### Limpieza Completa
```powershell
.\CLEANUP_ALL_JOBS.bat
```
Ejecuta:
1. mark_all_negatives.py
2. recalculate_fit_scores.py
3. update_status_from_emails.py

### Fixes Individuales
```powershell
.\FIX_OAUTH_TOKEN.bat        # OAuth expirado
py mark_all_negatives.py     # Marcar negativos
py recalculate_fit_scores.py # Ajustar FIT
py update_status_from_emails.py # Sync emails
py check_oauth_token.py      # Verificar OAuth
```

---

## 📊 GOOGLE SHEETS

**ID:** 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

**Tabs:**
1. Jobs (principal) - 78+ jobs
2. LinkedIn - Scraping directo
3. Indeed - Via Gmail
4. Glassdoor - Via Gmail
5. Resumen - Dashboard (⚠️ keywords erróneos)
6. Registry - Sin uso definido

**Columnas Jobs:**
- M: Status (New, INTERVIEW_SCHEDULED, EXPIRED, REJECTED_BY_USER)
- N: NextAction (Timeline de cambios)
- P: FitScore (0-10/10)
- Q: Why (Explicación del score)
- J: Comp (Salary)

---

## 💰 POLÍTICA SALARIO

```
< $20k MXN  → -5 puntos
$20k-30k    → -3 puntos
$30k-50k    → -1 punto
$50k-80k    → 0
> $80k      → +1 punto
```

**Mínimo aceptable:** $30,000 MXN (~$1,700 USD)

---

## ⏳ PENDIENTES (Continuar desde aquí)

### 1. Fix Dashboard Keywords (CRÍTICO)
**Problema:** Resumen tab muestra keywords de errores LM Studio  
**Keywords erróneos:** llm, conexi, error, httpconnection, host, 127.0.0.1, port, 11434  
**Causa:** Script de resumen incluye logs en vez de job keywords  
**Solución:** Crear script que filtre solo keywords reales de jobs

### 2. Integrar Nuevas Funciones al Control Center
**Pendiente:**
- Añadir opción 20: Mark All Negatives
- Añadir opción 21: Recalculate FIT Scores
- Actualizar prompt "0-17" → "0-21"

### 3. Registry Tab
**Decidir:**
- Opción A: Eliminar (no se usa)
- Opción B: Convertir en log de aplicaciones
- Opción C: Usar para tracking de entrevistas

### 4. Auto-Apply Testing
**Estado:** 80% funcional  
**Falta:** Testing exhaustivo con DRY RUN

---

## 🔧 TROUBLESHOOTING

### Web App No Carga
```powershell
# 1. Verificar OAuth
py check_oauth_token.py

# 2. Ver logs Flask
.\START_UNIFIED_APP.bat
# Mira consola para errores

# 3. Verificar Sheets tiene datos
py view_current_sheets.py
```

### OAuth Expirado
```powershell
.\FIX_OAUTH_TOKEN.bat
```

### Dashboard Muestra 0
- Verificar Google Sheets tiene jobs
- Revisar console de navegador (F12)
- Ver logs de Flask

### Botón Da Error
- Verificar script existe: `ls core/ingestion/ingest_email_to_sheet_v2.py`
- Ejecutar directo: `py core/ingestion/ingest_email_to_sheet_v2.py`
- Ver Console Output en web app

---

## 💡 TIPS PARA CLAUDE

### PowerShell Syntax
```powershell
# ❌ MAL (PowerShell 7)
FIX_OAUTH_TOKEN.bat

# ✅ BIEN
.\FIX_OAUTH_TOKEN.bat
```

### Paths Absolutos
```
C:\Users\MSI\Desktop\ai-job-foundry\
```

### Python Command
```powershell
py script.py  # ✅ BIEN
python script.py  # ❌ Puede fallar
```

---

## 📚 DOCUMENTOS ESENCIALES

**Leer en este orden:**

1. **PROJECT_STATUS.md** (308 líneas) - Estado completo
2. **WEB_APP_ERRORS_FIXED.md** (236 líneas) - Fixes web app
3. **COMANDOS_CORRECTOS.md** (217 líneas) - PowerShell syntax
4. **SOLUCION_EMAIL_SYNC.md** (352 líneas) - Email sync
5. **OAUTH_TOKEN_EXPIRADO.md** (317 líneas) - OAuth fix

**Perfil profesional:**
- PROMPT_MAESTRO___PERFIL_LABORAL_C.txt

---

## 🎯 OBJETIVOS PRÓXIMA SESIÓN

1. Fix dashboard keywords (Resumen tab)
2. Integrar mark_all_negatives + recalculate_fit al menú
3. Decidir qué hacer con Registry tab
4. Testing completo auto-apply

---

**Versión:** 2.3  
**Fecha:** 2025-11-30  
**Progreso:** 98%  
**Ubicación:** C:\Users\MSI\Desktop\ai-job-foundry
