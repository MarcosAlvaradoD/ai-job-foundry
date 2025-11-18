# -*- coding: utf-8 -*-
"""
enrich_sheet_with_llm_v3.py
- Lee pestañas indicadas en un Google Sheet
- Calcula FitScore (0..100) y la razón (Why) con tu LLM local
- Escribe SOLO en las columnas correctas, detectándolas/creándolas dinámicamente
Requisitos:
  pip install google-api-python-client google-auth-oauthlib requests
Archivos esperados:
  - credentials.json (OAuth) y token.json (se genera al autorizar)
Env vars (recomendado):
  - SHEET_ID=<id>
  - LLM_URL=http://127.0.0.1:11434/v1/chat/completions
  - LLM_MODEL=qwen2.5-14b-instruct
Ejemplo:
  py enrich_sheet_with_llm_v3.py --sheet %env:SHEET_ID% --tabs Glassdoor --cv ".\cv_descriptor.txt" --min-fit 0 --force
"""

import os
import json
import time
import argparse
import requests
from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
LLM_URL   = os.getenv("LLM_URL",   "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")

# -------------------- util A1 --------------------
def a1_col(n: int) -> str:
    """1->A, 2->B, ..., 26->Z, 27->AA, ..."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def col_index_by_name(headers: List[str], wanted: str, aliases: List[str] = None) -> int:
    """Devuelve índice 0-based si existe, o -1. Coincidencia por nombre (case-insensitive)."""
    if aliases is None:
        aliases = []
    lowered = [h.strip().lower() for h in headers]
    for name in [wanted] + aliases:
        name = name.lower()
        if name in lowered:
            return lowered.index(name)
    return -1

# -------------------- Google Sheets --------------------
def get_service() -> Any:
    creds = None
    if os.path.exists("../data/credentials/token.json"):
        creds = Credentials.from_authorized_user_file("../data/credentials/token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        # Nota: abrirá una URL para autorizar y guardará token.json
        creds = flow.run_local_server(port=0)
        with open("../data/credentials/token.json","w",encoding="utf-8") as f:
            f.write(creds.to_json())
        print("🔑 token.json generado.")
    return build("sheets", "v4", credentials=creds)

def fetch_headers(service, sheet_id: str, tab: str) -> List[str]:
    resp = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{tab}!1:1"
    ).execute()
    values = resp.get("values", [])
    if not values:
        return []
    return [c if c is not None else "" for c in values[0]]

def ensure_columns(service, sheet_id: str, tab: str, headers: List[str], needed: List[str]) -> List[str]:
    """
    Asegura que los encabezados de 'needed' existan.
    Si faltan, los agrega al final de la fila 1.
    Retorna la nueva lista de headers.
    """
    missing = [n for n in needed if col_index_by_name(headers, n) == -1]
    if not missing:
        return headers

    new_headers = headers[:]  # copia
    new_headers.extend(missing)
    end_col = a1_col(len(new_headers))
    body = {"values": [new_headers]}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{tab}!A1:{end_col}1",
        valueInputOption="RAW",
        body=body
    ).execute()
    return new_headers

def read_rows(service, sheet_id: str, tab: str) -> List[List[str]]:
    resp = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{tab}!A2:Z1000"  # suficiente, luego se recorta por último dato no vacío
    ).execute()
    return resp.get("values", [])

def write_column(service, sheet_id: str, tab: str, col_idx: int, values: List[Any], start_row: int = 2) -> None:
    """
    Escribe una sola columna (col_idx 0-based) desde start_row.
    'values' es una lista con uno por fila (se envuelven como listas para Sheets).
    """
    end_row = start_row + len(values) - 1
    col_a1 = a1_col(col_idx + 1)
    rng = f"{tab}!{col_a1}{start_row}:{col_a1}{end_row}"
    body = {"values": [[v] for v in values]}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=rng,
        valueInputOption="RAW",
        body=body
    ).execute()

# -------------------- LLM --------------------
def call_llm_fit(cv_text: str, role: str, description: str) -> Dict[str, Any]:
    """
    Llama al LLM local y devuelve dict {'fit': int, 'why': str}.
    Debe manejar 400 del runtime devolviendo LLM_ERROR.
    """
    prompt = (
        "Eres un evaluador de compatibilidad de vacantes y CV.\n"
        "Devuelve SOLO JSON con esta forma:\n"
        '{ "fit": <0-100>, "why": "<explicación corta>" }\n\n'
        f"CV (resumen):\n{cv_text}\n\n"
        f"Role: {role}\n"
        f"Descripción/Notas: {description}\n"
    )

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Devuelve únicamente JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "stream": False
    }

    try:
        r = requests.post(LLM_URL, json=payload, timeout=30)
        r.raise_for_status()
    except requests.HTTPError as e:
        # Si el runtime devuelve 400, devolvemos error manejable
        return {"fit": 0, "why": f"LLM_ERROR ({str(e)})"}
    except Exception as e:
        return {"fit": 0, "why": f"LLM_ERROR ({str(e)})"}

    try:
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        out = json.loads(text)
        fit = int(out.get("fit", 0))
        why = str(out.get("why", ""))
        fit = max(0, min(100, fit))
        return {"fit": fit, "why": why}
    except Exception as e:
        return {"fit": 0, "why": f"LLM_ERROR (parse): {e}"}

# -------------------- Main --------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=False, default=os.getenv("SHEET_ID",""),
                    help="ID de Google Sheet (o variable de entorno SHEET_ID)")
    ap.add_argument("--tabs", nargs="+", default=["Glassdoor","LinkedIn","Indeed"],
                    help="Lista de pestañas a procesar")
    ap.add_argument("--cv", required=True, help="Ruta a cv_descriptor.txt (o similar)")
    ap.add_argument("--min-fit", type=int, default=0, help="Umbral mínimo para considerar (0-100)")
    ap.add_argument("--force", action="store_true", help="Forzar recalcular aunque ya exista FitScore")
    args = ap.parse_args()

    sheet_id = args.sheet.strip()
    if not sheet_id:
        raise SystemExit("Falta --sheet o SHEET_ID")

    if not os.path.exists(args.cv):
        raise SystemExit(f"No existe el archivo CV: {args.cv}")

    with open(args.cv, "r", encoding="utf-8") as f:
        cv_text = f.read().strip()

    print(f"[LLM] URL: {LLM_URL} | MODEL: {LLM_MODEL}")

    service = get_service()
    total_updates = 0

    for tab in args.tabs:
        try:
            headers = fetch_headers(service, sheet_id, tab)
            if not headers:
                # crea cabeceras mínimas si no hay nada
                headers = ["Role","Location","RemoteScope","ApplyURL","Source","RecruiterEmail",
                           "Currency","Comp","Seniority","WorkAuthReq","Status","NextAction",
                           "SLA_Date","ContactName","ContactEmail","ThreadId","LastEmailAt",
                           "LastEmailSnippet"]
                end_col = a1_col(len(headers))
                service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range=f"{tab}!A1:{end_col}1",
                    valueInputOption="RAW",
                    body={"values":[headers]}
                ).execute()

            # Asegura columnas donde escribiremos
            headers = ensure_columns(service, sheet_id, tab, headers, needed=["FitScore","Why"])

            # Ubicaciones de columnas clave
            col_apply = col_index_by_name(headers, "ApplyURL", aliases=["Apply Url","Apply","URL"])
            col_role  = col_index_by_name(headers, "Role", aliases=["Title","Position"])
            col_notes = col_index_by_name(headers, "Notes")
            col_fit   = col_index_by_name(headers, "FitScore", aliases=["Fit"])
            col_why   = col_index_by_name(headers, "Why")

            rows = read_rows(service, sheet_id, tab)
            if not rows:
                continue

            # Leemos columnas existentes FitScore/Why para no sobreescribir si no --force
            existing_fit = []
            existing_why = []
            # fetch columnas para el tamaño exacto
            row_count = len(rows)
            if col_fit != -1:
                rng = f"{tab}!{a1_col(col_fit+1)}2:{a1_col(col_fit+1)}{row_count+1}"
                resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=rng).execute()
                existing_fit = [r[0] if r else "" for r in resp.get("values", [[]]*row_count)]
                if len(existing_fit)<row_count:
                    existing_fit += [""]*(row_count-len(existing_fit))
            else:
                existing_fit = [""]*row_count

            if col_why != -1:
                rng = f"{tab}!{a1_col(col_why+1)}2:{a1_col(col_why+1)}{row_count+1}"
                resp = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=rng).execute()
                existing_why = [r[0] if r else "" for r in resp.get("values", [[]]*row_count)]
                if len(existing_why)<row_count:
                    existing_why += [""]*(row_count-len(existing_why))
            else:
                existing_why = [""]*row_count

            out_fit = []
            out_why = []
            processed = 0

            for i, row in enumerate(rows, start=2):  # fila real en Sheet
                # normalizamos largo de fila
                if len(row) < len(headers):
                    row = row + [""]*(len(headers)-len(row))

                apply_url = row[col_apply] if 0 <= col_apply < len(row) else ""
                role      = row[col_role]  if 0 <= col_role  < len(row) else ""
                notes     = row[col_notes] if 0 <= col_notes < len(row) else ""

                # si no hay URL, saltamos (fila vacía)
                if not str(apply_url).strip():
                    out_fit.append("")
                    out_why.append("")
                    continue

                already_fit = str(existing_fit[i-2]).strip()
                if already_fit and not args.force:
                    # respetamos valores existentes
                    out_fit.append(already_fit)
                    out_why.append(existing_why[i-2] if i-2 < len(existing_why) else "")
                    continue

                res = call_llm_fit(cv_text=cv_text, role=role, description=notes)
                fit = res.get("fit", 0)
                why = res.get("why", "")
                # umbral
                if fit < args.min_fit:
                    # igual escribimos, pero lo verás < umbral
                    pass

                out_fit.append(fit)
                out_why.append(why)
                processed += 1
                # para no bombardear al runtime local
                time.sleep(0.2)

            # Escritura por columnas
            write_column(service, sheet_id, tab, col_fit, out_fit, start_row=2)
            write_column(service, sheet_id, tab, col_why, out_why, start_row=2)
            total_updates += processed
            print(f"[{tab}] filas actualizadas: {processed}")

        except HttpError as e:
            print(f"[{tab}] ERROR Sheets: {e}")
        except Exception as e:
            print(f"[{tab}] ERROR: {e}")

    print(f"TOTAL enriquecidas/actualizadas: {total_updates}")

if __name__ == "__main__":
    main()
