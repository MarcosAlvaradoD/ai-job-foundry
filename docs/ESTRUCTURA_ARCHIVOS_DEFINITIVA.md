# 📂 ESTRUCTURA DE ARCHIVOS DEFINITIVA - AI JOB FOUNDRY

**Última actualización:** 2025-12-12  
**Propósito:** Evitar mover archivos después de crearlos

---

## 🎯 REGLA DE ORO

**ANTES de crear cualquier archivo, consulta esta guía para saber EXACTAMENTE dónde va.**

---

## 📁 DIRECTORIO RAÍZ (`/`)

### ✅ LO QUE VA EN LA RAÍZ:
- `README.md` - Documentación principal del proyecto
- `.env` - Variables de entorno
- `.gitignore` - Archivos a ignorar en Git
- `requirements.txt` - Dependencias Python
- `paths.py` - Configuración centralizada de rutas
- `run_daily_pipeline.py` - Pipeline principal
- `control_center.py` - Lanzador unificado
- `PROJECT_STATUS.md` - Estado general del proyecto
- `PROMPT_NUEVO_CHAT.md` - Para migrar contexto entre chats

### ✅ SCRIPTS DE AUTOMATIZACIÓN (*.ps1):
- `START_*.bat` / `START_*.ps1` - Lanzadores de servicios
- `ORGANIZE_*.ps1` - Scripts de organización
- `CLEANUP_*.ps1` - Scripts de limpieza
- `DIAGNOSTICO_*.ps1` - Scripts de diagnóstico
- `TEST_*.ps1` - Scripts de testing rápido

### ❌ LO QUE NO VA EN LA RAÍZ:
- Documentación extensa (→ `docs/`)
- Scripts de mantenimiento (→ `scripts/maintenance/`)
- Configuraciones específicas (→ `config/`)
- Archivos de prueba (→ `scripts/tests/`)
- Backups o versiones antiguas (→ `archive/`)

---

## 📚 DIRECTORIO `docs/`

### Documentación General:
```
docs/
├── PROJECT_STATUS.md          # Estado detallado actualizado
├── MASTER_FEATURE_ROADMAP.md  # Roadmap completo
├── CONTROL_CENTER_GUIDE.md    # Guía del Control Center
├── AUTO_APPLY_GUIDE.md        # Guía de auto-apply
├── FIX_OAUTH_SCOPES.md        # Fix de OAuth ⭐ NUEVO
└── FIX_UNICODE_EXPIRE.md      # Fix de Unicode ⭐ NUEVO
```

### Subdirectorios:
```
docs/
├── guides/              # Guías de uso detalladas
├── setup/               # Guías de instalación/configuración
├── audit/               # Auditorías y análisis
├── prompts/             # Prompts para IA
├── session_reports/     # Reportes de sesiones
├── quickstart/          # Guías de inicio rápido
└── archive/             # Documentación obsoleta
```

### 🆕 NUEVOS DOCUMENTOS DE INVESTIGACIÓN:
```
docs/research/           # ⭐ CARPETA NUEVA
├── ANALISIS_MODELOS_NUEVOS_DIC2025.md      # Análisis comparativo
├── GUIA_CAMBIO_MODELO_LLAMA3GROQ.md        # Paso a paso
└── RESUMEN_EJECUTIVO_CAMBIO_MODELO.md      # Resumen ejecutivo
```

---

## 🔧 DIRECTORIO `scripts/`

### Scripts por Categoría:
```
scripts/
├── tests/               # Scripts de testing
│   ├── test_*.py        # Tests específicos
│   └── visual_test.py   # Tests visuales
│
├── maintenance/         # Mantenimiento del sistema ⭐ NUEVA
│   ├── cleanup_*.py     # Scripts de limpieza
│   ├── fix_*.py         # Scripts de corrección
│   └── fix_unicode_expire.py  # Fix Unicode ⭐ NUEVO
│
├── verification/        # Verificación de datos
│   └── check_*.py       # Chequeos de integridad
│
├── verifiers/           # Verificadores específicos
│   ├── EXPIRE_LIFECYCLE.py
│   ├── GLASSDOOR_SMART_VERIFIER.py
│   ├── INDEED_SMART_VERIFIER.py
│   └── LINKEDIN_SMART_VERIFIER_V3.py
│
├── oauth/               # Scripts de OAuth
│   └── reauthenticate_gmail.py
│
├── batch/               # Procesamiento por lotes
│   └── batch_*.py
│
├── setup/               # Scripts de configuración inicial
│   └── setup_*.py
│
└── powershell/          # Scripts PowerShell auxiliares
    └── *.ps1
```

---

## 🗃️ DIRECTORIO `data/`

```
data/
├── credentials/         # Credenciales (NO en GitHub)
│   ├── credentials.json
│   ├── token.json
│   └── gmail-token.json
│
├── linkedin_cookies.json  # Cookies LinkedIn (NO en GitHub)
├── cv_descriptor.txt      # Descriptor del CV
├── sheets_config.json     # Configuración de Sheets
│
├── templates/           # Plantillas
│   └── cover_letter_*.txt
│
├── raw_jobs/            # Jobs sin procesar
├── applications/        # Historial de aplicaciones
├── interviews/          # Datos de entrevistas
├── samples/             # Datos de ejemplo
├── state/               # Estado del sistema
├── model_memory/        # Memoria de modelos IA
├── browser_data/        # Datos del navegador (LinkedIn)
└── browser_data_indeed/ # Datos del navegador (Indeed)
```

---

## ⚙️ DIRECTORIO `config/`

```
config/
└── devfoundry.yaml      # Configuración de DevFoundry
```

---

## 🏭 DIRECTORIO `core/` (NO TOCAR)

**Código Python del sistema:**
```
core/
├── automation/          # Gmail monitor, etc.
├── copilot/             # Interview Copilot
├── enrichment/          # AI analyzer
├── ingestion/           # Scrapers
├── sheets/              # Sheet manager
├── utils/               # Utilidades (llm_client, etc.)
└── jobs_pipeline/       # Pipeline de trabajos
```

**REGLA:** Solo modifica archivos aquí cuando sea ABSOLUTAMENTE necesario.

---

## 📦 DIRECTORIO `archive/`

```
archive/
├── backups/             # Backups de archivos
├── old_scripts/         # Scripts obsoletos
├── old_configs/         # Configuraciones antiguas
├── old_docs/            # Documentación obsoleta
├── old_versions/        # Versiones antiguas de código
└── migrations/          # Scripts de migración antiguos
```

**REGLA:** Mueve aquí cualquier archivo que ya no uses pero quieras conservar.

---

## 🚫 DIRECTORIOS A NO MODIFICAR MANUALMENTE

```
.git/                    # Git metadata (automático)
.claude/                 # Configuración de Claude
__pycache__/             # Cache de Python (automático)
build/                   # Build de ejecutables
dist/                    # Distribución de ejecutables
logs/                    # Logs del sistema (automático)
state/                   # Estado del sistema (automático)
```

---

## 📝 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Crear script de diagnóstico
```powershell
# ❌ INCORRECTO:
New-Item -Path "C:\Users\MSI\Desktop\ai-job-foundry\DIAGNOSTICO_MODELOS.ps1"

# ✅ CORRECTO:
New-Item -Path "C:\Users\MSI\Desktop\ai-job-foundry\scripts\maintenance\DIAGNOSTICO_MODELOS.ps1"
```

### Ejemplo 2: Crear documento de investigación
```powershell
# ❌ INCORRECTO:
New-Item -Path "C:\Users\MSI\Desktop\ai-job-foundry\COMPARATIVA_MODELOS.md"

# ✅ CORRECTO:
New-Item -Path "C:\Users\MSI\Desktop\ai-job-foundry\docs\research\COMPARATIVA_MODELOS.md"
```

### Ejemplo 3: Crear script de test
```powershell
# ❌ INCORRECTO:
New-Item -Path "C:\Users\MSI\Desktop\ai-job-foundry\test_nuevo_modelo.py"

# ✅ CORRECTO:
New-Item -Path "C:\Users\MSI\Desktop\ai-job-foundry\scripts\tests\test_nuevo_modelo.py"
```

---

## 🎯 CHECKLIST ANTES DE CREAR UN ARCHIVO

- [ ] ¿Es documentación? → `docs/` (o `docs/research/` si es investigación)
- [ ] ¿Es un script de test? → `scripts/tests/`
- [ ] ¿Es un script de mantenimiento? → `scripts/maintenance/`
- [ ] ¿Es un launcher/automation? → Raíz (solo si es .ps1 o .bat)
- [ ] ¿Es configuración? → `config/` o raíz (solo .env o requirements.txt)
- [ ] ¿Es código core? → `core/` (rara vez)
- [ ] ¿Es un backup? → `archive/backups/`
- [ ] ¿Es obsoleto pero útil? → `archive/`

---

## 🚨 SEÑALES DE ALARMA

### Si ves esto en la raíz, ¡MUÉVELO!
- `test_*.py` → `scripts/tests/`
- `fix_*.py` → `scripts/maintenance/`
- `GUIA_*.md` → `docs/` o `docs/guides/`
- `COMPARATIVA_*.md` → `docs/research/`
- `ANALISIS_*.md` → `docs/audit/`
- `*.backup` → `archive/backups/`
- `*.old` → `archive/old_versions/`

---

## 📋 RESUMEN RÁPIDO

| Tipo de Archivo | Ubicación |
|-----------------|-----------|
| Launcher/Start scripts | Raíz |
| Documentación general | `docs/` |
| Investigación/Research | `docs/research/` |
| Scripts de test | `scripts/tests/` |
| Scripts de mantenimiento | `scripts/maintenance/` |
| Código core | `core/` |
| Configuración | `config/` o raíz (.env) |
| Credenciales | `data/credentials/` |
| Backups | `archive/backups/` |
| Obsoletos | `archive/` |

---

**¿Dudas?** Consulta esta guía ANTES de crear cualquier archivo nuevo.
