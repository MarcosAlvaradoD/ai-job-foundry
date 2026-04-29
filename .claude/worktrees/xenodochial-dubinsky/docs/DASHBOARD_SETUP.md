# Dashboard - Configuración de API Key

## 📌 Cómo obtener tu Google Sheets API Key

El dashboard necesita una API Key de Google para leer los datos de Google Sheets.

### Pasos:

1. **Ve a Google Cloud Console:**
   https://console.cloud.google.com/

2. **Crea un proyecto nuevo** (o usa uno existente)

3. **Habilita la API de Google Sheets:**
   - Ve a "APIs & Services" > "Library"
   - Busca "Google Sheets API"
   - Click "Enable"

4. **Crea una API Key:**
   - Ve a "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copia la API Key generada

5. **Edita dashboard.html:**
   - Línea 242: Reemplaza `AIzaSyDG8mhYE7RYJ4wZx3eJ7Qz_0xK9LZ8x1Yk` con tu API Key real

6. **Abre dashboard.html en tu navegador**

## 📊 Características del Dashboard

✅ Conectado en tiempo real con Google Sheets  
✅ Estadísticas: Total jobs, High matches, Avg score  
✅ Gráficas: Distribución de scores y fuentes  
✅ Tabla de top matches (FIT 7+)  
✅ Tabla completa con filtros por fuente  
✅ Auto-refresh cada 60 segundos  

## ⚠️ Nota

Si no configuras la API Key, el dashboard mostrará datos de ejemplo automáticamente.
