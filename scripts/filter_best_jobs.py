#!/usr/bin/env python3
"""
FILTRO: Extrae SOLO las mejores vacantes de RH-IT Home
De 64 vacantes FIT 7+, extrae solo FIT 9-10 (las mejores)
"""
import re

# Leer archivo completo
input_file = "boards/rh_it_home.txt"
output_file = "boards/rh_it_home_MEJORES.txt"

print("="*70)
print("📊 FILTRO DE MEJORES VACANTES")
print("="*70)

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extraer bloques individuales
jobs = content.split('-'*70)[1:]  # Skip header

# Filtrar solo FIT 9-10
best_jobs = []
for job in jobs:
    if not job.strip():
        continue
    
    # Buscar FIT score
    fit_match = re.search(r'FIT: (\d+)/10', job)
    if fit_match:
        fit_score = int(fit_match.group(1))
        if fit_score >= 9:
            best_jobs.append(job)

print(f"\n📈 Encontradas {len(best_jobs)} vacantes con FIT 9-10")

# Escribir archivo filtrado
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write("AI JOB FOUNDRY - MEJORES VACANTES (FIT 9-10)\n")
    f.write(f"Total: {len(best_jobs)} vacantes\n")
    f.write("="*70 + "\n\n")
    
    for i, job in enumerate(best_jobs, 1):
        f.write(f"[{i}]" + job)
        if i < len(best_jobs):
            f.write('-'*70 + "\n\n")

print(f"💾 Guardado en: {output_file}")
print("\n" + "="*70)
print("🎯 RECOMENDACIÓN:")
print("   Aplica SOLO a estas vacantes FIT 9-10")
print("   Son las que mejor match con tu perfil")
print("="*70)

# Mostrar títulos
print("\n📋 VACANTES SELECCIONADAS:\n")
for i, job in enumerate(best_jobs, 1):
    # Extraer título
    title_match = re.search(r'\| (.+?)\n', job)
    url_match = re.search(r'URL: (.+?)\n', job)
    
    if title_match and url_match:
        title = title_match.group(1).strip()
        url = url_match.group(1).strip()
        print(f"  [{i}] {title}")
        print(f"      {url}\n")
