# 🔧 FIX OAUTH SCOPES - CRITICAL

**Problema identificado:** Los OAuth tokens tienen scopes incorrectos causando:
```
google.auth.exceptions.RefreshError: ('invalid_scope: Bad Request')
```

## 🎯 SOLUCIÓN RÁPIDA (5 minutos)

### Paso 1: Borrar Tokens Viejos
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry\data\credentials
del token.json
del gmail-token.json
```

### Paso 2: Re-autenticar Gmail
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py scripts\oauth\reauthenticate_gmail.py
```

**Qué va a pasar:**
1. Se abre navegador
2. Login con markalvati@gmail.com
3. Acepta permisos (Gmail + Sheets)
4. Token nuevo se guarda automáticamente

### Paso 3: Verificar Funciona
```powershell
.\START_CONTROL_CENTER.bat
# Debería mostrar: "Checking OAuth Token... OK"
```

## 🔍 CAUSA DEL PROBLEMA

El código antiguo tenía scopes limitados:
```python
# ANTES (limitado)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# AHORA (completo)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets"
]
```

Los tokens viejos NO tienen el scope `spreadsheets`, por eso falla CLEAN_INDEED_INVALID.

## ⚠️ NO NECESITAS EDITAR CÓDIGO

El script `reauthenticate_gmail.py` ya tiene los scopes correctos.
Solo necesitas:
1. Borrar tokens viejos
2. Re-autenticar
3. Listo

## 🎓 EXPLICACIÓN TÉCNICA

**Scopes** = Permisos que le das a la app.

Cuando cambias los scopes en el código pero ya tienes un `token.json` viejo:
- Token viejo: solo Gmail readonly
- Código nuevo: necesita Gmail + Sheets
- Google dice: "Este token no tiene permiso para Sheets" → `invalid_scope`

**Solución:** Borrar token viejo y generar uno nuevo con los scopes correctos.

---

**Después de esto, CLEAN_INDEED_INVALID.ps1 funcionará sin errores.**
