# 🚀 CLAUDE CODE - PROMPT MAESTRO COMPLETO
**Proyecto:** AI Job Foundry  
**Estado:** 80% completo
**Objetivo:** Auto-Apply con IA Local (100% gratis)

---

## ⚡ PROBLEMA URGENTE RESUELTO

**LM Studio ahora requiere API token** - YA DESACTIVADO
- Toggle "Require Authentication" = OFF
- LM Studio corriendo en: http://172.17.32.1:11434
- Modelo: qwen2.5-14b-instruct

---

## 🔴 PROBLEMAS ACTUALES A RESOLVER

### 1. **FIT Scores con error HTTPConnection**
**Síntoma:** Columna S en Sheets muestra:
```
Error: HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded
```

**Causa:** Script usa `localhost:11434` pero LM Studio está en `172.17.32.1:11434`

**Solución:** Actualizar .env:
```env
LLM_URL=http://172.17.32.1:11434/v1/chat/completions
```

### 2. **URLs manuales NO calculan FIT**
**Síntoma:** URLs agregadas manualmente en Sheets NO tienen FIT score
**Sheets afectado:** LinkedIn tab (filas 168-209)
**Causa:** Script solo procesa jobs con ciertos criterios

**Solución:** Ejecutar:
```powershell
py scripts\maintenance\calculate_linkedin_fit_scores.py
```

### 3. **Auto-Apply abre páginas pero NO aplica**
**Síntoma:** Timeout después de 5 minutos
**Causa:** Selectores CSS no encuentran botones

**Solución:** Implementar Auto-Apply con IA Local (próximo objetivo)

---

## 📂 ESTRUCTURA DEL PROYECTO

```
C:\Users\MSI\Desktop\ai-job-foundry\
├── core/
│   ├── automation/
│   │   ├── auto_apply_linkedin.py              ← VIEJO (mantener)
│   │   ├── auto_apply_linkedin_ai_local.py     ← NUEVO (crear)
│   │   ├── linkedin_ocr_helper.py              ← Helper OCR
│   │   └── job_bulletin_processor.py
│   ├── enrichment/
│   │   └── ai_analyzer.py
│   ├── sheets/
│   │   └── sheet_manager.py
├── scripts/
│   ├── maintenance/
│   │   └── calculate_linkedin_fit_scores.py    ← USAR ESTE
│   └── oauth/
├── data/credentials/
│   ├── token.json
│   └── linkedin_session.json
├── .env                                        ← ACTUALIZAR IP
└── PROMPT_MIGRACION_AUTOAPPLY_AI.md            ← REFERENCIA

```

---

## 🎯 TAREAS INMEDIATAS (Orden de prioridad)

### **TAREA 1: Fix LM Studio IP (5 min)**
```powershell
# Actualizar .env
(Get-Content C:\Users\MSI\Desktop\ai-job-foundry\.env) -replace 'LLM_URL=http://localhost:11434','LLM_URL=http://172.17.32.1:11434' | Set-Content C:\Users\MSI\Desktop\ai-job-foundry\.env

# Verificar
py -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('LLM_URL'))"
```

### **TAREA 2: Calcular FIT scores faltantes (10 min)**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py scripts\maintenance\calculate_linkedin_fit_scores.py
```

**Resultado esperado:** ~50 jobs con FIT scores calculados

### **TAREA 3: Crear Auto-Apply AI Local (60 min)**

**Archivos a crear:**
1. `core/automation/linkedin_ocr_helper.py`
2. `core/automation/auto_apply_linkedin_ai_local.py`

**Stack tecnológico (100% gratis):**
- EasyOCR (extrae texto + coordenadas)
- LM Studio Qwen 2.5 14B (analiza y decide)
- Playwright smart locators (fallback)

**Instalación:**
```powershell
pip install easyocr pillow
```

**Implementación:** Ver `PROMPT_MIGRACION_AUTOAPPLY_AI.md` líneas 200-600

---

## 🔧 ARCHIVOS CRÍTICOS

### **SheetManager métodos correctos:**
```python
# CORRECTO:
jobs = sheet_manager.get_all_jobs('linkedin')  # minúscula
sheet_manager.update_job(row, updates, 'linkedin')

# INCORRECTO:
jobs = sheet_manager.read_tab('LinkedIn')  # NO EXISTE
```

### **Google Sheets:**
```
URL: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
TAB: LinkedIn (159 jobs)
```

### **LM Studio:**
```
URL CORRECTA: http://172.17.32.1:11434/v1/chat/completions
Modelo: qwen2.5-14b-instruct
Auth: DESACTIVADA
```

---

## 📊 MÉTRICAS ACTUALES

- **LinkedIn Jobs:** 159 (147 con FIT, 12 pendientes)
- **Glassdoor Jobs:** 452
- **Indeed Jobs:** 5
- **FIT 7+:** ~140 jobs (elegibles para auto-apply)
- **Aplicados:** 0 (esperando AI local)

---

## ⚠️ PRINCIPIOS CRÍTICOS

1. **NO romper código que funciona**
2. **Crear archivos NUEVOS**, no modificar viejos
3. **DRY RUN primero**, LIVE después
4. **Un cambio a la vez**

---

## 📝 COMANDOS ÚTILES

```powershell
# Control Center
py control_center.py

# Ver Sheets
start https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg

# Verificar LM Studio
curl http://172.17.32.1:11434/v1/models

# Calcular FIT scores
py scripts\maintenance\calculate_linkedin_fit_scores.py
```

---

**EJECUTA TAREAS 1 Y 2 PRIMERO.** Luego implementamos Auto-Apply AI Local.
