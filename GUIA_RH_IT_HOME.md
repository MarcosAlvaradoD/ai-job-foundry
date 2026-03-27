# ⚡ GUÍA COMPLETA - RH-IT HOME APPLICATION

## 📋 PASO 1: Preparar archivos requeridos

### **1.1 Crear carpeta para CV:**
```powershell
mkdir data\cv
```

### **1.2 Copiar archivos:**
- Copia tu **foto.jpg** a `data\cv\foto.jpg` (opcional)
- Copia tu **CV.pdf** a `data\cv\CV_Marcos_Alvarado.pdf` (**REQUERIDO**)

---

## ⚙️ PASO 2: Configurar datos personales

Abre y edita: `scripts\itc\apply_to_job.py`

**Busca `CV_DATA` y ajusta:**
```python
'fecha_nacimiento': '1985-06-15',  # ← CAMBIA ESTO
'ingreso_actual': '70000',          # ← CAMBIA ESTO
'expectativa_ingreso': '85000',     # ← CAMBIA ESTO
```

**Las demás (email, teléfono) se toman de tu `.env`**

---

## 🧪 PASO 3: Probar con DRY RUN

```powershell
py scripts\itc\apply_to_job.py --job-id 262 --dry-run
```

**Qué hace:**
1. Abre el formulario en navegador VISIBLE
2. Llena TODOS los campos
3. **NO envía la aplicación**
4. Te deja revisar que todo esté correcto

**Si ves errores**, ajusta los datos en `CV_DATA`.

---

## 🚀 PASO 4: Aplicar a vacante #262 (PM Senior)

```powershell
py scripts\itc\apply_to_job.py --job-id 262
```

**Qué hace:**
1. Llena el formulario completo
2. Te pregunta: **"¿Enviar aplicación? (y/n)"**
3. Si dices **y** → ENVÍA la aplicación
4. Si dices **n** → Cancela

---

## 🎯 PASO 5: Aplicar a las mejores 5 vacantes

```powershell
py scripts\itc\apply_to_job.py --job-ids 262,214,218,220,221
```

**Qué hace:**
- Aplica a 5 vacantes consecutivamente
- Delay de 5 segundos entre cada una
- Te pide confirmación ANTES de cada envío

---

## 📊 LAS 11 MEJORES VACANTES (FIT 9/10)

Según análisis de AI:

1. **vacante/262** - Project Manager Senior ⭐⭐⭐ (LA MEJOR)
2. vacante/179
3. vacante/180
4. vacante/196
5. vacante/214
6. vacante/218
7. vacante/219
8. vacante/220
9. vacante/221
10. vacante/223
11. vacante/229

**RECOMENDACIÓN:** Aplica a las primeras 3-5 solamente.

---

## 🔧 TROUBLESHOOTING

### **Error: "CV no encontrado"**
```
❌ CV no encontrado: data/cv/CV_Marcos_Alvarado.pdf
```

**Solución:**
1. Verifica que el archivo existe
2. Si tiene otro nombre, edita `CV_DATA['cv_path']` en el script

### **Error: "Campo no encontrado"**
```
❌ Error: Selector 'input[name="nombre"]' not found
```

**Solución:**
- El formulario de ITC cambió
- Avísame y actualizo el script

### **Error: "Playwright not installed"**
```powershell
pip install playwright --break-system-packages
playwright install chromium
```

---

## 📝 CAMPOS QUE LLENA AUTOMÁTICAMENTE

El script llena **TODO EL FORMULARIO** (30+ campos):

✅ Datos personales (nombre, email, teléfono, fecha nacimiento)
✅ Ubicación (país, estado)
✅ Estudios (grado, área, estatus)
✅ Certificaciones (hasta 2)
✅ Skills primario y secundario
✅ Nivel de inglés
✅ Empresa actual
✅ Tipo de contrato
✅ Ingreso actual y expectativa
✅ Disponibilidad
✅ Reubicación
✅ Archivos (foto y CV)
✅ Aviso de privacidad

**¡NO tienes que llenar NADA manualmente!**

---

## 🎓 TIPS

1. **Usa DRY RUN primero** - Siempre prueba antes de enviar
2. **Revisa el navegador** - Puedes ver exactamente qué hace
3. **Aplica en lotes pequeños** - Máximo 5 vacantes por día
4. **Guarda logs** - El output de PowerShell te muestra qué se llenó

---

## 📞 PRÓXIMOS PASOS

Después de aplicar:

1. ✅ Revisa tu email (confirmaciones)
2. ✅ Anota en Google Sheets (Status: APPLIED)
3. ✅ Prepara para entrevistas con Interview Copilot

---

**Creado:** 2025-12-22  
**Vacantes analizadas:** 91  
**Mejores matches:** 11 (FIT 9/10)  
**Script:** `scripts\itc\apply_to_job.py`
