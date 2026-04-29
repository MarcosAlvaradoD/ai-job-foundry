#!/usr/bin/env python3
"""
Marca HCLTech (fila 351, tab LinkedIn) como Applied en el Google Sheet.
También registra fecha de aplicación y método.
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
TOKEN_PATH = os.path.join(Path(__file__).parent.parent, "data", "credentials", "token.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)

svc = get_sheets_service()
sheets = svc.spreadsheets()

# Fila 351 = HCLTech (primera vacante insertada en insert_jobs_today.py)
# Columnas (A=1): A=Empresa, B=Puesto, C=Ubicacion, D=Remoto, E=ApplyURL,
#                 F=Fuente, G=Moneda, H=Comp, I=Seniority, J=Fit, K=Notes,
#                 L=Status, M=FechaAplicacion, ...
# La columna de Status varía por sheet — revisamos primero la fila

range_check = "LinkedIn!A351:R351"
result = sheets.values().get(spreadsheetId=SHEET_ID, range=range_check).execute()
row = result.get("values", [[]])[0]
print(f"Fila 351 actual ({len(row)} cols): {row[:6]}...")

# Columna L (índice 11) = Status, Columna M (índice 12) = FechaAplicacion
# Actualizar Status → "Applied" y agregar fecha
update_range = "LinkedIn!L351:M351"
sheets.values().update(
    spreadsheetId=SHEET_ID,
    range=update_range,
    valueInputOption="USER_ENTERED",
    body={"values": [["Applied", "2026-04-01"]]}
).execute()

print("✓ HCLTech marcado como Applied (2026-04-01) en LinkedIn!L351:M351")
