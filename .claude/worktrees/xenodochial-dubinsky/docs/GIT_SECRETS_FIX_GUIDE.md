# 🔒 GIT SECRETS FIX - GUÍA RÁPIDA

**Problema:** GitHub bloqueó el push porque detectó credenciales OAuth.

**Archivos problemáticos:**
- `data/credentials/token.json.old` ❌
- `workflows/google_credentials.json` ❌

---

## ✅ SOLUCIÓN EN 2 PASOS

### **PASO 1: INTENTA ESTO PRIMERO (5 MIN)**

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\git_fix_secrets.ps1
```

**Qué hace:**
1. Revierte el último commit (mantiene cambios)
2. Elimina archivos con secretos
3. Actualiza .gitignore
4. Crea commit limpio sin secretos
5. Push a GitHub

**Resultado esperado:**
```
✅✅ SUCCESS! Proyecto sincronizado con GitHub!
🔗 Verifica en: https://github.com/MarcosAlvaradoD/ai-job-foundry
```

---

### **PASO 2: SI EL PASO 1 FALLA (LIMPIEZA PROFUNDA)**

```powershell
.\git_clean_secrets.ps1
```

**Qué hace:**
- Limpia el historial completo de Git
- Elimina rastros de secretos
- Force push al remoto

⚠️ **ADVERTENCIA:** Reescribe historial (pero está bien, es tu repo)

---

## 🔍 VERIFICAR QUE FUNCIONÓ

**Después de ejecutar cualquiera de los scripts:**

1. **Abre GitHub:**
   https://github.com/MarcosAlvaradoD/ai-job-foundry

2. **Verifica que aparezca:**
   - "feat: AI Job Foundry - 94% Complete"
   - Fecha: hace unos minutos
   - Archivos actualizados visibles

3. **Confirma que NO estén estos archivos:**
   - `data/credentials/token.json.old` ❌
   - `workflows/google_credentials.json` ❌

---

## ⚡ COMANDOS RÁPIDOS

### **Intento 1 (Recomendado):**
```powershell
.\git_fix_secrets.ps1
```

### **Intento 2 (Si falla):**
```powershell
.\git_clean_secrets.ps1
```

### **Verificar status:**
```powershell
git status
```

### **Ver último commit:**
```powershell
git log --oneline -1
```

---

## 🛡️ PREVENCIÓN FUTURA

**El .gitignore ya está actualizado para prevenir esto:**

```
# Estos archivos NUNCA se subirán a GitHub
data/credentials/*.json
workflows/google_credentials.json
workflows/token.json
*.json.old
**/credentials.json
**/token.json
```

**Para futuros updates:**
```powershell
.\git_update.ps1
```

Este script ahora verifica que NO haya secretos antes de push.

---

## 🆘 SI TODO FALLA

**Última opción (nuclear):**

1. Ve a GitHub: https://github.com/MarcosAlvaradoD/ai-job-foundry/settings
2. Scroll hasta el final
3. "Delete this repository"
4. Confirma eliminación
5. Crea nuevo repo con el mismo nombre
6. Ejecuta:
   ```powershell
   git remote set-url origin https://github.com/MarcosAlvaradoD/ai-job-foundry.git
   git push -u origin main --force
   ```

---

## 📋 CHECKLIST

```
[ ] 1. Ejecuté git_fix_secrets.ps1
[ ] 2. Vi mensaje de SUCCESS
[ ] 3. Verifiqué en GitHub que se actualizó
[ ] 4. Confirmé que NO hay archivos sensibles
[ ] 5. Listo para continuar ✅
```

---

## 💡 POR QUÉ PASÓ ESTO

GitHub tiene **Push Protection** que bloquea automáticamente cuando detecta:
- OAuth tokens
- API keys
- Passwords
- Credenciales de cualquier tipo

**Esto es BUENO** - Te protege de exponer secretos públicamente.

**Solución:** Los secretos deben estar SOLO en tu máquina local:
- ✅ En archivos locales
- ✅ En .env (no en Git)
- ✅ En data/credentials/ (ignorado por Git)
- ❌ NUNCA en GitHub

---

**Tiempo estimado:** 5 minutos  
**Dificultad:** Fácil (solo ejecutar script)  
**Resultado:** Push limpio a GitHub ✅
