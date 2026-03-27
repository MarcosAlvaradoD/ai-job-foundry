# 🎯 SOLUCIÓN COMPLETA - CLAUDE CODE CON OLLAMA + FALLBACK

## ❌ PROBLEMA ACTUAL:
Claude Code intenta usar modelo 'claude-sonnet-4-6' que NO existe.
Modelo correcto: 'claude-sonnet-4-20250514'

## ✅ SOLUCIÓN SIMPLE (SIN OLLAMA):

### PASO 1: Abrir VS Code Settings
1. En VS Code presiona: **Ctrl+Shift+P**
2. Escribe: **Preferences: Open User Settings (JSON)**
3. Presiona Enter

### PASO 2: Agregar esta configuración:
`json
{
  "claude.model": "claude-sonnet-4-20250514",
  "claude.apiKey": "TU_API_KEY_AQUI"
}
`

### PASO 3: Obtener API Key
1. Ve a: https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copia la key
4. Pégala en settings.json reemplazando "TU_API_KEY_AQUI"

---

## 🚀 SOLUCIÓN AVANZADA (OLLAMA + CLAUDE FALLBACK):

Esta es MÁS COMPLEJA pero te da:
- 5 intentos con Ollama GRATIS
- Si falla → pregunta si usar Claude API
- Control total de gastos

### OPCIÓN A: Modelo en LM Studio (SIMPLE)

Ya tienes LM Studio corriendo con Qwen 2.5 14B en:
**http://172.17.32.1:11434**

Configuración VS Code settings.json:
`json
{
  "claude.provider": "openai-compatible",
  "claude.baseURL": "http://172.17.32.1:11434/v1",
  "claude.model": "qwen2.5-14b-instruct",
  "claude.apiKey": "not-needed"
}
`

### OPCIÓN B: Ollama (REQUIERE SETUP)

1. **Descargar modelo** (6GB, tarda 10-15 min):
`powershell
& 'C:\Users\MSI\AppData\Local\Programs\Ollama\ollama.exe' pull qwen2.5:14b
`

2. **Configurar VS Code** settings.json:
`json
{
  "claude.provider": "ollama",
  "claude.ollamaUrl": "http://localhost:11434",
  "claude.model": "qwen2.5:14b"
}
`

---

## 💡 RECOMENDACIÓN INMEDIATA:

**OPCIÓN 1: Usar LM Studio** (Ya lo tienes funcionando)
`json
{
  "claude.baseURL": "http://172.17.32.1:11434/v1",
  "claude.model": "qwen2.5-14b-instruct",
  "claude.provider": "openai-compatible"
}
`

**OPCIÓN 2: Usar Claude API** (Más fácil, $)
`json
{
  "claude.model": "claude-sonnet-4-20250514",
  "claude.apiKey": "sk-ant-..."
}
`

---

## 📝 PASOS RÁPIDOS (OPCIÓN 1 - LM Studio):

1. **Ctrl+Shift+P** en VS Code
2. **Preferences: Open User Settings (JSON)**
3. Agregar:
`json
{
  "claude.provider": "openai-compatible",
  "claude.baseURL": "http://172.17.32.1:11434/v1",
  "claude.model": "qwen2.5-14b-instruct",
  "claude.apiKey": "not-needed",
  "claude.temperature": 0.7
}
`
4. **Ctrl+S** para guardar
5. Reload VS Code: **Ctrl+Shift+P** → **Developer: Reload Window**

---

## ✅ VERIFICACIÓN:

Después de configurar, ejecuta en VS Code terminal:
`powershell
curl http://172.17.32.1:11434/v1/models
`

Deberías ver: qwen2.5-14b-instruct

---

**¿Qué opción prefieres?**
- A) LM Studio (gratis, ya funciona)
- B) Claude API (fácil, $)
- C) Ollama (setup adicional, gratis)
