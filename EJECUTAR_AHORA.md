# 🚀 EJECUCIÓN INMEDIATA - LinkedIn Auto-Apply V3

## ⚡ QUICK START (3 PASOS)

### 1️⃣ Abre PowerShell en la raíz del proyecto

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
```

### 2️⃣ Ejecuta el test

```powershell
.\test_linkedin_autoapply.ps1
```

### 3️⃣ Observa el navegador

- ✅ Se abrirá Chrome
- ✅ Navegará a LinkedIn
- ✅ Hará login automático con tus credenciales
- ✅ Intentará aplicar a jobs con FIT >= 7

---

## 📊 QUÉ VERÁS

### En la consola PowerShell:

```powershell
========================================
  LINKEDIN AUTO-APPLY V3 - TEST
========================================

[CHECK] Verifying LinkedIn credentials...
[OK] Email: markalvati@gmail.com
[OK] Password: ***********

[START] Running LinkedIn Auto-Apply V3...
[INFO] This is a DRY-RUN - no applications will be submitted

======================================================================
[AUTO-APPLY V3] LinkedIn Easy Apply with AUTO-LOGIN
[CONFIG] Dry-run: True | Max applies: 2 | Min FIT: 7
======================================================================

[SEARCH] Finding jobs with FIT >= 7...
[FOUND] 8 jobs ready for auto-apply

[PLAN] Found 8 jobs. Will process 2:
  1. Company A - Product Manager (FIT: 9/10)
  2. Company B - Project Manager (FIT: 8/10)

[DRY-RUN] This is a simulation. Forms will be analyzed but not submitted.

[START] Starting browser...

[SESSION] Checking LinkedIn session...
[INFO] Not logged in - will attempt auto-login

[LOGIN] Starting automatic LinkedIn login...
[INFO] Email: markalvati@gmail.com
[OK] Email entered
[OK] Password entered
[CLICK] Login button pressed
[SUCCESS] Login successful!
[OK] Saved 15 cookies to data/linkedin_cookies.json

[OK] Valid session active
[OK] LinkedIn session established - starting applications...

======================================================================
[APPLY] Company A - Product Manager
[FIT] 9/10 | Created: 2025-12-20
[URL] https://www.linkedin.com/jobs/view/...
======================================================================
[FOUND] Easy Apply button!
[DRY-RUN] Would click Easy Apply and fill form

======================================================================
[SUMMARY]
  ✅ Success: 2
  ❌ Failed: 0
  ⏭️  Skipped: 0
======================================================================

[SUCCESS] Test completed!
[OK] Cookies saved - next run will be faster!
```

---

## 🎯 SI TODO FUNCIONA

Verás:
1. ✅ "[SUCCESS] Login successful!"
2. ✅ "[OK] Saved X cookies to data/linkedin_cookies.json"
3. ✅ "[FOUND] X jobs ready for auto-apply"
4. ✅ Chrome abierto navegando en LinkedIn

**Siguiente paso:**
Editar `scripts/test_linkedin_autoapply_v3.py` y cambiar:
```python
dry_run=True  →  dry_run=False
```

---

## 🐛 SI HAY PROBLEMAS

### Problema 1: "LinkedIn credentials not found"
```powershell
# Verificar .env
Get-Content .env | Select-String "LINKEDIN"
```

Debe mostrar:
```
LINKEDIN_EMAIL=markalvati@gmail.com
LINKEDIN_PASSWORD=...
```

### Problema 2: "Login failed"
Causas posibles:
- ❌ Contraseña incorrecta
- 🔐 LinkedIn requiere verificación

Solución:
1. Login manual en navegador normal
2. Completa verificación si es necesaria
3. Reintenta el script

### Problema 3: "No high-FIT jobs found"
```powershell
# Verificar Google Sheets
py view_sheets_data.py
```

Debe haber jobs con FitScore >= 7

---

## 📁 ARCHIVOS CREADOS

```
✅ core/automation/linkedin_auto_apply.py (ACTUALIZADO V3)
✅ scripts/test_linkedin_autoapply_v3.py (NUEVO)
✅ test_linkedin_autoapply.ps1 (NUEVO)
✅ docs/LINKEDIN_AUTO_APPLY_V3.md (NUEVO)
✅ docs/IMPLEMENTACION_V3_RESUMEN.md (NUEVO)
✅ data/ (carpeta creada)
⚠️ data/linkedin_cookies.json (se creará al ejecutar)
```

---

## 🔄 EJECUCIONES FUTURAS

**Primera vez (HOY):**
- Login automático
- Guarda cookies
- ~3-5 minutos

**Siguientes veces:**
- Usa cookies guardadas
- NO hace login
- ~1-2 minutos

---

## 📞 AYUDA RÁPIDA

**Ver documentación completa:**
```powershell
notepad docs\LINKEDIN_AUTO_APPLY_V3.md
```

**Ver implementación:**
```powershell
notepad docs\IMPLEMENTACION_V3_RESUMEN.md
```

**Ver estado del proyecto:**
```powershell
notepad PROJECT_STATUS.md
```

---

## ✅ CHECKLIST PRE-EJECUCIÓN

- [✅] Estoy en: `C:\Users\MSI\Desktop\ai-job-foundry`
- [✅] Existe: `.env` con credenciales
- [✅] LM Studio está corriendo (para ver datos de Sheets)
- [✅] Google Sheets tiene jobs con FIT >= 7
- [✅] Tengo 5 minutos para observar

---

## 🎬 EJECUTA AHORA

```powershell
# Copiar y pegar:
cd C:\Users\MSI\Desktop\ai-job-foundry
.\test_linkedin_autoapply.ps1
```

**¡Listo! El script hará todo automáticamente.**

---

**Fecha:** 2025-12-24  
**Versión:** V3 (Auto-Login)  
**Tiempo estimado:** 3-5 minutos primera vez, 1-2 minutos siguientes
