"""
HANDLE LARGE FILES - Analizar y comprimir archivos grandes
Para archivos que no caben en el chat
"""

import json
import os
from pathlib import Path
from datetime import datetime

def analyze_large_json(file_path):
    """Analiza un archivo JSON grande sin cargarlo completo en memoria"""
    
    file_path = Path(file_path)
    file_size = file_path.stat().st_size
    
    print(f"\n📄 Analizando: {file_path.name}")
    print(f"💾 Tamaño: {file_size / (1024*1024):.2f} MB\n")
    
    # Leer en chunks
    with open(file_path, 'r', encoding='utf-8') as f:
        # Leer primeras líneas
        first_lines = []
        for i in range(20):
            line = f.readline()
            if not line:
                break
            first_lines.append(line)
        
        # Intentar parsear estructura
        f.seek(0)
        try:
            data = json.load(f)
            
            # Analizar estructura
            analysis = {
                "file": file_path.name,
                "size_mb": round(file_size / (1024*1024), 2),
                "type": type(data).__name__,
                "analyzed_at": datetime.now().isoformat()
            }
            
            if isinstance(data, dict):
                analysis["keys"] = list(data.keys())
                analysis["num_keys"] = len(data.keys())
                
                # Ejemplo de contenido
                analysis["sample"] = {}
                for key in list(data.keys())[:5]:
                    value = data[key]
                    if isinstance(value, (dict, list)):
                        analysis["sample"][key] = f"<{type(value).__name__} con {len(value)} elementos>"
                    else:
                        analysis["sample"][key] = str(value)[:100]
            
            elif isinstance(data, list):
                analysis["num_items"] = len(data)
                analysis["first_item_keys"] = list(data[0].keys()) if data and isinstance(data[0], dict) else None
                analysis["sample"] = data[:3] if len(data) <= 3 else [data[0], "...", data[-1]]
            
            # Guardar análisis
            output_file = file_path.parent / f"{file_path.stem}_ANALYSIS.json"
            with open(output_file, 'w', encoding='utf-8') as out:
                json.dump(analysis, out, indent=2, ensure_ascii=False)
            
            print("✅ Análisis guardado en:", output_file)
            print("\n📊 Resumen:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
            return analysis
        
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            return None

def compress_json(file_path, keep_fields=None):
    """Comprime un JSON manteniendo solo campos importantes"""
    
    file_path = Path(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Si es una lista de objetos
    if isinstance(data, list) and keep_fields:
        compressed = []
        for item in data:
            if isinstance(item, dict):
                compressed_item = {k: item.get(k) for k in keep_fields if k in item}
                compressed.append(compressed_item)
            else:
                compressed.append(item)
        
        output_file = file_path.parent / f"{file_path.stem}_COMPRESSED.json"
        with open(output_file, 'w', encoding='utf-8') as out:
            json.dump(compressed, out, indent=2, ensure_ascii=False)
        
        original_size = file_path.stat().st_size
        compressed_size = output_file.stat().st_size
        reduction = (1 - compressed_size/original_size) * 100
        
        print(f"\n✅ Comprimido: {output_file}")
        print(f"📉 Reducción: {reduction:.1f}% ({original_size/(1024*1024):.2f} MB → {compressed_size/(1024*1024):.2f} MB)")
        
        return output_file

def split_large_json(file_path, max_size_mb=1):
    """Divide un JSON grande en archivos más pequeños"""
    
    file_path = Path(file_path)
    max_size = max_size_mb * 1024 * 1024  # Convertir a bytes
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print("⚠️ Solo funciona con listas JSON")
        return
    
    parts = []
    current_part = []
    current_size = 0
    part_num = 1
    
    for item in data:
        item_size = len(json.dumps(item).encode('utf-8'))
        
        if current_size + item_size > max_size and current_part:
            # Guardar parte actual
            part_file = file_path.parent / f"{file_path.stem}_part{part_num}.json"
            with open(part_file, 'w', encoding='utf-8') as out:
                json.dump(current_part, out, indent=2, ensure_ascii=False)
            
            print(f"✅ Parte {part_num} guardada: {len(current_part)} items")
            parts.append(part_file)
            
            # Reset
            current_part = []
            current_size = 0
            part_num += 1
        
        current_part.append(item)
        current_size += item_size
    
    # Guardar última parte
    if current_part:
        part_file = file_path.parent / f"{file_path.stem}_part{part_num}.json"
        with open(part_file, 'w', encoding='utf-8') as out:
            json.dump(current_part, out, indent=2, ensure_ascii=False)
        print(f"✅ Parte {part_num} guardada: {len(current_part)} items")
        parts.append(part_file)
    
    print(f"\n📦 Total de partes: {len(parts)}")
    return parts


# EJEMPLO DE USO
if __name__ == "__main__":
    import sys
    
    print("""
    🗂️ MANEJADOR DE ARCHIVOS GRANDES
    =================================
    
    Uso:
    python handle_large_files.py <archivo.json> [acción]
    
    Acciones:
    - analyze   : Analiza estructura sin cargar todo (default)
    - compress  : Comprime manteniendo campos clave
    - split     : Divide en archivos de 1MB
    
    Ejemplo:
    python handle_large_files.py project_audit_report.json analyze
    """)
    
    if len(sys.argv) < 2:
        print("❌ Debes especificar un archivo JSON")
        sys.exit(1)
    
    file_path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "analyze"
    
    if not Path(file_path).exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        sys.exit(1)
    
    if action == "analyze":
        analyze_large_json(file_path)
    
    elif action == "compress":
        # Pedir campos a mantener
        print("\n¿Qué campos quieres mantener? (separados por coma)")
        fields = input("Campos: ").split(",")
        fields = [f.strip() for f in fields if f.strip()]
        compress_json(file_path, fields)
    
    elif action == "split":
        split_large_json(file_path)
    
    else:
        print(f"❌ Acción desconocida: {action}")