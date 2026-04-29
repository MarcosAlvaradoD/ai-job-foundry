"""
UNIFIED RUNNER - Ejecutor unificado del sistema
Orquesta: Ingesta → Enriquecimiento → Tracking
"""

import time
import schedule
from pathlib import Path
import sys

# Agregar paths
sys.path.insert(0, str(Path(__file__).parent / "core" / "ingestion"))
sys.path.insert(0, str(Path(__file__).parent / "core" / "enrichment"))
sys.path.insert(0, str(Path(__file__).parent / "core" / "tracking"))

def run_ingestion():
    """Ejecuta ingesta de emails"""
    print("\n🔽 Ejecutando ingesta...")
    try:
        from ingest_email_to_sheet_v2 import main as ingest_main
        ingest_main()
        print("✅ Ingesta completada")
    except Exception as e:
        print(f"❌ Error en ingesta: {e}")

def run_enrichment():
    """Ejecuta enriquecimiento con IA"""
    print("\n🤖 Ejecutando enriquecimiento...")
    try:
        from enrich_sheet_with_llm_v3 import main as enrich_main
        enrich_main()
        print("✅ Enriquecimiento completado")
    except Exception as e:
        print(f"❌ Error en enriquecimiento: {e}")

def run_tracking():
    """Ejecuta tracking de aplicaciones"""
    print("\n🎯 Ejecutando tracking...")
    try:
        from job_tracker import JobTracker
        tracker = JobTracker()
        tracker.check_gmail_for_responses()
        print("✅ Tracking completado")
    except Exception as e:
        print(f"❌ Error en tracking: {e}")

def run_full_pipeline():
    """Ejecuta pipeline completo"""
    print("\n" + "="*60)
    print("  🚀 PIPELINE COMPLETO")
    print("="*60)
    
    run_ingestion()
    time.sleep(5)
    
    run_enrichment()
    time.sleep(5)
    
    run_tracking()
    
    print("\n✅ Pipeline completado\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Runner")
    parser.add_argument('--mode', choices=['once', 'schedule'], default='once')
    parser.add_argument('--interval', type=int, default=30, help='Minutos entre ejecuciones')
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        run_full_pipeline()
    else:
        print(f"🔄 Modo scheduled: cada {args.interval} minutos")
        print("Presiona Ctrl+C para detener\n")
        
        schedule.every(args.interval).minutes.do(run_full_pipeline)
        
        # Primera ejecución inmediata
        run_full_pipeline()
        
        # Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n🛑 Detenido por usuario")
