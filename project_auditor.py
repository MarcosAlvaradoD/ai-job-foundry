"""
PROJECT AUDITOR - Análisis completo de la estructura del proyecto
Escanea todas las carpetas, detecta código, configuraciones y genera reporte
"""

import os
import json
from pathlib import Path
from datetime import datetime
import hashlib

class ProjectAuditor:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.report = {
            "scan_date": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "folders": {},
            "files_by_type": {},
            "total_files": 0,
            "total_size_mb": 0,
            "dependencies": set(),
            "issues": [],
            "recommendations": []
        }
    
    def scan_directory(self, path, max_depth=5, current_depth=0):
        """Escanea recursivamente un directorio"""
        if current_depth > max_depth:
            return
        
        try:
            folder_info = {
                "path": str(path),
                "files": [],
                "subfolders": [],
                "total_files": 0,
                "total_size": 0,
                "file_types": {}
            }
            
            for item in path.iterdir():
                if item.is_file():
                    file_info = self.analyze_file(item)
                    folder_info["files"].append(file_info)
                    folder_info["total_files"] += 1
                    folder_info["total_size"] += file_info["size"]
                    
                    # Contar por tipo
                    ext = file_info["extension"]
                    folder_info["file_types"][ext] = folder_info["file_types"].get(ext, 0) + 1
                    
                elif item.is_dir() and not item.name.startswith('.'):
                    subfolder_info = self.scan_directory(item, max_depth, current_depth + 1)
                    if subfolder_info:
                        folder_info["subfolders"].append(subfolder_info)
            
            self.report["folders"][str(path)] = folder_info
            return folder_info
        
        except PermissionError:
            self.report["issues"].append(f"Sin permisos: {path}")
            return None
    
    def analyze_file(self, file_path):
        """Analiza un archivo individual"""
        stat = file_path.stat()
        
        file_info = {
            "name": file_path.name,
            "extension": file_path.suffix.lower(),
            "size": stat.st_size,
            "size_human": self.human_readable_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "full_path": str(file_path)
        }
        
        # Análisis específico por tipo
        if file_info["extension"] in ['.py', '.js', '.json', '.yaml', '.yml', '.txt', '.md']:
            file_info.update(self.analyze_code_file(file_path))
        
        # Actualizar estadísticas globales
        ext = file_info["extension"]
        if ext not in self.report["files_by_type"]:
            self.report["files_by_type"][ext] = []
        self.report["files_by_type"][ext].append(file_info)
        
        self.report["total_files"] += 1
        self.report["total_size_mb"] += stat.st_size / (1024 * 1024)
        
        return file_info
    
    def analyze_code_file(self, file_path):
        """Análisis específico para archivos de código"""
        analysis = {
            "lines": 0,
            "imports": [],
            "functions": [],
            "classes": [],
            "todos": [],
            "errors_found": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                analysis["lines"] = len(lines)
                
                # Detectar imports (Python y JS)
                for line in lines:
                    line = line.strip()
                    
                    # Python imports
                    if line.startswith('import ') or line.startswith('from '):
                        module = line.split()[1].split('.')[0]
                        analysis["imports"].append(module)
                        self.report["dependencies"].add(module)
                    
                    # JS/Node imports
                    elif 'require(' in line or 'import ' in line:
                        # Extraer nombre del módulo
                        if 'require(' in line:
                            start = line.find("require('") + 9
                            end = line.find("')", start)
                            if start > 8 and end > start:
                                module = line[start:end].split('/')[0]
                                analysis["imports"].append(module)
                                self.report["dependencies"].add(module)
                    
                    # Detectar funciones/clases (básico)
                    if line.startswith('def ') or line.startswith('async def '):
                        func_name = line.split('(')[0].replace('def ', '').replace('async ', '').strip()
                        analysis["functions"].append(func_name)
                    
                    if line.startswith('class '):
                        class_name = line.split('(')[0].replace('class ', '').strip(':')
                        analysis["classes"].append(class_name)
                    
                    # TODOs y FIXMEs
                    if 'TODO' in line.upper() or 'FIXME' in line.upper():
                        analysis["todos"].append(line.strip())
                
        except Exception as e:
            analysis["errors_found"].append(str(e))
        
        return analysis
    
    def human_readable_size(self, size):
        """Convierte bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def detect_project_type(self, folder_path):
        """Detecta qué tipo de proyecto es"""
        indicators = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "*.py"],
            "node": ["package.json", "node_modules", "*.js"],
            "n8n": ["workflows", ".n8n"],
            "docker": ["Dockerfile", "docker-compose.yml"],
            "git": [".git", ".gitignore"]
        }
        
        detected = []
        folder = Path(folder_path)
        
        for project_type, files in indicators.items():
            for pattern in files:
                if list(folder.glob(pattern)):
                    detected.append(project_type)
                    break
        
        return detected
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        recs = []
        
        # Revisar si hay muchos archivos repetidos
        for ext, files in self.report["files_by_type"].items():
            if len(files) > 10 and ext in ['.py', '.js']:
                recs.append(f"📦 Considera organizar los {len(files)} archivos {ext} en subcarpetas")
        
        # Revisar dependencias
        if len(self.report["dependencies"]) > 20:
            recs.append("📋 Crear/actualizar requirements.txt con todas las dependencias")
        
        # Revisar TODOs
        total_todos = sum(len(f.get("todos", [])) for files in self.report["files_by_type"].values() for f in files)
        if total_todos > 5:
            recs.append(f"✅ Hay {total_todos} TODOs pendientes - considera priorizarlos")
        
        # Revisar tamaño
        if self.report["total_size_mb"] > 500:
            recs.append("💾 Proyecto grande (>500MB) - considera usar .gitignore para excluir archivos pesados")
        
        self.report["recommendations"] = recs
    
    def generate_report(self, output_file="project_audit_report.json"):
        """Genera reporte completo en JSON"""
        # Convertir sets a listas para JSON
        self.report["dependencies"] = sorted(list(self.report["dependencies"]))
        
        # Generar recomendaciones
        self.generate_recommendations()
        
        # Guardar
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte guardado: {output_file}")
        return output_file
    
    def generate_markdown_report(self, output_file="PROJECT_AUDIT.md"):
        """Genera reporte legible en Markdown"""
        md = f"""# 📊 AUDITORÍA DE PROYECTO - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📁 Estructura General

**Ruta base:** `{self.report['base_path']}`
**Total de archivos:** {self.report['total_files']}
**Tamaño total:** {self.human_readable_size(self.report['total_size_mb'] * 1024 * 1024)}

## 📂 Carpetas Principales

"""
        
        # Listar carpetas principales
        for folder_path, info in self.report["folders"].items():
            if info["total_files"] > 0:
                md += f"\n### `{Path(folder_path).name}`\n"
                md += f"- **Archivos:** {info['total_files']}\n"
                md += f"- **Tamaño:** {self.human_readable_size(info['total_size'])}\n"
                
                if info["file_types"]:
                    md += f"- **Tipos:** "
                    md += ", ".join([f"{ext} ({count})" for ext, count in info["file_types"].items()])
                    md += "\n"
        
        # Archivos por tipo
        md += "\n## 📄 Distribución de Archivos\n\n"
        for ext, files in sorted(self.report["files_by_type"].items(), key=lambda x: len(x[1]), reverse=True):
            if ext:
                md += f"- **{ext}**: {len(files)} archivos\n"
        
        # Dependencias
        if self.report["dependencies"]:
            md += "\n## 📦 Dependencias Detectadas\n\n"
            md += "```\n"
            for dep in sorted(self.report["dependencies"]):
                md += f"{dep}\n"
            md += "```\n"
        
        # Recomendaciones
        if self.report["recommendations"]:
            md += "\n## 💡 Recomendaciones\n\n"
            for rec in self.report["recommendations"]:
                md += f"- {rec}\n"
        
        # Issues
        if self.report["issues"]:
            md += "\n## ⚠️ Problemas Detectados\n\n"
            for issue in self.report["issues"]:
                md += f"- {issue}\n"
        
        # Guardar
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"✅ Reporte Markdown guardado: {output_file}")
        return output_file


# EJECUCIÓN
if __name__ == "__main__":
    import sys
    
    print("""
    🔍 PROJECT AUDITOR
    ==================
    
    Este script escaneará toda tu estructura de proyecto y generará:
    1. Reporte JSON completo (project_audit_report.json)
    2. Reporte Markdown legible (PROJECT_AUDIT.md)
    
    Uso:
    python project_auditor.py [ruta]
    
    Si no especificas ruta, escaneará el escritorio actual.
    """)
    
    # Determinar ruta base
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        # Por defecto: Escritorio
        base_path = Path.home() / "Desktop"
    
    print(f"\n📁 Escaneando: {base_path}\n")
    
    # Crear auditor
    auditor = ProjectAuditor(base_path)
    
    # Escanear carpetas específicas
    folders_to_scan = ["dev", "Jobs", "job_apply_mvp_v4"]
    
    for folder_name in folders_to_scan:
        folder_path = Path(base_path) / folder_name
        if folder_path.exists():
            print(f"  📂 Escaneando: {folder_name}...")
            auditor.scan_directory(folder_path)
            
            # Detectar tipo de proyecto
            project_types = auditor.detect_project_type(folder_path)
            if project_types:
                print(f"     Tipo detectado: {', '.join(project_types)}")
        else:
            print(f"  ⚠️  No encontrado: {folder_name}")
    
    print("\n📊 Generando reportes...\n")
    
    # Generar reportes
    auditor.generate_report()
    auditor.generate_markdown_report()
    
    print("""
    ✅ AUDITORÍA COMPLETADA
    
    Revisa los archivos:
    - project_audit_report.json (datos completos)
    - PROJECT_AUDIT.md (resumen legible)
    
    Siguiente paso: Revisa el reporte y compártelo conmigo para continuar.
    """)