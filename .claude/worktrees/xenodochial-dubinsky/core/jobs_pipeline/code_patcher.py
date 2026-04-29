# -*- coding: utf-8 -*-
"""
code_patcher.py
Aplica parches declarativos a archivos de tu repo desde un archivo de instrucciones (.txt).
Soporta la instrucción:
  REPLACE-WHOLE-FILE: <ruta>

- Crea backup con timestamp: <archivo>.bak-YYYYMMDD-HHMMSS
- Valida que el contenido nuevo sea Python UTF-8 cuando el destino es .py
- Reporta bytes escritos y muestra 3 primeras y 3 últimas líneas para verificación rápida

Uso:
  py code_patcher.py --file summary_patch.txt --instruction INSTRUCTION

Donde el archivo .txt debe contener una sección del tipo:

REPLACE-WHOLE-FILE: sheet_summary.py
<contenido completo nuevo del archivo aquí>

Autor: tú 🛠️
"""
import argparse, io, os, re, sys, time

def read_text(path: str) -> str:
    with io.open(path, "r", encoding="utf-8", errors="strict") as f:
        return f.read()

def write_text(path: str, data: str):
    with io.open(path, "w", encoding="utf-8", errors="strict") as f:
        f.write(data)

def backup_file(path: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = f"{path}.bak-{ts}"
    if os.path.exists(path):
        with io.open(path, "rb") as fsrc, io.open(bak, "wb") as fdst:
            fdst.write(fsrc.read())
    return bak

def extract_replace_whole_file(block: str):
    """
    Devuelve (dest_path, new_content) para la primer instrucción REPLACE-WHOLE-FILE encontrada.
    """
    # Permitimos líneas previas con powershell-style $patch = @'  ...  '@
    m = re.search(r"REPLACE-WHOLE-FILE:\s*(.+?)\r?\n(.*)\Z", block, flags=re.S)
    if not m:
        return None, None
    dest = m.group(1).strip()
    content = m.group(2)
    return dest, content

def sanity_python_utf8(path: str, data: str):
    if not path.endswith(".py"):
        return
    # Validar que compile
    try:
        compile(data, path, "exec")
    except Exception as e:
        print(f"[ERROR] El nuevo contenido de {path} no compila: {e}")
        sys.exit(2)

def preview_lines(label: str, data: str, n: int = 3):
    lines = data.splitlines()
    head = "\n".join(lines[:n])
    tail = "\n".join(lines[-n:]) if len(lines) > n else ""
    print(f"--- {label}: primeras {n} líneas ---\n{head}\n--- fin primeras ---")
    if tail:
        print(f"--- {label}: últimas {n} líneas ---\n{tail}\n--- fin últimas ---")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Archivo de instrucciones (patch)")
    ap.add_argument("--instruction", default="REPLACE-WHOLE-FILE", help="Tipo de instrucción a aplicar")
    args = ap.parse_args()

    txt = read_text(args.file)
    dest, new_content = extract_replace_whole_file(txt)
    if not dest:
        print("[ERROR] No encontré instrucción REPLACE-WHOLE-FILE en el patch.")
        sys.exit(1)

    if not os.path.exists(dest):
        # si el destino no existe, igual crearemos backup “vacío” para consistencia
        open(dest, "a", encoding="utf-8").close()

    old = read_text(dest)
    sanity_python_utf8(dest, new_content)

    bak = backup_file(dest)
    write_text(dest, new_content)

    print(f"✅ Patch aplicado sobre {dest}")
    print(f"   • Backup: {bak}  (existe={'sí' if os.path.exists(bak) else 'no'})")
    print(f"   • Bytes antiguos: {len(old)} | nuevos: {len(new_content)} | delta: {len(new_content)-len(old)}")
    preview_lines("nuevo", new_content, 3)

if __name__ == "__main__":
    main()
