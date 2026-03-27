# 🚀 AI JOB FOUNDRY - CLAUDE CODE INSTRUCTIONS

**Versión:** 2.0  
**Fecha:** 2026-03-07  
**Usuario:** Marcos Alberto Alvarado De La Torre  
**Ubicación:** C:\Users\MSI\Desktop\ai-job-foundry

---

## 🎯 PROYECTO OVERVIEW

Sistema automatizado de búsqueda de empleo que:
1. Scrapea LinkedIn/Indeed/Glassdoor
2. Procesa emails de reclutadores
3. Analiza match con IA local (LM Studio + Qwen 2.5 14B)
4. Calcula FIT SCORES (0-10)
5. Guarda en Google Sheets
6. Auto-aplica a ofertas (en desarrollo)

---

## 📊 ESTADO ACTUAL (2026-03-07)

### ✅ COMPLETADO:
- **TAREA 1:** LM Studio IP actualizada → http://172.17.32.1:11434
- **TAREA 2:** 52/69 FIT scores calculados (75%)
- OAuth funcionando con auto-refresh
- LinkedIn scraper operativo
- Gmail API procesando emails
- Google Sheets integrado

### ⏳ PENDIENTE:
- **17 FIT scores** restantes (rate limit issue)
- Auto-Apply con IA Local (TAREA 3)
- Interview Copilot

---

## 🗂️ ESTRUCTURA DEL PROYECTO

\\\
ai-job-foundry/
├── core/
│   ├── automation/
│   │   ├── gmail_jobs_monitor.py
│   │   ├── auto_apply_linkedin.py
│   │   └── job_bulletin_processor.py
│   ├── enrichment/
│   │   └── ai_analyzer.py
│   ├── ingestion/
│   │   ├── linkedin_scraper_V2.py
│   │   └── indeed_scraper.py
│   ├── sheets/
│   │   └── sheet_manager.py
│   └── utils/
│       └── llm_client.py
├── scripts/
│   ├── maintenance/
│   │   ├── calculate_linkedin_fit_scores.py
│   │   └── calculate_linkedin_fit_scores_v2.py
│   └── tests/
├── data/
│   ├── credentials/
│   │   ├── token.json
│   │   ├── credentials.json
│   │   └── linkedin_session.json
│   └── cv/
│       └── CV_Marcos_Alvarado.pdf
├── .env
└── control_center.py
\\\

---

## 🔧 CONFIGURACIÓN CRÍTICA

### Variables de Entorno (.env):
\\\env
LLM_URL=http://172.17.32.1:11434/v1/chat/completions
LLM_MODEL=qwen2.5-14b-instruct
GOOGLE_SHEETS_ID=1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
GMAIL_ADDRESS=markalvati@gmail.com
LINKEDIN_EMAIL=markalvati@gmail.com
LINKEDIN_PASSWORD=4&nxXdJbaL["Rax*C!8e"4P5
\\\

### LM Studio:
- URL: http://172.17.32.1:11434
- Modelo: Qwen/Qwen2.5-14B-Instruct-GGUF
- Auth: DESACTIVADA
- Status: ✅ Running

### Google Sheets:
- ID: 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
- URL: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
- Tabs: Registry, LinkedIn (252 jobs), Indeed, Glassdoor

---

## 🎯 TAREAS INMEDIATAS

### TAREA 2 (URGENTE): Completar 17 FIT Scores restantes

**Problema:** Rate limit de Google Sheets (60 escrituras/minuto)

**Solución:** Usar script V2 con protección de rate limit

\\\powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py scripts\maintenance\calculate_linkedin_fit_scores_v2.py
\\\

**Resultado esperado:**
- Procesará 17 jobs pendientes
- Pausará automáticamente al acercarse a rate limit
- Guardará todos los FIT scores en Google Sheets

### TAREA 3: Auto-Apply AI Local (100% gratis)

**Stack tecnológico:**
1. EasyOCR - Extrae texto + coordenadas de screenshots
2. LM Studio (Qwen 2.5 14B) - Analiza y decide acciones
3. Playwright - Ejecuta navegación

**Instalación:**
\\\powershell
pip install easyocr pillow
\\\

**Archivos a crear:**
1. \core/automation/linkedin_ocr_helper.py\
2. \core/automation/auto_apply_linkedin_ai_local.py\

**Flujo:**
1. Screenshot de página → EasyOCR extrae texto
2. LM Studio analiza: "¿Dónde está el botón 'Easy Apply'?"
3. Playwright hace click en coordenadas
4. Repite hasta completar aplicación
5. Actualiza Google Sheets: Status="Applied"

---

## 📝 COMANDOS ÚTILES

### Control Center:
\\\powershell
py control_center.py
\\\

### Calcular FIT Scores:
\\\powershell
py scripts\maintenance\calculate_linkedin_fit_scores_v2.py
\\\

### Ver Google Sheets:
\\\powershell
start https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
\\\

### Verificar LM Studio:
\\\powershell
curl http://172.17.32.1:11434/v1/models
\\\

### Test Email Processing:
\\\powershell
py scripts\tests\test_email_processing.py
\\\

### LinkedIn Scraper:
\\\powershell
py scripts\visual_test.py
\\\

---

## 🚨 PROBLEMAS CONOCIDOS

### 1. Google Sheets Rate Limit (429)
**Síntoma:** Error al guardar FIT scores  
**Causa:** >60 escrituras/minuto  
**Solución:** Script V2 con delays automáticos

### 2. LinkedIn Auto-Apply Timeout
**Síntoma:** Abre páginas pero no aplica  
**Causa:** Selectores CSS no encuentran botones  
**Solución:** Implementar Auto-Apply AI Local (TAREA 3)

### 3. Claude Code API Error
**Síntoma:** "request.thinking.type: Invalid discriminator value"  
**Causa:** Bug de API de Anthropic  
**Solución:** Usar Claude Code standalone (funcionando) o Chat Web

---

## 🎓 PERFIL PROFESIONAL DEL USUARIO

**Roles objetivo:**
- Project Manager
- Product Owner
- Senior Business Analyst
- IT Manager
- ETL Consultant

**NO busca:** Software Developer positions

**Experiencia:**
- ERP migrations (Intelisis → Dynamics AX LATAM)
- ETL masivo (800+ TB Toyota Finance)
- IT Infrastructure (Ubiquiti → Meraki)
- BI/Power BI
- Proyectos multinacionales

**Ubicación:** Guadalajara, México (CST, GMT-6)  
**Preferencia:** Remote work (familia con bebé)

---

## 📊 MÉTRICAS ACTUALES

| Métrica | Valor |
|---------|-------|
| LinkedIn Jobs | 252 |
| Con FIT Score | 235 (93%) |
| Sin FIT Score | 17 (7%) |
| FIT 7+ | ~235 |
| Glassdoor Jobs | 452 |
| Indeed Jobs | 5 |
| Aplicados | 0 |

---

## 🔐 ARCHIVOS SENSIBLES (NO MODIFICAR)

- \data/credentials/token.json\ - OAuth Google
- \data/credentials/credentials.json\ - Google API
- \data/credentials/linkedin_session.json\ - LinkedIn session
- \.env\ - Variables de entorno

---

## ✅ PRINCIPIOS DE DESARROLLO

1. **NO romper código que funciona**
2. **Crear archivos NUEVOS**, no modificar viejos
3. **DRY RUN primero**, LIVE después
4. **Un cambio a la vez**
5. **Logging comprehensivo** en logs/powershell/
6. **Windows-optimized:** PowerShell, paths absolutos

---

## 🚀 WORKFLOW RECOMENDADO

1. **Verificar estado:**
   \\\powershell
   py check_linkedin_status.py
   \\\

2. **Completar FIT scores:**
   \\\powershell
   py scripts\maintenance\calculate_linkedin_fit_scores_v2.py
   \\\

3. **Verificar en Sheets:**
   https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg

4. **Implementar Auto-Apply AI:**
   - Instalar: \pip install easyocr pillow\
   - Crear: \core/automation/auto_apply_linkedin_ai_local.py\
   - Test en DRY RUN
   - Ejecutar LIVE

---

## 📞 CONTACTO Y RECURSOS

**Google Sheets Dashboard:**  
https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg

**LM Studio Interface:**  
http://172.17.32.1:11434

**Documentación de referencia:**
- PROJECT_STATUS.md - Estado detallado
- ESTADO_FINAL_2026-03-07.md - Resumen de sesión
- PROMPT_MIGRACION_AUTOAPPLY_AI.md - Detalles Auto-Apply

---

## 🎯 META DICIEMBRE 2026

- ✅ Gmail processing (100%)
- ✅ AI Analysis (100%)
- ✅ Google Sheets (100%)
- ⏳ FIT Scores (93% - completar 100%)
- ⏳ Auto-Apply (0% - implementar)
- ❌ Interview Copilot (0%)

**Progreso total:** 85%  
**Meta:** 95% by end of December

---

**IMPORTANTE:** Este archivo contiene TODA la información necesaria para trabajar con el proyecto. Lee completamente antes de ejecutar comandos.
