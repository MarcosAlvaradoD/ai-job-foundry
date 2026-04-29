#!/usr/bin/env python3
"""
Guarda en la DB de Chalan (localhost:4001) todo el conocimiento
aprendido durante la sesión de auto-apply de 2026-03-31.

Tablas usadas:
  memories     -> hechos y flujos reutilizables
  tasks_queue  -> vacantes pendientes de aplicar
"""

import requests
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

CHALAN_API = "http://localhost:4001"

# ── PostgreSQL directo para tasks_queue (no tiene endpoint REST) ──────────────
PG = dict(host="127.0.0.1", port=15432, dbname="theagora",
          user="theagora", password=os.getenv("POSTGRES_PASSWORD", "changeme"))

def post_memory(content, category, importance, tags):
    r = requests.post(f"{CHALAN_API}/memory", json={
        "content": content,
        "category": category,
        "importance": importance,
        "tags": tags
    }, timeout=10)
    data = r.json()
    print(f"  [{category}] id={data.get('memory_id','?')} — {content[:60]}")
    return data

def insert_task(cur, task_text, priority=5):
    cur.execute("""
        INSERT INTO tasks_queue (task_text, priority, status)
        VALUES (%s, %s, 'pending')
        ON CONFLICT DO NOTHING
    """, (task_text, priority))

# ══════════════════════════════════════════════════════════════════════════════
print("=== Guardando conocimiento de auto-apply en Chalan ===\n")

# ── 1. Flujos de LinkedIn Easy Apply ─────────────────────────────────────────
print("[ LinkedIn - Flujo Easy Apply ]")

post_memory(
    "LinkedIn Easy Apply flujo estándar: "
    "1) Click botón 'Easy Apply' → 2) Contact info pre-llenado (markalvati@gmail.com, Mexico +52, 3323320358) → "
    "3) Click Next → 4) Resume step: seleccionar 'CV_Marcos_Alvarado_.pdf' (147KB, última versión 3/27/2026) → "
    "5) Click Review → 6) Revisar resumen → 7) Click 'Submit application'. "
    "Progreso: 0% → 50% → 100%. Tab se cierra automáticamente al enviar.",
    "auto_apply", 9,
    ["linkedin", "easy_apply", "flujo", "aplicacion"]
)

post_memory(
    "LinkedIn Easy Apply - overlay 'Save this application?': "
    "Cuando existe un borrador guardado de una aplicación previa, LinkedIn muestra un overlay "
    "'Save this application?' SOBRE el formulario. "
    "SOLUCIÓN: Hacer click en la X (cerrar) del overlay para descartarlo SIN afectar el formulario. "
    "NO hacer click en 'Discard' (descarta la aplicación completa). "
    "Coordenadas aproximadas del X: 881, 189 según screenshots previos.",
    "auto_apply", 8,
    ["linkedin", "easy_apply", "overlay", "bug", "workaround"]
)

post_memory(
    "LinkedIn Easy Apply - React modal requiere clicks reales del mouse. "
    "JS .click() no dispara los event handlers de React correctamente. "
    "Usar mcp__Claude_in_Chrome__computer con action=left_click y coordenadas reales "
    "o ref del elemento para garantizar que los eventos React se activen.",
    "auto_apply", 8,
    ["linkedin", "easy_apply", "react", "click", "mcp"]
)

post_memory(
    "LinkedIn Easy Apply - Extracción de Job IDs: "
    "Para encontrar el job ID directamente, la URL del job es "
    "https://www.linkedin.com/jobs/view/{JOB_ID}/. "
    "Al buscar con filtros, el currentJobId aparece en la URL de búsqueda como "
    "?currentJobId=XXXXXXXXXX. "
    "HCLTech BA: 4390404145 (APPLIED 2026-03-31). "
    "Stand8 Technology: 4392502231. Capgemini Cloud: 4388412062.",
    "auto_apply", 7,
    ["linkedin", "job_id", "url", "scraping"]
)

# ── 2. Sitios externos / portales de empleo ───────────────────────────────────
print("\n[ Perfiles de sitios de empleo ]")

post_memory(
    "BairesDev - Portal de aplicación: https://applicants.bairesdev.com/. "
    "Requiere cuenta propia en su portal O autenticación LinkedIn OAuth (requiere re-ingresar password de LinkedIn). "
    "No se puede auto-aplicar sin credenciales previas guardadas. "
    "SOLUCIÓN: El usuario debe crear cuenta en applicants.bairesdev.com con Google/LinkedIn una vez, "
    "luego las aplicaciones futuras sí pueden automatizarse con sesión activa.",
    "site_profile", 8,
    ["bairesdev", "portal", "auth_required", "linkedin_oauth", "bloqueado"]
)

post_memory(
    "Indeed Mexico - URLs de vacantes: "
    "URL directa de vacante: https://mx.indeed.com/viewjob?jk={JOB_ID}. "
    "El JOB_ID (data-jk) se extrae del DOM con: "
    "document.querySelectorAll('[data-jk]').forEach(el => console.log(el.getAttribute('data-jk'))). "
    "Indeed bloquea scraping directo con Python (403 + Cloudflare). "
    "Siempre extraer desde la sesión autenticada del navegador.",
    "site_profile", 8,
    ["indeed", "mexico", "url_pattern", "job_id", "data-jk", "scraping"]
)

post_memory(
    "Google Sheets - AI Job Foundry: "
    "Spreadsheet con tabs: 'LinkedIn' (vacantes LI, filas 351-375 insertadas 2026-03-31) y "
    "'Indeed' (14 vacantes, filas 6-19). "
    "Color azul #ADD8E6 = RGB(0.678, 0.847, 0.902) identifica vacantes capturadas por Claude. "
    "Scripts: insert_jobs_today.py (insertar), fix_indeed_urls.py (arreglar URLs Indeed). "
    "Ruta: C:/Users/MSI/Desktop/ai-job-foundry/scripts/",
    "job_search", 7,
    ["google_sheets", "ai_job_foundry", "linkedin", "indeed", "scripts"]
)

# ── 3. CV y documentos ────────────────────────────────────────────────────────
print("\n[ CV y documentos ]")

post_memory(
    "CV de Marcos - versión Indeed 2026: "
    "DOCX: C:/Users/MSI/Documents/Resume/Marcos_Alvarado_Indeed_2026.docx (48KB). "
    "PDF: C:/Users/MSI/Documents/Resume/Marcos_Alvarado_Indeed_2026.pdf (310KB). "
    "Generado con Node.js (docx-js) en C:/Users/MSI/Documents/Resume/gen_cv.js. "
    "En LinkedIn el PDF 'CV_Marcos_Alvarado_.pdf' (147KB) es el que usa Easy Apply "
    "(versión anterior, subida 3/27/2026).",
    "auto_apply", 8,
    ["cv", "pdf", "docx", "resume", "linkedin", "indeed"]
)

# ── 4. Vacantes aplicadas / status ────────────────────────────────────────────
print("\n[ Registro de aplicaciones ]")

post_memory(
    "HCLTech - 'Business Analysis & Application Support' (LinkedIn Job ID: 4390404145): "
    "APLICADA via Easy Apply el 2026-03-31. "
    "Remote, Full-time, Mexico. Hiring: Daniel Morales (Sr IT Recruiter). "
    "Perfil compartido + CV_Marcos_Alvarado_.pdf enviado.",
    "job_applications", 7,
    ["hcltech", "aplicada", "linkedin", "easy_apply", "business_analysis", "2026-03-31"]
)

post_memory(
    "BairesDev - 'Analista de Negocios - Trabajo Remoto' (LinkedIn Job 4391894958): "
    "NO aplicada 2026-03-31 - requiere login a portal externo applicants.bairesdev.com. "
    "35 personas hicieron click. Latin America (Remote). "
    "Pendiente: crear cuenta en portal BairesDev para auto-apply futuro.",
    "job_applications", 6,
    ["bairesdev", "pendiente", "linkedin", "analista_negocios", "bloqueado"]
)

# ── 5. Vacantes pendientes → tasks_queue ─────────────────────────────────────
print("\n[ Insertando vacantes pendientes en tasks_queue ]")

pending_vacantes = [
    ("APPLY LinkedIn: Crossing Hurdles - Business Analyst (Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Excelia - Business Analyst (TCS alum) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: DaCodes - Business Process Analyst 35-40K (Easy Apply, Early) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Commerce Social - Project Manager TikTok Shop — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: GK Software SE - Project Manager (TCS alum) — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Stand8 Technology - Technical Project Manager (ID: 4392502231) Easy Apply GDL", 7),
    ("APPLY LinkedIn: LTIMindtree - Project Manager Cloud (Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Somewhere - Project Manager Remote (TCS alum, Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Apply Digital - Engagement Manager Technical (TCS alum) — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Sutherland - Manager Product Delivery (UdG alum) — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Littelfuse - Sr Project Manager Solutions (Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Visit.org - Events Project Manager (Easy Apply, 3 días) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Getmore - Project Manager — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Comptech - Senior IT Payments PM (Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Comptech - Global Transaction PM — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Avahi - Technical Project Manager (TCS alum) — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Capgemini - FBS Associate Cloud Business Manager (ID: 4388412062, Easy Apply)", 8),
    ("APPLY LinkedIn: Instructure - GTM Systems Manager (UdG alum) — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Capgemini - FBS IT Change Management Specialist (Easy Apply, TCS alum) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: HCLTech - SAP Release Manager (Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Motivus - Service Manager AMS — buscar en LinkedIn", 6),
    ("APPLY LinkedIn: Sezzle - IT Vendor Management Program Manager (Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY LinkedIn: Huzzle - Senior IT Infrastructure PM (TCS alum, Easy Apply) — buscar en LinkedIn", 7),
    ("APPLY Indeed: 14 vacantes en Sheet 'Indeed' filas 6-19 — usar fix_indeed_urls.py para URLs", 6),
    ("APPLY BairesDev: Crear cuenta en applicants.bairesdev.com para habilitar auto-apply", 5),
]

try:
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    for task_text, priority in pending_vacantes:
        insert_task(cur, task_text, priority)
        print(f"  [tasks_queue] {task_text[:70]}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n  -> {len(pending_vacantes)} tareas insertadas en tasks_queue")
except Exception as e:
    print(f"  ERROR tasks_queue: {e}")

print("\n=== Listo. Todo guardado en Chalan DB ===")
