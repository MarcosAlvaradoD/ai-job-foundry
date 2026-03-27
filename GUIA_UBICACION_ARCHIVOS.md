# 📂 GUÍA DE UBICACIÓN DE ARCHIVOS DESCARGADOS

## 🎯 ARCHIVOS A COLOCAR

### 1. CLEANUP_FINAL.ps1
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\CLEANUP_FINAL.ps1`

**Razón:** Es un script de utilidad que debe ejecutarse desde la raíz

**Acción:**
```powershell
# Descargar desde el chat y copiar a:
C:\Users\MSI\Desktop\ai-job-foundry\CLEANUP_FINAL.ps1
```

---

### 2. COMPARATIVA_LAUNCHERS.md
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\docs\COMPARATIVA_LAUNCHERS.md`

**Razón:** Es documentación sobre los launchers

**Acción:**
```powershell
# Descargar desde el chat y copiar a:
C:\Users\MSI\Desktop\ai-job-foundry\docs\COMPARATIVA_LAUNCHERS.md
```

---

### 3. REORGANIZACION_PROYECTO.md
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\docs\REORGANIZACION_PROYECTO.md`

**Razón:** Es documentación sobre la reorganización

**Acción:**
```powershell
# Descargar desde el chat y copiar a:
C:\Users\MSI\Desktop\ai-job-foundry\docs\REORGANIZACION_PROYECTO.md
```

---

### 4. RESUMEN_EJECUTIVO_REORGANIZACION.md
**Ubicación:** `C:\Users\MSI\Desktop\ai-job-foundry\docs\RESUMEN_EJECUTIVO_REORGANIZACION.md`

**Razón:** Es documentación ejecutiva sobre los cambios

**Acción:**
```powershell
# Descargar desde el chat y copiar a:
C:\Users\MSI\Desktop\ai-job-foundry\docs\RESUMEN_EJECUTIVO_REORGANIZACION.md
```

---

## ✅ RESUMEN DE UBICACIONES

```
C:\Users\MSI\Desktop\ai-job-foundry\
├── CLEANUP_FINAL.ps1                              ← AQUÍ
└── docs\
    ├── COMPARATIVA_LAUNCHERS.md                   ← AQUÍ
    ├── REORGANIZACION_PROYECTO.md                 ← AQUÍ
    └── RESUMEN_EJECUTIVO_REORGANIZACION.md        ← AQUÍ
```

---

## 🚀 SCRIPT RÁPIDO DE INSTALACIÓN

Copia este script a un archivo `.ps1` y ejecútalo:

```powershell
# ============================================================================
# INSTALAR ARCHIVOS DESCARGADOS
# ============================================================================

$downloads = "$env:USERPROFILE\Downloads"
$project = "C:\Users\MSI\Desktop\ai-job-foundry"

# Copiar archivos
Copy-Item "$downloads\CLEANUP_FINAL.ps1" "$project\" -Force
Copy-Item "$downloads\COMPARATIVA_LAUNCHERS.md" "$project\docs\" -Force
Copy-Item "$downloads\REORGANIZACION_PROYECTO.md" "$project\docs\" -Force
Copy-Item "$downloads\RESUMEN_EJECUTIVO_REORGANIZACION.md" "$project\docs\" -Force

Write-Host "✓ Archivos copiados correctamente" -ForegroundColor Green
```
