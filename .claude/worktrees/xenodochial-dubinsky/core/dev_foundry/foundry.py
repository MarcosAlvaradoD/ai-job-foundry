
**foundry.py** (esqueleto; usa tu `code_patcher.py` existente)
```python
# -*- coding: utf-8 -*-
"""
foundry.py — orquestador mínimo para autoparches:
- lee devfoundry.yaml
- selecciona proveedor/modelo (regla simple local-first)
- llama a code_patcher.py con la instrucción pedida
- registra logs/costos (placeholder por ahora)
"""

import os
import json
import time
import subprocess
from datetime import datetime

CFG = "devfoundry.yaml"

def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", "foundry.log"), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def run_patch(patch_file, instruction):
    # Delegamos en tu code_patcher.py para hacer el reemplazo seguro (con .bak)
    cmd = ["py", "code_patcher.py", "--file", patch_file, "--instruction", instruction]
    log(f"RUN: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout:
        log(r.stdout.strip())
    if r.stderr:
        log("[stderr] " + r.stderr.strip())
    return r.returncode == 0

def main():
    log("Foundry start")
    # Ejemplo: aplicar REPLACE-WHOLE-FILE a summary_patch.txt (igual que en Jobs)
    patch_file = "summary_patch.txt"  # cambia por el patch que quieras
    instruction = "REPLACE-WHOLE-FILE"
    ok = run_patch(patch_file, instruction)
    log(f"patch result: {ok}")
    log("Foundry end")

if __name__ == "__main__":
    main()
