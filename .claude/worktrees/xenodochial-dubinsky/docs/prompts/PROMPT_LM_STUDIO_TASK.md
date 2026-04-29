# 🎯 PROMPT PARA LM STUDIO - TAREA ESPECÍFICA Y EVALUABLE

**Proyecto:** AI Job Foundry  
**Tarea:** Crear Sistema de Verificación de Duplicados + Health Check  
**Objetivo:** Evaluar capacidad de LM Studio para desarrollo autónomo

---

## 📋 CONTEXTO DEL PROYECTO

Estás trabajando en **AI Job Foundry**, un sistema automatizado de búsqueda de empleo que:
- Scrapea ofertas de LinkedIn, Indeed, Glassdoor
- Procesa emails de reclutadores  
- Analiza match con AI (FIT scores 0-10)
- Guarda todo en Google Sheets
- Aplica automáticamente a ofertas

**Ubicación del proyecto:**  
`C:\Users\MSI\Desktop\ai-job-foundry`

**Estructura clave:**
```
ai-job-foundry/
├── core/
│   ├── sheets/
│   │   └── sheet_manager.py          # Gestor de Google Sheets
│   ├── jobs_pipeline/
│   │   ├── job_cleaner.py           # Limpieza automática (RECIÉN CREADO)
│   │   └── update_resumen.py        # Actualizar Resumen (RECIÉN CREADO)
│   ├── ingestion/                   # Scrapers (LinkedIn, Indeed)
│   ├── enrichment/                  # AI analyzer
│   └── automation/                  # Gmail monitor
├── data/
│   ├── state/
│   │   └── job_blacklist.json       # Blacklist temporal (30 días)
│   └── credentials/                 # OAuth tokens
├── logs/                            # Session logs
└── docs/                            # Documentación
```

**Google Sheets ID:** `1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg`

**Pestañas en Sheets:**
- **Jobs** (10 ofertas) - Vista consolidada principal
- **Registry** (16 ofertas) - Backup histórico  
- **LinkedIn** (37 ofertas) - Ofertas de LinkedIn
- **Indeed** (11 ofertas) - Ofertas de Indeed
- **Glassdoor** (11 ofertas) - Ofertas de Glassdoor
- **Resumen** - Dashboard de estadísticas (RECIÉN CREADO)

**Total jobs:** 74 ofertas en el sistema

---

## 🎯 TU TAREA ESPECÍFICA

Debes crear un **SISTEMA DE HEALTH CHECK Y VERIFICACIÓN DE DUPLICADOS** que:

### **1. Verifica duplicados en Google Sheets** 🔍
- Lee TODAS las pestañas (Jobs, LinkedIn, Indeed, Glassdoor)
- Detecta jobs duplicados por URL (ApplyURL)
- Identifica duplicados por Company + Role
- Genera lista de duplicados encontrados

### **2. Ejecuta Health Check del sistema** 🏥
- Verifica archivos críticos existen
- Comprueba conexión a Google Sheets
- Revisa blacklist (data/state/job_blacklist.json)
- Valida logs recientes
- Chequea estructura de directorios

### **3. Genera reporte completo** 📊
- Estadísticas de duplicados
- Estado del sistema (✅/⚠️/❌)
- Recomendaciones de acción
- Guarda en archivo de texto y JSON

---

## 📝 ESPECIFICACIONES TÉCNICAS DETALLADAS

### **Archivo a crear:** `core/jobs_pipeline/system_health_check.py`

### **Estructura del script:**

```python
"""
AI JOB FOUNDRY - System Health Check & Duplicate Verifier
Verifica estado del sistema y detecta jobs duplicados

Autor: LM Studio (Qwen 2.5 14B)
Fecha: 2025-11-21
Tarea asignada por: Marcos Alvarado
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
        critical_files = [
            ".env",
            "core/sheets/sheet_manager.py",
            "core/jobs_pipeline/job_cleaner.py",
            "core/jobs_pipeline/update_resumen.py",
            "data/credentials/token.json",
            "data/credentials/credentials.json"
        ]
        
        results = {}
        for file_path in critical_files:
            full_path = self.project_root / file_path
            results[file_path] = {
                "exists": full_path.exists(),
                "readable": full_path.exists() and os.access(full_path, os.R_OK)
            }
        
        return results
    
    def check_directory_structure(self) -> Dict:
        """Verifica estructura de directorios"""
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
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            results[dir_path] = full_path.exists() and full_path.is_dir()
        
        return results
    
    def check_sheets_connection(self) -> Dict:
        """Verifica conexión a Google Sheets"""
        try:
            # Try to read Jobs tab
            result = self.sheet_manager.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range="Jobs!A1:A1"
            ).execute()
            
            return {
                "connected": True,
                "error": None,
                "spreadsheet_id": self.spreadsheet_id
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "spreadsheet_id": self.spreadsheet_id
            }
    
    def find_duplicate_jobs(self) -> Dict:
        """Encuentra jobs duplicados en todas las pestañas"""
        tabs = ["Jobs", "LinkedIn", "Indeed", "Glassdoor"]
        
        all_jobs = []
        urls_seen = defaultdict(list)
        company_role_seen = defaultdict(list)
        
        for tab_name in tabs:
            try:
                result = self.sheet_manager.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{tab_name}!A1:Z1000"
                ).execute()
                
                values = result.get('values', [])
                if not values:
                    continue
                
                headers = values[0]
                for idx, row in enumerate(values[1:], start=2):
                    row_data = row + [''] * (len(headers) - len(row))
                    job = dict(zip(headers, row_data))
                    job['_tab'] = tab_name
                    job['_row'] = idx
                    
                    # Track by URL
                    url = job.get('ApplyURL', '')
                    if url:
                        urls_seen[url].append({
                            'tab': tab_name,
                            'row': idx,
                            'company': job.get('Company', 'Unknown'),
                            'role': job.get('Role', 'Unknown')
                        })
                    
                    # Track by Company + Role
                    company = job.get('Company', '')
                    role = job.get('Role', '')
                    if company and role:
                        key = f"{company}||{role}"
                        company_role_seen[key].append({
                            'tab': tab_name,
                            'row': idx,
                            'url': url
                        })
                    
                    all_jobs.append(job)
            
            except Exception as e:
                print(f"⚠️  Error reading {tab_name}: {e}")
                continue
        
        # Find duplicates
        url_duplicates = {url: jobs for url, jobs in urls_seen.items() if len(jobs) > 1}
        company_role_duplicates = {key: jobs for key, jobs in company_role_seen.items() if len(jobs) > 1}
        
        return {
            "total_jobs": len(all_jobs),
            "url_duplicates": url_duplicates,
            "company_role_duplicates": company_role_duplicates,
            "duplicate_count_by_url": len(url_duplicates),
            "duplicate_count_by_company_role": len(company_role_duplicates)
        }
    
    def check_blacklist(self) -> Dict:
        """Verifica estado de la blacklist"""
        blacklist_file = self.project_root / "data/state/job_blacklist.json"
        
        if not blacklist_file.exists():
            return {
                "exists": False,
                "jobs_count": 0,
                "last_cleanup": None
            }
        
        try:
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
            
            return {
                "exists": True,
                "jobs_count": len(blacklist.get('jobs', [])),
                "last_cleanup": blacklist.get('last_cleanup', 'Never')
            }
        except Exception as e:
            return {
                "exists": True,
                "jobs_count": 0,
                "error": str(e)
            }
    
    def check_recent_logs(self) -> Dict:
        """Verifica logs recientes"""
        logs_dir = self.project_root / "logs/powershell"
        
        if not logs_dir.exists():
            return {
                "logs_found": False,
                "recent_logs": []
            }
        
        log_files = list(logs_dir.glob("daily_cleanup_*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent_logs = []
        for log_file in log_files[:5]:  # Last 5 logs
            recent_logs.append({
                "filename": log_file.name,
                "size_bytes": log_file.stat().st_size,
                "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            })
        
        return {
            "logs_found": True,
            "total_logs": len(log_files),
            "recent_logs": recent_logs
        }
    
    def generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en hallazgos"""
        recommendations = []
        
        # Check duplicates
        if self.health_report['duplicates'].get('duplicate_count_by_url', 0) > 0:
            recommendations.append(
                f"⚠️  Se encontraron {self.health_report['duplicates']['duplicate_count_by_url']} "
                f"URLs duplicadas. Considera ejecutar deduplicación."
            )
        
        # Check blacklist size
        blacklist_count = self.health_report['checks'].get('blacklist', {}).get('jobs_count', 0)
        if blacklist_count > 20:
            recommendations.append(
                f"⚠️  Blacklist tiene {blacklist_count} jobs. "
                f"Considera limpiar jobs con más de 30 días."
            )
        
        # Check sheets connection
        if not self.health_report['checks'].get('sheets', {}).get('connected', False):
            recommendations.append(
                "❌ Error de conexión a Google Sheets. "
                "Verifica credenciales en data/credentials/"
            )
        
        if not recommendations:
            recommendations.append("✅ Sistema funcionando correctamente. No se requieren acciones.")
        
        return recommendations
    
    def run_full_check(self) -> Dict:
        """Ejecuta verificación completa del sistema"""
        print("\n" + "="*70)
        print("🏥 AI JOB FOUNDRY - SYSTEM HEALTH CHECK")
        print("="*70 + "\n")
        
        # 1. Check critical files
        print("1️⃣  Verificando archivos críticos...")
        self.health_report['checks']['files'] = self.check_critical_files()
        files_ok = all(f['exists'] for f in self.health_report['checks']['files'].values())
        print(f"   {'✅' if files_ok else '❌'} Archivos críticos\n")
        
        # 2. Check directory structure
        print("2️⃣  Verificando estructura de directorios...")
        self.health_report['checks']['directories'] = self.check_directory_structure()
        dirs_ok = all(self.health_report['checks']['directories'].values())
        print(f"   {'✅' if dirs_ok else '❌'} Estructura de directorios\n")
        
        # 3. Check Sheets connection
        print("3️⃣  Verificando conexión a Google Sheets...")
        self.health_report['checks']['sheets'] = self.check_sheets_connection()
        sheets_ok = self.health_report['checks']['sheets']['connected']
        print(f"   {'✅' if sheets_ok else '❌'} Conexión a Sheets\n")
        
        # 4. Find duplicates
        print("4️⃣  Buscando duplicados en Sheets...")
        self.health_report['duplicates'] = self.find_duplicate_jobs()
        dup_count = self.health_report['duplicates']['duplicate_count_by_url']
        print(f"   {'⚠️' if dup_count > 0 else '✅'} Duplicados encontrados: {dup_count}\n")
        
        # 5. Check blacklist
        print("5️⃣  Verificando blacklist...")
        self.health_report['checks']['blacklist'] = self.check_blacklist()
        blacklist_ok = self.health_report['checks']['blacklist']['exists']
        print(f"   {'✅' if blacklist_ok else '⚠️'} Blacklist\n")
        
        # 6. Check recent logs
        print("6️⃣  Verificando logs recientes...")
        self.health_report['checks']['logs'] = self.check_recent_logs()
        logs_ok = self.health_report['checks']['logs']['logs_found']
        print(f"   {'✅' if logs_ok else '⚠️'} Logs recientes\n")
        
        # 7. Generate recommendations
        print("7️⃣  Generando recomendaciones...")
        self.health_report['recommendations'] = self.generate_recommendations()
        print("   ✅ Recomendaciones generadas\n")
        
        # Determine overall status
        if files_ok and dirs_ok and sheets_ok and dup_count == 0:
            self.health_report['system_status'] = "HEALTHY"
        elif sheets_ok:
            self.health_report['system_status'] = "WARNING"
        else:
            self.health_report['system_status'] = "ERROR"
        
        return self.health_report
    
    def print_report(self):
        """Imprime reporte en consola"""
        print("\n" + "="*70)
        print("📊 REPORTE DE SALUD DEL SISTEMA")
        print("="*70 + "\n")
        
        status_emoji = {
            "HEALTHY": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        
        print(f"Status General: {status_emoji[self.health_report['system_status']]} "
              f"{self.health_report['system_status']}")
        print(f"Timestamp: {self.health_report['timestamp']}")
        print()
        
        # Duplicates summary
        print("📋 DUPLICADOS:")
        print(f"   - Por URL: {self.health_report['duplicates']['duplicate_count_by_url']}")
        print(f"   - Por Company+Role: {self.health_report['duplicates']['duplicate_count_by_company_role']}")
        print(f"   - Total jobs: {self.health_report['duplicates']['total_jobs']}")
        print()
        
        # Recommendations
        print("💡 RECOMENDACIONES:")
        for rec in self.health_report['recommendations']:
            print(f"   {rec}")
        print()
        
        print("="*70)
    
    def save_report(self):
        """Guarda reporte en archivo"""
        # Save JSON
        json_file = self.project_root / f"logs/health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.health_report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte guardado en: {json_file}")
        
        # Save TXT
        txt_file = json_file.with_suffix('.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("AI JOB FOUNDRY - SYSTEM HEALTH CHECK REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Timestamp: {self.health_report['timestamp']}\n")
            f.write(f"Status: {self.health_report['system_status']}\n\n")
            
            f.write("DUPLICADOS:\n")
            f.write(f"  - Por URL: {self.health_report['duplicates']['duplicate_count_by_url']}\n")
            f.write(f"  - Por Company+Role: {self.health_report['duplicates']['duplicate_count_by_company_role']}\n\n")
            
            f.write("RECOMENDACIONES:\n")
            for rec in self.health_report['recommendations']:
                f.write(f"  {rec}\n")
        
        print(f"💾 Reporte TXT guardado en: {txt_file}")
        print()


def main():
    """Función principal"""
    checker = SystemHealthChecker()
    checker.run_full_check()
    checker.print_report()
    checker.save_report()


if __name__ == "__main__":
    main()
```

---

## ✅ CRITERIOS DE ÉXITO (CHECKLIST DE EVALUACIÓN)

### **Funcionalidad:**
- [ ] Script se ejecuta sin errores
- [ ] Lee todas las pestañas de Google Sheets correctamente
- [ ] Detecta duplicados por URL
- [ ] Detecta duplicados por Company+Role
- [ ] Verifica archivos críticos
- [ ] Verifica directorios
- [ ] Comprueba conexión a Sheets
- [ ] Revisa blacklist
- [ ] Chequea logs

### **Output:**
- [ ] Imprime reporte legible en consola
- [ ] Guarda reporte en JSON
- [ ] Guarda reporte en TXT
- [ ] Status general correcto (HEALTHY/WARNING/ERROR)
- [ ] Recomendaciones útiles y accionables

### **Código:**
- [ ] Bien estructurado (clases, métodos)
- [ ] Docstrings en español
- [ ] Manejo de errores con try/except
- [ ] Type hints donde sea posible
- [ ] Código limpio y legible

### **Extras (Bonus):**
- [ ] Logging detallado
- [ ] Progress indicators
- [ ] Colores en consola (opcional)
- [ ] Tests unitarios (opcional)

---

## 🧪 CÓMO PROBAR TU CÓDIGO

```powershell
cd C:\Users\MSI\Desktop\ai-job-foundry
py core\jobs_pipeline\system_health_check.py
```

**Output esperado:**
```
======================================================================
🏥 AI JOB FOUNDRY - SYSTEM HEALTH CHECK
======================================================================

1️⃣  Verificando archivos críticos...
   ✅ Archivos críticos

2️⃣  Verificando estructura de directorios...
   ✅ Estructura de directorios

3️⃣  Verificando conexión a Google Sheets...
   ✅ Conexión a Sheets

4️⃣  Buscando duplicados en Sheets...
   ⚠️ Duplicados encontrados: X

5️⃣  Verificando blacklist...
   ✅ Blacklist

6️⃣  Verificando logs recientes...
   ✅ Logs recientes

7️⃣  Generando recomendaciones...
   ✅ Recomendaciones generadas

======================================================================
📊 REPORTE DE SALUD DEL SISTEMA
======================================================================

Status General: ⚠️ WARNING
Timestamp: 2025-11-21T02:30:00

📋 DUPLICADOS:
   - Por URL: X
   - Por Company+Role: Y
   - Total jobs: 74

💡 RECOMENDACIONES:
   ⚠️  Se encontraron X URLs duplicadas. Considera ejecutar deduplicación.
   ✅ Sistema funcionando correctamente.

======================================================================

💾 Reporte guardado en: logs/health_check_20251121_023000.json
💾 Reporte TXT guardado en: logs/health_check_20251121_023000.txt
```

---

## 📚 RECURSOS DISPONIBLES

**MCPs habilitados:**
- ✅ `filesystem` - Leer/escribir archivos en `C:\Users\MSI\Desktop\ai-job-foundry`
- ✅ `fetch` - Hacer requests HTTP
- ✅ `playwright` - Navegación web (si necesitas)
- ⚠️ `searxng` - NO funciona (ignorar)

**Herramientas de filesystem:**
- `read_file` - Leer archivos
- `write_file` - Escribir archivos
- `create_directory` - Crear directorios
- `list_directory` - Listar contenidos
- `move_file` - Mover/renombrar
- `search_files` - Buscar archivos

**Módulos Python disponibles:**
- pathlib, json, datetime, typing, collections
- dotenv (load_dotenv)
- google-api-python-client (para Sheets)
- requests (para HTTP)

---

## 🎯 TU MISIÓN

1. **Lee este prompt completamente**
2. **Crea el archivo exacto:** `core/jobs_pipeline/system_health_check.py`
3. **Implementa TODAS las funciones descritas**
4. **Prueba tu código** ejecutándolo
5. **Genera los reportes** (JSON + TXT)
6. **Confirma que funciona** sin errores

---

## 📊 EVALUACIÓN

Marcos va a evaluar tu código basándose en:
1. ✅ **Funcionalidad** (40 pts) - ¿Hace lo que debe?
2. 🎨 **Calidad de código** (30 pts) - ¿Está bien escrito?
3. 📝 **Documentación** (15 pts) - ¿Tiene docstrings?
4. 🐛 **Manejo de errores** (15 pts) - ¿No crashea?
5. 🎁 **Extras** (Bonus +10 pts) - Features adicionales

**Puntaje mínimo para aprobar:** 70/100

---

## ⏰ TIEMPO ESTIMADO

- Lectura del prompt: 10 minutos
- Implementación: 30-45 minutos
- Testing: 10 minutos
- **Total:** ~1 hora

---

## 🚀 ¡ADELANTE!

**Recuerda:**
- Usa los MCPs (filesystem) para leer/escribir
- Importa `SheetManager` desde `core.sheets.sheet_manager`
- Guarda reportes en `logs/`
- Maneja errores con try/except
- Imprime progress mientras trabajas

**¡BUENA SUERTE!** 🎉

---

**Creado por:** Marcos Alvarado + Claude (Sonnet 4)  
**Fecha:** 2025-11-21  
**Versión:** 1.0  
**Para:** LM Studio (Qwen 2.5 14B) + MCP Filesystem
