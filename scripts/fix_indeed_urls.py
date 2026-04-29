#!/usr/bin/env python3
"""
Scrapea Indeed, extrae URLs reales y actualiza la pestaña Indeed del Sheet.
"""
import os, sys, re, time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.insert(0, r'C:\Users\MSI\Desktop\ai-job-foundry')
os.chdir(r'C:\Users\MSI\Desktop\ai-job-foundry')
from dotenv import load_dotenv
load_dotenv('.env')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES   = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
TODAY    = datetime.now().strftime('%Y-%m-%d')
BLUE_BG  = {'red': 0.678, 'green': 0.847, 'blue': 0.902}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-MX,es;q=0.9',
}

SEARCHES = [
    ('https://mx.indeed.com/q-dynamics-365-finance-operations-empleos.html',
     ['D365 F&O Supply Chain Analyst','Functional Consultant - D365 Finance',
      'Consultor Especialista en Dynamics 365 Finance','ERP Consultant',
      'ERP Fuctional Business Analyst','Líder Dynamics 365',
      'Business Systems Manager','Consultor funcional SCM']),
    ('https://mx.indeed.com/q-project-manager-remoto-empleos.html',
     ['Remote Project Manager','Project manager (IT Business Analyst)',
      'Technical Project Manager (Development)','Technical Project Manager - SaaS',
      'Project Manager','Proyect Manager']),
]

def scrape_jobs(url):
    """Scrapea una página de Indeed y devuelve lista de dicts con title/company/location/url."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.content, 'html.parser')
        jobs = []
        for card in soup.select('td.resultContent'):
            title_el   = card.select_one('h2 span[id], h2 a span')
            company_el = card.select_one('[data-testid="company-name"]')
            location_el= card.select_one('[data-testid="text-location"]')
            salary_el  = card.select_one('.salary-snippet-container')
            # Buscar jk en el contenedor padre
            parent = card.find_parent(class_=re.compile(r'job_seen_beacon|slider_item'))
            parent = parent or card.find_parent('tr')
            jk = None
            if parent:
                # Buscar en atributo data-jk o en href
                a = parent.select_one('h2 a[data-jk], a[data-jk]')
                if a:
                    jk = a.get('data-jk')
                if not jk:
                    # Buscar en cualquier href que tenga jk=
                    for a in parent.find_all('a', href=True):
                        m = re.search(r'jk=([a-z0-9]+)', a['href'])
                        if m:
                            jk = m.group(1)
                            break
            job_url = f'https://mx.indeed.com/viewjob?jk={jk}' if jk else ''
            title   = title_el.get_text(strip=True) if title_el else ''
            company = company_el.get_text(strip=True) if company_el else ''
            location= location_el.get_text(strip=True) if location_el else 'México'
            salary  = salary_el.get_text(' ', strip=True) if salary_el else ''
            if title:
                jobs.append({'title': title, 'company': company,
                             'location': location, 'salary': salary,
                             'url': job_url})
        print(f'  [INFO] {url.split("/")[-1][:40]} -> {len(jobs)} vacantes encontradas')
        return jobs
    except Exception as e:
        print(f'  [ERROR] {e}')
        return []

def row(company, role, location, remote, comp, fit, url, notes=''):
    return [TODAY, company, role, location, remote, url, 'Indeed', '',
            'MXN', comp, 'Sr', '', 'New', '', '', 'Revisar JD', notes, fit]

def main():
    creds   = Credentials.from_authorized_user_file('data/credentials/token.json', SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Limpiar filas anteriores de Indeed (las que puse con URL vacía: filas 6-19)
    # Primero leer para confirmar cuáles son las mías (Source=Indeed, URL=https://mx.indeed.com)
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range='Indeed!A1:R100').execute()
    existing = result.get('values', [])

    # Encontrar filas a reemplazar (source=Indeed y url exactamente 'https://mx.indeed.com')
    rows_to_clear = []
    for i, row_data in enumerate(existing[1:], start=2):  # skip header
        if len(row_data) > 6 and row_data[6] == 'Indeed' and row_data[5] in ('https://mx.indeed.com', ''):
            rows_to_clear.append(i)

    print(f'[INFO] Filas a limpiar/reemplazar: {rows_to_clear}')

    # Scrape Indeed
    all_scraped = {}
    for search_url, _ in SEARCHES:
        scraped = scrape_jobs(search_url)
        for j in scraped:
            key = j['title'][:40].lower().strip()
            all_scraped[key] = j
        time.sleep(1)

    print(f'[INFO] Total vacantes scrapeadas: {len(all_scraped)}')
    for k, v in all_scraped.items():
        print(f'  {v["company"]:25s} | {v["title"][:45]:45s} | {v["url"]}')

    # Construir nuevas filas con URLs reales
    # Mapa: nombre parcial → configuración fija de la row
    JOB_CONFIG = [
        ('D365 F&O Supply Chain',       'Xideral',              'Loma Bonita, Méx.',    'Hibrido',  '50K-70K/mes', 8, ''),
        ('Functional Consultant - D365','Unify Dots',           'Ciudad de México',     'Hibrido',  '',             8, 'D365 Finance'),
        ('Consultor Especialista en Dyn','Opti',                'Naucalpan, Méx.',      'Hibrido',  '',             8, ''),
        ('ERP Consultant',              'Calsoft Systems',      'Desde casa',           'Remoto',   '',             9, 'Remoto · ERP PM'),
        ('ERP',                         'CIMMYT',               'Texcoco, Méx.',        'Hibrido',  '',             8, 'Internacional'),
        ('Líder Dynamics 365',          'Global Executive',     'Ciudad de México',     'Hibrido',  '',             8, 'Liderazgo D365'),
        ('Business Systems',            'CIMMYT',               'Texcoco, Méx.',        'Hibrido',  '',             7, 'Int. Recruited'),
        ('Consultor funcional SCM',     'Nexer',                'Ciudad de México',     'Hibrido',  '',             8, 'SCM/D365'),
        ('Remote Project Manager',      'FARO Integral Solutions','Desde casa',         'Remoto',   '11K-40K/mes', 8, 'Profit Sharing · 100% remoto'),
        ('Project manager (IT',         'SOL SER SISTEM',       'Querétaro, Qro.',      'Hibrido',  '',             7, ''),
        ('Technical Project Manager (D','Dresden Partners',     'México',               'Remoto',   '',             7, 'SaaS/Dev'),
        ('Technical Project Manager - S','Dresden Partners',    'Aguascalientes',       'Hibrido',  '',             7, ''),
        ('Project Manager',             'VLK Talent Solutions', 'Roma Norte, CDMX',     'Hibrido',  '30K-35K/mes', 7, ''),
        ('Project Manager',             'KTK General Contractor','Zapopan, Jal.',       'Presencial','35K-40K/mes', 5, 'Presencial GDL'),
    ]

    new_rows = []
    for (title_key, company, location, remote, comp, fit, notes) in JOB_CONFIG:
        # Buscar URL en scraped por título parcial
        url = ''
        for scraped_key, scraped_job in all_scraped.items():
            if title_key.lower() in scraped_key or scraped_key in title_key.lower():
                url = scraped_job['url']
                break
            # También comparar por empresa
            if company.lower() in scraped_job['company'].lower() and scraped_job['url']:
                url = scraped_job['url']
                break
        new_rows.append(row(company, title_key, location, remote, comp, fit, url, notes))

    # Limpiar filas viejas y escribir las nuevas
    if rows_to_clear:
        first_row = min(rows_to_clear)
        # Limpiar rango
        service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=f'Indeed!A{first_row}:Z{first_row + len(rows_to_clear)}'
        ).execute()
        # Escribir nuevas
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f'Indeed!A{first_row}',
            valueInputOption='USER_ENTERED',
            body={'values': new_rows}
        ).execute()
        end_row = first_row + len(new_rows) - 1

        # Re-aplicar color azul
        meta  = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        gid   = next(s['properties']['sheetId'] for s in meta['sheets']
                     if s['properties']['title'] == 'Indeed')
        service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={'requests': [{
            'repeatCell': {
                'range': {'sheetId': gid, 'startRowIndex': first_row-1,
                          'endRowIndex': end_row, 'startColumnIndex': 0, 'endColumnIndex': 26},
                'cell': {'userEnteredFormat': {'backgroundColor': BLUE_BG}},
                'fields': 'userEnteredFormat.backgroundColor'
            }
        }]}).execute()
        print(f'\n[OK] Indeed: {len(new_rows)} filas actualizadas con URLs reales (filas {first_row}-{end_row}).')
    else:
        print('[WARN] No se encontraron filas para reemplazar.')

if __name__ == '__main__':
    main()
