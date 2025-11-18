REPLACE-WHOLE-FILE: verify_sheet_access.py

# -*- coding: utf-8 -*-
"""
verify_sheet_access.py

Verifica:
  - Con qué cuenta de Google estás autenticado (email)
  - Si el SHEET_ID es accesible: imprime título y lista de pestañas

Requisitos:
  pip install google-api-python-client google-auth-oauthlib

Uso:
  $env:SHEET_ID="<tu_id>"
  py verify_sheet_access.py
"""

import os
import sys
from typing import Tuple

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes:
#  - spreadsheets.readonly   -> para leer metadata de la hoja
#  - openid + userinfo.email -> para poder leer el email del usuario OAuth
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]

def get_creds() -> Credentials:
    """Carga token.json o arranca flujo OAuth con credentials.json."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print("[ok] token.json generado/refrescado.")
    return creds

def whoami(creds: Credentials) -> str:
    """
    Devuelve el correo de la cuenta autenticada usando la API oauth2 v2.
    Si no se puede, retorna '(desconocido)'.
    """
    try:
        oauth2 = build("oauth2", "v2", credentials=creds)
        info = oauth2.userinfo().get().execute()
        return info.get("email", "(desconocido)")
    except Exception:
        return "(desconocido)"

def check_sheet(service, sheet_id: str) -> Tuple[str, list]:
    """
    Hace spreadsheets.get (no values.get) para leer título y pestañas.
    Retorna (title, [tab_names])
    """
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    title = meta.get("properties", {}).get("title", "(sin título)")
    tabs = [s["properties"]["title"] for s in meta.get("sheets", [])]
    return title, tabs

def main():
    sheet_id = os.getenv("SHEET_ID", "").strip()
    if not sheet_id:
        print("Falta --sheet o SHEET_ID en el entorno.")
        sys.exit(1)

    # 1) Autenticación y correo
    creds = get_creds()
    email = whoami(creds)
    print(f"Autenticado como: {email}")

    # 2) Construye servicio de Sheets (solo lectura)
    svc = build("sheets", "v4", credentials=creds)

    # 3) Verificación de acceso a la hoja
    try:
        title, tabs = check_sheet(svc, sheet_id)
        print(f"[OK] Acceso a spreadsheet: '{title}'")
        if tabs:
            print("    Pestañas:", ", ".join(tabs))
        else:
            print("    (no se encontraron pestañas)")
        print("✅ Verificación completada.")
    except HttpError as e:
        status = getattr(e, "resp", None).status if hasattr(e, "resp") else None
        if status == 404:
            print("❌ 404 Not Found:")
            print("   - El SHEET_ID no existe o")
            print("   - NO has compartido el documento con esta cuenta:", email)
            print("     > Ábrelo en Google Sheets y comparte con ese correo (lector/edición).")
        elif status == 403:
            print("❌ 403 Forbidden:")
            print("   - Existe el sheet pero tu cuenta no tiene permisos. Comparte con:", email)
        else:
            print("❌ Error de la API:", str(e))
        sys.exit(2)

if __name__ == "__main__":
    main()
