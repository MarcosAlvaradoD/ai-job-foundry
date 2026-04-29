# enrich_sheet_with_llm_v2.py
# v2 – FitScore + Why + auto-NextAction/SLA por pestaña
# Requiere: requests, python-dateutil, PyPDF2

import os, re, json, argparse, datetime as dt
from dateutil.relativedelta import relativedelta
import requests
from PyPDF2 import PdfReader

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# -------- Config --------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TABS_DEFAULT = ["Registry", "LinkedIn", "Indeed", "Glassdoor"]
MIN_FIT_DEFAULT = 70

# -------- LLM --------
LLM_URL   = os.getenv("LLM_URL", "http://127.0.0.1:11134/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")
print(f"[LLM] URL: {LLM_URL} | MODEL: {LLM_MODEL}")

# Cabeceras estándar (DEBEN estar en fila 1, las generamos si faltan)
COLS = [
    "CreatedAt","Company","Role","Location","RemoteScope","ApplyURL","Source",
    "RecruiterEmail","Currency","Comp","Seniority","WorkAuthReq",
    "Status","NextAction","Notes","FitScore","Why","SLA_Date","RegionRestrict",
    "ThreadId","LastEmailAt","LastEmailSnippet"
]

# ---------- Utilidades de rango ----------
def _col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n-1, 26)
        s = chr(65+r) + s
    return s

def write_range_for(tab: str) -> str:
    """A:LAST según longitud de COLS."""
    last = _col_letter(len(COLS))
    return f"{tab}!A:{last}"

def a1_for_row_block(tab: str, first_row: int, ncols: int, nrows: int) -> str:
    """Devuelve un rango A1 para un bloque rectangular de ncols x nrows desde (first_row, col=1)."""
    last_col = _col_letter(ncols)
    last_row = first_row + nrows - 1
    return f"{tab}!A{first_row}:{last_col}{last_row}"

# ---------- Google Sheets ----------
def get_sheets_service():
    creds = None
    token_path = "token.json"
    cred_path = "credentials.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("sheets", "v4", credentials=creds).spreadsheets()

def read_sheet_tab(svc, sheet_id: str, tab: str):
    # lee suficiente ancho (AZ -> 52 cols) y muchas filas
    rng = f"{tab}!A1:AZ9999"
    res = svc.values().get(spreadsheetId=sheet_id, range=rng).execute()
    values = res.get("values", [])
    if not values:
        return [], []
    headers = values[0]
    rows = values[1:]
    return headers, rows

def ensure_headers(svc, sheet_id: str, tab: str, headers: list) -> list:
    """
    Garantiza que estén TODAS las columnas COLS en fila 1.
    Si falta alguna, reescribe la fila 1 completa con COLS (sin tocar el resto).
    """
    changed = False
    have = list(headers)
    for must in COLS:
        if must not in have:
            changed = True
            have.append(must)

    if changed:
        # sobrescribe la fila 1 de A:LAST con la lista completa COLS
        svc.values().update(
            spreadsheetId=sheet_id,
            range=f"{tab}!A1:{_col_letter(len(COLS))}1",  # <-- AQUÍ va el UPDATE de encabezados
            valueInputOption="RAW",
            body={"values": [COLS]},
        ).execute()
        return COLS[:]  # headers normalizados

    return headers

def write_rows_block(svc, sheet_id: str, tab: str, first_row: int, rows_2d: list):
    """
    Escribe un bloque de filas ya alineadas al número de columnas de headers.
    """
    if not rows_2d:
        return
    ncols = len(rows_2d[0])
    rng = a1_for_row_block(tab, first_row, ncols, len(rows_2d))
    svc.values().update(
        spreadsheetId=sheet_id,
        range=rng,
        valueInputOption="RAW",
        body={"values": rows_2d},
    ).execute()

# --- AÑADIR: helpers de columnas y headers -------------------------------

def a1_col(n: int) -> str:
    """1->A, 26->Z, 27->AA, etc."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def fetch_headers(svc, sheet_id: str, tab: str):
    """Lee la fila 1 de la pestaña y regresa la lista de headers."""
    resp = svc.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{tab}!1:1",
        majorDimension="ROWS",
    ).execute()
    values = resp.get("values", [[]])
    return list(values[0]) if values else []

def ensure_len(arr, n):
    """Rellena con '' hasta longitud n."""
    if len(arr) < n:
        arr.extend([""] * (n - len(arr)))
    return arr

def set_fit_fields(row_list: list, headers: list, fit_score, why_text=None):
    """
    Escribe el número en la columna cuyo header sea 'FitScore'
    y la explicación opcional en la columna 'Why', sin importar su posición.
    """
    try:
        i_fit = headers.index("FitScore")
        ensure_len(row_list, len(headers))
        row_list[i_fit] = fit_score
    except ValueError:
        # No hay header 'FitScore' -> no escribimos
        pass

    if why_text is not None:
        try:
            i_why = headers.index("Why")
            ensure_len(row_list, len(headers))
            row_list[i_why] = why_text
        except ValueError:
            pass

def write_rows_dynamic(svc, sheet_id: str, tab: str, start_row: int, rows_2d: list):
    """
    Escribe filas normalizando su ancho a la cantidad de headers de la pestaña,
    y ampliando el rango A1 dinámicamente hasta la última columna.
    """
    headers = fetch_headers(svc, sheet_id, tab)
    maxw = len(headers) if headers else 26  # por si acaso

    normalized = []
    for r in rows_2d:
        rr = list(r)
        if len(rr) < maxw:
            rr += [""] * (maxw - len(rr))
        elif len(rr) > maxw:
            rr = rr[:maxw]
        normalized.append(rr)

    if not normalized:
        return

    end_row = start_row + len(normalized) - 1
    end_col = a1_col(maxw)
    range_a1 = f"{tab}!A{start_row}:{end_col}{end_row}"

    svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_a1,
        valueInputOption="RAW",
        body={"values": normalized},
    ).execute()
# --- FIN helpers ----------------------------------------------------------


# ---------- CV ----------
def load_cv_text(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    if path.lower().endswith(".pdf"):
        try:
            reader = PdfReader(path)
            return "\n".join([(p.extract_text() or "") for p in reader.pages])
        except Exception as e:
            print(f"[WARN] No pude leer PDF: {e}")
            return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

# ---------- LLM ----------
def llm_fit_score(cv_text: str, job_blob: dict) -> dict:
    """
    Devuelve: {"fit":0-100,"why":str,"remote_scope":str,"region_restrict":str,
               "seniority":str,"work_auth":str}
    """
    sys = (
        "Eres un evaluador de vacantes. "
        "Devuelve JSON con: fit (0-100), why (1 línea), "
        "remote_scope en {Remote, Hybrid, Onsite, Unknown}, "
        "region_restrict, seniority, work_auth."
    )
    usr = (
        f"CV:\n{cv_text[:4000]}\n\n"
        f"JOB:\nCompany: {job_blob.get('Company','')}\n"
        f"Role: {job_blob.get('Role','')}\n"
        f"Location: {job_blob.get('Location','')}\n"
        f"Notes: {job_blob.get('Notes','')}\n"
        f"ApplyURL: {job_blob.get('ApplyURL','')}\n"
        "Responde SOLO JSON."
    )
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role":"system","content":sys},{"role":"user","content":usr}],
        "temperature": 0.2,
        "response_format": {"type":"json_object"},
    }
    try:
        r = requests.post(LLM_URL, json=payload, timeout=90)
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"]
        data = json.loads(txt)
        return {
            "fit": max(0, min(100, int(data.get("fit", 0)))),
            "why": str(data.get("why","")).strip()[:300],
            "remote_scope": (data.get("remote_scope") or "Unknown").strip() or "Unknown",
            "region_restrict": str(data.get("region_restrict","")).strip(),
            "seniority": str(data.get("seniority","")).strip(),
            "work_auth": str(data.get("work_auth","")).strip(),
        }
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return {"fit":0,"why":"LLM_ERROR","remote_scope":"Unknown","region_restrict":"","seniority":"","work_auth":""}

# ---------- Core ----------
def enrich_tab(svc, sheet_id: str, tab: str, cv_text: str, min_fit: int, force: bool) -> int:
    headers, rows = read_sheet_tab(svc, sheet_id, tab)
    if not rows:
        return 0

    headers = ensure_headers(svc, sheet_id, tab, headers)
    # mapa nombre->índice 0-based
    idx = {name: headers.index(name) for name in headers}

    updated = []
    for r_i, row in enumerate(rows, start=2):  # desde fila 2
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))

        apply_url = row[idx.get("ApplyURL", 0)]
        role      = row[idx.get("Role", 0)]
        company   = row[idx.get("Company", 0)]
        if not (apply_url or role or company):
            continue

        if not force and row[idx.get("FitScore", 0)]:
            continue

        blob = {
            "Company": company,
            "Role": role,
            "Location": row[idx.get("Location", 0)],
            "ApplyURL": apply_url,
            "Notes": row[idx.get("Notes", 0)],
        }
        ans = llm_fit_score(cv_text, blob)

        row[idx["FitScore"]]      = str(ans["fit"])
        row[idx["Why"]]           = ans["why"]
        row[idx["RemoteScope"]]   = ans["remote_scope"]
        row[idx["RegionRestrict"]] = ans["region_restrict"]
        if ans["seniority"]:
            row[idx["Seniority"]] = ans["seniority"]
        if ans["work_auth"]:
            row[idx["WorkAuthReq"]] = ans["work_auth"]

        if ans["fit"] >= min_fit:
            row[idx["Status"]]     = row[idx["Status"]] or "To-Apply"
            row[idx["NextAction"]] = "Prepare-Apply"
            row[idx["SLA_Date"]]   = (dt.datetime.now() + relativedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
        else:
            if not row[idx["Status"]]:
                row[idx["Status"]] = "ParsedOK"

        note = row[idx["Notes"]]
        if " | LLM v2" not in note:
            row[idx["Notes"]] = (note + " | LLM v2").strip()

        updated.append((r_i, row))

    if updated:
        # bloque continuo desde la primera fila actualizada
        first_row = updated[0][0]
        values = [u[1] for u in updated]
        write_rows_block(svc, sheet_id, tab, first_row, values)

    print(f"[{tab}] enriquecidas/actualizadas: {len(updated)}")
    return len(updated)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=os.getenv("SHEET_ID",""), help="ID de la hoja (o pasa SHEET_ID por env)")
    ap.add_argument("--tabs", nargs="*", default=TABS_DEFAULT, help="Pestañas a procesar")
    ap.add_argument("--cv", default="cv.pdf", help="Ruta a tu CV (PDF/MD/TXT)")
    ap.add_argument("--min-fit", type=int, default=MIN_FIT_DEFAULT, help="Umbral FitScore para To-Apply")
    ap.add_argument("--force", action="store_true", help="Recalcular aunque ya exista FitScore")
    args = ap.parse_args()

    sheet_id = args.sheet or os.getenv("SHEET_ID","").strip()
    if not sheet_id:
        raise SystemExit("Falta --sheet o variable de entorno SHEET_ID")

    cv_text = load_cv_text(args.cv)
    if os.path.exists("cv_descriptor.txt"):
        with open("cv_descriptor.txt","r",encoding="utf-8") as fh:
            cv_text = fh.read() + "\n\n" + cv_text

    if not cv_text:
        print(f"[WARN] CV vacío o no encontrado: {args.cv}")

    svc = get_sheets_service()
    total = 0
    for tab in args.tabs:
        try:
            total += enrich_tab(svc, sheet_id, tab, cv_text, args.min_fit, args.force)
        except Exception as e:
            print(f"[{tab}] ERROR: {e}")
    print(f"TOTAL enriquecidas/actualizadas: {total}")

if __name__ == "__main__":
    main()
