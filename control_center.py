#!/usr/bin/env python3
"""
AI JOB FOUNDRY - CONTROL CENTER V2
Interactive menu with startup check integration

Usage:
    py control_center.py
    Or double-click: START_CONTROL_CENTER.bat
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import subprocess
import webbrowser
from datetime import datetime

# Import OAuth validator
from core.utils.oauth_validator import ensure_valid_oauth_token

# Import centralized paths
try:
    from paths import get_startup_check_script, SCRIPTS_POWERSHELL
except ImportError:
    # Fallback if paths.py doesn't exist
    SCRIPTS_POWERSHELL = Path(__file__).parent / "scripts" / "powershell"
    def get_startup_check_script():
        for script in ["startup_check_v3.ps1", "startup_check_v2.ps1", "startup_check.ps1"]:
            script_path = SCRIPTS_POWERSHELL / script
            if script_path.exists():
                return script_path
        return None

# Color support for Windows
try:
    import colorama
    colorama.init()
    COLORS = {
        'HEADER': '\033[95m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'END': '\033[0m'
    }
except ImportError:
    COLORS = {k: '' for k in ['HEADER', 'BLUE', 'CYAN', 'GREEN', 'YELLOW', 'RED', 'BOLD', 'UNDERLINE', 'END']}

def run_startup_check():
    """Run startup checks before showing menu"""
    print(f"{COLORS['CYAN']}Ejecutando verificación de servicios...{COLORS['END']}\n")
    
    # Get startup check script using paths.py
    startup_script = get_startup_check_script()
    
    if not startup_script:
        print(f"{COLORS['YELLOW']}⚠️  No se encontró script de startup check - continuando sin verificar{COLORS['END']}")
        input(f"\n{COLORS['BOLD']}Presiona Enter para continuar...{COLORS['END']}")
        return
    
    print(f"{COLORS['CYAN']}Usando: {startup_script}{COLORS['END']}\n")
    
    # Run PowerShell startup check
    try:
        result = subprocess.run(
            ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', str(startup_script)],
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"\n{COLORS['RED']}⚠️  Startup check encontró problemas{COLORS['END']}")
            response = input(f"\n{COLORS['BOLD']}¿Continuar de todas formas? (s/n): {COLORS['END']}").strip().lower()
            if response != 's':
                print(f"\n{COLORS['YELLOW']}👋 Saliendo. Por favor arregla los problemas primero.{COLORS['END']}\n")
                sys.exit(0)
        
        print(f"\n{COLORS['GREEN']}✅ Verificación completada{COLORS['END']}")
        input(f"\n{COLORS['BOLD']}Presiona Enter para continuar al menú...{COLORS['END']}")
        
    except FileNotFoundError:
        print(f"{COLORS['YELLOW']}⚠️  Script no encontrado: {startup_script}{COLORS['END']}")
    except Exception as e:
        print(f"{COLORS['RED']}❌ Error ejecutando startup check: {e}{COLORS['END']}")

def print_header():
    """Print control center header"""
    print("\n" + "="*70)
    print(f"{COLORS['CYAN']}{COLORS['BOLD']}🚀 AI JOB FOUNDRY - CONTROL CENTER{COLORS['END']}")
    print("="*70)
    print(f"{COLORS['YELLOW']}Sistema automatizado de búsqueda de empleo{COLORS['END']}")
    print(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

def print_menu():
    """Print main menu"""
    print(f"\n{COLORS['BOLD']}📋 MENÚ PRINCIPAL:{COLORS['END']}\n")
    
    print(f"{COLORS['GREEN']}PIPELINE COMPLETO:{COLORS['END']}")
    print("  1. 🚀 Ejecutar Pipeline Completo (emails + AI + expire + report)")
    print("  2. ⚡ Pipeline Rápido (solo emails + report)")
    
    print(f"\n{COLORS['CYAN']}OPERACIONES INDIVIDUALES:{COLORS['END']}")
    print("  3. 📧 Procesar Emails Nuevos (reclutadores directos)")
    print("  4. 📬 Procesar Boletines (LinkedIn/Indeed/Glassdoor)")
    print("  5. 🤖 Análisis AI (calcular FIT SCORES)")
    print("  6. 🚫 Verificar Ofertas Expiradas (por fecha)")
    print("  7. 🔍 Verificar URLs (Playwright por plataforma)")
    print("  8. 📊 Generar Reporte")
    
    print(f"\n{COLORS['YELLOW']}SCRAPING:{COLORS['END']}")
    print("  9. 🔗 LinkedIn Scraper (buscar ofertas)")
    print("  10. 🔗 Indeed Scraper (buscar ofertas)")
    
    print(f"\n{COLORS['BLUE']}AUTO-APPLY:{COLORS['END']}")
    print("  11. 🎯 Auto-Apply (DRY RUN - simulación)")
    print("  12. 💼 Auto-Apply (LIVE - aplica realmente)")
    
    print(f"\n{COLORS['HEADER']}VISUALIZACIÓN:{COLORS['END']}")
    print("  13. 📊 Abrir Dashboard")
    print("  14. 📄 Ver Google Sheets")
    
    print(f"\n{COLORS['BOLD']}INTERVIEW COPILOT:{COLORS['END']}")
    print(f"  17. 🔒 Copilot OVERLAY (invisible en Zoom/Teams/Meet) ⭐ NUEVO")
    print("  18. 🎤 Copilot Simple / V2 con Job Context")

    print(f"\n{COLORS['BOLD']}UTILIDADES:{COLORS['END']}")
    print("  19. 📩 Actualizar Status desde Emails (entrevistas, rechazos)")
    print("  20. 🚫 Marcar Jobs Expirados (auto-detect)")
    print("  21. 🔐 Regenerar Credenciales OAuth (Gmail/Sheets)")
    print("  22. 🔍 Diagnóstico del Pipeline (estado real del sheet)")
    print("  23. 📋 Backlog Kanban (pizarrón de tareas pendientes)")
    print("  24. 🔧 Ver Configuración (.env)")
    print("  25. 📚 Ver Documentación")

    print(f"\n{COLORS['RED']}SALIR:{COLORS['END']}")
    print("  0. 🚪 Salir")
    
    print("\n" + "="*70)

def run_command(command: list, description: str):
    """Run a command and show status"""
    print(f"\n{COLORS['YELLOW']}▶️  {description}...{COLORS['END']}")
    print(f"{COLORS['CYAN']}Ejecutando: {' '.join(command)}{COLORS['END']}\n")
    
    try:
        result = subprocess.run(command, check=True)
        print(f"\n{COLORS['GREEN']}✅ Completado exitosamente{COLORS['END']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{COLORS['RED']}❌ Error: {e}{COLORS['END']}")
        return False
    except FileNotFoundError:
        print(f"\n{COLORS['RED']}❌ Error: Comando no encontrado{COLORS['END']}")
        return False

def open_browser(url: str, description: str):
    """Open URL in browser"""
    print(f"\n{COLORS['YELLOW']}▶️  {description}...{COLORS['END']}")
    webbrowser.open(url)
    print(f"{COLORS['GREEN']}✅ Abriendo en navegador{COLORS['END']}")

def show_file(filepath: str, description: str):
    """Show file contents"""
    print(f"\n{COLORS['YELLOW']}▶️  {description}...{COLORS['END']}\n")
    
    if not os.path.exists(filepath):
        print(f"{COLORS['RED']}❌ Archivo no encontrado: {filepath}{COLORS['END']}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content[:2000])  # First 2000 chars
        if len(content) > 2000:
            print(f"\n{COLORS['YELLOW']}... (mostrando primeros 2000 caracteres){COLORS['END']}")
    
    print(f"\n{COLORS['CYAN']}Ruta completa: {filepath}{COLORS['END']}")

def handle_option(option: str):
    """Handle menu option"""
    
    if option == '1':
        # Pipeline completo
        return run_command(
            ['py', 'run_daily_pipeline.py', '--all'],
            'Pipeline Completo (emails + AI + expire + report)'
        )
    
    elif option == '2':
        # Pipeline rápido
        return run_command(
            ['py', 'run_daily_pipeline.py', '--emails', '--report'],
            'Pipeline Rápido (emails + report)'
        )
    
    elif option == '3':
        # Procesar emails
        return run_command(
            ['py', 'run_daily_pipeline.py', '--emails'],
            'Procesando emails nuevos'
        )
    
    elif option == '4':
        # Procesar boletines
        return run_command(
            ['py', 'core/automation/job_bulletin_processor.py'],
            'Procesando boletines de LinkedIn/Indeed/Glassdoor'
        )
    
    elif option == '5':
        # AI Analysis
        return run_command(
            ['py', 'run_daily_pipeline.py', '--analyze'],
            'Análisis AI (calculando FIT SCORES)'
        )
    
    elif option == '6':
        # Verificar expirados por fecha
        return run_command(
            ['py', 'run_daily_pipeline.py', '--expire'],
            'Verificando ofertas expiradas (fecha + URLs)'
        )
    
    elif option == '7':
        # Verificar URLs con SMART VERIFIERS (Playwright por plataforma)
        print(f"\n{COLORS['CYAN']}Selecciona plataforma:{COLORS['END']}")
        print("  1. LinkedIn (con login automático)")
        print("  2. Indeed")
        print("  3. Glassdoor")
        print("  4. Todas las plataformas (secuencial)")
        
        platform = input(f"\n{COLORS['BOLD']}Plataforma [1/2/3/4]: {COLORS['END']}").strip()
        
        # Ask for limit
        limit_input = input(f"{COLORS['BOLD']}¿Cuántos jobs verificar? [Enter=todos]: {COLORS['END']}").strip()
        limit_arg = ['--limit', limit_input] if limit_input else []
        
        if platform == '1':
            # LinkedIn V3 con cookies
            return run_command(
                ['py', 'scripts/verifiers/LINKEDIN_SMART_VERIFIER_V3.py'] + limit_arg,
                'Verificando LinkedIn (con login automático y cookies)'
            )
        elif platform == '2':
            # Indeed
            return run_command(
                ['py', 'scripts/verifiers/INDEED_SMART_VERIFIER.py'] + limit_arg,
                'Verificando Indeed'
            )
        elif platform == '3':
            # Glassdoor
            return run_command(
                ['py', 'scripts/verifiers/GLASSDOOR_SMART_VERIFIER.py'] + limit_arg,
                'Verificando Glassdoor'
            )
        elif platform == '4':
            # Todas (ejecuta --expire que incluye las 3)
            print(f"\n{COLORS['YELLOW']}ℹ️  Ejecutando verificación completa (las 3 plataformas){COLORS['END']}")
            return run_command(
                ['py', 'run_daily_pipeline.py', '--expire'],
                'Verificando todas las plataformas (LinkedIn V3 + Indeed + Glassdoor)'
            )
        else:
            print(f"{COLORS['RED']}❌ Opción inválida{COLORS['END']}")
            return False
    
    elif option == '8':
        # Generar reporte
        return run_command(
            ['py', 'run_daily_pipeline.py', '--report'],
            'Generando reporte'
        )
    
    elif option == '9':
        # LinkedIn Notifications Scraper (NUEVO)
        print(f"\n{COLORS['CYAN']}🔍 LinkedIn Notifications Scraper{COLORS['END']}")
        print(f"Extrae ofertas de recomendaciones de LinkedIn")
        print(f"\nOpciones:")
        print(f"  1. Solo scraping (extrae y guarda)")
        print(f"  2. Workflow completo DRY RUN (scrape + analyze + test apply)")
        print(f"  3. Workflow completo LIVE (scrape + analyze + REAL apply)")
        
        choice = input(f"\n{COLORS['BOLD']}Selecciona [1/2/3]: {COLORS['END']}").strip()
        
        if choice == '1':
            return run_command(
                ['py', 'run_linkedin_workflow.py', '--scrape-only'],
                '🔍 LinkedIn Notifications Scraper (solo extracción)'
            )
        elif choice == '2':
            return run_command(
                ['py', 'run_linkedin_workflow.py', '--all'],
                '🚀 LinkedIn Workflow Completo (DRY RUN)'
            )
        elif choice == '3':
            print(f"\n{COLORS['RED']}⚠️  MODO LIVE - Aplicará a ofertas reales{COLORS['END']}")
            confirm = input(f"{COLORS['BOLD']}¿Estás seguro? (escribe 'SÍ' o 'SI' o 'S' para confirmar): {COLORS['END']}").strip().upper()
            if confirm in ['SÍ', 'SI', 'S', 'YES', 'Y']:
                return run_command(
                    ['py', 'run_linkedin_workflow.py', '--all', '--live'],
                    '🚀 LinkedIn Workflow Completo (LIVE)'
                )
            else:
                print(f"{COLORS['YELLOW']}Cancelado{COLORS['END']}")
                return False
        else:
            print(f"{COLORS['RED']}❌ Opción inválida{COLORS['END']}")
            return False
    
    elif option == '10':
        # Indeed Scraper
        print(f"\n{COLORS['YELLOW']}Indeed Scraper tiene problemas de timeout.{COLORS['END']}")
        print(f"Prioridad baja - LinkedIn es suficiente.")
        return False
    
    elif option == '11':
        # Auto-Apply DRY RUN (EASY APPLY COMPLETE)
        print(f"\n{COLORS['CYAN']}🤖 Auto-Apply EASY APPLY (DRY RUN){COLORS['END']}")
        print(f"Sistema: Playwright + Detección Inteligente Easy Apply")
        print(f"Detecta: Easy Apply vs External Apply\n")
        
        # Ask for parameters
        min_fit = input(f"{COLORS['BOLD']}FIT Score mínimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        
        max_jobs = input(f"{COLORS['BOLD']}Máximo de jobs a procesar [default=5]: {COLORS['END']}").strip()
        max_jobs = max_jobs if max_jobs else '5'
        
        return run_command(
            ['py', 'core/automation/auto_apply_linkedin_easy_complete.py', 
             '--min-fit', min_fit, '--max-jobs', max_jobs],
            f'Easy Apply (DRY RUN - FIT>={min_fit}, max={max_jobs})'
        )
    
    elif option == '12':
        # Auto-Apply LIVE (EASY APPLY COMPLETE)
        print(f"\n{COLORS['RED']}⚠️  MODO LIVE - Aplicará a ofertas reales{COLORS['END']}")
        print(f"Sistema: Playwright + Detección Inteligente Easy Apply")
        print(f"Detecta: Easy Apply vs External Apply\n")
        
        # Ask for parameters
        min_fit = input(f"{COLORS['BOLD']}FIT Score mínimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        
        max_jobs = input(f"{COLORS['BOLD']}Máximo de jobs a procesar [default=5]: {COLORS['END']}").strip()
        max_jobs = max_jobs if max_jobs else '5'
        
        confirm = input(f"\n{COLORS['RED']}{COLORS['BOLD']}¿Aplicar REALMENTE a hasta {max_jobs} ofertas? (escribe 'SÍ' o 'SI' o 'S'): {COLORS['END']}").strip().upper()
        
        if confirm in ['SÍ', 'SI', 'S', 'YES', 'Y']:
            return run_command(
                ['py', 'core/automation/auto_apply_linkedin_easy_complete.py', 
                 '--live', '--min-fit', min_fit, '--max-jobs', max_jobs],
                f'Easy Apply (LIVE - FIT>={min_fit}, max={max_jobs})'
            )
        else:
            print(f"{COLORS['YELLOW']}Cancelado{COLORS['END']}")
            return False
    
    elif option == '13':
        # Dashboard
        print(f"\n{COLORS['YELLOW']}▶️  Iniciando Dashboard Server...{COLORS['END']}")
        print(f"Abre tu navegador en: {COLORS['CYAN']}http://localhost:8000{COLORS['END']}")
        print(f"{COLORS['RED']}Presiona Ctrl+C para detener el servidor{COLORS['END']}\n")
        
        try:
            subprocess.run(['py', 'web/serve_dashboard.py'], check=True)
        except KeyboardInterrupt:
            print(f"\n{COLORS['YELLOW']}👋 Dashboard server stopped.{COLORS['END']}")
        except Exception as e:
            print(f"\n{COLORS['RED']}❌ Error: {e}{COLORS['END']}")
        finally:
            print(f"\n{COLORS['GREEN']}✅ Servidor detenido{COLORS['END']}")
        return True
    
    elif option == '14':
        # Google Sheets
        open_browser(
            'https://docs.google.com/spreadsheets/d/1EqWPiHdcYyMr5trEuiT_-lzPVEr0owOoDEtTsCIBxdg',
            'Abriendo Google Sheets'
        )
        return True
    
    elif option == '15':
        # Ver .env
        show_file('.env', 'Configuración (.env)')
        return True
    
    elif option == '16':
        # Ver Documentación
        print(f"\n{COLORS['CYAN']}Documentación disponible:{COLORS['END']}")
        print("  1. docs/PROJECT_STATUS.md - Estado del proyecto")
        print("  2. docs/JOB_EXPIRATION_SYSTEM.md - Sistema de expiración")
        print("  3. docs/DASHBOARD_SETUP.md - Configurar dashboard")
        print("  4. docs/AUTO_APPLY_GUIDE.md - Guía de auto-apply")
        print("  5. README.md - Documentación general")
        
        doc_choice = input(f"\n{COLORS['BOLD']}¿Cuál ver? [1-5 o Enter para omitir]: {COLORS['END']}").strip()
        
        docs = {
            '1': 'docs/PROJECT_STATUS.md',
            '2': 'docs/JOB_EXPIRATION_SYSTEM.md',
            '3': 'docs/DASHBOARD_SETUP.md',
            '4': 'docs/AUTO_APPLY_GUIDE.md',
            '5': 'README.md'
        }
        
        if doc_choice in docs:
            show_file(docs[doc_choice], f'Documentación - {docs[doc_choice]}')
        
        return True
    
    elif option == '17':
        # Interview Copilot OVERLAY — invisible en screen share
        print(f"\n{COLORS['CYAN']}🔒 INTERVIEW COPILOT OVERLAY{COLORS['END']}")
        print(f"{COLORS['GREEN']}✅ INVISIBLE en Zoom / Teams / Google Meet / OBS{COLORS['END']}")
        print(f"   Usa WDA_EXCLUDEFROMCAPTURE (Windows API)")
        print(f"\n{COLORS['YELLOW']}Instrucciones:{COLORS['END']}")
        print(f"   1. Abre tu videollamada normalmente")
        print(f"   2. El overlay aparece en la esquina — solo TÚ lo ves")
        print(f"   3. Escribe la pregunta del entrevistador → Enter")
        print(f"   4. LM Studio responde con sugerencia basada en tu CV")
        print(f"   5. Ctrl+Shift+H para ocultar/mostrar rápido")
        print(f"\n{COLORS['CYAN']}Requiere: LM Studio corriendo con Qwen2.5 14B{COLORS['END']}")
        input(f"\n{COLORS['BOLD']}Presiona Enter para lanzar el overlay...{COLORS['END']}")
        return run_command(
            ['py', 'core/copilot/interview_copilot_overlay.py'],
            'Interview Copilot OVERLAY (invisible en screen share)'
        )

    elif option == '18':
        # Interview Copilot clásico
        print(f"\n{COLORS['CYAN']}🎤 Interview Copilot (modo clásico){COLORS['END']}")
        print("\nOpciones:")
        print("  1. Simple Mode (texto, sin grabar)")
        print("  2. V2 con Job Context (carga job del Sheet)")
        print("  3. Session Recorder (push-to-talk + Whisper)")

        copilot_option = input(f"\n{COLORS['BOLD']}Selecciona [1/2/3]: {COLORS['END']}").strip()

        if copilot_option == '1':
            return run_command(
                ['py', 'core/copilot/interview_copilot_simple.py'],
                'Interview Copilot - Simple Mode'
            )
        elif copilot_option == '2':
            return run_command(
                ['py', 'core/copilot/interview_copilot_v2.py'],
                'Interview Copilot V2 - Job Context'
            )
        elif copilot_option == '3':
            return run_command(
                ['py', 'core/copilot/interview_copilot_session_recorder.py'],
                'Interview Copilot - Session Recorder'
            )
        else:
            print(f"{COLORS['RED']}❌ Opción inválida{COLORS['END']}")
            return False

    elif option == '19':
        # Actualizar status desde emails
        return run_command(
            ['py', 'update_status_from_emails.py'],
            'Actualizando status desde emails (entrevistas, rechazos)'
        )

    elif option == '20':
        # Marcar jobs expirados
        return run_command(
            ['py', 'scripts/verifiers/EXPIRE_LIFECYCLE.py', '--mark'],
            'Marcando jobs expirados (>30 días)'
        )

    elif option == '21':
        # Regenerar credenciales OAuth
        print(f"\n{COLORS['YELLOW']}🔐 REGENERAR CREDENCIALES OAUTH{COLORS['END']}")
        print(f"\n{COLORS['CYAN']}Permisos que se solicitarán:{COLORS['END']}")
        print(f"  • Google Sheets - Lectura/escritura")
        print(f"  • Gmail - Lectura de emails")
        print(f"  • Gmail - Modificar etiquetas")
        print(f"  • Gmail - Mover a papelera")
        print(f"\n{COLORS['YELLOW']}NOTA: Elimina token.json y pide login de nuevo{COLORS['END']}")

        confirm = input(f"\n{COLORS['BOLD']}¿Regenerar credenciales? (SI/S): {COLORS['END']}").strip().upper()

        if confirm in ['SI', 'S', 'YES', 'Y']:
            return run_command(
                ['py', 'scripts/oauth/regenerate_oauth_token.py'],
                'Regenerando credenciales OAuth'
            )
        else:
            print(f"{COLORS['YELLOW']}Cancelado{COLORS['END']}")
            return False

    elif option == '22':
        # Diagnóstico del pipeline
        return run_command(
            ['py', 'scripts/diagnostics/diagnose_pipeline.py'],
            'Diagnóstico completo del pipeline (Sheet + ApplyURL + elegibles)'
        )

    elif option == '23':
        # Backlog Kanban
        backlog_path = str(Path(__file__).parent / 'boards' / 'backlog.html')
        if Path(backlog_path).exists():
            print(f"\n{COLORS['GREEN']}✅ Abriendo Backlog Kanban en el navegador...{COLORS['END']}")
            webbrowser.open(f'file:///{backlog_path}')
        else:
            print(f"{COLORS['RED']}❌ No se encontró boards/backlog.html{COLORS['END']}")
        return True

    elif option == '24':
        # Ver .env
        show_file('.env', 'Configuración (.env)')
        return True

    elif option == '25':
        # Ver Documentación
        print(f"\n{COLORS['CYAN']}Documentación disponible:{COLORS['END']}")
        print("  1. docs/PROJECT_STATUS.md - Estado del proyecto")
        print("  2. docs/MASTER_FEATURE_ROADMAP.md - Roadmap de features")
        print("  3. docs/AUTO_APPLY_AI_LOCAL_GUIDE.md - Guía auto-apply")
        print("  4. docs/LINKEDIN_AUTO_APPLY_V3.md - LinkedIn V3")
        print("  5. README.md - Documentación general")

        doc_choice = input(f"\n{COLORS['BOLD']}¿Cuál ver? [1-5 o Enter para omitir]: {COLORS['END']}").strip()

        docs = {
            '1': 'docs/PROJECT_STATUS.md',
            '2': 'docs/MASTER_FEATURE_ROADMAP.md',
            '3': 'docs/AUTO_APPLY_AI_LOCAL_GUIDE.md',
            '4': 'docs/LINKEDIN_AUTO_APPLY_V3.md',
            '5': 'README.md'
        }

        if doc_choice in docs:
            show_file(docs[doc_choice], f'Documentación - {docs[doc_choice]}')

        return True
    
    elif option == '0':
        # Salir
        print(f"\n{COLORS['GREEN']}👋 ¡Hasta luego!{COLORS['END']}\n")
        return None
    
    else:
        print(f"\n{COLORS['RED']}❌ Opción inválida{COLORS['END']}")
        return False

def main():
    """Main control center loop"""
    # Run startup check first
    run_startup_check()
    
    # ✅ CRITICAL: Validate OAuth token BEFORE any operations
    print(f"\n{COLORS['CYAN']}🔐 Validating OAuth token...{COLORS['END']}")
    if not ensure_valid_oauth_token(auto_refresh=True):
        print(f"{COLORS['RED']}❌ OAuth token validation FAILED{COLORS['END']}")
        print(f"{COLORS['YELLOW']}Manual fix: py scripts\\oauth\\reauthenticate_gmail_v2.py{COLORS['END']}\n")
        sys.exit(1)
    print(f"{COLORS['GREEN']}✅ OAuth token validated{COLORS['END']}\n")
    
    while True:
        print_header()
        print_menu()
        
        try:
            option = input(f"{COLORS['BOLD']}Selecciona una opción [0-20]: {COLORS['END']}").strip()
            
            result = handle_option(option)
            
            if result is None:
                break  # Exit
            
            # Wait for user
            try:
                input(f"\n{COLORS['BOLD']}Presiona Enter para continuar...{COLORS['END']}")
            except (EOFError, KeyboardInterrupt):
                print(f"\n{COLORS['YELLOW']}👋 Saliendo...{COLORS['END']}\n")
                break
                
        except KeyboardInterrupt:
            print(f"\n{COLORS['YELLOW']}👋 Saliendo...{COLORS['END']}\n")
            break
        except Exception as e:
            print(f"\n{COLORS['RED']}❌ Error inesperado: {e}{COLORS['END']}")
            input(f"\n{COLORS['BOLD']}Presiona Enter para continuar...{COLORS['END']}")

if __name__ == "__main__":
    main()
