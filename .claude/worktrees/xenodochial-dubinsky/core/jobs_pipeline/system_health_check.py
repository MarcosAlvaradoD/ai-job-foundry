"""
AI JOB FOUNDRY - System Health Check & Duplicate Verifier
Verifica estado del sistema y detecta jobs duplicados

Autor: Claude Sonnet 4.5 (via Desktop Commander)
Fecha: 2025-11-23
Tarea original asignada a: LM Studio (Qwen 2.5 14B) - NO completada
Completada por: Claude + Desktop Commander
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent.parent))

from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()


class SystemHealthChecker:
    """Verificador de salud del sistema y duplicados"""
    
    def __init__(self):
        self.sheet_manager = SheetManager()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.project_root = Path(__file__).parent.parent.parent
        
        self.health_report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "UNKNOWN",
            "checks": {},
            "duplicates": {},
            "recommendations": []
        }
    
    def check_critical_files(self) -> Dict:
        """Verifica que archivos críticos existan"""
        print("\n🔍 Verificando archivos críticos...")
        
        critical_files = [
            ".env",
            "core/sheets/sheet_manager.py",
            "core/jobs_pipeline/job_cleaner.py",
            "core/jobs_pipeline/update_resumen.py",
            "data/credentials/token.json",
            "data/credentials/credentials.json"
        ]
        
        results = {}
        missing_count = 0
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            readable = exists and os.access(full_path, os.R_OK)
            
            results[file_path] = {
                "exists": exists,
                "readable": readable
            }
            
            if not exists:
                missing_count += 1
                print(f"  ❌ Falta: {file_path}")
            elif not readable:
                print(f"  ⚠️  No legible: {file_path}")
            else:
                print(f"  ✅ OK: {file_path}")
        
        return {
            "status": "OK" if missing_count == 0 else "WARNING",
            "files": results,
            "missing_count": missing_count
        }
    
    def check_directory_structure(self) -> Dict:
        """Verifica estructura de directorios"""
        print("\n📁 Verificando estructura de directorios...")
        
        required_dirs = [
            "core/sheets",
            "core/jobs_pipeline",
            "core/ingestion",
            "core/enrichment",
            "data/state",
            "data/credentials",
            "logs",
            "docs"
        ]
        
        results = {}
        missing_count = 0
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            exists = full_path.exists() and full_path.is_dir()
            results[dir_path] = exists
            
            if not exists:
                missing_count += 1
                print(f"  ❌ Falta: {dir_path}")
            else:
                print(f"  ✅ OK: {dir_path}")
        
        return {
            "status": "OK" if missing_count == 0 else "WARNING",
            "directories": results,
            "missing_count": missing_count
        }
    
    def check_sheets_connection(self) -> Dict:
        """Verifica conexión a Google Sheets"""
        print("\n🔗 Verificando conexión a Google Sheets...")
        
        try:
            # Intenta leer la hoja Jobs!A1:A1 para verificar la conexión
            result = self.sheet_manager.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range="Jobs!A1:A1"
            ).execute()
            
            print(f"  ✅ Conectado a Sheets ID: {self.spreadsheet_id}")
            
            return {
                "status": "OK",
                "connected": True,
                "error": None,
                "spreadsheet_id": self.spreadsheet_id
            }
        except Exception as e:
            print(f"  ❌ Error de conexión: {str(e)}")
            return {
                "status": "ERROR",
                "connected": False,
                "error": str(e),
                "spreadsheet_id": self.spreadsheet_id
            }
    
    def find_duplicate_jobs(self) -> Dict:
        """Encuentra jobs duplicados en todas las pestañas"""
        print("\n🔎 Buscando jobs duplicados...")
        
        try:
            # Leer todas las pestañas
            sheets_data = self.sheet_manager.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            all_jobs = []
            url_map = defaultdict(list)
            company_role_map = defaultdict(list)
            
            # Procesar cada pestaña
            for sheet in sheets_data.get('sheets', []):
                sheet_name = sheet['properties']['title']
                
                if sheet_name in ['RESUMEN', 'BLACKLIST']:
                    continue
                
                print(f"  📄 Procesando: {sheet_name}")
                
                # Leer datos
                result = self.sheet_manager.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A2:F1000"
                ).execute()
                
                rows = result.get('values', [])
                
                for idx, row in enumerate(rows, start=2):
                    if len(row) < 6:
                        continue
                    
                    # Extraer datos
                    url = row[5] if len(row) > 5 else ""
                    company = row[1] if len(row) > 1 else ""
                    role = row[2] if len(row) > 2 else ""
                    
                    if url and url != "Unknown":
                        url_map[url].append({
                            "sheet": sheet_name,
                            "row": idx,
                            "company": company,
                            "role": role
                        })
                    
                    if company and role and company != "Unknown":
                        key = f"{company}|{role}"
                        company_role_map[key].append({
                            "sheet": sheet_name,
                            "row": idx,
                            "url": url
                        })
                    
                    all_jobs.append({
                        "sheet": sheet_name,
                        "row": idx,
                        "company": company,
                        "role": role,
                        "url": url
                    })
            
            # Encontrar duplicados por URL
            url_duplicates = []
            for url, jobs in url_map.items():
                if len(jobs) > 1:
                    url_duplicates.append({
                        "url": url,
                        "count": len(jobs),
                        "locations": jobs
                    })
                    print(f"  ⚠️  URL duplicada ({len(jobs)}x): {url}")
            
            # Encontrar duplicados por Company+Role
            company_role_duplicates = []
            for key, jobs in company_role_map.items():
                if len(jobs) > 1:
                    company, role = key.split("|")
                    company_role_duplicates.append({
                        "company": company,
                        "role": role,
                        "count": len(jobs),
                        "locations": jobs
                    })
                    print(f"  ⚠️  Company+Role duplicado ({len(jobs)}x): {company} - {role}")
            
            print(f"\n  📊 Total jobs: {len(all_jobs)}")
            print(f"  🔗 Duplicados por URL: {len(url_duplicates)}")
            print(f"  🏢 Duplicados por Company+Role: {len(company_role_duplicates)}")
            
            return {
                "status": "OK" if len(url_duplicates) == 0 and len(company_role_duplicates) == 0 else "WARNING",
                "total_jobs": len(all_jobs),
                "url_duplicates": url_duplicates,
                "company_role_duplicates": company_role_duplicates,
                "duplicate_count_by_url": len(url_duplicates),
                "duplicate_count_by_company_role": len(company_role_duplicates)
            }
            
        except Exception as e:
            print(f"  ❌ Error buscando duplicados: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "total_jobs": 0,
                "url_duplicates": [],
                "company_role_duplicates": []
            }
    
    def check_blacklist(self) -> Dict:
        """Verifica estado de la blacklist"""
        print("\n🚫 Verificando BLACKLIST...")
        
        try:
            result = self.sheet_manager.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range="BLACKLIST!A2:F1000"
            ).execute()
            
            rows = result.get('values', [])
            jobs_count = len(rows)
            
            print(f"  📊 Jobs en blacklist: {jobs_count}")
            
            return {
                "status": "OK",
                "exists": True,
                "jobs_count": jobs_count
            }
        except Exception as e:
            print(f"  ⚠️  Error accediendo BLACKLIST: {str(e)}")
            return {
                "status": "WARNING",
                "exists": False,
                "jobs_count": 0,
                "error": str(e)
            }
    
    def check_recent_logs(self) -> Dict:
        """Verifica logs recientes"""
        print("\n📝 Verificando logs recientes...")
        
        logs_dir = self.project_root / "logs" / "powershell"
        
        if not logs_dir.exists():
            print(f"  ⚠️  Directorio de logs no existe: {logs_dir}")
            return {
                "status": "WARNING",
                "logs_found": False,
                "recent_logs": []
            }
        
        # Buscar archivos .log recientes
        log_files = list(logs_dir.glob("*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent_logs = []
        for log_file in log_files[:5]:  # Últimos 5 logs
            stat = log_file.stat()
            recent_logs.append({
                "file": log_file.name,
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
            print(f"  📄 {log_file.name} ({round(stat.st_size / 1024, 2)} KB)")
        
        return {
            "status": "OK",
            "logs_found": len(log_files) > 0,
            "recent_logs": recent_logs,
            "total_log_files": len(log_files)
        }
    
    def generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en hallazgos"""
        recommendations = []
        
        # Archivos críticos
        if self.health_report['checks'].get('critical_files', {}).get('missing_count', 0) > 0:
            recommendations.append("⚠️  CRÍTICO: Archivos faltantes. Ejecutar setup inicial.")
        
        # Directorios
        if self.health_report['checks'].get('directory_structure', {}).get('missing_count', 0) > 0:
            recommendations.append("⚠️  Crear directorios faltantes con start_all.ps1")
        
        # Conexión Sheets
        if not self.health_report['checks'].get('sheets_connection', {}).get('connected', False):
            recommendations.append("🔥 CRÍTICO: No hay conexión a Google Sheets. Verificar credenciales.")
        
        # Duplicados
        dup_check = self.health_report.get('duplicates', {})
        url_dups = dup_check.get('duplicate_count_by_url', 0)
        company_dups = dup_check.get('duplicate_count_by_company_role', 0)
        
        if url_dups > 0:
            recommendations.append(f"🧹 Ejecutar job_cleaner.py para eliminar {url_dups} duplicados por URL")
        
        if company_dups > 0:
            recommendations.append(f"🔍 Revisar {company_dups} posibles duplicados por Company+Role")
        
        # Si todo está bien
        if not recommendations:
            recommendations.append("✅ Sistema funcionando correctamente. No se requieren acciones.")
        
        return recommendations
    
    def run_full_check(self) -> Dict:
        """Ejecuta verificación completa del sistema"""
        print("="*60)
        print("🏥 AI JOB FOUNDRY - SYSTEM HEALTH CHECK")
        print("="*60)
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar todas las verificaciones
        self.health_report['checks']['critical_files'] = self.check_critical_files()
        self.health_report['checks']['directory_structure'] = self.check_directory_structure()
        self.health_report['checks']['sheets_connection'] = self.check_sheets_connection()
        self.health_report['duplicates'] = self.find_duplicate_jobs()
        self.health_report['checks']['blacklist'] = self.check_blacklist()
        self.health_report['checks']['recent_logs'] = self.check_recent_logs()
        
        # Generar recomendaciones
        self.health_report['recommendations'] = self.generate_recommendations()
        
        # Determinar estado general
        all_ok = all([
            self.health_report['checks']['critical_files']['status'] == 'OK',
            self.health_report['checks']['directory_structure']['status'] == 'OK',
            self.health_report['checks']['sheets_connection']['status'] == 'OK'
        ])
        
        self.health_report['system_status'] = "HEALTHY" if all_ok else "NEEDS_ATTENTION"
        
        return self.health_report
    
    def print_report(self):
        """Imprime reporte en consola"""
        print("\n" + "="*60)
        print(f"📊 ESTADO DEL SISTEMA: {self.health_report['system_status']}")
        print("="*60)
        
        print("\n🎯 RECOMENDACIONES:")
        for rec in self.health_report['recommendations']:
            print(f"  {rec}")
        
        print("\n" + "="*60)
        print(f"📁 Reporte completo guardado en: logs/health_check_*.json")
        print("="*60 + "\n")
    
    def save_report(self):
        """Guarda reporte en archivo"""
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar JSON
        json_path = logs_dir / f"health_check_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.health_report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON guardado: {json_path}")
        
        # Guardar TXT legible
        txt_path = logs_dir / f"health_check_{timestamp}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("AI JOB FOUNDRY - SYSTEM HEALTH CHECK\n")
            f.write("="*60 + "\n\n")
            f.write(f"Timestamp: {self.health_report['timestamp']}\n")
            f.write(f"System Status: {self.health_report['system_status']}\n\n")
            
            f.write("RECOMMENDATIONS:\n")
            for rec in self.health_report['recommendations']:
                f.write(f"  {rec}\n")
            
            f.write("\n" + "="*60 + "\n")
        
        print(f"📄 TXT guardado: {txt_path}")


def main():
    checker = SystemHealthChecker()
    checker.run_full_check()
    checker.print_report()
    checker.save_report()


if __name__ == "__main__":
    main()
