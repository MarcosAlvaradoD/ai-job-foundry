# 🚀 Guía Rápida: MCPs para IA Job Foundry

## 📋 Herramientas Instaladas y Sus Usos

### 1️⃣ **filesystem** - Gestión de Archivos Local
**Cuándo usar:**
- Leer/escribir archivos del proyecto
- Gestionar CVs y cover letters
- Guardar configuraciones

**Ejemplos:**
```
"Guarda esta descripción de empleo en /ai-job-foundry/jobs/linkedin-001.txt"
"Lee mi CV base en /ai-job-foundry/cv/cv-base.docx"
"Crea una carpeta /ai-job-foundry/applications/[empresa]"
```

---

### 2️⃣ **searxng-local** - Búsqueda Web Privada
**Cuándo usar:**
- Búsquedas rápidas de información general
- "¿Qué empresas en México buscan especialistas en Power Platform?"
- "Salario promedio BI Consultant Guadalajara"
- Investigación de empresas antes de aplicar

**Ventajas:**
- ✅ Privacidad total (sin tracking)
- ✅ Agrega resultados de 70+ motores
- ✅ Rápido para consultas simples

**Ejemplos:**
```
"Busca empresas tecnológicas en Guadalajara contratando"
"Investiga sobre la empresa X antes de mi entrevista"
"¿Cuál es el rango salarial para Power Platform Developer en México?"
```

### 3️⃣ **playwright** - Web Scraping Avanzado
**Cuándo usar:**
- Scraping de LinkedIn/Indeed/Glassdoor
- Llenar formularios de aplicación automáticamente
- Extraer ofertas de trabajo de sitios dinámicos
- Tomar screenshots de ofertas

**Ventajas:**
- ✅ Maneja JavaScript (SPAs como LinkedIn)
- ✅ Puede hacer login y navegar como humano
- ✅ Llena formularios y hace clicks

**Ejemplos para Job Foundry:**
```
"Ve a LinkedIn y scrapeame todas las ofertas de 'Power Platform' en México"
"Navega a Indeed y extrae las ofertas de BI Consultant en Guadalajara"
"Toma un screenshot de esta oferta de trabajo antes de que expire"
"Llena el formulario de aplicación en [URL] con mis datos"
```

---

### 4️⃣ **postgres-jobs** - Base de Datos de Trabajos
**Cuándo usar:**
- Guardar ofertas scraped
- Trackear aplicaciones enviadas
- Analizar match con tu perfil
- Generar reportes de búsqueda

**Schema recomendado:**
```sql
CREATE TABLE job_listings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    url TEXT UNIQUE,
    salary_min INT,
    salary_max INT,
    requirements TEXT[],
    match_score INT,  -- 0-100
    status VARCHAR(50),  -- 'scraped', 'applied', 'interview', 'rejected'
    scraped_at TIMESTAMP,
    applied_at TIMESTAMP
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    job_id INT REFERENCES job_listings(id),
    cv_version TEXT,
    cover_letter TEXT,
    applied_at TIMESTAMP,
    response_status VARCHAR(50)
);
```

**Ejemplos:**
```
"Guarda esta oferta de LinkedIn en la base de datos"
"Muéstrame todas las ofertas con match_score > 80"
"¿Cuántas aplicaciones he enviado esta semana?"
"Actualiza el status de la oferta X a 'interview'"
```

---

### 5️⃣ **fetch** - APIs y Servicios Externos
**Cuándo usar:**
- Integrar con APIs de LinkedIn/Indeed
- Enviar notificaciones (Telegram, Discord)
- Consultar APIs de empresas
- Webhooks a n8n para automation

**Ejemplos:**
```
"Haz un POST a mi webhook de n8n con esta nueva oferta"
"Envía notificación a mi Telegram cuando match_score > 90"
"Consulta la API de LinkedIn para obtener datos de la empresa"
```

---

### 6️⃣ **github** - Control de Versiones
**Cuándo usar:**
- Versionar tus CVs personalizados
- Guardar scripts de automatización
- Colaborar en el proyecto Job Foundry
- Backup de configuraciones

**Ejemplos:**
```
"Sube mi último CV a GitHub como cv-v2024-11.docx"
"Crea un commit con los cambios en los scripts de scraping"
"Muéstrame el historial de cambios en mi CV"
```

---

### 7️⃣ **memory** - Contexto Persistente
**Cuándo usar:**
- Recordar preferencias de búsqueda
- Guardar plantillas de CVs
- Tracking de empresas blacklist/wishlist
- Contexto entre conversaciones

**Ejemplos:**
```
"Recuerda que no quiero trabajar para empresas que requieran 100% presencial"
"Guarda que mi rango salarial esperado es $50k-$70k MXN mensuales"
"¿Cuáles son mis skills principales que guardaste?"
```

---

## 🎯 Workflow Completo: Job Foundry

### Paso 1: Búsqueda y Scraping
```
1. "Usa playwright para scraping de LinkedIn: ofertas 'Power Platform Developer' México"
2. "Guarda todos los resultados en PostgreSQL"
```

### Paso 2: Análisis y Filtrado
```
3. "Analiza las ofertas en la BD y calcula match_score con mi perfil"
4. "Muéstrame solo las ofertas con match > 75 y salario > $40k"
```

### Paso 3: Personalización
```
5. "Para cada oferta con match > 80, genera un CV personalizado"
6. "Guarda los CVs en /ai-job-foundry/applications/[empresa]/cv.pdf"
```

### Paso 4: Aplicación
```
7. "Usa playwright para llenar formulario de aplicación en [URL]"
8. "Actualiza status en BD a 'applied' y registra la fecha"
9. "Envía notificación a mi Telegram"
```

---

## ⚡ Comandos Rápidos

### Búsqueda Diaria
```
"Scrapea nuevas ofertas de Power Platform y BI en LinkedIn/Indeed, 
guárdalas en PostgreSQL, y envíame por Telegram las que tengan match > 85"
```

### Reporte Semanal
```
"Dame un reporte de:
- Nuevas ofertas esta semana
- Aplicaciones enviadas
- Entrevistas pendientes
- Match promedio de ofertas"
```

### Backup
```
"Sube a GitHub todos los CVs generados esta semana y 
haz commit del estado actual de la base de datos"
```

---

## 🛠️ Servicios Docker Activos

| Servicio | Puerto | Uso en Job Foundry |
|----------|--------|-------------------|
| **SearXNG** | 8888 | Búsquedas web privadas |
| **PostgreSQL** | 5432 | BD de ofertas y aplicaciones |
| **Redis** | 6379 | Cache y queues |
| **n8n** | 5678 | Workflows de automatización |
| **LiteLLM** | 4000 | Routing de modelos AI |
| **Plane** | 8080 | Project management |
| **MinIO** | 9000-9001 | Storage de CVs/attachments |

---

## 🔥 Tips Pro

1. **Combina herramientas:**
   ```
   "Usa searxng para encontrar la empresa, playwright para scraping de la oferta,
   postgres para guardarla, y fetch para notificarme"
   ```

2. **Automatiza con n8n:**
   - Crea workflow que corra cada mañana
   - Trigger: Nuevo día
   - Action: Scraping → Análisis → Notificación

3. **Usa memory para contexto:**
   ```
   "Recuerda mis últimas 5 aplicaciones para no duplicar"
   ```

4. **Playwright > SearXNG para sitios complejos:**
   - LinkedIn, Indeed, Glassdoor → Usa **playwright**
   - Google search rápida → Usa **searxng**

---

## ⚠️ Cuándo Usar Cada Uno

| Necesito... | Herramienta |
|-------------|------------|
| Buscar "empresas tech Guadalajara" | **searxng** |
| Scraping LinkedIn con login | **playwright** |
| Guardar oferta de trabajo | **postgres** |
| Leer mi CV base | **filesystem** |
| Enviar a webhook n8n | **fetch** |
| Versionar CVs | **github** |
| Recordar preferencias | **memory** |

---

## 🚀 Next Steps

1. ✅ SearXNG configurado y funcionando
2. ✅ Playwright listo para scraping
3. ⏳ Crear schema PostgreSQL para ofertas
4. ⏳ Integrar workflow n8n
5. ⏳ Configurar notificaciones Telegram
6. ⏳ Primera prueba end-to-end

---

## 📊 COMPARATIVA: Playwright vs SearXNG

| Característica | Playwright | SearXNG |
|----------------|-----------|---------|
| **Velocidad** | 🟡 Lento (2-10s) | 🟢 Rápido (<1s) |
| **JavaScript** | ✅ Sí | ❌ No |
| **Login/Forms** | ✅ Sí | ❌ No |
| **Privacidad** | 🟡 Media | 🟢 Alta |
| **Recursos** | 🔴 Alto (Docker) | 🟢 Bajo |
| **Contenido dinámico** | ✅ Sí | ❌ No |
| **Múltiples fuentes** | ❌ Una por vez | ✅ 70+ motores |

**Conclusión:** Usa **SearXNG** para búsquedas rápidas, **Playwright** para scraping profundo.

---

**Contacto:** Mark - IT Manager @ Guadalajara, México  
**Proyecto:** IA Job Foundry - Sistema automatizado de búsqueda de empleo  
**Hardware:** i9-14900K, 64GB RAM, RTX 4090 24GB
