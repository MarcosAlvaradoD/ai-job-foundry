# 🎯 PREPARACIÓN PARA ENTREVISTA - LUNES 24 NOVIEMBRE

**Status:** LISTO ✅  
**Fecha límite:** Lunes 24 Nov 2025  
**Objetivo:** Interview Copilot completamente funcional con job context

---

## ✅ NUEVAS HERRAMIENTAS CREADAS

### 1. **Interview Copilot V2** 🎤✨
**Archivo:** `core/copilot/interview_copilot_v2.py`  
**Status:** COMPLETO ✅

**Nuevas características:**
- ✅ Job Context Injection - Info de la vacante en el prompt
- ✅ Carga automática desde Google Sheets
- ✅ Ingreso manual de job info
- ✅ Company Research con AI
- ✅ System prompt optimizado con CV + Job + Company

**Cómo usar:**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py core\copilot\interview_copilot_v2.py
```

**Flujo de uso:**
1. Selecciona job desde Google Sheets (FIT >= 7)
2. O ingresa info manualmente
3. Sistema carga: CV + Job Info + Company Context
4. Push-to-talk: Ctrl+Shift+R para grabar
5. 'summary' al final para resumen completo

---

### 2. **LM Studio Internet Test** 🌐
**Archivo:** `test_lm_studio_internet.py`  
**Status:** LISTO PARA EJECUTAR ✅

**Qué hace:**
- Verifica si LM Studio puede acceder a internet
- 5 tests diferentes (precios, noticias, clima, etc.)
- Análisis automático de respuestas
- Reporte detallado en JSON

**Cómo ejecutar:**
```powershell
py test_lm_studio_internet.py
```

**Resultado esperado:**
```
✅ LM STUDIO PARECE TENER ACCESO A INTERNET
O
❌ LM STUDIO NO TIENE ACCESO A INTERNET
   Usa Gemini API como fallback
```

---

### 3. **Dashboard Backend Seguro** 🔒
**Archivo:** `dashboard_backend.py`  
**Status:** COMPLETO ✅

**Por qué era necesario:**
- ❌ Dashboard viejo: API key hardcoded (INSEGURO)
- ✅ Dashboard nuevo: Backend Python que lee del .env (SEGURO)

**Cómo usar:**
```powershell
# Instalar Flask si no lo tienes
pip install flask flask-cors

# Iniciar backend
py dashboard_backend.py

# Abrir en navegador
http://localhost:5000
```

---

## 📋 CHECKLIST PARA EL LUNES 24

### **VIERNES 21 (HOY) - 30 MIN**
```
[ ] 1. Probar LM Studio Internet Access
       py test_lm_studio_internet.py
       
[ ] 2. Revisar resultado
       - Si ✅ Internet: Listo para usar
       - Si ❌ No internet: Configurar Gemini fallback
```

### **SÁBADO 22 - 1 HORA**
```
[ ] 3. Probar Interview Copilot V2
       py core\copilot\interview_copilot_v2.py
       
[ ] 4. Cargar job desde Google Sheets
       - Seleccionar tu entrevista del lunes
       - Verificar que cargue CV + Job Info
       
[ ] 5. Test rápido de push-to-talk
       - Ctrl+Shift+R funciona?
       - Transcripción correcta?
```

### **DOMINGO 23 - 2 HORAS**
```
[ ] 6. Sesión de práctica completa
       - Preguntas behavioral típicas
       - STAR responses con copilot
       - Verificar latencia (< 5s ideal)
       
[ ] 7. Preparar job context manual
       - Si el job no está en Sheets
       - Tener descripción lista
       
[ ] 8. Review company research
       - Verificar AI research de la empresa
       - Agregar notas personales
```

### **LUNES 24 MAÑANA - 30 MIN**
```
[ ] 9. Test final pre-entrevista
       - LM Studio corriendo
       - Copilot cargado con job correcto
       - Audio funcionando
       
[ ] 10. Backup plan ready
        - Gemini API key verificada
        - Notas manuales como respaldo
```

---

## 🚀 COMANDOS RÁPIDOS

### **Test de Internet (30 min)**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py test_lm_studio_internet.py
```

### **Copilot V2 con Job Context (listo para usar)**
```powershell
py core\copilot\interview_copilot_v2.py
```

### **Dashboard Seguro (opcional)**
```powershell
py dashboard_backend.py
# Abre http://localhost:5000
```

---

## 📊 QUÉ ESPERAR EL LUNES 24

### **Durante la entrevista:**

1. **Antes de entrar:**
   - LM Studio corriendo
   - Copilot cargado
   - Job context configurado

2. **Durante preguntas:**
   - Escuchas pregunta
   - Ctrl+Shift+R + habla pregunta
   - Copilot te da STAR response
   - Usas como guía (no leas literal)

3. **System Prompt incluye:**
   ```
   ✅ Tu CV completo
   ✅ Empresa y rol específico
   ✅ FIT Score y por qué
   ✅ Company research
   ✅ Requisitos del job
   ```

4. **Respuestas optimizadas para:**
   - Alinear experiencia con job
   - Mencionar FIT alto
   - Destacar projects relevantes
   - Mostrar interés en empresa

---

## ⚠️ TROUBLESHOOTING

### **LM Studio no responde**
```powershell
# Verificar que está corriendo
http://172.23.0.1:11434/v1/models

# Si falla, reiniciar
.\detect_lm_studio_ip.ps1
```

### **Copilot no transcribe**
```
1. Verificar micrófono (Windows Sound Settings)
2. Run as administrator
3. Reinstalar Whisper: pip install --upgrade openai-whisper
```

### **Job context no carga**
```
1. Verificar Google Sheets connection
2. Usar ingreso manual como backup
3. FIT Score debe ser >= 7 para aparecer en lista
```

---

## 💡 TIPS PARA LA ENTREVISTA

### **Usa el copilot para:**
- ✅ STAR responses rápidas
- ✅ Recordar projects específicos
- ✅ Alinear experiencia con job
- ✅ Data points concretos

### **NO uses el copilot para:**
- ❌ Leer respuestas textualmente
- ❌ Preguntas muy específicas técnicas
- ❌ Small talk inicial

### **Best practices:**
- Escucha completa la pregunta
- Graba solo la pregunta (no tu respuesta)
- Usa respuesta del copilot como OUTLINE
- Agrega tu toque personal
- Mantén naturalidad

---

## 📁 ARCHIVOS CLAVE

```
ai-job-foundry/
├── core/copilot/
│   └── interview_copilot_v2.py       # 🆕 Copilot con job context
├── test_lm_studio_internet.py         # 🆕 Test de internet
├── dashboard_backend.py                # 🆕 Backend seguro
└── web/
    └── dashboard_secure.html           # 🆕 Frontend sin API key
```

---

## 🎯 OBJETIVO FINAL

**LUNES 24 A.M.:**
- ✅ LM Studio online y testeado
- ✅ Copilot cargado con tu job específico
- ✅ Company research completo
- ✅ Audio funcionando perfectamente
- ✅ Backup plan ready

**RESULTADO ESPERADO:**
- Respuestas STAR bien estructuradas
- Referencias específicas a tu experiencia
- Alineación clara con el job
- Confianza al responder
- Interview exitosa 🚀

---

**Tiempo total de prep:** ~4 horas distribuidas en 3 días  
**Status actual:** TODAS LAS HERRAMIENTAS LISTAS ✅  
**Próximo paso:** Ejecutar `py test_lm_studio_internet.py`
