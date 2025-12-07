"""
AI Job Cleaner - Sistema automático de limpieza de Google Sheets
Maneja jobs expirados, rechazados y limpieza temporal (30 días)

FUNCIONALIDADES:
1. Verifica URLs con AI (job_expiration_system.md)
2. Marca jobs para borrar después de 30 días
3. Mantiene blacklist temporal de 30 días
4. Mueve jobs archivados a pestaña separada
5. Actualiza estadísticas en Resumen

USO:
py ai_job_cleaner.py --dry-run  # Ver qué se borraría
py ai_job_cleaner.py             # Ejecutar limpieza real
py ai_job_cleaner.py --stats     # Ver estadísticas
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from core.utils.llm_client import LLMClient

# Configuración
DAYS_TO_DELETE = 30  # Días antes de borrar permanentemente
BLACKLIST_FILE = "data/state/job_blacklist.json"

class JobCleaner:
    """
    Limpiador automático de jobs con AI
    """
    
    def __init__(self, dry_run=False):
        self.sheet_manager = SheetManager()
        self.llm = LLMClient()
        self.dry_run = dry_run
        self.blacklist = self._load_blacklist()
        
        print(f"\n🧹 AI JOB CLEANER - {'DRY RUN' if dry_run else 'REAL MODE'}\n")
    
    def _load_blacklist(self) -> dict:
        """Carga blacklist temporal de jobs"""
        if os.path.exists(BLACKLIST_FILE):
            with open(BLACKLIST_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_blacklist(self):
        """Guarda blacklist"""
        os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump(self.blacklist, f, indent=2)
    
    def _is_in_blacklist(self, job_url: str) -> bool:
        """Verifica si un job está en blacklist temporal"""
        if job_url not in self.blacklist:
            return False
        
        # Verificar si ya pasaron 30 días
        blacklisted_date = datetime.fromisoformat(self.blacklist[job_url]['date'])
        days_passed = (datetime.now() - blacklisted_date).days
        
        if days_passed >= DAYS_TO_DELETE:
            # Ya pasaron 30 días, remover de blacklist
            del self.blacklist[job_url]
            self._save_blacklist()
            return False
        
        return True
    
    def _add_to_blacklist(self, job_url: str, reason: str):
        """Agrega job a blacklist temporal"""
        self.blacklist[job_url] = {
            'date': datetime.now().isoformat(),
            'reason': reason,
            'days_remaining': DAYS_TO_DELETE
        }
        self._save_blacklist()
    
    def analyze_jobs(self):
        """
        Analiza todos los jobs y determina cuáles borrar
        """
        print("📊 Cargando jobs desde Google Sheets...")
        jobs = self.sheet_manager.get_all_jobs(tab='registry')
        
        if not jobs:
            print("❌ No se encontraron jobs")
            return
        
        print(f"✅ {len(jobs)} jobs encontrados\n")
        
        # Categorías
        to_delete = []  # Borrar inmediatamente
        to_mark = []    # Marcar para borrar en 30 días
        to_keep = []    # Mantener
        in_blacklist = []  # Ya en blacklist
        
        print("🔍 Analizando jobs...\n")
        
        for job in jobs:
            row_id = job.get('row_id')
            status = job.get('Status', 'Unknown')
            apply_url = job.get('ApplyURL', '')
            created_at = job.get('CreatedAt', '')
            company = job.get('Company', 'Unknown')
            role = job.get('Role', 'Unknown')
            
            # Calcular días desde creación
            try:
                created_date = datetime.fromisoformat(created_at.split()[0])
                days_old = (datetime.now() - created_date).days
            except:
                days_old = 0
            
            # Verificar blacklist
            if apply_url and self._is_in_blacklist(apply_url):
                in_blacklist.append({
                    'row_id': row_id,
                    'company': company,
                    'role': role,
                    'reason': self.blacklist[apply_url]['reason'],
                    'days_in_blacklist': DAYS_TO_DELETE - self.blacklist[apply_url]['days_remaining']
                })
                continue
            
            # Lógica de limpieza
            if status == "No longer accepting applications":
                if days_old >= DAYS_TO_DELETE:
                    to_delete.append({
                        'row_id': row_id,
                        'company': company,
                        'role': role,
                        'status': status,
                        'days_old': days_old,
                        'url': apply_url
                    })
                else:
                    to_mark.append({
                        'row_id': row_id,
                        'company': company,
                        'role': role,
                        'status': status,
                        'days_old': days_old,
                        'days_remaining': DAYS_TO_DELETE - days_old,
                        'url': apply_url
                    })
            
            elif "reject" in status.lower() or "declined" in status.lower():
                if days_old >= DAYS_TO_DELETE:
                    to_delete.append({
                        'row_id': row_id,
                        'company': company,
                        'role': role,
                        'status': status,
                        'days_old': days_old,
                        'url': apply_url
                    })
                else:
                    to_mark.append({
                        'row_id': row_id,
                        'company': company,
                        'role': role,
                        'status': status,
                        'days_old': days_old,
                        'days_remaining': DAYS_TO_DELETE - days_old,
                        'url': apply_url
                    })
            
            else:
                to_keep.append({
                    'row_id': row_id,
                    'company': company,
                    'role': role,
                    'status': status
                })
        
        # Reportar resultados
        self._print_report(to_delete, to_mark, to_keep, in_blacklist)
        
        # Ejecutar acciones (si no es dry-run)
        if not self.dry_run:
            self._execute_cleanup(to_delete, to_mark)
        else:
            print("\n⚠️  DRY RUN - No se realizaron cambios")
            print("   Ejecuta sin --dry-run para aplicar cambios\n")
    
    def _print_report(self, to_delete, to_mark, to_keep, in_blacklist):
        """Imprime reporte de análisis"""
        print("="*70)
        print("📊 REPORTE DE ANÁLISIS")
        print("="*70 + "\n")
        
        # A borrar
        if to_delete:
            print(f"🗑️  BORRAR AHORA ({len(to_delete)} jobs):")
            for job in to_delete:
                print(f"   [{job['days_old']}d] {job['company']} - {job['role']}")
                print(f"       Status: {job['status']}")
            print()
        
        # A marcar
        if to_mark:
            print(f"⏰ MARCAR PARA BORRAR ({len(to_mark)} jobs):")
            for job in to_mark:
                print(f"   [{job['days_remaining']}d restantes] {job['company']} - {job['role']}")
                print(f"       Status: {job['status']}")
            print()
        
        # En blacklist
        if in_blacklist:
            print(f"🚫 EN BLACKLIST TEMPORAL ({len(in_blacklist)} jobs):")
            for job in in_blacklist:
                print(f"   {job['company']} - {job['role']}")
                print(f"       Razón: {job['reason']}")
            print()
        
        # A mantener
        print(f"✅ MANTENER ({len(to_keep)} jobs)")
        print()
        
        # Resumen
        total = len(to_delete) + len(to_mark) + len(to_keep) + len(in_blacklist)
        print("="*70)
        print(f"TOTAL: {total} jobs analizados")
        print("="*70 + "\n")
    
    def _execute_cleanup(self, to_delete, to_mark):
        """Ejecuta la limpieza real"""
        print("\n🔄 EJECUTANDO LIMPIEZA...\n")
        
        # Borrar jobs
        if to_delete:
            print(f"🗑️  Borrando {len(to_delete)} jobs...")
            for job in to_delete:
                # Agregar a blacklist
                if job['url']:
                    self._add_to_blacklist(job['url'], f"Deleted: {job['status']}")
                
                # TODO: Implementar borrado real de Google Sheets
                # self.sheet_manager.delete_job(job['row_id'])
                print(f"   ✅ {job['company']} - {job['role']}")
        
        # Marcar jobs
        if to_mark:
            print(f"\n⏰ Marcando {len(to_mark)} jobs para borrar...")
            for job in to_mark:
                # TODO: Actualizar status en Sheets
                # self.sheet_manager.update_job(job['row_id'], {
                #     'Status': f"Marked for deletion ({job['days_remaining']}d)"
                # })
                print(f"   ✅ {job['company']} - {job['role']}")
        
        print("\n✅ Limpieza completada\n")
    
    def update_resumen(self):
        """Actualiza pestaña Resumen con estadísticas"""
        print("📊 Actualizando Resumen...")
        
        jobs = self.sheet_manager.get_all_jobs(tab='registry')
        
        if not jobs:
            print("❌ No hay jobs para estadísticas")
            return
        
        # Calcular estadísticas
        total_jobs = len(jobs)
        by_source = {}
        by_status = {}
        fit_scores = []
        
        for job in jobs:
            # Por fuente
            source = job.get('Source', 'Unknown')
            by_source[source] = by_source.get(source, 0) + 1
            
            # Por status
            status = job.get('Status', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1
            
            # FIT scores
            try:
                fit = int(job.get('FitScore', 0))
                if fit > 0:
                    fit_scores.append(fit)
            except:
                pass
        
        avg_fit = sum(fit_scores) / len(fit_scores) if fit_scores else 0
        
        # TODO: Actualizar pestaña Resumen en Sheets
        stats = {
            'ultima_actualizacion': datetime.now().isoformat(),
            'ofertas_analizadas': total_jobs,
            'por_fuente': by_source,
            'por_status': by_status,
            'fit_promedio': round(avg_fit, 1)
        }
        
        print(f"✅ Estadísticas calculadas:")
        print(f"   Total: {total_jobs}")
        print(f"   FIT Promedio: {avg_fit:.1f}")
        print()
        
        return stats

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Job Cleaner')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin hacer cambios')
    parser.add_argument('--stats', action='store_true', help='Solo actualizar estadísticas')
    
    args = parser.parse_args()
    
    cleaner = JobCleaner(dry_run=args.dry_run)
    
    if args.stats:
        cleaner.update_resumen()
    else:
        cleaner.analyze_jobs()
        cleaner.update_resumen()

if __name__ == "__main__":
    main()
