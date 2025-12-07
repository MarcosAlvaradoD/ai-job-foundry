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
    
    # Run PowerShell startup check
    try:
        result = subprocess.run(
            ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', 'startup_check_v2.ps1'],
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
        print(f"{COLORS['YELLOW']}⚠️  startup_check_v2.ps1 no encontrado - continuando sin verificar{COLORS['END']}")
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
    print("  11. 🎯 Auto-Apply (DRY RUN - no aplica real)")
    print("  12. 💼 Auto-Apply (LIVE - aplica realmente)")
    
    print(f"\n{COLORS['HEADER']}VISUALIZACIÓN:{COLORS['END']}")
    print("  13. 📊 Abrir Dashboard")
    print("  14. 📄 Ver Google Sheets")
    
    print(f"\n{COLORS['BOLD']}UTILIDADES:{COLORS['END']}")
    print("  15. 🔧 Ver Configuración (.env)")
    print("  16. 📚 Ver Documentación")
    print("  17. 🎤 Interview Copilot (prep entrevistas)")
    print("  18. 📩 Actualizar Status desde Emails (entrevistas, rechazos)")
    print("  19. 🚫 Marcar Jobs Expirados (auto-detect)")
    
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
                ['py', 'LINKEDIN_SMART_VERIFIER_V3.py'] + limit_arg,
                'Verificando LinkedIn (con login automático y cookies)'
            )
        elif platform == '2':
            # Indeed
            return run_command(
                ['py', 'INDEED_SMART_VERIFIER.py'] + limit_arg,
                'Verificando Indeed'
            )
        elif platform == '3':
            # Glassdoor
            return run_command(
                ['py', 'GLASSDOOR_SMART_VERIFIER.py'] + limit_arg,
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
        # LinkedIn Scraper
        print(f"\n{COLORS['YELLOW']}LinkedIn Scraper requiere configuración manual.{COLORS['END']}")
        print(f"Ver: core/ingestion/linkedin_scraper_V2.py")
        print(f"O usar: py scripts/visual_test.py")
        return False
    
    elif option == '10':
        # Indeed Scraper
        print(f"\n{COLORS['YELLOW']}Indeed Scraper tiene problemas de timeout.{COLORS['END']}")
        print(f"Prioridad baja - LinkedIn es suficiente.")
        return False
    
    elif option == '11':
        # Auto-Apply DRY RUN
        return run_command(
            ['py', 'run_daily_pipeline.py', '--apply', '--dry-run'],
            'Auto-Apply (DRY RUN - sin aplicar realmente)'
        )
    
    elif option == '12':
        # Auto-Apply LIVE
        print(f"\n{COLORS['RED']}⚠️  MODO LIVE - Aplicará a ofertas reales{COLORS['END']}")
        confirm = input(f"{COLORS['BOLD']}¿Estás seguro? (escribe 'SÍ' para confirmar): {COLORS['END']}").strip()
        if confirm == 'SÍ':
            return run_command(
                ['py', 'run_daily_pipeline.py', '--apply'],
                'Auto-Apply (LIVE - aplicando realmente)'
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
        # Interview Copilot
        print(f"\n{COLORS['CYAN']}🎤 Interview Copilot{COLORS['END']}")
        print("\nOpciones:")
        print("  1. Session Recorder (grabar + transcribir)")
        print("  2. Simple Mode (sin grabar)")
        print("  3. V2 con Job Context")
        
        copilot_option = input(f"\n{COLORS['BOLD']}Selecciona [1/2/3]: {COLORS['END']}").strip()
        
        if copilot_option == '1':
            return run_command(
                ['py', 'core/copilot/interview_copilot_session_recorder.py'],
                'Interview Copilot - Session Recorder'
            )
        elif copilot_option == '2':
            return run_command(
                ['py', 'core/copilot/interview_copilot_simple.py'],
                'Interview Copilot - Simple Mode'
            )
        elif copilot_option == '3':
            return run_command(
                ['py', 'core/copilot/interview_copilot_v2.py'],
                'Interview Copilot V2 - Job Context'
            )
        else:
            print(f"{COLORS['RED']}❌ Opción inválida{COLORS['END']}")
            return False
    elif option == '18':
        # Actualizar status desde emails
        return run_command(
            ['py', 'update_status_from_emails.py'],
            'Actualizando status desde emails (entrevistas, rechazos)'
        )
    
    elif option == '19':
        # Marcar jobs expirados
        return run_command(
            ['py', 'EXPIRE_LIFECYCLE.py', '--mark'],
            'Marcando jobs expirados (>30 días)'
        )
    
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
    
    while True:
        print_header()
        print_menu()
        
        try:
            option = input(f"{COLORS['BOLD']}Selecciona una opción [0-19]: {COLORS['END']}").strip()
            
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
