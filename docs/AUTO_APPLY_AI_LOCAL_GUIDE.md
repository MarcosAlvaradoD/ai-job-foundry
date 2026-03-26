# 🤖 AUTO-APPLY AI LOCAL - GUÍA DE USO

## 📊 RESUMEN

Sistema de auto-aplicación a ofertas de LinkedIn usando **IA 100% LOCAL y GRATIS**:
- **EasyOCR** - Extrae texto y coordenadas de screenshots
- **LM Studio (Qwen 2.5 14B)** - Analiza páginas y decide acciones
- **Playwright Smart Locators** - Fallback confiable

**Ventajas:**
✅ 100% gratis - sin APIs pagas  
✅ 100% local - total privacidad  
✅ Funciona offline  
✅ Adaptive - se adapta a cambios en LinkedIn

---

## 🔧 INSTALACIÓN

Ya completada! Se instaló:
```powershell
pip install easyocr pillow
```

**Archivos creados:**
- `core/automation/linkedin_ocr_helper.py` - Helper OCR
- `core/automation/auto_apply_linkedin_ai_local.py` - Auto-applier principal
- `scripts/test_ocr_system.py` - Script de prueba

---

## 🧪 PRUEBA RÁPIDA

Antes de usar el sistema, prueba que todo funciona:

```powershell
py scripts\test_ocr_system.py
```

Esto verifica:
1. EasyOCR instalado correctamente
2. LinkedInOCRHelper funciona
3. LM Studio está conectado
4. OCR extrae texto de imágenes

---

## 🚀 USO BÁSICO

### Opción 1: Desde Control Center (RECOMENDADO)

```powershell
py control_center.py
```

Luego selecciona:
- **12a** - Auto-Apply AI Local (DRY RUN) - Simula aplicaciones
- **12b** - Auto-Apply AI Local (LIVE) - Aplica realmente

### Opción 2: Desde línea de comandos

**DRY RUN (simular):**
```powershell
py core\automation\auto_apply_linkedin_ai_local.py --min-fit 7 --max-jobs 10
```

**LIVE (aplicar realmente):**
```powershell
py core\automation\auto_apply_linkedin_ai_local.py --live --min-fit 7 --max-jobs 10
```

---

## ⚙️ PARÁMETROS

- `--min-fit N` - FIT Score mínimo (default: 7, rango 0-10)
- `--max-jobs N` - Máximo de jobs a procesar (default: 10)
- `--live` - Modo LIVE (sin esto es DRY RUN)

**Ejemplos:**

```powershell
# Solo jobs con FIT 8+, máximo 5
py core\automation\auto_apply_linkedin_ai_local.py --min-fit 8 --max-jobs 5

# LIVE: FIT 7+, máximo 20 jobs
py core\automation\auto_apply_linkedin_ai_local.py --live --min-fit 7 --max-jobs 20
```

---

## 🎯 CÓMO FUNCIONA

### Flujo del Sistema:

1. **Obtener Jobs** - Lee Google Sheets (tab LinkedIn)
   - Filtra por FIT Score >= min_fit
   - Excluye ya aplicados
   - Requiere ApplyURL presente

2. **Login LinkedIn** - Automático con credenciales del .env
   - Mantiene sesión activa
   - Auto-reautentica si expira

3. **Para cada job:**
   
   a. **Navegar** a la página de la oferta
   
   b. **Análisis Híbrido** (multi-step):
      - **Prioridad 1:** Playwright Smart Locators
        - Busca "Easy Apply", "Next", "Submit" con regex
        - Más rápido y confiable
      
      - **Prioridad 2:** OCR + IA fallback
        - Screenshot de la página
        - EasyOCR extrae texto + coordenadas
        - LM Studio analiza y decide:
          - ¿Hacer clic en Easy Apply?
          - ¿Rellenar formulario?
          - ¿Siguiente paso?
          - ¿Enviar aplicación?
      
   c. **Ejecutar acción** decidida por IA
      - Click en botones por coordenadas OCR
      - Rellenar campos con datos de CV
      - Continuar hasta completar
   
   d. **Actualizar Sheets** (solo en LIVE)
      - Status: Applied
      - NextAction: Auto-applied via AI [fecha]

4. **Reporte Final**
   - Total procesados
   - Aplicaciones exitosas
   - Errores

---

## 📋 DATOS DEL CV

El sistema usa estos datos para rellenar formularios (definidos en `auto_apply_linkedin_ai_local.py`):

```python
CV_DATA = {
    "name": "Marcos Alberto Alvarado de la Torre",
    "first_name": "Marcos",
    "last_name": "Alvarado",
    "email": "markalvati@gmail.com",
    "phone": "+52 33 1234 5678",
    "location": "Guadalajara, Jalisco, Mexico",
    "years_experience": "10",
    "current_role": "Senior Project Manager / Product Owner",
    ...
}
```

**Editar CV_DATA:**
1. Abre: `core\automation\auto_apply_linkedin_ai_local.py`
2. Busca: `CV_DATA = {`
3. Modifica los valores
4. Guarda

---

## 🔍 TROUBLESHOOTING

### EasyOCR no funciona
```powershell
pip install easyocr pillow --force-reinstall
```

### LM Studio no responde
1. Abre LM Studio
2. Carga modelo: Qwen 2.5 14B Instruct
3. Start Server (puerto 11434)
4. Verifica: http://127.0.0.1:11434

### LinkedIn bloquea login
- El sistema usa credenciales del .env
- Si falla, login manual una vez
- Playwright guarda sesión automáticamente

### No encuentra botón "Easy Apply"
- El sistema usa OCR fallback automáticamente
- LM Studio analiza y encuentra botón
- Si falla, revisa logs en consola

### Playwright timeout
- LinkedIn puede estar lento
- El sistema reintenta automáticamente
- Max 10 pasos por aplicación

---

## 📊 GOOGLE SHEETS

El sistema actualiza automáticamente (solo en LIVE):

**Columnas actualizadas:**
- **Status:** Applied (si exitoso)
- **NextAction:** Auto-applied via AI YYYY-MM-DD

**Pestaña:** LinkedIn  
**URL:** https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

---

## 🎓 MEJORES PRÁCTICAS

1. **Siempre empezar con DRY RUN**
   - Verifica que todo funciona
   - Revisa que jobs son correctos
   - No actualiza Sheets

2. **Usar FIT Score alto primero**
   - Empezar con FIT 8+ (mejores matches)
   - Bajar gradualmente si necesario

3. **Procesar lotes pequeños**
   - Máximo 10-20 jobs por vez
   - LinkedIn puede limitar si aplicas demasiado

4. **Monitorear logs**
   - El sistema imprime cada paso
   - Revisa errores en consola
   - Screenshots temporales se eliminan automáticamente

5. **LM Studio debe estar corriendo**
   - Verifica ANTES de empezar
   - Modelo Qwen 2.5 14B cargado
   - Server activo en puerto 11434

---

## 🔄 COMPARACIÓN: Viejo vs Nuevo

| Feature | Auto-Apply Viejo (Opción 11/12) | Auto-Apply AI Local (Opción 12a/12b) |
|---------|----------------------------------|--------------------------------------|
| Método | Playwright locators fijos | OCR + IA adaptativa |
| Costos | Gratis | Gratis |
| Funciona con cambios LinkedIn | ❌ No | ✅ Sí |
| Formularios complejos | ⚠️ Limitado | ✅ Adaptativo |
| Privacidad | ✅ Local | ✅ 100% Local |
| Requiere APIs | ❌ No | ❌ No |
| Success rate | ~50% | ~80-90% (estimado) |

---

## 📞 SOPORTE

**Si algo no funciona:**

1. Corre test: `py scripts\test_ocr_system.py`
2. Verifica LM Studio está corriendo
3. Revisa logs en consola
4. Prueba DRY RUN primero
5. Reporta error con logs completos

**Logs útiles:**
- Consola: muestra cada paso
- Screenshots: temp_screenshot_stepN.png (se borran automáticamente)

---

## 🎯 PRÓXIMOS PASOS

1. **Testing inicial:**
   ```powershell
   py scripts\test_ocr_system.py
   py control_center.py  # Opción 12a
   ```

2. **Primer DRY RUN:**
   - 5 jobs
   - FIT 8+
   - Verificar que detecta Easy Apply

3. **Primer LIVE:**
   - 3 jobs MAX
   - FIT 9+
   - Monitorear de cerca

4. **Incrementar gradualmente:**
   - Si funciona bien → más jobs
   - Bajar FIT score
   - Procesar backlog

---

**¡Sistema listo para usar!**  
**Creado:** 2026-01-27  
**Progreso del proyecto:** 75% → 85%
