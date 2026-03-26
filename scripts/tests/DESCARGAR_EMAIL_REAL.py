#!/usr/bin/env python3
"""
DESCARGAR EMAIL REAL DE GLASSDOOR
Para analizar el formato actual de los boletines
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email import policy
from email.parser import BytesParser

def get_gmail_service():
    """Initialize Gmail API service"""
    creds = None
    if os.path.exists('data/credentials/token.json'):
        creds = Credentials.from_authorized_user_file('data/credentials/token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return build('gmail', 'v1', credentials=creds)

def main():
    service = get_gmail_service()
    
    # Query for recent Glassdoor job alerts (not company news)
    query = 'from:noreply@glassdoor.com subject:"empleos" newer_than:3d'
    
    print("\n" + "="*70)
    print("📧 BUSCANDO EMAILS DE GLASSDOOR CON OFERTAS")
    print("="*70 + "\n")
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=5
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No hay emails recientes de Glassdoor con ofertas")
        return
    
    print(f"📊 Encontrados: {len(messages)} emails\n")
    
    # Listar para que el usuario elija
    for i, msg_ref in enumerate(messages, 1):
        msg_id = msg_ref['id']
        
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
        date = msg.get('Date', '')
        
        print(f"{i}. Subject: {subject}")
        print(f"   Date: {date}")
        print(f"   ID: {msg_id}")
        print()
    
    # Descargar el primero automáticamente
    msg_ref = messages[0]
    msg_id = msg_ref['id']
    
    print("="*70)
    print("📥 Descargando el primer email...")
    print("="*70 + "\n")
    
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='raw'
    ).execute()
    
    msg_bytes = base64.urlsafe_b64decode(message['raw'])
    msg = BytesParser(policy=policy.default).parsebytes(msg_bytes)
    
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
        # Save to file
        output_file = 'GLASSDOOR_EMAIL_REAL.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML guardado en: {output_file}")
        print(f"   Tamaño: {len(html_content)} caracteres")
        
        # Show snippet
        print(f"\n📝 Primeros 500 caracteres:")
        print("-"*70)
        print(html_content[:500])
        print("-"*70)
    else:
        print("❌ No se encontró contenido HTML")

if __name__ == '__main__':
    main()
