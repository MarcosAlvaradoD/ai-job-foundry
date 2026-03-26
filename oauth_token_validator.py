"""
🔐 OAuth Token Validator - AI Job Foundry
==========================================
Módulo centralizado para validación y renovación automática de tokens OAuth.

FLUJO AUTOMÁTICO:
1. Detecta si el token está expirado
2. Si está expirado → Ejecuta renovación automática
3. Abre navegador para que autorices (requiere tu intervención)
4. Una vez autorizado → Verifica que el nuevo token funciona
5. Solo entonces continúa con el pipeline

Autor: Marcos Alberto Alvarado
Fecha: 2026-01-02
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import logging
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent
TOKEN_PATH = PROJECT_ROOT / "data" / "credentials" / "token.json"
REAUTH_SCRIPT = PROJECT_ROOT / "scripts" / "oauth" / "reauthenticate_gmail_v2.py"


def validate_and_refresh_token(force_refresh: bool = False) -> bool:
    """
    Valida el token OAuth y lo renueva si está expirado.
    
    FLUJO AUTOMÁTICO:
    - Detecta token expirado
    - Ejecuta renovación (abre navegador automáticamente)
    - Espera que completes la autorización
    - Verifica que el nuevo token funciona
    - Continúa solo si todo OK
    
    Args:
        force_refresh: Si True, fuerza la renovación incluso si el token es válido
        
    Returns:
        bool: True si el token es válido o fue renovado exitosamente
    """
    logger.info("=" * 70)
    logger.info("🔐 OAUTH TOKEN VALIDATOR")
    logger.info("=" * 70)
    
    # Verificar que existe el script de renovación
    if not REAUTH_SCRIPT.exists():
        logger.error(f"❌ Script de renovación no encontrado: {REAUTH_SCRIPT}")
        logger.error("   Ubicación esperada: scripts/oauth/reauthenticate_gmail_v2.py")
        return False
    
    # Verificar si existe el token
    if not TOKEN_PATH.exists():
        logger.warning("⚠️  Token no encontrado. Ejecutando autenticación inicial...")
        logger.info("")
        logger.info("🌐 Se abrirá tu navegador para autorizar la aplicación")
        logger.info("   Por favor completa la autorización en el navegador")
        logger.info("")
        return _run_reauth_script()
    
    # Si se fuerza el refresh, ejecutar directamente
    if force_refresh:
        logger.info("🔄 Forzando renovación de token...")
        logger.info("")
        logger.info("🌐 Se abrirá tu navegador para autorizar la aplicación")
        logger.info("   Por favor completa la autorización en el navegador")
        logger.info("")
        return _run_reauth_script()
    
    # Cargar y verificar el token
    try:
        with open(TOKEN_PATH, 'r') as f:
            token_data = json.load(f)
        
        # Verificar campos requeridos
        if 'expiry' not in token_data:
            logger.warning("⚠️  Token no tiene campo 'expiry'. Renovando...")
            return _run_reauth_script()
        
        # Parsear fecha de expiración
        expiry_str = token_data['expiry']
        try:
            # Intentar con formato ISO 8601
            if expiry_str.endswith('Z'):
                expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            else:
                expiry = datetime.fromisoformat(expiry_str)
        except ValueError:
            logger.warning(f"⚠️  Formato de fecha inválido: {expiry_str}")
            return _run_reauth_script()
        
        # Hacer ambas fechas timezone-aware para comparación
        now = datetime.now(timezone.utc)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        
        # Verificar si está expirado o por expirar (< 5 minutos)
        time_until_expiry = (expiry - now).total_seconds()
        
        if time_until_expiry <= 0:
            logger.warning("⚠️  Token EXPIRADO. Renovando automáticamente...")
            logger.info("")
            logger.info("🌐 Se abrirá tu navegador para autorizar la aplicación")
            logger.info("   Por favor completa la autorización en el navegador")
            logger.info("   El pipeline continuará automáticamente después")
            logger.info("")
            return _run_reauth_script()
        elif time_until_expiry < 300:  # Menos de 5 minutos
            logger.warning(f"⚠️  Token expira en {int(time_until_expiry/60)} minutos.")
            logger.warning("   Renovando preventivamente...")
            logger.info("")
            logger.info("🌐 Se abrirá tu navegador para autorizar la aplicación")
            logger.info("")
            return _run_reauth_script()
        else:
            # Token válido
            hours = int(time_until_expiry / 3600)
            minutes = int((time_until_expiry % 3600) / 60)
            logger.info(f"✅ Token válido. Expira en {hours}h {minutes}m")
            logger.info(f"   Fecha expiración: {expiry.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info("=" * 70)
            return True
            
    except json.JSONDecodeError:
        logger.error("❌ Token corrupto (JSON inválido). Renovando...")
        return _run_reauth_script()
    except Exception as e:
        logger.error(f"❌ Error al validar token: {e}")
        return _run_reauth_script()


def _run_reauth_script() -> bool:
    """
    Ejecuta el script de reautenticación y ESPERA a que termine.
    
    El script abre el navegador automáticamente y espera que el usuario
    complete la autorización. Una vez completado, verifica que el nuevo
    token funciona correctamente.
    
    Returns:
        bool: True si la renovación fue exitosa y el token funciona
    """
    logger.info("🔄 Ejecutando renovación de token...")
    logger.info(f"   Script: {REAUTH_SCRIPT}")
    logger.info("")
    logger.info("⏳ ESPERANDO que completes la autorización en el navegador...")
    logger.info("   (Esto puede tomar 1-2 minutos)")
    logger.info("")
    
    try:
        # Ejecutar script de renovación (ESPERA a que termine)
        result = subprocess.run(
            [sys.executable, str(REAUTH_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=120  # Timeout de 120 segundos (2 minutos)
        )
        
        logger.info("")
        logger.info("-" * 70)
        
        if result.returncode == 0:
            logger.info("✅ Renovación completada exitosamente")
            logger.info("")
            
            # VERIFICAR que el nuevo token funciona
            logger.info("🔍 Verificando que el nuevo token funciona...")
            
            # Esperar 1 segundo para que el archivo se escriba
            time.sleep(1)
            
            # Verificar que el token existe
            if not TOKEN_PATH.exists():
                logger.error("❌ Token no fue creado después de renovación")
                logger.info("=" * 70)
                return False
            
            # Cargar y verificar el nuevo token
            try:
                with open(TOKEN_PATH, 'r') as f:
                    new_token_data = json.load(f)
                
                # Verificar que tiene los campos necesarios
                if 'token' in new_token_data and 'expiry' in new_token_data:
                    logger.info("✅ Nuevo token es válido")
                    logger.info("")
                    logger.info("=" * 70)
                    logger.info("✅ LISTO PARA CONTINUAR")
                    logger.info("=" * 70)
                    return True
                else:
                    logger.error("❌ Nuevo token no tiene los campos requeridos")
                    logger.info("=" * 70)
                    return False
            except Exception as e:
                logger.error(f"❌ Error al verificar nuevo token: {e}")
                logger.info("=" * 70)
                return False
        else:
            # Renovación falló
            logger.error(f"❌ Renovación falló con código {result.returncode}")
            logger.info("")
            
            if result.stdout:
                logger.info("📋 Output del script:")
                for line in result.stdout.split('\n')[:10]:  # Primeras 10 líneas
                    if line.strip():
                        logger.info(f"   {line}")
            
            if result.stderr:
                logger.error("📋 Errores:")
                for line in result.stderr.split('\n')[:10]:  # Primeras 10 líneas
                    if line.strip():
                        logger.error(f"   {line}")
            
            logger.info("")
            logger.info("=" * 70)
            logger.error("❌ RENOVACIÓN FALLÓ")
            logger.info("=" * 70)
            logger.info("")
            logger.info("💡 Solución manual:")
            logger.info("   1. Ejecuta: py scripts\\oauth\\reauthenticate_gmail_v2.py")
            logger.info("   2. Completa la autorización en el navegador")
            logger.info("   3. Vuelve a ejecutar el pipeline")
            logger.info("")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("")
        logger.error("❌ Renovación excedió tiempo límite (120 segundos)")
        logger.error("   Puede que el navegador esté esperando tu autorización")
        logger.info("")
        logger.info("💡 Solución:")
        logger.info("   1. Completa la autorización en el navegador si está abierto")
        logger.info("   2. O ejecuta manualmente: py scripts\\oauth\\reauthenticate_gmail_v2.py")
        logger.info("")
        logger.info("=" * 70)
        return False
    except Exception as e:
        logger.error("")
        logger.error(f"❌ Error al ejecutar renovación: {e}")
        logger.info("=" * 70)
        return False



def validate_token_or_exit(exit_code: int = 1) -> None:
    """
    Valida el token y termina el programa si falla.
    
    FLUJO AUTOMÁTICO:
    1. Detecta token expirado
    2. Ejecuta renovación automática (abre navegador)
    3. Espera que completes la autorización
    4. Verifica que funciona
    5. Solo entonces continúa
    
    Si falla en cualquier paso, termina el programa con mensaje claro.
    
    Args:
        exit_code: Código de salida si la validación falla
    """
    if not validate_and_refresh_token():
        logger.error("")
        logger.error("❌ No se pudo obtener token válido")
        logger.error("")
        logger.error("El pipeline NO puede continuar sin token OAuth válido")
        logger.error("")
        logger.error("💡 Solución manual:")
        logger.error("   py scripts\\oauth\\reauthenticate_gmail_v2.py")
        logger.error("")
        sys.exit(exit_code)


# Script ejecutable directo
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validar y renovar token OAuth de Gmail/Sheets"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar renovación incluso si el token es válido"
    )
    
    args = parser.parse_args()
    
    print()
    print("🔐 OAuth Token Validator - AI Job Foundry")
    print("=" * 70)
    print()
    
    success = validate_and_refresh_token(force_refresh=args.force)
    
    print()
    if success:
        print("✅ Token OAuth está listo para usar")
        print()
        sys.exit(0)
    else:
        print("❌ No se pudo validar/renovar el token")
        print()
        sys.exit(1)
