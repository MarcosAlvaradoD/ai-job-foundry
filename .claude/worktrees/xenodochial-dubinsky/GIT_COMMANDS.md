# 🚀 SUBIR A GITHUB - COMANDOS PASO A PASO

## 📋 PREREQUISITOS

Asegúrate de tener:
- [ ] Git instalado: `git --version`
- [ ] Cuenta de GitHub creada
- [ ] .gitignore actualizado (✅ ya está)
- [ ] README.md creado (✅ ya está)

---

## 🔐 PASO 0: VERIFICAR ARCHIVOS SENSIBLES

**CRÍTICO:** Verifica que estos archivos NO se subirán:

```powershell
# Ver qué archivos se ignorarán
git status --ignored

# Verificar que estos estén en .gitignore:
# - data/credentials/credentials.json
# - data/credentials/token.json
# - .env
# - data/linkedin_cookies.json
# - data/state/seen_ids.json
```

---

## 📦 PASO 1: INICIALIZAR GIT (si no está inicializado)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry

# Inicializar repo (solo si es primera vez)
git init

# Ver status
git status
```

---

## 📝 PASO 2: CONFIGURAR GIT (primera vez)

```powershell
# Tu nombre
git config --global user.name "Marcos Alvarado"

# Tu email de GitHub
git config --global user.email "markalvati@gmail.com"

# Verificar configuración
git config --list
```

---

## ➕ PASO 3: AGREGAR ARCHIVOS

```powershell
# Agregar TODO (respetando .gitignore)
git add .

# Ver qué se agregará
git status

# Verificar que NO aparezcan:
# - credentials.json
# - token.json
# - .env
# - linkedin_cookies.json
```

**⚠️ SI VES ARCHIVOS SENSIBLES:**
```powershell
# Removerlos del staging
git reset HEAD data/credentials/credentials.json
git reset HEAD .env

# Agregarlos a .gitignore si no están
```

---

## 💾 PASO 4: HACER COMMIT

```powershell
git commit -m "🚀 Initial commit - AI Job Foundry v1.0

✅ Features:
- Gmail email processing
- LinkedIn/Indeed/Glassdoor scrapers
- AI analysis with LM Studio (Qwen 2.5 14B)
- Smart URL verifiers (Playwright)
- Auto-apply LinkedIn Easy Apply
- Google Sheets integration
- Control Center menu
- Daily pipeline automation

📊 Status: Production ready
🔒 Security: All credentials excluded via .gitignore"
```

---

## 🌐 PASO 5: CREAR REPO EN GITHUB

### Opción A: Desde la web (Recomendado)

1. Ve a: https://github.com/new
2. **Repository name:** `ai-job-foundry`
3. **Description:** `🤖 Automated job search system with local AI`
4. **Visibility:** `Private` (recomendado por credenciales)
5. ❌ NO marques "Initialize with README" (ya lo tienes)
6. Click **"Create repository"**

### Opción B: Desde GitHub CLI (si tienes gh instalado)

```powershell
# Crear repo privado
gh repo create ai-job-foundry --private --source=. --remote=origin

# Crear repo público
gh repo create ai-job-foundry --public --source=. --remote=origin
```

---

## 🔗 PASO 6: CONECTAR CON GITHUB

**Después de crear el repo en GitHub, GitHub te mostrará comandos. Usa estos:**

```powershell
# Agregar remote (reemplaza TU_USUARIO con tu username)
git remote add origin https://github.com/TU_USUARIO/ai-job-foundry.git

# Verificar remote
git remote -v

# Renombrar branch a 'main' (si es necesario)
git branch -M main
```

---

## ⬆️ PASO 7: PUSH A GITHUB

```powershell
# Push inicial
git push -u origin main
```

**Si pide autenticación:**
- **Opción 1:** Usar Personal Access Token (PAT)
  1. Ve a: https://github.com/settings/tokens
  2. "Generate new token (classic)"
  3. Scopes: `repo` (full control)
  4. Copia el token
  5. Úsalo como password al hacer push

- **Opción 2:** Usar GitHub CLI
  ```powershell
  gh auth login
  ```

---

## ✅ PASO 8: VERIFICAR EN GITHUB

1. Ve a: `https://github.com/TU_USUARIO/ai-job-foundry`
2. Verifica que veas:
   - ✅ README.md renderizado
   - ✅ Estructura de carpetas
   - ✅ Archivos .py
   - ❌ NO debe haber `credentials.json`
   - ❌ NO debe haber `.env`
   - ❌ NO debe haber `token.json`

---

## 🔄 COMANDOS PARA FUTUROS CAMBIOS

```powershell
# Ver cambios
git status

# Agregar cambios
git add .

# Commit
git commit -m "Descripción del cambio"

# Push
git push
```

---

## 🚨 EMERGENCIA: SI SUBISTE CREDENCIALES

**Si accidentalmente subiste archivos sensibles:**

```powershell
# 1. Remover del historial
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch data/credentials/credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Push forzado
git push origin --force --all

# 3. CRÍTICO: Regenerar credenciales en Google Cloud Console
# Las viejas están comprometidas
```

**Mejor prevenir:** Siempre verifica con `git status` antes de commit.

---

## 📚 COMANDOS ÚTILES

```powershell
# Ver historial
git log --oneline

# Ver diferencias
git diff

# Deshacer cambios no commiteados
git checkout .

# Ver archivos ignorados
git status --ignored

# Ver remote
git remote -v

# Clonar en otra máquina
git clone https://github.com/TU_USUARIO/ai-job-foundry.git
```

---

## 🎯 CHECKLIST FINAL

- [ ] Git inicializado
- [ ] Archivos agregados con `git add .`
- [ ] Verificado que NO hay credenciales en staging
- [ ] Commit realizado
- [ ] Repo creado en GitHub (privado recomendado)
- [ ] Remote agregado
- [ ] Push exitoso
- [ ] Verificado en GitHub web
- [ ] README.md se ve bien
- [ ] NO aparecen archivos sensibles

---

**¡Listo! Tu proyecto está en GitHub.** 🎉

Para colaborar desde otra máquina:
```powershell
git clone https://github.com/TU_USUARIO/ai-job-foundry.git
cd ai-job-foundry
# Seguir instrucciones de README.md para setup
```
