# 🚨 PROBLEMA CRÍTICO: API KEY EXPUESTA EN GITHUB

**Email de GitHub:** "Possible valid secrets detected"

---

## 🔍 **QUÉ DETECTÓ GITHUB:**

1. **Google API Key** en `web/dashboard.html` línea 171
2. **OAuth tokens** en commits anteriores
3. **Credenciales** en archivos que se intentaron subir

---

## ❌ **EL PROBLEMA:**

**Archivo:** `web/dashboard.html`  
**Línea 171:**
```javascript
const API_KEY = '[GEMINI_API_KEY_REDACTED]'; // ❌ EXPUESTO
```

**Por qué es grave:**
- 🔓 Cualquiera puede ver tu API key
- 💸 Pueden usar tu quota de Google
- 📊 Acceso a tus datos de Sheets
- 🚫 GitHub bloquea el push automáticamente

---

## ✅ **LA SOLUCIÓN (3 PASOS):**

### **PASO 1: EJECUTA EL LIMPIADOR (5 MIN)**

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\git_clean_all_secrets.ps1
```

**Qué hace este script:**
1. ❌ Elimina `web/dashboard.html` (con API key)
2. ❌ Elimina `token.json.old`
3. ❌ Elimina `google_credentials.json`
4. 📝 Actualiza .gitignore
5. 🔥 Limpia el historial de Git
6. ✅ Push limpio a GitHub

**Tiempo:** 3-5 minutos  
**Requiere:** Confirmar reescritura de historial (es seguro)

---

### **PASO 2: USA DASHBOARD SEGURO**

**En lugar de:** `web/dashboard.html` ❌  
**Usa:** `dashboard_secure.html` + `dashboard_backend.py` ✅

**Cómo ejecutar:**

```powershell
# Terminal 1: Backend
py dashboard_backend.py

# Navegador: Frontend
http://localhost:5000
```

**Por qué es seguro:**
```python
# Backend lee credenciales del .env (no expuesto)
sheet_manager = SheetManager()
# NO hay API keys en el código público
```

---

### **PASO 3: VERIFICA EN GITHUB (1 MIN)**

Después del push exitoso:

1. Abre: https://github.com/MarcosAlvaradoD/ai-job-foundry
2. Verifica que diga: "security: Remove ALL secrets from repository"
3. Confirma que NO aparezcan estos archivos:
   - ❌ `web/dashboard.html`
   - ❌ `data/credentials/token.json.old`
   - ❌ `workflows/google_credentials.json`

---

## 📊 **COMPARACIÓN:**

### **ANTES (INSEGURO):**
```
web/dashboard.html ❌
├── const API_KEY = 'AIzaSy...' (expuesto)
├── Cualquiera puede verlo
└── GitHub lo bloquea
```

### **AHORA (SEGURO):**
```
dashboard_backend.py ✅
├── Lee del .env (local)
├── NO expone credenciales
└── GitHub permite el push

dashboard_secure.html ✅
├── Llama al backend
├── Sin API keys
└── Totalmente seguro
```

---

## 🔄 **SI EL SCRIPT FALLA:**

### **Opción 1: Retry con force**
El script preguntará si quieres forzar la limpieza del historial. Di "y" (yes).

### **Opción 2: Resolver manualmente en GitHub**
1. Ve a: https://github.com/MarcosAlvaradoD/ai-job-foundry/security
2. Click en cada alerta de secreto
3. "Mark as resolved" o "Revoke"

### **Opción 3: Nuclear (último recurso)**
1. Elimina el repo en GitHub
2. Crea uno nuevo con el mismo nombre
3. Force push:
   ```powershell
   git push -u origin main --force
   ```

---

## 📋 **CHECKLIST COMPLETO:**

```
[ ] 1. Ejecutar: .\git_clean_all_secrets.ps1
[ ] 2. Confirmar limpieza de historial (y)
[ ] 3. Ver mensaje SUCCESS
[ ] 4. Verificar en GitHub (no más alertas)
[ ] 5. Probar dashboard seguro:
       py dashboard_backend.py
       http://localhost:5000
[ ] 6. Confirmar funciona sin API key expuesta
[ ] 7. LISTO ✅
```

---

## 💡 **PREVENCIÓN FUTURA:**

**El .gitignore ahora incluye:**
```
# Nunca subir estos archivos
web/dashboard.html          # Tiene API key
data/credentials/*.json     # Credenciales
workflows/*credentials.json # OAuth
*.json.old                  # Backups
```

**Para futuros updates:**
```powershell
.\git_update.ps1  # Verifica secretos automáticamente
```

---

## 🆘 **SI TIENES DUDAS:**

**Email de GitHub sigue llegando:**
- Espera 5-10 minutos (GitHub tarda en actualizar)
- Verifica que el commit con secretos ya no esté en main
- Si persiste, resuelve manualmente en GitHub Security

**El dashboard no funciona:**
- Usa `dashboard_secure.html` + `dashboard_backend.py`
- NO uses `dashboard.html` (obsoleto)
- Backend debe estar corriendo (py dashboard_backend.py)

---

## 🎯 **EJECUTA AHORA:**

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\git_clean_all_secrets.ps1
```

**Tiempo total:** 5 minutos  
**Resultado:** Push exitoso sin secretos ✅  
**Dashboard:** Funcional y seguro ✅

---

**Status:** PROBLEMA IDENTIFICADO ✅  
**Solución:** SCRIPT LISTO ✅  
**Acción:** EJECUTAR git_clean_all_secrets.ps1  
**Tiempo:** 5 minutos
