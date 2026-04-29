#!/usr/bin/env python3
"""
cleanup_sheet.py
Elimina filas del tab LinkedIn que ya no sirven:
  - Status = "Skip - US Only"
  - Status = "No longer accepting applications"
  - Status = "No application allowed" (variantes)
Borra de abajo hacia arriba para no desplazar índices.
"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SHEET_ID    = os.getenv('GOOGLE_SHEETS_ID')
TOKEN_PATH  = str(Path(__file__).parent.parent / 'data' / 'credentials' / 'token.json')
LINKEDIN_ID = 186301015   # sheetId numérico del tab LinkedIn
SCOPES      = ['https://www.googleapis.com/auth/spreadsheets']
STATUS_COL  = 12          # columna M (0-index)

DELETE_STATUSES = {
    'skip - us only',
    'no longer accepting applications',
    'no application allowed',
    'no application allowed anymore',
    'closed',
    'expired',
}

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('sheets', 'v4', credentials=creds)

svc    = get_service()
sheets = svc.spreadsheets()

print("Leyendo LinkedIn tab...")
result = sheets.values().get(
    spreadsheetId=SHEET_ID, range='LinkedIn!A2:M500'
).execute()
rows = result.get('values', [])
print(f"  {len(rows)} filas leidas (fila real: 2 a {len(rows)+1})\n")

# Identificar filas a eliminar (índice real en sheet = i + 2)
to_delete = []
for i, row in enumerate(rows):
    status = (row[STATUS_COL] if len(row) > STATUS_COL else '').strip().lower()
    if status in DELETE_STATUSES:
        real_row = i + 2   # +1 header, +1 porque enumerate es 0-based
        company  = row[1] if len(row) > 1 else '?'
        role     = row[2] if len(row) > 2 else '?'
        to_delete.append((real_row, company, role, status))

print(f"Filas a eliminar: {len(to_delete)}")
for r, co, ro, st in to_delete[:10]:
    print(f"  Fila {r:3d} | {co:25s} | {ro[:35]:35s} | {st}")
if len(to_delete) > 10:
    print(f"  ... y {len(to_delete)-10} más")

if not to_delete:
    print("\nNada que eliminar.")
    sys.exit(0)

# Ordenar de mayor a menor fila (borrar desde abajo para no desplazar)
to_delete_sorted = sorted(to_delete, key=lambda x: x[0], reverse=True)

# Construir requests de deleteDimension en batch
requests = []
for real_row, _, _, _ in to_delete_sorted:
    requests.append({
        "deleteDimension": {
            "range": {
                "sheetId": LINKEDIN_ID,
                "dimension": "ROWS",
                "startIndex": real_row - 1,   # 0-based
                "endIndex":   real_row         # exclusive
            }
        }
    })

print(f"\nEliminando {len(requests)} filas...")
# Google tiene límite de 1000 requests por batch — lo dividimos en chunks
CHUNK = 500
for i in range(0, len(requests), CHUNK):
    chunk = requests[i:i+CHUNK]
    svc.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": chunk}
    ).execute()
    print(f"  Chunk {i//CHUNK + 1}: {len(chunk)} filas eliminadas")

print(f"\n[OK] {len(to_delete)} filas eliminadas del tab LinkedIn.")
print("La lista queda mas compacta ahora.")
