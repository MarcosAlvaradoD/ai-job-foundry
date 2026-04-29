# ingest_job.py
# ------------------ PASO 0: EDITA AQUÍ ------------------
SPREADSHEET_ID = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"
DEFAULT_TAB = "LinkedIn"  # si no especificas Source
LMS_URL   = "http://127.0.0.1:11434/v1/chat/completions"
LMS_MODEL = "google/gemma-3-12b"   # o "qwen2.5-14b-instruct", etc.
# Filtros de Mark:
REMOTE_RULE = "Global OK; if restricted accept MX, LATAM, or US timezones if no residency/visa required."
TARGET_COMP_USD = "65-90k USD (mark Notes: unknown salary if missing). MX: >= 50,000 MXN."
# --------------------------------------------------------

import os, json, time, requests, re
from typing import Dict, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

HEADERS = [
    "CreatedAt","Company","Role","Location","RemoteScope","ApplyURL",
    "Source","RecruiterEmail","Currency","Comp","Seniority","WorkAuthReq",
    "Status","NextAction","Notes"
]

def sheets_service():
    sa_path = os.path.expanduser(r"C:\Users\MSI\Documents\service_account.json")
    scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly"
]
    creds = Credentials.from_service_account_file(sa_path, scopes=scopes)
    return build("sheets", "v4", credentials=creds)

def read_all_apply_urls(svc, tab) -> set:
    # Busca ApplyURL (col F) desde F2:F
    rng = f"{tab}!F2:F"
    res = svc.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=rng).execute()
    vals = res.get("values", [])
    return set(v[0].strip() for v in vals if v and v[0].strip())

def append_row(svc, tab, row: List[str]):
    rng = f"{tab}!A:A"
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values":[row]}
    ).execute()

def lm_extract(text: str, source: str) -> Dict:
    prompt = f"""
You extract structured fields for a job opportunity. If salary missing, set Currency='' and Comp=''; put 'Notes: unknown salary' in Notes.
Input text (source={source}):
{text}

Remote rule for candidate: {REMOTE_RULE}
Target comp: {TARGET_COMP_USD}

Return strict JSON with keys:
Company, Role, Location, RemoteScope, ApplyURL, RecruiterEmail, Currency, Comp, Seniority, WorkAuthReq, Notes
"""
    payload = {
        "model": LMS_MODEL,
        "temperature": 0.1,
        "messages": [
            {"role":"system","content":"You are an expert ATS data normalizer. Output valid JSON only."},
            {"role":"user","content": prompt}
        ]
    }
    r = requests.post(LMS_URL, json=payload, timeout=60)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    # limpiar fences si los hay
    content = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE)
    return json.loads(content)

def make_row(rec: Dict, source: str) -> List[str]:
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    vals = {
        "CreatedAt": now,
        "Company": rec.get("Company",""),
        "Role": rec.get("Role",""),
        "Location": rec.get("Location",""),
        "RemoteScope": rec.get("RemoteScope",""),
        "ApplyURL": rec.get("ApplyURL",""),
        "Source": source,
        "RecruiterEmail": rec.get("RecruiterEmail",""),
        "Currency": rec.get("Currency",""),
        "Comp": rec.get("Comp",""),
        "Seniority": rec.get("Seniority",""),
        "WorkAuthReq": rec.get("WorkAuthReq",""),
        "Status": "New",
        "NextAction": "",
        "Notes": rec.get("Notes","")
    }
    return [vals.get(h,"") for h in HEADERS]

def ingest(svc, source: str, raw_text: str, tab: str):
    record = lm_extract(raw_text, source)
    apply_url = (record.get("ApplyURL") or "").strip()
    if not apply_url:
        raise ValueError("No ApplyURL found by LLM — pega la URL del portal real de aplicación en el texto.")
    seen = read_all_apply_urls(svc, tab)
    if apply_url in seen:
        print("↩️  Duplicate (ApplyURL ya existe). No se inserta.")
        return
    row = make_row(record, source)
    append_row(svc, tab, row)
    print("✅ Ingestado en", tab, "|", record.get("Company"), "—", record.get("Role"))

if __name__ == "__main__":
    import argparse, sys
    p = argparse.ArgumentParser(description="Ingesta de vacantes -> Google Sheet con dedupe por ApplyURL.")
    p.add_argument("--source", default=DEFAULT_TAB, help="LinkedIn/Indeed/... (también se usa como pestaña)")
    p.add_argument("--file", help="Ruta a txt con la vacante; si se omite, lee stdin.")
    args = p.parse_args()

    svc = sheets_service()
    # lee input
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print("Pega la descripción (Ctrl+V). Termina con Ctrl+Z + Enter:")
        text = sys.stdin.read()

    ingest(svc, args.source, text, args.source)
