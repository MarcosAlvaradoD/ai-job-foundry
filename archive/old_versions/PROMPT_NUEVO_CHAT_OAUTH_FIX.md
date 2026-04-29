# 🚨 PROMPT PARA NUEVO CHAT - AI JOB FOUNDRY

**COPIAR TODO ESTO en el nuevo chat de Claude:**

---

# CONTEXTO DEL PROYECTO

Soy Marcos Alvarado, Project Manager/Business Analyst de Guadalajara, México. Estoy desarrollando **AI Job Foundry**, un sistema automatizado de búsqueda de empleo que:

1. Scrapea ofertas (LinkedIn, Indeed, Glassdoor)
2. Procesa emails de reclutadores con Gmail API
3. Analiza match con AI local (LM Studio + Qwen 2.5 14B)
4. Calcula FIT SCORES (0-10)
5. Guarda en Google Sheets
6. Verifica URLs con Playwright (detecta expirados)
7. Auto-aplica a ofertas (próximamente)

**Ubicación del proyecto:** `C:\Users\MSI\Desktop\ai-job-foundry`

---

## 🚨 PROBLEMA ACTUAL (URGENTE)

### Error OAuth Token
```
Checking OAuth token... MISSING
[ERROR] No se encontró credentials.json
Ubicación esperada: C:\Users\MSI\Desktop\ai-job-foundry\scripts\oauth\data\credentials\credentials.json
```

**Consecuencia:**
- ❌ No puede leer Gmail (emails de reclutadores)
- ❌ No puede leer/escribir Google Sheets (tracking de jobs)
- ❌ Pipeline completo falla

### Lo que ya intenté:
```powershell
py fix_oauth_scopes.py          # Error: No such file
py \scripts\oauth\fix_oauth_scopes.py   # Error: No such file
```

---

## ✅ TRABAJO COMPLETADO EN SESIÓN ANTERIOR

### 1. LinkedIn Smart Verifier V3 (100% FUNCIONAL)
Creado `LINKEDIN_SMART_VERIFIER_V3.py` con:
- ✅ Login automático sin bloqueos (sin `input()`)
- ✅ Cookies persistentes (`data/linkedin_cookies.json`)
- ✅ 32 patrones de detección (16 EXPIRED + 16 ACTIVE)
- ✅ Manejo de checkpoints (30 segundos automáticos)
- ✅ Modo debug para analizar UNKNOWNs

**Resultados de pruebas:**
- Primera ejecución: Login exitoso, cookies guardadas
- Segunda ejecución: Session válida, sin login
- 28 jobs verificados: 46.4% EXPIRED, 39.3% ACTIVE, 14.3% UNKNOWN

### 2. Pipeline integrado
Modificado `run_daily_pipeline.py` para usar V3:
```python
from LINKEDIN_SMART_VERIFIER_V3 import LinkedInSmartVerifierV3
```

### 3. Control Center actualizado
Opción 7 mejorada con submenú por plataforma:
1. LinkedIn (con login automático)
2. Indeed
3. Glassdoor
4. Todas las plataformas

---

## 🎯 LO QUE NECESITO AHORA

### Tarea 1: Arreglar OAuth (URGENTE)
Necesito regenerar el token de Google OAuth para:
- Gmail API (leer emails de reclutadores)
- Google Sheets API (leer/escribir jobs)

**Cuenta Google:** markalvati@gmail.com

### Tarea 2: Validar sistema completo
Una vez arreglado OAuth:
1. Probar opción 7 del Control Center (LinkedIn V3)
2. Probar pipeline completo (opción 1)
3. Verificar que Google Sheets se actualice

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ai-job-foundry/
├── LINKEDIN_SMART_VERIFIER_V3.py      # ✅ Nuevo (funcional)
├── GLASSDOOR_SMART_VERIFIER.py        # ✅ Funcional
├── INDEED_SMART_VERIFIER.py           # ✅ Funcional
├── run_daily_pipeline.py              # ✅ Actualizado con V3
├── control_center.py                  # ✅ Actualizado opción 7
├── data/
│   ├── credentials/
│   │   ├── credentials.json           # ❌ FALTA (problema OAuth)
│   │   └── token.json                 # ❌ Expirado
│   └── linkedin_cookies.json          # ✅ Generado por V3
├── core/
│   ├── sheets/
│   │   └── sheet_manager.py           # Necesita OAuth
│   └── automation/
│       └── gmail_jobs_monitor.py      # Necesita OAuth
└── scripts/
    └── oauth/                         # ❌ Ruta confusa
```

---

## 🔑 CREDENCIALES Y CONFIGURACIÓN

### .env actual
```
LINKEDIN_EMAIL=markalvati@gmail.com
LINKEDIN_PASSWORD=4&nxXdJbaL["Rax*C!8e"4P5
GMAIL_ADDRESS=markalvati@gmail.com
GOOGLE_SHEETS_ID=1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
```

### URLs importantes
- Google Sheets: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
- LM Studio: http://172.23.0.1:11434 (o 127.0.0.1:11434)

---

## 📚 DOCUMENTACIÓN CREADA

1. `LINKEDIN_VERIFIER_V3_QUICKSTART.md` - Guía de uso de V3
2. `RESUMEN_SESION_LINKEDIN_V3.md` - Resumen técnico completo
3. `RESUMEN_INTEGRACION_CONTROL_CENTER.md` - Integración en menu
4. `GUIA_VERIFICACION_MULTIPLATAFORMA.md` - Sistema completo

---

## 🚀 ACCIÓN INMEDIATA REQUERIDA

**Por favor ayúdame a:**

1. **Encontrar/regenerar credentials.json**
   - ¿Dónde debe estar exactamente?
   - ¿Cómo lo descargo de Google Cloud Console?
   - ¿Qué scopes necesito?

2. **Regenerar token.json**
   - Script para autenticar con Google
   - Autorizar Gmail API + Sheets API
   - Guardar token válido

3. **Validar que todo funcione**
   - Ejecutar `py control_center.py`
   - Opción 7 → LinkedIn → 3 jobs
   - Confirmar que marca EXPIRED en Sheets

---

## 💡 CONTEXTO ADICIONAL

### Principios del proyecto:
- **Local-first AI:** LM Studio > Cloud (privacidad)
- **Set it and forget it:** Máxima automatización
- **Functional > Perfect:** Entregar features funcionando
- **Windows-optimized:** PowerShell scripts

### Tech Stack:
- Python 3.13 (comando: `py`)
- Playwright + Firefox para scraping
- LM Studio con Qwen 2.5 14B
- Google APIs (Gmail + Sheets)
- Windows 11 + PowerShell 7.5.4

---

## ❓ PREGUNTAS PARA ARRANCAR

1. ¿Ves algún archivo `credentials.json` en el proyecto usando Desktop Commander?
2. ¿Puedes guiarme para descargarlo de Google Cloud Console?
3. ¿Cuál es la estructura correcta de carpetas para OAuth?

---

**¡Gracias por la ayuda! Necesito arreglar OAuth URGENTE para que el sistema vuelva a funcionar.** 🙏
