# 🔐 OAUTH AUTO-REFRESH SYSTEM

## 📋 Overview

El sistema de auto-refresh OAuth garantiza que todos los componentes de AI Job Foundry tengan acceso válido a Gmail API y Google Sheets API sin intervención manual.

---

## 🎯 Problema Resuelto

**ANTES:**
```
❌ Token expirado → Pipeline falla → Usuario debe correr manualmente reauthenticate_gmail_v2.py → Usuario vuelve a correr pipeline
```

**AHORA:**
```
✅ Token expirado → Sistema auto-detecta → Auto-refresh automático → Pipeline continúa sin interrupción
```

---

## 🔧 Componentes del Sistema

### 1. **oauth_validator.py** (Módulo Central)
- **Ubicación:** `core/utils/oauth_validator.py`
- **Funciones principales:**
  - `ensure_valid_oauth_token()` - Valida y refresh automático
  - `check_token_validity()` - Verifica estado del token
  - `run_reauthentication()` - Ejecuta script de re-auth

### 2. **run_daily_pipeline.py** (Integración)
- Valida OAuth **ANTES** de ejecutar cualquier operación
- Si falla → Exit con código 1 (previene errores en cascada)

### 3. **Test Suite**
- **Script:** `scripts/tests/test_oauth_validator.py`
- **PowerShell:** `TEST_OAUTH_VALIDATOR.ps1`
- Valida funcionamiento antes de usar en producción

---

## 📊 Flujo de Validación

```
┌─────────────────────────────────────────────────────┐
│  Pipeline Start (run_daily_pipeline.py)             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  ensure_valid_oauth_token()                         │
│  ↓                                                   │
│  1. Check token.json exists?                        │
│     ↓ NO → Run reauthenticate_gmail_v2.py          │
│     ↓ YES → Continue                                │
│                                                      │
│  2. Check token expiry datetime                     │
│     ↓ EXPIRED → Run reauthenticate_gmail_v2.py     │
│     ↓ VALID → Continue                              │
│                                                      │
│  3. Check token expires soon? (<5 min)              │
│     ↓ YES → Run reauthenticate_gmail_v2.py         │
│     ↓ NO → Token is VALID                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  IF VALID:                                          │
│  ✅ Continue with pipeline operations               │
│  - Email Processing                                 │
│  - Bulletin Processing                              │
│  - AI Analysis                                      │
│  - Auto-Apply                                       │
│  - Reporting                                        │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  IF INVALID:                                        │
│  ❌ Exit with error code 1                          │
│  - Display error message                            │
│  - Provide manual fix instructions                  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Uso del Sistema

### Opción 1: Testing Manual
```powershell
# Probar validación OAuth
.\TEST_OAUTH_VALIDATOR.ps1

# O directamente con Python
py scripts\tests\test_oauth_validator.py
```

### Opción 2: Integrado en Pipeline
```powershell
# Pipeline automáticamente valida OAuth al inicio
py run_daily_pipeline.py --all
```

### Opción 3: Uso Programático
```python
from core.utils.oauth_validator import ensure_valid_oauth_token

# En cualquier script que use Gmail/Sheets API
if not ensure_valid_oauth_token():
    print("OAuth validation failed")
    sys.exit(1)

# Ahora es seguro usar Gmail/Sheets
from core.sheets.sheet_manager import SheetManager
sheet_manager = SheetManager()
```

---

## 📂 Archivos del Sistema

### Core Module
```
core/
└── utils/
    ├── __init__.py
    └── oauth_validator.py  ← Módulo principal
```

### Test Scripts
```
scripts/
└── tests/
    └── test_oauth_validator.py  ← Suite de pruebas
```

### PowerShell Helpers
```
ai-job-foundry/
└── TEST_OAUTH_VALIDATOR.ps1  ← Test rápido desde raíz
```

### OAuth Credentials
```
data/
└── credentials/
    ├── credentials.json  ← OAuth client config
    └── token.json        ← Refresh token (auto-managed)
```

---

## ⚙️ Configuración

### 1. Obtener credentials.json
1. Visitar: https://console.cloud.google.com/
2. Crear proyecto (o usar existente)
3. Habilitar APIs:
   - Gmail API
   - Google Sheets API
4. Crear credenciales OAuth 2.0
5. Descargar JSON
6. Guardar como: `data/credentials/credentials.json`

### 2. Primera Autenticación
```powershell
# Generar token inicial
py scripts\oauth\reauthenticate_gmail_v2.py

# Se abrirá navegador para autorizar
# Aceptar TODOS los permisos solicitados
# Token se guarda en: data/credentials/token.json
```

### 3. Verificar Funcionamiento
```powershell
# Test completo
.\TEST_OAUTH_VALIDATOR.ps1

# Debería ver:
# ✅ OAuth token is VALID
# ✅ ALL TESTS PASSED
```

---

## 🐛 Troubleshooting

### Error: "Token file not found"
```powershell
# Solución: Correr primera autenticación
py scripts\oauth\reauthenticate_gmail_v2.py
```

### Error: "credentials.json not found"
```
Solución:
1. Obtener credentials.json de Google Cloud Console
2. Guardar en: data/credentials/credentials.json
3. Reintentar
```

### Error: "Token expired"
```
Solución automática:
- El sistema auto-refresh debería manejar esto
- Si falla, manual: py scripts\oauth\reauthenticate_gmail_v2.py
```

### Error: "invalid_grant"
```
Causa: OAuth client fue eliminado o revocado
Solución:
1. Crear nuevo OAuth client en Google Cloud Console
2. Descargar nuevo credentials.json
3. py scripts\oauth\reauthenticate_gmail_v2.py
4. Aceptar permisos nuevamente
```

---

## 📈 Ventajas del Sistema

### 1. **Automatic Recovery**
- Token expirado → Auto-refresh
- Sin intervención manual requerida

### 2. **Fail-Fast**
- Valida OAuth ANTES de operaciones costosas
- Previene errores en cascada

### 3. **Comprehensive Logging**
- Logs detallados de validación
- Mensajes claros de error
- Instrucciones de fix manual si auto-refresh falla

### 4. **Centralized Management**
- Un solo módulo para toda la app
- Fácil de mantener y actualizar

### 5. **Time Buffer Protection**
- Detecta tokens que expiran pronto (<5 min)
- Refresh preventivo antes de fallar

---

## 🔄 Ciclo de Vida del Token

```
Token Fresh (60+ min remaining)
    ↓
Token Valid (5-60 min remaining)
    ↓
Token Expiring Soon (<5 min)  ← AUTO-REFRESH HERE
    ↓
Token Expired                  ← ALSO AUTO-REFRESH HERE
    ↓
Token Refreshed (60 min new expiry)
```

---

## 📝 Notas de Implementación

### Token Expiry Format
El token usa formato ISO 8601 con timezone:
- `2025-01-02T14:47:10.123456Z` (UTC con Z)
- `2025-01-02T14:47:10.123456+00:00` (UTC con offset)

### Refresh Timeout
- Re-authentication script timeout: 5 minutos
- Tiempo suficiente para autorización manual en browser

### Scopes Requeridos
```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/spreadsheets'
]
```

---

## ✅ Checklist de Integración

Para integrar OAuth validator en un nuevo script:

- [ ] Agregar import: `from core.utils.oauth_validator import ensure_valid_oauth_token`
- [ ] Llamar al inicio: `if not ensure_valid_oauth_token(): sys.exit(1)`
- [ ] Validar que el script funciona: `py <script>.py`
- [ ] Agregar al PROJECT_STATUS.md si es crítico

---

## 📚 Referencias

- **Google OAuth 2.0:** https://developers.google.com/identity/protocols/oauth2
- **Gmail API:** https://developers.google.com/gmail/api
- **Google Sheets API:** https://developers.google.com/sheets/api

---

**Última actualización:** 2026-01-02  
**Autor:** Marcos Alberto Alvarado  
**Versión:** 1.0  
**Estado:** Production-Ready ✅
