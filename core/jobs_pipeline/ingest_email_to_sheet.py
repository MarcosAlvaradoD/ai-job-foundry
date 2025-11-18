# ingest_email_to_sheet.py
# -*- coding: utf-8 -*-

# =============== CONFIG ============================
SHEET_ID_FIXED  = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"  # fallback
SHEET_ID        = __import__("os").getenv("SHEET_ID", SHEET_ID_FIXED)

TAB_REGISTRY    = "Registry"
TAB_LINKEDIN    = "LinkedIn"
TAB_INDEED      = "Indeed"
TAB_GLASSDOOR   = "Glassdoor"

LABEL_PATH      = "JOBS/Inbound"
QUERY_DAYS      = 60
MAX_RESULTS     = 50

LOG_TO_FILE     = True
SEEN_IDS_FILE   = "state/seen_ids.json"
CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_PATH          = "token.json"
# ====================================================

import os, re, json, base64, pathlib, datetime as dt
from email import policy
from email.parser import BytesParser
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

pathlib.Path("state").mkdir(exist_ok=True)

# ---- columnas únicas y en orden (A:Z)
HEADERS = [
    "CreatedAt","Company","Role","Location","RemoteScope",
    "ApplyURL","Source","RecruiterEmail","Currency","Comp",
    "Seniority","WorkAuthReq","Status","NextAction","SLA_Date",
    "ContactName","ContactEmail","ThreadId","LastEmailAt",
    "LastEmailSnippet","FitScore","Why","Notes","UseLaTeXCV"
]

def log(msg):
    print(msg)
    if LOG_TO_FILE:
        with open("ingest.log", "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now().isoformat()} {msg}\n")

# ---- Google APIs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
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

# ---- URL helpers
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

# ---------- Sheets helpers ----------
def ensure_tab_exists_and_headers(ssvc, sheet_id: str, tab: str):
    # 1) si no existe, créala
    try:
        ssvc.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=f"{tab}!A1"
        ).execute()
    except Exception:
        try:
            ssvc.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={"requests":[{"addSheet":{"properties":{"title": tab}}}]}
            ).execute()
            log(f"[SHEETS] Creada pestaña {tab}")
        except Exception as e:
            log(f"[SHEETS] Aviso creando {tab}: {e}")

    # 2) headers en la fila 1 si está vacía
    try:
        res = ssvc.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=f"{tab}!1:1"
        ).execute()
        vals = res.get("values", [])
        if not vals:
            ssvc.spreadsheets().values().update(
                spreadsheetId=sheet_id, range=f"{tab}!1:1",
                valueInputOption="RAW",
                body={"values":[HEADERS]}
            ).execute()
            log(f"[SHEETS] Headers creados en {tab}")
    except Exception as e:
        # Fuerza los headers si la lectura falló
        try:
            ssvc.spreadsheets().values().update(
                spreadsheetId=sheet_id, range=f"{tab}!1:1",
                valueInputOption="RAW",
                body={"values":[HEADERS]}
            ).execute()
            log(f"[SHEETS] Headers forzados en {tab}")
        except Exception as e2:
            log(f"[SHEETS] Error headers {tab}: {e2}")

def existing_urls_set(ssvc, sheet_id: str, tabs: list[str]) -> set[str]:
    s = set()
    for tab in tabs:
        try:
            res = ssvc.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f"{tab}!A:Z"
            ).execute()
            vals = res.get("values", [])
            if not vals: continue
            headers, rows = vals[0], vals[1:]
            if "ApplyURL" not in headers: continue
            idx = headers.index("ApplyURL")
            for r in rows:
                if idx < len(r) and r[idx]:
                    s.add(normalize_url(r[idx]))
        except Exception:
            pass
    return s

def row_to_values(row: dict) -> list:
    # produce la fila en el orden exacto de HEADERS
    return [str(row.get(h, "") or "") for h in HEADERS]

def sheet_append(ssvc, sheet_id: str, tab: str, rows: list[dict]) -> int:
    if not rows: return 0
    body = {"values": [row_to_values(r) for r in rows]}
    ssvc.spreadsheets().values().append(
        spreadsheetId=sheet_id, range=f"{tab}!A:Z",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    return len(rows)

# ---------- Gmail parsing ----------
def list_message_ids(gsvc, query, max_results=50):
    log(f"[GMAIL] Query: {query}")
    res = gsvc.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
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
        role = subject.strip()[:80]

    # Regla ATS → UseLaTeXCV = Yes
    use_latex = ""
    try:
        host = urlparse(url).netloc.lower()
        if any(d in host for d in (
            "workday","myworkdayjobs","greenhouse","lever","icims",
            "smartrecruiters","taleo","successfactors","adp","workable","workforcenow"
        )):
            use_latex = "Yes"
    except Exception:
        pass

    return {
        "CreatedAt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Company": company,
        "Role": role,
        "Location": "",
        "RemoteScope": "",
        "ApplyURL": url,
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
        "UseLaTeXCV": use_latex,
    }

# ---------- seen ids ----------
def load_seen_ids():
    try:
        with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen_ids(ids):
    with open(SEEN_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(ids)), f)

# ---------- main ----------
def main():
    log("="*70)
    log("Ingest v2 arrancando…")

    if not SHEET_ID:
        raise SystemExit("❌ SHEET_ID no definido. Exporta SHEET_ID o edita la constante.")

    creds = get_creds()
    gsvc = gmail_service(creds)
    ssvc = sheets_service(creds)

    # Pestañas y headers
    for t in (TAB_REGISTRY, TAB_LINKEDIN, TAB_INDEED, TAB_GLASSDOOR):
        ensure_tab_exists_and_headers(ssvc, SHEET_ID, t)

    # Dedupe global por ApplyURL
    all_urls = existing_urls_set(
        ssvc, SHEET_ID, [TAB_REGISTRY, TAB_LINKEDIN, TAB_INDEED, TAB_GLASSDOOR]
    )

    def maybe_add(tab_name, row_dict, bucket):
        url = normalize_url(row_dict.get("ApplyURL",""))
        if url and url in all_urls:
            log(f"[SKIP] Duplicada por URL -> {url}")
            return False
        if url:
            all_urls.add(url)
        bucket[tab_name].append(row_dict)
        return True

    query = f'label:"{LABEL_PATH}" newer_than:{QUERY_DAYS}d'
    ids = list_message_ids(gsvc, query, MAX_RESULTS)

    seen = load_seen_ids()
    new_seen = set(seen)

    rows_by_tab = {
        TAB_REGISTRY: [], TAB_LINKEDIN: [], TAB_INDEED: [], TAB_GLASSDOOR: []
    }
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
        log(f"[{mid}] source={source} | subj='{subject}' | url={url or '-'}")

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

    total_inserted = 0
    for tab, rows in rows_by_tab.items():
        n = sheet_append(ssvc, SHEET_ID, tab, rows)
        total_inserted += n
        log(f"[SHEETS] {tab}: insertadas {n} filas")

    save_seen_ids(new_seen)
    log(f"Listo. Nuevas filas insertadas: {total_inserted}. Correos inspeccionados: {inspected}")

if __name__ == "__main__":
    main()
