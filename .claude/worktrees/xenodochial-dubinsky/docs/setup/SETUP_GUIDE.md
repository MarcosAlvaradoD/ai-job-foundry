# 🔧 AI JOB FOUNDRY - INSTALACIÓN Y CONFIGURACIÓN MULTI-USUARIO

**Fecha:** 2025-11-23  
**Versión:** 2.0 (Multi-User)

---

## 🆕 NOVEDADES EN ESTA VERSIÓN

### ✅ Sistema Multi-Usuario
- Cada usuario puede tener su propio perfil
- CV y preferencias personalizadas por usuario
- Cambio fácil entre perfiles
- Configuración independiente de API keys

### ✅ Setup Wizard
- Configuración guiada paso a paso
- No requiere editar archivos manualmente
- Validación de datos

### ✅ Build EXE
- Crear ejecutable standalone
- Distribuir a otros usuarios
- No requiere instalar Python

---

## 🚀 INSTALACIÓN RÁPIDA (ARREGLAR ERRORES)

### Opción 1: Fix Rápido (solo dependencias faltantes)
```powershell
.\FIX_DEPENDENCIES.bat
```

### Opción 2: Instalación Completa (recomendado)
```powershell
.\INSTALL_COMPLETE.bat
```

Esto hará:
1. ✅ Instalar TODAS las dependencias
2. ✅ Instalar Playwright browsers
3. ✅ Crear directorios necesarios
4. ✅ Ejecutar setup wizard para tu perfil

---

## 👤 CREAR TU PERFIL DE USUARIO

### 1. Ejecutar Setup Wizard
```powershell
py setup_wizard.py
```

### 2. Responder las preguntas
El wizard te preguntará:

**STEP 1: USER PROFILE**
- Nombre completo
- Ubicación (ej: Guadalajara, México)
- Timezone (ej: CST)

**STEP 2: PROFESSIONAL INFORMATION**
- Roles que buscas (ej: Project Manager, Product Owner)
- Años de experiencia
- Habilidades clave (ej: Python, SQL, Agile)
- Industrias con experiencia

**STEP 3: JOB PREFERENCES**
- Preferencia de ubicación (Remote/Hybrid/On-site)
- Salario mínimo (opcional)
- FIT score threshold (recomendado: 7)

**STEP 4: CV/RESUME DESCRIPTION**
- Descripción profesional completa
- Se usa para análisis AI de matches

**STEP 5: API KEYS (OPTIONAL)**
- Gemini API key (opcional)
- Se puede configurar después

### 3. Tu perfil queda guardado en:
```
data/profiles/tu_nombre/
├── config.json          # Configuración
├── cv_description.txt   # Tu CV
└── .env                # API keys (opcional)
```

---

## 🔄 CAMBIAR ENTRE PERFILES

Si tienes múltiples usuarios/perfiles:

```powershell
py switch_profile.py
```

Esto muestra:
- Lista de todos los perfiles
- Perfil activo actual
- Permite seleccionar otro perfil

**Nota:** Reinicia la app después de cambiar perfil.

---

## 📦 CREAR EXE PARA DISTRIBUCIÓN

### 1. Construir el EXE
```powershell
.\BUILD_EXE.bat
```

Esto crea:
```
dist/AIJobFoundry/
├── AIJobFoundry.exe        # Executable
├── INSTALL.bat            # Instalador para usuario final
├── requirements.txt       # Dependencias
├── setup_wizard.py        # Setup para nuevo usuario
└── data/                  # Directorios de datos
```

### 2. Distribuir
Copia la carpeta completa `dist/AIJobFoundry/` a otro usuario.

### 3. Usuario final ejecuta:
```powershell
INSTALL.bat
```

Esto:
1. Instala dependencias Python
2. Instala Playwright browsers
3. Ejecuta setup wizard
4. Configura el perfil del usuario

### 4. Usuario ejecuta la app:
```powershell
AIJobFoundry.exe
```
O:
```powershell
START_UNIFIED_APP.bat
```

---

## 📁 ESTRUCTURA DE PERFILES

```
data/profiles/
├── marcos/                    # Perfil de Marcos
│   ├── config.json           # Configuración
│   ├── cv_description.txt    # CV
│   └── .env                  # API keys
│
├── john_smith/               # Otro usuario
│   ├── config.json
│   ├── cv_description.txt
│   └── .env
│
└── active_profile.txt        # Perfil activo actual
```

---

## 🔧 COMANDOS ÚTILES

### Instalación
```powershell
.\INSTALL_COMPLETE.bat     # Instalación completa
.\FIX_DEPENDENCIES.bat     # Solo arreglar dependencias
.\VERIFY_INSTALLATION.ps1  # Verificar instalación
```

### Perfiles
```powershell
py setup_wizard.py         # Crear nuevo perfil
py switch_profile.py       # Cambiar perfil
```

### Build & Distribución
```powershell
.\BUILD_EXE.bat           # Crear ejecutable
```

### Uso Normal
```powershell
START_UNIFIED_APP.bat     # Iniciar app
py run_auto_apply.py --dry-run   # Auto-apply test
```

---

## ⚙️ CONFIGURACIÓN AVANZADA

### Editar Perfil Manualmente

Si necesitas editar tu perfil después:

**1. Editar config.json:**
```
data/profiles/tu_nombre/config.json
```

**2. Editar CV:**
```
data/profiles/tu_nombre/cv_description.txt
```

**3. Editar API keys:**
```
data/profiles/tu_nombre/.env
```

### Migrar Perfil Existente

Si ya tenías configuración en `data/cv_descriptor.txt`:

1. Ejecutar setup wizard con tu nombre
2. Copiar contenido de `data/cv_descriptor.txt` cuando te lo pida
3. Tu configuración anterior en `.env` raíz sigue funcionando

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "google-auth not installed"
```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### Error: "python-dotenv not installed"
```powershell
pip install python-dotenv
```

### Error: "No profiles found"
```powershell
py setup_wizard.py
```

### Error: "Profile config.json not found"
El perfil está corrupto, crea uno nuevo:
```powershell
py setup_wizard.py
```

### Error al ejecutar EXE
El usuario necesita:
1. Python 3.11+ instalado
2. Ejecutar `INSTALL.bat` primero
3. Tener permisos de administrador

---

## 📊 COMPATIBILIDAD

**Sistema Operativo:**
- Windows 10/11 (optimizado)
- Linux (parcial, sin .bat scripts)
- macOS (parcial, sin .bat scripts)

**Python:**
- 3.11+ (recomendado)
- 3.10+ (compatible)

**Hardware:**
- 8GB RAM mínimo
- 16GB RAM recomendado para LM Studio
- GPU (RTX series) recomendado para AI local

---

## 🎯 FLUJO RECOMENDADO PARA NUEVOS USUARIOS

```
1. Descargar/Clonar proyecto
   ↓
2. Ejecutar: INSTALL_COMPLETE.bat
   ↓
3. Setup wizard crea tu perfil
   ↓
4. Configurar Google Sheets ID en .env
   ↓
5. Ejecutar: py setup_oauth_helper.py
   ↓
6. Iniciar: START_UNIFIED_APP.bat
   ↓
7. ¡Usar el sistema!
```

---

## 📚 ARCHIVOS DE REFERENCIA

**Para usuarios finales:**
- `QUICK_START_UNIFIED.md` - Guía rápida de uso
- `README.md` - Overview del proyecto

**Para desarrolladores:**
- `PROJECT_STATUS.md` - Estado del proyecto
- `requirements.txt` - Dependencias
- `ai_job_foundry.spec` - Configuración PyInstaller

**Para distribución:**
- `BUILD_EXE.bat` - Crear ejecutable
- `INSTALL.bat` - Instalador para usuarios finales

---

## 🔐 SEGURIDAD Y PRIVACIDAD

### Datos Locales
- Todos los datos se almacenan localmente
- No se envían datos a servidores externos (excepto APIs configuradas)
- Cada perfil tiene sus propios credentials

### API Keys
- Almacenadas en archivos .env por perfil
- No se comparten entre perfiles
- Opcionales (sistema funciona sin ellas)

### Google OAuth
- Tokens almacenados en `data/credentials/token.json`
- Compartidos entre perfiles (misma cuenta Google)
- Se pueden tener múltiples tokens si usas múltiples cuentas

---

## 🆘 SOPORTE

### Problemas comunes

**"Profile not found"**
→ Ejecuta `py setup_wizard.py`

**"Dependencies missing"**
→ Ejecuta `INSTALL_COMPLETE.bat`

**"OAuth error"**
→ Ejecuta `py setup_oauth_helper.py`

**"LM Studio offline"**
→ Inicia LM Studio manualmente

### Logs
Revisa logs en:
- `logs/powershell/session_*.log`
- `logs/ingest.log`

---

## 🎉 CONCLUSIÓN

Tu sistema ahora es **multi-usuario** y **distribuible**:

✅ Cada usuario tiene su perfil  
✅ Setup wizard guiado  
✅ Generación de EXE  
✅ Instalador automático  
✅ Cambio fácil de perfiles  

**Próximos pasos:**
1. Ejecutar `INSTALL_COMPLETE.bat` si aún no lo has hecho
2. Crear tu perfil con `py setup_wizard.py`
3. Configurar Google Sheets y OAuth
4. ¡Usar el sistema!

---

**Autor:** Marcos Alberto Alvarado de la Torre  
**Proyecto:** AI Job Foundry  
**Versión:** 2.0 (Multi-User)  
**Fecha:** 2025-11-23
