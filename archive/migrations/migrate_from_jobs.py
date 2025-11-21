"""
MIGRATE FROM JOBS - Migración automática del proyecto Jobs/
Unifica todo en ai-job-foundry
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class JobsMigrator:
    def __init__(self):
        self.desktop = Path.home() / "Desktop"
        self.jobs_dir = self.desktop / "Jobs"
        self.foundry_dir = self.desktop / "ai-job-foundry"
        
        self.migration_log = []
    
    def log(self, message, level="INFO"):
        """Log de migración"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.migration_log.append(log_entry)
        
        icon = "✅" if level == "OK" else "⚠️" if level == "WARN" else "ℹ️"
        print(f"{icon} {message}")
    
    def verify_structure(self):
        """Verifica que existan ambas carpetas"""
        if not self.jobs_dir.exists():
            self.log("Carpeta Jobs/ no encontrada", "ERROR")
            return False
        
        if not self.foundry_dir.exists():
            self.log("Carpeta ai-job-foundry/ no encontrada", "ERROR")
            return False
        
        self.log("Estructura verificada", "OK")
        return True
    
    def migrate_config(self):
        """Crea configuración unificada"""
        self.log("Creando configuración unificada...")
        
        # Buscar ID de Sheet en Jobs/
        sheet_id = None
        for script in ['ingest_email_to_sheet_v2.py', 'enrich_sheet_with_llm_v3.py']:
            script_path = self.jobs_dir / script
            if script_path.exists():
                content = script_path.read_text(encoding='utf-8')
                # Buscar SPREADSHEET_ID
                import re
                match = re.search(r'SPREADSHEET_ID\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    sheet_id = match.group(1)
                    break
        
        config = {
            "gmail": {
                "enabled": True,
                "check_interval_minutes": 30
            },
            "llm": {
                "provider": "ollama",  # Tu setup actual
                "endpoint": "http://172.23.0.1:11434/v1",
                "model": "qwen2.5-14b-instruct"
            },
            "sheets": {
                "spreadsheet_id": sheet_id or "TU_SHEET_ID",
                "ingestion_sheet": "Registry",
                "tracking_sheet": "Applications"
            },
            "tracking": {
                "auto_detect_interviews": True,
                "reminder_hours_before": 2
            },
            "migrated_from": "Jobs/",
            "migration_date": datetime.now().isoformat()
        }
        
        config_file = self.foundry_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log(f"Configuración guardada: {config_file}", "OK")
        return config
    
    def migrate_data(self):
        """Migra archivos de datos"""
        self.log("Migrando datos...")
        
        files_to_migrate = {
            "cv_descriptor.txt": "data/",
            "token.json": "data/credentials/",
            "model_memory/profile.json": "data/model_memory/",
            "state/seen_ids.json": "data/state/"
        }
        
        migrated = 0
        for source, dest_dir in files_to_migrate.items():
            source_path = self.jobs_dir / source
            if source_path.exists():
                dest_path = self.foundry_dir / dest_dir / source_path.name
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_path, dest_path)
                self.log(f"Copiado: {source} → {dest_dir}", "OK")
                migrated += 1
            else:
                self.log(f"No encontrado: {source}", "WARN")
        
        return migrated
    
    def create_unified_runner(self):
        """Crea script unificado de ejecución"""
        self.log("Creando runner unificado...")
        
        runner_script = '''"""
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
    print("\\n🔽 Ejecutando ingesta...")
    try:
        from ingest_email_to_sheet_v2 import main as ingest_main
        ingest_main()
        print("✅ Ingesta completada")
    except Exception as e:
        print(f"❌ Error en ingesta: {e}")

def run_enrichment():
    """Ejecuta enriquecimiento con IA"""
    print("\\n🤖 Ejecutando enriquecimiento...")
    try:
        from enrich_sheet_with_llm_v3 import main as enrich_main
        enrich_main()
        print("✅ Enriquecimiento completado")
    except Exception as e:
        print(f"❌ Error en enriquecimiento: {e}")

def run_tracking():
    """Ejecuta tracking de aplicaciones"""
    print("\\n🎯 Ejecutando tracking...")
    try:
        from job_tracker import JobTracker
        tracker = JobTracker()
        tracker.check_gmail_for_responses()
        print("✅ Tracking completado")
    except Exception as e:
        print(f"❌ Error en tracking: {e}")

def run_full_pipeline():
    """Ejecuta pipeline completo"""
    print("\\n" + "="*60)
    print("  🚀 PIPELINE COMPLETO")
    print("="*60)
    
    run_ingestion()
    time.sleep(5)
    
    run_enrichment()
    time.sleep(5)
    
    run_tracking()
    
    print("\\n✅ Pipeline completado\\n")

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
        print("Presiona Ctrl+C para detener\\n")
        
        schedule.every(args.interval).minutes.do(run_full_pipeline)
        
        # Primera ejecución inmediata
        run_full_pipeline()
        
        # Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\\n\\n🛑 Detenido por usuario")
'''
        
        runner_path = self.foundry_dir / "run_unified.py"
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(runner_script)
        
        self.log(f"Runner creado: {runner_path}", "OK")
    
    def update_scripts(self):
        """Actualiza rutas en scripts migrados"""
        self.log("Actualizando rutas en scripts...")
        
        scripts_to_update = [
            "core/ingestion/ingest_email_to_sheet_v2.py",
            "core/enrichment/enrich_sheet_with_llm_v3.py"
        ]
        
        replacements = {
            'token.json': '../data/credentials/token.json',
            'cv_descriptor.txt': '../data/cv_descriptor.txt',
            'model_memory/profile.json': '../data/model_memory/profile.json'
        }
        
        for script_path in scripts_to_update:
            full_path = self.foundry_dir / script_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                
                for old, new in replacements.items():
                    content = content.replace(f'"{old}"', f'"{new}"')
                    content = content.replace(f"'{old}'", f"'{new}'")
                
                full_path.write_text(content, encoding='utf-8')
                self.log(f"Actualizado: {script_path}", "OK")
    
    def create_readme(self):
        """Crea README actualizado"""
        readme = f"""# AI Job Foundry - Sistema Unificado

**Fecha de unificación:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🎯 Sistema Completo

Este proyecto unifica:
- **Pipeline de Jobs/** (ingesta + enriquecimiento IA)
- **Job Tracker** (seguimiento de aplicaciones)
- **Interview Copilot** (asistente de entrevistas)

## 📁 Estructura

```
ai-job-foundry/
├── core/
│   ├── ingestion/          # Gmail → Sheets
│   ├── enrichment/         # IA → Análisis
│   └── tracking/           # Seguimiento
├── data/
│   ├── cv_descriptor.txt   # Tu CV
│   └── credentials/        # OAuth tokens
├── run_unified.py          # Ejecutor principal
└── config.json             # Configuración
```

## 🚀 Uso Rápido

### Ejecución única:
```bash
py run_unified.py
```

### Ejecución programada (cada 30 min):
```bash
py run_unified.py --mode schedule --interval 30
```

### Componentes individuales:
```bash
# Solo tracker
py job_tracker.py check

# Solo dashboard
py run_dashboard.py

# Interview Copilot
py interview_copilot_simple.py
```

## 🔧 Configuración

Edita `config.json` para:
- Cambiar Sheet ID
- Ajustar endpoint de IA
- Configurar intervalos

## 📊 Dashboard

Abre en navegador:
```
http://localhost:8000/dashboard.html
```

## 🎙️ Interview Copilot

Antes de entrevista:
1. Edita empresa/posición en `interview_copilot_simple.py`
2. Ejecuta: `py interview_copilot_simple.py`
3. Posiciona ventana donde NO aparezca en cámara

## 📝 Migrado desde Jobs/

- ✅ Scripts de ingesta
- ✅ Enriquecimiento con LM Studio
- ✅ Análisis de fit
- ✅ Memoria de IA
- ✅ CV y credenciales

---

**Autor:** Marcos Alvarado
**Repositorio:** github.com/MarcosAlvaradoD/ai-job-foundry
"""
        
        readme_path = self.foundry_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        self.log("README actualizado", "OK")
    
    def save_log(self):
        """Guarda log de migración"""
        log_file = self.foundry_dir / f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("AI JOB FOUNDRY - LOG DE MIGRACIÓN\n")
            f.write("="*60 + "\n\n")
            for entry in self.migration_log:
                f.write(entry + "\n")
        
        self.log(f"Log guardado: {log_file}", "OK")
    
    def run(self):
        """Ejecuta migración completa"""
        print("\n" + "="*60)
        print("  🔄 MIGRACIÓN: Jobs/ → ai-job-foundry")
        print("="*60 + "\n")
        
        if not self.verify_structure():
            return False
        
        # Migración paso a paso
        config = self.migrate_config()
        migrated_files = self.migrate_data()
        self.create_unified_runner()
        self.update_scripts()
        self.create_readme()
        self.save_log()
        
        print("\n" + "="*60)
        print("  ✅ MIGRACIÓN COMPLETADA")
        print("="*60)
        print(f"\n  📊 Archivos migrados: {migrated_files}")
        print(f"  📁 Ubicación: {self.foundry_dir}")
        print(f"\n  🚀 Siguiente paso:")
        print(f"     py run_unified.py")
        print("\n" + "="*60 + "\n")
        
        return True

if __name__ == "__main__":
    migrator = JobsMigrator()
    success = migrator.run()
    
    if not success:
        print("\n❌ Migración fallida. Revisa los logs.")
        exit(1)