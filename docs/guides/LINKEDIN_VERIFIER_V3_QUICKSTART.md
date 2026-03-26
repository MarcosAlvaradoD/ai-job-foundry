# 🔍 LINKEDIN SMART VERIFIER V3 - QUICK START

## 🆕 NOVEDADES EN V3

### 1. **Sin bloqueos `input()`**
- ❌ **Antes (V2):** Se quedaba esperando "Press Enter..." al detectar checkpoint
- ✅ **Ahora (V3):** Da 30 segundos automáticos, luego continúa

### 2. **Cookies persistentes** 🍪
- ❌ **Antes:** Login en CADA ejecución
- ✅ **Ahora:** Login UNA vez, guarda cookies en `data/linkedin_cookies.json`
- 📝 Siguiente ejecución reutiliza sesión (no login necesario)

### 3. **Más patrones de detección** 🔍
- ✅ 16 patrones de EXPIRED (inglés + español)
- ✅ 16 patrones de ACTIVE (inglés + español)
- ✅ Detección mejorada de errores 404/403

### 4. **Mejor manejo de checkpoints** ⏱️
- Si LinkedIn pide verificación:
  - Muestra mensaje "⚠️ CHECKPOINT DETECTED!"
  - Da 30 segundos para resolverlo MANUALMENTE en el navegador
  - Revisa cada 5 segundos si fue resuelto
  - Continúa automáticamente (no bloquea el pipeline)

---

## 🚀 USO RÁPIDO

### Primera ejecución (con login manual)
```powershell
py LINKEDIN_SMART_VERIFIER_V3.py --limit 3
```

**¿Qué pasará?**
1. Se abre Firefox (visible)
2. Hace login automático con tus credenciales del `.env`
3. **SI HAY CHECKPOINT:**
   - Mensaje: "⚠️ CHECKPOINT DETECTED!"
   - Tienes 30 segundos para resolverlo en la ventana de Firefox
   - Completa el CAPTCHA, verificación de email, etc.
4. Guarda cookies en `data/linkedin_cookies.json`
5. Verifica los 3 primeros jobs

### Ejecuciones siguientes (sin login)
```powershell
py LINKEDIN_SMART_VERIFIER_V3.py --limit 5
```

**¿Qué pasará?**
1. Se abre Firefox
2. **Carga cookies guardadas** (no hace login)
3. Verifica que la sesión esté activa
4. Si está activa: ✅ "Session is still VALID!"
5. Si expiró: 🔄 Hace login de nuevo

---

## 📊 EJEMPLO DE SALIDA

### Con sesión válida (cookies funcionando)
```
🔍 LINKEDIN SMART VERIFIER V3
======================================================================
Timestamp: 2025-12-06 21:30:00
Mark as EXPIRED: YES
======================================================================

📋 Fetching jobs from LinkedIn tab...
✅ Found 5 jobs to verify

======================================================================
🌐 Starting browser with cookies...
======================================================================

  ✅ Loaded 15 cookies from linkedin_cookies.json
  ℹ️  Testing saved session...
  ✅ Session is still VALID! No need to login again.

[1/5] Checking: Google - Software Engineer...
  ✅ ACTIVE: Found: "easy apply"
  
[2/5] Checking: Meta - Data Scientist...
  ❌ EXPIRED: Found: "no longer accepting applications"
  📝 Marked as EXPIRED in sheet
```

### Con checkpoint (primera vez)
```
======================================================================
🌐 Starting browser with cookies...
======================================================================

  ℹ️  No saved cookies found, will need to login

🔐 Attempting LinkedIn login...
  📤 Login form submitted, waiting for response...
  ⚠️  CHECKPOINT DETECTED!
  ⏱️  Giving you 30 seconds to solve it VISUALLY in the browser...
  ⏱️  (Look at the Firefox window and complete the challenge)
  ⏱️  30 seconds remaining...
  ⏱️  25 seconds remaining...
  ⏱️  20 seconds remaining...
  ✅ Checkpoint SOLVED! Login successful!
  💾 Cookies saved to linkedin_cookies.json

[1/5] Checking: Google - Software Engineer...
  ✅ ACTIVE: Found: "apply now"
```

---

## 🔧 COMANDOS DISPONIBLES

### Verificar todos los jobs
```powershell
py LINKEDIN_SMART_VERIFIER_V3.py
```

### Verificar solo los primeros N jobs
```powershell
py LINKEDIN_SMART_VERIFIER_V3.py --limit 10
```

### Ver resultados sin marcar en Google Sheets (report only)
```powershell
py LINKEDIN_SMART_VERIFIER_V3.py --no-mark
```

### Desde el pipeline completo
```powershell
py run_daily_pipeline.py --expire
```
- Ahora usa automáticamente V3 (sin bloqueos)

---

## 🐛 DEBUGGING CUANDO SALEN MUCHOS "UNKNOWN"

Si muchos jobs salen como UNKNOWN, significa que los patrones no los detectan.

### Paso 1: Activar modo debug
Edita `LINKEDIN_SMART_VERIFIER_V3.py`, línea ~295:
```python
debug_mode = True  # Cambiar de False a True
```

### Paso 2: Ejecuta de nuevo
```powershell
py LINKEDIN_SMART_VERIFIER_V3.py --limit 3
```

### Paso 3: Revisa los HTMLs guardados
```
logs/linkedin_debug_1733533200.html
logs/linkedin_debug_1733533210.html
logs/linkedin_debug_1733533220.html
```

### Paso 4: Busca patrones
Abre los HTMLs y busca palabras que indiquen:
- **Job expirado:** "no longer", "expired", "removed", "filled"
- **Job activo:** "apply", "submit", "easy apply", "be an early applicant"

### Paso 5: Agrega nuevos patrones
Edita `LINKEDIN_SMART_VERIFIER_V3.py`, líneas 36-70, agrega los nuevos textos.

---

## ⚙️ ARCHIVOS IMPORTANTES

### Cookies guardadas
```
data/linkedin_cookies.json
```
- Se crea automáticamente después del primer login exitoso
- Si hay problemas de sesión, puedes borrarlo para forzar nuevo login

### HTMLs de debugging
```
logs/linkedin_debug_*.html
```
- Se crean cuando `debug_mode = True`
- Útiles para encontrar nuevos patrones

---

## ❓ FAQ

### ¿Por qué sale "CHECKPOINT DETECTED"?
LinkedIn detectó login automatizado y pide verificación (CAPTCHA, email, etc.)

**Solución:** 
- Completa la verificación en los 30 segundos
- LinkedIn guardará la sesión y no volverá a pedir checkpoint

### ¿Cookies no funcionan?
Si siempre hace login aunque exista el archivo `cookies.json`:

**Solución:**
1. Borra `data/linkedin_cookies.json`
2. Ejecuta de nuevo
3. Completa el checkpoint si aparece
4. Cookies nuevas se guardarán

### ¿Muchos jobs salen UNKNOWN?
Significa que los patrones no detectan el estado del job.

**Soluciones:**
1. Verifica que el login fue exitoso
2. Activa modo debug (ver sección arriba)
3. Revisa los HTMLs y encuentra nuevos patrones
4. Agrégalos al código

### ¿Quiero ejecutarlo en headless (sin ventana)?
Edita `LINKEDIN_SMART_VERIFIER_V3.py`, línea ~252:
```python
browser = p.firefox.launch(headless=True)  # Cambiar a True
```

⚠️ **IMPORTANTE:** Si hay checkpoint, no podrás resolverlo visualmente.

---

## 🎯 RESUMEN

### Primera vez
1. Ejecuta: `py LINKEDIN_SMART_VERIFIER_V3.py --limit 3`
2. Se abre Firefox (visible)
3. Hace login automático
4. SI HAY CHECKPOINT → Resuélvelo en 30 segundos
5. Guarda cookies ✅

### Siguientes veces
1. Ejecuta: `py LINKEDIN_SMART_VERIFIER_V3.py`
2. Usa cookies guardadas (sin login) ✅
3. Verifica todos los jobs
4. Marca EXPIRED en Google Sheets ✅

### Desde pipeline
1. Ejecuta: `py run_daily_pipeline.py --expire`
2. Borra EXPIRED anteriores ✅
3. Verifica Glassdoor + LinkedIn (V3) + Indeed ✅
4. Marca nuevos EXPIRED ✅

---

**🎉 ¡Listo! LinkedIn V3 está configurado y funcionando.**
