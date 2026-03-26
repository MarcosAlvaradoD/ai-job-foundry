# 🔧 FIX UNICODE ERROR - EXPIRE_LIFECYCLE

**Problema identificado:**
```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-1
```

Esto ocurre cuando EXPIRE_LIFECYCLE.py intenta imprimir emojis en Windows PowerShell.

## 🎯 SOLUCIÓN RÁPIDA

### Opción 1: Fix Automático con Script PowerShell (Recomendado)

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py scripts\maintenance\fix_unicode_expire.py
```

Este script:
1. Lee EXPIRE_LIFECYCLE.py
2. Reemplaza todos los emojis con texto ASCII
3. Guarda el archivo fixeado

### Opción 2: Fix Manual

Abre: `C:\Users\MSI\Desktop\ai-job-foundry\scripts\verifiers\EXPIRE_LIFECYCLE.py`

Busca línea 163 (aproximadamente):
```python
# ANTES (con emoji)
print("\U0001f5d1\ufe0f  DELETING EXPIRED JOBS")

# DESPUÉS (sin emoji)
print("[DELETE] DELETING EXPIRED JOBS")
```

Busca todas las líneas con emojis y reemplázalas con texto:
- 🗑️ → [DELETE]
- ✅ → [OK]
- ❌ → [ERROR]
- ⚠️ → [WARNING]
- 📋 → [INFO]

## 🔍 CAUSA DEL PROBLEMA

Windows PowerShell usa encoding `cp1252` por defecto, que NO soporta emojis Unicode.

Cuando Python intenta imprimir `\U0001f5d1` (🗑️), PowerShell dice:
```
"No sé cómo mostrar este carácter" → UnicodeEncodeError
```

## 🎬 DESPUÉS DEL FIX

El diagnóstico debería mostrar:
```
[3/5] Ejecutando EXPIRE_LIFECYCLE --delete manualmente...

  ✅ Comando exitoso
  [DELETE] DELETING EXPIRED JOBS
  [OK] Glassdoor: 127 jobs deleted
  [OK] LinkedIn: 38 jobs deleted  
  [OK] Indeed: 4 jobs deleted
```

---

**IMPORTANTE:** Después de este fix, los 169 jobs EXPIRED se borrarán correctamente del Sheet.
