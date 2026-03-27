# GUIA: USAR CLAUDE CODE PARA AI JOB FOUNDRY

**Fecha:** 2026-03-09 01:35 CST

---

##  CLAUDE CODE ESTA CONFIGURADO

Claude Code en VS Code ya está configurado con Ollama local (qwen2.5:7b).

**Configuración activa:**
- Provider: openai-compatible
- URL: http://127.0.0.1:11434/v1
- Modelo: qwen2.5:7b
- 100% GRATIS, 100% LOCAL

---

##  COMO USAR CLAUDE CODE

### 1. Abrir VS Code en el proyecto

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
code .
```

### 2. Activar Claude Code

- Presiona: **Ctrl+Shift+P**
- Escribe: **Claude Code**
- Selecciona: **Claude Code: Start**

### 3. Dar contexto a Claude Code

En el chat de Claude Code, puedes decir:

```
Lee el archivo CLAUDE.md en la raíz del proyecto para entender el contexto completo.

Necesito que me ayudes a:
[TU TAREA AQUÍ]
```

---

##  TAREAS QUE CLAUDE CODE PUEDE HACER

### Debugging:
```
El pipeline está fallando con este error:
[PEGAR ERROR]

Ayúdame a debuggear y fix
```

### Desarrollo de features:
```
Quiero agregar auto-apply con AI local usando EasyOCR + LM Studio.

Crea el código necesario en:
- core/automation/linkedin_ocr_helper.py
- core/automation/auto_apply_linkedin_ai_local.py
```

### Refactoring:
```
El archivo job_bulletin_processor.py tiene 800 líneas.
Ayúdame a refactorizar en módulos más pequeños.
```

### Code review:
```
Revisa el código de auto_apply_linkedin.py
y dame sugerencias de mejora.
```

---

##  VENTAJAS DE USAR CLAUDE CODE

1. **Ve todo el proyecto** - Tiene acceso completo al código
2. **Puede ejecutar comandos** - Corre tests, scripts, etc.
3. **Crea archivos** - Genera código completo funcional
4. **Lee logs** - Analiza errores automáticamente
5. **100% GRATIS** - Usa Ollama local, sin costos

---

##  ARCHIVOS IMPORTANTES PARA CLAUDE CODE

Cuando uses Claude Code, menciónale estos archivos:

- **CLAUDE.md** - Contexto maestro del proyecto
- **PROJECT_STATUS.md** - Estado actual (progreso, pendientes)
- **MEMORIA_PROYECTO.md** - Memoria compacta
- **PROMPT_NUEVO_CHAT.md** - Para migrar contexto (al 75% capacidad)

---

##  EJEMPLO DE USO

```
USER en Claude Code:
"Lee CLAUDE.md. El pipeline está fallando con error Generic!A1:Z1.
Ayúdame a debuggear y fixear."

CLAUDE CODE:
1. Lee CLAUDE.md (entiende el proyecto)
2. Lee job_bulletin_processor.py (encuentra el bug)
3. Analiza el error (Generic tab no existe)
4. Crea el fix (mapea Generic → LinkedIn)
5. Aplica el cambio
6. Ejecuta test para verificar

OK
```

---

##  CAMBIAR DE MODELO (OPCIONAL)

Si qwen2.5:7b es muy lento o quieres más calidad:

```powershell
# Abrir settings de VS Code
code \C:\Users\MSI\AppData\Roaming\Code\User\settings.json

# Cambiar línea:
\"claude.model\": \"qwen3-coder:latest\"

# Guardar (Ctrl+S) y recargar VS Code (Ctrl+Shift+P → reload window)
```

---

##  PROXIMOS PASOS CON CLAUDE CODE

1. **Abrir VS Code** en el proyecto
2. **Activar Claude Code**
3. **Darle contexto** (CLAUDE.md)
4. **Empezar a trabajar** en features pendientes

---

**Estado:** LISTO PARA USAR
**Siguiente tarea:** Auto-apply con AI local (EasyOCR + LM Studio)

