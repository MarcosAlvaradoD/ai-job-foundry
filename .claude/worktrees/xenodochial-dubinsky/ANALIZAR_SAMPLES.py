#!/usr/bin/env python3
"""
ANALIZAR SAMPLES DE EMAILS
Extrae patterns de cada fuente para crear parsers
"""
import re
from pathlib import Path

def analyze_html(filename, source_name):
    """Analiza un HTML sample y muestra patrones útiles"""
    
    if not Path(filename).exists():
        print(f"❌ {filename} no existe\n")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print("="*70)
    print(f"🔍 {source_name.upper()}")
    print("="*70 + "\n")
    
    print(f"📊 Size: {len(html)} chars\n")
    
    # Buscar URLs de jobs
    url_patterns = [
        r'https?://[^\s<>"]+/jobs?/[^\s<>"]+',
        r'https?://[^\s<>"]+/job-listing/[^\s<>"]+',
        r'https?://[^\s<>"]+/empleo[^\s<>"]+',
        r'https?://[^\s<>"]+/ofertas?[^\s<>"]+',
    ]
    
    all_urls = []
    for pattern in url_patterns:
        urls = re.findall(pattern, html)
        all_urls.extend(urls)
    
    # Deduplicar
    all_urls = list(set(all_urls))[:10]  # Solo primeras 10
    
    print(f"🔗 URLs encontradas: {len(all_urls)}")
    for url in all_urls[:3]:
        print(f"   • {url[:80]}...")
    print()
    
    # Buscar títulos de trabajo (patterns comunes)
    title_patterns = [
        r'<h[1-3][^>]*>([^<]*(?:Manager|Analyst|Engineer|Developer|Director|Lead|Specialist)[^<]*)</h[1-3]>',
        r'<a[^>]*>([^<]*(?:Manager|Analyst|Engineer|Developer|Director|Lead|Specialist)[^<]*)</a>',
        r'<strong>([^<]*(?:Manager|Analyst|Engineer|Developer|Director|Lead|Specialist)[^<]*)</strong>',
        r'<b>([^<]*(?:Manager|Analyst|Engineer|Developer|Director|Lead|Specialist)[^<]*)</b>',
    ]
    
    titles = []
    for pattern in title_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        titles.extend(matches)
    
    # Limpiar y deduplicar
    titles = [t.strip() for t in titles if len(t.strip()) > 10]
    titles = list(dict.fromkeys(titles))[:5]
    
    print(f"📌 Títulos encontrados: {len(titles)}")
    for title in titles[:3]:
        print(f"   • {title[:60]}...")
    print()
    
    # Buscar empresas (patterns comunes)
    company_patterns = [
        r'<span[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</span>',
        r'<div[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</div>',
        r'<p[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</p>',
    ]
    
    companies = []
    for pattern in company_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        companies.extend(matches)
    
    companies = [c.strip() for c in companies if len(c.strip()) > 2]
    companies = list(dict.fromkeys(companies))[:5]
    
    print(f"🏢 Empresas encontradas: {len(companies)}")
    for company in companies[:3]:
        print(f"   • {company[:60]}...")
    print()
    
    # Snippet del HTML
    print("📝 HTML Snippet (primeros 500 chars):")
    print("-"*70)
    print(html[:500])
    print("-"*70)
    print()

def main():
    print("\n" + "="*70)
    print("🔬 ANÁLISIS DE SAMPLES DE EMAILS")
    print("="*70 + "\n")
    
    samples = [
        ('ADZUNA_SAMPLE.html', 'ADZUNA'),
        ('COMPUTRABAJO_SAMPLE.html', 'COMPUTRABAJO'),
        ('ZIPRECRUITER_SAMPLE.html', 'ZIPRECRUITER'),
        ('MARKALVA_SAMPLE.html', 'MARKALVA (auto-emails)'),
    ]
    
    for filename, source_name in samples:
        analyze_html(filename, source_name)
    
    print("="*70)
    print("✅ ANÁLISIS COMPLETO\n")

if __name__ == '__main__':
    main()
