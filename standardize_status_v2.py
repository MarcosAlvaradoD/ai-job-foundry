#!/usr/bin/env python3
"""
Standardize Status Column Values - FIXED VERSION
Cleans up inconsistent status values in Google Sheets

Changes:
  "Ya no" → "Expired"
  "No" → "Expired"  
  "ParsedOK" → "New"
  "" (empty) → "New"

Standard values:
  - New: Just added, not reviewed
  - Active: Verified as available
  - Expired: No longer available
  - Applied: Application submitted
  - Interview: Interview scheduled
  - Rejected: Application rejected
  - Offer: Offer received

Usage:
    py standardize_status_v2.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager

def main():
    print("\n" + "="*70)
    print("STANDARDIZING STATUS VALUES")
    print("="*70)
    
    # Mapping of old values to new standard values
    status_mapping = {
        'Ya no': 'Expired',
        'No': 'Expired',
        'ParsedOK': 'New',
        '': 'New',  # Empty becomes New
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
            # Get all jobs from tab using CORRECT method
            jobs = sheet_manager.get_all_jobs(tab=tab)
            
            if not jobs:
                print(f"  [WARN] No hay datos en {tab}")
                continue
            
            tab_updates = 0
            
            # Need to get row indices for updates
            # Row 1 = headers, Row 2 = first job
            for i, job in enumerate(jobs, start=2):  # Start at row 2
                current_status = job.get('Status', '').strip()
                
                # Get mapped status
                new_status = status_mapping.get(current_status, current_status)
                
                # Update if changed
                if new_status != current_status:
                    try:
                        # Use correct method signature
                        sheet_manager.update_job_status(
                            row_index=i,
                            new_status=new_status,
                            tab=tab
                        )
                        print(f"  [OK] Row {i}: '{current_status}' -> '{new_status}'")
                        tab_updates += 1
                        total_updates += 1
                    except Exception as e:
                        print(f"  [ERROR] Row {i}: {e}")
            
            if tab_updates == 0:
                print(f"  [INFO] Todos los valores ya estan estandarizados")
            else:
                print(f"  [OK] {tab_updates} actualizaciones realizadas")
                
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
