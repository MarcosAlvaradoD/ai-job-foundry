# 🤖 AI Job Foundry

Sistema automatizado de búsqueda de empleo con IA local que procesa ofertas de LinkedIn, Indeed y Glassdoor.

## 🎯 Características

- ✅ **Procesamiento automatizado de emails** - Gmail API
- ✅ **Scraping inteligente** - Playwright + Firefox
- ✅ **Análisis con IA local** - LM Studio + Qwen 2.5 14B
- ✅ **Cálculo de FIT SCORES** - 0-10 basado en perfil
- ✅ **Verificación de expirados** - Smart verifiers por plataforma
- ✅ **Tracking en Google Sheets** - Integración completa
- ✅ **Auto-apply LinkedIn** - Easy Apply automation
- 🚧 **Interview Copilot** - En desarrollo

## 🛠️ Stack Tecnológico

- **Python 3.13** - Core del sistema
- **LM Studio** - IA local (Qwen 2.5 14B)
- **Playwright** - Web scraping y verificación
- **Gmail API** - Procesamiento de emails
- **Google Sheets API** - Tracking y storage
- **Flask** - Dashboard web
- **PowerShell** - Scripts de automatización

## 📋 Requisitos

### Software
- Python 3.13+
- LM Studio (o servidor LLM compatible con OpenAI API)
- Windows 11 (o adaptar scripts para Linux/Mac)
- Navegador Firefox (para Playwright)

### APIs y Credenciales
- Google Cloud Project con Gmail y Sheets APIs habilitadas
- Cuenta de LinkedIn (para scraping y auto-apply)
- Cuentas de Indeed/Glassdoor (opcional)

## 🚀 Instalación

### 1. Clonar repositorio
```bash
git clone https://github.com/TU_USUARIO/ai-job-foundry.git
cd ai-job-foundry
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
playwright install firefox
```

### 3. Configurar credenciales

**IMPORTANTE:** Nunca subas archivos de credenciales al repositorio.

#### A) Google OAuth
1. Crea proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilita Gmail API y Google Sheets API
3. Crea credenciales OAuth 2.0
4. Descarga como `data/credentials/credentials.json`

#### B) Variables de entorno
Crea archivo `.env` en la raíz:
```bash
# Google
GOOGLE_SHEETS_ID=tu_spreadsheet_id

# LinkedIn
LINKEDIN_EMAIL=tu_email@gmail.com
LINKEDIN_PASSWORD=tu_password

# Gmail
GMAIL_ADDRESS=tu_email@gmail.com

# LM Studio (opcional)
LM_STUDIO_URL=http://127.0.0.1:11434
```

#### C) CV Descriptor
Crea `data/cv_descriptor.txt` con tu perfil profesional para el análisis de IA.

### 4. Primera ejecución
```bash
# Generar token OAuth (abrirá navegador)
py FIX_OAUTH_TOKEN.py

# Ejecutar control center
py control_center.py
```

## 📊 Estructura del Proyecto

```
ai-job-foundry/
├── core/
│   ├── ingestion/       # Scrapers (LinkedIn, Indeed, Glassdoor)
│   ├── enrichment/      # IA analyzer, cover letter gen
│   ├── sheets/          # Google Sheets manager
│   ├── automation/      # Gmail monitor, auto-apply
│   └── utils/           # LLM client, helpers
├── data/
│   ├── credentials/     # OAuth (NO SUBIR A GIT)
│   ├── state/           # Tracking de procesados
│   └── cv_descriptor.txt # Tu perfil (NO SUBIR A GIT)
├── logs/                # Session logs
├── scripts/             # Scripts de prueba
├── web/                 # Dashboard Flask
├── *.py                 # Verifiers y utilities
└── control_center.py    # Menú principal
```

## 🎮 Uso

### Control Center (Recomendado)
```bash
py control_center.py
```
Menú interactivo con todas las opciones.

### Pipeline Completo
```bash
py run_daily_pipeline.py --all
```
Ejecuta: emails → boletines → IA → auto-apply → verificación → reporte

### Operaciones Individuales
```bash
# Procesar emails
py control_center.py  # Opción 3

# Verificar LinkedIn
py control_center.py  # Opción 7

# Análisis IA
py control_center.py  # Opción 5
```

## 📈 Pipeline Workflow

```
┌─────────────────┐
│  Gmail Monitor  │ ← Emails de reclutadores
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Bulletin Parser │ ← Boletines (LinkedIn/Indeed/Glassdoor)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Analyzer   │ ← Calcula FIT SCORES (0-10)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Google Sheets   │ ← Guarda jobs + scores
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Smart Verifiers │ ← Verifica URLs (Playwright)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Auto-Apply    │ ← Aplica a FIT 7+ (LinkedIn Easy Apply)
└─────────────────┘
```

## 🔧 Troubleshooting

### LM Studio no responde
```powershell
.\detect_lm_studio_ip.ps1
```

### Unicode errors
```powershell
.\fix_unicode_all.ps1
Get-Process python* | Stop-Process -Force
```

### OAuth expirado
```powershell
py FIX_OAUTH_TOKEN.py
```

## 📝 Notas Importantes

- **Privacidad:** Toda la IA corre local (LM Studio), no se envía data a APIs externas
- **Credenciales:** NUNCA subir `.env`, `credentials.json`, `token.json` a GitHub
- **Rate Limits:** Respeta los límites de las APIs (Gmail, Sheets, LinkedIn)
- **Uso Ético:** Solo para búsqueda personal de empleo

## 🤝 Contribuciones

Este es un proyecto personal, pero si quieres contribuir:
1. Fork el repo
2. Crea una branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Uso personal. No redistribuir sin permiso.

## 👤 Autor

**Marcos Alberto Alvarado de la Torre**
- Project Manager / Business Analyst
- Guadalajara, México

---

⭐ Si te sirvió este proyecto, dale una estrella!
