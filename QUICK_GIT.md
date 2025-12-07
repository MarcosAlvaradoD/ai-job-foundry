# ⚡ COMANDOS RÁPIDOS PARA GITHUB

## 🚀 MÉTODO 1: SCRIPT AUTOMATIZADO (Recomendado)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry

# Ejecutar script que hace todo automáticamente
.\push_to_github.ps1
```

**El script:**
- ✅ Verifica que Git esté instalado
- ✅ Valida que archivos sensibles estén protegidos
- ✅ Inicializa Git si es necesario
- ✅ Configura usuario de Git
- ✅ Hace commit con mensaje descriptivo
- ✅ Te guía para crear repo en GitHub
- ✅ Conecta y hace push

**Duración:** 3-5 minutos

---

## ⚡ MÉTODO 2: COMANDOS MANUALES (Rápido)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry

# 1. Inicializar Git (si no está)
git init

# 2. Configurar Git (primera vez)
git config --global user.name "Marcos Alvarado"
git config --global user.email "markalvati@gmail.com"

# 3. Agregar archivos
git add .

# 4. Verificar (IMPORTANTE: revisa que NO haya credenciales)
git status

# 5. Commit
git commit -m "🚀 Initial commit - AI Job Foundry v1.0

✅ Production-ready automated job search system
🔒 All credentials excluded via .gitignore"

# 6. Crear repo en GitHub
# - Ve a: https://github.com/new
# - Name: ai-job-foundry
# - Visibility: Private
# - NO marques "Initialize with README"
# - Click "Create repository"

# 7. Conectar y push (reemplaza TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/ai-job-foundry.git
git branch -M main
git push -u origin main
```

**Si pide autenticación:**
- Genera Personal Access Token: https://github.com/settings/tokens
- Usa el token como password

**Duración:** 2-3 minutos

---

## 🔍 VERIFICACIÓN RÁPIDA

Después del push, verifica en GitHub que NO aparezcan:

❌ `data/credentials/credentials.json`  
❌ `data/credentials/token.json`  
❌ `.env`  
❌ `data/linkedin_cookies.json`  

✅ Debe aparecer:
- README.md
- core/
- scripts/
- *.py
- .gitignore

---

## 📝 COMANDOS FUTUROS

```powershell
# Agregar cambios nuevos
git add .
git commit -m "Descripción del cambio"
git push

# Ver status
git status

# Ver historial
git log --oneline
```

---

## 🆘 EMERGENCIA: SI SUBISTE CREDENCIALES

```powershell
# 1. Remover del último commit
git rm --cached data/credentials/credentials.json
git commit --amend

# 2. Push forzado
git push --force

# 3. CRÍTICO: Regenerar credenciales en Google Cloud Console
```

---

## 📚 DOCUMENTACIÓN COMPLETA

- **GIT_COMMANDS.md** - Guía detallada paso a paso
- **README.md** - Documentación del proyecto
- **.gitignore** - Archivos excluidos (credenciales)

---

**Recomendación:** Usa el script `push_to_github.ps1` la primera vez.  
Para cambios futuros, usa los comandos manuales rápidos.
