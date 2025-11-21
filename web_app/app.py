#!/usr/bin/env python3
"""
AI Job Foundry - Web Application
Modern UI for job search automation

Features:
- Control Center (run pipeline, scrapers, etc.)
- Dashboard (jobs visualization)
- Logs viewer (real-time)
- Settings (edit .env)
- System status

Usage:
    py web_app/app.py
    # Opens at http://localhost:5000
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request, Response
import subprocess
import json
from datetime import datetime
from core.sheets.sheet_manager import SheetManager
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-job-foundry-secret-key-2025'

# Load environment
load_dotenv()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/jobs')
def get_jobs():
    """Get all jobs from Google Sheets"""
    try:
        sm = SheetManager()
        jobs = sm.get_all_jobs()
        return jsonify({'success': True, 'jobs': jobs, 'count': len(jobs)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get job statistics"""
    try:
        sm = SheetManager()
        jobs = sm.get_all_jobs()
        
        stats = {
            'total': len(jobs),
            'with_urls': len([j for j in jobs if j.get('ApplyURL', '').strip()]),
            'high_fit': len([j for j in jobs if float(j.get('FitScore', 0) or 0) >= 7]),
            'by_status': {},
            'by_source': {},
            'avg_fit': 0
        }
        
        # Count by status
        for job in jobs:
            status = job.get('Status', 'Unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
        # Count by source
        for job in jobs:
            source = job.get('Source', 'Unknown')
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        # Calculate average FIT
        fits = [float(j.get('FitScore', 0) or 0) for j in jobs if j.get('FitScore')]
        if fits:
            stats['avg_fit'] = round(sum(fits) / len(fits), 1)
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run/<command>', methods=['POST'])
def run_command(command):
    """Execute pipeline commands"""
    commands_map = {
        'pipeline_full': ['py', 'run_daily_pipeline.py', '--all'],
        'pipeline_quick': ['py', 'run_daily_pipeline.py', '--analyze'],
        'process_emails': ['py', 'control_center.py', '--option', '3'],
        'process_bulletins': ['py', 'control_center.py', '--option', '4'],
        'linkedin_scrape': ['py', 'scripts/visual_test.py'],
        'verify_urls': ['py', 'verify_job_status.py', '--high-fit'],
        'standardize_status': ['py', 'standardize_status_v2.py'],
    }
    
    if command not in commands_map:
        return jsonify({'success': False, 'error': 'Invalid command'}), 400
    
    try:
        # Run command in background
        result = subprocess.Popen(
            commands_map[command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'success': True,
            'message': f'Command {command} started',
            'pid': result.pid
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
def system_status():
    """Get system status"""
    try:
        status = {
            'oauth': 'Unknown',
            'lm_studio': 'Unknown',
            'sheets': 'Unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Check OAuth
        token_path = Path('data/credentials/token.json')
        if token_path.exists():
            status['oauth'] = 'Connected'
        else:
            status['oauth'] = 'Not configured'
        
        # Check LM Studio
        import requests
        try:
            resp = requests.get('http://172.23.0.1:11434/v1/models', timeout=2)
            if resp.status_code == 200:
                status['lm_studio'] = 'Running'
            else:
                status['lm_studio'] = 'Error'
        except:
            status['lm_studio'] = 'Offline'
        
        # Check Sheets
        try:
            sm = SheetManager()
            jobs = sm.get_all_jobs()
            status['sheets'] = f'Connected ({len(jobs)} jobs)'
        except:
            status['sheets'] = 'Error'
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/env', methods=['GET', 'POST'])
def env_settings():
    """Get or update .env settings"""
    env_path = Path('.env')
    
    if request.method == 'GET':
        # Read current .env
        try:
            with open(env_path, 'r') as f:
                content = f.read()
            return jsonify({'success': True, 'content': content})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        # Update .env
        try:
            data = request.get_json()
            content = data.get('content', '')
            
            with open(env_path, 'w') as f:
                f.write(content)
            
            # Reload environment
            load_dotenv(override=True)
            
            return jsonify({'success': True, 'message': '.env updated'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Stream logs in real-time using Server-Sent Events"""
    def generate():
        log_dir = Path('logs/powershell')
        if not log_dir.exists():
            yield f"data: No logs found\n\n"
            return
        
        # Get most recent log file
        log_files = sorted(log_dir.glob('session_*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
        if not log_files:
            yield f"data: No log files\n\n"
            return
        
        latest_log = log_files[0]
        
        # Stream log content
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                yield f"data: {json.dumps({'line': line.strip()})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("AI JOB FOUNDRY - WEB APPLICATION")
    print("="*70)
    print("\nStarting web server...")
    print("Open: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
