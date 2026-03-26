# ⚡ FLUJO AUTOMÁTICO - OAuth Token Validator

## 🎯 ¿CÓMO FUNCIONA AHORA?

El sistema es **completamente automático**. Cuando ejecutas `main.py` o el pipeline:

### 1️⃣ Detecta Token Expirado
```
[INFO] 🔐 OAUTH TOKEN VALIDATOR
[WARNING] ⚠️  Token EXPIRADO. Renovando automáticamente...
```

### 2️⃣ Abre Navegador Automáticamente
```
[INFO] 🌐 Se abrirá tu navegador para autorizar la aplicación
[INFO] Por favor completa la autorización en el navegador
[INFO] El pipeline continuará automáticamente después
```

### 3️⃣ Espera que Completes la Autorización
- Se abre tu navegador
- Inicias sesión en Google
- Autorizas los permisos (Gmail + Sheets)
- Cierras la pestaña

### 4️⃣ Verifica que el Nuevo Token Funciona
```
[INFO] ✅ Renovación completada exitosamente
[INFO] 🔍 Verificando que el nuevo token funciona...
[INFO] ✅ Nuevo token es válido
```

### 5️⃣ Continúa con el Pipeline Automáticamente
```
[INFO] ✅ LISTO PARA CONTINUAR
[INFO] ✅ Token OAuth validado. Iniciando pipeline...
[INFO] PASO 1: Procesando emails...
```

---

## 🚀 PRUEBA RÁPIDA

### Test del Flujo Automático

```powershell
# Opción 1: Test standalone
py oauth_token_validator.py

# Opción 2: Test con script PowerShell
.\TEST_OAUTH_FLOW.ps1

# Opción 3: Test con pipeline completo
py main.py
```

---

## ✅ LO QUE CAMBIASTE

### ANTES ❌ (Manual)
1. Pipeline se rompe con error de token
2. Tienes que ejecutar manualmente: `py scripts\oauth\reauthenticate_gmail_v2.py`
3. Abrir navegador, autorizar
4. Volver a ejecutar pipeline

### AHORA ✅ (Automático)
1. Pipeline detecta token expirado
2. **Abre navegador AUTOMÁTICAMENTE**
3. Espera que autorices
4. Verifica que funciona
5. **Continúa automáticamente** con el pipeline

---

## 🧪 EJEMPLO DE EJECUCIÓN

```powershell
PS> py main.py

======================================================================
🚀 AI JOB FOUNDRY - MAIN PIPELINE
======================================================================

PASO 0: Validando token OAuth...

======================================================================
🔐 OAUTH TOKEN VALIDATOR
======================================================================
⚠️  Token EXPIRADO. Renovando automáticamente...

🌐 Se abrirá tu navegador para autorizar la aplicación
   Por favor completa la autorización en el navegador
   El pipeline continuará automáticamente después

🔄 Ejecutando renovación de token...
   Script: C:\...\scripts\oauth\reauthenticate_gmail_v2.py

⏳ ESPERANDO que completes la autorización en el navegador...
   (Esto puede tomar 1-2 minutos)

----------------------------------------------------------------------
✅ Renovación completada exitosamente

🔍 Verificando que el nuevo token funciona...
✅ Nuevo token es válido

======================================================================
✅ LISTO PARA CONTINUAR
======================================================================

✅ Token OAuth validado. Iniciando pipeline...

PASO 1: Procesando emails...
✅ Emails procesados

PASO 2: Procesando boletines...
✅ Boletines procesados

...
```

---

## 💡 NOTAS IMPORTANTES

### ¿Qué Pasa en el Navegador?

1. Se abre Google OAuth
2. Te pide iniciar sesión (si no estás logueado)
3. Muestra los permisos que necesita:
   - ✅ Gmail (leer/modificar)
   - ✅ Google Sheets (leer/escribir)
4. Haces clic en "Permitir"
5. Muestra "Autenticación exitosa! Puedes cerrar esta ventana"
6. El pipeline continúa automáticamente

### Tiempo de Espera

- Máximo: **2 minutos** (120 segundos)
- Si no autorizas en ese tiempo, el script te lo dice
- Puedes ejecutar manual: `py scripts\oauth\reauthenticate_gmail_v2.py`

### ¿Qué Hace con el Token Viejo?

- Lo elimina automáticamente
- Genera uno nuevo
- Verifica que funciona
- Solo entonces continúa

---

## 🆘 SI ALGO FALLA

### Error: "Renovación falló con código 1"

**Solución:**
```powershell
# Ejecutar manual para ver el error exacto
py scripts\oauth\reauthenticate_gmail_v2.py
```

### Error: "Renovación excedió tiempo límite"

**Causa:** No completaste la autorización en 2 minutos

**Solución:**
```powershell
# Ejecutar de nuevo, esta vez más rápido
py oauth_token_validator.py --force
```

### Error: "Nuevo token no es válido"

**Solución:**
```powershell
# Verificar credentials.json
ls data\credentials\credentials.json

# Si no existe, descárgalo de Google Cloud Console
# y colócalo en data\credentials\
```

---

## ✅ RESULTADO FINAL

Después de esto:
- ✅ **Nunca más** tendrás que renovar manualmente
- ✅ El pipeline detecta y renueva **automáticamente**
- ✅ Solo necesitas **autorizar en el navegador** (1 vez cuando expire)
- ✅ Todo lo demás es **100% automático**

**Sistema verdaderamente "set it and forget it"** 🚀

---

**Autor:** Marcos Alberto Alvarado  
**Fecha:** 2026-01-02  
**Versión:** 2.0 (Flujo Automático Completo)
