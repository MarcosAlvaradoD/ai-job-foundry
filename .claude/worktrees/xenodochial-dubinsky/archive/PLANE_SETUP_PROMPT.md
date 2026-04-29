# 🚀 PROMPT PARA CONFIGURAR PLANE

**Copia este prompt completo a otra IA (Claude, ChatGPT, etc.)**

---

## CONTEXTO

Tengo Plane (https://plane.so) corriendo en Docker Desktop con los siguientes contenedores:

- `plane-workbench` (no arranca completamente)
- `plane-web` (puerto 8080:3000)
- `plane-worker`
- `plane-beat-worker`
- `plane-api`
- `plane-db` (PostgreSQL)
- `plane-redis`
- `plane-minio` (puerto 9000:9000)

## PROBLEMA ACTUAL

Cuando accedo a `http://localhost:8080/sign-up`, ingreso mi email `markalvati@gmail.com`, hago click en "Continue" pero no recibo el correo de verificación y no pasa nada.

## ARQUITECTURA ACTUAL

```
C:\Users\MSI\Desktop\dev\plane-workbench\
├── docker-compose.yml (probablemente)
└── (configuraciones de Plane)
```

**Contenedores activos:**
```
plane-web: 8080:3000
plane-api: (backend)
plane-db: PostgreSQL
plane-redis: Redis
plane-minio: 9000:9000 (object storage)
```

## OBJETIVO

1. **Hacer que Plane funcione localmente** para poder crear cuenta y usarlo
2. **Configurar email** (usar Gmail SMTP o modo consola)
3. **Acceder al panel de administración**
4. **Crear mi primer proyecto**

## OPCIONES DE CONFIGURACIÓN

### Opción A: Email en consola (más fácil)
Ver emails en logs de Docker en lugar de recibirlos realmente.

### Opción B: Gmail SMTP (producción)
Configurar con mi cuenta Gmail usando App Password.

### Opción C: Crear usuario directamente en base de datos
Bypass del email y crear usuario manualmente.

## LO QUE NECESITO

1. **Instrucciones paso a paso** para configurar Plane
2. **Comandos exactos** para ejecutar en PowerShell en Windows
3. **Variables de entorno** necesarias en `docker-compose.yml`
4. **Cómo acceder** después de configurado
5. **Troubleshooting** de problemas comunes

## RESTRICCIONES

- **Sistema operativo:** Windows 11
- **Docker Desktop** ya instalado y corriendo
- **Ruta del proyecto:** `C:\Users\MSI\Desktop\dev\plane-workbench\`
- **Email preferido:** markalvati@gmail.com
- **Uso:** Aprendizaje y gestión de proyectos personales

## INFORMACIÓN ADICIONAL

- Soy PM con experiencia en ERP y Data Infrastructure
- Quiero usar Plane para gestionar mi proyecto "AI Job Foundry"
- Necesito entender bien la herramienta para aplicarla en mi trabajo

## ENTREGABLES ESPERADOS

1. ✅ Archivo `docker-compose.yml` configurado
2. ✅ Archivo `.env` con variables necesarias
3. ✅ Comandos para ejecutar (PowerShell)
4. ✅ Cómo verificar que funciona
5. ✅ Guía rápida de uso inicial

---

## FORMATO DE RESPUESTA ESPERADO

Por favor estructura tu respuesta así:

### 1. Diagnóstico
(Explica qué está mal actualmente)

### 2. Solución Recomendada
(Cuál opción recomiendas: A, B o C)

### 3. Pasos de Implementación
(Comandos numerados)

### 4. Verificación
(Cómo saber que funcionó)

### 5. Uso Básico
(Primeros pasos en Plane)

---

**Nota:** Si necesitas más información, pregúntame. Puedo proporcionarte logs de Docker, contenido de archivos, capturas de pantalla, etc.