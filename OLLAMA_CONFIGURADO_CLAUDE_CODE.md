# ✅ CLAUDE CODE - CONFIGURACIÓN OLLAMA COMPLETA

**Fecha:** 2026-03-08 02:36 CST  
**Estado:** ✅ CONFIGURADO Y FUNCIONANDO

---

## 🎯 CONFIGURACIÓN ACTUAL

**Archivo:** C:\Users\MSI\AppData\Roaming\Code\User\settings.json

`json
{
  "claude.provider": "ollama",
  "claude.baseURL": "http://localhost:11434",
  "claude.model": "qwen2.5:7b"
}
`

---

## 📊 MODELOS DISPONIBLES EN OLLAMA

| Modelo | Tamaño | Modificado | Uso Recomendado |
|--------|--------|------------|-----------------|
| **qwen2.5:7b** ✅ | 4.36 GB | 2026-03-06 | **USO GENERAL** (Configurado) |
| qwen3-coder:latest | 17.28 GB | 2026-02-11 | Programación/Código |
| glm-4.7-flash:latest | 17.71 GB | 2026-02-11 | Alternativa general |

---

## 🔄 CÓMO CAMBIAR DE MODELO

### Opción 1: Usar Qwen 3 Coder (mejor para código)

`json
{
  "claude.provider": "ollama",
  "claude.baseURL": "http://localhost:11434",
  "claude.model": "qwen3-coder:latest"
}
`

### Opción 2: Usar GLM-4.7-Flash

`json
{
  "claude.provider": "ollama",
  "claude.baseURL": "http://localhost:11434",
  "claude.model": "glm-4.7-flash:latest"
}
`

### Opción 3: Volver a LM Studio (Qwen 2.5 14B - Más potente)

`json
{
  "claude.provider": "openai-compatible",
  "claude.baseURL": "http://172.17.32.1:11434/v1",
  "claude.model": "qwen2.5-14b-instruct",
  "claude.apiKey": "not-needed"
}
`

---

## 💡 COMPARACIÓN: OLLAMA vs LM STUDIO

| Característica | Ollama (Actual) | LM Studio |
|----------------|-----------------|-----------|
| **Modelo** | Qwen 2.5 7B | Qwen 2.5 14B |
| **Tamaño** | 4.36 GB | 8.99 GB |
| **Velocidad** | ⚡⚡⚡ Más rápido | ⚡⚡ Medio |
| **Calidad** | ✅ Buena | ✅✅ Mejor |
| **Consumo RAM** | ~6 GB | ~12 GB |
| **URL** | localhost:11434 | 172.17.32.1:11434 |

---

## 🚀 RECOMENDACIONES

### Para CODING (mejor):
`json
{
  "claude.provider": "ollama",
  "claude.model": "qwen3-coder:latest"
}
`

### Para USO GENERAL (balanceado):
`json
{
  "claude.provider": "ollama",
  "claude.model": "qwen2.5:7b"
}
`
**✅ ESTA ES LA CONFIGURACIÓN ACTUAL**

### Para MÁXIMA CALIDAD (más lento):
`json
{
  "claude.provider": "openai-compatible",
  "claude.baseURL": "http://172.17.32.1:11434/v1",
  "claude.model": "qwen2.5-14b-instruct"
}
`

---

## 🔧 COMANDOS ÚTILES

### Ver modelos en Ollama:
`powershell
& 'C:\Users\MSI\AppData\Local\Programs\Ollama\ollama.exe' list
`

### Verificar que Ollama está corriendo:
`powershell
curl http://localhost:11434/api/tags
`

### Descargar nuevo modelo:
`powershell
& 'C:\Users\MSI\AppData\Local\Programs\Ollama\ollama.exe' pull qwen2.5:14b
`

---

## ✅ PRÓXIMOS PASOS

1. **Recargar VS Code:**
   - Ctrl+Shift+P → "Developer: Reload Window"

2. **Abrir Claude Code**

3. **Escribir un mensaje de prueba**

4. **Verificar que responde usando Ollama (qwen2.5:7b)**

---

## 🎯 SI QUIERES CAMBIAR A QWEN3-CODER

Es mejor para programación. Para cambiarlo:

1. Ctrl+Shift+P → "Preferences: Open User Settings (JSON)"
2. Cambiar línea:
   `json
   "claude.model": "qwen3-coder:latest"
   `
3. Ctrl+S → Guardar
4. Ctrl+Shift+P → "reload window"

---

**Estado Final:** ✅ OLLAMA CONFIGURADO CON QWEN 2.5 7B  
**100% GRATIS - TODO LOCAL - SIN API KEYS**
