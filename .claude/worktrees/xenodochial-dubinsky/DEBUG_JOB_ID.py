#!/usr/bin/env python3
"""
DEBUG JOB LISTING ID
Encuentra el job_listing_id en el HTML
"""
import re

# Leer HTML
with open('GLASSDOOR_EMAIL_SAMPLE.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("\n" + "="*70)
print("🔍 BUSCANDO JOB_LISTING_ID")
print("="*70 + "\n")

# Intentar múltiples patrones
patterns = [
    (r'"job_listing_id":"(\d+)"', 'Pattern 1: JSON con comillas dobles'),
    (r"'job_listing_id':'(\d+)'", 'Pattern 2: JSON con comillas simples'),
    (r'job_listing_id["\']?:\s*["\']?(\d+)', 'Pattern 3: Flexible'),
    (r'jobAlertAlert&amp;utm_content=ja-jobpos\d+-(\d+)', 'Pattern 4: De URL tracking'),
    (r'JL_(\d+)\.htm', 'Pattern 5: De link directo'),
]

for pattern, desc in patterns:
    matches = re.findall(pattern, html)
    print(f"✓ {desc}")
    print(f"  Matches: {len(matches)}")
    if matches:
        print(f"  IDs: {matches[:5]}")  # Primeros 5
    print()

# Buscar "job_listing_id" literalmente
print("📝 Buscando texto literal 'job_listing_id':")
if 'job_listing_id' in html:
    idx = html.find('job_listing_id')
    snippet = html[idx-50:idx+100]
    print(f"  Encontrado en posición {idx}")
    print(f"  Snippet: ...{snippet}...")
else:
    print("  ❌ NO encontrado")

print("\n" + "="*70 + "\n")
