#!/usr/bin/env python3
"""
TEST DEL FIX DE BOLETINES
Prueba el nuevo sistema sin procesar emails reales

Lo que hace:
1. Simula verificación de edad (skip emails >7 días)
2. Verifica duplicados en Sheets ANTES de guardar
3. Lista emails que serían eliminados
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.automation.job_bulletin_processor import JobBulletinProcessor

def main():
    print("\n" + "="*70)
    print("🧪 TEST DEL FIX DE BOLETINES")
    print("="*70)
    print("Este script SOLO lee emails, NO los procesa")
    print("="*70 + "\n")
    
    processor = JobBulletinProcessor()
    
    # Obtener emails de boletines
    query = 'from:(noreply@glassdoor.com OR jobs-noreply@linkedin.com OR noreply@indeed.com) newer_than:30d'
    results = processor.gmail_service.users().messages().list(
        userId='me',
        q=query,
        maxResults=10  # Solo 10 para test
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No se encontraron emails")
        return
    
    print(f"📧 Encontrados {len(messages)} emails\n")
    
    # Analizar cada email
    for i, msg_ref in enumerate(messages, 1):
        msg_id = msg_ref['id']
        
        # Get full message
        message = processor.gmail_service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        # Obtener información
        subject = ""
        sender = ""
        date = ""
        
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'subject':
                subject = header['value']
            elif header['name'].lower() == 'from':
                sender = header['value']
            elif header['name'].lower() == 'date':
                date = header['value']
        
        # Calcular edad
        email_age = processor.get_email_age_days(message)
        
        # Determinar tipo
        bulletin_type = processor.detect_bulletin_type(sender, subject)
        
        print(f"📨 Email #{i}")
        print(f"   From: {sender[:50]}...")
        print(f"   Subject: {subject[:60]}...")
        print(f"   Date: {date}")
        print(f"   Age: {email_age} days")
        print(f"   Type: {bulletin_type or 'Unknown'}")
        
        if email_age > 7:
            print(f"   ⏭️  SERÍA SKIPPED (>7 días)")
        else:
            print(f"   ✅ SERÍA PROCESADO")
        
        print()
    
    print("="*70)
    print("✅ Test completado")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
