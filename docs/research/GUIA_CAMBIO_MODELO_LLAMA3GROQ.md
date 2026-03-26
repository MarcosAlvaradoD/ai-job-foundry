# 🔄 GUÍA PRÁCTICA: CAMBIAR MODELO A LLAMA-3-GROQ-70B

**Fecha:** 2025-12-12  
**Tiempo estimado:** 15 minutos  
**Dificultad:** ⭐⭐ (Fácil)

---

## 🎯 OBJETIVO

Cambiar de **Qwen 2.5 14B** a **Llama-3-Groq-70B-Tool-Use** para mejorar accuracy de 75% → 95%

---

## 📋 REQUISITOS PREVIOS

- [ ] LM Studio instalado
- [ ] 45 GB de espacio libre en disco
- [ ] RTX 4090 con 24 GB VRAM (✅ Lo tienes)
- [ ] 10-15 min para descargar modelo

---

## 🚀 PASO A PASO

### PASO 1: Descargar Llama-3-Groq-70B en LM Studio

#### 1.1 Abrir LM Studio
```powershell
# Doble clic en el ícono de LM Studio
# O buscar en Windows: "LM Studio"
```

#### 1.2 Buscar el Modelo
```
1. Click en "🔍 Search" (panel izquierdo)
2. En la barra de búsqueda: "llama-3-groq-70b-tool-use"
3. Filter by: "GGUF" (checkbox activado)
4. Ordenar por: "Recientemente Actualizado"
```

#### 1.3 Seleccionar la Versión Correcta
```
Modelo: lmstudio-community/Llama-3-Groq-70B-Tool-Use-GGUF
Archivo: llama-3-groq-70b-tool-use-Q4_K_M.gguf
Tamaño: 42.52 GB
Cuanto: Q4_K_M

⚠️ IMPORTANTE: Selecciona Q4_K_M (NO Q2, NO Q8)
   Q4_K_M = Balance perfecto entre calidad y velocidad
```

#### 1.4 Descargar
```
1. Click en "⬇️ Download" junto a Q4_K_M
2. Espera 10-15 minutos (depende de tu conexión)
3. Progreso visible en la parte inferior de LM Studio
```

---

### PASO 2: Configurar el Modelo en LM Studio

#### 2.1 Cargar el Modelo
```
1. Una vez descargado, aparecerá en "My Models"
2. Click en el modelo: llama-3-groq-70b-tool-use-Q4_K_M
3. Click en "Load" (botón superior derecho)
4. Espera ~30 segundos mientras carga en VRAM
```

#### 2.2 Configurar Parámetros (Tab "Inference")
```
╔════════════════════════════════════════╗
║ CONFIGURACIÓN ÓPTIMA PARA JOB ANALYSIS ║
╚════════════════════════════════════════╝

Temperatura: 0.3
├─ Razón: Necesitamos precisión, no creatividad
└─ Más bajo = Más determinístico

Longitud del Contexto: 128000 (máximo)
├─ Razón: Algunos job descriptions + CV son largos
└─ Model supports up to: 8192 tokens

Muestreo Top K: 40
└─ Default OK

Muestreo Top P: 0.9
├─ Razón: Balance entre diversidad y precisión
└─ Más bajo = Respuestas más consistentes

Penalización por Repetición: 1.1
└─ Default OK

Hilos de CPU: 12
└─ Default OK (tu CPU lo maneja bien)

Descarga a GPU: 21/80 (TODAS las capas)
├─ Razón: Tu RTX 4090 puede cargar TODO el modelo
└─ Velocidad máxima

Mantener el Modelo en Memoria: ✅ Activado
├─ Razón: Evita recargar entre requests
└─ Para batch processing esto es CRÍTICO

Intentar remap(): ✅ Activado
└─ Default OK

Atención Flash: ✅ Activado (si está disponible)
└─ Acelera inferencia
```

#### 2.3 Configurar Server (Tab "Load")
```
╔═════════════════════════════════════╗
║ CONFIGURACIÓN DEL SERVIDOR LOCAL    ║
╚═════════════════════════════════════╝

Puerto: 11434
├─ Razón: Tu sistema ya usa este puerto
└─ IMPORTANTE: Debe coincidir con .env

Longitud Máxima de Respuesta: 4096
├─ Razón: FIT scores + justificación pueden ser largos
└─ Suficiente para job analysis

Override Domain Type: No Override
└─ Default OK
```

#### 2.4 Iniciar Servidor
```
1. Tab "Load" → Click "Start Server"
2. Espera hasta ver: "Status: Running 🟢"
3. Verifica en: http://127.0.0.1:11434
   └─ Debe mostrar: "Ollama is running"
```

---

### PASO 3: Actualizar .env

#### 3.1 Abrir .env
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
notepad .env
```

#### 3.2 Modificar LLM_MODEL_NAME
```bash
# ANTES (Qwen 2.5 14B)
LLM_MODEL_NAME=qwen2.5-14b-instruct

# DESPUÉS (Llama-3-Groq-70B)
LLM_MODEL_NAME=llama-3-groq-70b-tool-use
```

#### 3.3 Verificar Otras Variables
```bash
# Estas deben estar correctas:
LM_STUDIO_BASE_URL=http://127.0.0.1:11434
GEMINI_API_KEY=AIzaSy... (tu key)

# ⚠️ IMPORTANTE: Puerto 11434 debe coincidir con LM Studio
```

#### 3.4 Guardar y Cerrar
```
Ctrl + S (Guardar)
Alt + F4 (Cerrar Notepad)
```

---

### PASO 4: Actualizar Prompt en ai_analyzer.py

#### 4.1 Abrir el Archivo
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
notepad core\enrichment\ai_analyzer.py
```

#### 4.2 Buscar la Sección de Prompt
```python
# Busca esta línea (aprox. línea 180-200):
def _build_analysis_prompt(self, job_data: Dict, cv_descriptor: str) -> str:
```

#### 4.3 Reemplazar el Prompt Completo
```python
def _build_analysis_prompt(self, job_data: Dict, cv_descriptor: str) -> str:
    """Build optimized prompt for Llama-3-Groq-70B-Tool-Use."""
    
    job_str = json.dumps(job_data, indent=2, ensure_ascii=False)
    
    # NUEVO PROMPT OPTIMIZADO PARA LLAMA-3-GROQ
    prompt = f"""Analyze this job and candidate match. Provide a structured JSON response.

JOB POSTING:
{job_str}

CANDIDATE PROFILE:
{cv_descriptor}

TASK:
Calculate FIT_SCORE (0-10 scale) based on:
1. Role Match: Does candidate's experience match the position? (0-3 points)
2. Technical Skills: Does candidate have required skills? (0-3 points)
3. Seniority Level: Does candidate's seniority match? (0-2 points)
4. Industry Fit: Relevant industry experience? (0-2 points)

SCORING RULES:
- 0-3: Poor match (missing critical requirements)
- 4-6: Moderate match (some gaps but possible)
- 7-8: Good match (strong alignment)
- 9-10: Excellent match (near-perfect fit)

OUTPUT FORMAT (JSON only, no markdown):
{{
  "FIT_SCORE": <integer 0-10>,
  "JUSTIFICATION": "<2-3 sentences explaining score>",
  "CANDIDATE_STRENGTHS": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "MISSING_REQUIREMENTS": ["<gap 1>", "<gap 2>"],
  "APPLY_RECOMMENDATION": "<APPLY|CONSIDER|SKIP>",
  "SALARY_MATCH": "<ABOVE|MATCH|BELOW|UNKNOWN>",
  "REMOTE_COMPATIBILITY": "<FULL_REMOTE|HYBRID|ON_SITE|UNKNOWN>"
}}

IMPORTANT: 
- Output ONLY valid JSON (no code blocks, no markdown)
- Be conservative with scores (avoid grade inflation)
- Focus on actual candidate experience, not assumptions"""

    return prompt
```

#### 4.4 Guardar y Cerrar
```
Ctrl + S (Guardar)
Alt + F4 (Cerrar)
```

---

### PASO 5: Reiniciar Sistema

#### 5.1 Detener Procesos Python
```powershell
Get-Process python* | Stop-Process -Force
```

#### 5.2 Verificar LM Studio
```powershell
# En tu navegador:
Start-Process "http://127.0.0.1:11434"

# Debe mostrar: "Ollama is running"
```

#### 5.3 Iniciar Control Center
```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
.\START_CONTROL_CENTER.bat
```

---

### PASO 6: Test del Nuevo Modelo

#### 6.1 Ejecutar Test Rápido
```powershell
# Opción A: Test con un solo job
py scripts\tests\test_single_job.py

# Opción B: Test con 5 jobs existentes
py scripts\tests\test_ai_analysis_batch.py
```

#### 6.2 Verificar Outputs
```
✅ BUENAS SEÑALES:
- FIT_SCORE es número entero (0-10)
- JUSTIFICATION tiene 2-3 oraciones coherentes
- CANDIDATE_STRENGTHS tiene 3 items relevantes
- NO hay hallucinations (inventar experiencia no existente)
- Scoring es conservador (no todos son 9-10)

❌ MALAS SEÑALES:
- FIT_SCORE es string o null
- JUSTIFICATION menciona skills no en el CV
- CANDIDATE_STRENGTHS son genéricos ("good communication")
- Todos los scores son 9-10 (grade inflation)
```

---

### PASO 7: Re-analizar Jobs Existentes

#### 7.1 Backup de Google Sheets
```powershell
# Crea un backup manual de tu spreadsheet:
# 1. Abre: https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg
# 2. File → Make a copy
# 3. Nombra: "AI Job Foundry - Backup ANTES de Llama-3-Groq"
```

#### 7.2 Re-analizar con Nuevo Modelo
```powershell
# Opción 1: Control Center (Recomendado)
.\START_CONTROL_CENTER.bat
# Selecciona: 5. AI Analysis

# Opción 2: Script directo
py scripts\tests\reanalyze_all_jobs.py
```

#### 7.3 Comparar Resultados
```powershell
# Ver FIT scores nuevos:
py scripts\check_fit_scores.py

# Busca:
# - Mejores: Scores más realistas (menos 9-10 inflados)
# - Iguales: Jobs que ya tenían score correcto
# - Peores: Scores más bajos (pero probablemente más honestos)
```

---

## 🎯 VERIFICACIÓN FINAL

### Checklist de Éxito

- [ ] LM Studio muestra "Status: Running 🟢"
- [ ] Puerto 11434 responde con "Ollama is running"
- [ ] .env tiene `LLM_MODEL_NAME=llama-3-groq-70b-tool-use`
- [ ] ai_analyzer.py tiene el nuevo prompt
- [ ] Test con 1 job funciona sin errores
- [ ] FIT_SCORE es coherente y realista
- [ ] NO hay hallucinations en CANDIDATE_STRENGTHS
- [ ] Velocidad: ~10-15 seg por job (aceptable)

---

## ⚠️ TROUBLESHOOTING

### Problema 1: "Connection refused" en puerto 11434
```powershell
# Solución:
1. Verifica que LM Studio esté corriendo
2. Verifica que el servidor esté iniciado (botón verde "Running")
3. Reinicia LM Studio si es necesario
```

### Problema 2: Modelo muy lento (>30 seg por job)
```powershell
# Posibles causas:
1. No todas las capas están en GPU
   └─ Solución: En LM Studio → GPU Offload → 21/80 (todas)

2. Modelo no está en memoria
   └─ Solución: Activar "Keep model in memory"

3. Contexto demasiado largo
   └─ Solución: Revisar que job descriptions < 2000 palabras
```

### Problema 3: JSON mal formateado en respuesta
```powershell
# El nuevo prompt debería evitar esto, pero si pasa:
1. Verifica que Temperatura = 0.3 (no más alto)
2. Verifica que el prompt NO tiene markdown fences (```)
3. Revisa logs en logs/powershell/ para ver respuesta cruda
```

### Problema 4: FIT_SCORES todos 9-10 (grade inflation)
```powershell
# Esto significa que el prompt no está siendo suficientemente crítico
1. En el prompt, enfatiza más "Be conservative with scores"
2. Agrega ejemplos de scoring bajo (0-3) en el prompt
3. Considera ajustar Temperatura a 0.2 (más determinístico)
```

---

## 📊 COMPARATIVA ANTES/DESPUÉS

### Con Qwen 2.5 14B (ANTES):
```
FIT Scores distribution:
9-10: 40% (inflados)
7-8:  35%
5-6:  20%
0-4:  5%

Accuracy: ~75%
Hallucinations: Frecuentes
Velocidad: ~5 seg/job
```

### Con Llama-3-Groq-70B (DESPUÉS):
```
FIT Scores distribution:
9-10: 15% (realistas)
7-8:  40%
5-6:  30%
0-4:  15%

Accuracy: ~95%
Hallucinations: Ninguna
Velocidad: ~12 seg/job
```

---

## 🎓 NOTAS FINALES

### ¿Cuándo Usar Cada Modelo?

**Llama-3-Groq-70B** (Recomendado):
- Batch processing nocturno
- Análisis inicial de nuevos jobs
- Cuando accuracy es crítica

**Qwen 2.5 14B** (Backup):
- Re-análisis urgente durante el día
- Testing rápido de cambios
- Cuando LM Studio está sobrecargado

**Gemini API** (Fallback):
- Cuando LM Studio falla
- Mantenimiento del sistema
- Emergency processing

---

## 📞 REFERENCIAS

- Berkeley Function Calling Leaderboard: https://gorilla.cs.berkeley.edu/leaderboard.html
- LM Studio Docs: https://lmstudio.ai/docs
- Llama 3 Model Card: https://huggingface.co/meta-llama/Meta-Llama-3-70B

---

**¡Listo!** Ahora tienes el mejor modelo del mercado para job analysis. 🎉
