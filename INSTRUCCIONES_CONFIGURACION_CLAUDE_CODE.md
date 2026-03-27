# 🔧 CONFIGURACIÓN CLAUDE CODE - CON OLLAMA + CLAUDE API FALLBACK

## 📍 Archivo a crear/modificar:
C:\Users\MSI\.claude\claude_desktop_config.json

## 🎯 Configuración Correcta:

`json
{
  "mcpServers": {},
  "anthropic": {
    "apiKey": "TU_API_KEY_AQUI"
  },
  "providers": [
    {
      "name": "ollama",
      "type": "ollama",
      "baseURL": "http://localhost:11434",
      "models": ["qwen2.5:14b"],
      "retries": 5,
      "timeout": 30000,
      "priority": 1
    },
    {
      "name": "anthropic",
      "type": "anthropic",
      "models": ["claude-sonnet-4-20250514"],
      "priority": 2,
      "requiresAuth": true
    }
  ],
  "defaultProvider": "ollama",
  "fallbackProvider": "anthropic",
  "model": "qwen2.5:14b"
}
`

## 🔑 PASO 1: Obtener API Key de Anthropic

1. Ve a: https://console.anthropic.com/settings/keys
2. Click en "Create Key"
3. Copia la API key
4. Guárdala en lugar seguro

## 📝 PASO 2: Aplicar configuración

`powershell
# Crear directorio si no existe
New-Item -ItemType Directory -Force -Path ~\.claude

# Crear archivo de configuración
@'
{
  "mcpServers": {},
  "providers": [
    {
      "name": "ollama",
      "baseURL": "http://localhost:11434",
      "models": ["qwen2.5:14b"],
      "retries": 5,
      "priority": 1
    },
    {
      "name": "anthropic",
      "models": ["claude-sonnet-4-20250514"],
      "priority": 2
    }
  ],
  "defaultProvider": "ollama",
  "model": "qwen2.5:14b"
}
'@ | Out-File -FilePath ~\.claude\claude_desktop_config.json -Encoding UTF8

Write-Host "✅ Configuración creada en: C:\Users\MSI\.claude\claude_desktop_config.json"
`

## ⚠️ IMPORTANTE: VS Code Settings

También necesitas configurar settings.json de VS Code:

**Ubicación:** 
- Windows: %APPDATA%\Code\User\settings.json
- O desde VS Code: Ctrl+Shift+P → "Preferences: Open User Settings (JSON)"

**Agregar:**
`json
{
  "claude.provider": "ollama",
  "claude.ollamaUrl": "http://localhost:11434",
  "claude.model": "qwen2.5:14b",
  "claude.fallbackProvider": "anthropic",
  "claude.retries": 5,
  "claude.requireApprovalForOllamaFallback": true
}
`

## 🚀 COMANDOS RÁPIDOS

### Verificar Ollama:
`powershell
curl http://localhost:11434/api/tags
`

### Ver modelos disponibles:
`powershell
ollama list
`

### Descargar modelo si falta:
`powershell
ollama pull qwen2.5:14b
`

## 🎯 FLUJO ESPERADO:

1. Claude Code intenta Ollama (5 veces)
2. Si falla 5 veces → Te pregunta si usar Claude API
3. Si aceptas → Usa Claude API (consume tokens)
4. Si rechazas → Error sin consumir tokens

---

**Guardado en:** INSTRUCCIONES_CONFIGURACION_CLAUDE_CODE.md
