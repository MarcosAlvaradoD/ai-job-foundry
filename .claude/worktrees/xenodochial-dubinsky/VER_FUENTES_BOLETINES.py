#!/usr/bin/env python3
"""
VER TODAS LAS FUENTES DE BOLETINES
Identifica qué otras fuentes de job alerts tienes
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email import policy
from email.parser import BytesParser
from collections import Counter

def get_gmail_service():
    creds = None
    if os.path.exists('data/credentials/token.json'):
        creds = Credentials.from_authorized_user_file('data/credentials/token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return build('gmail', 'v1', credentials=creds)

def main():
    service = get_gmail_service()
    
    # Query para TODOS los emails que parecen boletines de jobs
    query = 'subject:(jobs OR empleos OR opportunities OR postulate OR apply) newer_than:30d'
    
    print("\n" + "="*70)
    print("📧 ANÁLISIS DE FUENTES DE JOB ALERTS")
    print("="*70 + "\n")
    
    print(f"Query: {query}\n")
    print("Buscando emails...\n")
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100  # Analizar últimos 100
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No hay emails")
        return
    
    print(f"📊 Encontrados: {len(messages)} emails\n")
    print("Analizando remitentes...\n")
    
    senders = []
    
    for msg_ref in messages:
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
        
        sender = msg.get('From', '')
        senders.append(sender)
    
    # Contar frecuencia
    sender_counts = Counter(senders)
    
    print("="*70)
    print("📊 TOP REMITENTES DE JOB ALERTS (últimos 30 días)")
    print("="*70 + "\n")
    
    for sender, count in sender_counts.most_common(20):
        # Identificar tipo
        sender_lower = sender.lower()
        if 'glassdoor' in sender_lower:
            icon = "🔵 GLASSDOOR"
        elif 'linkedin' in sender_lower:
            icon = "🔷 LINKEDIN"
        elif 'indeed' in sender_lower:
            icon = "🟦 INDEED"
        elif 'ziprecruiter' in sender_lower:
            icon = "🟩 ZIPRECRUITER"
        elif 'monster' in sender_lower:
            icon = "🟧 MONSTER"
        elif 'simplyhired' in sender_lower:
            icon = "🟨 SIMPLYHIRED"
        else:
            icon = "❓ OTHER"
        
        print(f"{icon} ({count} emails)")
        print(f"   {sender}")
        print()
    
    print("="*70 + "\n")
    
    # Identificar fuentes NO procesadas actualmente
    print("🔍 FUENTES NO PROCESADAS ACTUALMENTE:\n")
    
    current_sources = ['glassdoor.com', 'linkedin.com', 'indeed.com']
    
    for sender, count in sender_counts.most_common(20):
        sender_lower = sender.lower()
        is_current = any(src in sender_lower for src in current_sources)
        
        if not is_current and count >= 3:
            print(f"   • {sender} ({count} emails)")
    
    print()

if __name__ == '__main__':
    main()
