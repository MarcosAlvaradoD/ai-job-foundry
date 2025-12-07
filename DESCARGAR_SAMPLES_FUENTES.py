#!/usr/bin/env python3
"""
DESCARGAR EMAILS DE EJEMPLO DE CADA FUENTE
Para analizar formatos y crear parsers
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email import policy
from email.parser import BytesParser

def get_gmail_service():
    creds = None
    if os.path.exists('data/credentials/token.json'):
        creds = Credentials.from_authorized_user_file('data/credentials/token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return build('gmail', 'v1', credentials=creds)

def download_sample_email(service, sender_filter, output_file):
    """Descarga un email de ejemplo de un remitente específico"""
    
    query = f'from:{sender_filter} newer_than:7d'
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=1
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print(f"❌ No hay emails de {sender_filter}")
        return False
    
    msg_id = messages[0]['id']
    
    # Get message
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='raw'
    ).execute()
    
    # Parse
    msg_bytes = base64.urlsafe_b64decode(message['raw'])
    msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
    
    subject = msg.get('Subject', '')
    
    # Extract HTML
    html_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_content()
                break
    else:
        if msg.get_content_type() == 'text/html':
            html_content = msg.get_content()
    
    if html_content:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ {output_file}")
        print(f"   Subject: {subject[:60]}")
        print(f"   Size: {len(html_content)} chars\n")
        return True
    else:
        print(f"❌ No HTML en {sender_filter}\n")
        return False

def main():
    service = get_gmail_service()
    
    print("\n" + "="*70)
    print("📥 DESCARGANDO EMAILS DE EJEMPLO")
    print("="*70 + "\n")
    
    # Fuentes a descargar
    sources = [
        ('adzuna.com.mx', 'ADZUNA_SAMPLE.html'),
        ('computrabajo.com', 'COMPUTRABAJO_SAMPLE.html'),
        ('ziprecruiter.com', 'ZIPRECRUITER_SAMPLE.html'),
        ('markalvati@gmail.com', 'MARKALVA_SAMPLE.html'),
    ]
    
    for sender_filter, output_file in sources:
        download_sample_email(service, sender_filter, output_file)
    
    print("="*70)
    print("✅ DESCARGA COMPLETA\n")

if __name__ == '__main__':
    main()
