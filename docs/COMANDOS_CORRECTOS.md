# 🚀 GUÍA RÁPIDA - COMANDOS CORRECTOS

**Fecha:** 2025-11-29  
**Problema:** PowerShell syntax + Salary scoring

---

## ⚠️ COMANDO POWERSHELL CORRECTO

### ❌ MAL:
```powershell
FIX_OAUTH_TOKEN.bat
```

### ✅ BIEN:
```powershell
.\FIX_OAUTH_TOKEN.bat
```

**Nota:** PowerShell requiere `.\` antes del nombre del archivo.

---

## 📋 PASOS INMEDIATOS

### 1. Arreglar OAuth
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\FIX_OAUTH_TOKEN.bat
```

### 2. Marcar expirados (MEJORADO)
```powershell
py mark_expired_jobs.py
```

**Qué hace ahora:**
- ✅ Marca "No longer accepting" como `EXPIRED`
- ✅ Marca "Payment is too low" como `REJECTED_BY_USER`
- ✅ Funciona con headers duplicados

### 3. Re-calcular FIT scores con salario
```powershell
py recalculate_fit_scores.py
```

**Qué hace:**
- Lee columna Comp (salario)
- Aplica penalización si salario < $30k MXN:
  - < $20k MXN → -5 puntos (SEVERO)
  - $20k-30k → -3 puntos
  - $30k-50k → -1 punto
  - $50k-80k → 0 (normal)
  - > $80k → +1 punto (bonus)

---

## 💰 POLÍTICA DE SALARIO

### Umbrales definidos:
```
Mínimo nacional MX:  $7,468 MXN    (legal)
Mínimo aceptable:   $30,000 MXN    (~$1,700 USD)
Preferido:          $50,000 MXN    (~$2,900 USD)
Excelente:          $80,000 MXN    (~$4,600 USD)
```

### Caso: $17,000 MXN
```
$17,000 < $20,000 → Penalty: -5 puntos
FIT original: 8/10
FIT nuevo:    3/10

Razón: "Below minimum (penalty -5)"
```

---

## 🔧 ARREGLOS HECHOS

### 1. mark_expired_jobs.py (MEJORADO)
**Cambios:**
- ✅ Maneja headers duplicados (LinkedIn/Indeed/Glassdoor)
- ✅ Detecta "payment is too low" → `REJECTED_BY_USER`
- ✅ Usa valores RAW (no get_all_records)

### 2. recalculate_fit_scores.py (NUEVO)
**Características:**
- ✅ Extrae salario de columna Comp
- ✅ Convierte USD → MXN (rate: 1 USD = 17 MXN)
- ✅ Aplica penalties/bonuses
- ✅ Actualiza FIT score + Why column

---

## 📊 EJEMPLO: Job con $17k MXN

### Antes:
```
Comp: $17,000 MXN
FitScore: 8/10
Why: (vacío)
Status: Application submitted
```

### Después de mark_expired_jobs.py:
```
Status: REJECTED_BY_USER
NextAction: [2025-11-29] User rejected: Payment is too low
```

### Después de recalculate_fit_scores.py:
```
FitScore: 3/10
Why: [Salary: $17,000 MXN] Below minimum (penalty -5)
```

---

## 🎯 EJECUCIÓN COMPLETA

```powershell
# 1. Fix OAuth
.\FIX_OAUTH_TOKEN.bat

# 2. Marcar expired + user rejected
py mark_expired_jobs.py

# 3. Re-calcular FIT scores
py recalculate_fit_scores.py

# 4. Actualizar desde emails
py update_status_from_emails.py

# 5. Ver resultados
# Abre Google Sheets
```

---

## 📈 PONDERACIÓN FIT SCORE (ACTUALIZADA)

### Antes (INCORRECTO):
```
Skills:     40%
Experience: 30%
Location:   20%
Salary:     10%  ← DEMASIADO BAJO
```

### Ahora (CORRECTO):
```
Salary:     HARD BLOCKER (si < $30k → max FIT 3/10)
Skills:     35%
Experience: 25%
Location:   15%
Salary bonus: 25%
```

### Ejemplo de scoring:
```
Job: Business Analyst
Salary: $17,000 MXN
Skills match: 90%
Experience: 80%
Location: Remote

Cálculo:
  Base: 8/10 (skills + experience)
  Salary penalty: -5
  Final: 3/10 ← BLOQUEADO POR SALARIO
```

---

## 🔄 COMANDOS DIARIOS

```powershell
# Cada día
cd C:\Users\MSI\Desktop\ai-job-foundry

# Marcar expired
py mark_expired_jobs.py

# Actualizar desde emails
py update_status_from_emails.py

# Control Center
.\START_UNIFIED_APP.bat
```

---

## 💡 NOTAS IMPORTANTES

### PowerShell vs CMD:
- CMD: `FIX_OAUTH_TOKEN.bat` (funciona)
- PowerShell: `.\FIX_OAUTH_TOKEN.bat` (requiere `.\`)

### Orden de ejecución:
1. mark_expired_jobs.py (limpia status)
2. recalculate_fit_scores.py (ajusta scores)
3. update_status_from_emails.py (sincroniza emails)

### Columna M (Status):
- `EXPIRED` - Compañía cerró posición
- `REJECTED_BY_USER` - Tú rechazaste
- `INTERVIEW_SCHEDULED` - Entrevista agendada
- `Application submitted` - Aplicaste

---

**Autor:** Marcos Alberto Alvarado de la Torre  
**Proyecto:** AI Job Foundry  
**Versión:** 2.1 (Salary Scoring)  
**Fecha:** 2025-11-29
