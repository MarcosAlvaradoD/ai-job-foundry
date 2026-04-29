from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

GOOGLE_CREDS_JSON = r"C:\Users\MSI\Documents\service_account.json"  # <-- tu ruta
SHEET_ID = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"           # <-- tu ID
TAB_NAME = "Registry"

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(GOOGLE_CREDS_JSON, scopes=scopes)
svc = build("sheets", "v4", credentials=creds)

# 1) Asegurar que exista la pestaña
meta = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
titles = [s["properties"]["title"] for s in meta["sheets"]]
if TAB_NAME not in titles:
    svc.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests":[{"addSheet":{"properties":{"title": TAB_NAME}}}]}
    ).execute()

# 2) Append de prueba
body = {"values":[["TEST", "SMOKE", "OK"]]}
svc.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range=f"{TAB_NAME}!A:C",
    valueInputOption="USER_ENTERED",
    body=body
).execute()

print("✅ Sheets conectado y fila insertada en Registry!A:C")
