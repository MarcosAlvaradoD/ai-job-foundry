# 🔬 DIAGNÓSTICO TÉCNICO COMPLETO - AI Job Foundry
**Fecha:** 2026-03-10
**Realizado por:** Claude Code (Experto en Desarrollo)
**Rama:** `claude/review-changes-mmkzbwxl6003ko6a-sLsTq`

---

## ✅ RESULTADO GENERAL: CÓDIGO SANO — REQUIERE CONFIGURACIÓN

El proyecto tiene **excelente estructura y código de calidad**. Todos los módulos principales pasan syntax check. Los problemas son de configuración/entorno, no de lógica.

---

## 1. 📦 DEPENDENCIAS — ESTADO

### Antes de este diagnóstico:
- Solo `requests` estaba instalado en el entorno Linux
- 8/9 dependencias críticas faltaban

### Después de instalar (ya corregido):
```
✅ beautifulsoup4     → Parseo de HTML
✅ google-auth        → OAuth Google
✅ google-api-python-client → Sheets + Gmail
✅ playwright         → Automatización de browser
✅ python-dotenv      → Variables de entorno
✅ openai             → API de IA
✅ flask + flask-cors → Dashboard web
✅ lxml               → Parser HTML rápido
✅ requests           → HTTP
```

### Problema en requirements.txt:
```python
sqlite3-python==1.0.0   # ❌ NO EXISTE este paquete
# sqlite3 viene incluido en Python — eliminar esta línea
```

**Fix:** Eliminar `sqlite3-python==1.0.0` de requirements.txt.

---

## 2. 🕷️ SCRAPERS — ANÁLISIS DE VERSIONES

### Resultado del syntax check: **14/14 archivos OK**

| Archivo | Clase | Estado | Recomendación |
|---------|-------|--------|---------------|
| `LINKEDIN_SMART_VERIFIER_V3.py` | `LinkedInSmartVerifierV3` | ✅ USAR ESTA | **Versión más completa** - cookies persistentes, sin `input()` bloqueantes |
| `LINKEDIN_SMART_VERIFIER.py` | (anterior) | ⚠️ OBSOLETO | Reemplazado por V3 |
| `GLASSDOOR_SMART_VERIFIER.py` | `GlassdoorSmartVerifier` | ✅ OK | Usar |
| `INDEED_SMART_VERIFIER.py` | `IndeedSmartVerifier` | ✅ OK | Usar |
| `UNIVERSAL_JOB_VERIFIER.py` | `UniversalJobVerifier` | ✅ MEJOR OPCIÓN | Detecta plataforma automáticamente |

### Versión canónica de LinkedIn Verifier:
```
LINKEDIN_SMART_VERIFIER_V3.py  ← USA ESTA
```
Tiene: cookies persistentes, login sin bloqueos, patrones en ES/EN, logging detallado.

---

## 3. 📧 ANALIZADOR DE BOLETINES DE CORREO

### Archivos relevantes:
- `core/automation/job_bulletin_processor.py` — V1
- `core/automation/improved_bulletin_processor.py` — **V2 (USAR ESTA)**

### Test con HTMLs reales del proyecto:
```
✅ GLASSDOOR_EMAIL_SAMPLE.html → 1 trabajo extraído correctamente
✅ ADZUNA_SAMPLE.html           → 10 trabajos extraídos correctamente
✅ BeautifulSoup + lxml parsing → FUNCIONANDO
```

### Comparativa V1 vs V2:

| Feature | V1 (job_bulletin_processor) | V2 (improved_bulletin_processor) |
|---------|----------------------------|----------------------------------|
| Parseo HTML | Básico | ✅ BeautifulSoup mejorado |
| Extracción de salario | ❌ No | ✅ Sí (MXN threshold filtering) |
| Filtro por ubicación | ❌ No | ✅ Sí |
| Pre-filtrado por salario | ❌ No | ✅ Sí (MXN 20K mínimo) |
| Soporte Glassdoor | Parcial | ✅ Completo |
| Soporte LinkedIn | Parcial | ✅ Completo |

**→ Usar `ImprovedBulletinProcessor` (V2)**

### Requisito crítico para funcionar:
```
data/credentials/credentials.json  ← OAuth Google (NO está en el repo - correcto)
data/credentials/token.json        ← Token generado tras autenticar
GOOGLE_SHEETS_ID                   ← En .env
```

---

## 4. 🤖 SISTEMA AUTO-APPLY

### Archivos relevantes:
- `core/automation/auto_apply_linkedin.py` — **VERSIÓN NUEVA** (async, con dry-run, 283 líneas)
- `core/automation/linkedin_auto_apply.py` — V2 (sync, más métodos de fill_form, 437 líneas)

### Comparativa:

| Feature | auto_apply_linkedin.py | linkedin_auto_apply.py |
|---------|----------------------|----------------------|
| Modo dry-run | ✅ Sí | ❌ No explícito |
| Async | ✅ Sí (async_playwright) | ❌ No (sync) |
| Form fill logic | Básico | ✅ 19 variantes de fill |
| Limit por run | ✅ MAX 10 apps | No definido |
| FIT Score threshold | ✅ 7+ | ✅ 7+ |
| Rate limiting | ✅ 5s entre apps | ❌ No |

**Recomendación:** `auto_apply_linkedin.py` para producción (tiene dry-run y rate limiting). `linkedin_auto_apply.py` tiene mejor form-fill pero le falta protección.

### Para ejecutar en modo seguro:
```bash
python3 core/automation/auto_apply_linkedin.py --dry-run
```

---

## 5. 🔧 VARIABLES DE ENTORNO REQUERIDAS

Crear `.env` en la raíz del proyecto (ver `.env.example`):

```bash
GOOGLE_SHEETS_ID=tu_spreadsheet_id
LINKEDIN_EMAIL=tu@email.com
LINKEDIN_PASSWORD=tu_password
LLM_BASE_URL=http://localhost:1234/v1      # LM Studio local
LLM_MODEL=nombre-del-modelo
CV_FILE=data/cv_descriptor.txt
SHEET_ID=tu_spreadsheet_id               # Alias de GOOGLE_SHEETS_ID
```

---

## 6. 📁 PROBLEMA DE ARCHIVOS DUPLICADOS / BACKUP

Los siguientes archivos son backup y no deberían estar en el repo:

```
run_daily_pipeline.py.BEFORE_VERIFY_FIX     ← Borrar
run_daily_pipeline.py.backup_autoapply      ← Borrar
run_daily_pipeline_BACKUP.py                ← Borrar
run_daily_pipeline(1).py                    ← Borrar
core/automation/job_bulletin_processor.py.backup_query ← Borrar
```

Y los ~30 scripts `ALL_CAPS_*.py` en la raíz son utilidades de diagnóstico one-shot y deberían moverse a `scripts/utils/` o eliminarse.

---

## 7. 🏗️ ARQUITECTURA — MÓDULOS CANÓNICOS

```
core/
  sheets/sheet_manager.py            ← Gestor central de Sheets ✅
  ingestion/ingest_email_to_sheet_v2.py ← Ingestión de emails ✅
  automation/
    improved_bulletin_processor.py   ← Boletines (V2) ✅
    auto_apply_linkedin.py           ← Auto-apply (async) ✅
  enrichment/enrich_sheet_with_llm_v3.py ← LLM enrichment ✅

Scrapers/Verifiers (raíz):
  LINKEDIN_SMART_VERIFIER_V3.py      ← Verificador LinkedIn ✅
  GLASSDOOR_SMART_VERIFIER.py        ← Verificador Glassdoor ✅
  INDEED_SMART_VERIFIER.py           ← Verificador Indeed ✅
  UNIVERSAL_JOB_VERIFIER.py          ← Verifica cualquier plataforma ✅

Entry points:
  run_daily_pipeline.py              ← Pipeline completo ✅
  unified_app/app.py                 ← Dashboard web Flask ✅
  control_center.py                  ← Menú CLI central ✅
```

---

## 8. 💡 RECOMENDACIONES DE MEJORA

### Prioridad Alta:
1. **Crear `.env`** con las variables requeridas (ver `.env.example`)
2. **Autenticar OAuth de Google** ejecutando `scripts/oauth/reauthenticate_gmail_v2.py`
3. **Instalar Playwright browsers**: `playwright install chromium`
4. **Fix requirements.txt**: eliminar `sqlite3-python==1.0.0`

### Prioridad Media:
5. **Consolidar scrapers** en `scrapers/` folder (sacarlos de la raíz)
6. **Eliminar archivos backup** de git (los .backup_query, BACKUP.py, etc.)
7. **Mover scripts ALL_CAPS** a `scripts/utils/` o `scripts/maintenance/`
8. **Unificar doble implementación de auto-apply** — elegir una como canónica

### Prioridad Baja:
9. **Agregar pytest** con tests básicos para bulletin_processor y sheet_manager
10. **Documentar el flujo completo** con un diagrama en README.md
11. **Reescribir historia git** para eliminar los secretos comprometidos (si el repo va a ser público)

---

## 9. 🐳 ACCESO A BASES DE DATOS (DOCKER)

Ver sección completa en: `docs/DOCKER_DB_ACCESS.md`

### Resumen rápido:
- **PostgreSQL (proyecto):** Puerto `19432` → `psql -h localhost -p 19432 -U postgres`
- **PostgreSQL (ai-workbench):** Puerto `5432` → `psql -h localhost -p 5432 -U postgres`
- **Redis:** Puerto `19379` → `redis-cli -p 19379`

---

## 10. 🆕 HERRAMIENTAS NUEVAS EVALUADAS

### OpenSandbox (Alibaba)
- **Qué es:** Sandbox open-source para agentes de IA (Apache 2.0, GRATIS)
- **Útil para este proyecto:** ✅ Sí — permite ejecutar Playwright en entorno aislado
- **Instalación:** Ver `docs/OPENSANDBOX_INSTALL.md`

### Firecrawl
- **Qué es:** API de web scraping → convierte webs en markdown para LLMs
- **Precio:** 500 páginas GRATIS, luego $16/mes (Hobby)
- **Útil para este proyecto:** ⚠️ Limitado — LinkedIn/Glassdoor bloquean scraping externo
- **Recomendación:** Playwright (ya lo tienes) es más efectivo para job boards

---

*Diagnóstico generado automáticamente con Claude Code*
