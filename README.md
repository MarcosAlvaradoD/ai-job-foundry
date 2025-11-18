# AI Job Foundry - Sistema Unificado

**Fecha de unificación:** 2025-11-06 02:12

## 🎯 Sistema Completo

Este proyecto unifica:
- **Pipeline de Jobs/** (ingesta + enriquecimiento IA)
- **Job Tracker** (seguimiento de aplicaciones)
- **Interview Copilot** (asistente de entrevistas)

## 📁 Estructura

```
ai-job-foundry/
├── core/
│   ├── ingestion/          # Gmail → Sheets
│   ├── enrichment/         # IA → Análisis
│   └── tracking/           # Seguimiento
├── data/
│   ├── cv_descriptor.txt   # Tu CV
│   └── credentials/        # OAuth tokens
├── run_unified.py          # Ejecutor principal
└── config.json             # Configuración
```

## 🚀 Uso Rápido

### Ejecución única:
```bash
py run_unified.py
```

### Ejecución programada (cada 30 min):
```bash
py run_unified.py --mode schedule --interval 30
```

### Componentes individuales:
```bash
# Solo tracker
py job_tracker.py check

# Solo dashboard
py run_dashboard.py

# Interview Copilot
py interview_copilot_simple.py
```

## 🔧 Configuración

Edita `config.json` para:
- Cambiar Sheet ID
- Ajustar endpoint de IA
- Configurar intervalos

## 📊 Dashboard

Abre en navegador:
```
http://localhost:8000/dashboard.html
```

## 🎙️ Interview Copilot

Antes de entrevista:
1. Edita empresa/posición en `interview_copilot_simple.py`
2. Ejecuta: `py interview_copilot_simple.py`
3. Posiciona ventana donde NO aparezca en cámara

## 📝 Migrado desde Jobs/

- ✅ Scripts de ingesta
- ✅ Enriquecimiento con LM Studio
- ✅ Análisis de fit
- ✅ Memoria de IA
- ✅ CV y credenciales

---

**Autor:** Marcos Alvarado
**Repositorio:** github.com/MarcosAlvaradoD/ai-job-foundry
