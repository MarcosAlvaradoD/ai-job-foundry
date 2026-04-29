# 🎮 CONTROL CENTER - GUÍA RÁPIDA

**Control Center es tu interfaz principal para manejar AI Job Foundry.**

---

## 🚀 INICIO RÁPIDO

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py control_center.py
```

**Eso es todo.** No necesitas recordar ningún comando más.

---

## 📋 CARACTERÍSTICAS

### **1. Pipeline Completo**
- Opción 1: Ejecuta TODO (emails → AI → expire → report)
- Opción 2: Pipeline rápido (emails + report)

### **2. Operaciones Individuales**
- Procesar emails
- Análisis AI
- Verificar expirados
- Verificar URLs con scraper
- Generar reportes

### **3. Scraping**
- LinkedIn (buscar ofertas)
- Indeed (buscar ofertas)

### **4. Auto-Apply**
- Dry run (prueba sin aplicar)
- Live (aplica realmente)

### **5. Visualización**
- Dashboard (abre http://localhost:8000)
- Google Sheets (abre browser)

### **6. Utilidades**
- Ver configuración (.env)
- Ver documentación
- Ver estado del proyecto

---

## 💡 EJEMPLOS DE USO

### **Uso Diario Típico:**
```
1. Ejecutar Control Center
2. Seleccionar Opción 1 (Pipeline Completo)
3. Esperar 5-10 minutos
4. Revisar reporte
5. Seleccionar Opción 12 (Abrir Dashboard)
6. Ver ofertas nuevas
```

### **Solo Procesar Emails:**
```
1. Ejecutar Control Center
2. Seleccionar Opción 3 (Procesar Emails)
3. Listo
```

### **Verificar URLs (Opción C que pediste):**
```
1. Ejecutar Control Center
2. Seleccionar Opción 6 (Verificar URLs)
3. Elegir sub-opción:
   a. Todas
   b. Solo nuevas
   c. Solo high-fit
   d. Personalizado
4. Esperar verificación
5. Ver reporte
```

---

## 🎨 COLORES (Windows)

El Control Center usa colores para mejor legibilidad:
- 🟢 Verde: Operaciones exitosas
- 🟡 Amarillo: Procesando...
- 🔵 Azul: Información
- 🔴 Rojo: Errores o advertencias

**Requiere:** `colorama` (instalado automáticamente)

---

## ⌨️ ATAJOS DE TECLADO

- **Enter:** Continuar después de operación
- **Ctrl+C:** Cancelar operación o salir
- **0:** Salir del Control Center

---

## 📚 MENÚ COMPLETO

```
📋 MENÚ PRINCIPAL:

PIPELINE COMPLETO:
  1. 🚀 Ejecutar Pipeline Completo (emails + AI + expire + report)
  2. ⚡ Pipeline Rápido (solo emails + report)

OPERACIONES INDIVIDUALES:
  3. 📧 Procesar Emails Nuevos
  4. 🤖 Análisis AI (calcular FIT SCORES)
  5. 🚫 Verificar Ofertas Expiradas (por fecha)
  6. 🔍 Verificar URLs (scraper automático)
  7. 📊 Generar Reporte

SCRAPING:
  8. 🔗 LinkedIn Scraper (buscar ofertas)
  9. 🔗 Indeed Scraper (buscar ofertas)

AUTO-APPLY:
  10. 🎯 Auto-Apply (DRY RUN - no aplica real)
  11. 💼 Auto-Apply (LIVE - aplica realmente)

VISUALIZACIÓN:
  12. 📊 Abrir Dashboard
  13. 📄 Ver Google Sheets

UTILIDADES:
  14. 🔧 Ver Configuración (.env)
  15. 📚 Ver Documentación
  16. 📈 Ver Estado del Proyecto

SALIR:
  0. 🚪 Salir
```

---

## 🔥 TIPS PRO

### **Ejecución Automática Diaria:**
En lugar de abrir manualmente, crea un Task Scheduler:
- Ejecuta: `py control_center.py`
- Con opción pre-seleccionada: (por implementar)

### **Ver Logs:**
Todos los comandos generan logs en:
- `logs/powershell/`
- `logs/scraper_*.log`
- `logs/interview_*.log`

### **Monitoreo en Tiempo Real:**
1. Abrir Dashboard (Opción 12)
2. Dejar abierto en segundo monitor
3. Auto-refresh cada 60 segundos

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### **Error: "colorama not found"**
```powershell
pip install colorama
```

### **Error: "playwright not found"**
```powershell
pip install playwright
py -m playwright install chromium
```

### **Control Center no responde:**
- Presiona Ctrl+C
- Reinicia
- Revisa que no haya procesos colgados: `Get-Process py*`

### **Comandos no funcionan:**
- Verifica que estás en directorio correcto
- `cd C:\Users\MSI\Desktop\ai-job-foundry`

---

## 🎯 SIGUIENTE NIVEL

### **Personalizar Opciones:**
Edita `control_center.py` para:
- Agregar nuevos comandos
- Cambiar descripciones
- Agregar sub-menús

### **Crear Atajos:**
Crea un `.bat` file:
```batch
@echo off
cd C:\Users\MSI\Desktop\ai-job-foundry
py control_center.py
pause
```

Guarda como: `AI_Job_Foundry.bat` en Desktop

---

## 📞 REFERENCIAS

**Documentación completa:**
- `docs/PROJECT_STATUS.md`
- `docs/JOB_EXPIRATION_SYSTEM.md`
- `docs/DASHBOARD_SETUP.md`

**Scripts que ejecuta:**
- `run_daily_pipeline.py`
- `verify_job_status.py`
- `web/serve_dashboard.py`

---

**Última actualización:** 2025-11-19  
**Autor:** Claude + Marcos Alvarado
