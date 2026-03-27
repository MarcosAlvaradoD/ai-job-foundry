# 🚀 AI JOB FOUNDRY - INICIO CLAUDE CODE

Hola Claude Code, soy Marcos. Este es mi proyecto de automatización de búsqueda de empleo.

## 📍 UBICACIÓN
C:\Users\MSI\Desktop\ai-job-foundry

## 🎯 QUÉ NECESITO AHORA

**TAREA INMEDIATA:** Completar 17 FIT scores restantes que fallaron por rate limit de Google Sheets

### Contexto:
- Acabo de ejecutar calculate_linkedin_fit_scores.py
- Procesó 52/69 jobs exitosamente
- 17 fallaron con error 429 (rate limit: 60 escrituras/minuto)
- Ya existe calculate_linkedin_fit_scores_v2.py con protección de rate limit

### Comando a ejecutar:
\\\powershell
py scripts\maintenance\calculate_linkedin_fit_scores_v2.py
\\\

## 📊 ESTADO ACTUAL

### ✅ Funcionando:
- LM Studio: http://172.17.32.1:11434 (Qwen 2.5 14B)
- Google Sheets: 252 jobs en LinkedIn tab
- OAuth: auto-refresh activo
- Gmail API: procesando emails

### 📈 Métricas:
- Total LinkedIn jobs: 252
- Con FIT score: ~235 (93%)
- Sin FIT score: ~17 (7%)
- FIT 7+: ~235 (auto-apply ready)

## 🔧 CONFIGURACIÓN

### Variables críticas (.env):
\\\
LLM_URL=http://172.17.32.1:11434/v1/chat/completions
LLM_MODEL=qwen2.5-14b-instruct
GOOGLE_SHEETS_ID=1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
LINKEDIN_EMAIL=markalvati@gmail.com
LINKEDIN_PASSWORD=4&nxXdJbaL["Rax*C!8e"4P5
\\\

### Google Sheets:
- URL: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEetTsCIBxdg
- Tab activa: LinkedIn (252 rows)

## 📁 ARCHIVOS CLAVE

| Archivo | Función |
|---------|---------|
| scripts/maintenance/calculate_linkedin_fit_scores_v2.py | Calcula FIT scores con protección rate limit |
| core/sheets/sheet_manager.py | Gestiona Google Sheets |
| core/enrichment/ai_analyzer.py | Analiza jobs con LM Studio |
| .env | Variables de entorno |

## 🎯 PRÓXIMOS PASOS DESPUÉS

1. ✅ Completar 17 FIT scores restantes
2. ⏳ Implementar Auto-Apply AI Local (TAREA 3)
   - Instalar: pip install easyocr pillow
   - Crear: core/automation/auto_apply_linkedin_ai_local.py
   - Stack: EasyOCR + LM Studio + Playwright

## 🚨 PROBLEMAS CONOCIDOS

1. **Rate Limit Google Sheets:** 60 escrituras/minuto → Solucionado en V2
2. **LinkedIn Auto-Apply:** No funciona, necesita implementación con IA
3. **Indeed Scraper:** Timeout, proceso se congela

## 💡 PRINCIPIOS

- Local-first AI (LM Studio > Cloud)
- NO romper código funcionando
- DRY RUN antes de LIVE
- Windows-optimized (PowerShell, py commands)
- Logging comprehensivo

## 📞 PERFIL PROFESIONAL

**Marcos Alberto Alvarado De La Torre**
- Roles objetivo: PM, PO, Senior BA, IT Manager, ETL Consultant
- NO busca: Software Developer
- Ubicación: Guadalajara, México
- Preferencia: Remote work (familia con bebé)
- Experiencia: ERP migrations, ETL 800+ TB, BI/Power BI

## ✅ PRIMER COMANDO

Por favor ejecuta:

\\\powershell
py scripts\maintenance\calculate_linkedin_fit_scores_v2.py
\\\

Esto completará los 17 FIT scores restantes con protección automática contra rate limit.

Lee el archivo CLAUDE.md en la raíz del proyecto para contexto completo.
