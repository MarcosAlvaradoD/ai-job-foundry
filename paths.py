"""
AI JOB FOUNDRY - CONFIGURACION DE RUTAS CENTRALIZADA
Este archivo contiene todas las rutas del proyecto.
Si se mueve algo, solo se modifica aqui.
"""

import os
from pathlib import Path

# ============================================================================
# DIRECTORIO RAIZ DEL PROYECTO
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.resolve()

# ============================================================================
# DIRECTORIOS PRINCIPALES
# ============================================================================
CORE_DIR = PROJECT_ROOT / "core"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
LOGS_DIR = PROJECT_ROOT / "logs"
STATE_DIR = PROJECT_ROOT / "state"
WEB_APP_DIR = PROJECT_ROOT / "web_app"
UNIFIED_APP_DIR = PROJECT_ROOT / "unified_app"
WORKFLOWS_DIR = PROJECT_ROOT / "workflows"
FIXES_DIR = PROJECT_ROOT / "fixes"

# ============================================================================
# SUBDIRECTORIOS DE CORE
# ============================================================================
CORE_AUTOMATION = CORE_DIR / "automation"
CORE_ENRICHMENT = CORE_DIR / "enrichment"
CORE_INGESTION = CORE_DIR / "ingestion"
CORE_SHEETS = CORE_DIR / "sheets"
CORE_UTILS = CORE_DIR / "utils"
CORE_COPILOT = CORE_DIR / "copilot"
CORE_PIPELINE = CORE_DIR / "jobs_pipeline"

# ============================================================================
# SUBDIRECTORIOS DE SCRIPTS
# ============================================================================
SCRIPTS_MAINTENANCE = SCRIPTS_DIR / "maintenance"
SCRIPTS_OAUTH = SCRIPTS_DIR / "oauth"
SCRIPTS_POWERSHELL = SCRIPTS_DIR / "powershell"
SCRIPTS_SETUP = SCRIPTS_DIR / "setup"
SCRIPTS_TESTS = SCRIPTS_DIR / "tests"
SCRIPTS_VERIFICATION = SCRIPTS_DIR / "verification"
SCRIPTS_VERIFIERS = SCRIPTS_DIR / "verifiers"

# ============================================================================
# SUBDIRECTORIOS DE DATA
# ============================================================================
DATA_CREDENTIALS = DATA_DIR / "credentials"
DATA_STATE = DATA_DIR / "state"
DATA_SAMPLES = DATA_DIR / "samples"
DATA_TEMPLATES = DATA_DIR / "templates"
DATA_APPLICATIONS = DATA_DIR / "applications"
DATA_INTERVIEWS = DATA_DIR / "interviews"

# ============================================================================
# ARCHIVOS PRINCIPALES
# ============================================================================

# Scripts PowerShell
STARTUP_CHECK_V3 = SCRIPTS_POWERSHELL / "startup_check_v3.ps1"
STARTUP_CHECK_V2 = SCRIPTS_POWERSHELL / "startup_check_v2.ps1"
STARTUP_CHECK = SCRIPTS_POWERSHELL / "startup_check.ps1"

# Archivos de control
CONTROL_CENTER = PROJECT_ROOT / "control_center.py"
RUN_DAILY_PIPELINE = PROJECT_ROOT / "run_daily_pipeline.py"

# Aplicaciones web
UNIFIED_APP = UNIFIED_APP_DIR / "app.py"
WEB_APP = WEB_APP_DIR / "app.py"

# Configuracion
ENV_FILE = PROJECT_ROOT / ".env"
GITIGNORE = PROJECT_ROOT / ".gitignore"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"

# Credenciales
CREDENTIALS_JSON = DATA_CREDENTIALS / "credentials.json"
TOKEN_JSON = DATA_CREDENTIALS / "token.json"
LINKEDIN_COOKIES = DATA_DIR / "linkedin_cookies.json"

# Estado
SEEN_IDS_JSON = STATE_DIR / "seen_ids.json"

# Google Sheets
SHEETS_CONFIG = DATA_DIR / "sheets_config.json"

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_path(path_name: str) -> Path:
    """
    Obtiene una ruta por su nombre.
    
    Args:
        path_name: Nombre de la ruta (ej: 'CORE_AUTOMATION')
        
    Returns:
        Path object
        
    Raises:
        AttributeError: Si la ruta no existe
    """
    try:
        return globals()[path_name]
    except KeyError:
        raise AttributeError(f"Ruta '{path_name}' no existe en paths.py")

def verify_paths() -> dict:
    """
    Verifica que todas las rutas existan.
    
    Returns:
        dict: {'missing': [], 'exists': []}
    """
    result = {'missing': [], 'exists': []}
    
    # Lista de directorios principales a verificar
    dirs_to_check = [
        'CORE_DIR', 'SCRIPTS_DIR', 'DATA_DIR', 'DOCS_DIR', 
        'LOGS_DIR', 'STATE_DIR', 'WEB_APP_DIR', 'UNIFIED_APP_DIR'
    ]
    
    for dir_name in dirs_to_check:
        path = globals()[dir_name]
        if path.exists():
            result['exists'].append(str(path))
        else:
            result['missing'].append(str(path))
    
    return result

def ensure_directories():
    """
    Crea directorios que no existan.
    """
    dirs_to_create = [
        LOGS_DIR, STATE_DIR, DATA_DIR, DATA_CREDENTIALS,
        DATA_STATE, DATA_SAMPLES, DATA_TEMPLATES
    ]
    
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

def get_startup_check_script() -> Path:
    """
    Retorna el script de startup check mas reciente disponible.
    
    Returns:
        Path al script de startup check
    """
    # Prioridad: v3 > v2 > base
    for script in [STARTUP_CHECK_V3, STARTUP_CHECK_V2, STARTUP_CHECK]:
        if script.exists():
            return script
    
    # Si ninguno existe, retornar None
    return None

# ============================================================================
# EXPORTAR TODAS LAS RUTAS COMO STRINGS
# ============================================================================

def get_all_paths() -> dict:
    """
    Retorna todas las rutas como un diccionario.
    
    Returns:
        dict: {'PATH_NAME': '/absolute/path'}
    """
    paths = {}
    for key, value in globals().items():
        if isinstance(value, Path) and key.isupper():
            paths[key] = str(value)
    return paths

# ============================================================================
# VERIFICACION AL IMPORTAR
# ============================================================================

if __name__ == "__main__":
    # Si se ejecuta directamente, verificar rutas
    print("AI JOB FOUNDRY - Verificacion de Rutas")
    print("=" * 60)
    
    result = verify_paths()
    
    print(f"\n[OK] Directorios existentes: {len(result['exists'])}")
    for path in result['exists']:
        print(f"  - {path}")
    
    if result['missing']:
        print(f"\n[ERROR] Directorios faltantes: {len(result['missing'])}")
        for path in result['missing']:
            print(f"  - {path}")
    else:
        print("\n[OK] Todas las rutas existen!")
    
    # Verificar startup check
    startup_script = get_startup_check_script()
    if startup_script:
        print(f"\n[OK] Script de startup: {startup_script}")
    else:
        print("\n[ERROR] No se encontro script de startup check")
