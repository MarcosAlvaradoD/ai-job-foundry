# 🚀 QUICK START - ENTREVISTA LUNES 24

**TIEMPO TOTAL:** 30 minutos de setup hoy  
**OBJETIVO:** Todo listo para el lunes

---

## ✅ PASO 1: TEST DE INTERNET LM STUDIO (5 MIN)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py test_lm_studio_internet.py
```

**Resultado esperado:**
```
✅ LM STUDIO PARECE TENER ACCESO A INTERNET
```

**Si sale ❌:**
- No problem - Gemini API será el fallback
- Copilot funcionará igual

---

## ✅ PASO 2: INSTALAR DEPENDENCIAS (5 MIN)

```powershell
# Flask para dashboard
pip install flask flask-cors

# Whisper ya debería estar, pero por si acaso
pip install --upgrade openai-whisper
```

---

## ✅ PASO 3: PROBAR COPILOT V2 (10 MIN)

```powershell
py core\copilot\interview_copilot_v2.py
```

**Qué hacer:**
1. Selecciona opción "1" (cargar desde Sheets)
2. Si ves lista de jobs → Selecciona cualquiera para probar
3. Si no hay jobs → Selecciona "2" (ingreso manual)
4. Verifica que cargue CV + Job Info
5. Presiona Enter para iniciar
6. Ctrl+C para salir (por ahora solo probamos que carga)

**¿Qué pasa si falla?**
- Si dice "ModuleNotFoundError: keyboard"
  ```powershell
  pip install keyboard
  ```
- Si dice "ModuleNotFoundError: pyaudio"
  ```powershell
  pip install pyaudio
  ```

---

## ✅ PASO 4: DASHBOARD SEGURO (5 MIN) - OPCIONAL

```powershell
py dashboard_backend.py
```

Abre navegador: http://localhost:5000

**¿Para qué sirve?**
- Ver jobs con FIT scores
- Identificar cuál job cargar para la entrevista
- Monitorear tus aplicaciones

---

## ✅ PASO 5: VERIFICAR QUE TODO ESTÁ OK (5 MIN)

**Checklist rápido:**
```
[ ] LM Studio corriendo (http://172.23.0.1:11434)
[ ] Test de internet ejecutado
[ ] Copilot V2 carga sin errores
[ ] CV cargado correctamente
[ ] Job context funciona
```

---

## 🎯 PARA EL LUNES 24

### **ANTES DE LA ENTREVISTA (15 min antes):**

1. **Iniciar LM Studio**
   - Abrir aplicación
   - Verificar que responda

2. **Cargar Copilot con JOB REAL**
   ```powershell
   py core\copilot\interview_copilot_v2.py
   ```
   - Seleccionar el job de la entrevista
   - Verificar que cargue toda la info
   - Dejar corriendo

3. **Test rápido de audio**
   - Ctrl+Shift+R
   - Hablar algo
   - Ver si transcribe

### **DURANTE LA ENTREVISTA:**

1. **Escuchar pregunta completa**
2. **Ctrl+Shift+R + repetir pregunta en voz baja**
3. **Leer respuesta del copilot (mental)**
4. **Responder con tus palabras**
5. **NO leer textualmente**

---

## ⚠️ TROUBLESHOOTING RÁPIDO

### **"LM Studio no responde"**
```powershell
.\detect_lm_studio_ip.ps1
```

### **"Copilot no transcribe"**
- Run PowerShell como Administrator
- Verificar micrófono en Windows Sound Settings

### **"No encuentra job en Sheets"**
- Usar ingreso manual (opción 2)
- Copiar descripción del email/LinkedIn

---

## 📋 BACKUP PLAN

Si algo falla el lunes:
1. ✅ Ten notas escritas con STAR responses preparadas
2. ✅ Gemini fallback está configurado
3. ✅ CV impreso/digital a la mano

---

## 💡 TIP FINAL

**El copilot es una GUÍA, no un teleprompter.**

Úsalo para:
- ✅ Recordar projects específicos
- ✅ Estructurar STAR responses
- ✅ Data points concretos

NO lo uses para:
- ❌ Leer respuestas palabra por palabra
- ❌ Reemplazar tu personalidad
- ❌ Small talk

---

## 🚀 EJECUTA ESTO AHORA:

```powershell
# 1. Test internet (5 min)
py test_lm_studio_internet.py

# 2. Probar copilot (10 min)
py core\copilot\interview_copilot_v2.py

# 3. LISTO! ✅
```

**Tiempo total:** 15 minutos  
**Resultado:** Interview Copilot V2 listo para el lunes 🎯

---

**¿Dudas? Todo está documentado en:**
- `docs/PREP_ENTREVISTA_24NOV.md` - Guía completa
- `docs/PROJECT_STATUS.md` - Estado del proyecto
