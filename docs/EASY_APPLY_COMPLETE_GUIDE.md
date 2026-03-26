# 🎯 EASY APPLY COMPLETO - GUÍA DE USO

## 📋 QUÉ HACE EL SISTEMA

El sistema **auto_apply_linkedin_easy_complete.py** automatiza **TODO** el proceso de Easy Apply de LinkedIn:

### ✅ Funcionalidad Completa:

1. **Detecta Easy Apply** - Encuentra el botón automáticamente
2. **Hace clic** - Inicia el proceso
3. **Llena Contact Info** - Email, teléfono, ubicación
4. **Sube CV** - Selecciona tu resume automáticamente
5. **Responde Screening Questions** - Proficiency, experiencia, salary, etc.
6. **Navega páginas** - Next → Next → Review → Submit
7. **Envía aplicación** - Submit final
8. **Actualiza Sheets** - Marca como "Applied"

---

## 🚀 CÓMO USAR

### Opción 1: Desde Control Center (RECOMENDADO)

```powershell
py control_center.py
```

Luego selecciona:
- **12a** = DRY RUN (simula, no aplica)
- **12b** = LIVE (aplica realmente)

### Opción 2: Desde línea de comandos

```powershell
# DRY RUN
py core/automation/auto_apply_linkedin_easy_complete.py --min-fit 8 --max-jobs 5

# LIVE
py core/automation/auto_apply_linkedin_easy_complete.py --live --min-fit 8 --max-jobs 3
```

---

## ⚙️ PARÁMETROS

- `--min-fit` - FIT score mínimo (0-10, default: 7)
- `--max-jobs` - Máximo de jobs a procesar (default: 5)
- `--live` - Modo LIVE (sin esto = DRY RUN)

---

## 📝 TUS DATOS (CV_DATA)

El sistema usa estos datos en `core/automation/auto_apply_linkedin_easy_complete.py`:

```python
CV_DATA = {
    "first_name": "Marcos",
    "last_name": "Alvarado",
    "email": "markalvati@gmail.com",
    "phone": "3323320358",
    "resume_path": r"C:\...\Alvarado Marcos.pdf",
    
    # Screening answers
    "english_proficiency": "Professional",
    "work_authorization_mexico": "Yes",
    "salary_expectation_mxn": "50000",
    "python_experience": "Yes",
    "erp_experience": "Yes",
    # ... más respuestas
}
```

**⚠️ IMPORTANTE:** Si cambias tus datos (email, teléfono, salary), edita ese archivo.

---

## 🎯 EJEMPLO DE USO

### DRY RUN (Primero siempre)

```powershell
py core/automation/auto_apply_linkedin_easy_complete.py --min-fit 8 --max-jobs 1
```

Verás algo como:

```
🎯 Processing: Project Manager at GlobalLogic
   URL: https://linkedin.com/jobs/view/...
   ✅ Page loaded
   ✅ Clicked Easy Apply
   📝 Filling contact info...
      ✓ Email: markalvati@gmail.com
      ✓ Phone: 3323320358
   📄 Checking resume...
      ✓ Resume already uploaded
   ❓ Answering screening questions...
      Q: What is your level of proficiency in English?
         A: Professional
      Q: Are you available to travel to Sweden...
         A: Yes
      Q: What is your salary expectation...
         A: 50000
   ➡️  Clicked Next
   ➡️  Clicked Next
   🎯 [DRY RUN] Would submit application

✅ SUCCESS: Project Manager
```

### LIVE (Cuando DRY RUN funcione)

```powershell
py core/automation/auto_apply_linkedin_easy_complete.py --live --min-fit 8 --max-jobs 3
```

Esto **SÍ aplicará realmente**.

---

## 🔧 TROUBLESHOOTING

### "❌ Easy Apply button not found"

**Solución:**
- El job NO es Easy Apply
- Es aplicación externa (redirige a otra página)
- El sistema solo funciona con Easy Apply

### "⚠️ Could not fill answer"

**Solución:**
- Pregunta nueva que no conocemos
- Edita `_match_screening_answer()` en el código
- Agrega el keyword de la pregunta

### "❌ Navigation failed"

**Solución:**
- URL expiró
- LinkedIn bloqueó temporalmente
- Espera 5-10 minutos y reinténtalo

---

## 📊 ESTADÍSTICAS ESPERADAS

**Tasa de éxito:** 80-90% para Easy Apply

**Tiempo por aplicación:** 30-60 segundos

**Límite LinkedIn:** ~20-30 aplicaciones/día (recomendado no más de 10)

---

## 🎓 RESPUESTAS A SCREENING QUESTIONS

El sistema responde automáticamente basado en keywords:

| Pregunta contiene... | Responde...  |
|----------------------|--------------|
| "english", "proficiency" | "Professional" |
| "relocate", "relocation" | "No" |
| "remote", "work from home" | "Yes" |
| "travel" | "Yes" |
| "salary", "compensation" | "50000" (MXN) |
| "python" | "Yes" |
| "erp" | "Yes" |
| "banking" | "Yes" |
| "aviation" | "No" |

---

## 💡 RECOMENDACIONES

### 1. Empieza conservador

```powershell
# Primera vez
--min-fit 9 --max-jobs 1

# Después
--min-fit 8 --max-jobs 3

# Cuando confíes
--min-fit 7 --max-jobs 10
```

### 2. Revisa Google Sheets después

Verifica que Status = "Applied"

### 3. Actualiza salary según el job

Para USA jobs: edita `salary_expectation_usd` en CV_DATA

### 4. No abuses

LinkedIn detecta bots si aplicas a 50+ jobs/día

---

## 🔥 PRÓXIMAS MEJORAS (Futuro)

- [ ] Soportar aplicaciones externas (no solo Easy Apply)
- [ ] Cover letter personalizado por job
- [ ] Video recording para responder video questions
- [ ] Detección de "Already applied" para skip

---

## 📞 SOPORTE

Si algo no funciona:

1. Corre en DRY RUN primero
2. Revisa logs en consola
3. Toma screenshot del error
4. Abre el archivo y edita `_match_screening_answer()` para nuevas preguntas

---

**Última actualización:** 2026-01-28
**Autor:** Marcos Alberto Alvarado
**Proyecto:** AI Job Foundry
