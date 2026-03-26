"""
📋 GUÍA DE INTEGRACIÓN - OAuth Token Validator
===============================================

Esta guía explica cómo integrar la validación automática de tokens OAuth
en todos los módulos del proyecto AI Job Foundry.

Autor: Marcos Alberto Alvarado
Fecha: 2026-01-02
"""

# ============================================================================
# 🎯 ARCHIVOS QUE REQUIEREN INTEGRACIÓN
# ============================================================================

Los siguientes archivos necesitan agregar validación de token OAuth:

1. ✅ main.py - HECHO
2. ✅ run_daily_pipeline.py - HECHO
3. ⏳ core/automation/gmail_jobs_monitor.py
4. ⏳ core/automation/job_bulletin_processor.py
5. ⏳ core/sheets/sheet_manager.py
6. ⏳ core/automation/auto_apply_linkedin.py
7. ⏳ scripts/test_email_processing.py
8. ⏳ scripts/view_linkedin_jobs.py
9. ⏳ scripts/report_generator.py


# ============================================================================
# 📝 MÉTODO 1: VALIDACIÓN AL INICIO DEL SCRIPT
# ============================================================================

Para scripts standalone (test_email_processing.py, report_generator.py, etc.):

```python
"""
Script: test_email_processing.py
Descripción: Procesar emails de prueba
"""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 🔐 IMPORTAR Y EJECUTAR VALIDACIÓN (CRÍTICO)
from oauth_token_validator import validate_token_or_exit

def main():
    # Validar token al inicio
    validate_token_or_exit()
    
    # Resto del código...
    from core.automation.gmail_jobs_monitor import GmailJobsMonitor
    monitor = GmailJobsMonitor()
    monitor.process_emails()

if __name__ == "__main__":
    main()
```


# ============================================================================
# 📝 MÉTODO 2: VALIDACIÓN EN EL CONSTRUCTOR DE CLASE
# ============================================================================

Para clases que se instancian múltiples veces:

```python
"""
Módulo: core/automation/gmail_jobs_monitor.py
"""

from oauth_token_validator import validate_and_refresh_token
import logging

logger = logging.getLogger(__name__)

class GmailJobsMonitor:
    def __init__(self):
        # 🔐 VALIDAR TOKEN EN CONSTRUCTOR
        if not validate_and_refresh_token():
            raise RuntimeError("Failed to obtain valid OAuth token")
        
        # Resto de la inicialización...
        self.credentials = self._get_credentials()
        # ... más código ...
    
    def _get_credentials(self):
        # Este método YA NO necesita intentar refresh
        # porque el token ya fue validado en __init__
        from google.oauth2.credentials import Credentials
        
        token_path = Path("data/credentials/token.json")
        if token_path.exists():
            return Credentials.from_authorized_user_file(str(token_path))
        else:
            raise FileNotFoundError("Token file not found after validation")
```


# ============================================================================
# 📝 MÉTODO 3: VALIDACIÓN LAZY (SOLO SI ES NECESARIO)
# ============================================================================

Para módulos que pueden funcionar sin OAuth en ciertos casos:

```python
"""
Módulo: core/enrichment/ai_analyzer.py
"""

from oauth_token_validator import validate_and_refresh_token
import logging

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.sheets_manager = None
        self._token_validated = False
    
    def _ensure_token_valid(self):
        """Valida token solo cuando se necesita por primera vez."""
        if not self._token_validated:
            if not validate_and_refresh_token():
                raise RuntimeError("Failed to obtain valid OAuth token")
            self._token_validated = True
    
    def analyze_all_pending_jobs(self):
        # Validar token antes de usar Sheets API
        self._ensure_token_valid()
        
        if self.sheets_manager is None:
            from core.sheets.sheet_manager import SheetManager
            self.sheets_manager = SheetManager()
        
        # Resto del código...
```


# ============================================================================
# 🔧 MODIFICACIONES ESPECÍFICAS POR ARCHIVO
# ============================================================================

## 1. core/automation/gmail_jobs_monitor.py
```python
# ANTES:
class GmailJobsMonitor:
    def __init__(self):
        self.credentials = self._get_credentials()
        # ...

# DESPUÉS:
from oauth_token_validator import validate_and_refresh_token

class GmailJobsMonitor:
    def __init__(self):
        # 🔐 Validar token primero
        if not validate_and_refresh_token():
            raise RuntimeError("OAuth token validation failed")
        
        self.credentials = self._get_credentials()
        # ...
```

## 2. core/automation/job_bulletin_processor.py
```python
# ANTES:
class JobBulletinProcessor:
    def __init__(self):
        self.credentials = self._get_credentials()
        # ...

# DESPUÉS:
from oauth_token_validator import validate_and_refresh_token

class JobBulletinProcessor:
    def __init__(self):
        # 🔐 Validar token primero
        if not validate_and_refresh_token():
            raise RuntimeError("OAuth token validation failed")
        
        self.credentials = self._get_credentials()
        # ...
```

## 3. core/sheets/sheet_manager.py
```python
# ANTES:
class SheetManager:
    def __init__(self):
        self.credentials = self._get_credentials()
        # ...

# DESPUÉS:
from oauth_token_validator import validate_and_refresh_token

class SheetManager:
    def __init__(self):
        # 🔐 Validar token primero
        if not validate_and_refresh_token():
            raise RuntimeError("OAuth token validation failed")
        
        self.credentials = self._get_credentials()
        # ...
```

## 4. core/automation/auto_apply_linkedin.py
```python
# ANTES:
class LinkedInAutoApplier:
    def __init__(self, dry_run=True):
        self.sheet_manager = SheetManager()
        # ...

# DESPUÉS:
from oauth_token_validator import validate_and_refresh_token

class LinkedInAutoApplier:
    def __init__(self, dry_run=True):
        # 🔐 Validar token primero
        if not validate_and_refresh_token():
            raise RuntimeError("OAuth token validation failed")
        
        self.sheet_manager = SheetManager()
        # ...
```


# ============================================================================
# ⚠️  NOTA IMPORTANTE SOBRE _get_credentials()
# ============================================================================

Después de agregar la validación en los constructores, los métodos 
`_get_credentials()` pueden simplificarse eliminando el bloque de refresh:

```python
# ANTES (con manejo de refresh):
def _get_credentials(self):
    creds = None
    token_path = Path("data/credentials/token.json")
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path))
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # ❌ YA NO NECESARIO
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    
    return creds

# DESPUÉS (simplificado, sin refresh):
def _get_credentials(self):
    """
    Carga credentials del token file.
    El token ya fue validado/renovado en __init__, así que solo cargamos.
    """
    token_path = Path("data/credentials/token.json")
    
    if not token_path.exists():
        raise FileNotFoundError(
            "Token file not found. This shouldn't happen after validation."
        )
    
    return Credentials.from_authorized_user_file(str(token_path))
```


# ============================================================================
# ✅ CHECKLIST DE INTEGRACIÓN
# ============================================================================

Para cada archivo que modifiques:

□ Importar: from oauth_token_validator import validate_and_refresh_token
□ Agregar validación en __init__() o al inicio del script
□ Simplificar _get_credentials() removiendo bloque de refresh
□ Agregar logging apropiado
□ Probar que funciona con token válido
□ Probar que funciona con token expirado (debe renovar automáticamente)
□ Verificar que los errores se manejan correctamente


# ============================================================================
# 🚀 ORDEN DE IMPLEMENTACIÓN RECOMENDADO
# ============================================================================

1. ✅ Crear oauth_token_validator.py (HECHO)
2. ✅ Modificar main.py (HECHO)
3. ✅ Modificar run_daily_pipeline.py (HECHO)
4. ⏳ Modificar core/sheets/sheet_manager.py (BASE para todo)
5. ⏳ Modificar core/automation/gmail_jobs_monitor.py
6. ⏳ Modificar core/automation/job_bulletin_processor.py
7. ⏳ Modificar core/automation/auto_apply_linkedin.py
8. ⏳ Modificar scripts de testing
9. ⏳ Probar pipeline completo


# ============================================================================
# 🧪 TESTING
# ============================================================================

Para probar la integración:

1. Forzar expiración del token:
   ```powershell
   Remove-Item data\credentials\token.json
   ```

2. Ejecutar pipeline:
   ```powershell
   py main.py
   ```

3. Verificar que:
   - Se detecta token faltante/expirado
   - Se ejecuta renovación automática
   - El pipeline continúa normalmente
   - No hay errores "invalid_grant"


# ============================================================================
# 📞 SOPORTE
# ============================================================================

Si encuentras problemas:

1. Verificar logs: oauth_token_validator imprime mensajes detallados
2. Ejecutar manualmente: py oauth_token_validator.py --force
3. Verificar token file: data/credentials/token.json
4. Verificar script de renovación: scripts/oauth/reauthenticate_gmail_v2.py


# ============================================================================
# 🎯 RESULTADO ESPERADO
# ============================================================================

Después de la integración completa:

✅ Ningún script debería fallar con "invalid_grant" nunca más
✅ Tokens expirados se renuevan automáticamente
✅ Pipeline funciona sin intervención manual
✅ Mensajes claros cuando hay problemas de autenticación
✅ Sistema verdaderamente "set it and forget it"
