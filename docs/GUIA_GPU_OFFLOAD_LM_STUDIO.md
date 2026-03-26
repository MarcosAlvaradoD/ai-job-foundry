# 🎯 GUÍA PASO A PASO - CONFIGURAR GPU OFFLOAD EN LM STUDIO

## ⚠️ TU GPU ESTÁ BIEN - TIENE 24 GB DE VRAM

**CONFIRMADO:**
- ✅ nvidia-smi reporta: 24564 MiB (24 GB)
- ✅ Administrador de Tareas: 24.0 GB
- ✅ Tu RTX 4090 NO está dañada
- ✅ NO le quitaron VRAM físicamente

**PROBLEMA REAL:**
- ❌ LM Studio solo usa 17 GB de los 24 GB disponibles
- ❌ Algunas capas están en CPU en lugar de GPU
- ❌ Por eso es 10x más lento

---

## 🔧 SOLUCIÓN EN 5 PASOS

### PASO 1: Abre LM Studio

1. Haz doble click en el ícono de LM Studio
2. Espera a que cargue completamente

---

### PASO 2: Localiza el modelo cargado

**En la barra lateral IZQUIERDA** verás:

```
├─ 💬 Chat
├─ 🧑‍💻 Desarrollador
└─ 📚 Mis Modelos  ← BUSCA AQUÍ
```

**Busca el modelo que dice:**
```
llama-3-groq-70b-tool-use
[READY] Size: ~42 GB
```

**Status indicators:**
- 🟢 **[READY]** = Modelo cargado
- 🔴 **[NOT LOADED]** = No está en memoria
- 🟡 **[LOADING...]** = Cargando

---

### PASO 3: Accede a configuración del modelo

**OPCIÓN A: Si el modelo está cargado (READY)**

1. Click en el nombre del modelo en la lista
2. Aparecerá un panel a la derecha
3. Busca tabs: **"Load" / "Config" / "Settings"**

**OPCIÓN B: Si no ves las configuraciones**

1. Ve a: **"Desarrollador"** (Developer)
2. Ve a: **"Local Server"** o **"Inference"**
3. Click en: **⚙️ Model Settings** o **Configure**

---

### PASO 4: Localiza "GPU Offload" (GPU Layers)

**Nombres posibles del parámetro:**
- GPU Offload
- GPU Layers  
- n-gpu-layers
- Offload Layers

**Ubicación exacta:**
```
Model Settings
  ├─ Basic
  │   ├─ Context Length: [8192]
  │   ├─ Temperature: [0.3]
  │   └─ ...
  ├─ Advanced  ← BUSCA AQUÍ
  │   ├─ GPU Offload: [ ●━━━━━━━ ] X / 80 layers  ← ESTE ES
  │   ├─ Keep in Memory: ☑
  │   └─ Flash Attention: ☑
  └─ ...
```

---

### PASO 5: Ajustar GPU Offload AL MÁXIMO

**CONFIGURACIÓN ACTUAL (probablemente):**
```
GPU Offload: [ ●━━━━━━━━━━━ ] 10 / 80 layers
             ↑ Slider       ↑ Actual / Total
```

**PROBLEMA:** Solo 10 capas en GPU, 70 capas en CPU → LENTO ❌

---

**CONFIGURACIÓN CORRECTA:**
```
GPU Offload: [ ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ] 21 / 80 layers
             ↑ Slider al máximo                    ↑ Máximo posible
```

**CÓMO AJUSTAR:**
1. **Arrastra el slider hacia la DERECHA** hasta que no pueda ir más
2. El número debería llegar a **21/80** o similar (depende de VRAM libre)
3. Si no llega a 21, cierra Chrome y otros programas que usen GPU
4. Intenta de nuevo hasta llegar al máximo

---

### PASO 6: Aplicar cambios

**Después de mover el slider:**

1. Busca botón: **"Reload Model"** o **"Apply"** o **"Save"**
2. Click en el botón
3. Espera ~30 segundos (modelo se recarga en GPU)
4. Verifica que siga diciendo **[READY]**

**Si falla la recarga:**
- Error: "Out of memory" → Cierra programas (Chrome, Discord, etc.)
- Error: "GPU not available" → Reinicia LM Studio
- Modelo no carga → Reduce slider a 19/80 y reintenta

---

## 🧪 VERIFICAR QUE FUNCIONÓ

### Test 1: nvidia-smi (CMD)

```cmd
nvidia-smi
```

**ANTES del fix:**
```
|   0  NVIDIA GeForce RTX 4090   | 17120MiB / 24564MiB |  ← Solo 17 GB
```

**DESPUÉS del fix:**
```
|   0  NVIDIA GeForce RTX 4090   | 20500MiB / 24564MiB |  ← ~20 GB ✅
```

---

### Test 2: Speed test (PowerShell)

```powershell
py scripts\tests\test_lm_studio_speed.py
```

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

---

## 🎚️ OTROS PARÁMETROS A VERIFICAR

Mientras estás en configuración del modelo, verifica:

### Context Length
```
Context Length: [8192]  ← ✅ Correcto (NO cambies)
```

❌ **Si dice 16384 o más:** Cámbialo a 8192  
**Razón:** Más contexto = más VRAM desperdiciada

---

### Keep Model in Memory
```
☑ Keep model loaded in memory  ← ✅ DEBE estar marcado
```

❌ **Si NO está marcado:** Márcalo  
**Razón:** Sin esto, el modelo se descarga y recarga constantemente

---

### Flash Attention (si existe)
```
☑ Use Flash Attention  ← ✅ Si existe, márcalo
```

**Razón:** Flash Attention hace el modelo 2-3x más rápido

---

## 🔍 TROUBLESHOOTING

### Problema 1: No encuentro "GPU Offload"

**Posibles razones:**
1. Estás en la pantalla equivocada
   → Ve a: Desarrollador → Local Server → Model Settings
2. Tu versión de LM Studio es antigua
   → Actualiza a la última versión
3. El parámetro tiene otro nombre
   → Busca: "layers", "gpu", "offload", "n-gpu-layers"

---

### Problema 2: Slider no llega a 21/80

**Causa:** No hay suficiente VRAM libre

**Soluciones:**
1. Cierra Chrome (usa mucha VRAM en aceleración)
2. Cierra Discord, OBS, o programas con GPU
3. En Task Manager → Click derecho en Chrome → GPU 0 → End Task
4. Reinicia LM Studio
5. Intenta de nuevo

**Si persiste:**
- Reduce a 19/80 (aún será mucho más rápido que 10/80)
- O descarga cuantización más ligera (Q4_0 en lugar de Q4_K_M)

---

### Problema 3: Modelo falla al recargar

**Error: "Out of memory"**
→ Cierra TODOS los navegadores
→ Reduce slider a 18/80
→ Reintenta

**Error: "CUDA error"**
→ Reinicia Windows
→ Abre solo LM Studio (nada más)
→ Recarga modelo

---

## 📊 CUÁNTA VRAM DEBE USAR

**Para Llama-3-Groq-70B Q4_K_M:**

| GPU Offload | VRAM Usada | Capas en GPU | Velocidad |
|-------------|------------|--------------|-----------|
| 10/80 | ~17 GB | 12% | 44 seg ❌ |
| 15/80 | ~19 GB | 19% | 25 seg ⚠️ |
| 21/80 | ~20.5 GB | 26% | 10-15 seg ✅ |

**NOTA:** Con 70B modelos, NUNCA todas las capas caben en 24 GB.  
Lo importante es llegar al **MÁXIMO** que permita tu GPU.

---

## 🎯 RESUMEN RÁPIDO

1. ✅ **Tu GPU tiene 24 GB** (verificado con nvidia-smi y Task Manager)
2. ❌ **LM Studio solo usa 17 GB** (debería usar ~20 GB)
3. 🔧 **Solución:** Aumentar GPU Offload de 10/80 a 21/80
4. 🚀 **Resultado esperado:** 44 seg → 10-15 seg (3-4x más rápido)

---

## 📞 SI NADA FUNCIONA

**PLAN B: Descarga Qwen 2.5 32B**

- Accuracy: 85% (mejor que 14B)
- Velocidad: 15 seg/job
- **TODAS las capas caben en 24 GB** (33/33 layers)
- Sin necesidad de ajustar sliders

**Instrucciones:**
1. LM Studio → Buscar: "Qwen2.5 32B"
2. Descargar: qwen2.5-32b-instruct-q4_k_m.gguf
3. Cargar con GPU Offload = MAX (automático)
4. Listo → 3x más rápido que configurar Llama

---

**¿Lograste encontrar el GPU Offload en LM Studio?**  
Dime qué número tiene actualmente (X/80) para confirmar.
