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
    print("  1. 🚀 Pipeline Completo AUTO (scrape→emails→fit→cartas→APPLY) ⭐")
    print("  2. ⚡ Pipeline Rápido (emails + enrich + dedup + clean básico)")
    
    print(f"\n{COLORS['CYAN']}OPERACIONES INDIVIDUALES:{COLORS['END']}")
    print("  3. 📧 Procesar Emails Nuevos (reclutadores directos)")
    print("  4. 📬 Procesar Boletines (LinkedIn/Indeed/Glassdoor)")
    print("  5. 🤖 Análisis AI (calcular FIT SCORES)")
    print("  6. 🚫 Verificar Ofertas Expiradas (por fecha)")
    print("  7. 🔍 Verificar URLs (Playwright por plataforma)")
    print("  8. 📊 Generar Reporte")
    
    print(f"\n{COLORS['YELLOW']}SCRAPING:{COLORS['END']}")
    print("  9. 🔗 LinkedIn Scraper (Búsqueda Activa V3 + Notificaciones → Staging)")
    print("  10. 🔗 Indeed Scraper (buscar ofertas)")
    
    print(f"\n{COLORS['BLUE']}AUTO-APPLY:{COLORS['END']}")
    print("  11. 🎯 Auto-Apply (DRY RUN - simulación)  [Easy Apply + Sitios Externos]")
    print("  12. 💼 Auto-Apply (LIVE - aplica realmente) [Easy Apply + Workday/Greenhouse/Lever]")
    
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

    print(f"\n{COLORS['GREEN']}MANTENIMIENTO DEL SHEET:{COLORS['END']}")
    print("  26. 🔧 Mantenimiento Completo (enrich + dedup + clean + fit)")
    print("  27. 🏷️  Enriquecer Jobs Desconocidos (Company/Role via API)")
    print("  28. 🗑️  Eliminar Duplicados del Sheet")
    print("  29. 🚫 Limpiar Jobs Cerrados (no aceptan aplicaciones)")
    print("  30. 🤖 Recalcular FIT Scores (solo nuevos)")

    print(f"\n{COLORS['BLUE']}FLUJO DE APLICACION:{COLORS['END']}")
    print("  31. 📋 Reporte Pre-Apply (ver qué está listo)")
    print("  32. ✉️  Generar Cartas de Presentación (LiteLLM)")
    print("  33. 🚀 Auto-Apply V2 (DRY RUN — nuevo runner)")
    print("  34. 💼 Auto-Apply V2 (LIVE — aplica realmente)")

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
        # Pipeline completo end-to-end FULL AUTO:
        #   0. LinkedIn Scraping V3 LIVE → Staging  (nuevos jobs del día)
        #   1. Ingestion  — emails + AI + expire + report
        #   2. Maintenance — enrich + dedup + clean_closed + fit_scores (tab LinkedIn)
        #   3. Cover letters — genera cartas para jobs FIT>=8 sin carta
        #   4. Readiness   — reporte: cuántos listos para aplicar
        #   5. Auto-apply  — aplica a jobs FIT>=7 que ya están en tab LinkedIn
        print(f"\n{COLORS['CYAN']}Pipeline completo AUTO (6 pasos){COLORS['END']}")
        print(f"{COLORS['YELLOW']}Scraping → Emails → Mantenimiento → Cartas → Reporte → AUTO-APPLY{COLORS['END']}")

        # Pedir parámetros antes de empezar (para no interrumpir el pipeline a mitad)
        print(f"\n{COLORS['BOLD']}Configuración del Auto-Apply (paso 6/6):{COLORS['END']}")
        min_fit_input = input(f"  FIT mínimo para aplicar [default=7]: ").strip()
        min_fit = min_fit_input if min_fit_input else '7'
        max_apps_input = input(f"  Máximo de aplicaciones [default=10]: ").strip()
        max_apps = max_apps_input if max_apps_input else '10'

        print(f"\n{COLORS['RED']}⚠️  El pipeline aplicará AUTOMÁTICAMENTE a hasta {max_apps} jobs con FIT>={min_fit}{COLORS['END']}")
        confirm = input(f"{COLORS['BOLD']}¿Confirmar pipeline completo + auto-apply? (SI/S para confirmar): {COLORS['END']}").strip().upper()
        if confirm not in ['SI', 'S', 'YES', 'Y']:
            print(f"{COLORS['YELLOW']}Cancelado{COLORS['END']}")
            return False

        print(f"\n  [0/6] LinkedIn Scraping V3 (jobs nuevos → Staging)")
        run_command(
            ['py', 'core/ingestion/linkedin_search_scraper_v3.py', '--live'],
            'LinkedIn Búsqueda Activa V3 (nuevos jobs → Staging)'
        )
        # No bloqueamos si falla el scraping — el pipeline puede continuar con jobs existentes

        print(f"\n  [1/6] Emails + AI + Expire + Report")
        ok1 = run_command(
            ['py', 'run_daily_pipeline.py', '--all'],
            'Ingestion (emails + AI + expire + report)'
        )

        print(f"\n  [2/6] Mantenimiento Sheet (enrich + dedup + clean_closed + fit_scores)")
        ok2 = run_command(
            ['py', 'scripts/maintenance/run_maintenance.py'],
            'Mantenimiento (enrich + dedup + cerradas + FIT scores)'
        )

        print(f"\n  [3/6] Generando cartas de presentacion (FIT>=8, max 10)")
        run_command(
            ['py', 'scripts/apply/generate_cover_letters.py', '--min', '8', '--limit', '10'],
            'Cover letters (FIT>=8, max 10 cartas nuevas)'
        )

        print(f"\n  [4/6] Reporte pre-apply")
        run_command(
            ['py', 'scripts/apply/check_apply_readiness.py', '--min', min_fit],
            f'Reporte pre-apply (FIT >= {min_fit})'
        )

        print(f"\n  [5/6] Auto-Apply LIVE (FIT>={min_fit}, max {max_apps} jobs)")
        print(f"  {COLORS['YELLOW']}Aplicando: Easy Apply + Workday / Greenhouse / Lever...{COLORS['END']}")
        ok5 = run_command(
            ['py', 'scripts/apply/run_autoapply.py',
             '--submit', '--min-fit', min_fit, '--max', max_apps,
             '--no-confirm', '--external'],
            f'Auto-Apply LIVE (FIT>={min_fit}, max={max_apps}, Easy+External)'
        )

        print(f"\n{COLORS['GREEN']}{'='*60}{COLORS['END']}")
        print(f"{COLORS['GREEN']}✅ Pipeline completo finalizado{COLORS['END']}")
        print(f"  • Jobs nuevos scrapeados → Staging (revisar y promover a LinkedIn)")
        print(f"  • FIT scores calculados para jobs en tab LinkedIn")
        print(f"  • Auto-apply ejecutado para jobs con FIT>={min_fit}")
        print(f"{COLORS['GREEN']}{'='*60}{COLORS['END']}")

        return ok1 and ok2

    elif option == '2':
        # Pipeline rapido: emails + mantenimiento basico (sin cartas ni apply)
        print(f"\n{COLORS['CYAN']}Pipeline rapido (2 pasos){COLORS['END']}")

        print(f"\n  [1/2] Emails + Report")
        ok1 = run_command(
            ['py', 'run_daily_pipeline.py', '--emails', '--report'],
            'Emails + Report'
        )

        print(f"\n  [2/2] Mantenimiento rapido (enrich + dedup + clean, max 20 jobs)")
        ok2 = run_command(
            ['py', 'scripts/maintenance/run_maintenance.py', '--only', 'enrich'],
            'Enrich jobs desconocidos'
        )
        run_command(
            ['py', 'scripts/maintenance/run_maintenance.py', '--only', 'dedup'],
            'Dedup'
        )
        run_command(
            ['py', 'scripts/maintenance/run_maintenance.py', '--only', 'clean'],
            'Limpiar cerradas (max 20)'
        )
        return ok1 and ok2
    
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
        # LinkedIn Scraper — dos modos: búsqueda activa V3 o notificaciones
        print(f"\n{COLORS['CYAN']}🔍 LinkedIn Scraper{COLORS['END']}")
        print(f"\n{COLORS['BOLD']}Modo:{COLORS['END']}")
        print(f"  {COLORS['GREEN']}1. 🚀 Búsqueda Activa V3 (DRY RUN){COLORS['END']}  — nuevas keywords ERP/SAP/PM → pestaña Staging")
        print(f"  {COLORS['GREEN']}2. 💼 Búsqueda Activa V3 (LIVE){COLORS['END']}     — guarda en pestaña Staging del Sheet")
        print(f"  {COLORS['CYAN']}3. 📩 Notificaciones Scraper (solo extracción){COLORS['END']}")
        print(f"  {COLORS['CYAN']}4. 📩 Notificaciones Workflow completo (DRY RUN){COLORS['END']}")
        print(f"  {COLORS['CYAN']}5. 📩 Notificaciones Workflow completo (LIVE){COLORS['END']}")

        choice = input(f"\n{COLORS['BOLD']}Selecciona [1-5]: {COLORS['END']}").strip()

        if choice == '1':
            return run_command(
                ['py', 'core/ingestion/linkedin_search_scraper_v3.py', '--dry-run'],
                '🔍 LinkedIn Búsqueda Activa V3 (DRY RUN)'
            )
        elif choice == '2':
            print(f"\n{COLORS['YELLOW']}Jobs nuevos se guardarán en pestaña 'Staging' del Sheet.{COLORS['END']}")
            print(f"Revísalos ahí y mueve los buenos a 'LinkedIn' para que entren al pipeline.")
            confirm = input(f"\n{COLORS['BOLD']}¿Continuar? (S/n): {COLORS['END']}").strip().upper()
            if confirm in ['S', 'SI', 'YES', 'Y', '']:
                return run_command(
                    ['py', 'core/ingestion/linkedin_search_scraper_v3.py', '--live'],
                    '💼 LinkedIn Búsqueda Activa V3 (LIVE → Staging)'
                )
            else:
                print(f"{COLORS['YELLOW']}Cancelado{COLORS['END']}")
                return False
        elif choice == '3':
            return run_command(
                ['py', 'run_linkedin_workflow.py', '--scrape-only'],
                '📩 LinkedIn Notifications Scraper (solo extracción)'
            )
        elif choice == '4':
            return run_command(
                ['py', 'run_linkedin_workflow.py', '--all'],
                '📩 LinkedIn Notifications Workflow Completo (DRY RUN)'
            )
        elif choice == '5':
            print(f"\n{COLORS['RED']}⚠️  MODO LIVE - Aplicará a ofertas reales{COLORS['END']}")
            confirm = input(f"{COLORS['BOLD']}¿Estás seguro? (escribe 'SI' o 'S' para confirmar): {COLORS['END']}").strip().upper()
            if confirm in ['SÍ', 'SI', 'S', 'YES', 'Y']:
                return run_command(
                    ['py', 'run_linkedin_workflow.py', '--all', '--live'],
                    '📩 LinkedIn Notifications Workflow Completo (LIVE)'
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
        # Auto-Apply DRY RUN — Easy Apply + External Sites
        print(f"\n{COLORS['CYAN']}🤖 Auto-Apply DRY RUN{COLORS['END']}")
        print(f"Cubre: LinkedIn Easy Apply + Workday / Greenhouse / Lever / SmartRecruiters")
        print(f"Usa IA local (LM Studio) para preguntas personalizadas\n")

        min_fit = input(f"{COLORS['BOLD']}FIT Score mínimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        max_jobs = input(f"{COLORS['BOLD']}Máximo de jobs [default=5]: {COLORS['END']}").strip()
        max_jobs = max_jobs if max_jobs else '5'
        ext = input(f"{COLORS['BOLD']}¿Incluir sitios externos? Workday/Greenhouse/etc (S/n): {COLORS['END']}").strip().upper()
        ext_flag = ['--external'] if ext not in ['N', 'NO'] else []

        return run_command(
            ['py', 'scripts/apply/run_autoapply.py', '--dry-run',
             '--min-fit', min_fit, '--max', max_jobs] + ext_flag,
            f'Auto-Apply DRY RUN (FIT>={min_fit}, max={max_jobs})'
        )

    elif option == '12':
        # Auto-Apply LIVE — Easy Apply + External Sites
        print(f"\n{COLORS['RED']}⚠️  MODO LIVE — Se enviarán aplicaciones REALES{COLORS['END']}")
        print(f"Cubre: LinkedIn Easy Apply + Workday / Greenhouse / Lever / SmartRecruiters")
        print(f"Usa IA local (LM Studio) para preguntas personalizadas\n")

        min_fit = input(f"{COLORS['BOLD']}FIT Score mínimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        max_jobs = input(f"{COLORS['BOLD']}Máximo de jobs [default=5]: {COLORS['END']}").strip()
        max_jobs = max_jobs if max_jobs else '5'
        ext = input(f"{COLORS['BOLD']}¿Incluir sitios externos? Workday/Greenhouse/etc (S/n): {COLORS['END']}").strip().upper()
        ext_flag = ['--external'] if ext not in ['N', 'NO'] else []

        confirm = input(f"\n{COLORS['RED']}{COLORS['BOLD']}¿Aplicar REALMENTE a hasta {max_jobs} ofertas? (SI/S): {COLORS['END']}").strip().upper()
        if confirm in ['SÍ', 'SI', 'S', 'YES', 'Y']:
            return run_command(
                ['py', 'scripts/apply/run_autoapply.py', '--submit',
                 '--min-fit', min_fit, '--max', max_jobs] + ext_flag,
                f'Auto-Apply LIVE (FIT>={min_fit}, max={max_jobs})'
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
        lm_model = os.getenv("LM_STUDIO_MODEL", "Qwen2.5-14B")
        print(f"\n{COLORS['CYAN']}Requiere: LM Studio corriendo — modelo activo: {lm_model}{COLORS['END']}")
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
    
    # ── MANTENIMIENTO DEL SHEET ───────────────────────────────────────────────

    elif option == '26':
        # Mantenimiento completo
        print(f"\n{COLORS['CYAN']}Modo:{COLORS['END']}")
        print("  1. Normal (limita clean a 30 jobs — rapido)")
        print("  2. Deep (sin limite — completo, tarda mas)")
        print("  3. Dry-run (preview sin cambios)")
        m = input(f"\n{COLORS['BOLD']}Selecciona [1/2/3, default=1]: {COLORS['END']}").strip()
        extra = []
        if m == '2':
            extra = ['--deep']
        elif m == '3':
            extra = ['--dry-run']
        return run_command(
            ['py', 'scripts/maintenance/run_maintenance.py'] + extra,
            'Mantenimiento completo (enrich + dedup + clean_closed + fit_scores)'
        )

    elif option == '27':
        # Enriquecer jobs desconocidos
        limit = input(f"{COLORS['BOLD']}Limite de jobs a enriquecer [default=50]: {COLORS['END']}").strip()
        limit = limit if limit else '50'
        return run_command(
            ['py', 'scripts/maintenance/enrich_unknown_jobs.py', '--limit', limit],
            f'Enriqueciendo Company/Role para jobs desconocidos (max {limit})'
        )

    elif option == '28':
        # Eliminar duplicados
        print(f"\n{COLORS['CYAN']}Modo:{COLORS['END']}")
        print("  1. Delete (elimina filas duplicadas — default)")
        print("  2. Dry-run (preview sin cambios)")
        m = input(f"\n{COLORS['BOLD']}Selecciona [1/2, default=1]: {COLORS['END']}").strip()
        extra = ['--dry-run'] if m == '2' else []
        return run_command(
            ['py', 'scripts/maintenance/deduplicate_linkedin_sheet.py'] + extra,
            'Eliminando filas duplicadas del Sheet'
        )

    elif option == '29':
        # Limpiar jobs cerrados
        print(f"\n{COLORS['CYAN']}Modo:{COLORS['END']}")
        print("  1. Delete (elimina jobs cerrados — default)")
        print("  2. Mark (marca como Skip-Closed, no elimina)")
        print("  3. Dry-run (preview sin cambios)")
        m = input(f"\n{COLORS['BOLD']}Selecciona [1/2/3, default=1]: {COLORS['END']}").strip()
        limit = input(f"{COLORS['BOLD']}Limite de jobs a verificar [default=30, 0=todos]: {COLORS['END']}").strip()
        limit = limit if limit else '30'
        extra = []
        if m == '2':
            extra = ['--mark']
        elif m == '3':
            extra = ['--dry-run']
        if limit != '0':
            extra += ['--limit', limit]
        return run_command(
            ['py', 'scripts/maintenance/clean_closed_jobs.py'] + extra,
            f'Limpiando jobs cerrados (verificando max {limit})'
        )

    elif option == '30':
        # Recalcular FIT scores
        return run_command(
            ['py', 'scripts/maintenance/calculate_linkedin_fit_scores.py'],
            'Calculando FIT scores para jobs sin analizar'
        )

    # ── FLUJO DE APLICACION ───────────────────────────────────────────────────

    elif option == '31':
        # Reporte pre-apply
        min_fit = input(f"{COLORS['BOLD']}FIT minimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        show = input(f"{COLORS['BOLD']}Mostrar lista de jobs READY? (s/N): {COLORS['END']}").strip().lower()
        extra = ['--show-ready'] if show == 's' else []
        return run_command(
            ['py', 'scripts/apply/check_apply_readiness.py', '--min', min_fit] + extra,
            f'Reporte de readiness (FIT >= {min_fit})'
        )

    elif option == '32':
        # Generar cartas de presentacion
        min_fit = input(f"{COLORS['BOLD']}FIT minimo para generar carta [default=8]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '8'
        limit = input(f"{COLORS['BOLD']}Max cartas a generar [default=10]: {COLORS['END']}").strip()
        limit = limit if limit else '10'
        dry = input(f"{COLORS['BOLD']}Dry-run (preview sin guardar)? (s/N): {COLORS['END']}").strip().lower()
        extra = ['--dry-run'] if dry == 's' else []
        return run_command(
            ['py', 'scripts/apply/generate_cover_letters.py',
             '--min', min_fit, '--limit', limit] + extra,
            f'Generando cartas de presentacion (FIT >= {min_fit}, max {limit})'
        )

    elif option == '33':
        # Auto-Apply V2 DRY RUN
        min_fit = input(f"{COLORS['BOLD']}FIT minimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        max_apps = input(f"{COLORS['BOLD']}Max aplicaciones [default=5]: {COLORS['END']}").strip()
        max_apps = max_apps if max_apps else '5'
        return run_command(
            ['py', 'scripts/apply/run_autoapply.py',
             '--dry-run', '--min-fit', min_fit, '--max', max_apps],
            f'Auto-Apply V2 DRY-RUN (FIT>={min_fit}, max={max_apps})'
        )

    elif option == '34':
        # Auto-Apply V2 LIVE
        print(f"\n{COLORS['RED']}⚠️  MODO LIVE — Se enviarán aplicaciones REALES a LinkedIn{COLORS['END']}")
        min_fit = input(f"{COLORS['BOLD']}FIT minimo [default=7]: {COLORS['END']}").strip()
        min_fit = min_fit if min_fit else '7'
        max_apps = input(f"{COLORS['BOLD']}Max aplicaciones [default=5]: {COLORS['END']}").strip()
        max_apps = max_apps if max_apps else '5'
        confirm = input(f"\n{COLORS['RED']}{COLORS['BOLD']}¿Aplicar REALMENTE a hasta {max_apps} jobs? (escribe SI): {COLORS['END']}").strip().upper()
        if confirm in ['SI', 'S', 'YES', 'Y']:
            return run_command(
                ['py', 'scripts/apply/run_autoapply.py',
                 '--submit', '--min-fit', min_fit, '--max', max_apps],
                f'Auto-Apply V2 LIVE (FIT>={min_fit}, max={max_apps})'
            )
        else:
            print(f"{COLORS['YELLOW']}Cancelado{COLORS['END']}")
            return False

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
            option = input(f"{COLORS['BOLD']}Selecciona una opción [0-34]: {COLORS['END']}").strip()
            
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
