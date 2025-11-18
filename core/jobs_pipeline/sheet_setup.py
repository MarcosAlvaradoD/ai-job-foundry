# sheet_setup.py
# ------------------ PASO 0: EDITA AQUÍ ------------------
SPREADSHEET_ID = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"  # tu sheet
TABS = ["Registry", "LinkedIn", "Indeed", "Glassdoor"]  # agrega más si quieres

HEADERS = [
    "CreatedAt","Company","Role","Location","RemoteScope","ApplyURL",
  "Source","RecruiterEmail","Currency","Comp","Seniority","WorkAuthReq",
  "Status","NextAction","SLA_Date","ContactName","ContactEmail","ThreadId",
  "LastEmailAt","LastEmailSnippet","FitScore","Why","Notes","UseLaTeXCV"
]
# --------------------------------------------------------

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def sheets_service():
    # Usa la misma service account que ya creaste
    sa_path = os.path.expanduser(r"C:\Users\MSI\Documents\service_account.json")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(sa_path, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

def tab_exists(svc, title):
    meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for sh in meta.get("sheets", []):
        if sh["properties"]["title"] == title:
            return True
    return False

def create_tab_if_missing(svc, title):
    if tab_exists(svc, title):
        return
    req = {
        "requests": [
            {"addSheet": {"properties": {"title": title}}}
        ]
    }
    svc.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=req
    ).execute()

def write_headers(svc, title):
    rng = f"{title}!A1:{chr(ord('A')+len(HEADERS)-1)}1"
    body = {"values": [HEADERS]}
    svc.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=rng,
        valueInputOption="RAW",
        body=body
    ).execute()

if __name__ == "__main__":
    svc = sheets_service()
    for t in TABS:
        create_tab_if_missing(svc, t)
        write_headers(svc, t)
    print("✅ Tabs + headers listos:", TABS)
