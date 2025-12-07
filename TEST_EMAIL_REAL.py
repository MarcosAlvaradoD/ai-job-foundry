#!/usr/bin/env python3
"""
TEST CON EMAIL REAL DE GLASSDOOR
"""
import re
from datetime import datetime

# Leer HTML REAL
with open('GLASSDOOR_EMAIL_REAL.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("\n" + "="*70)
print("🧪 TEST CON EMAIL REAL DE GLASSDOOR")
print("="*70 + "\n")

print(f"📄 HTML cargado: {len(html_content)} caracteres\n")

jobs = []

try:
    # Extract job_listing_id from tracking URL (Pattern 4)
    job_id_pattern = r'jobAlertAlert&amp;utm_content=ja-jobpos\d+-(\d+)'
    job_ids = re.findall(job_id_pattern, html_content)
    
    # Extract job titles (font-weight:600, 14px)
    title_pattern = r'<p style="font-size:14px;line-height:1\.4;margin:0;font-weight:600">([^<]+)</p>'
    titles = re.findall(title_pattern, html_content)
    
    # Extract companies
    company_pattern = r'<p style="font-size:12px;line-height:1\.33;margin:0;font-weight:400;white-space:normal">([^<]+)</p>'
    companies = re.findall(company_pattern, html_content)
    
    # Extract locations
    location_pattern = r'<p style="font-size:12px;line-height:1\.33;margin:0;margin-top:4px">([^<$]+)</p>'
    locations = re.findall(location_pattern, html_content)
    
    # Extract salaries
    salary_pattern = r'<p style="font-size:12px;line-height:1\.33;margin:0;margin-top:4px">(\d+\s*k\$[^<]*)</p>'
    salaries = re.findall(salary_pattern, html_content)
    
    print(f"   🔍 Extracted:")
    print(f"      • {len(titles)} titles")
    print(f"      • {len(companies)} companies")
    print(f"      • {len(job_ids)} job IDs")
    print(f"      • {len(locations)} locations")
    print(f"      • {len(salaries)} salaries\n")
    
    # Build jobs
    for i, title in enumerate(titles):
        job_url = f"https://www.glassdoor.com/job-listing/JL_{job_ids[i]}.htm" if i < len(job_ids) else "Unknown"
        
        job = {
            'Source': 'Glassdoor',
            'ApplyURL': job_url,
            'Role': title.strip(),
            'Company': companies[i].strip() if i < len(companies) else 'Unknown',
            'Location': locations[i].strip() if i < len(locations) else 'Unknown',
            'Comp': salaries[i].strip() if i < len(salaries) else '',
            'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Status': 'New'
        }
        jobs.append(job)
    
    print(f"📊 RESULTADOS:")
    print(f"   Jobs extraídos: {len(jobs)}\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"📌 Job #{i}:")
        print(f"   Título: {job['Role']}")
        print(f"   Empresa: {job['Company']}")
        print(f"   Location: {job['Location']}")
        print(f"   Salario: {job['Comp'] if job['Comp'] else '(no especificado)'}")
        print(f"   URL: {job['ApplyURL']}")
        print()
    
except Exception as e:
    print(f"   ⚠️  Error: {e}")
    import traceback
    traceback.print_exc()

print("="*70 + "\n")

# Resultado esperado
if len(jobs) > 0:
    print(f"✅ ÉXITO: Parser extrajo {len(jobs)} jobs del email real!")
    print(f"\n💡 Ahora ejecuta: py control_center.py → opción 4")
else:
    print(f"⚠️ PROBLEMA: No se extrajeron jobs")
    print(f"\n🔍 Necesito analizar el HTML manualmente")
