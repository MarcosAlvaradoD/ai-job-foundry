# ⚠️ DASHBOARD VIEJO - NO USAR

**Este archivo tiene una API key de Google hardcoded y NO debe usarse.**

**GitHub lo detectó como secreto expuesto:** 
Línea 171: `const API_KEY = 'AIzaSy...'`

---

## ✅ USA EN SU LUGAR:

### **dashboard_secure.html + dashboard_backend.py**

**Backend (seguro):**
```powershell
py dashboard_backend.py
```

**Frontend:**
Abre en navegador: http://localhost:5000

---

## 🔒 POR QUÉ ES INSEGURO:

```javascript
// ❌ INSEGURO - API key expuesta públicamente
const API_KEY = '[GEMINI_API_KEY_REDACTED]';
```

Cualquiera con acceso al código puede:
- Ver tu API key
- Usar tu quota de Google Sheets API
- Acceder a tus datos
- GitHub lo bloquea automáticamente

---

## ✅ ALTERNATIVA SEGURA:

**Backend Python lee del .env:**
```python
# ✅ SEGURO - Credenciales en .env
sheet_manager = SheetManager()
# Lee credentials.json local (no en GitHub)
```

**Frontend NO tiene API keys:**
```javascript
// ✅ SEGURO - Solo llama al backend
const API_BASE = 'http://localhost:5000/api';
fetch(`${API_BASE}/jobs`)
```

---

## 🗑️ ESTE ARCHIVO SERÁ ELIMINADO

El script `git_clean_all_secrets.ps1` eliminará este archivo del repositorio y del historial.

**Usa:** `dashboard_secure.html` + `dashboard_backend.py`

---

**Status:** DEPRECATED - No usar  
**Reemplazo:** dashboard_secure.html + dashboard_backend.py  
**Razón:** API key expuesta (inseguro)
