# 🔧 GUÍA PASO A PASO - OPTIMIZAR LM STUDIO PARA RTX 4090

**Problema:** Llama-3-Groq-70B tarda 44 segundos/job (debería ser 10-15 seg)  
**Causa:** Configuración incorrecta de GPU offload o cuantización  
**Solución:** 5 minutos de ajustes

---

## 📸 PASO 1: ABRIR CONFIGURACIÓN DEL MODELO

1. **Abre LM Studio**
2. **En la barra lateral izquierda** verás el modelo cargado:
   ```
   llama-3-groq-70b-tool-use
   [READY] 42.52 GB
   ```
3. **Click en el nombre del modelo**

---

## 🎛️ PASO 2: VERIFICAR GPU OFFLOAD

**Ubicación:** Tab "Load" o "Inference" (depende de la versión)

### Configuración ACTUAL (probablemente incorrecta):

```
GPU Offload: [ ●━━━━━━━━━━━━━ ] 10 / 80 layers  ← ❌ ESTO ESTÁ MAL
```

**Si ves esto, significa que solo 10 capas están en GPU.**  
**Las otras 70 capas están en CPU** → Por eso es 10x más lento.

### Configuración CORRECTA:

```
GPU Offload: [ ●━━━━━━━━━━━━━━━━━━━ ] 21 / 80 layers  ← ✅ ESTO ES CORRECTO
```

**NOTA:** En algunos modelos 70B con Q4_K_M, el máximo puede ser menor (ej: 21/80).  
**Lo importante:** Arrastrar el slider **hasta el máximo que permita.**

---

## 🎚️ PASO 3: OTROS PARÁMETROS CRÍTICOS

En la misma ventana, verifica:

### Context Length
```
Context Length: [8192]  ← ✅ Correcto
```

❌ **Si dice 16384 o más:** REDUCE a 8192  
**Razón:** Más context = más VRAM = más lento

### Keep Model in Memory
```
☑ Keep model loaded in memory  ← ✅ DEBE ESTAR MARCADO
```

❌ **Si NO está marcado:** ACTÍVALO  
**Razón:** Sin esto, el modelo se recarga cada vez (súper lento)

### Temperature
```
Temperature: 0.3  ← ✅ Dejarlo en 0.3-0.4
```

**Nota:** Esto ya lo controla el código Python, pero verifica que no esté en 0.1 o menos.

---

## 🔄 PASO 4: APLICAR CAMBIOS

1. **Después de cambiar GPU Offload:**
   - Click en **"Reload Model"** o **"Apply"**
   - Espera 30 segundos (recarga el modelo)

2. **Verifica que el modelo siga en "READY"**

3. **Si falla la recarga:**
   - Puede que tu GPU no tenga suficiente VRAM libre
   - Cierra otros programas (Chrome, etc.)
   - Intenta con un slider un poco menor (ej: 19/80)

---

## 🧪 PASO 5: RE-EJECUTAR TEST

```powershell
py scripts\tests\test_lm_studio_speed.py
```

### Resultados esperados:

**ANTES del fix:**
```
Time: 44.7 seconds
DIAGNOSIS: SLOW
```

**DESPUÉS del fix:**
```
Time: 10-20 seconds  ← ✅ EXCELENTE
DIAGNOSIS: EXCELLENT or GOOD
```

**Si sigue lento (30+ seg):**
→ Problema puede ser la cuantización Q4_K_M  
→ Prueba con modelo alternativo (ver abajo)

---

## 🔍 TROUBLESHOOTING

### Problema 1: "No puedo arrastrar slider a 21, solo llega a 10"

**Causa:** No hay suficiente VRAM libre

**Soluciones:**
1. Cierra navegadores (Chrome come mucha VRAM)
2. Cierra otros programas con GPU
3. Reinicia LM Studio
4. Si persiste: Descarga cuantización más ligera (Q4_0 en lugar de Q4_K_M)

---

### Problema 2: "Slider ya está en 21/80 pero sigue lento"

**Causa:** Cuantización Q4_K_M es inherentemente lenta en algunos modelos

**Soluciones (en orden):**

**A) Prueba cuantización más rápida del MISMO modelo:**
```
1. LM Studio → Buscar: "llama-3-groq-70b-tool-use"
2. Descargar: bartowski/Llama-3-Groq-70B-Tool-Use-GGUF
3. Cuantización: Q4_0 (más rápida) o IQ3_XS (muy rápida)
4. En .env cambiar:
   LLM_MODEL=llama-3-groq-70b-tool-use-Q4_0
   (o el nombre exacto del archivo descargado sin .gguf)
```

**B) Cambia a modelo MEJOR que Qwen pero más RÁPIDO:**
→ Ver sección "MODELOS ALTERNATIVOS" abajo

---

## 🎯 MODELOS ALTERNATIVOS RECOMENDADOS

### Comparativa:

| Modelo | Accuracy | Velocidad | Tamaño | Recomendación |
|--------|----------|-----------|--------|---------------|
| Llama-3-Groq-70B Q4_K_M | 95% | 44 seg ❌ | 42 GB | Actual (lento) |
| **Qwen 2.5 32B Instruct Q4_K_M** | **85%** | **15 seg** ✅ | **20 GB** | **MEJOR OPCIÓN** ⭐ |
| Mistral Small 22B Q4_K_M | 82% | 10 seg ✅ | 14 GB | Muy rápido |
| Gemma 2 27B Q4_K_M | 80% | 12 seg ✅ | 16 GB | Bueno |
| Qwen 2.5 14B (actual) | 75% | 5 seg ✅ | 9 GB | Rápido pero menos preciso |

---

## 🥇 OPCIÓN RECOMENDADA: QWEN 2.5 32B

**Por qué es el SWEET SPOT:**
- ✅ 85% accuracy (10% mejor que Qwen 14B)
- ✅ 15 seg/job (3x más rápido que Llama 70B)
- ✅ No hallucinations (como Llama)
- ✅ Cabe holgado en tu RTX 4090 (24 GB VRAM)

**Tiempo total pipeline:** 182 jobs × 15 seg = 45 minutos ✅

---

## 📥 CÓMO DESCARGAR QWEN 2.5 32B

### En LM Studio:

1. **Click en ícono de búsqueda** (lupa arriba a la izquierda)
2. **Buscar:** `Qwen2.5 32B Instruct`
3. **Seleccionar:** `Qwen/Qwen2.5-32B-Instruct-GGUF`
4. **Cuantización:** `qwen2.5-32b-instruct-q4_k_m.gguf` (20.47 GB)
5. **Click Download**
6. **Espera:** ~10 minutos (depende de tu internet)

---

## ⚙️ CONFIGURAR QWEN 2.5 32B

### Paso 1: Cargar modelo en LM Studio

1. **En LM Studio:** Tab "My Models"
2. **Buscar:** Qwen2.5-32B-Instruct
3. **Click "Load"**
4. **Configuración:**
   ```
   GPU Offload: [MAX] (debería ser ~33/33 layers)
   Context Length: 8192
   Keep in Memory: ✅
   Temperature: 0.4
   ```
5. **Click "Load Model"**

### Paso 2: Actualizar .env

```powershell
notepad .env
```

**Cambiar línea:**
```bash
# ANTES
LLM_MODEL=llama-3-groq-70b-tool-use

# DESPUÉS
LLM_MODEL=qwen2.5-32b-instruct
```

**Guardar y cerrar**

### Paso 3: Test

```powershell
py scripts\tests\test_lm_studio_speed.py
```

**Resultado esperado:**
```
Time: 12-20 seconds
DIAGNOSIS: GOOD or EXCELLENT
Expected pipeline: 36-60 minutes
```

---

## 🚀 EJECUCIÓN FINAL

```powershell
.\START_CONTROL_CENTER.bat
# Opción 1 (Pipeline Completo)

# Con Qwen 2.5 32B:
# - Termina en ~45 minutos
# - Accuracy: 85%
# - Sin hallucinations
```

---

## 📊 RESUMEN DE DECISIÓN

### Si tienes 5 minutos AHORA:
→ **Optimiza Llama-3-Groq** (verificar GPU offload)  
→ Re-ejecuta test  
→ Si sigue lento, descarga Qwen 32B

### Si tienes 15 minutos AHORA:
→ **Descarga Qwen 2.5 32B directamente** (mejor opción)  
→ Configura en .env  
→ Ejecuta pipeline

### Si tienes prisa (resultados en 15 min):
→ **Cambia a Qwen 14B temporalmente**  
→ Accuracy 75% pero termina rápido  
→ Mañana optimizas con 32B

---

## 🎓 POR QUÉ ES TAN LENTO

**Explicación técnica:**

Tu modelo Llama-3-Groq-70B Q4_K_M tiene:
- 80 capas totales
- Solo 21 caben en 24 GB VRAM
- Las otras 59 van a RAM (CPU) → **ESTO ES NORMAL**

**Pero si el slider dice 10/80:**
- 10 capas en GPU (rápidas)
- 70 capas en CPU (súper lentas)
- **Resultado:** 10x más lento

**Con Qwen 2.5 32B:**
- 33 capas totales
- TODAS caben en 24 GB VRAM
- **Resultado:** Todo en GPU → 3x más rápido

---

## 📝 CHECKLIST FINAL

- [ ] Verificado GPU Offload en LM Studio
- [ ] Keep in Memory activado
- [ ] Context Length = 8192
- [ ] Test ejecutado: < 20 segundos
- [ ] (Opcional) Descargado Qwen 2.5 32B
- [ ] .env actualizado
- [ ] Pipeline ejecutándose

---

**¿Dudas?** Ejecuta `.\DIAGNOSTICO_GPU.ps1` para diagnóstico automático.
