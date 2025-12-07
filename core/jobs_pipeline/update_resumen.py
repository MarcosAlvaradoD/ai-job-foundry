"""
AI JOB FOUNDRY - Resumen Sheet Updater
Actualiza la pestaña Resumen con estadísticas en tiempo real

Autor: Marcos Alvarado
Fecha: 2025-11-21
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent.parent))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()


class ResumenUpdater:
    """Actualiza la pestaña Resumen del Sheet"""
    
    def __init__(self):
        self.sheet_manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        
        blacklist_file = Path("data/state/job_blacklist.json")
        self.blacklist_count = 0
        if blacklist_file.exists():
            with open(blacklist_file, 'r') as f:
                blacklist = json.load(f)
                self.blacklist_count = len(blacklist.get('jobs', []))
    
    def collect_statistics(self) -> dict:
        """Recolecta estadísticas de todas las pestañas"""
        print("\n📊 RECOLECTANDO ESTADÍSTICAS...")
        
        tabs_to_check = ["Jobs", "Registry", "LinkedIn", "Indeed"]
        all_jobs = []
        
        for tab_name in tabs_to_check:
            try:
                result = self.sheet_manager.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{tab_name}!A1:Z1000"
                ).execute()
                
                values = result.get('values', [])
                if values:
                    headers = values[0]
                    for row in values[1:]:
                        row_data = row + [''] * (len(headers) - len(row))
                        job = dict(zip(headers, row_data))
                        all_jobs.append(job)
                    print(f"   ✅ {tab_name}: {len(values)-1} jobs")
            except:
                continue
        
        if not all_jobs:
            print("❌ No se encontraron jobs")
            return None
        
        stats = {
            "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ofertas_analizadas": len(all_jobs),
            "blacklisted": self.blacklist_count
        }
        
        print(f"\n✅ Total ofertas: {stats['ofertas_analizadas']}")
        return stats
    
    def update_resumen_sheet(self, stats: dict) -> bool:
        """Actualiza la pestaña Resumen con las estadísticas"""
        print("\n💾 ACTUALIZANDO PESTAÑA RESUMEN...")
        
        try:
            rows = [
                ["Métrica", "Valor"],
                ["Última Actualización", stats['ultima_actualizacion']],
                ["", ""],
                ["📊 GENERAL", ""],
                ["Total Ofertas Analizadas", stats['ofertas_analizadas']],
                ["Ofertas en Blacklist", stats['blacklisted']],
            ]
            
            self.sheet_manager.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range="Resumen!A1",
                valueInputOption='USER_ENTERED',
                body={'values': rows}
            ).execute()
            
            print("✅ Pestaña Resumen actualizada correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando Resumen: {e}")
            return False
    
    def run(self):
        """Ejecuta actualización completa"""
        print("\n" + "="*70)
        print("📊 ACTUALIZADOR DE PESTAÑA RESUMEN")
        print("="*70 + "\n")
        
        stats = self.collect_statistics()
        if not stats:
            print("❌ No se pudieron recolectar estadísticas")
            return False
        
        return self.update_resumen_sheet(stats)


def main():
    updater = ResumenUpdater()
    updater.run()


if __name__ == "__main__":
    main()
