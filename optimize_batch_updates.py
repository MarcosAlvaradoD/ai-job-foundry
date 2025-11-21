"""
Batch Update Optimizer - Migra updates individuales a batch updates
Reduce 60 requests/min a ~5 requests/min
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager

def optimize_batch_updates():
    """
    Ejemplo de cómo usar batch_update_jobs en lugar de múltiples update_job
    """
    print("\n📊 BATCH UPDATE OPTIMIZER\n")
    
    sheet_manager = SheetManager()
    
    # ❌ FORMA INCORRECTA (Rate limit):
    # for job in jobs:
    #     sheet_manager.update_job(row_id=job['row_id'], updates={'Status': 'Processed'})
    
    # ✅ FORMA CORRECTA (Batch):
    jobs = sheet_manager.get_all_jobs()
    
    # Preparar todos los updates
    batch_updates = []
    for job in jobs:
        if job.get('row_id'):
            batch_updates.append({
                'row_id': job['row_id'],
                'tab': 'registry',
                'updates': {
                    'Status': 'Processed',
                    'ProcessedDate': '2025-11-20'
                }
            })
    
    print(f"📦 Preparando batch de {len(batch_updates)} updates")
    
    # Ejecutar en batches de 50 (para no exceder limits)
    batch_size = 50
    for i in range(0, len(batch_updates), batch_size):
        batch = batch_updates[i:i+batch_size]
        print(f"   Procesando batch {i//batch_size + 1} ({len(batch)} items)...")
        sheet_manager.batch_update_jobs(batch)
    
    print(f"\n✅ {len(batch_updates)} updates completados en batch")
    print(f"   Requests: ~{len(batch_updates)//batch_size + 1} (vs {len(batch_updates)} individuales)")

if __name__ == "__main__":
    optimize_batch_updates()
