# smoke_check.py — Paso 0 con CONFIG claro (LM Studio + ToolUse + Sheets + Gmail)
import os, json, time, requests

# =========================
# ======  C O N F I G =====
# =========================
# 1) LM Studio
LMS_URL   = "http://127.0.0.1:11434/v1/chat/completions"   # cambia si usas otro puerto
LMS_MODEL = "google/gemma-3-12b"                           # copia el "API identifier" tal cual desde LM Studio

# 2) Google Sheets (Service Account)
JOBS_SHEET_ID     = "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg"
GOOGLE_CREDS_JSON = r"C:\Users\MSI\Documents\service_account.json"
TAB_REGISTRY      = "Registry"                             # nombre exacto de la pestaña

# 3) Gmail (OAuth de usuario)
GMAIL_QUERY = 'label:"JOBS/Inbound" newer_than:14d'          # tu label anidada

# =========================
# ======  F U N C S  ======
# =========================
def ping_lmstudio():
    payload = {
        "model": LMS_MODEL,
        "temperature": 0.1,
        "messages": [
            {"role":"system","content":"You are a terse assistant."},
            {"role":"user","content":"Reply with the word OK."}
        ]
    }
    r = requests.post(LMS_URL, json=payload, timeout=30)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return "OK" in content.upper()

def tool_use_test():
    tools = [{
        "type":"function",
        "function":{
            "name":"fetch_url",
            "description":"Fetch a URL and return its text content",
            "parameters":{"type":"object","properties":{
                "url":{"type":"string","description":"HTTP or HTTPS URL"}
            },"required":["url"]}
        }
    }]
    messages = [
        {"role":"system","content":"You can call tools to browse the web."},
        {"role":"user","content":"Use fetch_url to read https://httpbin.org/uuid and return only the uuid."}
    ]
    r = requests.post(LMS_URL, json={
        "model":LMS_MODEL,"messages":messages,"tools":tools,"tool_choice":"auto"
    }, timeout=60)
    r.raise_for_status()
    data = r.json()
    msg = data["choices"][0]["message"]

    if "tool_calls" not in msg:
        return False, "Model did not request tool."

    for call in msg["tool_calls"]:
        if call["function"]["name"] == "fetch_url":
            args = json.loads(call["function"]["arguments"])
            url = args["url"]
            text = requests.get(url, timeout=30).text  # aquí “sale a internet”
            messages += [
                msg,
                {"role":"tool","tool_call_id":call["id"],"name":"fetch_url","content":text}
            ]
            r2 = requests.post(LMS_URL, json={"model":LMS_MODEL,"messages":messages}, timeout=60)
            r2.raise_for_status()
            out = r2.json()["choices"][0]["message"]["content"].strip()
            return True, out
    return False, "No fetch_url call."

def test_sheets():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_JSON, scopes=scopes)
    svc = build("sheets","v4",credentials=creds)

    # Mostrar pestañas existentes (debug)
    meta = svc.spreadsheets().get(spreadsheetId=JOBS_SHEET_ID).execute()
    titles = [s["properties"]["title"] for s in meta["sheets"]]
    print("Tabs actuales:", titles)

    # Crear pestaña si falta
    if TAB_REGISTRY not in titles:
        svc.spreadsheets().batchUpdate(
            spreadsheetId=JOBS_SHEET_ID,
            body={"requests":[{"addSheet":{"properties":{"title": TAB_REGISTRY}}}]}
        ).execute()

    body = {"values":[[time.strftime("%F %T"), "SMOKE", "OK"]]}
    # OJO: comillas simples alrededor del nombre del tab
    svc.spreadsheets().values().append(
        spreadsheetId=JOBS_SHEET_ID,
        range=f"'{TAB_REGISTRY}'!A:C",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    return True

def test_gmail():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    if not os.path.exists("credentials.json"):
        raise FileNotFoundError(
            "credentials.json no existe. Crea el OAuth client (Desktop app) en Cloud Console y "
            "coloca el archivo junto a este script."
        )

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json","w") as f: f.write(creds.to_json())

    service = build('gmail','v1',credentials=creds)
    resp = service.users().messages().list(userId='me', q=GMAIL_QUERY, maxResults=3).execute()
    ids = [m["id"] for m in resp.get("messages",[])]
    return ids

def list_subjects():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    svc = build("gmail","v1",credentials=creds)

    resp = svc.users().messages().list(userId="me", q='label:"JOBS/Inbound"', maxResults=3).execute()
    for m in resp.get("messages", []):
        msg = svc.users().messages().get(userId="me", id=m["id"], format="metadata", metadataHeaders=["Subject","From"]).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        print(headers.get("From","(sin From)"), "—", headers.get("Subject","(sin Subject)"))

# Llama list_subjects() desde __main__ después de test_gmail()





if __name__ == "__main__":
    try:
        print("1) LM Studio:", "OK" if ping_lmstudio() else "FAIL")
    except Exception as e:
        print("1) LM Studio: FAIL ->", e)

    try:
        ok, msg = tool_use_test()
        print("2) ToolUse:", "OK" if ok else f"FAIL ({msg})", "| Output:", (msg[:80]+"...") if isinstance(msg,str) else msg)
    except Exception as e:
        print("2) ToolUse: FAIL ->", e)

    try:
        print("3) Sheets:", "OK" if test_sheets() else "FAIL")
    except Exception as e:
        print("3) Sheets: FAIL ->", e)

    try:
        print("4) Gmail IDs:", test_gmail())
    except Exception as e:
        print("4) Gmail: FAIL ->", e)

# al final del __main__, después del bloque de Gmail:
    try:
        list_subjects()
    except Exception as e:
        print("list_subjects: FAIL ->", e)

