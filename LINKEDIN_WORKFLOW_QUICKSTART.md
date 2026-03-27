# 🚀 LINKEDIN WORKFLOW - LISTO PARA USAR

## ✅ LO QUE SE CREÓ (2026-01-18)

### 1. LinkedIn Notifications Scraper
**Qué hace:** Extrae ofertas de las recomendaciones de LinkedIn
**Archivo:** `core/ingestion/linkedin_notifications_scraper.py`

### 2. Workflow Completo Automatizado
**Qué hace:** Scrape → AI Analysis → Auto-Apply (todo automático)
**Archivo:** `run_linkedin_workflow.py`

### 3. Quick Launcher (Menu)
**Qué hace:** Menú interactivo para ejecutar workflows
**Archivo:** `RUN_LINKEDIN_WORKFLOW.bat`

---

## 🎯 CÓMO USAR (3 OPCIONES)

### ✨ OPCIÓN 1: Menú Interactivo (MÁS FÁCIL)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\RUN_LINKEDIN_WORKFLOW.bat
```

Selecciona:
- **Opción 2** → Test completo (DRY RUN - no aplica)
- **Opción 3** → LIVE (aplica realmente)

---

### ⚡ OPCIÓN 2: Comando Directo (MÁS RÁPIDO)

**Test DRY RUN:**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py run_linkedin_workflow.py --all
```

**LIVE (aplica realmente):**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py run_linkedin_workflow.py --all --live
```

---

### 🔧 OPCIÓN 3: Pasos Individuales (MÁS CONTROL)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry

# Paso 1: Solo scraping
py run_linkedin_workflow.py --scrape-only

# Paso 2: Solo análisis AI
py run_linkedin_workflow.py --analyze-only

# Paso 3: Solo auto-apply (DRY RUN)
py run_linkedin_workflow.py --apply-only

# Paso 3b: Solo auto-apply (LIVE)
py run_linkedin_workflow.py --apply-only --live
```

---

## 📋 FLUJO COMPLETO

```
1. SCRAPE      → LinkedIn notifications (~20 jobs)
   ⬇️ ~2 min
   
2. ANALYZE     → AI calcula FIT scores
   ⬇️ ~5 min
   
3. FILTER      → Jobs con FIT >= 7
   ⬇️ ~0 sec
   
4. AUTO-APPLY  → Aplica automáticamente
   ⬇️ ~3 min
   
TOTAL: ~10 minutos
```

---

## ⚙️ PRIMERA VEZ - SETUP

### 1. Login a LinkedIn

```
1. Abre Chrome/Edge
2. Ve a linkedin.com
3. Haz login normalmente
4. Mantén la sesión activa
```

### 2. Ejecuta el workflow

```powershell
py run_linkedin_workflow.py --all
```

El sistema guardará tu sesión automáticamente en:
`data/credentials/linkedin_session.json`

---

## 📊 VER RESULTADOS

**Google Sheets:**
https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

**Tab:** LinkedIn

**Ver desde terminal:**
```powershell
py view_sheets_data.py
```

---

## 🔥 CASOS DE USO

### Caso 1: Quick Daily Check
```powershell
# Ejecuta 1-2 veces al día
.\RUN_LINKEDIN_WORKFLOW.bat
# Opción 2 (DRY RUN)
```

### Caso 2: Aplicar Inmediatamente
```powershell
# Cuando ves jobs buenos en el pipeline
py run_linkedin_workflow.py --all --live
```

### Caso 3: Solo Ver Qué Hay
```powershell
# Solo scrape, sin aplicar
py run_linkedin_workflow.py --scrape-only
py view_sheets_data.py
```

---

## 🐛 TROUBLESHOOTING

### "Not logged into LinkedIn"
**Solución:**
```powershell
# Borrar sesión guardada y login de nuevo
del data\credentials\linkedin_session.json
# Luego login manual en Chrome y re-ejecutar
```

### "No jobs found"
**Causas:**
- No hay nuevas recomendaciones (normal, espera 24h)
- LinkedIn cambió estructura (avisar a Marcos)

### "Timeout error"
**Solución:**
```powershell
# Aumentar timeout en run_linkedin_workflow.py
# Línea 75: timeout=600 (cambiar a 900)
```

---

## 📈 PRÓXIMAS MEJORAS

- [ ] Agregar scraping de notificaciones push (email alerts)
- [ ] Integrar al Control Center (menú principal)
- [ ] Agregar 4 job boards nuevos (nodesk, weworkremotely, etc.)
- [ ] Scheduler automático (2x al día)

---

## ✅ CHECKLIST RÁPIDO

Antes de ejecutar LIVE:

- [ ] LinkedIn session activa (login manual)
- [ ] LM Studio corriendo (http://172.23.0.1:11434)
- [ ] Google Sheets accesible
- [ ] CV actualizado en `data/cv/`
- [ ] Revisar jobs con FIT >= 7 antes de aplicar

---

**Autor:** Marcos Alberto Alvarado  
**Fecha:** 2026-01-18 00:45 CST  
**Versión del Sistema:** 3.3 (90% completo)

**¡LISTO PARA USAR! 🚀**
