# 📖 GUÍA DE USO - PROMPTS PARA NUEVO CHAT

## 🎯 CUÁNDO USAR ESTOS PROMPTS

**Usa el prompt cuando:**
- ✅ El chat actual está al 65-75% de capacidad
- ✅ Claude empieza a "olvidar" contexto
- ✅ Necesitas migrar a nueva sesión
- ✅ Quieres iniciar con contexto completo

**NO uses si:**
- ❌ Chat está al <50% (aún hay espacio)
- ❌ Solo quieres hacer una pregunta rápida

---

## 📋 ARCHIVOS DISPONIBLES

### 1. PROMPT_NUEVO_CHAT.md (COMPLETO)
**Líneas:** 461  
**Tiempo lectura IA:** ~2 minutos  
**Contiene:**
- Contexto completo proyecto
- Estado actual sistema
- Principios de desarrollo
- Bugs resueltos (cómo NO reintroducir)
- Próximos pasos detallados
- Comandos útiles
- Checklist pre-inicio

**Usa cuando:**
- Necesitas contexto COMPLETO
- Primera vez trabajando con IA en proyecto
- Cambio importante de dirección
- Quieres que IA entienda TODO

---

### 2. PROMPT_COMPACTO.md (RÁPIDO)
**Líneas:** 180  
**Tiempo lectura IA:** ~1 minuto  
**Contiene:**
- Resumen ejecutivo
- Componentes clave
- Archivos importantes
- Principios básicos
- Comandos esenciales

**Usa cuando:**
- Necesitas migrar RÁPIDO
- IA ya trabajó en proyecto antes
- Solo continuación de trabajo
- Contexto básico suficiente

---

## 🚀 CÓMO USAR

### PASO 1: Identifica momento de cambio

**Señales de que necesitas cambiar:**
```
- Claude dice "me estoy quedando sin espacio"
- Respuestas más lentas
- "Olvida" cosas recientes
- Token count >130k/190k
```

---

### PASO 2: Elige el prompt apropiado

**PROMPT_NUEVO_CHAT.md si:**
- Primera vez con nueva IA
- Proyecto complejo
- Necesitas contexto profundo
- Tiempo no es crítico

**PROMPT_COMPACTO.md si:**
- Ya trabajaste con IA en proyecto
- Solo continuación
- Necesitas arrancar rápido
- Contexto básico suficiente

---

### PASO 3: Copia el contenido

**Opción A: Manual (recomendado)**
```powershell
# Abrir con editor
notepad PROMPT_NUEVO_CHAT.md
# O
notepad PROMPT_COMPACTO.md

# Copiar TODO el contenido
# Ctrl+A, Ctrl+C
```

**Opción B: Por comandos**
```powershell
Get-Content PROMPT_NUEVO_CHAT.md | Set-Clipboard
# O
Get-Content PROMPT_COMPACTO.md | Set-Clipboard
```

---

### PASO 4: Pega en nuevo chat

1. Abre nuevo chat con Claude
2. Pega TODO el contenido (Ctrl+V)
3. Envía el mensaje
4. **ESPERA** a que Claude confirme que leyó PROJECT_STATUS.md

---

### PASO 5: Verifica comprensión

**Claude debe responder con:**
```
"¡Hola Marcos! He leído todo el contexto del proyecto AI Job Foundry.

Estado actual: Sistema 100% funcional (v2.6) con 426 jobs procesados.

Oportunidad detectada: Tienes 368 jobs de Glassdoor (86% del total) sin auto-apply.

¿Qué prefieres hacer en esta sesión?
A) Glassdoor Auto-Apply...
B) Filtros Gmail...
[etc]"
```

**Si Claude NO menciona:**
- Estado actual del sistema
- Oportunidades detectadas
- Opciones de trabajo

**Entonces:**
1. Pide que lea PROJECT_STATUS.md explícitamente:
   ```
   "Lee primero C:\Users\MSI\Desktop\ai-job-foundry\PROJECT_STATUS.md"
   ```

2. Verifica que entendió el principio de NO romper:
   ```
   "¿Entiendes que NO debes modificar archivos que funcionan sin razón fuerte?"
   ```

---

## ✅ CHECKLIST POST-MIGRACIÓN

Después de migrar al nuevo chat, verifica:

- [ ] Claude leyó PROJECT_STATUS.md
- [ ] Claude entiende estado actual (v2.6, 100% funcional)
- [ ] Claude sabe que 368 jobs Glassdoor esperan
- [ ] Claude conoce principio "NO romper lo que funciona"
- [ ] Claude sabe que debe actualizar PROJECT_STATUS.md
- [ ] Claude ofreció opciones de qué hacer

---

## 🔧 TROUBLESHOOTING

### Problema: Claude no lee PROJECT_STATUS.md

**Solución:**
```
Usuario: "Lee primero el archivo PROJECT_STATUS.md ubicado en 
C:\Users\MSI\Desktop\ai-job-foundry\PROJECT_STATUS.md y dime qué 
versión del sistema tenemos"

Respuesta esperada: "v2.6"
```

---

### Problema: Claude quiere "mejorar" código funcional

**Solución:**
```
Usuario: "DETENTE. El código que quieres modificar funciona al 100%.
Lee la sección '🐛 BUGS RECIENTEMENTE RESUELTOS' del prompt.
¿Por qué es crítico NO tocar [archivo].py sin razón fuerte?"

Claude debe explicar los bugs que ya se resolvieron.
```

---

### Problema: Claude no menciona actualizar PROJECT_STATUS.md

**Solución:**
```
Usuario: "Recuerda que DEBES actualizar PROJECT_STATUS.md al 
finalizar cada iteración con:
- Fecha y hora
- Cambios realizados
- Archivos modificados
- Próximos pasos"
```

---

## 💡 TIPS PRO

### Tip 1: Copia también logs recientes

Si hubo problemas recientes, copia logs:
```powershell
Get-Content logs\powershell\session_*.log | Select-Object -Last 100
```

Pega en chat después del prompt:
```
"Aquí están los últimos logs por si son útiles:
[logs]"
```

---

### Tip 2: Menciona prioridad explícita

Si tienes una prioridad clara:
```
"[Prompt completo]

Mi prioridad para esta sesión es: CREAR GLASSDOOR AUTO-APPLY
Por favor enfócate en esto primero."
```

---

### Tip 3: Prueba con pregunta técnica

Después de pegar prompt, prueba comprensión:
```
"¿Por qué NO debo modificar auto_apply_linkedin.py 
directamente para agregar Glassdoor?"

Respuesta esperada: "Porque acabas de resolver 4 bugs en ese 
archivo. Mejor crear auto_apply_glassdoor.py NUEVO y reutilizar 
código..."
```

---

## 📊 MÉTRICAS DE ÉXITO

**Chat nuevo exitoso si:**
✅ Claude leyó PROJECT_STATUS.md  
✅ Conoce versión actual (2.6)  
✅ Sabe qué NO tocar  
✅ Ofrece opciones relevantes  
✅ Pregunta antes de cambios grandes  
✅ Actualiza PROJECT_STATUS.md al final  

**Chat necesita refuerzo si:**
❌ Quiere "mejorar" código funcional  
❌ No pregunta antes de cambios  
❌ Modifica múltiples archivos sin tests  
❌ Olvida actualizar PROJECT_STATUS.md  

---

## 🎯 RESULTADO ESPERADO

Después de usar el prompt, deberías tener:

1. ✅ IA con contexto completo
2. ✅ IA que respeta código funcional
3. ✅ IA que pregunta antes de cambios
4. ✅ IA que actualiza documentación
5. ✅ Continuidad de trabajo sin pérdida

---

## 📞 AYUDA ADICIONAL

**Si aún tienes dudas:**
1. Lee PROMPT_NUEVO_CHAT.md completo tú mismo
2. Verifica PROJECT_STATUS.md está actualizado
3. Usa PROMPT_COMPACTO.md si prefieres rápido
4. Experimenta con ambos y elige tu preferido

---

**Ubicación archivos:**
```
C:\Users\MSI\Desktop\ai-job-foundry\PROMPT_NUEVO_CHAT.md
C:\Users\MSI\Desktop\ai-job-foundry\PROMPT_COMPACTO.md
C:\Users\MSI\Desktop\ai-job-foundry\PROJECT_STATUS.md
C:\Users\MSI\Desktop\ai-job-foundry\MASTER_FEATURE_ROADMAP.md
```

---

**Fecha creación:** 2025-12-03 00:05 CST  
**Versión:** 1.0  
**Mantenido por:** Marcos Alvarado
