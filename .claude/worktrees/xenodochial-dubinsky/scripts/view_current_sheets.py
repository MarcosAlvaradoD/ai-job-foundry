"""
AI JOB FOUNDRY - Quick Sheets Viewer
Visualiza rápidamente qué hay en tus Google Sheets

Autor: Marcos Alvarado
Fecha: 2025-11-21
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()


def main():
    """Ver datos actuales de Google Sheets"""
    
    print("\n" + "="*70)
    print("📊 QUICK SHEETS VIEWER - AI JOB FOUNDRY")
    print("="*70 + "\n")
    
    manager = SheetManager()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    print(f"Sheet ID: {spreadsheet_id}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n")
    
    # Try all possible tab names
    tabs_to_try = ["Jobs", "Registry", "LinkedIn", "Indeed", "Glassdoor", "Resumen"]
    
    found_tabs = []
    
    for tab_name in tabs_to_try:
        try:
            result = manager.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{tab_name}!A1:Z1000"
            ).execute()
            
            values = result.get('values', [])
            
            if values:
                found_tabs.append(tab_name)
                headers = values[0]
                num_jobs = len(values) - 1
                
                print(f"✅ Pestaña: {tab_name}")
                print(f"   - Headers: {len(headers)} columnas")
                print(f"   - Jobs: {num_jobs}")
                
                if num_jobs > 0 and len(headers) > 2:
                    print(f"   - Columnas: {', '.join(headers[:8])}...")
                    
                    if len(values) > 1:
                        first_job = values[1]
                        company = first_job[1] if len(first_job) > 1 else "N/A"
                        role = first_job[2] if len(first_job) > 2 else "N/A"
                        print(f"   - Primera entrada: {company} - {role}")
                
                print()
        
        except Exception as e:
            print(f"⚠️  Pestaña: {tab_name} - No encontrada")
            print(f"   Error: {str(e)[:50]}...\n")
    
    print("="*70)
    print(f"📊 RESUMEN")
    print("="*70)
    print(f"Pestañas encontradas: {len(found_tabs)}")
    print(f"Pestañas: {', '.join(found_tabs)}")
    print()
    
    print("="*70)
    print("🚀 PRÓXIMOS PASOS")
    print("="*70)
    print()
    
    if "Resumen" in found_tabs:
        print("1. ✅ Pestaña Resumen existe - Actualízala con:")
        print("   py core\\jobs_pipeline\\update_resumen.py")
    else:
        print("1. ⚠️  Pestaña Resumen NO existe - Créala manualmente en Google Sheets")
        print("   Nombre exacto: 'Resumen'")
        print("   Después ejecuta: py core\\jobs_pipeline\\update_resumen.py")
    
    print()
    print("2. Ejecutar limpieza automática:")
    print("   .\\run_daily_cleanup.ps1")
    print()
    print("3. Ver resultados en Google Sheets:")
    print(f"   https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print()


if __name__ == "__main__":
    main()
