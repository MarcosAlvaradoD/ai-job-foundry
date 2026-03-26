# 🔐 SEGURIDAD DE CREDENCIALES - AI JOB FOUNDRY

**Fecha:** 2025-12-12 02:15  
**Estado:** ✅ TODO PROTEGIDO

---

## 📋 RESUMEN EJECUTIVO

**Pregunta:** ¿Las credenciales de LinkedIn se suben a GitHub?  
**Respuesta:** ❌ **NO**. Todo está protegido en `.gitignore`

**Sistema LinkedIn:**
- NO guarda username/password ✅
- Solo guarda **cookies de sesión** (42 cookies)
- Cookies se regeneran cada login
- Cookies **NO** se suben a GitHub

---

## 🗂️ ARCHIVOS PROTEGIDOS (.gitignore)

### Google OAuth
```
data/credentials/credentials.json  ❌ GitHub
data/credentials/token.json        ❌ GitHub
```

**Contenido:**
- `credentials.json` - OAuth Client ID (permanente, descargado de Google Cloud)
- `token.json` - Access Token (temporal, se regenera cada OAuth)

### LinkedIn Session
```
data/linkedin_cookies.json  ❌ GitHub
```

**Contenido:**
- 42 cookies de sesión de LinkedIn
- Se generan al hacer login manual primera vez
- Válidas por ~30 días (LinkedIn decide)
- Se regeneran automáticamente si expiran

### Environment Variables
```
.env  ❌ GitHub
```

**Contenido:**
```bash
GOOGLE_SHEETS_ID=1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
LM_STUDIO_BASE_URL=http://127.0.0.1:11434
GEMINI_API_KEY=...
```

### Personal Data
```
data/cv_descriptor.txt      ❌ GitHub
data/cover_letters/         ❌ GitHub
data/marcos_*.txt           ❌ GitHub
data/job_applications.json  ❌ GitHub
```

---

## 🔍 SISTEMA DE COOKIES LINKEDIN

### Cómo Funciona

**Primera Ejecución:**
```
1. Usuario ejecuta: py scripts\verifiers\LINKEDIN_SMART_VERIFIER_V3.py
2. Se abre navegador Playwright (Firefox)
3. Usuario hace login MANUAL en LinkedIn
4. Script detecta login exitoso
5. Script guarda 42 cookies en linkedin_cookies.json
6. Navegador se cierra
```

**Siguientes Ejecuciones:**
```
1. Usuario ejecuta verificador LinkedIn
2. Script lee linkedin_cookies.json
3. Script carga cookies en navegador
4. Navegador tiene sesión activa ✅
5. NO necesita login manual
6. Verifica jobs directamente
```

### Ventajas del Sistema

| Característica | Beneficio |
|----------------|-----------|
| Sin credenciales | No guarda username/password |
| Session-based | Como navegador normal |
| Auto-refresh | Se regenera si expira |
| Seguro | Solo cookies, no datos sensibles |
| Rápido | No login cada vez (ahorra 30s) |

### Estructura de linkedin_cookies.json

```json
[
  {
    "name": "li_at",
    "value": "AQEDAR...",
    "domain": ".linkedin.com",
    "path": "/",
    "expires": 1744156800,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "JSESSIONID",
    "value": "ajax:1234567890",
    "domain": ".www.linkedin.com",
    "path": "/",
    ...
  },
  ... (40 más cookies)
]
```

**Cookie más importante:** `li_at` - Token de autenticación principal

---

## ⚙️ RENOVACIÓN DE COOKIES

### Cuando Expiran las Cookies

LinkedIn decide cuando expiran (típicamente ~30 días). Síntomas:

```
❌ Failed to load session
❌ Redirected to /uas/login-submit
❌ Need to login again
```

### Cómo Regenerar

**Método 1: Automático (Recomendado)**
```
El verifier detecta cookies expiradas automáticamente:
1. Intenta cargar cookies
2. Detecta que falló
3. Borra linkedin_cookies.json
4. Abre navegador para login manual
5. Guarda nuevas cookies
```

**Método 2: Manual**
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
Remove-Item data\linkedin_cookies.json -Force
py scripts\verifiers\LINKEDIN_SMART_VERIFIER_V3.py
# Hace login manual cuando lo pida
```

---

## 🚨 QUÉ PASA SI SE FILTRA linkedin_cookies.json

### Impacto

Si alguien obtiene tu `linkedin_cookies.json`:
- ✅ Puede acceder a tu LinkedIn temporalmente
- ✅ Solo hasta que las cookies expiren (~30 días)
- ❌ NO puede cambiar tu password
- ❌ NO puede ver datos de pago
- ❌ NO tiene acceso permanente

### Mitigación

1. **Cambiar password de LinkedIn** → Invalida todas las sesiones
2. **Cerrar todas las sesiones** → LinkedIn → Settings → Security → "Sign out of all sessions"
3. **Regenerar cookies** → Login manual nueva vez

---

## 🔒 BUENAS PRÁCTICAS DE SEGURIDAD

### ✅ Hacer Siempre

1. **Verificar .gitignore antes de commit:**
   ```powershell
   git status
   # Verificar que NO aparezcan:
   # - data/credentials/*.json
   # - data/linkedin_cookies.json
   # - .env
   ```

2. **Usar .env para secrets:**
   ```bash
   # ✅ BUENO
   GEMINI_API_KEY=xxx
   
   # ❌ MALO
   # Hardcodear en código: api_key = "xxx"
   ```

3. **Backups de credentials en lugar seguro:**
   ```
   C:\Users\MSI\Backups\ai-job-foundry\credentials\
   ❌ NO EN: GitHub, Google Drive público, Dropbox
   ✅ SÍ EN: USB encriptado, 1Password, Bitwarden
   ```

### ❌ Nunca Hacer

1. **NO compartir .env o credentials.json en Discord/Slack**
2. **NO subir a GitHub aunque sea repo privado**
3. **NO pegar API keys en screenshots/videos**
4. **NO enviar por email sin cifrar**

---

## 📊 ARCHIVOS EN GITHUB vs LOCAL

| Archivo | GitHub | Local | Qué es |
|---------|--------|-------|--------|
| `run_daily_pipeline.py` | ✅ | ✅ | Código público |
| `core/automation/*.py` | ✅ | ✅ | Código público |
| `.env` | ❌ | ✅ | Secrets |
| `credentials.json` | ❌ | ✅ | OAuth Client |
| `token.json` | ❌ | ✅ | OAuth Token |
| `linkedin_cookies.json` | ❌ | ✅ | Session cookies |
| `cv_descriptor.txt` | ❌ | ✅ | Datos personales |
| `.gitignore` | ✅ | ✅ | Protección |

---

## 🧪 CÓMO VERIFICAR PROTECCIÓN

### Test 1: Verificar .gitignore

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
Get-Content .gitignore | Select-String "linkedin_cookies"
```

**Resultado esperado:**
```
data/linkedin_cookies.json
```

### Test 2: Git Status

```powershell
git status
```

**Resultado esperado:** NO debe aparecer:
- ❌ `data/credentials/credentials.json`
- ❌ `data/credentials/token.json`
- ❌ `data/linkedin_cookies.json`
- ❌ `.env`

### Test 3: Verificar GitHub

1. Ir a: https://github.com/TU_USER/ai-job-foundry
2. Buscar archivo: `linkedin_cookies.json`
3. Resultado esperado: **404 Not Found** ✅

---

## 🔧 TROUBLESHOOTING

### Problema: "git add . agrega credenciales"

**Causa:** `.gitignore` no está funcionando

**Solución:**
```powershell
# Limpiar caché de Git
git rm -r --cached .
git add .
git commit -m "Fix .gitignore"
```

### Problema: "Subí credentials.json a GitHub por error"

**Solución CRÍTICA:**
```powershell
# 1. BORRAR del repo
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch data/credentials/credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# 2. FORZAR push
git push origin --force --all

# 3. REGENERAR credentials.json
# Ve a Google Cloud Console
# Borra el OAuth Client viejo
# Crea uno nuevo
# Descarga nuevo credentials.json
```

### Problema: "LinkedIn cookies no funcionan"

**Causa:** Cookies expiradas o LinkedIn detectó bot

**Solución:**
```powershell
# Regenerar cookies
Remove-Item data\linkedin_cookies.json -Force
py scripts\verifiers\LINKEDIN_SMART_VERIFIER_V3.py
# Login manual cuando lo pida
```

---

## 📈 CHECKLIST DE SEGURIDAD

### Antes de Git Push

- [ ] `git status` - No hay archivos sensibles
- [ ] `.gitignore` incluye todos los secrets
- [ ] `.env` NO aparece en staging
- [ ] `credentials.json` NO aparece
- [ ] `linkedin_cookies.json` NO aparece

### Después de Clonar Repo (Nueva PC)

- [ ] Crear `.env` manualmente
- [ ] Copiar `credentials.json` de backup
- [ ] Re-autenticar OAuth → Genera `token.json`
- [ ] Login LinkedIn manual → Genera `linkedin_cookies.json`
- [ ] Verificar que funciona

### Cada Mes

- [ ] Rotar API keys (Gemini, etc.)
- [ ] Verificar logs de acceso a Google Sheets
- [ ] Revisar sesiones activas en LinkedIn
- [ ] Backup de credentials en lugar seguro

---

## 🎯 RESUMEN FINAL

### ¿Qué SE SUBE a GitHub?

✅ **Código:**
- Scripts Python
- PowerShell scripts
- Documentación (README, docs/)
- .gitignore

### ¿Qué NO SE SUBE a GitHub?

❌ **Secrets:**
- Credenciales OAuth
- API Keys
- Cookies de sesión
- Datos personales (CV, cover letters)
- Logs con información sensible

### Sistema LinkedIn

**Pregunta:** ¿Dónde están las credenciales de LinkedIn?  
**Respuesta:** NO hay credenciales tradicionales

**En su lugar:**
- `linkedin_cookies.json` - Cookies de sesión (como navegador)
- Se generan al hacer login manual primera vez
- Se usan automáticamente después
- Expiran ~30 días, se regeneran automáticamente

**¿Es seguro?**
- ✅ SÍ - Protegido en `.gitignore`
- ✅ SÍ - NO se sube a GitHub
- ✅ SÍ - Temporal (expira automáticamente)
- ✅ SÍ - NO contiene password real

---

**Última actualización:** 2025-12-12 02:15  
**Estado:** ✅ TODO PROTEGIDO  
**Archivos sensibles:** 0 en GitHub  
**Nivel de seguridad:** ALTO
