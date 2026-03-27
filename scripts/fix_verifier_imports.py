#!/usr/bin/env python3
"""
FIX: Arregla imports en scripts de verifiers
"""
import os
import re

# Path al archivo
verifier_path = r"C:\Users\MSI\Desktop\ai-job-foundry\scripts\verifiers\LINKEDIN_SMART_VERIFIER_V3.py"

print(f"Arreglando imports en: {verifier_path}")

# Leer archivo
with open(verifier_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Si NO tiene el fix de path, agregarlo
if 'sys.path.insert' not in content:
    # Agregar después de los imports
    new_imports = '''#!/usr/bin/env python3
"""LinkedIn Smart Verifier V3"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

'''
    
    # Reemplazar el inicio
    content = re.sub(r'^#!/usr/bin/env python3\n', new_imports, content)
    
    # Escribir de vuelta
    with open(verifier_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Imports arreglados!")
else:
    print("✅ Ya tiene el fix de imports")
