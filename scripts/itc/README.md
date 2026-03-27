# 🎯 RH-IT HOME - AUTO-APPLY FINAL

## ✅ ESTADO: **98% AUTOMÁTICO**

El script llena **TODO EL FORMULARIO** automáticamente excepto:
- ⏸️ **Checkbox de privacidad** (debes marcarlo manualmente - 1 click)

---

## 🚀 USO RÁPIDO

### **1. Aplicar a UNA vacante:**
```powershell
py scripts\itc\apply_final.py --job-id 262
```

### **2. Aplicar a MÚLTIPLES vacantes:**
```powershell
py scripts\itc\apply_final.py --job-ids 262,214,218,220,221
```

### **3. DRY RUN (prueba sin enviar):**
```powershell
py scripts\itc\apply_final.py --job-id 262 --dry-run
```

---

## 📋 FLUJO DE TRABAJO

### **AUTOMÁTICO (98%):**
1. ✅ Abre formulario en navegador
2. ✅ Llena todos los campos (30+)
3. ✅ Sube foto y CV
4. ⏸️ **PAUSA** - Te avisa que marques el checkbox
5. ⏸️ Esperas a que marques (1 click)
6. ⏸️ Presionas Enter
7. ✅ Te pregunta: "¿Enviar? (y/n)"
8. ✅ Si dices 'y' → ENVÍA automáticamente
9. ✅ Espera confirmación
10. ✅ Continúa con siguiente vacante (si hay más)

---

## 🎯 LAS 11 MEJORES VACANTES (FIT 9/10)

Según análisis de IA:

```powershell
# Las 5 MEJORES:
py scripts\itc\apply_final.py --job-ids 262,214,218,220,221

# Todas las FIT 9/10:
py scripts\itc\apply_final.py --job-ids 262,179,180,196,214,218,219,220,221,223,229
```

---

## ⚙️ CONFIGURACIÓN

**Edita `apply_final.py` si necesitas cambiar:**

```python
# Línea 21 - Tu fecha de nacimiento
'fecha_nacimiento': '1985-02-07',  # YYYY-MM-DD

# Líneas 64-68 - Salarios
'ingreso_actual': '65000',
'expectativa_ingreso': '75000',

# Líneas 77-78 - Rutas de archivos
'foto_path': r'data\cv\Foto.jpg',
'cv_path': r'data\cv\Alvarado Marcos.pdf'
```

**Lo demás se toma de tu `.env`:**
- `USER_EMAIL` = markalvati@gmail.com
- `USER_PHONE` = +523323320358

---

## 📊 QUÉ LLENA AUTOMÁTICAMENTE

✅ **30+ CAMPOS:**
- Nombre, apellidos, email, teléfono
- Fecha de nacimiento
- Red social (LinkedIn)
- País y estado (México, Jalisco)
- Grado de estudios (Licenciatura - Informática)
- Certificaciones (2): Lean Six Sigma, Scrum Master
- Skills primario y secundario (Project Manager, Manager)
- Experiencia (EXPERT +9 años)
- Nivel de inglés (Avanzado)
- Empresa actual
- Tipo de contrato
- Prestaciones
- Ingreso actual y expectativa
- Disponibilidad (Inmediata)
- Reubicación (No)
- Foto y CV

**Solo debes marcar:** ☑️ Checkbox de privacidad (1 click)

---

## 💡 TIPS

### **Para aplicación masiva:**
1. Usa `--job-ids` con las 5 mejores primero
2. El script espera 10 segundos entre cada vacante
3. Puedes cancelar con `Ctrl+C` en cualquier momento
4. Cada vacante toma ~2-3 minutos (con el checkbox manual)

### **Si algo falla:**
- El navegador queda ABIERTO para que veas qué pasó
- Puedes completar/enviar manualmente
- Luego presiona Enter en PowerShell para continuar

---

## 🎬 EJEMPLO DE SESIÓN

```
🎯 APLICANDO A VACANTE 262
🌐 Abriendo formulario...

📝 DATOS GENERALES
  ✅ Nombre: Marcos Alberto
  ✅ Apellidos: Alvarado de la Torre
  ✅ Email: markalvati@gmail.com
  [... 30+ campos más ...]

✅ FORMULARIO COMPLETADO (99%)

📋 ACCIÓN REQUERIDA:
   1. Busca el checkbox 'Aviso de Privacidad'
   2. MÁRCALO (1 click)
   3. Presiona Enter aquí

⏸️  Presiona Enter cuando HAYAS MARCADO el checkbox...
[TÚ MARCAS EL CHECKBOX Y PRESIONAS ENTER]

📤 ¿ENVIAR APLICACIÓN?
Vacante: 262
Escribe 'y' para ENVIAR: y

📤 Enviando aplicación...
   ✅ Click en 'Enviar' ejecutado
   ✅ ¡APLICACIÓN ENVIADA EXITOSAMENTE!

✅ PROCESO COMPLETADO

[Si hay más vacantes, espera 10 segundos y continúa...]
```

---

## ⚠️ TROUBLESHOOTING

### **"Error: CV no encontrado"**
- Verifica: `data\cv\Alvarado Marcos.pdf` existe
- Ajusta la ruta en línea 78 si el nombre es diferente

### **"No se pudo seleccionar [campo]"**
- Algunos dropdowns tienen valores específicos
- El script ya tiene los correctos, pero si cambian, avísame

### **"Checkbox de privacidad - márcalo manualmente"**
- **ESTO ES NORMAL** - no es un error
- Solo marca el checkbox al final del formulario
- Presiona Enter

---

## 📈 RENDIMIENTO

**Por vacante:**
- ⏱️ Tiempo: ~2-3 minutos
- 🤖 Automático: 98%
- 👤 Manual: 2% (1 checkbox)

**Para 5 vacantes:**
- ⏱️ Tiempo total: ~15-20 minutos
- ✅ Todo en una sesión

**Para 11 vacantes:**
- ⏱️ Tiempo total: ~30-40 minutos
- ✅ Recomendado: Hazlo en 2 sesiones (5 + 6)

---

## 🏆 ÉXITO GARANTIZADO

**Este script es la MEJOR forma de aplicar a ITC porque:**
1. ✅ Llena TODO perfectamente
2. ✅ No comete errores de tipeo
3. ✅ Es consistente en todas las aplicaciones
4. ✅ Es rápido (2-3 min vs 15 min manual)
5. ✅ Te deja revisar antes de enviar

---

**Creado:** 2025-12-22  
**Versión:** FINAL v1.0  
**Funcionalidad:** 98% automático  
**Vacantes analizadas:** 91  
**Mejores matches:** 11 (FIT 9/10)
