# ingest_email_to_sheet_v2.py
# -*- coding: utf-8 -*-

# =============== CONFIG ============================
SHEET_ID_FIXED  = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"  # cámbialo si quieres
import os
SHEET_ID        = os.getenv("SHEET_ID", SHEET_ID_FIXED)

# Nombre de pestañas
TAB_REGISTRY    = "Registry"
TAB_LINKEDIN    = "LinkedIn"
TAB_INDEED      = "Indeed"
TAB_GLASSDOOR   = "Glassdoor"

# Gmail / comportamiento
LABEL_PATH      = "JOBS/Inbound"
QUERY_DAYS      = 60
MAX_RESULTS     = 50
LOG_TO_FILE     = True
SEEN_IDS_FILE   = "data/state/seen_ids.json"

# OAuth
CLIENT_SECRETS_FILE = "data/credentials/credentials.json"
TOKEN_PATH          = "data/credentials/token.json"
# ====================================================

import re, json, base64, pathlib, datetime as dt
from email import policy
from email.parser import BytesParser
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

pathlib.Path("data/state").mkdir(parents=True, exist_ok=True)

# ---- columnas únicas y en orden (24 -> X)
HEADERS = [
    "CreatedAt","Company","Role","Location","RemoteScope",
    "ApplyURL","Source","RecruiterEmail","Currency","Comp",
    "Seniority","WorkAuthReq","Status","NextAction","SLA_Date",
    "ContactName","ContactEmail","ThreadId","LastEmailAt",
    "LastEmailSnippet","FitScore","Why","Notes","UseLaTeXCV"
]

# ========= Logging =========
def log(msg: str):
    print(msg)
    if LOG_TO_FILE:
        with open("ingest.log", "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now().isoformat()} {msg}\n")

# ========= Google APIs =========
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar"
]

def get_creds():
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception:
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds

def gmail_service(creds):  return build("gmail", "v1", credentials=creds)
def sheets_service(creds): return build("sheets", "v4", credentials=creds)

# ========= URL helpers =========
STRIP_PARAMS = {
    "utm_source","utm_medium","utm_campaign","utm_term","utm_content",
    "gclid","fbclid","ao","s","guid","src","t","vt","uido","ea","cs","cb",
    "jobListingId","pos"
}
def normalize_url(u: str) -> str:
    if not u: return ""
    try:
        p = urlparse(u.strip())
        p = p._replace(fragment="")
        q = [(k,v) for (k,v) in parse_qsl(p.query, keep_blank_values=True)
             if k not in STRIP_PARAMS]
        p = p._replace(query=urlencode(q), netloc=p.netloc.lower())
        return urlunparse(p)
    except Exception:
        return u.strip()

# ========= Sheets helpers =========
def ensure_tab_exists_and_headers(ssvc, tab: str):
    """Crea pestaña si falta y escribe headers en A1:X1 si la fila 1 está vacía."""
    # 1) crear pestaña si no existe
    try:
        ssvc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f"{tab}!A1"
        ).execute()
    except Exception:
        try:
            ssvc.spreadsheets().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={"requests": [{"addSheet": {"properties": {"title": tab}}}]},
            ).execute()
            log(f"[SHEETS] Pestaña creada: {tab}")
        except Exception as e:
            log(f"[SHEETS] Aviso creando {tab}: {e}")

    # 2) headers en A1:X1 (24 columnas)
    try:
        res = ssvc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f"{tab}!1:1"
        ).execute()
        row = res.get("values", [])
        if not row:
            ssvc.spreadsheets().values().update(
                spreadsheetId=SHEET_ID,
                range=f"{tab}!1:1",
                valueInputOption="RAW",
                body={"values": [HEADERS]},
            ).execute()
            log(f"[SHEETS] Headers escritos en {tab}")
    except Exception as e:
        # si falló lectura, intenta escribir igual
        try:
            ssvc.spreadsheets().values().update(
                spreadsheetId=SHEET_ID,
                range=f"{tab}!1:1",
                valueInputOption="RAW",
                body={"values": [HEADERS]},
            ).execute()
            log(f"[SHEETS] Headers escritos (fallback) en {tab}")
        except Exception as e2:
            log(f"[SHEETS] Error headers {tab}: {e2}")

def existing_urls_set(ssvc, tabs: list[str]) -> set[str]:
    s = set()
    for tab in tabs:
        try:
            res = ssvc.spreadsheets().values().get(
                spreadsheetId=SHEET_ID, range=f"{tab}!A:Z"
            ).execute()
            vals = res.get("values", [])
            if not vals: 
                continue
            headers, rows = vals[0], vals[1:]
            try:
                idx = headers.index("ApplyURL")
            except ValueError:
                continue
            for r in rows:
                if idx < len(r) and r[idx]:
                    s.add(normalize_url(r[idx]))
        except Exception:
            pass
    return s

def row_from_dict(d: dict) -> list[str]:
    """Convierte dict -> fila en el orden exacto de HEADERS."""
    return [str(d.get(k, "") or "") for k in HEADERS]

def append_rows(ssvc, tab: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    values = [row_from_dict(r) for r in rows]
    ssvc.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{tab}!A:Z",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
    return len(values)

# ========= ATS helpers =========
ATS_DOMAINS = (
    "workday", "myworkdayjobs", "greenhouse", "lever",
    "icims", "smartrecruiters", "taleo", "successfactors",
    "adp", "workable", "workforcenow"
)
def is_ats(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
        return any(d in host for d in ATS_DOMAINS)
    except Exception:
        return False

def detect_tab_from_url(url: str) -> str:
    host = ""
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        pass
    if "linkedin." in host:  return TAB_LINKEDIN
    if "indeed."   in host:  return TAB_INDEED
    if "glassdoor." in host: return TAB_GLASSDOOR
    return TAB_REGISTRY

# ========= Gmail parsing =========
def list_message_ids(gsvc, query, max_results=50):
    log(f"[GMAIL] Query: {query}")
    res = gsvc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    ids = [m["id"] for m in res.get("messages", [])]
    log(f"[GMAIL] {len(ids)} mensajes candidatos")
    return ids

def get_message(gsvc, msg_id):
    return gsvc.users().messages().get(userId="me", id=msg_id, format="raw").execute()

def parse_email_raw(raw_b64):
    raw_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    subject = msg["subject"] or ""
    sender  = msg["from"] or ""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if (part.get_content_type() or "") == "text/plain":
                try: body += part.get_content()
                except: pass
    else:
        if (msg.get_content_type() or "") == "text/plain":
            try: body = msg.get_content()
            except: pass
    return subject, sender, body

def first_url(text):
    m = re.search(r'https?://\S+', text)
    return m.group(0) if m else ""

def detect_source(subject, sender, body, url):
    low = (subject + " " + sender + " " + body + " " + url).lower()
    if "linkedin" in low or "lnkd.in" in low: return "LinkedIn"
    if "indeed"   in low: return "Indeed"
    if "glassdoor" in low: return "Glassdoor"
    return "Unknown"

def parse_job_fields(source, subject, body, url):
    role, company = "", ""
    m = re.search(r'(?P<role>.+?)\s+at\s+(?P<company>.+)', subject, flags=re.I)
    if m:
        role = m.group("role").strip()
        company = m.group("company").strip()
    m2 = re.search(r'(?P<company>.+?)\s*-\s*(?P<role>.+)', subject)
    if not role and m2:
        company = company or m2.group("company").strip()
        role = role or m2.group("role").strip()
    if not role:
        role = subject.strip()[:120]

    row = {
        "CreatedAt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Company": company,
        "Role": role,
        "Location": "",
        "RemoteScope": "",
        "ApplyURL": normalize_url(url),
        "Source": source,
        "RecruiterEmail": "",
        "Currency": "",
        "Comp": "",
        "Seniority": "",
        "WorkAuthReq": "",
        "Status": "",
        "NextAction": "",
        "SLA_Date": "",
        "ContactName": "",
        "ContactEmail": "",
        "ThreadId": "",
        "LastEmailAt": "",
        "LastEmailSnippet": "",
        "FitScore": "",
        "Why": "",
        "Notes": subject,
        "UseLaTeXCV": "Yes" if is_ats(url) else "",
    }
    return row

# ========= Seen IDs =========
def load_seen_ids():
    try:
        with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen_ids(ids):
    with open(SEEN_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(ids)), f)

# ========= Main =========
def main():
    print("="*70)
    print("Ingest v2 arrancando…")

    if not SHEET_ID:
        raise SystemExit("❌ SHEET_ID no definido. Exporta SHEET_ID o edita SHEET_ID_FIXED en el script.")

    creds = get_creds()
    gsvc = gmail_service(creds)
    ssvc = sheets_service(creds)

    # Asegura pestañas y headers
    for tab in (TAB_REGISTRY, TAB_LINKEDIN, TAB_INDEED, TAB_GLASSDOOR):
        ensure_tab_exists_and_headers(ssvc, tab)

    # Dedupe global por ApplyURL (todas las pestañas)
    all_urls = existing_urls_set(ssvc, [TAB_REGISTRY, TAB_LINKEDIN, TAB_INDEED, TAB_GLASSDOOR])

    def maybe_add(tab_name, row_dict, buckets):
        url = row_dict.get("ApplyURL","")
        if url:
            u = normalize_url(url)
            if u in all_urls:
                log(f"[SKIP] Duplicada por URL -> {u}")
                return False
            all_urls.add(u)
            row_dict["ApplyURL"] = u
        buckets[tab_name].append(row_dict)
        return True

    # Buscar mensajes
    query = f'label:"{LABEL_PATH}" newer_than:{QUERY_DAYS}d'
    ids = list_message_ids(gsvc, query, MAX_RESULTS)

    seen = load_seen_ids()
    new_seen = set(seen)

    rows_by_tab = {TAB_REGISTRY: [], TAB_LINKEDIN: [], TAB_INDEED: [], TAB_GLASSDOOR: []}
    inspected = 0

    for mid in ids:
        if mid in seen:
            log(f"  - {mid} ya procesado (skip).")
            continue
        inspected += 1

        msg = get_message(gsvc, mid)
        subject, sender, body = parse_email_raw(msg["raw"])
        url = first_url(subject + "\n" + body)
        source = detect_source(subject, sender, body, url)
        tab = {
            "LinkedIn": TAB_LINKEDIN,
            "Indeed": TAB_INDEED,
            "Glassdoor": TAB_GLASSDOOR
        }.get(source, TAB_REGISTRY)

        if not url and len(subject.strip()) < 6:
            log("    -> descartado: sin URL y subject corto")
            new_seen.add(mid)
            continue

        row = parse_job_fields(source, subject, body, url)
        maybe_add(tab, row, rows_by_tab)
        new_seen.add(mid)

    # Escribir por pestaña
    total = 0
    for tab, rows in rows_by_tab.items():
        n = append_rows(ssvc, tab, rows)
        total += n
        log(f"[SHEETS] {tab}: insertadas {n} filas")

    save_seen_ids(new_seen)
    log(f"Listo. Nuevas filas insertadas: {total}. Correos inspeccionados: {inspected}")

if __name__ == "__main__":
    main()
