# 🔐 GUÍA: CUENTAS GMAIL Y OAUTH

**Última actualización:** 2025-11-19 16:45 CST

---

## 📧 TUS DOS CUENTAS

### 1. fbmark@gmail.com
**¿Qué tiene?**
- OAuth client antiguo (ahora ELIMINADO)
- credentials.json apunta a esta cuenta

**¿Para qué se usaba?**
- Era la cuenta configurada en OAuth
- Pero NO recibe emails de job boards

**¿Necesitas migrar algo?**
- ❌ NO - El OAuth client fue eliminado
- Solo necesitas crear uno NUEVO con la cuenta correcta

---

### 2. markalvati@gmail.com ⭐ CUENTA CORRECTA
**¿Qué tiene?**
- Emails de LinkedIn Job Alerts
- Emails de Indeed Job Alerts  
- Emails de Glassdoor Job Alerts
- Emails de reclutadores

**¿Para qué debe usarse?**
- ✅ Recibir job board emails (ya lo hace)
- ✅ OAuth authentication (DEBES configurar)
- ✅ Google Sheets access
- ✅ Todo el sistema AI Job Foundry

---

## 🚨 PROBLEMA ACTUAL

```
credentials.json → OAuth Client (ELIMINADO) → fbmark@gmail.com
                                               ❌ Cuenta equivocada
                                               ❌ Client eliminado

Emails de jobs → markalvati@gmail.com
                 ✅ Aquí llegan los emails
                 ❌ Pero OAuth no configurado
```

---

## ✅ SOLUCIÓN

### OPCIÓN A: Guía Automática (RECOMENDADO) ⭐

```powershell
py setup_oauth_helper.py
```

Este script te guiará paso a paso para:
1. Crear OAuth client NUEVO en Google Cloud
2. Configurarlo para **markalvati@gmail.com**
3. Descargar credentials.json nuevo
4. Reemplazar el antiguo
5. Re-autenticar

**Tiempo:** 10-15 minutos siguiendo los pasos

---

### OPCIÓN B: Manual Rápido

**PASO 1:** Ve a https://console.cloud.google.com/
- Inicia sesión con: **markalvati@gmail.com**

**PASO 2:** Habilitar APIs
- Gmail API → HABILITAR
- Google Sheets API → HABILITAR

**PASO 3:** Crear OAuth Client
1. APIs y servicios → Credenciales
2. CREAR CREDENCIALES → ID de cliente OAuth 2.0
3. Tipo: Aplicación de escritorio
4. Nombre: "AI Job Foundry"
5. CREAR → DESCARGAR JSON

**PASO 4:** Reemplazar archivo
```powershell
# Archivo descargado:
client_secret_XXXXX.json

# Copiar a:
C:\Users\MSI\Desktop\ai-job-foundry\data\credentials\credentials.json

# Reemplazar el antiguo
```

**PASO 5:** Re-autenticar
```powershell
py reauthenticate_gmail.py
# ⚠️ SELECCIONA: markalvati@gmail.com
# ✅ Acepta todos los permisos
```

---

## 🔍 ¿QUÉ HAY EN FBMARK?

Según tu .env anterior:
```
LINKEDIN_EMAIL=markalvati@gmail.com  # LinkedIn usa markalvati
GMAIL_ADDRESS=markalvati@gmail.com   # Gmail usa markalvati
```

**Pero credentials.json apuntaba a fbmark** → Configuración inconsistente

**Conclusión:**
- fbmark solo tenía el OAuth client (ahora eliminado)
- Todos los emails siempre fueron a markalvati
- Solo necesitas OAuth nuevo con markalvati

---

## 📊 CHECKLIST DE MIGRACIÓN

- [ ] Ejecutar: `py setup_oauth_helper.py`
- [ ] Seguir pasos para crear OAuth nuevo
- [ ] Descargar credentials.json nuevo
- [ ] Reemplazar en: `data/credentials/credentials.json`
- [ ] Verificar .env tiene `markalvati@gmail.com`
- [ ] Ejecutar: `py reauthenticate_gmail.py`
- [ ] Seleccionar: **markalvati@gmail.com** en navegador
- [ ] Aceptar todos los permisos
- [ ] Probar: `py process_bulletins.py`
- [ ] Verificar: `py control_center.py` → Opción 1

---

## 💡 TIPS IMPORTANTES

### Al crear OAuth nuevo:
1. **SIEMPRE** usa markalvati@gmail.com
2. Habilita Gmail API + Google Sheets API
3. Configura "Aplicación de escritorio" (NO web)
4. Agrega markalvati@gmail.com como "usuario de prueba"

### Al autenticar:
1. **SELECCIONA** markalvati@gmail.com en el navegador
2. Si aparece fbmark, cambia de cuenta
3. Acepta **TODOS** los permisos (4 scopes)
4. Espera "Autenticación exitosa"

### Verificación final:
```powershell
# Verifica que token.json fue creado
ls data\credentials\token.json

# Debe existir y ser reciente (fecha de hoy)
```

---

## 🚫 ERRORES COMUNES

### Error: "deleted_client"
**Causa:** OAuth client fue eliminado
**Solución:** Crear OAuth client nuevo (esta guía)

### Error: "access_denied"
**Causa:** No aceptaste todos los permisos
**Solución:** Re-autenticar y aceptar TODO

### Error: Seleccioné fbmark por accidente
**Causa:** Navegador tenía fbmark como default
**Solución:** 
1. Elimina token.json
2. Ejecuta `py reauthenticate_gmail.py` de nuevo
3. En navegador, click en "Usar otra cuenta"
4. Selecciona markalvati

---

## 📞 REFERENCIAS

**Google Cloud Console:**
https://console.cloud.google.com/

**Gmail API:**
https://console.cloud.google.com/apis/library/gmail.googleapis.com

**Sheets API:**
https://console.cloud.google.com/apis/library/sheets.googleapis.com

**Credenciales:**
https://console.cloud.google.com/apis/credentials

---

## 🎯 RESUMEN EJECUTIVO

**Situación actual:**
- fbmark: Tenía OAuth eliminado ❌
- markalvati: Recibe emails pero sin OAuth ✅❌

**Solución:**
```powershell
py setup_oauth_helper.py  # Guía paso a paso
```

**Resultado esperado:**
- markalvati: Recibe emails + OAuth configurado ✅✅
- Sistema completo funcional ✅

**Tiempo total:** 10-15 minutos

---

**Próximo paso inmediato:**
```powershell
py setup_oauth_helper.py
```

Sigue los pasos del helper y estarás listo.
