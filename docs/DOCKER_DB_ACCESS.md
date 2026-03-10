# 🐳 ACCESO A BASES DE DATOS VIA DOCKER
**Actualizado:** 2026-03-10

Basado en los contenedores activos en Docker Desktop.

---

## 📊 CONTENEDORES DE BASE DE DATOS DISPONIBLES

### Desde Docker Desktop ves estos contenedores de bases de datos:

| Contenedor | Imagen | Puerto Externo | Puerto Interno | Stack |
|-----------|--------|---------------|----------------|-------|
| `postgres` | postgres:16 | 19432 | 5432 | Standalone |
| `theagora-postgr` | postgres:16-alpine | 15432 | 5432 | Agora |
| `plane-db` | postgres:15-alpine | 15432 | 5432 | Plane |
| `postgres-workbench` | postgres:16-alpine | 5432 | 5432 | AI Workbench |
| `redis` | redis:7-alpine | 19379 | 6379 | Standalone |
| `theagora-redis` | redis:7-alpine | 16379 | 6379 | Agora |
| `plane-redis` | redis:7-alpine | — | 6379 | Plane |
| `redis-workbench` | redis:7-alpine | 6379 | 6379 | AI Workbench |

---

## 🔌 CÓMO CONECTARTE A POSTGRESQL

### Opción 1: Desde Terminal (psql)

```bash
# PostgreSQL standalone (puerto 19432)
psql -h localhost -p 19432 -U postgres

# AI Workbench PostgreSQL (puerto 5432 directo)
psql -h localhost -p 5432 -U postgres

# Agora PostgreSQL (puerto 15432)
psql -h localhost -p 15432 -U postgres
```

> Si no tienes `psql` instalado localmente:
> ```bash
> # Conectarse entrando AL contenedor de Docker
> docker exec -it postgres psql -U postgres
> docker exec -it postgres-workbench psql -U postgres
> docker exec -it theagora-postgres psql -U postgres
> ```

### Opción 2: Desde Python (psycopg2)

```python
import psycopg2

# Conectar al PostgreSQL standalone
conn = psycopg2.connect(
    host="localhost",
    port=19432,
    user="postgres",
    password="postgres",   # o la contraseña configurada
    dbname="postgres"
)
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())
```

### Opción 3: Desde DBeaver / TablePlus / pgAdmin
- Host: `localhost`
- Puerto: `19432` (standalone) o `5432` (ai-workbench)
- Usuario: `postgres`
- Contraseña: depende de cómo se configuró el contenedor

---

## 🔴 CÓMO CONECTARTE A REDIS

```bash
# Redis standalone (puerto 19379)
redis-cli -h localhost -p 19379

# AI Workbench Redis (puerto 6379)
redis-cli -h localhost -p 6379

# Desde Docker directamente
docker exec -it redis redis-cli
docker exec -it redis-workbench redis-cli
```

---

## 🛠️ COMANDOS SQL ÚTILES (PostgreSQL)

```sql
-- Ver bases de datos disponibles
\l

-- Conectarse a una base de datos
\c nombre_db

-- Ver tablas
\dt

-- Ver estructura de una tabla
\d nombre_tabla

-- Ver todos los registros de una tabla
SELECT * FROM nombre_tabla LIMIT 10;

-- Salir
\q
```

---

## 📝 CREAR UNA NUEVA BASE DE DATOS PARA AI JOB FOUNDRY

Si quieres migrar de Google Sheets a PostgreSQL:

```sql
-- Conectarte primero: psql -h localhost -p 19432 -U postgres

-- Crear la base de datos
CREATE DATABASE ai_job_foundry;

-- Conectarse
\c ai_job_foundry

-- Crear tabla de jobs
CREATE TABLE jobs (
    id          SERIAL PRIMARY KEY,
    job_id      VARCHAR(100) UNIQUE,
    title       VARCHAR(300),
    company     VARCHAR(200),
    location    VARCHAR(200),
    url         VARCHAR(500),
    source      VARCHAR(50),    -- linkedin, glassdoor, indeed, adzuna
    salary_min  NUMERIC,
    salary_max  NUMERIC,
    currency    VARCHAR(10) DEFAULT 'MXN',
    fit_score   INTEGER,
    status      VARCHAR(50) DEFAULT 'nuevo',  -- nuevo, aplicado, rechazado, expirado
    source_type VARCHAR(50),    -- email_bulletin, manual, scraper
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    raw_data    JSONB           -- datos adicionales sin esquema fijo
);

-- Índices para búsqueda rápida
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_fit_score ON jobs(fit_score);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);

-- Ver la tabla creada
\d jobs
```

---

## 🐍 CONECTAR AI JOB FOUNDRY A POSTGRESQL (en vez de Google Sheets)

### Instalar driver:
```bash
pip install psycopg2-binary
```

### Agregar al .env:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:19432/ai_job_foundry
```

### Uso básico en Python:
```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))

def insert_job(job_data: dict):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO jobs (job_id, title, company, location, url, source, fit_score, status)
            VALUES (%(job_id)s, %(title)s, %(company)s, %(location)s, %(url)s, %(source)s, %(fit_score)s, %(status)s)
            ON CONFLICT (job_id) DO UPDATE SET
                updated_at = NOW(),
                status = EXCLUDED.status
        """, job_data)
    conn.commit()
```

---

## 🔍 VER LOGS DE UN CONTENEDOR

```bash
docker logs postgres --tail 50
docker logs postgres-workbench --tail 50
```

---

## ⚠️ NOTA SOBRE CONTRASEÑAS

Si no conoces la contraseña del contenedor de postgres, revisa cómo fue creado:
```bash
docker inspect postgres | grep -i password
docker inspect postgres | grep POSTGRES_PASSWORD
```

O reinicia el contenedor con una contraseña conocida (solo si no hay datos importantes):
```bash
docker run -e POSTGRES_PASSWORD=mipassword -p 19432:5432 postgres:16
```

---

*Documentación generada con Claude Code basada en Docker Desktop screenshots*
