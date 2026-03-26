# 🚀 LinkedIn Auto-Apply V3 - AUTO-LOGIN FEATURE

## ✨ QUÉ CAMBIÓ

**ANTES (V2):**
```
❌ ERROR: Not logged into LinkedIn!
❌ Dependía de sesión manual previa
❌ No usaba credenciales del .env
```

**AHORA (V3):**
```
✅ Lee credenciales del .env automáticamente
✅ Hace login automático si es necesario
✅ Guarda cookies para reutilizar sesión
✅ Aplica a jobs con Easy Apply sin intervención
```

---

## 🔧 CONFIGURACIÓN

### 1️⃣ Verifica tus credenciales en `.env`

```env
# LinkedIn (requerido para auto-login)
LINKEDIN_EMAIL=markalvati@gmail.com
LINKEDIN_PASSWORD=tu_contraseña_aquí
```

**✅ YA ESTÁN CONFIGURADAS** en tu `.env` actual.

---

## 🧪 PRUEBA RÁPIDA

### Ejecutar test (modo seguro - dry-run):

```powershell
# Desde la raíz del proyecto
py scripts\test_linkedin_autoapply_v3.py
```

**Qué va a pasar:**
1. ✅ Busca jobs con FIT >= 7
2. ✅ Inicia navegador Chrome (visible)
3. ✅ Intenta cargar cookies guardadas
4. ✅ Si no hay sesión válida, hace login automático
5. ✅ Navega a los primeros 2 jobs
6. ✅ Detecta si tienen "Easy Apply"
7. ✅ Analiza formularios (pero NO envía - modo dry-run)

---

## 🎯 USO REAL (LIVE MODE)

### Para aplicar de verdad (con revisión manual antes de submit):

```python
# Edita: scripts\test_linkedin_autoapply_v3.py
auto_apply.run(
    dry_run=False,     # ⚠️ MODO REAL
    max_applies=5,     # Máximo 5 aplicaciones
    min_score=7        # Solo FIT >= 7
)
```

**IMPORTANTE:** El script llenará formularios pero **NO enviará automáticamente**. Dejará una pausa para que revises antes del submit final.

---

## 📁 ARCHIVOS MODIFICADOS

```
core/automation/
├── linkedin_auto_apply.py         ✅ ACTUALIZADO (V3 con auto-login)

scripts/
├── test_linkedin_autoapply_v3.py  ✨ NUEVO (test rápido)

data/
├── linkedin_cookies.json          ✨ SE CREARÁ (cookies guardadas)
└── browser_data/                  ⚠️ Opcional (ya no requerido)
```

---

## 🔐 SEGURIDAD

### Cookies guardadas en: `data/linkedin_cookies.json`

**Beneficios:**
- ✅ No tienes que loguearte cada vez
- ✅ Sesión reutilizable entre ejecuciones
- ✅ Evita límites de login de LinkedIn

**IMPORTANTE:**
- 🔒 El archivo `data/linkedin_cookies.json` contiene tu sesión activa
- 🔒 NO lo compartas ni lo subas a GitHub
- 🔒 Está incluido en `.gitignore`

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "LinkedIn credentials not found in .env"

**Solución:**
```powershell
# Verifica que existan en .env
py -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('LINKEDIN_EMAIL'))"
```

### ❌ Error: "Not logged in - will attempt auto-login"

**Esto es NORMAL.** El script detectó que no hay sesión y va a hacer login automático.

### 🔐 LinkedIn pide verificación (captcha/SMS)

**Solución:**
1. El script pausará 60 segundos
2. Completa la verificación manualmente en el navegador
3. El script continuará automáticamente

### ❌ "Login failed - unexpected URL"

**Causas posibles:**
- Contraseña incorrecta en `.env`
- LinkedIn bloqueó el login (demasiados intentos)
- Verificación de seguridad requerida

**Solución:**
1. Verifica credenciales en `.env`
2. Intenta login manual en navegador normal
3. Espera 30 minutos y reintenta

---

## 📊 FLUJO COMPLETO

```
1. INICIO
   └─> Carga credenciales del .env
   └─> Busca jobs con FIT >= 7

2. SESIÓN LINKEDIN
   └─> Intenta cargar cookies guardadas
   └─> Si no hay sesión válida:
       └─> Login automático
       └─> Guarda cookies para próxima vez

3. APLICACIONES
   └─> Por cada job elegible:
       ├─> Navega a URL del job
       ├─> Verifica "Easy Apply"
       ├─> Click en "Easy Apply"
       ├─> Analiza formulario
       ├─> Llena campos automáticamente
       ├─> Detecta pasos múltiples
       └─> Pausa antes de submit (revisión manual)

4. ACTUALIZACIÓN SHEETS
   └─> Marca jobs como "Applied"
   └─> Guarda timestamp
```

---

## 🎯 PRÓXIMOS PASOS

1. **Ejecutar test:**
   ```powershell
   py scripts\test_linkedin_autoapply_v3.py
   ```

2. **Verificar que funcione el login automático**

3. **Si funciona, activar modo LIVE:**
   - Cambiar `dry_run=False` en el script
   - Ejecutar con max_applies=5

4. **Integrar al control_center.py:**
   - Agregar auto-apply al pipeline diario
   - Ejecutar después de AI analysis

---

## 📝 NOTAS

- ✅ Compatible con el sistema actual (no rompe nada)
- ✅ Backward compatible (sigue funcionando con sesiones manuales)
- ✅ Las credenciales ya están en tu `.env`
- ✅ Solo requiere ejecutar el test para activar

**Estado actual:**
- linkedin_auto_apply.py ✅ ACTUALIZADO
- .env ✅ YA CONFIGURADO
- test script ✅ LISTO PARA EJECUTAR

---

**Última actualización:** 2025-12-24
**Versión:** V3 (Auto-Login)
**Autor:** Marcos A. Alvarado + Claude
