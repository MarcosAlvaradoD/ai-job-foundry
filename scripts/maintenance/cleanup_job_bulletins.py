# -*- coding: utf-8 -*-
"""
cleanup_job_bulletins.py — Limpieza de boletines de empleo viejos en Gmail
===========================================================================
Busca emails de plataformas de empleo (LinkedIn, Indeed, Glassdoor, etc.)
con mas de 30 dias de antiguedad y los mueve a la papelera (TRASH).

IMPORTANTE:
  - Mueve a papelera, NO borra permanentemente (puedes recuperarlos desde Gmail)
  - Usa --dry-run primero para ver que se va a mover antes de ejecutar
  - Solo toca emails de plataformas de empleo conocidas, nunca emails personales

Uso:
  py scripts/maintenance/cleanup_job_bulletins.py --dry-run
  py scripts/maintenance/cleanup_job_bulletins.py --execute

Opciones:
  --dry-run     Solo lista los emails que se moveran (DEFAULT - mas seguro)
  --execute     Mueve a papelera los emails listados
  --days N      Dias de antiguedad minimo (default: 30)
  --tab YYYY-MM-DD  Fecha corte en lugar de dias (ej: 2026-02-25)
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ── Remitentes de boletines de empleo conocidos ────────────────────────────────
JOB_BULLETIN_SENDERS = [
    # LinkedIn
    "jobs-noreply@linkedin.com",
    "jobalerts-noreply@linkedin.com",
    "inmail-hit-reply@linkedin.com",
    "messages-noreply@linkedin.com",
    "notifications-noreply@linkedin.com",
    # Indeed
    "alert@indeed.com",
    "jobalert@indeed.com",
    "noreply@indeed.com",
    "jobs@indeed.com",
    # Glassdoor
    "noreply@glassdoor.com",
    "alerts@glassdoor.com",
    "jobs@glassdoor.com",
    # Adzuna
    "noreply@adzuna.com",
    "alerts@adzuna.com",
    "jobs@adzuna.com",
    # Computrabajo
    "noreply@computrabajo.com",
    "alertas@computrabajo.com",
    "avisos@computrabajo.com.mx",
    # JobLeads / otros
    "noreply@jobleads.com",
    "hello@jobleads.com",
    # ZipRecruiter
    "info@ziprecruiter.com",
    "noreply@ziprecruiter.com",
    # Otros job boards comunes
    "noreply@hired.com",
    "alerts@simplyhired.com",
    "noreply@monster.com",
    "noreply@careerbuilder.com",
    "noreply@wellfound.com",
    "hello@remoteok.com",
    "noreply@weworkremotely.com",
]

# Palabras clave en el asunto que indican boletin de empleo (si remitente no esta en la lista)
JOB_SUBJECT_KEYWORDS = [
    "job alert",
    "alerta de empleo",
    "new jobs for you",
    "job recommendation",
    "jobs matching",
    "nuevas ofertas",
    "empleos para ti",
    "job opportunities",
    "hiring",
]

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
]


def get_gmail_service():
    """Obtiene el servicio de Gmail con OAuth."""
    base_path = ROOT
    token_path = base_path / "data" / "credentials" / "token.json"

    if not token_path.exists():
        raise FileNotFoundError(f"Token no encontrado: {token_path}")

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("[AUTH] Renovando token...")
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
            print("[AUTH] Token renovado OK")
        else:
            raise Exception(
                "Token invalido y no se puede renovar automaticamente.\n"
                "Ejecuta: py scripts/oauth/reauthenticate_gmail_v2.py"
            )

    return build('gmail', 'v1', credentials=creds)


def build_gmail_query(cutoff_date: datetime) -> str:
    """Construye la query de Gmail para buscar boletines viejos."""
    # Fecha en formato Gmail: before:YYYY/MM/DD
    date_str = cutoff_date.strftime("%Y/%m/%d")

    # FROM: con todos los remitentes conocidos
    from_parts = " OR ".join(f"from:{s}" for s in JOB_BULLETIN_SENDERS)

    query = f"({from_parts}) before:{date_str} -in:trash -in:sent"
    return query


def fetch_old_bulletins(service, cutoff_date: datetime) -> list:
    """
    Busca todos los emails de boletines anteriores a cutoff_date.
    Retorna lista de dicts con id, subject, from, date.
    """
    query = build_gmail_query(cutoff_date)
    print(f"\n[QUERY] {query[:120]}...")
    print()

    messages = []
    page_token = None

    while True:
        params = {
            "userId": "me",
            "q": query,
            "maxResults": 500,
        }
        if page_token:
            params["pageToken"] = page_token

        result = service.users().messages().list(**params).execute()
        batch = result.get("messages", [])
        messages.extend(batch)

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    print(f"[FOUND] {len(messages)} emails encontrados")
    return messages


def get_message_details(service, msg_id: str) -> dict:
    """Obtiene detalles de un mensaje (subject, from, date)."""
    try:
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        return {
            "id":      msg_id,
            "subject": headers.get("Subject", "(sin asunto)")[:80],
            "from":    headers.get("From", "?")[:60],
            "date":    headers.get("Date", "?"),
            "labels":  msg.get("labelIds", []),
        }
    except Exception:
        return {"id": msg_id, "subject": "?", "from": "?", "date": "?", "labels": []}


def trash_message(service, msg_id: str) -> bool:
    """Mueve un email a la papelera (no es borrado permanente)."""
    try:
        service.users().messages().trash(userId="me", id=msg_id).execute()
        return True
    except Exception as e:
        print(f"  [ERR] No se pudo mover {msg_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Limpieza de boletines de empleo viejos")
    parser.add_argument("--dry-run",  action="store_true", default=True,
                        help="Solo lista sin mover (DEFAULT)")
    parser.add_argument("--execute",  action="store_true",
                        help="Ejecutar: mover a papelera")
    parser.add_argument("--days",     type=int, default=30,
                        help="Dias de antiguedad minimo (default: 30)")
    parser.add_argument("--date",     type=str,
                        help="Fecha de corte YYYY-MM-DD (override --days)")
    parser.add_argument("--limit",    type=int, default=0,
                        help="Maximo de emails a procesar (0=todos)")
    args = parser.parse_args()

    # Si --execute, desactivar dry-run
    dry_run = not args.execute

    # Calcular fecha de corte
    if args.date:
        cutoff = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    mode_str = "DRY-RUN (solo listado)" if dry_run else "EJECUTAR (mover a papelera)"

    print()
    print("=" * 65)
    print("  LIMPIEZA DE BOLETINES DE EMPLEO")
    print("=" * 65)
    print(f"  Modo:         {mode_str}")
    print(f"  Fecha corte:  {cutoff.strftime('%Y-%m-%d')} (emails anteriores a esta fecha)")
    print(f"  Hoy:          {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 65)
    print()

    # Conectar a Gmail
    try:
        service = get_gmail_service()
        print("[AUTH] Gmail conectado OK")
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a Gmail: {e}")
        sys.exit(1)

    # Buscar emails
    messages = fetch_old_bulletins(service, cutoff)
    if not messages:
        print("[OK] No se encontraron boletines viejos. Nada que hacer.")
        return

    # Limitar si se pidio
    if args.limit > 0:
        messages = messages[:args.limit]
        print(f"[LIMIT] Procesando solo los primeros {args.limit}")

    # Obtener detalles y mostrar lista
    print(f"\n{'#':<5} {'REMITENTE':<45} {'ASUNTO'}")
    print("-" * 90)

    details_list = []
    for i, msg in enumerate(messages, 1):
        details = get_message_details(service, msg["id"])
        details_list.append(details)
        sender_short = details["from"][:43]
        print(f"{i:<5} {sender_short:<45} {details['subject'][:40]}")

        if i % 50 == 0:
            print(f"  ... ({i}/{len(messages)} listados)")

    print("-" * 90)
    print(f"\nTotal a procesar: {len(details_list)} emails")

    if dry_run:
        print()
        print("[DRY-RUN] No se movio ningun email.")
        print("Para ejecutar: py scripts/maintenance/cleanup_job_bulletins.py --execute")
        return

    # ── EJECUTAR: mover a papelera ─────────────────────────────────────────────
    print()
    print(f"[EXECUTE] Moviendo {len(details_list)} emails a papelera...")
    print("  (Recuperables desde Gmail > Papelera por 30 dias)")
    print()

    success = 0
    errors  = 0

    for i, details in enumerate(details_list, 1):
        ok = trash_message(service, details["id"])
        if ok:
            success += 1
        else:
            errors += 1

        if i % 25 == 0:
            print(f"  Progreso: {i}/{len(details_list)} ({success} OK, {errors} errores)")

    print()
    print("=" * 65)
    print(f"  RESULTADO: {success} movidos a papelera | {errors} errores")
    print("  Los emails son recuperables desde Gmail > Papelera (30 dias)")
    print("=" * 65)


if __name__ == "__main__":
    main()
