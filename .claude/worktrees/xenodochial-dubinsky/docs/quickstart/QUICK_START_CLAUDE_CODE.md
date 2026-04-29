# 🎯 QUICK START - CLAUDE CODE

**Copy-paste este comando en Claude Code para empezar:**

---

## 📋 CONTEXTO ULTRA-RÁPIDO

Proyecto AI Job Foundry al 94%. OAuth ✅ resuelto. **PROBLEMA CRÍTICO:** 87.5% de jobs sin URLs.

---

## ⚡ COMANDO INICIAL

```bash
cd ~/Desktop/ai-job-foundry && python investigate_urls.py
```

Esto diagnostica por qué faltan URLs.

---

## 🔍 ARCHIVOS A REVISAR

**1. core/automation/gmail_jobs_monitor_v2.py**
- Email processor principal
- Buscar: extracción de URLs

**2. core/automation/job_bulletin_processor.py**  
- Procesa boletines
- Verificar: URLs individuales

---

## 🎯 OBJETIVOS

1. **URGENTE:** Fix extracción de URLs (de 12.5% a >90%)
2. **MEDIO:** Estandarizar status (`python standardize_status_v2.py`)
3. **SIGUIENTE:** Auto-apply básico

---

## 📊 MÉTRICAS ACTUALES

- Total jobs: 16
- Con URLs: 2 (12.5%) ❌
- Sin URLs: 14 (87.5%)
- Status: 14 "ParsedOK", 2 vacíos

---

## 💡 TIP

SheetManager API correcto:
```python
jobs = sm.get_all_jobs(tab="registry")  # NOT get_all_jobs_from_tab!
```

---

## 📖 DOCS COMPLETAS

Ver: `CLAUDE_CODE_PROMPT.md` para guía completa (359 líneas)

---

**¡Adelante! Prioridad: URLs faltantes**
