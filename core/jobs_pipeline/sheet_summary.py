
# -*- coding: utf-8 -*-
"""
sheet_summary.py
Crea/actualiza la pestaña 'Summary' con:
- Estadísticas de compensación (por Currency): Min, Max, Average, Count
- Promedio de FitScore por Source (y Count)
- Hasta 3 sugerencias "PRO" leídas de cv_descriptor.txt

Requisitos:
  pip install google-api-python-client google-auth-oauthlib
Archivos:
  - credentials.json / token.json (OAuth)
Uso:
  set SHEET_ID=<id>
  py sheet_summary.py
  py sheet_summary.py --sheet <id> --tabs LinkedIn Indeed Glassdoor
"""

import os
import re
import argparse
import datetime as dt
from collections import defaultdict

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# -------------------- util A1 --------------------
def a1_col(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


# -------------------- Sheets helpers --------------------
def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print("[ok] token.json generado.")
    return build("sheets", "v4", credentials=creds)


def ensure_tab_exists(service, sheet_id: str, tab_name: str):
    try:
        service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{tab_name}!A1:A1"
        ).execute()
    except HttpError as e:
        # Si la hoja no existe, la creamos
        if e.resp.status in (400, 404):
            body = {"requests": [{"addSheet": {"properties": {"title": tab_name}}}]}
            service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        else:
            raise


def fetch_headers(service, sheet_id: str, tab: str):
    resp = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{tab}!1:1"
    ).execute()
    vals = resp.get("values", [])
    if not vals:
        return []
    return [c if c is not None else "" for c in vals[0]]


def col_index_by_name(headers, wanted, aliases=None):
    if aliases is None:
        aliases = []
    lowered = [h.strip().lower() for h in headers]
    for name in [wanted] + aliases:
        n = name.lower()
        if n in lowered:
            return lowered.index(n)
    return -1


def read_rows(service, sheet_id: str, tab: str):
    resp = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{tab}!A2:Z2000"
    ).execute()
    return resp.get("values", [])


def write_block(service, sheet_id: str, tab: str, values):
    # Limpia y escribe en bloque desde A1 el contenido de 'values'
    end_col = a1_col(max(len(r) for r in values) if values else 1)
    end_row = len(values)
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{tab}!A1:{end_col}{end_row}",
        valueInputOption="RAW",
        body={"values": values}
    ).execute()


# -------------------- Parsing / Aggregation --------------------
_range_sep = re.compile(r"\s*(?:-|[\u2013\u2014]|to|a)\s*", re.IGNORECASE)
_num = re.compile(r"(\d+(?:[.,]\d+)*)")

def parse_comp_to_numbers(text):
    """
    Devuelve (low, high) numéricos si encuentra números; si no, None.
    Acepta "120000 - 140000", "120000–140000", "140000", etc.
    Cambia comas por puntos y elimina separadores de miles.
    """
    if not text:
        return None
    s = str(text)
    nums = [n.replace(".", "").replace(",", "") for n in _num.findall(s)]
    nums = [n for n in nums if n.isdigit()]
    if not nums:
        return None
    if len(nums) == 1:
        val = float(nums[0]); return (val, val)
    try:
        low = float(nums[0]); high = float(nums[1])
        if low > high: low, high = high, low
        return (low, high)
    except:
        return None


def read_pro_suggestions(path="cv_descriptor.txt", max_items=3):
    if not os.path.exists(path):
        return []
    lines = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f.readlines()]
    cands = []
    for ln in reversed(lines):
        if not ln:
            continue
        if ln.lower().startswith("sug:") or ln.lower().startswith("sugerencia"):
            cands.append(ln)
        elif ln.startswith("- "):
            cands.append(ln)
        if len(cands) >= max_items:
            break
    return list(reversed(cands))


# -------------------- Main --------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=os.getenv("SHEET_ID", ""), help="Sheet ID")
    ap.add_argument("--tabs", nargs="+", default=["LinkedIn", "Indeed", "Glassdoor"], help="Pestañas origen")
    args = ap.parse_args()

    sheet_id = args.sheet.strip()
    if not sheet_id:
        raise SystemExit("Falta --sheet o SHEET_ID")

    service = get_service()
    summary_tab = "Summary"
    ensure_tab_exists(service, sheet_id, summary_tab)

    # Acumuladores
    comp_by_currency = defaultdict(list)  # currency -> list[(low, high)]
    fit_sum_by_source = defaultdict(float)
    fit_count_by_source = defaultdict(int)

    for tab in args.tabs:
        try:
            headers = fetch_headers(service, sheet_id, tab)
            if not headers:
                continue

            idx_comp = col_index_by_name(headers, "Comp")
            idx_curr = col_index_by_name(headers, "Currency")
            idx_fit  = col_index_by_name(headers, "FitScore", aliases=["Fit"])
            idx_src  = col_index_by_name(headers, "Source")

            rows = read_rows(service, sheet_id, tab)
            if not rows:
                continue

            for row in rows:
                if len(row) < len(headers):
                    row = row + [""] * (len(headers) - len(row))

                comp_txt = row[idx_comp] if idx_comp != -1 and idx_comp < len(row) else ""
                currency = (row[idx_curr] if idx_curr != -1 and idx_curr < len(row) else "").strip() or "Unknown"

                rng = parse_comp_to_numbers(comp_txt)
                if rng is not None:
                    comp_by_currency[currency].append(rng)

                if idx_fit != -1 and idx_fit < len(row):
                    try:
                        fit_val = float(str(row[idx_fit]).strip())
                    except:
                        fit_val = None
                    if fit_val is not None:
                        src = (row[idx_src] if idx_src != -1 and idx_src < len(row) else "").strip() or "Unknown"
                        fit_sum_by_source[src] += fit_val
                        fit_count_by_source[src] += 1

        except Exception as e:
            print(f"[{tab}] WARN: {e}")

    out = []
    out.append([f"Summary ({dt.datetime.now().isoformat(timespec='seconds')})"])
    out.append([])

    out.append(["Compensation Stats (by Currency)"])
    out.append(["Currency", "Min", "Max", "Average", "Count"])
    for currency, pairs in sorted(comp_by_currency.items()):
        if not pairs:
            continue
        lows  = [p[0] for p in pairs]
        highs = [p[1] for p in pairs]
        mins  = min(lows + highs)
        maxs  = max(lows + highs)
        avgs  = sum((l+h)/2.0 for (l,h) in pairs) / len(pairs)
        out.append([currency, mins, maxs, round(avgs, 2), len(pairs)])
    if len(out) == 4:
        out.append(["(no numeric comp found)"])
    out.append([])

    out.append(["Average Fit by Source"])
    out.append(["Source", "AvgFit", "Count"])
    sources = sorted(set(list(fit_sum_by_source.keys()) + list(fit_count_by_source.keys())))
    if sources:
        for s in sources:
            cnt = fit_count_by_source.get(s, 0)
            avg = round(fit_sum_by_source.get(s, 0.0) / cnt, 2) if cnt else ""
            out.append([s, avg, cnt])
    else:
        out.append(["(no fit found)", "", ""])
    out.append([])

    out.append(["PRO Suggestions"])
    sugs = read_pro_suggestions("cv_descriptor.txt", max_items=3)
    if sugs:
        for s in sugs:
            if not s.startswith("- "):
                s = f"- {s}"
            out.append([s])
    else:
        out.append(["(No suggestions found)"])

    write_block(service, sheet_id, summary_tab, out)
    print("[ok] Summary actualizado.")

if __name__ == "__main__":
    main()
