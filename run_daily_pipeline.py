"""
📅 AI Job Foundry - Daily Pipeline (RESTORED - WORKING VERSION)
================================================================
Pipeline diario que usa los scripts que REALMENTE existen y funcionan.

Opciones:
  --all          : Pipeline completo
  --quick        : Pipeline rápido (bulletins + report)
  --emails       : Solo procesar emails (bulletins)
  --analyze      : Solo análisis AI
  --apply        : Solo auto-apply
  --expire       : Solo verificar expirados
  --report       : Solo reporte

Autor: Marcos Alberto Alvarado
Fecha: 2026-01-06 (RESTAURADO)
"""

import sys
import argparse
import logging
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

# ✅ FIX: Get absolute project root path
PROJECT_ROOT = Path(__file__).parent.absolute()

# ✅ FIX: Windows UTF-8 support for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 🔐 IMPORTAR VALIDADOR DE TOKENS
from oauth_token_validator import validate_token_or_exit

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def print_header():
    """Imprime el header del pipeline."""
    print("=" * 70)
    print("🚀 AI JOB FOUNDRY - DAILY PIPELINE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()


def print_footer(summary: dict):
    """Imprime el summary del pipeline."""
    print()
    print("=" * 70)
    print("📈 PIPELINE SUMMARY")
    print("=" * 70)
    for step, status in summary.items():
        if status == "PASS":
            icon = "✅"
        elif status == "SKIP":
            icon = "❌"
        else:
            icon = "❌"
        print(f"{step:<20} {icon} {status}")
    print("=" * 70)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()


def validate_oauth():
    """
    ✅ FUNCIONA PERFECTAMENTE
    Valida el token OAuth antes de comenzar.
    """
    logger.info("🔐 STEP 0: Validating OAuth token...")
    logger.info("")
    try:
        validate_token_or_exit(exit_code=1)
        logger.info("")
        logger.info("✅ OAuth token validated - pipeline ready to run")
        logger.info("")
        return True
    except SystemExit:
        logger.error("❌ OAuth validation failed")
        raise


def run_bulletin_processing():
    """
    ✅ USA: core/automation/job_bulletin_processor.py
    Procesa boletines de Glassdoor/LinkedIn/Indeed
    """
    logger.info("ℹ️  STEP 1: Processing bulletins...")
    try:
        script_path = PROJECT_ROOT / 'core' / 'automation' / 'job_bulletin_processor.py'
        # ✅ FIX: No capturar output, dejar que el script imprima directamente
        result = subprocess.run(
            [sys.executable, str(script_path)],
            timeout=300,
            check=False  # No raise exception on non-zero exit
        )
        
        if result.returncode == 0:
            logger.info("✅ Bulletins processed successfully")
            return "PASS"
        else:
            logger.error(f"❌ Bulletin processing failed with exit code: {result.returncode}")
            return "FAIL"
    except subprocess.TimeoutExpired:
        logger.error("❌ Bulletin processing timed out after 5 minutes")
        return "FAIL"
    except Exception as e:
        logger.error(f"❌ Bulletin processing failed: {e}")
        return "FAIL"


def run_ai_analysis():
    """
    ✅ USA: scripts/maintenance/calculate_linkedin_fit_scores.py
    Calcula FIT scores para LinkedIn jobs sin score
    """
    logger.info("ℹ️  STEP 2: Running AI analysis...")
    try:
        script_path = PROJECT_ROOT / 'scripts' / 'maintenance' / 'calculate_linkedin_fit_scores.py'
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600  # 10 minutes for AI analysis
        )
        
        if result.returncode == 0:
            logger.info("✅ AI analysis completed")
            return "PASS"
        else:
            logger.error(f"❌ AI analysis failed: {result.stderr[:200]}")
            return "FAIL"
    except Exception as e:
        logger.error(f"❌ AI analysis failed: {e}")
        return "FAIL"


def run_auto_apply(dry_run: bool = True):
    """
    ✅ USA: core/automation/auto_apply_linkedin_easy_complete.py
    Auto-aplica a ofertas con FIT 7+
    """
    mode = "DRY RUN" if dry_run else "LIVE"
    logger.info(f"ℹ️  STEP 3: Auto-apply ({mode})...")
    try:
        script_path = PROJECT_ROOT / 'core' / 'automation' / 'auto_apply_linkedin_easy_complete.py'
        args = [sys.executable, str(script_path)]
        if not dry_run:
            args.append('--live')
        args.extend(['--min-fit', '7', '--max-jobs', '5'])
        
        # ✅ FIX: No capture output para ver qué pasa en tiempo real
        # ✅ FIX: Timeout aumentado a 15 minutos (900s) para procesar múltiples jobs
        result = subprocess.run(
            args,
            timeout=900,  # 15 minutes for multiple applications
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Auto-apply completed ({mode})")
            return "PASS"
        else:
            logger.warning(f"⚠️  Auto-apply finished with warnings (code: {result.returncode})")
            return "PASS"  # Don't fail pipeline if some jobs failed
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Auto-apply timed out after 15 minutes")
        return "FAIL"
    except Exception as e:
        logger.error(f"❌ Auto-apply failed: {e}")
        return "FAIL"


def run_expiration_check():
    """
    ✅ USA: scripts/verifiers/EXPIRE_LIFECYCLE.py --mark
    Marca jobs expirados (>30 días)
    """
    logger.info("ℹ️  STEP 4: Checking for expired jobs...")
    try:
        script_path = PROJECT_ROOT / 'scripts' / 'verifiers' / 'EXPIRE_LIFECYCLE.py'
        result = subprocess.run(
            [sys.executable, str(script_path), '--mark'],
            capture_output=True,
            text=True,
            encoding='utf-8',  # ✅ FIX: Explicit UTF-8 encoding
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✅ Expiration check completed")
            return "PASS"
        else:
            logger.error(f"❌ Expiration check failed: {result.stderr[:200]}")
            return "FAIL"
    except Exception as e:
        logger.error(f"❌ Expiration check failed: {e}")
        return "FAIL"


def run_report_generation():
    """
    ✅ USA: Generación simple de reporte
    """
    logger.info("ℹ️  STEP 5: Generating report...")
    try:
        from core.sheets.sheet_manager import SheetManager
        sheet_manager = SheetManager()
        
        # Get jobs from all tabs
        jobs = sheet_manager.get_all_jobs()
        
        # Basic stats
        total_jobs = len(jobs)
        with_fitscore = len([j for j in jobs if j.get('FitScore')])
        applied = len([j for j in jobs if j.get('Status') == 'Applied'])
        expired = len([j for j in jobs if j.get('Status') == 'EXPIRED'])
        
        # Print report
        print()
        print("=" * 70)
        print("📊 DAILY REPORT")
        print("=" * 70)
        print(f"Total Jobs:       {total_jobs}")
        print(f"With FIT Score:   {with_fitscore}")
        print(f"Applied:          {applied}")
        print(f"Expired:          {expired}")
        print("=" * 70)
        print()
        
        logger.info("✅ Report generated")
        return "PASS"
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return "FAIL"


def run_full_pipeline(dry_run_apply=True):
    """Pipeline completo: bulletins + AI + apply + expire + report"""
    summary = {}
    
    # OAuth validation
    try:
        validate_oauth()
    except SystemExit:
        return {"OAuth": "FAIL"}
    
    # Run all steps
    summary["Bulletin Processing"] = run_bulletin_processing()
    summary["AI Analysis"] = run_ai_analysis()
    summary["Auto-Apply"] = run_auto_apply(dry_run=dry_run_apply)
    summary["Expire Check"] = run_expiration_check()
    summary["Report"] = run_report_generation()
    
    return summary


def run_quick_pipeline():
    """Pipeline rápido: bulletins + report"""
    summary = {}
    
    # OAuth validation
    try:
        validate_oauth()
    except SystemExit:
        return {"OAuth": "FAIL"}
    
    summary["Bulletin Processing"] = run_bulletin_processing()
    summary["Report"] = run_report_generation()
    
    return summary


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="AI Job Foundry - Daily Pipeline"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run full pipeline"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick pipeline (bulletins + report)"
    )
    parser.add_argument(
        "--emails",
        action="store_true",
        help="Process emails (bulletins)"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run AI analysis"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Run auto-apply (LIVE mode)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode for auto-apply"
    )
    parser.add_argument(
        "--expire",
        action="store_true",
        help="Check expired jobs"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate report"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    summary = {}
    
    # Ejecutar modo seleccionado
    if args.all:
        summary = run_full_pipeline(dry_run_apply=args.dry_run)
    elif args.quick:
        summary = run_quick_pipeline()
    elif args.emails:
        try:
            validate_oauth()
            summary["Bulletin Processing"] = run_bulletin_processing()
        except SystemExit:
            summary = {"OAuth": "FAIL"}
    elif args.analyze:
        try:
            validate_oauth()
            summary["AI Analysis"] = run_ai_analysis()
        except SystemExit:
            summary = {"OAuth": "FAIL"}
    elif args.apply:
        try:
            validate_oauth()
            summary["Auto-Apply"] = run_auto_apply(dry_run=args.dry_run)
        except SystemExit:
            summary = {"OAuth": "FAIL"}
    elif args.expire:
        try:
            validate_oauth()
            summary["Expire Check"] = run_expiration_check()
        except SystemExit:
            summary = {"OAuth": "FAIL"}
    elif args.report:
        try:
            validate_oauth()
            summary["Report"] = run_report_generation()
        except SystemExit:
            summary = {"OAuth": "FAIL"}
    else:
        # Default: quick pipeline
        summary = run_quick_pipeline()
    
    print_footer(summary)
    
    # Exit code
    if any(status == "FAIL" for status in summary.values()):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
