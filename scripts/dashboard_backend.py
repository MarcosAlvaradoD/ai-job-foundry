"""
Dashboard Backend - Servidor seguro que lee del .env
NO expone API keys en el frontend

Uso:
1. py dashboard_backend.py
2. Abre http://localhost:5000 en el navegador
"""
import os
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager

# Load .env
load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)

# Initialize Sheet Manager
sheet_manager = SheetManager()

@app.route('/')
def index():
    """Serve dashboard.html"""
    return send_from_directory('../web', 'dashboard.html')

@app.route('/api/jobs')
def get_jobs():
    """
    API endpoint seguro que devuelve jobs desde Google Sheets
    NO expone credenciales
    """
    try:
        jobs = sheet_manager.get_all_jobs(tab='registry')
        
        # Transform to frontend format
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'company': job.get('Company', 'Unknown'),
                'role': job.get('Role', 'Unknown'),
                'location': job.get('Location', 'Unknown'),
                'remoteScope': job.get('RemoteScope', 'Unknown'),
                'applyURL': job.get('ApplyURL', ''),
                'source': job.get('Source', 'Unknown'),
                'fitScore': int(job.get('FitScore', 0)),
                'why': job.get('Why', ''),
                'status': job.get('Status', 'Unknown'),
                'createdAt': job.get('CreatedAt', ''),
                'seniority': job.get('Seniority', 'Unknown'),
                'comp': job.get('Comp', ''),
                'currency': job.get('Currency', '')
            })
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'count': len(jobs_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """
    Obtiene estadísticas agregadas
    """
    try:
        jobs = sheet_manager.get_all_jobs(tab='registry')
        
        total = len(jobs)
        high_match = len([j for j in jobs if j.get('FitScore', 0) >= 8])
        
        fit_scores = [j.get('FitScore', 0) for j in jobs if j.get('FitScore')]
        avg_fit = sum(fit_scores) / len(fit_scores) if fit_scores else 0
        
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        today_count = len([j for j in jobs if j.get('CreatedAt', '').startswith(today)])
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'highMatch': high_match,
                'avgFit': round(avg_fit, 1),
                'today': today_count
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DASHBOARD BACKEND - SERVIDOR SEGURO")
    print("="*60)
    print("\n✅ Credenciales cargadas desde .env")
    print("✅ NO expone API keys en frontend")
    print("\n📊 Dashboard disponible en:")
    print("   http://localhost:5000")
    print("\n📡 API endpoints:")
    print("   GET /api/jobs   - Lista de jobs")
    print("   GET /api/stats  - Estadísticas")
    print("\n⏸️  Ctrl+C para detener\n")
    
    app.run(debug=True, port=5000)
