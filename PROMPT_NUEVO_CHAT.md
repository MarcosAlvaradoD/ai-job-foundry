# 🔄 PROMPT PARA NUEVO CHAT - AI JOB FOUNDRY

**Fecha preparación:** 2025-11-19 08:15 CST  
**Progreso actual:** 92%  
**Próximo hito:** Auto-Apply form filling  
**Token usage chat anterior:** 64,477 / 190,000

---

## ⚡ ACCIONES INMEDIATAS AL INICIAR NUEVO CHAT

### 🚨 PASO 1: Fix OAuth (1 minuto) - CRÍTICO
```powershell
py reauthenticate_gmail.py
```
**Sin esto NO FUNCIONA:** Gmail, Bulletins, Deduplicación

### ✅ PASO 2: Probar Pipeline (2 minutos)
```powershell
py control_center.py
# Opción 1 (Pipeline Completo)
```
**Validar:** OAuth + AI Analysis + Bulletin processing

### 📊 PASO 3: Ver Resultados (1 minuto)
```powershell
py control_center.py
# Opción 14 (Ver Google Sheets)
```

---

## 🎯 OBJETIVO DE ESTE CHAT: AUTO-APPLY

### Meta:
Implementar **auto-apply form filling** completo (de 40% → 100%)

### Archivo principal:
`run_auto_apply.py` (wrapper ya creado)

### Tareas específicas:

1. **Detectar campos dinámicos** (30 min)
   - Identificar tipos de campos (text, select, radio, checkbox)
   - Mapear campos comunes (nombre, email, teléfono, CV upload, etc.)
   - Handle unexpected fields

2. **Auto-fill con datos del CV** (45 min)
   - Cargar datos desde `data/cv_descriptor.txt`
   - Mapear campos CV → formulario
   - Validar datos antes de submit

3. **Submit automático con confirmación** (30 min)
   - Dry-run mode (preview sin submit)
   - Confirmación antes de submit real
   - Handle errores de red/timeout

4. **Update status en Google Sheets** (30 min)
   - Columna "Status" → "Applied"
   - Columna "AppliedDate" → timestamp
   - Columna "ApplicationMethod" → "Easy Apply"

5. **Logging completo** (15 min)
   - Qué campos se llenaron
   - Qué errores ocurrieron
   - Tiempo de aplicación

6. **Testing exhaustivo** (30 min)
   - Dry-run con 3-5 ofertas high-fit
   - Verificar no hay errores
   - Probar con ofertas reales

**Total estimado:** 2-3 horas

---

## 📊 ESTADO ACTUAL DEL PROYECTO

### ✅ Componentes al 100%:
- Control Center (interface completa)
- Interview Copilot Session Recorder (push-to-talk + AI)
- URL Verifier
- Dashboard
- Google Sheets integration
- PowerShell automation scripts
- Sistema de expiración híbrido

### ⚠️ Componentes bloqueados por OAuth:
- Gmail Processing (100% → 0% sin OAuth)
- Bulletin Processor (95% → 0% sin OAuth)  
- Deduplicación (100% → 0% sin OAuth)

### ⏳ Componentes en progreso:
- **Auto-Apply** (40% → objetivo 100%)
- Cover Letters (60%)
- Interview Copilot avanzado (15%)

---

## 🔥 CONTEXTO CLAVE

### Perfil profesional (Marcos):
- **Roles objetivo:** PM, PO, Senior BA, IT Manager, ETL Consultant
- **NO busca:** Software Developer positions
- **Prioridad:** Remote work (familia con bebé)
- **Ubicación:** Guadalajara, México (CST)
- **Experiencia:** ERP migrations, ETL (800+ TB), BI/Power BI, IT Infrastructure

### Tech Stack:
- **AI Local:** LM Studio (Qwen 2.5 14B) @ http://172.23.0.1:11434
- **AI Fallback:** Gemini API
- **Storage:** Google Sheets (ID: 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg)
- **Scraping:** Playwright con stealth mode
- **Email:** Gmail API (requiere OAuth fix)
- **OS:** Windows 11 + PowerShell

### Sistema operativo:
- Windows 11
- PowerShell (no WSL)
- Usar `py` en lugar de `python`
- Paths con backslash `\`

---

## 📁 ARCHIVOS IMPORTANTES

### Control & Pipeline:
- `control_center.py` - Interface principal (331 líneas)
- `START_CONTROL_CENTER.bat` - Atajo doble-click
- `run_daily_pipeline.py` - Pipeline maestro
- `run_auto_apply.py` - Wrapper auto-apply (creado, pendiente implementación)

### Core Components:
- `core/ingestion/linkedin_scraper_V2.py` - LinkedIn scraper (FINAL)
- `core/automation/gmail_jobs_monitor_v2.py` - Gmail processor (346 líneas)
- `core/automation/job_bulletin_processor.py` - Bulletin processor (362 líneas)
- `core/enrichment/enrich_sheet_with_llm_v3.py` - AI analyzer
- `core/sheets/google_sheets_manager.py` - Sheets manager

### Interview Copilot:
- `interview_copilot_session_recorder.py` - Session recorder (467 líneas) ✅

### Documentation:
- `docs/PROJECT_STATUS.md` - Estado actualizado (este fue actualizado hoy)
- `docs/CONTROL_CENTER_GUIDE.md` - Guía Control Center
- `docs/INTERVIEW_COPILOT_SESSION_RECORDER.md` - Guía Copilot
- `docs/SOLUCION_DUPLICADOS.md` - Deduplicación
- `docs/JOB_EXPIRATION_SYSTEM.md` - Sistema expiración

### Logs:
- `logs/powershell/session_*.log` - PowerShell sessions
- `logs/interview_session_*.json` - Interview sessions
- Google Sheets URL: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

---

## 🚨 ERRORES ACTIVOS Y SUS FIXES

### 1. OAuth Client Deleted ❌ BLOQUEADOR CRÍTICO
**Error:** `google.auth.exceptions.RefreshError: deleted_client`

**Afecta:** Gmail, Bulletins, Deduplicación

**Fix (1 minuto):**
```powershell
py reauthenticate_gmail.py
# Acepta todos los permisos en navegador
```

### 2. AI Analysis Fix Pendiente ⚠️
**Error:** "Falta --sheet o SHEET_ID"

**Status:** Fix implementado pero NO probado

**Workaround:**
```powershell
py core\enrichment\enrich_sheet_with_llm_v3.py --sheet 1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg --cv data\cv_descriptor.txt
```

---

## 💡 WORKFLOW PARA AUTO-APPLY

### Fase 1: Preparación (15 min)
1. ✅ Verificar OAuth funciona
2. ✅ Ejecutar pipeline completo (obtener ofertas)
3. ✅ Verificar FIT SCORES altos (7+) en Sheets

### Fase 2: Desarrollo (2 horas)
4. Implementar detección de campos
5. Auto-fill con datos CV
6. Submit con confirmación
7. Update Sheets con status

### Fase 3: Testing (30 min)
8. Dry-run con 3 ofertas high-fit
9. Verificar datos correctos
10. Probar submit real con 1 oferta
11. Validar Sheets se actualiza

### Fase 4: Documentación (15 min)
12. Actualizar PROJECT_STATUS.md
13. Crear AUTO_APPLY_GUIDE.md
14. Agregar opción al Control Center

---

## 🎯 CRITERIOS DE ÉXITO

### Auto-Apply será considerado 100% cuando:

✅ **Detección de campos:**
- Identifica todos los campos del formulario
- Reconoce tipos (text, select, radio, etc.)
- Handle campos opcionales vs requeridos

✅ **Auto-fill:**
- Llena nombre, email, teléfono correctamente
- Maneja CV upload automáticamente
- Responde preguntas comunes (experiencia, sueldo, etc.)

✅ **Submit:**
- Dry-run muestra preview sin aplicar
- Confirmación antes de submit real
- Handle errores de red/timeout

✅ **Integration:**
- Update Google Sheets con status "Applied"
- Guarda timestamp de aplicación
- Logging completo de proceso

✅ **Testing:**
- Probado con al menos 5 ofertas reales
- Tasa éxito > 90%
- Cero aplicaciones con datos incorrectos

---

## 🔧 COMANDOS ÚTILES PARA ESTA SESIÓN

### Control Center:
```powershell
py control_center.py
# Usar Opciones 11-12 para auto-apply
```

### Auto-Apply directo:
```powershell
# Dry-run (preview sin aplicar)
py run_auto_apply.py --dry-run --fit-score 7

# Live apply (aplicar de verdad)
py run_auto_apply.py --live --fit-score 8 --max-applies 3
```

### Verificar resultados:
```powershell
# Ver aplicaciones en Sheets
py view_sheets_data.py

# O abrir Sheets en navegador
py control_center.py
# Opción 14
```

### Debug LinkedIn:
```powershell
# Test scraper con modo visual
py scripts\visual_test.py
```

---

## 📚 DOCUMENTACIÓN RELEVANTE

### Leer antes de empezar:
1. `docs/PROJECT_STATUS.md` - Estado completo actualizado
2. `docs/CONTROL_CENTER_GUIDE.md` - Cómo usar interface
3. `data/cv_descriptor.txt` - Datos para auto-fill

### Referencias técnicas:
- Playwright docs: https://playwright.dev/python/
- LinkedIn Easy Apply: Usar selectores específicos
- Google Sheets API: Ya implementado en `core/sheets/`

---

## 🎓 LECCIONES DEL CHAT ANTERIOR

### Qué funcionó bien:
- Control Center simplifica mucho el workflow
- Push-to-talk es mejor que grabación fija
- Deduplicación evita ofertas repetidas
- Local AI + Cloud fallback es optimal

### Qué aprendimos:
- OAuth tokens se borran y hay que re-autenticar
- JSON serialization requiere extraer .content de LLM responses
- Testing incremental es clave (un componente a la vez)
- Wrapping scripts centralizan path management

### Qué mejorar:
- Probar fixes en pipeline completo ANTES de migrar chat
- Documentar troubleshooting mientras desarrollamos
- Mantener logs más estructurados

---

## 🎯 MÉTRICAS ACTUALES

**Google Sheets:**
- Total Jobs: 16
- High Fit (7+): 2
- Average FIT: 7.7/10
- Con URLs: 2 (ambas activas)
- Sin URLs: 14

**Interview Copilot:**
- Sessions grabadas: 5
- Última: 2025-11-18 04:47 CST
- Status: 100% funcional

**Última verificación URLs:**
- Fecha: 2025-11-19 03:57 CST
- Verificados: 16
- Activos: 2 (100%)

---

## 🔮 PRÓXIMOS PASOS DESPUÉS DE AUTO-APPLY

### Alta prioridad:
1. Task Scheduler (ejecutar pipeline cada 6 horas)
2. Interview Copilot con screening questions
3. Cover letters automáticas mejoradas

### Media prioridad:
4. Analytics avanzado (dashboard mejorado)
5. Multi-board scraping optimization
6. Performance tuning

### Baja prioridad:
7. Multi-user support
8. Mobile notifications
9. API para integraciones

---

## 🏆 LOGROS HASTA AHORA

### Total líneas código nuevo: ~4,900
- Sesión 18 Nov: ~1,990 líneas
- Sesión 19 Nov: ~2,000 líneas
- Documentación: ~910 líneas

### Componentes completados: 10/13
- ✅ Control Center
- ✅ Session Recorder
- ✅ Deduplicación
- ✅ Bulletin Processor
- ✅ URL Verifier
- ✅ Dashboard
- ✅ Pipeline maestro
- ✅ Sistema expiración
- ✅ Google Sheets
- ✅ LinkedIn scraper
- ⏳ Auto-Apply (40% → 100%)
- ⏳ Cover Letters (60%)
- ⏳ Interview Copilot avanzado (15%)

---

## 💬 TONE & ESTILO DE RESPUESTA

### Marcos prefiere:
- Respuestas concisas y al punto
- Código funcional sobre arquitectura perfecta
- PowerShell scripts cuando sea posible
- Paths absolutos (no relativos)
- Emoji para clarity visual
- "py" en lugar de "python"

### Marcos NO quiere:
- Explicaciones muy largas
- Teoría sin práctica
- Comandos que no funcionan en Windows
- WSL/Linux-only solutions
- Respuestas que asumen conocimiento previo sin explicar

---

## 🚀 CHECKLIST INICIO NUEVO CHAT

### Antes de empezar con Auto-Apply:

- [ ] Pegar este prompt completo en nuevo chat
- [ ] Ejecutar `py reauthenticate_gmail.py` (OAuth fix)
- [ ] Ejecutar `py control_center.py` → Opción 1 (Pipeline)
- [ ] Verificar no hay errores
- [ ] Ver `py control_center.py` → Opción 14 (Sheets)
- [ ] Confirmar hay ofertas high-fit (7+) para aplicar
- [ ] Leer `data/cv_descriptor.txt` (datos para auto-fill)
- [ ] Revisar `docs/PROJECT_STATUS.md` (estado actualizado)

### Durante desarrollo Auto-Apply:

- [ ] Empezar con dry-run (no aplicar de verdad)
- [ ] Probar con 1 oferta primero
- [ ] Validar datos antes de submit
- [ ] Logging completo de cada paso
- [ ] Update Sheets después de cada aplicación
- [ ] Testing con al menos 5 ofertas reales
- [ ] Documentar en AUTO_APPLY_GUIDE.md

### Al finalizar:

- [ ] Update PROJECT_STATUS.md (92% → 95%)
- [ ] Agregar Auto-Apply al Control Center
- [ ] Crear script PowerShell para auto-apply
- [ ] Testing exhaustivo end-to-end
- [ ] Preparar PROMPT_NUEVO_CHAT.md para próxima sesión

---

## 📞 REFERENCIAS RÁPIDAS

**Google Sheets:**  
https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg

**LM Studio:**  
http://172.23.0.1:11434

**Dashboard:**  
http://localhost:8000 (`cd web && py serve_dashboard.py`)

**Proyecto:**  
C:\Users\MSI\Desktop\ai-job-foundry

**CV Descriptor:**  
C:\Users\MSI\Desktop\ai-job-foundry\data\cv_descriptor.txt

---

## 🎯 RESUMEN ULTRA-CORTO

### Estado:
- **Progreso:** 92%
- **Bloqueador:** OAuth fix (1 min)
- **Próximo:** Auto-Apply (2-3 hrs)

### Pasos inmediatos:
1. `py reauthenticate_gmail.py`
2. `py control_center.py` → Opción 1
3. Implementar auto-apply
4. Testing exhaustivo
5. Update docs

### Criterio éxito:
- ✅ Apply automático a ofertas high-fit
- ✅ Update Sheets con status "Applied"
- ✅ Testing con 5+ ofertas reales
- ✅ Tasa éxito > 90%

---

**Preparado:** 2025-11-19 08:15 CST  
**Para:** Nuevo chat enfocado en Auto-Apply  
**Progreso objetivo:** 92% → 95%  
**Tiempo estimado:** 2-3 horas  

**¡TODO LISTO PARA CONTINUAR! 🚀**