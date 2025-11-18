
# -*- coding: utf-8 -*-
"""
verify_sheet_access.py
Verifica acceso a un Google Sheet SIN modificar tu token principal de escritura.
- Usa su propio token: token_readonly.json
- Scope: spreadsheets.readonly + openid + email (diagnóstico)
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ¡OJO! Scope SOLO LECTURA y token separado:
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "openid",
    "email",
]

TOKEN_FILE = "token_readonly.json"

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print("[ok] token_readonly.json generado/refrescado.")
    return build("sheets", "v4", credentials=creds), creds

def whoami(creds):
    # Muestra el email del token si existe (sin llamar APIs extra)
    info = getattr(creds, "_id_token", None) or {}
    email = getattr(info, "get", lambda *_: None)("email")
    return email or "(desconocido)"

def main():
    SHEET_ID = os.getenv("SHEET_ID", "").strip()
    if not SHEET_ID:
        print("Falta --sheet o SHEET_ID")
        return

    svc, creds = get_service()
    print(f"Autenticado como: {whoami(creds)}")
    try:
        meta = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        title = meta.get("properties", {}).get("title", "(sin título)")
        print(f"[ok] Acceso de lectura a: {title}")
    except HttpError as e:
        if e.resp.status == 404:
            print("❌ 404 Not Found:\n"
                  "  - El SHEET_ID no existe o\n"
                  "  - No has compartido el documento con esta cuenta (Editor o al menos Lector).\n"
                  "  ➜ Ábrelo en Google Sheets y comparte con el correo mostrado arriba.")
        else:
            print(f"❌ HTTP {e.resp.status}: {e}")
        return

if __name__ == "__main__":
    main()
