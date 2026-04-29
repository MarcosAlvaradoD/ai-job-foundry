# 🔧 ERRORES CORREGIDOS - WEB APP

**Fecha:** 2025-11-29  
**Versión:** 2.3 (Web App Fixed)

---

## ❌ PROBLEMAS ENCONTRADOS

### 1. Dashboard Mostraba Todos 0
**Síntoma:**
- Total Jobs: 0
- High Fit (7+): 0
- Applied: 0
- Pending: 0
- Gráfico vacío

**Causa:**
FIT score parsing incorrecto. El código esperaba números enteros pero los sheets tienen strings `"8/10"`.

**Fix:**
```python
# ANTES (MALO)
fit = int(j.get('FitScore', 0))  # Falla con "8/10"

# DESPUÉS (CORRECTO)
fit_str = str(j.get('FitScore', '0'))
fit = int(fit_str.split('/')[0] if '/' in fit_str else fit_str)
```

---

### 2. Todos los Botones → ERROR: undefined

**Síntomas:**
- Process Emails → undefined
- AI Analysis → undefined
- Auto-Apply → undefined
- (Todos menos Verify URLs)

**Causa:**
Rutas de scripts incorrectas. Los subprocesses intentaban ejecutar archivos que:
1. No existían
2. Tenían paths incorrectos

**Ejemplos de rutas MALAS:**
```python
# ❌ NO EXISTE
'run_daily_pipeline.py'
'process_bulletins.py'
'scripts/test_ai_workbenches.py'
'verify_job_status.py'
'run_auto_apply.py'
```

**Fix - Rutas CORRECTAS:**
```python
# ✅ EXISTEN
'core/ingestion/ingest_email_to_sheet_v2.py'
'core/automation/job_bulletin_processor.py'
'core/enrichment/enrich_sheet_with_llm_v3.py'
'core/jobs_pipeline/job_cleaner.py'
'core/automation/linkedin_auto_apply.py'
```

---

### 3. SheetManager Import Error

**Síntoma:**
```
ModuleNotFoundError: No module named 'core.sheets.sheet_manager'
```

**Causa:**
Path import incorrecto en app.py

**Fix:**
```python
# Añadir al inicio de app.py
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

## ✅ SOLUCIONES IMPLEMENTADAS

### unified_app/app.py (Reescrito - 293 líneas)

**Cambios Principales:**

1. **run_script() helper**
```python
def run_script(script_path, timeout=120, cwd=None):
    """Helper con manejo de errores correcto"""
    try:
        result = subprocess.run(
            ['py', script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or Path(__file__).parent.parent
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': f'Timeout ({timeout}s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

2. **FIT Score Parsing Correcto**
```python
# Parsea "8/10" → 8
fit_str = str(j.get('FitScore', '0'))
fit = int(fit_str.split('/')[0] if '/' in fit_str else fit_str)
```

3. **Status Detection Mejorado**
```python
# Detecta múltiples variantes
applied = len([
    j for j in jobs 
    if 'applied' in str(j.get('Status', '')).lower() 
    or 'application submitted' in str(j.get('Status', '')).lower()
])
```

---

## 📊 MAPEO CORRECTO DE FUNCIONES

| Botón | Script CORRECTO |
|-------|-----------------|
| Process Emails | `core/ingestion/ingest_email_to_sheet_v2.py` |
| Process Bulletins | `core/automation/job_bulletin_processor.py` |
| AI Analysis | `core/enrichment/enrich_sheet_with_llm_v3.py` |
| Check Expired | `core/jobs_pipeline/job_cleaner.py` |
| Verify URLs | `check_urls_status.py` |
| Generate Report | `core/jobs_pipeline/sheet_summary.py` |
| LinkedIn Scraper | `scripts/visual_test.py` |
| Indeed Scraper | DISABLED (timeout issues) |
| Auto-Apply DRY | `core/automation/linkedin_auto_apply.py` |
| Auto-Apply LIVE | DISABLED (safety) |
| Dashboard | Already open |
| Google Sheets | Opens in browser |
| Health Check | `core/jobs_pipeline/system_health_check.py` |
| View Data | SheetManager direct |
| Refresh OAuth | `fix_oauth_complete.py` |

---

## 🚀 CÓMO PROBAR

```powershell
# 1. Detener app vieja (Ctrl+C si está corriendo)

# 2. Iniciar app corregida
cd C:\Users\MSI\Desktop\ai-job-foundry
.\START_UNIFIED_APP.bat

# 3. Verificar en navegador
http://localhost:5555
```

**Resultados esperados:**
- ✅ Dashboard carga con números reales
- ✅ FIT Score Distribution muestra gráfico
- ✅ Todos los botones responden (no "undefined")
- ✅ Sistema muestra OAuth/LM Studio/Sheets status

---

## 🐛 DEBUGGING

### Si Dashboard sigue en 0:

1. **Verificar OAuth:**
```powershell
py check_oauth_token.py
```

2. **Verificar Google Sheets tiene datos:**
```powershell
py view_current_sheets.py
```

3. **Ver logs de Flask:**
Mira la consola donde corre `START_UNIFIED_APP.bat`

### Si botones fallan:

1. **Check script existe:**
```powershell
ls core/ingestion/ingest_email_to_sheet_v2.py
```

2. **Ejecutar script directo:**
```powershell
py core/ingestion/ingest_email_to_sheet_v2.py
```

3. **Ver error completo:**
Click botón → mira Console Output en web app

---

## 📈 MEJORAS ADICIONALES

### Todavía Pendientes:

1. **Indeed Scraper** - Timeout issues
   - Solución temporal: Use Gmail processing
   
2. **Auto-Apply LIVE** - Disabled for safety
   - Solución: Probar DRY RUN primero

3. **Dashboard Keywords** - Resumen tab
   - Solución: Crear script filtrado (pendiente)

---

## 📚 ARCHIVOS MODIFICADOS

1. `unified_app/app.py` (293 líneas) - REESCRITO
2. `WEB_APP_ERRORS_FIXED.md` (este archivo)

---

**Autor:** Marcos + Claude  
**Fecha:** 2025-11-29  
**Versión:** 2.3 (Web App Fixed)
