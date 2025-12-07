#!/usr/bin/env python3
"""
ANALIZAR EMAIL DE GLASSDOOR
Descarga un email real y muestra su estructura HTML para arreglar el parser
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import base64
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email import policy
from email.parser import BytesParser

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    """Get OAuth credentials"""
    creds = None
    token_path = "data/credentials/token.json"
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    return creds

def main():
    print("\n" + "="*70)
    print("🔍 ANALIZAR EMAIL DE GLASSDOOR")
    print("="*70 + "\n")
    
    creds = get_credentials()
    if not creds:
        print("❌ No se encontraron credenciales")
        return
    
    gmail = build('gmail', 'v1', credentials=creds)
    
    # Buscar email más reciente de Glassdoor
    query = 'from:noreply@glassdoor.com newer_than:1d'
    results = gmail.users().messages().list(
        userId='me',
        q=query,
        maxResults=1
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No se encontraron emails de Glassdoor recientes")
        return
    
    # Obtener email completo
    msg_id = messages[0]['id']
    message = gmail.users().messages().get(
        userId='me',
        id=msg_id,
        format='raw'
    ).execute()
    
    # Parsear email
    msg_bytes = base64.urlsafe_b64decode(message['raw'])
    msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
    
    subject = msg.get('Subject', '')
    sender = msg.get('From', '')
    
    print(f"📧 Email:")
    print(f"   From: {sender}")
    print(f"   Subject: {subject}")
    print()
    
    # Extraer HTML
    html_content = ""
    text_content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_content()
            elif part.get_content_type() == 'text/plain':
                text_content = part.get_content()
    else:
        content = msg.get_content()
        if msg.get_content_type() == 'text/html':
            html_content = content
        else:
            text_content = content
    
    # Guardar HTML para análisis
    output_file = "GLASSDOOR_EMAIL_SAMPLE.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML guardado en: {output_file}")
    print()
    
    # Mostrar estructura básica
    print("📋 Estructura del HTML:")
    print("="*70)
    
    # Buscar patrones comunes
    import re
    
    # URLs de Glassdoor
    urls = re.findall(r'https://www\.glassdoor\.com[^\s"<>]+', html_content)
    print(f"\n🔗 URLs encontradas: {len(urls)}")
    if urls:
        print("   Primeras 3:")
        for url in urls[:3]:
            print(f"   - {url[:80]}...")
    
    # Títulos de trabajo (patterns comunes)
    title_patterns = [
        r'<a[^>]*>([^<]*(?:Manager|Director|Lead|Analyst|Engineer|Developer)[^<]*)</a>',
        r'<td[^>]*>([^<]*(?:Manager|Director|Lead|Analyst|Engineer|Developer)[^<]*)</td>',
        r'<div[^>]*>([^<]*(?:Manager|Director|Lead|Analyst|Engineer|Developer)[^<]*)</div>'
    ]
    
    all_titles = []
    for pattern in title_patterns:
        titles = re.findall(pattern, html_content, re.IGNORECASE)
        all_titles.extend(titles)
    
    print(f"\n📝 Títulos potenciales encontrados: {len(all_titles)}")
    if all_titles:
        print("   Primeros 5:")
        for title in all_titles[:5]:
            print(f"   - {title.strip()}")
    
    # Empresas
    company_patterns = [
        r'<span[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</span>',
        r'<div[^>]*class="[^"]*employer[^"]*"[^>]*>([^<]+)</div>',
        r'<td[^>]*>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)</td>'
    ]
    
    all_companies = []
    for pattern in company_patterns:
        companies = re.findall(pattern, html_content)
        all_companies.extend(companies)
    
    print(f"\n🏢 Empresas potenciales: {len(all_companies)}")
    if all_companies:
        print("   Primeras 5:")
        for company in all_companies[:5]:
            print(f"   - {company.strip()}")
    
    print("\n" + "="*70)
    print(f"📄 Abre {output_file} en un navegador para ver el HTML completo")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
