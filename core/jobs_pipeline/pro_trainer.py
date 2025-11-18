# pro_trainer.py
"""
Aprende del mercado observado y mantiene memoria en ./model_memory/profile.json.
- Lee pestañas Registry/LinkedIn/Indeed/Glassdoor
- Calcula skills/keywords frecuentes con alto Fit
- Actualiza cv_descriptor.txt con una sección de recomendaciones (no sobreescribe, añade al final)
"""

import os
import re
import json
from collections import Counter, defaultdict
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = os.getenv("SHEET_ID")
CV_FILE = os.getenv("CV_FILE", "cv_descriptor.txt")
MEM_DIR = "model_memory"
MEM_FILE = os.path.join(MEM_DIR, "profile.json")

TABS = ["Registry", "LinkedIn", "Indeed", "Glassdoor"]

def get_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPE)
    return build("sheets", "v4", credentials=creds)

def read_tab_values(svc, tab):
    r = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f"{tab}!A1:ZZ5000"
    ).execute()
    values = r.get("values", [])
    if not values:
        return [], []
    return values[0], values[1:]

def header_index(headers, names):
    low = [h.strip().lower() for h in headers]
    for n in names:
        if n.lower() in low:
            return low.index(n.lower())
    return None

def load_memory():
    if not os.path.isdir(MEM_DIR):
        os.makedirs(MEM_DIR, exist_ok=True)
    if os.path.isfile(MEM_FILE):
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"skill_weights": {}, "salary": {"min": None, "max": None, "avg": None}, "history": []}

def save_memory(mem):
    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def parse_comp_to_number(raw):
    if not raw or raw.strip().lower() in {"unknown", "competitive", "n/a", "na"}:
        return None
    txt = re.sub(r"[^\d\-\.\s]", "", raw)
    nums = re.findall(r"\d+(?:\.\d+)?", txt)
    if not nums:
        return None
    vals = [float(n) for n in nums]
    return sum(vals)/len(vals)

def main():
    if not SHEET_ID:
        raise SystemExit("Falta SHEET_ID")

    svc = get_service()
    mem = load_memory()

    all_rows = []
    bag_highfit = []
    comps = []
    fits = []

    for tab in TABS:
        headers, rows = read_tab_values(svc, tab)
        if not headers:
            continue

        idx_comp = header_index(headers, ["Comp", "Salary", "Compensation"])
        idx_fit  = header_index(headers, ["FitScore", "Fit"])
        idx_role = header_index(headers, ["Role", "Title"])
        idx_notes = header_index(headers, ["Notes", "Why"])

        for r in rows:
            comp = r[idx_comp] if idx_comp is not None and idx_comp < len(r) else ""
            fit  = r[idx_fit] if idx_fit is not None and idx_fit < len(r) else ""
            role = r[idx_role] if idx_role is not None and idx_role < len(r) else ""
            notes= r[idx_notes] if idx_notes is not None and idx_notes < len(r) else ""

            comp_num = parse_comp_to_number(comp)
            try:
                fit_num = float(str(fit)) if str(fit).strip() else None
            except:
                fit_num = None

            all_rows.append((tab, comp_num, fit_num, role, notes))
            if comp_num is not None:
                comps.append(comp_num)
            if fit_num is not None:
                fits.append(fit_num)

            if fit_num is not None and fit_num >= 80:  # “alto fit”
                text = f"{role} {notes}".lower()
                toks = re.findall(r"[a-zA-Z0-9\+\#\.]+", text)
                bag_highfit.extend(w for w in toks if len(w) > 2)

    # Recompute salary stats
    mem["salary"]["min"] = round(min(comps), 2) if comps else None
    mem["salary"]["max"] = round(max(comps), 2) if comps else None
    mem["salary"]["avg"] = round(sum(comps)/len(comps), 2) if comps else None
    avg_fit = round(sum(fits)/len(fits), 2) if fits else None

    # Update skill weights (frecuencia acumulada)
    freq = Counter(bag_highfit)
    for k, c in freq.items():
        mem["skill_weights"][k] = mem["skill_weights"].get(k, 0) + c

    mem["history"].append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "offers_seen": len(all_rows),
        "avg_fit": avg_fit,
        "salary": mem["salary"]
    })

    save_memory(mem)

    # Escribe recomendaciones al CV
    top_now = [k for k, _ in Counter(bag_highfit).most_common(10)]
    with open(CV_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n# AUTO-LEARNING (pro_trainer)\n")
        f.write(f"- Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if mem["salary"]["avg"] is not None:
            f.write(f"- Mercado observado (prom. comp.): {mem['salary']['avg']}\n")
        if avg_fit is not None:
            f.write(f"- Fit promedio observado: {avg_fit}\n")
        if top_now:
            f.write(f"- Keywords de alto fit más recientes: {', '.join(top_now)}\n")

    print("✅ PRO actualizado: memoria y sugerencias agregadas a", CV_FILE)

if __name__ == "__main__":
    main()
