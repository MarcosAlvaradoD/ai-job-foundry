# AI JOB FOUNDRY - ÍNDICE DE PROYECTO

**Fecha de consolidación:** 2025-11-03 01:49
**Autor:** Marcos Alvarado
**Repositorio:** https://github.com/MarcosAlvaradoD/ai-job-foundry

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ai-job-foundry/
├── core/                      # Código principal
│   ├── jobs_pipeline/         # Pipeline de vacantes (desde Jobs/)
│   ├── dev_foundry/           # Sistema de autoprogramación (desde dev/)
│   └── tracker/               # Sistema de seguimiento (NUEVO)
│       ├── job_tracker.py
│       ├── interview_copilot.py
│       └── project_auditor.py
│
├── workflows/                 # Workflows de n8n
│   └── *.json
│
├── data/                      # Datos locales (NO subir a Git)
│   ├── credentials/           # OAuth tokens
│   ├── applications/          # Estado de aplicaciones
│   └── cv_descriptor.txt      # Tu CV
│
├── config/                    # Configuraciones
│   ├── devfoundry.yaml
│   └── models_registry.json
│
├── logs/                      # Logs del sistema
├── docs/                      # Documentación
└── tests/                     # Pruebas
```

---

## 🔧 SCRIPTS PRINCIPALES

### Jobs Pipeline (core/jobs_pipeline/)
- `analyze_market_fit.py` - `code_patcher.py` - `enrich_sheet_with_llm_v2.py` - `enrich_sheet_with_llm_v3.py` - `enrich_sheet_with_llm.py` - `ingest_email_to_sheet_v2.py` - `ingest_email_to_sheet.py` - `ingest_job.py` - `pro_trainer.py` - `PRO.py` - `send_test_email.py` - `sheet_setup.py` - `sheet_summary.py` - `smoke_check.py` - `test_sheets.py` - `verify_sheet_access.py`

### Dev Foundry (core/dev_foundry/)
- `foundry.py` - `verify_sheet_access.py`

### JobTracker (core/tracker/)
- `job_tracker.py` - Monitor de comunicaciones
- `interview_copilot.py` - Asistente de entrevistas
- `project_auditor.py` - Auditor de estructura

---

## 📦 DEPENDENCIAS

Ver `requirements.txt` para lista completa.

Principales:
- google-auth
- google-api-python-client
- pandas
- requests
- whisper (para interview copilot)

---

## 🚀 INICIO RÁPIDO

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar credenciales de Google:
   - Descargar `credentials.json` desde Google Cloud Console
   - Colocar en `data/credentials/`

3. Ejecutar pipeline de vacantes:
   ```bash
   python core/jobs_pipeline/daily_job_harvest.py
   ```

4. Iniciar monitor de seguimiento:
   ```bash
   python core/tracker/job_tracker.py
   ```

---

## 📄 LICENCIA

MIT License with Commercial Clause
Copyright (c) 2025 Marcos Alvarado

Uso personal: GRATIS
Uso comercial: Requiere permiso y compensación

Contacto: markalvati@gmail.com

