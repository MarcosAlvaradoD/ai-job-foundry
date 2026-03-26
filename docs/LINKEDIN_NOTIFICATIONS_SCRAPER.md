# 🔍 LinkedIn Notifications Scraper - Quick Start

## 🎯 ¿Qué hace?

Extrae ofertas de trabajo de las **recomendaciones de LinkedIn** (panel derecho + Jobs page) y las guarda automáticamente en Google Sheets.

---

## 🚀 Uso Rápido

### Opción 1: Test Simple (Solo Scraping)
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py test_linkedin_notifications.py
```

### Opción 2: Workflow Completo (Scrape + Analyze + Apply)
```powershell
# DRY RUN (testing - no aplica realmente)
py run_linkedin_workflow.py --all

# LIVE (aplica realmente a jobs con FIT >= 7)
py run_linkedin_workflow.py --all --live
```

### Opción 3: Pasos Individuales
```powershell
# Solo scraping
py run_linkedin_workflow.py --scrape-only

# Solo análisis AI
py run_linkedin_workflow.py --analyze-only

# Solo auto-apply
py run_linkedin_workflow.py --apply-only
```

---

## 📊 ¿Qué Extrae?

El scraper captura:
- ✅ Título del trabajo
- ✅ Empresa
- ✅ Ubicación
- ✅ URL directa al job
- ✅ Si tiene "Easy Apply" badge
- ✅ Fecha de scraping

**Fuentes:**
- LinkedIn Jobs page (https://www.linkedin.com/jobs/)
- Recomendaciones personalizadas
- "Jobs for you" section

---

## 🔄 Flujo Completo Automatizado

```
1. SCRAPE      → Extrae ~20 jobs de LinkedIn notifications
   ⬇️
2. ANALYZE     → Calcula FIT scores con AI (Qwen 2.5 14B)
   ⬇️
3. FILTER      → Selecciona jobs con FIT >= 7
   ⬇️
4. AUTO-APPLY  → Aplica automáticamente con Easy Apply
```

---

## ⚙️ Configuración

### Primera Vez:

1. **Login a LinkedIn** en tu navegador normal
2. **Mantén la sesión activa**
3. Ejecuta el scraper
4. El scraper guardará tu sesión automáticamente

### Archivo de Sesión:
- Ubicación: `data/credentials/linkedin_session.json`
- Se crea automáticamente la primera vez
- Reutiliza la sesión en ejecuciones futuras

---

## 📈 Output

**Google Sheets:**
- Tab: **LinkedIn**
- Columnas: CreatedAt, Company, Role, Location, ApplyURL, FitScore, Status

**Ver en Sheets:**
https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

---

## 🔧 Troubleshooting

### "Not logged into LinkedIn"
```powershell
# Solución: Login manual
1. Abre Chrome/Edge
2. Ve a linkedin.com
3. Haz login normalmente
4. Vuelve a ejecutar el scraper
```

### "No jobs found"
```powershell
# Posibles causas:
- LinkedIn cambió selectores CSS (contacta a Marcos)
- No hay nuevas recomendaciones (espera 24h)
- Filtros de búsqueda demasiado específicos
```

### "Playwright error"
```powershell
# Reinstalar Playwright
py -m playwright install chromium
```

---

## 💡 Tips

**Frecuencia Recomendada:**
- 1-2 veces por día
- LinkedIn actualiza recomendaciones cada 24h

**Best Practices:**
1. Ejecuta en horario laboral (9am - 5pm CST)
2. No ejecutes más de 3 veces al día (para evitar rate limits)
3. Usa `--all` para workflow completo automatizado

**Integración con Pipeline:**
```powershell
# Agregar al pipeline diario
py run_daily_pipeline.py --all
# Incluirá LinkedIn scraping automáticamente
```

---

## 📁 Archivos Creados

```
core/ingestion/
  └─ linkedin_notifications_scraper.py  # Scraper principal

test_linkedin_notifications.py         # Test rápido
run_linkedin_workflow.py                # Workflow completo

data/credentials/
  └─ linkedin_session.json              # Sesión guardada (auto-generado)
```

---

## 🎯 Próximos Pasos

Una vez que el scraper funciona:

1. **Integrar al Control Center** (menú opción "LinkedIn Scraper")
2. **Agregar a cron/scheduler** (ejecutar 2x al día)
3. **Crear variante para notificaciones push** (email alerts)

---

**Autor:** Marcos Alberto Alvarado  
**Fecha:** 2026-01-18  
**Versión:** 1.0
