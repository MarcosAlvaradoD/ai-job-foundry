#!/usr/bin/env python3
"""
flag_us_only_jobs.py
====================
Revisa TODAS las filas de la tab LinkedIn del Sheet y marca con
  - Columna Notes: agrega "[!] US_WORK_AUTH_REQUIRED"
  - Columna Status: cambia a "Skip - US Only"
  - Fondo rojo (#FFCCCC) para visibilidad

Criterios para marcar como US-Only:
  1. Location contiene "United States" o ", US" o " US," o "New York" o
     cualquier ciudad/estado de EE.UU. sin México/LATAM en el campo
  2. Location NO contiene: Mexico, México, LATAM, Latinoam, Remote (sin país)
     cuando la empresa claramente es US-only

Además imprime un reporte de vacantes sospechosas para revisión manual.
"""

import sys, os, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SHEET_ID   = os.getenv("GOOGLE_SHEETS_ID")
TOKEN_PATH = str(Path(__file__).parent.parent / "data" / "credentials" / "token.json")
SCOPES     = ["https://www.googleapis.com/auth/spreadsheets"]

# Patrones que indican US-Only (trabajo desde EE.UU.)
US_PATTERNS = [
    r'\bUnited States\b', r'\bUSA\b', r'\bU\.S\.A\b',
    r'\bNew York\b', r'\bSan Francisco\b', r'\bLos Angeles\b',
    r'\bChicago\b', r'\bAustin\b', r'\bSeattle\b', r'\bBoston\b',
    r'\bAtlanta\b', r'\bDenver\b', r'\bDallas\b', r'\bMiami\b',
    r',\s*[A-Z]{2}\s*$',   # termina en ", NY" / ", CA" etc.
]

# Si contiene alguno de estos, está bien (México/LATAM)
SAFE_PATTERNS = [
    r'[Mm][eé]xico', r'M[eé]xico City', r'LATAM', r'Latinoam',
    r'Guadalajara', r'Monterrey', r'Ciudad de M', r'CDMX',
    r'M[eé]xico Metropolitan', r'Mexico Metropolitan',
    r'Latin America', r'Remote$',  # solo "Remote" sin país = ambiguo pero ok
]

def is_us_only(location: str) -> bool:
    loc = location.strip()
    if not loc:
        return False
    # Si tiene patrón seguro, no es US-only
    for pat in SAFE_PATTERNS:
        if re.search(pat, loc, re.IGNORECASE):
            return False
    # Si tiene patrón US, sí es US-only
    for pat in US_PATTERNS:
        if re.search(pat, loc, re.IGNORECASE):
            return True
    return False

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)

svc    = get_service()
sheets = svc.spreadsheets()

print("Leyendo tab LinkedIn...")
result = sheets.values().get(
    spreadsheetId=SHEET_ID,
    range="LinkedIn!A2:T500"
).execute()
rows = result.get("values", [])
print(f"  {len(rows)} filas encontradas\n")

# Columnas (0-index): A=0 Fecha, B=1 Empresa, C=2 Puesto, D=3 Location,
# E=4 Remoto, F=5 URL, G=6 Fuente ... K=10 Status, L=11 FechaAplicacion,
# M=12 ?, N=13 Notes ... (varía por sheet, ajustamos dinámico)
# Detectamos por header qué columna es cada cosa

header_range = sheets.values().get(
    spreadsheetId=SHEET_ID,
    range="LinkedIn!A1:T1"
).execute().get("values", [[]])[0]

print("Header:", header_range)

# Mapeo flexible: busca columnas por nombre
def col_idx(headers, *names):
    for name in names:
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
    return None

loc_col    = col_idx(header_range, "ubicacion", "location", "ciudad") or 3
status_col = col_idx(header_range, "status", "estado")               or 10
notes_col  = col_idx(header_range, "notes", "notas", "comentarios")  or 17
empresa_col = 1
puesto_col  = 2

print(f"  location col={loc_col}, status col={status_col}, notes col={notes_col}\n")

flagged = []
for i, row in enumerate(rows, start=2):  # fila real en sheet = i+1
    location = row[loc_col] if len(row) > loc_col else ""
    status   = row[status_col] if len(row) > status_col else ""
    empresa  = row[empresa_col] if len(row) > empresa_col else ""
    puesto   = row[puesto_col]  if len(row) > puesto_col  else ""

    # Skip si ya marcado
    if "US Only" in status or "Skip" in status:
        continue

    if is_us_only(location):
        flagged.append({
            "row": i,
            "empresa": empresa,
            "puesto": puesto,
            "location": location,
            "status": status,
        })

print(f"Vacantes US-Only detectadas: {len(flagged)}\n")
for f in flagged:
    print(f"  Fila {f['row']:3d} | {f['empresa']:25s} | {f['puesto']:40s} | {f['location']}")

if flagged:
    print("\nActualizando Sheet...")

    # Batch update status + notes para cada fila encontrada
    data_updates = []
    for f in flagged:
        row_num = f["row"]
        # Status col (letter)
        status_letter = chr(ord('A') + status_col)
        notes_letter  = chr(ord('A') + notes_col)

        data_updates.append({
            "range": f"LinkedIn!{status_letter}{row_num}",
            "values": [["Skip - US Only"]]
        })
        data_updates.append({
            "range": f"LinkedIn!{notes_letter}{row_num}",
            "values": [[f"[!] US_WORK_AUTH_REQUIRED - {f['location']}"]]
        })

    sheets.values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": data_updates}
    ).execute()

    # Color rojo fondo
    color_requests = []
    for f in flagged:
        color_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": f["row"] - 1,
                    "endRowIndex": f["row"],
                    "startColumnIndex": 0,
                    "endColumnIndex": 20
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 1.0, "green": 0.8, "blue": 0.8
                        }
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })

    sheets.batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": color_requests}
    ).execute()

    print(f"\n[OK] {len(flagged)} vacantes marcadas como 'Skip - US Only' con fondo rojo.")
else:
    print("[OK] No se encontraron vacantes US-Only sin marcar.")

print("\nDone.")
