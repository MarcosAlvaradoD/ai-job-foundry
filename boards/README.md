# 📁 BOARDS - Job Boards Analyzers

Scripts para analizar boards de empleo externos (RH-IT Home, OCC Mundial, etc)

## 📂 ARCHIVOS

### 1. analyze_board.py
Analiza TODO un board de empleos con IA

**Uso:**
```powershell
py boards\analyze_board.py --url "https://vacantes.rh-itchome.com/" --output results.txt
```

**Qué hace:**
- Encuentra TODOS los enlaces a vacantes
- Analiza cada uno con IA (FIT score)
- Genera TXT ordenado por FIT

### 2. auto_fill_application.py
Llena formularios de aplicación automáticamente

**Uso:**
```powershell
# DRY RUN (solo muestra)
py boards\auto_fill_application.py --url "https://vacantes.rh-itchome.com/aplicar/262" --dry-run

# LIVE (llena formulario)
py boards\auto_fill_application.py --url "https://vacantes.rh-itchome.com/aplicar/262"
```

**Qué hace:**
- Detecta campos del formulario
- Llena con datos de CV
- Usa IA para preguntas abiertas

## 🎯 FLUJO COMPLETO

```powershell
# 1. Analizar board
py boards\analyze_board.py --url "https://vacantes.rh-itchome.com/" --output rh_it.txt

# 2. Leer rh_it.txt → encontrar vacantes FIT 7+

# 3. Aplicar
py boards\auto_fill_application.py --url "https://vacantes.rh-itchome.com/aplicar/262"
```

## ⚠️ REQUISITOS

- LM Studio corriendo (para FIT scores)
- Playwright instalado: `pip install playwright`
- Variables .env: USER_EMAIL, USER_PHONE
