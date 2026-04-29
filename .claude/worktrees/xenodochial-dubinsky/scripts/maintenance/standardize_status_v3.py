#!/usr/bin/env python3
"""
Standardize Status Column Values - V3 with BATCH UPDATES
Fixes rate limiting by batching all updates

Changes:
  "Ya no" → "Expired"
  "No" → "Expired"  
  "ParsedOK" → "New"
  "" (empty) → "New"

Usage:
    py standardize_status_v3.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager
import time

def main():
    print("\n" + "="*70)
    print("STANDARDIZING STATUS VALUES (BATCH MODE)")
    print("="*70)
    
    # Mapping of old values to new standard values
    status_mapping = {
        'Ya no': 'Expired',
        'No': 'Expired',
        'ParsedOK': 'New',
        '': 'New',
        'OK': 'New',
        # Already standard (no change)
        'New': 'New',
        'Active': 'Active',
        'Expired': 'Expired',
        'Applied': 'Applied',
        'Interview': 'Interview',
        'Rejected': 'Rejected',
        'Offer': 'Offer'
    }
    
    print("\nStatus mapping:")
    for old, new in status_mapping.items():
        if old != new:
            old_display = f'"{old}"' if old else '(empty)'
            print(f"  {old_display:20} -> {new}")
    
    response = input("\nContinuar? (s/n): ").strip().lower()
    if response != 's':
        print("Cancelado")
        return
    
    sheet_manager = SheetManager()
    
    # Get all tabs
    tabs = ['registry', 'linkedin', 'indeed', 'glassdoor']
    
    total_updates = 0
    
    for tab in tabs:
        print(f"\nProcesando pestana: {tab.upper()}")
        
        try:
            # Get all jobs from tab
            jobs = sheet_manager.get_all_jobs(tab=tab)
            
            if not jobs:
                print(f"  [WARN] No hay datos en {tab}")
                continue
            
            # Collect all updates for batch processing
            batch_updates = []
            
            for i, job in enumerate(jobs, start=2):  # Start at row 2
                current_status = job.get('Status', '').strip()
                new_status = status_mapping.get(current_status, current_status)
                
                if new_status != current_status:
                    batch_updates.append({
                        'row_id': i,
                        'tab': tab,
                        'updates': {'Status': new_status}
                    })
            
            if not batch_updates:
                print(f"  [INFO] Todos los valores ya estan estandarizados")
                continue
            
            # Apply batch updates (more efficient)
            print(f"  [INFO] Aplicando {len(batch_updates)} actualizaciones en batch...")
            
            try:
                sheet_manager.batch_update_jobs(batch_updates)
                print(f"  [OK] {len(batch_updates)} actualizaciones realizadas")
                total_updates += len(batch_updates)
            except Exception as e:
                print(f"  [ERROR] Batch update failed: {e}")
            
            # Small delay between tabs to avoid rate limiting
            if tab != tabs[-1]:  # Not the last tab
                print(f"  [INFO] Esperando 2 segundos...")
                time.sleep(2)
                
        except Exception as e:
            print(f"  [ERROR] Procesando {tab}: {e}")
    
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Total actualizaciones: {total_updates}")
    print("\n[OK] Proceso completado")
    print("="*70)
    
    if total_updates > 0:
        print("\nTIP: Abre Google Sheets para ver los cambios:")
        print("   py control_center.py -> Opcion 14")

if __name__ == "__main__":
    main()
