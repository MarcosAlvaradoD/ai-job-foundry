# LM STUDIO 0.4.1 - NEW REST API v1

**Actualización:** 2026-02-20  
**Versión LM Studio:** 0.4.1

---

## 🆕 CAMBIOS PRINCIPALES

### REST API v1
LM Studio 0.4.1 introduce una nueva API REST nativa en `/api/v1/*` endpoints.

**Antes (0.3.x):**
- OpenAI-compatible endpoints: `/v1/chat/completions`
- Anthropic-compatible endpoints

**Ahora (0.4.1+):**
- **Nuevo:** Native REST API v1: `/api/v1/chat`
- **Sigue funcionando:** OpenAI-compatible endpoints
- **Sigue funcionando:** Anthropic-compatible endpoints

---

## 📊 ENDPOINTS DISPONIBLES

| Endpoint | Method | Descripción |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Chat completions (native) |
| `/api/v1/models` | GET | List available models |
| `/api/v1/models/load` | POST | Load a model |
| `/api/v1/models/unload` | POST | Unload current model |
| `/api/v1/models/download` | POST | Download new models |
| `/api/v1/models/download/status` | GET | Check download status |

---

## 🔐 PERMISSION TOKENS

LM Studio 0.4.1 ahora soporta **Permission Tokens** para control granular de acceso a la API.

**Permisos disponibles:**
- `Allow per-request remote MCP servers`
- `Allow calling servers from mcp.json`

**Cómo usar:**
1. En LM Studio → Developer → Permission Tokens
2. Create token con permisos específicos
3. Usar en requests: `Authorization: Bearer sk-lm-...`

---

## 🎯 FEATURES COMPARISON

### Native `/api/v1/chat` vs OpenAI-compatible

| Feature | `/api/v1/chat` (Native) | `/v1/chat/completions` (OpenAI) |
|---------|------------------------|--------------------------------|
| Streaming | ✅ | ✅ |
| Stateful chat | ✅ | ❌ |
| Remote MCPs | ✅ | ❌ |
| Local MCPs (from mcp.json) | ✅ | ❌ |
| Custom tools | ❌ | ✅ |
| Assistant messages in request | ❌ | ✅ |
| Model load streaming events | ✅ | ❌ |
| Prompt processing events | ✅ | ❌ |
| Specify context length | ✅ | ❌ |

---

## 💻 EJEMPLO DE USO

### Native API v1 (Nuevo)

```python
import requests

# Con Permission Token
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-lm-q5EbkdND:wzLAIjGVZP0S8I2JOQ21"
}

# Native endpoint
response = requests.post(
    "http://localhost:1234/api/v1/chat",
    headers=headers,
    json={
        "model": "qwen/qwen2.5-14b-instruct-q4_k_m",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "stream": True,
        "context_length": 32000  # ✅ Nuevo: Especificar context length
    }
)
```

### OpenAI-Compatible (Sigue funcionando)

```python
import requests

# Sin token (para uso local)
response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "qwen/qwen2.5-14b-instruct-q4_k_m",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "stream": True
    }
)
```

---

## 🔧 MCP VIA API

LM Studio 0.4.1 permite usar MCP servers directamente desde la API.

**Ejemplo con MCP:**

```bash
curl http://localhost:1234/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LM_API_TOKEN" \
  -d '{
    "model": "openai/gpt-oss-20b",
    "input": "Find me the latest Qwen models.",
    "integrations": [
      {
        "type": "ephemeral_mcp",
        "server_label": "huggingface",
        "server_url": "https://huggingface.co/mcp",
        "allowed_tools": ["model_search"]
      }
    ]
  }'
```

---

## ⚠️ COMPATIBILIDAD CON AI JOB FOUNDRY

### ¿Necesitamos actualizar?

**Respuesta: NO urgentemente**

Nuestro código actual usa:
```python
LLM_ENDPOINT = "http://172.23.0.1:11434/v1/chat/completions"  # OpenAI-compatible
```

Este endpoint **sigue funcionando** en LM Studio 0.4.1.

### Cuándo actualizar

Actualizar a `/api/v1/chat` sería útil si queremos:
1. ✅ **Stateful chat** - Mantener contexto entre llamadas
2. ✅ **Context length control** - Especificar tamaño de contexto
3. ✅ **Model load events** - Streaming de carga de modelo
4. ✅ **MCP servers** - Usar MCP servers desde Interview Copilot

### Cómo actualizar

Si decidimos actualizar:

**1. Actualizar endpoint:**
```python
# core/utils/llm_client.py
LLM_ENDPOINT = "http://172.23.0.1:11434/api/v1/chat"  # ← Cambiar aquí
```

**2. Ajustar formato de request:**
```python
# Native API usa "input" en lugar de "messages"
response = requests.post(
    LLM_ENDPOINT,
    json={
        "model": model_name,
        "input": prompt,  # ← Cambio aquí
        "stream": False
    }
)
```

**3. Opcional: Agregar Permission Token**
```python
headers = {
    "Authorization": f"Bearer {LM_STUDIO_TOKEN}"
}
```

---

## 📚 DOCUMENTACIÓN OFICIAL

**LM Studio REST API Docs:**
- Native API v1: https://lmstudio.ai/docs/api/rest-api
- OpenAI-compatible: https://lmstudio.ai/docs/api/openai
- Anthropic-compatible: https://lmstudio.ai/docs/api/anthropic

**GitHub Issues:**
https://github.com/lmstudio-ai/lmstudio.js/issues

---

## 🎯 RECOMENDACIÓN

**Para AI Job Foundry:**

1. **Ahora:** Seguir usando OpenAI-compatible endpoint ✅
2. **Corto plazo:** No actualizar (funciona perfectamente)
3. **Largo plazo:** Considerar Native API v1 para:
   - Interview Copilot (stateful chat)
   - Context length control (mejor rendimiento)

**Prioridad:** Baja (nice-to-have, no urgente)

---

**Última actualización:** 2026-02-20 por Claude
