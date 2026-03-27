# 🚀 COMPARATIVA DE LAUNCHERS - AI JOB FOUNDRY

## 📊 TABLA COMPARATIVA

| Característica | START_CONTROL_CENTER.bat | START_WEB_APP.bat | START_UNIFIED_APP.bat ⭐ |
|----------------|-------------------------|-------------------|--------------------------|
| **Puerto** | N/A (CLI) | 5000 | 5555 |
| **Interfaz** | Terminal | Web básica | Web completa |
| **Funciones** | 17 opciones | Dashboard | 17 funciones + Dashboard |
| **Publicidad** | ❌ No | ❌ No | ✅ SÍ (3 zonas) 💰 |
| **Auto-abre navegador** | ❌ No | ❌ No | ✅ Sí |
| **Health checks** | Manual | No | ✅ Automático |
| **LM Studio check** | Manual | No | ✅ Automático |
| **Ubicación app** | `control_center.py` | `web_app\app.py` | `unified_app\app.py` |
| **Mejor para** | Admin/Testing | Desarrollo | **Producción/Demo** |

## 🎯 RECOMENDACIONES DE USO

### 1️⃣ START_CONTROL_CENTER.bat
**Cuándo usar:**
- Administración rápida del sistema
- Testing de funciones individuales
- Debugging y troubleshooting
- Cuando no necesitas interfaz web

**Ventajas:**
- Rápido de lanzar
- Bajo consumo de recursos
- Acceso directo a todas las funciones

**Desventajas:**
- Solo terminal (sin UI)
- Sin publicidad integrada
- Menos presentable para demos

---

### 2️⃣ START_WEB_APP.bat
**Cuándo usar:**
- Desarrollo de nuevas features web
- Testing de interfaz básica
- Cuando no necesitas las funciones completas

**Ventajas:**
- Interfaz web simple
- Puerto estándar (5000)

**Desventajas:**
- Funcionalidad limitada
- Sin publicidad
- Sin auto-inicio de servicios

---

### 3️⃣ START_UNIFIED_APP.bat ⭐ **RECOMENDADO**
**Cuándo usar:**
- **Demos a clientes/inversores**
- **Presentaciones profesionales**
- **Uso en producción**
- **Cuando quieres monetizar (tiene anuncios)**

**Ventajas:**
- ✅ **3 zonas de publicidad integradas** 💰
- ✅ Interfaz completa y profesional
- ✅ Auto-verifica servicios (LM Studio, etc.)
- ✅ Abre navegador automáticamente
- ✅ Health checks integrados
- ✅ 17 funciones del Control Center
- ✅ Dashboard en tiempo real

**Desventajas:**
- Consumo de recursos ligeramente mayor (vale la pena)

---

## 💰 MONETIZACIÓN

### Zonas de Publicidad en UNIFIED_APP

**Zona 1: Header Banner**
- Ubicación: Superior de la página
- Tamaño: 728x90 (Leaderboard)
- Visibilidad: Máxima

**Zona 2: Sidebar**
- Ubicación: Lateral derecho
- Tamaño: 300x600 (Half Page)
- Visibilidad: Alta

**Zona 3: Footer Banner**
- Ubicación: Inferior de la página
- Tamaño: 728x90 (Leaderboard)
- Visibilidad: Media-Alta

### Implementación de Anuncios

Para activar anuncios reales (Google AdSense, etc.):

1. Editar `unified_app\templates\index.html`
2. Buscar comentarios `<!-- AD ZONE X -->`
3. Reemplazar con código de Google AdSense o red publicitaria

**Ejemplo:**
```html
<!-- AD ZONE 1: Header Banner -->
<div class="ad-space">
    <!-- Pegar código de AdSense aquí -->
    <script async src="https://pagead2.googlesyndication.com/..."></script>
</div>
```

---

## 🎮 COMANDOS DE INICIO

### Inicio Rápido
```batch
REM Para PRODUCCIÓN/DEMOS (con anuncios)
START_UNIFIED_APP.bat

REM Para ADMINISTRACIÓN
START_CONTROL_CENTER.bat

REM Para DESARROLLO
START_WEB_APP.bat
```

### Verificación de Estado
```powershell
# Ver qué está corriendo
netstat -ano | findstr "5000 5555 11434"

# 5000  = Web App
# 5555  = Unified App
# 11434 = LM Studio
```

### Detener Servicios
```powershell
# Detener Web App (puerto 5000)
for /f "tokens=5" %a in ('netstat -ano ^| findstr ":5000"') do taskkill /F /PID %a

# Detener Unified App (puerto 5555)
for /f "tokens=5" %a in ('netstat -ano ^| findstr ":5555"') do taskkill /F /PID %a
```

---

## 📈 CASOS DE USO

### Caso 1: Demo a Inversores
**Launcher:** START_UNIFIED_APP.bat ⭐
**Por qué:**
- Interfaz profesional y pulida
- Espacios de publicidad visibles (potencial de monetización)
- Auto-inicio de servicios (no fallas técnicas)
- Dashboard con estadísticas en tiempo real

### Caso 2: Presentación a Cliente
**Launcher:** START_UNIFIED_APP.bat ⭐
**Por qué:**
- Se ve profesional y terminado
- Funcionalidad completa visible
- Modelo de negocio evidente (ads)

### Caso 3: Testing Rápido
**Launcher:** START_CONTROL_CENTER.bat
**Por qué:**
- Inicio rápido
- Acceso directo a funciones
- Sin overhead de navegador

### Caso 4: Desarrollo de Features
**Launcher:** START_WEB_APP.bat o START_CONTROL_CENTER.bat
**Por qué:**
- Menos dependencias
- Más fácil de debugear
- Iteración rápida

---

## 🔧 TROUBLESHOOTING

### Error: "Puerto ya en uso"
```powershell
# Identificar proceso
netstat -ano | findstr ":5555"

# Matar proceso (reemplaza PID)
taskkill /F /PID <PID>

# Reintentar
START_UNIFIED_APP.bat
```

### Error: "LM Studio not found"
```powershell
# Verificar LM Studio
Test-NetConnection -ComputerName localhost -Port 11434

# Si falla, iniciar LM Studio manualmente
# Luego reintentar
START_UNIFIED_APP.bat
```

### Error: "Python not found"
```powershell
# Verificar Python
py --version

# Si falla, reinstalar Python 3.13+
# Verificar que 'py' esté en PATH
```

---

## 📊 RENDIMIENTO

### Consumo de Recursos (Aproximado)

| Launcher | RAM | CPU | Disco I/O |
|----------|-----|-----|-----------|
| Control Center | 50 MB | 2-5% | Bajo |
| Web App | 80 MB | 5-8% | Medio |
| Unified App | 120 MB | 8-12% | Medio |

**Nota:** El Unified App vale el consumo extra por la experiencia completa.

---

## ✅ CHECKLIST DE LANZAMIENTO

### Antes de Demo/Presentación

- [ ] LM Studio corriendo
- [ ] Puerto 5555 libre
- [ ] Navegador predeterminado configurado
- [ ] Google Sheets accesible
- [ ] Token OAuth válido
- [ ] Ejecutar START_UNIFIED_APP.bat
- [ ] Verificar que abre navegador automáticamente
- [ ] Confirmar 3 zonas de anuncios visibles

---

## 🎯 RESUMEN EJECUTIVO

**Para 90% de los casos, usa:** `START_UNIFIED_APP.bat` ⭐

**Es el launcher más completo, profesional y listo para producción.**

**Solo usa los otros launchers si:**
- Necesitas testing rápido (Control Center)
- Estás desarrollando features (Web App)
- Tienes restricciones de recursos (Control Center)

---

**Última actualización:** 2025-12-07
**Recomendación oficial:** START_UNIFIED_APP.bat ⭐
