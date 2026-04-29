# 🔴 OAUTH TOKEN EXPIRADO - GUÍA COMPLETA

**Fecha:** 2025-11-29  
**Error:** `invalid_grant: Token has been expired or revoked.`

---

## 🎯 RESUMEN EJECUTIVO

**Problema:** Token OAuth de Google expiró  
**Causa:** Normal - Los tokens expiran cada 7-30 días  
**Solución:** Re-autenticar (2 minutos)  
**¿Movimos algo?** NO - Es proceso normal de Google

---

## ❌ ERROR DETECTADO

```
google.auth.exceptions.RefreshError: 
  invalid_grant: Token has been expired or revoked.
```

**Afecta:**
- ❌ Email processing (Gmail)
- ❌ Google Sheets access
- ❌ AI Analysis (necesita Sheets)
- ❌ Report generation (necesita Sheets)

---

## ❓ ¿POR QUÉ PASÓ?

### Razones comunes:
1. **Token expiró naturalmente** (7-30 días sin uso)
2. **Google revocó por seguridad** (login desde nuevo lugar)
3. **Cambiaste contraseña** de Google
4. **No usaste el sistema** por varios días

### ¿Es culpa nuestra?
**NO** - Este es un comportamiento NORMAL de OAuth.

Los tokens OAuth:
- ✅ Expiran por seguridad
- ✅ Requieren renovación periódica
- ✅ Es política de Google, no bug del código

---

## ✅ SOLUCIÓN (2 MINUTOS)

### OPCIÓN 1: Script Automático (RECOMENDADO)
```powershell
FIX_OAUTH_TOKEN.bat
```

**Qué hace:**
1. Elimina token viejo
2. Abre Google OAuth en navegador
3. Te pide login + permisos
4. Genera token nuevo
5. ✅ LISTO

### OPCIÓN 2: Manual
```powershell
py fix_oauth_complete.py
```

**Pasos:**
1. Se abre navegador
2. Login con tu Gmail
3. Acepta TODOS los permisos
4. Espera "Success"

---

## 📋 PASOS DETALLADOS

### 1. Ejecutar Fix
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
FIX_OAUTH_TOKEN.bat
```

### 2. En el navegador:
- Selecciona tu cuenta de Gmail
- Acepta TODOS los permisos:
  - ✅ Ver/editar Google Sheets
  - ✅ Leer emails
  - ✅ Modificar labels de Gmail
  - ✅ Crear labels
  - ✅ Enviar emails (futuro)
  - ✅ Acceder Calendar (futuro)

### 3. Verificar
```powershell
START_UNIFIED_APP.bat
```

Ejecuta opción 1 (Pipeline Completo)

**Debe mostrar:**
```
✅ Email Processing     PASS
✅ AI Analysis          PASS
✅ Expire Check         PASS
✅ Report               PASS
```

---

## 🔍 ¿MOVIMOS ALGO EN LA SESIÓN ANTERIOR?

### RESPUESTA: NO

**Lo que hicimos ayer:**
- ✅ Arreglamos `startup_check_v3.ps1`
- ✅ Creamos `setup_wizard_complete.py`
- ✅ Creamos instaladores silenciosos
- ✅ Documentación

**NO tocamos:**
- ❌ OAuth configuration
- ❌ Token files
- ❌ Google API credentials
- ❌ Nada relacionado con autenticación

**Conclusión:** El token expiró por tiempo, no por cambios en código.

---

## 🛡️ PREVENIR EN EL FUTURO

### Opción 1: Uso Regular
**Ejecutar sistema cada 2-3 días**
- Tokens se auto-renuevan con uso frecuente
- Google ve actividad constante
- No requiere re-login manual

### Opción 2: Service Account (Avanzado)
**Token que NO expira**

Requisitos:
- Google Workspace (no Gmail personal)
- Configuración en Google Cloud Console
- Más complejo pero permanente

Pasos:
1. Google Cloud Console
2. Create Service Account
3. Download JSON key
4. Share Sheet/Gmail con service account email

### Opción 3: Monitoreo Automático
**Script que detecta expiración**

Creamos script que:
- Chequea token antes de ejecutar
- Auto-renueva si es posible
- Alerta si requiere re-login

---

## 📊 ARCHIVOS INVOLUCRADOS

### Token (expira)
```
data/credentials/token.json
```
- Contiene: access_token, refresh_token
- Duración: 7-30 días
- Renovable: Sí (a veces requiere re-login)

### Credentials (permanente)
```
data/credentials/credentials.json
```
- Contiene: client_id, client_secret
- Duración: Permanente
- Descargado de: Google Cloud Console

### Scopes (permisos)
```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]
```

---

## 🚨 TROUBLESHOOTING

### Si FIX_OAUTH_TOKEN.bat falla:

**Error 1: credentials.json not found**
```
Solución:
1. Ir a Google Cloud Console
2. Credentials > OAuth 2.0 Client IDs
3. Download JSON
4. Copiar a data/credentials/credentials.json
```

**Error 2: Browser doesn't open**
```
Solución:
1. Copiar URL del terminal
2. Pegar en navegador manualmente
3. Completar login
4. Copiar código de autorización
```

**Error 3: Permission denied**
```
Solución:
1. Verificar cuenta de Google
2. Aceptar TODOS los permisos
3. No denegar ninguno
```

---

## 📈 DESPUÉS DE ARREGLAR

### Verificación completa:
```powershell
# 1. Check token existe
dir data\credentials\token.json

# 2. Start app
START_UNIFIED_APP.bat

# 3. Run pipeline
Opción 1 (Pipeline Completo)
```

### Expected output:
```
[2025-11-29 XX:XX:XX] ✅ Email processing completed
[2025-11-29 XX:XX:XX] ✅ AI analysis completed
[2025-11-29 XX:XX:XX] ✅ Expire check completed
[2025-11-29 XX:XX:XX] ✅ Report generated

PIPELINE SUMMARY
Email Processing     ✅ PASS
AI Analysis          ✅ PASS
Auto-Apply           ✅ PASS
Expire Check         ✅ PASS
Report               ✅ PASS
```

---

## 💡 PREGUNTAS FRECUENTES

### ¿Cada cuánto pasa esto?
- Con uso regular (cada 2-3 días): Casi nunca
- Sin uso (semanas): Cada 7-30 días
- Depende de políticas de Google

### ¿Pierdo datos?
- NO - Datos en Google Sheets están seguros
- Solo necesitas re-autorizar acceso

### ¿Afecta otros usuarios?
- NO - Token es por usuario
- Cada quien tiene su token

### ¿Solución permanente?
- Service Account (Google Workspace)
- O uso regular del sistema

---

## 🎯 COMANDOS RÁPIDOS

```powershell
# Fix OAuth (recomendado)
FIX_OAUTH_TOKEN.bat

# Fix manual
py fix_oauth_complete.py

# Verificar token existe
dir data\credentials\token.json

# Start app
START_UNIFIED_APP.bat

# Test pipeline
py run_daily_pipeline.py --all
```

---

## 📞 SOPORTE

Si después de arreglar OAuth sigue fallando:

1. **Verificar credentials.json existe**
2. **Verificar token.json fue creado**
3. **Revisar que aceptaste TODOS los permisos**
4. **Intentar con otra cuenta de Google**
5. **Revisar logs en logs/powershell/**

---

**Autor:** Marcos Alberto Alvarado de la Torre  
**Proyecto:** AI Job Foundry  
**Versión:** 2.0  
**Fecha:** 2025-11-29
