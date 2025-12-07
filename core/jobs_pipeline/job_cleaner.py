"""
AI JOB FOUNDRY - Job Cleaner V2
Sistema automático de limpieza con blacklist temporal

Funcionalidad:
1. Revisa URLs para detectar expirados
2. Marca jobs "No longer accepting applications"
3. Blacklist temporal de 30 días
4. Auto-limpieza después de 30 días
5. Actualiza pestaña "Resumen"

Autor: Marcos Alvarado
Fecha: 2025-11-21
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time

# Add core to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

# Try to import LLMClient (optional)
try:
    from core.utils.llm_client import LLMClient
    HAS_LLM = True
except:
    HAS_LLM = False


class JobCleaner:
    """Sistema de limpieza automática de jobs con blacklist temporal"""
    
    def __init__(self):
        self.sheet_manager = SheetManager()
        
        # Try to initialize LLM (optional)
        if HAS_LLM:
            try:
                self.llm = LLMClient()
            except:
                self.llm = None
                print("⚠️  LLM Client no disponible")
        else:
            self.llm = None
            print("⚠️  LLM Client no disponible")
        
        self.blacklist_file = Path("data/state/job_blacklist.json")
        self.blacklist = self._load_blacklist()
        
        # Estados que activan limpieza
        self.expiry_statuses = [
            "No longer accepting applications",
            "Expired",
            "Rejected",
            "Position filled"
        ]
        
        # Días para mantener en blacklist
        self.blacklist_days = 30
    
    def _load_blacklist(self) -> Dict:
        """Carga blacklist desde archivo JSON"""
        if self.blacklist_file.exists():
            with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"jobs": [], "last_cleanup": None}
    
    def _save_blacklist(self):
        """Guarda blacklist a archivo JSON"""
        self.blacklist_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(self.blacklist, f, indent=2, ensure_ascii=False)
    
    def check_url_status(self, url: str) -> Dict:
        """Verifica si una URL sigue activa"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=10)
            content = response.text.lower()
            
            expiry_keywords = [
                "no longer accepting",
                "position has been filled",
                "job posting expired",
                "this job is no longer available"
            ]
            
            expired = any(keyword in content for keyword in expiry_keywords)
            
            return {
                "active": response.status_code == 200 and not expired,
                "status_code": response.status_code,
                "expired": expired or response.status_code == 404,
                "error": None
            }
        except Exception as e:
            return {"active": False, "status_code": 0, "expired": False, "error": str(e)}
    
    def add_to_blacklist(self, job: Dict, reason: str):
        """Agrega un job a la blacklist temporal"""
        blacklist_entry = {
            "url": job.get('ApplyURL', ''),
            "company": job.get('Company', 'Unknown'),
            "role": job.get('Role', 'Unknown'),
            "reason": reason,
            "added_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=self.blacklist_days)).isoformat(),
            "row_id": job.get('_row_id')
        }
        
        existing_urls = [entry.get('url') for entry in self.blacklist['jobs']]
        if blacklist_entry['url'] not in existing_urls:
            self.blacklist['jobs'].append(blacklist_entry)
            self._save_blacklist()
            print(f"  🚫 Added to blacklist: {job.get('Company')} - {job.get('Role')}")
    
    def clean_expired_from_blacklist(self) -> int:
        """Limpia jobs que ya cumplieron 30 días en blacklist"""
        now = datetime.now()
        expired_entries = []
        remaining_entries = []
        
        for entry in self.blacklist['jobs']:
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if now >= expires_at:
                expired_entries.append(entry)
            else:
                remaining_entries.append(entry)
        
        self.blacklist['jobs'] = remaining_entries
        self.blacklist['last_cleanup'] = now.isoformat()
        self._save_blacklist()
        
        print(f"\n🗑️  Jobs expirados de blacklist (30+ días): {len(expired_entries)}")
        return len(expired_entries)
    
    def scan_and_mark(self, tab: str = "Jobs") -> Dict:
        """Escanea todos los jobs y marca los que deben limpiarse"""
        print(f"\n🔍 ESCANEANDO JOBS EN {tab.upper()}\n")
        
        try:
            jobs = self.sheet_manager.get_all_jobs(tab.lower())
        except:
            print(f"⚠️  Intento con nombre exacto: {tab}")
            # Try exact tab name
            result = self.sheet_manager.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_manager.spreadsheet_id,
                range=f"{tab}!A1:Z1000"
            ).execute()
            values = result.get('values', [])
            if not values:
                print(f"❌ No se encontraron datos en {tab}")
                return {"total_scanned": 0, "newly_marked": 0, "blacklisted": 0}
            headers = values[0]
            jobs = [dict(zip(headers, row + [''] * (len(headers) - len(row)))) for row in values[1:]]
        
        stats = {"total_scanned": len(jobs), "newly_marked": 0, "blacklisted": 0}
        
        for idx, job in enumerate(jobs, start=2):
            current_status = job.get('Status', '')
            
            if current_status in self.expiry_statuses:
                self.add_to_blacklist(job, f"Already marked as {current_status}")
                stats['blacklisted'] += 1
        
        print(f"\n✅ Escaneo completado: {stats['total_scanned']} jobs")
        return stats
    
    def run_daily_cleanup(self, tab: str = "Jobs"):
        """Ejecuta limpieza diaria completa"""
        print("\n" + "="*70)
        print("🧹 AI JOB CLEANER - LIMPIEZA DIARIA")
        print("="*70)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Pestaña: {tab}")
        print("="*70 + "\n")
        
        # 1. Clean expired from blacklist
        expired_count = self.clean_expired_from_blacklist()
        
        # 2. Scan and mark jobs
        stats = self.scan_and_mark(tab=tab)
        
        # 3. Print final report
        print("\n" + "="*70)
        print("📋 REPORTE FINAL")
        print("="*70)
        print(f"✅ Jobs escaneados: {stats['total_scanned']}")
        print(f"🚫 Agregados a blacklist: {stats['blacklisted']}")
        print(f"🗑️  Expirados de blacklist: {expired_count}")
        print(f"📊 Blacklist actual: {len(self.blacklist['jobs'])} jobs")
        print("="*70 + "\n")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Job Cleaner")
    parser.add_argument('--tab', default='Jobs', help='Pestaña a procesar')
    parser.add_argument('--view-blacklist', action='store_true', help='Ver blacklist')
    args = parser.parse_args()
    
    cleaner = JobCleaner()
    
    if args.view_blacklist:
        print("\n🚫 BLACKLIST ACTUAL\n")
        print(f"Total jobs: {len(cleaner.blacklist['jobs'])}")
        for entry in cleaner.blacklist['jobs']:
            print(f"- {entry['company']} - {entry['role']}")
            print(f"  Razón: {entry['reason']}")
            print(f"  Expira: {entry['expires_at']}\n")
    else:
        cleaner.run_daily_cleanup(tab=args.tab)


if __name__ == "__main__":
    main()
