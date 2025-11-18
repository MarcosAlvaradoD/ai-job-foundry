import os, re, json, time
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

from dotenv import load_dotenv
import requests

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ----------------- CONFIG -----------------
load_dotenv()
SHEET_ID     = os.getenv("SHEET_ID", "1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL    = os.getenv("LLM_MODEL", "google/gemma-3-12b")


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
]
TABS = ["Registry","LinkedIn","Indeed","Glassdoor"]
HEADERS = ["CreatedAt","Company","Role","Location","RemoteScope","ApplyURL","Source","RecruiterEmail","Currency","Comp","Seniority","WorkAuthReq","Status","NextAction","Notes"]

# Marca para saber si ya pasamos por LLM (no obligatoria, pero útil)
PROCESSED_FLAG = "ParsedOK"

# --------------- AUTH / SHEETS ---------------
def get_creds():
    # Usa el token.json creado por tus otros scripts
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return creds

def get_svc():
    return build("sheets","v4", credentials=get_creds()).spreadsheets().values()

def read_sheet_tab(svc, tab_name: str):
    rng = f"{tab_name}!A:Z"
    res = svc.get(spreadsheetId=SHEET_ID, range=rng).execute()
    values = res.get("values", [])
    if not values:
        return [], []
    headers = values[0]
    rows = values[1:]
    return headers, rows

def write_sheet_tab(svc, tab_name: str, rows_out):
    if not rows_out:
        return
    rng = f"{tab_name}!A2"
    svc.update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body={"values": rows_out}
    ).execute()

def write_rows(svc, tab, start_row_index, headers, new_rows):
    if not new_rows:
        return
    rng = f"{tab}!A{start_row_index}:Z"
    svc.update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body={"values": new_rows}
    ).execute()


# --------------- URL NORMALIZATION ---------------
STRIP_PARAMS = {
    # comunes
    "utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid",
    # glassdoor/indeed/linkedin habituales
    "ao","s","guid","src","t","vt","uido","ea","cs","cb","jobListingId","pos"
}

def normalize_url(u: str) -> str:
    if not u:
        return ""
    try:
        p = urlparse(u.strip())
        # quita fragment
        fragless = p._replace(fragment="")
        # limpia query
        q = [(k,v) for (k,v) in parse_qsl(fragless.query, keep_blank_values=True) if k not in STRIP_PARAMS]
        fragless = fragless._replace(query=urlencode(q))
        # normaliza host (lower) y path
        fragless = fragless._replace(netloc=fragless.netloc.lower())
        return urlunparse(fragless)
    except Exception:
        return u.strip()

# --------------- LLM CALL ---------------
SYSTEM_PROMPT = (
    "Eres un asistente que extrae información estructurada de ofertas de trabajo. "
    "Devuelve **solo JSON** con estas claves:\n"
    "{"
    "\"Company\":\"string or empty\","
    "\"Role\":\"string or empty\","
    "\"Location\":\"string or empty\","
    "\"RemoteScope\":\"Onsite|Hybrid|Remote|Unknown\","
    "\"Currency\":\"string or empty\","
    "\"Comp\":\"string or empty\","
    "\"Seniority\":\"string or empty\","
    "\"WorkAuthReq\":\"string or empty\","
    "\"Notes\":\"string or empty\""
    "}\n"
    "Si no hay dato, deja \"\" o valores sugeridos (RemoteScope puede ser Unknown). "
    "No añadas texto fuera del JSON."
)

def call_llm(subject: str, body: str, url: str, source: str) -> dict:
    user_prompt = f"""
Extrae fields de esta oferta. 
SOURCE: {source}
URL: {url}

SUBJECT:
{subject}

BODY:
{body}
"""
    payload = {
        "model": LLM_MODEL,
        "messages":[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": user_prompt}
        ],
        "temperature": 0.2
    }
    r = requests.post(LLM_BASE_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    # intenta parsear JSON
    try:
        return json.loads(content)
    except Exception:
        # a veces el modelo rodea el json; intenta limpiarlo
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            return json.loads(m.group(0))
        return {}

# --------------- MAIN LOGIC ---------------
def ensure_headers(headers):
    # arma mapa de col -> index, respetando HEADERS
    colmap = {}
    for i, h in enumerate(headers):
        colmap[h] = i
    # completa si faltan columnas
    changed = False
    for i, h in enumerate(HEADERS):
        if h not in colmap:
            headers.append(h)
            colmap[h] = len(headers)-1
            changed = True
    return headers, colmap, changed

def row_to_list(row, headers):
    # extiende fila al tamaño de headers
    r = list(row)
    if len(r) < len(headers):
        r += [""]*(len(headers)-len(r))
    return r

def is_processed(row, colmap):
    status_idx = colmap.get("Status", None)
    if status_idx is None:
        return False
    return PROCESSED_FLAG.lower() in (row[status_idx] or "").lower()

def mark_processed(row, colmap, note=""):
    sidx = colmap["Status"]
    nidx = colmap["Notes"]
    row[sidx] = PROCESSED_FLAG
    if note:
        row[nidx] = (row[nidx] + " | " + note).strip(" |")

def enrich_row(row, colmap, llm_out: dict):
    def put(k, v): 
        if k in colmap and v is not None and str(v).strip():
            row[colmap[k]] = str(v).strip()
    put("Company", llm_out.get("Company",""))
    put("Role", llm_out.get("Role",""))
    put("Location", llm_out.get("Location",""))
    put("RemoteScope", llm_out.get("RemoteScope","Unknown"))
    put("Currency", llm_out.get("Currency",""))
    put("Comp", llm_out.get("Comp",""))
    put("Seniority", llm_out.get("Seniority",""))
    put("WorkAuthReq", llm_out.get("WorkAuthReq",""))
    put("Notes", llm_out.get("Notes",""))

def main():
    svc = get_svc()
    total_updates = 0
    for tab in TABS:
        headers, rows = read_sheet_tab(svc, tab)
        if not headers:
            continue
        headers, colmap, changed = ensure_headers(headers)
        # si agregamos headers nuevos, re-escribe fila 1
        if changed:
            get_svc().update(
                spreadsheetId=SHEET_ID,
                range=f"{tab}!A1:Z1",
                valueInputOption="USER_ENTERED",
                body={"values":[headers]}
            ).execute()


        # procesa filas
        out_rows   = []
        start_at   = 2  # A partir de la fila 2 se escriben updates
        for r in rows:
            row = row_to_list(r, headers)
            # datos base
            subject = row[colmap.get("Role", 2)] if "Role" in colmap else ""   # (por si llenaste Role con el subject inicialmente)
            apply   = row[colmap.get("ApplyURL", 5)] if "ApplyURL" in colmap else ""
            src     = row[colmap.get("Source", 6)] if "Source" in colmap else ""
            created = row[colmap.get("CreatedAt", 0)] if "CreatedAt" in colmap else ""
            # Intenta usar Role como subject si lo habías guardado así; si tu subject real está en otra col, cámbialo.

            # si ya está procesada y no forzamos, salta
            if is_processed(row, colmap):
                out_rows.append(row)
                continue

            # necesitas el cuerpo original para enriquecer más; si no lo tienes, aun así el LLM puede sacar datos del subject y URL
            body = ""  # si luego guardas body en una col, léelo aquí

            # normaliza URL (y reescribe)
            nurl = normalize_url(apply)
            if "ApplyURL" in colmap:
                row[colmap["ApplyURL"]] = nurl

            # llama al LLM
            try:
                llm = call_llm(subject=subject, body=body, url=nurl, source=src or tab)
                enrich_row(row, colmap, llm)
                mark_processed(row, colmap, note="LLM v1")
                total_updates += 1
                # respirito
                time.sleep(0.2)
            except Exception as e:
                # No marcamos como ok, pero guardamos el error en Notes
                nidx = colmap.get("Notes", None)
                if nidx is not None:
                    row[nidx] = (row[nidx] + f" | LLM_ERROR:{e}").strip(" |")

            out_rows.append(row)

        if out_rows:
            write_rows(svc, tab, start_row_index=2, headers=headers, new_rows=out_rows)

    print(f"Enriquecidas/actualizadas: {total_updates}")

if __name__ == "__main__":
    main()
