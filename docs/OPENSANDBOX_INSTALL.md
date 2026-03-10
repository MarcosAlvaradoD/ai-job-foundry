# 🚀 OpenSandbox — Guía de Instalación y Uso
**Actualizado:** 2026-03-10
**Fuente:** Alibaba (agent-infra/sandbox) — Apache 2.0 LICENSE (GRATIS)

---

## ¿Qué es OpenSandbox?

OpenSandbox es un sandbox de código abierto creado por Alibaba para **ejecutar agentes de IA de forma aislada y segura**. Combina en un solo contenedor Docker:

- 🌐 **Browser** (Playwright/Chrome) — para navegar y hacer web scraping
- 💻 **Shell** — para ejecutar código Python/JS
- 📁 **File system** — para leer/escribir archivos
- 🔧 **MCP** — Model Context Protocol para integración con Claude, GPT, etc.
- 🖥️ **VSCode Server** — editor web integrado

**Para AI Job Foundry es MUY ÚTIL** porque permite ejecutar los scrapers de LinkedIn/Glassdoor en un entorno aislado sin afectar el sistema host.

---

## Precio

**COMPLETAMENTE GRATIS** — Apache 2.0 License
- Sin límites de páginas
- Sin suscripción
- Self-hosted en tu máquina o servidor
- Funciona con Docker (ya lo tienes instalado)

---

## Requisitos

- Docker Desktop (ya lo tienes ✅)
- Python 3.8+ (ya lo tienes ✅)
- pip

---

## Instalación Rápida

### Opción A: Via pip (servidor local)

```bash
# Instalar el servidor OpenSandbox
pip install opensandbox-server

# Inicializar configuración
opensandbox-server init-config

# Arrancar el servidor
opensandbox-server
```

El servidor quedará disponible en `http://localhost:8000`

### Opción B: Via Docker (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/agent-infra/sandbox.git
cd sandbox

# Levantar con Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Opción C: Imagen Docker directa

```bash
docker run -d \
  --name opensandbox \
  -p 8000:8000 \
  -v /tmp/sandbox:/workspace \
  agent-infra/sandbox:latest
```

---

## Uso con AI Job Foundry

### Instalar el SDK de Python

```bash
pip install opensandbox
```

### Ejemplo: Ejecutar un scraper en sandbox aislado

```python
from opensandbox import Sandbox

# Crear sandbox
sandbox = Sandbox()

# Ejecutar scraper de LinkedIn dentro del sandbox
result = sandbox.run_code("""
import subprocess
result = subprocess.run(
    ['python3', 'LINKEDIN_SMART_VERIFIER_V3.py', '--dry-run'],
    capture_output=True, text=True
)
print(result.stdout)
""")

print(result.output)
sandbox.close()
```

### Ejemplo: Browser automation en sandbox

```python
from opensandbox import Sandbox

with Sandbox() as sb:
    # Navegar a LinkedIn
    page = sb.browser.new_page()
    page.goto("https://www.linkedin.com/jobs/")

    # Extraer jobs
    jobs = page.query_selector_all('.job-card-container')
    for job in jobs[:5]:
        print(job.inner_text())
```

---

## Integración con Claude Code

OpenSandbox soporta integración nativa con Claude Code via MCP:

```json
// En .claude/settings.json - agregar MCP server
{
  "mcpServers": {
    "opensandbox": {
      "command": "opensandbox-mcp",
      "args": ["--port", "8000"]
    }
  }
}
```

---

## Casos de Uso para este Proyecto

| Caso | Sin Sandbox | Con OpenSandbox |
|------|------------|-----------------|
| Scraping LinkedIn | Riesgo de ban IP host | ✅ IP aislada del sandbox |
| Auto-apply testing | Modifica estado real | ✅ Dry-run en entorno aislado |
| Ejecución de pipeline | Afecta sistema host | ✅ Contenedor limpio |
| Debugging scrapers | Mezcla con env local | ✅ Entorno reproducible |

---

## Recursos

- GitHub: https://github.com/agent-infra/sandbox
- Documentación: https://github.com/agent-infra/sandbox/wiki
- Issues: https://github.com/agent-infra/sandbox/issues

---

*Documentado por Claude Code para AI Job Foundry*
