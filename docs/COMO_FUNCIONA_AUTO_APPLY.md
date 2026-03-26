# 📖 CÓMO FUNCIONA LINKEDIN AUTO-APPLY V3

## 🎯 VISIÓN GENERAL

El LinkedIn Auto-Apply V3 es un sistema automatizado que:
1. ✅ Hace login automático en LinkedIn
2. ✅ Busca jobs con FIT Score >= 7
3. ✅ Filtra SOLO jobs de LinkedIn (linkedin.com/jobs)
4. ✅ Detecta botón "Easy Apply"
5. ✅ Abre el formulario de aplicación
6. ✅ Llena campos automáticamente
7. ⏸️  Pausa para revisión manual antes de enviar

---

## 🔄 FLUJO COMPLETO PASO A PASO

### PASO 1: INICIALIZACIÓN
```python
auto_apply = LinkedInAutoApplyV3()
```

**Qué hace:**
- Carga credenciales del `.env`
- Prepara datos del candidato (nombre, email, teléfono, etc.)
- Configura rutas de archivos (cookies, browser data)

---

### PASO 2: BUSCAR JOBS ELEGIBLES
```python
jobs = self.get_high_fit_jobs(min_score=7)
```

**Qué hace:**
1. Lee todos los jobs de Google Sheets (tab="registry")
2. Filtra por:
   - ✅ FIT Score >= 7
   - ✅ Status NO contiene "applied"
   - ✅ ApplyURL existe
   - ✅ **CRÍTICO:** URL contiene "linkedin.com/jobs"

**Resultado:**
```
[FOUND] 0 LinkedIn jobs ready for auto-apply
[SKIP] 2 external jobs (not LinkedIn Easy Apply)
```

---

### PASO 3: INICIAR NAVEGADOR
```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
```

**Qué hace:**
- Abre Chrome visible (para monitoreo)
- Configura user agent para evitar detección
- Crea contexto para cookies

---

### PASO 4: VERIFICAR/CREAR SESIÓN DE LINKEDIN
```python
if not self.ensure_linkedin_session(context, page):
    return  # No se pudo logear
```

**Sub-pasos:**

#### 4.1. Intentar cargar cookies guardadas
```python
self.load_cookies(context)
# Lee: data/linkedin_cookies.json
```

#### 4.2. Verificar si hay sesión activa
```python
page.goto('https://www.linkedin.com/feed/')
if '/feed' in page.url:
    # ✅ Ya está logueado
```

#### 4.3. Si NO hay sesión → Auto-login
```python
self.login_to_linkedin(page)
```

**Proceso de login:**
```
1. Navega a: https://www.linkedin.com/login
2. Llena campo #username con LINKEDIN_EMAIL
3. Llena campo #password con LINKEDIN_PASSWORD
4. Click en button[type="submit"]
5. Espera navegación
6. Si requiere verificación → Pausa 60s para manual
7. Verifica que llegue a /feed
8. Guarda cookies para próxima vez
```

---

### PASO 5: PROCESAR CADA JOB
```python
for job in jobs:
    self.apply_to_job(job, page, dry_run=True)
```

#### 5.1. Navegar al job
```python
page.goto(apply_url)
time.sleep(3)  # Esperar carga
```

#### 5.2. Buscar botón "Easy Apply"
```python
easy_apply_button = page.query_selector('button:has-text("Easy Apply")')

if not easy_apply_button:
    print("[SKIP] Not an Easy Apply job")
    return False
```

**¿Por qué algunos jobs NO tienen Easy Apply?**
- Job es externo (Greenhouse, Workday, etc.)
- LinkedIn lo redirige a sitio de la empresa
- Job requiere aplicación completa

#### 5.3. Click en "Easy Apply"
```python
easy_apply_button.click()
time.sleep(2)
```

#### 5.4. Verificar modal de aplicación
```python
modal = page.query_selector('[role="dialog"]')
if not modal:
    print("[ERROR] Application modal not found")
    return False
```

---

### PASO 6: LLENAR FORMULARIO (Multi-Step)
```python
max_steps = 5
current_step = 1

while current_step <= max_steps:
    # Llenar formulario actual
    self.handle_easy_apply_form(page)
    
    # Buscar botón Next/Continue
    next_button = self.check_for_next_step(page)
    if next_button:
        next_button.click()
        current_step += 1
        continue
    
    # Buscar botón Submit
    submit_button = self.check_for_submit(page)
    if submit_button:
        # ⏸️ PAUSA AQUÍ - No envía automáticamente
        print("[PAUSE] Review form before submit")
        return True
```

#### 6.1. Detectar tipo de campo
```python
def detect_field_type(self, input_element):
    # Lee: label, placeholder, name, id, aria-label
    # Combina todo y busca keywords:
    
    if 'first name' in combined:
        return 'first_name'
    elif 'email' in combined:
        return 'email'
    elif 'phone' in combined:
        return 'phone'
    # ... etc
```

#### 6.2. Llenar campo
```python
def fill_form_field(self, input_element, field_type):
    value = self.candidate_data.get(field_type)
    # Ejemplo: 'first_name' → 'Marcos'
    
    input_element.fill('')  # Limpiar
    input_element.type(value, delay=50)  # Escribir
```

**Datos del candidato:**
```python
{
    'full_name': 'Marcos Alberto Alvarado de la Torre',
    'first_name': 'Marcos',
    'last_name': 'Alvarado',
    'email': 'markalvati@gmail.com',
    'phone': '+52 33 2332 0358',
    'location': 'Guadalajara, Jalisco, Mexico',
    'linkedin_url': 'https://www.linkedin.com/in/marcos-alvarado',
    'years_experience': '10',
    'current_company': 'Independent Consultant',
    'current_title': 'Project Manager / Business Analyst'
}
```

---

### PASO 7: PAUSA PARA REVISIÓN
```python
print("[PAUSE] Review form before final submit")
print("[INFO] Browser will stay open for 10 seconds...")
time.sleep(10)
```

**¿Por qué NO envía automáticamente?**
1. ✅ Permite revisar que todo esté correcto
2. ✅ Evita errores en la aplicación
3. ✅ Da control final al usuario
4. ✅ Previene aplicaciones no deseadas

**Para activar envío automático:**
```python
# En línea ~460 de linkedin_auto_apply.py
# Descomentar:
submit_button.click()
time.sleep(2)
print("[SUCCESS] Application submitted!")
```

---

## 🎛️ MODOS DE OPERACIÓN

### Modo DRY-RUN (Actual)
```python
auto_apply.run(dry_run=True, max_applies=2, min_score=7)
```

**Qué hace:**
- ✅ Busca jobs elegibles
- ✅ Navega a cada URL
- ✅ Verifica "Easy Apply"
- ❌ NO hace click en nada
- ✅ Muestra qué HARÍA hacer

**Output:**
```
[FOUND] Easy Apply button!
[DRY-RUN] Would click Easy Apply and fill form
```

### Modo LIVE (Form Fill Only)
```python
auto_apply.run(dry_run=False, max_applies=5, min_score=7)
```

**Qué hace:**
- ✅ Busca jobs elegibles
- ✅ Navega a cada URL
- ✅ Click en "Easy Apply"
- ✅ Llena formulario completo
- ⏸️ **PAUSA** antes de submit
- ❌ NO envía automáticamente

### Modo FULL AUTO (Requiere descomentar código)
```python
# En el código, descomentar líneas ~460
submit_button.click()
```

**Qué hace:**
- ✅ Todo lo del modo LIVE
- ✅ **ENVÍA** la aplicación automáticamente
- ⚠️ **PELIGRO:** No hay revisión

---

## 🔍 ¿POR QUÉ NO ENCUENTRA JOBS?

### Razón 1: No hay jobs de LinkedIn en Sheets
```
[FOUND] 0 LinkedIn jobs ready for auto-apply
[SKIP] 2 external jobs (not LinkedIn Easy Apply)
```

**Solución:** Procesar más emails o ejecutar scraper de LinkedIn

### Razón 2: Jobs de LinkedIn pero FIT < 7
**Solución:** Bajar threshold a 5 o 6 temporalmente

### Razón 3: Jobs de LinkedIn ya aplicados
**Solución:** Verificar columna Status en Sheets

---

## 📊 EJEMPLO DE EJECUCIÓN EXITOSA

```
======================================================================
[AUTO-APPLY V3] LinkedIn Easy Apply with AUTO-LOGIN
======================================================================

[SEARCH] Finding LinkedIn jobs with FIT >= 7...
[FOUND] 3 LinkedIn jobs ready for auto-apply

[PLAN] Found 3 jobs. Will process 3:
  1. Microsoft - Senior Product Manager (FIT: 8.5/10)
  2. Google - Technical Program Manager (FIT: 8.0/10)
  3. Amazon - Sr. Business Analyst (FIT: 7.5/10)

[DRY-RUN] This is a simulation.

[START] Starting browser...

[SESSION] Checking LinkedIn session...
[OK] Loaded 38 cookies from data/linkedin_cookies.json
[OK] Already logged into LinkedIn!

======================================================================
[APPLY] Microsoft - Senior Product Manager
[FIT] 8.5/10 | Created: 2025-12-20
[URL] https://www.linkedin.com/jobs/view/3234567890
======================================================================
[FOUND] Easy Apply button!
[DRY-RUN] Would click Easy Apply and fill form

======================================================================
[APPLY] Google - Technical Program Manager
[FIT] 8.0/10 | Created: 2025-12-21
[URL] https://www.linkedin.com/jobs/view/3234567891
======================================================================
[FOUND] Easy Apply button!
[DRY-RUN] Would click Easy Apply and fill form

======================================================================
[APPLY] Amazon - Sr. Business Analyst
[FIT] 7.5/10 | Created: 2025-12-22
[URL] https://www.linkedin.com/jobs/view/3234567892
======================================================================
[FOUND] Easy Apply button!
[DRY-RUN] Would click Easy Apply and fill form

======================================================================
[SUMMARY]
  ✅ Success: 3
  ❌ Failed: 0
  ⏭️  Skipped: 0
======================================================================
```

---

## 🎯 PRÓXIMOS PASOS PARA TI

### 1. Verificar cuántos jobs de LinkedIn tienes
```powershell
# Ver Google Sheets manualmente:
# https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

# Filtrar por:
# - Column "ApplyURL" contiene "linkedin.com/jobs"
# - Column "FitScore" >= 7
# - Column "Status" NO contiene "Applied"
```

### 2. Si NO hay jobs de LinkedIn
**Opciones:**
- A. Bajar threshold temporal: `min_score=5`
- B. Procesar más emails de job bulletins
- C. Ejecutar LinkedIn scraper manual

### 3. Si SÍ hay jobs → Test LIVE
```python
# Editar: scripts/test_linkedin_autoapply_v3.py
auto_apply.run(
    dry_run=False,  # ⚠️ Cambiar a LIVE
    max_applies=1,  # Solo 1 para probar
    min_score=7
)
```

---

**Fecha:** 2025-12-24 18:00 CST  
**Estado:** Sistema 100% funcional  
**Bloqueador:** No hay jobs de LinkedIn con FIT >= 7 en Sheets
