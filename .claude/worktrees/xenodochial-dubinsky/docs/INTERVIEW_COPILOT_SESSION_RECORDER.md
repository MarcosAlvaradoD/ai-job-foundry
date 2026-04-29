# 🎤 INTERVIEW COPILOT - SESSION RECORDER

## 🎯 QUÉ ES ESTO

Sistema completo para grabar y documentar entrevistas técnicas con:

✅ **Push-to-Talk** - Mantén Ctrl+Shift+R presionado para grabar
✅ **Grabación continua** - Graba mientras mantienes la tecla
✅ **Transcripción automática** - Whisper convierte audio a texto
✅ **Sugerencias en vivo** - AI sugiere respuestas en tiempo real
✅ **Resumen final completo** - Transcripción + hitos + análisis

---

## 🚀 CÓMO USAR

### Inicio Rápido

```powershell
# 1. Ejecutar como ADMINISTRADOR (requerido para hotkeys)
py interview_copilot_session_recorder.py
```

### Durante la Entrevista

**Opción 1: Push-to-Talk (Recomendado)**
1. Mantén presionado **Ctrl+Shift+R**
2. Habla tu pregunta/respuesta
3. Suelta las teclas cuando termines
4. El sistema transcribe y sugiere automáticamente

**Opción 2: Texto Manual**
1. Escribe tu pregunta en el prompt
2. Presiona Enter
3. Obtén sugerencia de respuesta

**Ver Resumen:**
- Escribe `summary` para ver resumen de la sesión actual
- Incluye: transcripción completa + análisis AI + hitos

**Salir:**
- Escribe `exit`
- Se guarda automáticamente el log completo

---

## 📊 FORMATO DEL RESUMEN FINAL

Al escribir `summary` o al salir, obtienes:

```
📊 RESUMEN DE LA SESIÓN
═══════════════════════════════════════════════════════════════
[INFO] Total de interacciones: 8

📝 TRANSCRIPCIÓN COMPLETA
───────────────────────────────────────────────────────────────
Q: Tell me about your experience with ETL processes
A: Based on my extensive experience...

Q: How would you handle a large data migration?
A: Given my work with Toyota Financial Services...

...

🎯 RESUMEN CON AI
───────────────────────────────────────────────────────────────
EXECUTIVE SUMMARY:
The candidate demonstrated strong technical knowledge...

KEY HIGHLIGHTS:
1. Discussed complex ETL experience with 800+ TB data
2. Showed leadership in multi-country projects
3. Highlighted expertise in Power BI and data visualization

AREAS COVERED:
- ETL and data migration strategies
- Project management methodologies
- Technical skills in SQL, Python, Power BI

RECOMMENDATIONS:
1. Emphasize specific metrics and outcomes
2. Provide more concrete examples of leadership
3. Connect technical skills to business impact
═══════════════════════════════════════════════════════════════
```

---

## 📁 ARCHIVOS GENERADOS

Cada sesión genera un archivo JSON en `logs/`:

**Nombre:** `interview_session_YYYYMMDD_HHMMSS.json`

**Contenido:**
```json
{
  "session_date": "2025-11-18T04:30:00",
  "total_interactions": 8,
  "full_transcript": "Q: ...\nA: ...",
  "ai_summary": "EXECUTIVE SUMMARY:\n...",
  "raw_data": [
    {
      "timestamp": "2025-11-18T04:05:00",
      "question": "Tell me about...",
      "suggestion": "Based on...",
      "type": "audio_interaction"
    }
  ]
}
```

---

## 🔧 INSTALACIÓN

### Requisitos Base

```powershell
pip install openai-whisper pyaudio keyboard numpy
```

### ⚠️ PyAudio en Windows (Especial)

PyAudio puede fallar en Windows. Soluciones:

**Opción 1: Wheel pre-compilado**
```powershell
# Descargar desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Ejemplo para Python 3.13 64-bit:
pip install PyAudio‑0.2.13‑cp313‑cp313‑win_amd64.whl
```

**Opción 2: Pipwin**
```powershell
pip install pipwin
pipwin install pyaudio
```

**Opción 3: Conda (si usas Anaconda)**
```powershell
conda install pyaudio
```

### Verificar Instalación

```python
# Test rápido
py -c "import whisper; import pyaudio; import keyboard; print('✅ Todo OK')"
```

---

## 🎮 CONTROLES

| Acción | Comando |
|--------|---------|
| **Grabar audio** | Mantén `Ctrl+Shift+R` |
| **Detener grabación** | Suelta `Ctrl+Shift+R` |
| **Pregunta texto** | Escribe y presiona Enter |
| **Ver resumen** | Escribe `summary` |
| **Salir** | Escribe `exit` |

---

## 💡 TIPS DE USO

### Para Mejor Transcripción

1. **Habla claro** - Articula bien las palabras
2. **Reduce ruido** - Ambiente silencioso
3. **Micrófono cerca** - A 15-30 cm de distancia
4. **Pausa natural** - No hables demasiado rápido

### Para Mejores Sugerencias

1. **Pregunta completa** - Graba la pregunta entera
2. **Contexto claro** - Menciona tecnologías específicas
3. **CV actualizado** - Asegura que `data/cv_descriptor.txt` esté al día

### Ejecutar Como Administrador (Windows)

**¿Por qué?** Los hotkeys globales requieren permisos elevados

**Cómo:**
```powershell
# Opción 1: Click derecho en PowerShell > "Ejecutar como administrador"

# Opción 2: Desde PowerShell admin
cd C:\Users\MSI\Desktop\ai-job-foundry
py interview_copilot_session_recorder.py
```

---

## 🔍 TROUBLESHOOTING

### "keyboard no disponible"

```powershell
pip install keyboard
```

### "PyAudio no instalado"

Ver sección de instalación de PyAudio arriba.

### "Whisper no funciona"

```powershell
# Reinstalar
pip uninstall openai-whisper
pip install openai-whisper

# Verificar
py -c "import whisper; print(whisper.__version__)"
```

### "Error: Permission denied (hotkey)"

**Ejecuta PowerShell como Administrador**

### "No graba audio"

```powershell
# Verificar micrófono
py -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_default_input_device_info())"
```

---

## 🆚 COMPARACIÓN DE VERSIONES

| Feature | Unified (anterior) | Session Recorder (nuevo) |
|---------|-------------------|--------------------------|
| Grabación | 10 seg fijos | Mientras mantienes tecla ⭐ |
| Transcripción | ✅ | ✅ |
| Sugerencias AI | ✅ | ✅ |
| Resumen sesión | ❌ | ✅ Completo ⭐ |
| Transcripción completa | ❌ | ✅ Con hitos ⭐ |
| Análisis AI final | ❌ | ✅ Ejecutivo ⭐ |
| Push-to-talk | ❌ | ✅ Ctrl+Shift+R ⭐ |

---

## 📝 EJEMPLO DE USO REAL

```
🎤 PUSH-TO-TALK: Mantén Ctrl+Shift+R para grabar

❓ Pregunta (o mantén Ctrl+Shift+R): 
[Usuario mantiene Ctrl+Shift+R y dice:]
"Tell me about your experience with large scale data migrations"

🎤 GRABANDO... (suelta Ctrl+Shift+R para parar)
⏹️ Grabación detenida
[AI] Transcribiendo...
[TRANSCRIBED] Tell me about your experience with large scale data migrations

💡 Analizando pregunta...

═══════════════════════════════════════════════════════════════
  💡 SUGERENCIA DE RESPUESTA
═══════════════════════════════════════════════════════════════

SUGGESTION: I led the migration of over 800TB of data at Toyota Financial 
Services, where I mapped complete database structures and automated file 
organization using Python. The project involved coordinating between legacy 
systems and modern ERP platforms.

KEY POINTS:
- Managed 800+ TB data migration at Toyota Financial Services
- Created automated Python scripts for data classification
- Coordinated between legacy and modern ERP systems

═══════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────

❓ Pregunta (o mantén Ctrl+Shift+R): summary

📊 RESUMEN DE LA SESIÓN
═══════════════════════════════════════════════════════════════
[INFO] Total de interacciones: 5

📝 TRANSCRIPCIÓN COMPLETA
...

🎯 RESUMEN CON AI
EXECUTIVE SUMMARY:
Strong performance demonstrating technical depth and project leadership...
═══════════════════════════════════════════════════════════════
```

---

## ✅ CHECKLIST PRE-ENTREVISTA

- [ ] LM Studio running (`http://127.0.0.1:11434`)
- [ ] CV actualizado en `data/cv_descriptor.txt`
- [ ] Micrófono conectado y testeado
- [ ] PowerShell ejecutado como administrador
- [ ] Ambiente silencioso
- [ ] Script ejecutado: `py interview_copilot_session_recorder.py`
- [ ] Hotkey testeado (Ctrl+Shift+R)

---

## 📞 SOPORTE

**Logs:** `logs/interview_session_*.json`

**Errores comunes:** Ver sección Troubleshooting

**Documentación completa:** Este archivo

---

**Versión:** 3.0 - Session Recorder  
**Fecha:** 2025-11-18  
**Autor:** AI Job Foundry Team
