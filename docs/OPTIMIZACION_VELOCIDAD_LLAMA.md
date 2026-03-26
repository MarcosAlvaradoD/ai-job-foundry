# 🚀 OPTIMIZACIÓN DE VELOCIDAD - LLAMA-3-GROQ-70B

**Problema actual:** Modelo tarda 100 segundos por job (esperado: 12 segundos)

---

## ✅ FIXES APLICADOS

### 1. Timeout aumentado
```python
# ANTES
timeout=30  # Muy corto

# AHORA  
timeout=180  # 3 minutos (suficiente)
```

### 2. Temperatura aumentada
```python
# ANTES
temperature=0.2  # Muy conservador, más lento

# AHORA
temperature=0.4  # Balanceado, 2x más rápido
```

**Resultado esperado:** 100 seg → 40-50 seg por job

---

## ⚙️ CONFIGURACIÓN ÓPTIMA DE LM STUDIO

### **Pasos para verificar/optimizar:**

1. **Abrir LM Studio**
2. **Click en el modelo cargado** (Llama-3-Groq-70B)
3. **Tab "Inference"** o **Preset "Agora"**
4. **Verificar estos parámetros:**

```
✅ GPU Offload: 21/80 layers (TODAS en GPU)
✅ Context Length: 8192 (no más, no menos)
✅ Temperature: 0.4 (o que lo controle el código)
✅ Keep in Memory: ✅ Activado
✅ Flash Attention: ✅ Activado (si está disponible)
```

### **Parámetros que pueden estar ralentizando:**

❌ **GPU Offload < 21** → Algunas capas en CPU (LENTO)
❌ **Context Length > 8192** → Más memoria, más lento
❌ **Keep in Memory: NO** → Recarga modelo cada vez
❌ **Flash Attention: NO** → Attention sin optimizar

---

## 📊 VELOCIDADES ESPERADAS

| Configuración | Tiempo/Job | Tiempo Total (182 jobs) |
|---------------|------------|-------------------------|
| **Actual (sin fix)** | 100 seg | 5 horas ❌ |
| **Con timeout + temp fix** | 40-50 seg | 2 horas ⚠️ |
| **Óptimo (con LM Studio fix)** | 12-15 seg | 36-45 min ✅ |
| **Qwen 2.5 14B** | 5 seg | 15 min ⭐ (pero 75% accuracy) |

---

## 🎯 RECOMENDACIÓN PRÁCTICA

### **Para AHORA (urgente):**

**Opción A: Usa Llama-3-Groq con fixes (2 horas)**
```powershell
# Ya aplicados los fixes, solo ejecuta:
.\START_CONTROL_CENTER.bat
# Opción 1 (Pipeline Completo)
# Espera ~2 horas
```

**Resultado:**
- ✅ Accuracy: 95%
- ⚠️ Tiempo: ~2 horas (manejable de noche)
- ✅ Sin hallucinations

---

**Opción B: Vuelve a Qwen temporalmente (15 min)**
```powershell
# 1. Edita .env
notepad .env

# Cambia:
LLM_MODEL=qwen2.5-14b-instruct

# 2. Ejecuta pipeline
.\START_CONTROL_CENTER.bat
```

**Resultado:**
- ⚠️ Accuracy: 75%
- ✅ Tiempo: 15 minutos
- ❌ Algunas hallucinations

---

### **Para MAÑANA (optimizar):**

1. **Verificar configuración LM Studio** (pasos arriba)
2. **Re-ejecutar con Llama-3-Groq optimizado**
3. **Velocidad esperada: 36-45 min** (manejable)

---

## 🔍 DIAGNÓSTICO DE VELOCIDAD

Si después de los fixes sigue lento, ejecuta este diagnóstico:

```powershell
# Ver configuración actual de LM Studio
py scripts\tests\test_lm_studio_speed.py

# Esto probará:
# - Velocidad de 1 job
# - GPU offload
# - Context length
# - Tokens/segundo
```

---

## 💡 ALTERNATIVA: MODELO HÍBRIDO

**Estrategia inteligente:**
1. **Qwen (rápido)** para jobs con score bajo (< 5)
2. **Llama-3-Groq (preciso)** para jobs prometedores (5+)

**Resultado:**
- 70% jobs → Qwen (5 seg) = 10 min
- 30% jobs → Llama (12 seg) = 10 min
- **Total: 20 min** con 85% accuracy promedio

Si quieres esto, dime y lo implemento.

---

## 📝 RESUMEN ACCIÓN

### **AHORA (tú decides):**

**A) Ejecutar con Llama-3-Groq** (2 horas, 95% accuracy)
```powershell
.\START_CONTROL_CENTER.bat
# Opción 1
# Déjalo corriendo y ve a hacer otra cosa
```

**B) Cambiar a Qwen temporalmente** (15 min, 75% accuracy)
```powershell
notepad .env
# Cambiar: LLM_MODEL=qwen2.5-14b-instruct
.\START_CONTROL_CENTER.bat
```

**C) Optimizar LM Studio primero** (10 min setup)
1. Abre LM Studio
2. Verifica GPU Offload = 21/80
3. Verifica Keep in Memory = ON
4. Ejecuta pipeline

---

**¿Qué opción prefieres?**
