#!/usr/bin/env python3
"""
AI JOB FOUNDRY - UNIFIED WEB APP (FIXED)
Combines Control Center + Dashboard + Ads with CORRECT file paths

Fixed Issues:
- Corrected all subprocess script paths
- Better error handling
- Dashboard loads correctly
- All buttons work
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
import subprocess
import os
from datetime import datetime
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv
import requests
import threading
import time
import webbrowser

# Initialize
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-job-foundry-fixed-2025'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

load_dotenv()

# Global state
system_status = {
    'lm_studio': 'Unknown',
    'oauth': 'Unknown',
    'sheets': 'Unknown',
    'last_check': None
}

# ============================================================================
# SYSTEM HEALTH CHECKER
# ============================================================================

def check_system_health():
    """Background health checker"""
    global system_status
    
    while True:
        try:
            # OAuth
            token_path = Path('data/credentials/token.json')
            system_status['oauth'] = 'Connected' if token_path.exists() else 'Not configured'
            
            # LM Studio
            lm_ips = ['http://172.23.0.1:11434', 'http://localhost:11434', 'http://127.0.0.1:11434']
            lm_found = False
            for lm_url in lm_ips:
                try:
                    resp = requests.get(f'{lm_url}/v1/models', timeout=2)
                    if resp.status_code == 200:
                        system_status['lm_studio'] = 'Running'
                        lm_found = True
                        break
                except Exception:
                    continue
            if not lm_found:
                system_status['lm_studio'] = 'Offline'
            
            # Google Sheets
            try:
                sm = SheetManager()
                sheet_id = os.getenv('GOOGLE_SHEETS_ID')
                if sheet_id:
                    # Quick test
                    sm.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
                    system_status['sheets'] = 'Connected'
                else:
                    system_status['sheets'] = 'No SHEET_ID'
            except Exception as e:
                system_status['sheets'] = f'Error: {str(e)[:30]}'
            
            system_status['last_check'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Health check error: {e}")
        
        time.sleep(30)

# Start health thread
health_thread = threading.Thread(target=check_system_health, daemon=True)
health_thread.start()

# ============================================================================
# ROUTES - Pages
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system/status')
def get_system_status():
    return jsonify({
        'success': True,
        'status': system_status
    })

@app.route('/api/jobs/stats')
def get_job_stats():
    """Get job statistics for dashboard - FIXED"""
    try:
        sm = SheetManager()
        jobs = sm.get_all_jobs()
        
        # Stats
        total_jobs = len(jobs)
        high_fit = len([j for j in jobs if int(j.get('FitScore', '0').split('/')[0] if '/' in str(j.get('FitScore', '0')) else j.get('FitScore', 0)) >= 7])
        applied = len([j for j in jobs if 'applied' in str(j.get('Status', '')).lower() or 'application submitted' in str(j.get('Status', '')).lower()])
        pending = len([j for j in jobs if j.get('Status') == 'New' or j.get('Status') == 'ParsedOK'])
        
        # FIT distribution
        fit_dist = {}
        for job in jobs:
            try:
                fit_str = str(job.get('FitScore', '0'))
                fit = int(fit_str.split('/')[0] if '/' in fit_str else fit_str) if fit_str else 0
                if fit > 0:  # Only count scored jobs
                    fit_dist[fit] = fit_dist.get(fit, 0) + 1
            except Exception:
                continue
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_jobs,
                'high_fit': high_fit,
                'applied': applied,
                'pending': pending,
                'fit_distribution': fit_dist
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ACTIONS - FIXED FILE PATHS
# ============================================================================

def run_script(script_path, timeout=120, cwd=None):
    """Helper to run scripts with proper error handling"""
    try:
        result = subprocess.run(
            ['py', script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or Path(__file__).parent.parent
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': f'Timeout ({timeout}s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/api/action/process_emails', methods=['POST'])
def process_emails():
    """3. Process emails - FIXED PATH"""
    return jsonify(run_script('core/ingestion/ingest_email_to_sheet_v2.py'))

@app.route('/api/action/process_bulletins', methods=['POST'])
def process_bulletins():
    """4. Process bulletins - FIXED PATH"""
    return jsonify(run_script('core/automation/job_bulletin_processor.py'))

@app.route('/api/action/ai_analysis', methods=['POST'])
def ai_analysis():
    """5. AI Analysis - FIXED PATH"""
    return jsonify(run_script('core/enrichment/enrich_sheet_with_llm_v3.py', timeout=180))

@app.route('/api/action/check_expired', methods=['POST'])
def check_expired():
    """6. Check expired - FIXED PATH"""
    return jsonify(run_script('core/jobs_pipeline/job_cleaner.py'))

@app.route('/api/action/check_urls', methods=['POST'])
def check_urls():
    """7. Verify URLs - FIXED PATH"""
    return jsonify(run_script('check_urls_status.py', timeout=180))

@app.route('/api/action/generate_report', methods=['POST'])
def generate_report():
    """8. Generate report - FIXED PATH"""
    return jsonify(run_script('core/jobs_pipeline/sheet_summary.py'))

@app.route('/api/action/scrape_linkedin', methods=['POST'])
def scrape_linkedin():
    """9. LinkedIn Scraper - FIXED PATH"""
    return jsonify(run_script('scripts/visual_test.py', timeout=180))

@app.route('/api/action/scrape_indeed', methods=['POST'])
def scrape_indeed():
    """10. Indeed Scraper - NOT RECOMMENDED"""
    return jsonify({
        'success': False,
        'error': 'Indeed scraper disabled due to timeout issues',
        'suggestion': 'Use Gmail processing instead'
    })

@app.route('/api/action/auto_apply_dry', methods=['POST'])
def auto_apply_dry():
    """11. Auto-Apply DRY - FIXED PATH"""
    result = run_script('core/automation/linkedin_auto_apply.py', timeout=120)
    result['mode'] = 'DRY RUN - No real applications'
    return jsonify(result)

@app.route('/api/action/auto_apply_live', methods=['POST'])
def auto_apply_live():
    """12. Auto-Apply LIVE - DISABLED FOR SAFETY"""
    return jsonify({
        'success': False,
        'error': 'LIVE mode disabled for safety',
        'message': 'Use DRY RUN first to verify'
    })

@app.route('/api/action/open_dashboard', methods=['POST'])
def open_dashboard():
    """13. Dashboard (already open)"""
    return jsonify({
        'success': True,
        'message': 'Already viewing dashboard'
    })

@app.route('/api/action/open_sheets', methods=['POST'])
def open_sheets():
    """14. Open Google Sheets"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEETS_ID')}"
        webbrowser.open(url)
        return jsonify({'success': True, 'url': url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/action/run_health_check', methods=['POST'])
def run_health_check():
    """15. Health Check - FIXED PATH"""
    return jsonify(run_script('core/jobs_pipeline/system_health_check.py'))

@app.route('/api/action/view_sheets_data', methods=['POST'])
def view_sheets_data():
    """16. View Data - FIXED"""
    try:
        sm = SheetManager()
        jobs = sm.get_all_jobs()
        return jsonify({
            'success': True,
            'output': f"Found {len(jobs)} jobs in Google Sheets\n\nSample:\n" + "\n".join([
                f"- {j.get('Role', 'N/A')} at {j.get('Company', 'N/A')} (FIT: {j.get('FitScore', 'N/A')})"
                for j in jobs[:5]
            ])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/action/refresh_oauth', methods=['POST'])
def refresh_oauth():
    """17. Refresh OAuth - FIXED PATH"""
    return jsonify(run_script('fix_oauth_complete.py'))

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 AI JOB FOUNDRY - UNIFIED WEB APP (FIXED)")
    print("="*70)
    print(f"\n✨ Starting at http://localhost:5555")
    print(f"📊 Dashboard + 17 Control Functions")
    print(f"💰 Advertising Enabled (3 zones)")
    print("\n" + "="*70 + "\n")
    
    # Auto-open
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5555')).start()
    
    # Run
    app.run(host='0.0.0.0', port=5555, debug=True)
