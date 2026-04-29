#!/usr/bin/env python3
"""
Inserta vacantes encontradas manualmente en las hojas LinkedIn / Indeed
con fondo azul para identificarlas como "buscadas por Claude".

FILTRO US-ONLY: cualquier vacante con location = "United States" / estado USA
se marca automáticamente como "Skip - US Only" con fondo rojo en vez de azul.
Marcos no tiene work authorization para EE.UU. (solo visa turista).
"""
import os, sys, re
from datetime import datetime
sys.path.insert(0, r'C:\Users\MSI\Desktop\ai-job-foundry')
os.chdir(r'C:\Users\MSI\Desktop\ai-job-foundry')

from dotenv import load_dotenv
load_dotenv('.env')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES   = ['https://www.googleapis.com/auth/spreadsheets']
CREDS    = r'C:\Users\MSI\Desktop\ai-job-foundry\data\credentials\token.json'
SHEET_ID = os.getenv('GOOGLE_SHEETS_ID', '1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg')
TODAY    = datetime.now().strftime('%Y-%m-%d')

# ── Colores ────────────────────────────────────────────────────────────────
BLUE_BG = {"red": 0.678, "green": 0.847, "blue": 0.902}   # #ADD8E6 azul = Claude
RED_BG  = {"red": 1.0,   "green": 0.8,   "blue": 0.8}     # #FFCCCC rojo = US-Only

# ── Filtro US-Only ─────────────────────────────────────────────────────────
_US_PATTERNS = [
    r'\bUnited States\b', r'\bUSA\b', r'\bU\.S\.A\b',
    r'\bNew York\b', r'\bSan Francisco\b', r'\bLos Angeles\b',
    r'\bChicago\b', r'\bAustin\b', r'\bSeattle\b', r'\bBoston\b',
    r'\bAtlanta\b', r'\bDenver\b', r'\bDallas\b', r'\bMiami\b',
    r',\s*[A-Z]{2}\s*$',  # termina en ", CA" / ", NY" etc.
]
_SAFE_PATTERNS = [
    r'[Mm][eé]xico', r'LATAM', r'Latinoam', r'Guadalajara',
    r'Monterrey', r'CDMX', r'Latin America',
]

def _is_us_only(location: str) -> bool:
    loc = location.strip()
    if not loc:
        return False
    for pat in _SAFE_PATTERNS:
        if re.search(pat, loc, re.IGNORECASE):
            return False
    for pat in _US_PATTERNS:
        if re.search(pat, loc, re.IGNORECASE):
            return True
    return False

# ── Columnas: CreatedAt, Company, Role, Location, RemoteScope, ApplyURL,
#              Source, RecruiterEmail, Currency, Comp, Seniority, WorkAuthReq,
#              Status, Tienes, Faltan, NextAction, Notes, FitScore ──────────
def row(company, role, location, remote, url, source, currency='MXN', comp='', seniority='Sr', fit=7, notes=''):
    us_only  = _is_us_only(location)
    status   = 'Skip - US Only' if us_only else 'New'
    bg_color = RED_BG            if us_only else BLUE_BG
    notes_   = f'[!] US_WORK_AUTH_REQUIRED | {notes}' if us_only else notes
    if us_only:
        print(f'  [SKIP US-ONLY] {company} — {location}')
    return {
        'data': [TODAY, company, role, location, remote, url, source,
                 '', currency, comp, seniority, '', status, '', '', 'Revisar JD', notes_, fit],
        'bg': bg_color,
        'us_only': us_only,
    }

# ── VACANTES LINKEDIN ───────────────────────────────────────────────────────
LINKEDIN_JOBS = [
    row('HCLTech',               'Business Analysis & Application Support', 'México',                  'Remoto', 'https://www.linkedin.com/jobs/view/4390404145', 'LinkedIn', fit=7),
    row('BairesDev',             'Analista de Negocios',                    'Mexico City',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=BairesDev+Analista+Negocios', 'LinkedIn', fit=7),
    row('Crossing Hurdles',      'Business Analyst',                        'Latinoamérica',           'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Crossing+Hurdles+Business+Analyst', 'LinkedIn', fit=8, notes='Easy Apply · 6 días'),
    row('Excelia',               'Business Analyst',                        'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Excelia+Business+Analyst', 'LinkedIn', fit=8, notes='TCS alum · 5 días'),
    row('DaCodes',               'Business Process Analyst (Scrum/BPMN/UML)','Querétaro',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=DaCodes+Business+Process+Analyst', 'LinkedIn', comp='35K-40K', fit=8, notes='Early applicant · 3 días'),
    row('Commerce Social',       'Project Manager — TikTok Shop Agency',    'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Commerce+Social+Project+Manager', 'LinkedIn', fit=6),
    row('GK Software SE',        'Project Manager',                         'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=GK+Software+Project+Manager', 'LinkedIn', fit=7, notes='TCS alum'),
    row('Stand8 Technology',     'Technical Project Manager',               'Guadalajara, Jalisco',    'Remoto', 'https://www.linkedin.com/jobs/view/4392502231', 'LinkedIn', fit=8, notes='GDL · Easy Apply'),
    row('LTIMindtree',           'Project Manager (Cloud)',                  'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=LTIMindtree+Project+Manager+Cloud', 'LinkedIn', fit=7, notes='Easy Apply'),
    row('Somewhere',             'Project Manager (Remote)',                 'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Somewhere+Project+Manager', 'LinkedIn', fit=7, notes='TCS alum · Easy Apply'),
    row('Apply Digital',         'Engagement Manager - Technical',          'Mexico City',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Apply+Digital+Engagement+Manager', 'LinkedIn', fit=7, notes='TCS alum'),
    row('Sutherland',            'Manager - Product Delivery',              'Mexico City',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Sutherland+Manager+Product+Delivery', 'LinkedIn', fit=7, notes='UdG alum'),
    row('Littelfuse',            'Sr. Project Manager, Solutions',          'Piedras Negras, Coahuila','Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Littelfuse+Project+Manager', 'LinkedIn', fit=6, notes='Easy Apply'),
    row('Visit.org',             'Events Project Manager (Remote - Mexico)', 'Mexico City',            'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Visit.org+Events+Project+Manager', 'LinkedIn', fit=6, notes='Easy Apply · 3 días'),
    row('Getmore',               'Project Manager',                         'Mexico City',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Getmore+Project+Manager', 'LinkedIn', fit=6),
    row('Comptech Associates',   'Senior IT Payments Project Manager',      'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Comptech+Senior+IT+Payments+PM', 'LinkedIn', fit=7, notes='Easy Apply'),
    row('Comptech Associates',   'Global Transaction Project Manager',      'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Comptech+Global+Transaction+PM', 'LinkedIn', fit=7),
    row('Avahi',                 'Technical Project Manager',               'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Avahi+Technical+Project+Manager', 'LinkedIn', fit=7, notes='TCS alum'),
    row('Capgemini',             'FBS Associate Cloud Business Manager',    'México',                  'Remoto', 'https://www.linkedin.com/jobs/view/4388412062', 'LinkedIn', comp='MX$1/yr', fit=7, notes='Easy Apply · UdG alum'),
    row('Instructure',           'GTM Systems Manager',                     'Mexico City',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Instructure+GTM+Systems+Manager', 'LinkedIn', fit=7, notes='UdG alum'),
    row('Capgemini',             'FBS IT Change Management Specialist',     'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Capgemini+IT+Change+Management', 'LinkedIn', comp='MX$1/yr', fit=7, notes='Easy Apply · TCS alum'),
    row('HCLTech',               'SAP Release Manager',                     'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=HCLTech+SAP+Release+Manager', 'LinkedIn', fit=6, notes='Easy Apply'),
    row('Motivus',               'Service Manager (AMS)',                   'México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Motivus+Service+Manager+AMS', 'LinkedIn', fit=7),
    row('Sezzle',                'IT Vendor Management Program Manager',    'Mexico City',             'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Sezzle+IT+Vendor+Management', 'LinkedIn', fit=7, notes='Easy Apply'),
    row('Huzzle.com',            'Senior IT Infrastructure Project Manager','México',                  'Remoto', 'https://www.linkedin.com/jobs/search/?keywords=Huzzle+IT+Infrastructure+PM', 'LinkedIn', fit=8, notes='TCS alum · Easy Apply'),
]

# ── VACANTES INDEED (búsqueda nacional remoto) ──────────────────────────────
INDEED_JOBS = [
    # Indeed bloqueó el scraping — se añade placeholder para completar manualmente
    # row('empresa', 'puesto', 'ubicacion', 'Remoto', 'url', 'Indeed', fit=7),
]

_LI_JOB_RE = re.compile(r'/(?:comm/)?jobs/(?:view|comm/jobs/view)/(\d+)', re.IGNORECASE)

def _normalize_url_for_dedup(url: str) -> str:
    """Canonical URL key for deduplication. LinkedIn job IDs → /jobs/view/{id}"""
    if not url:
        return ''
    m = _LI_JOB_RE.search(url)
    if m and 'linkedin.com' in url.lower():
        return f'https://www.linkedin.com/jobs/view/{m.group(1)}'
    return url.strip().rstrip('/')

def _get_existing_job_keys(service, tab: str) -> set:
    """Load all ApplyURL values from a sheet tab, normalized for dedup."""
    try:
        res = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f'{tab}!A:Z').execute()
        vals = res.get('values', [])
        if not vals:
            return set()
        headers = vals[0]
        try:
            url_idx = headers.index('ApplyURL')
        except ValueError:
            return set()
        keys = set()
        for row in vals[1:]:
            if len(row) > url_idx and row[url_idx]:
                keys.add(_normalize_url_for_dedup(row[url_idx]))
        return keys
    except Exception:
        return set()

def get_last_row(service, tab):
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f'{tab}!A:A').execute()
    vals = result.get('values', [])
    return len(vals) + 1  # next empty row

def append_rows(service, tab, jobs):
    if not jobs:
        print(f'[INFO] {tab}: sin vacantes para insertar.')
        return 0

    # Dedup: check existing job IDs before inserting
    existing_keys = _get_existing_job_keys(service, tab)
    filtered = []
    for job_row in jobs:
        url = job_row['data'][5] if isinstance(job_row, dict) and 'data' in job_row else (job_row[5] if isinstance(job_row, list) and len(job_row) > 5 else '')
        key = _normalize_url_for_dedup(url)
        if key and key in existing_keys:
            company = job_row['data'][1] if isinstance(job_row, dict) and 'data' in job_row else (job_row[1] if isinstance(job_row, list) and len(job_row) > 1 else '?')
            print(f'  [SKIP DUPLICATE] {company} — ya existe en {tab}: {url[:70]}')
        else:
            filtered.append(job_row)
            if key:
                existing_keys.add(key)

    skipped = len(jobs) - len(filtered)
    if skipped:
        print(f'[INFO] {tab}: {skipped} vacantes omitidas (ya existen).')
    jobs = filtered

    if not jobs:
        print(f'[INFO] {tab}: sin vacantes nuevas para insertar.')
        return 0

    start_row = get_last_row(service, tab)
    end_row   = start_row + len(jobs) - 1

    # Escribir datos (jobs es lista de dicts con 'data' y 'bg')
    body = {'values': [j['data'] for j in jobs]}
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f'{tab}!A{start_row}',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    # Obtener sheet id numérico
    meta = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheet_gid = None
    for s in meta['sheets']:
        if s['properties']['title'] == tab:
            sheet_gid = s['properties']['sheetId']
            break

    # Aplicar color de fondo por fila (azul=nuevo, rojo=US-Only)
    bg_requests = []
    for i, job in enumerate(jobs):
        bg_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_gid,
                    "startRowIndex": start_row - 1 + i,
                    "endRowIndex": start_row + i,
                    "startColumnIndex": 0,
                    "endColumnIndex": 26
                },
                "cell": {"userEnteredFormat": {"backgroundColor": job.get('bg', BLUE_BG)}},
                "fields": "userEnteredFormat.backgroundColor"
            }
        })
    requests = bg_requests
    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": requests}
    ).execute()

    print(f'[OK] {tab}: {len(jobs)} vacantes insertadas en filas {start_row}-{end_row} con fondo azul.')
    return len(jobs)

def main():
    creds   = Credentials.from_authorized_user_file(CREDS, SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    total = 0
    total += append_rows(service, 'LinkedIn', LINKEDIN_JOBS)
    total += append_rows(service, 'Indeed',   INDEED_JOBS)

    print(f'\n[DONE] Total: {total} vacantes agregadas al Sheet con fondo azul (#ADD8E6).')
    print(f'[INFO] Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}')

if __name__ == '__main__':
    main()
