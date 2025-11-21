#!/usr/bin/env python3
"""
Dashboard Server - Reads .env and serves dashboard with API key
Usage: py serve_dashboard.py
Then open: http://localhost:8000
"""
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom handler that injects API key into dashboard.html"""
    
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read dashboard template
            dashboard_path = Path(__file__).parent / 'dashboard.html'
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get API key from .env (if exists)
            api_key = os.getenv('GOOGLE_SHEETS_API_KEY', '')
            
            # Inject API key into JavaScript
            if api_key:
                # Replace placeholder
                content = content.replace(
                    "const API_KEY = '';  // Your API Key",
                    f"const API_KEY = '{api_key}';  // From .env"
                )
            
            self.wfile.write(content.encode('utf-8'))
        
        elif self.path == '/api/config':
            # API endpoint for config
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            config = {
                'apiKey': os.getenv('GOOGLE_SHEETS_API_KEY', ''),
                'sheetId': os.getenv('GOOGLE_SHEETS_ID', ''),
            }
            self.wfile.write(json.dumps(config).encode('utf-8'))
        else:
            # Serve other files normally
            super().do_GET()

def main():
    port = 8000
    os.chdir(Path(__file__).parent)  # Change to web directory
    
    server = HTTPServer(('localhost', port), DashboardHandler)
    
    print("="*70)
    print("🚀 AI JOB FOUNDRY - DASHBOARD SERVER")
    print("="*70)
    print(f"📊 Dashboard running at: http://localhost:{port}")
    print(f"📂 Serving from: {Path.cwd()}")
    
    api_key = os.getenv('GOOGLE_SHEETS_API_KEY', '')
    if api_key:
        print(f"✅ API Key loaded from .env: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("⚠️  No GOOGLE_SHEETS_API_KEY in .env")
        print("   Dashboard will use placeholder. Add to .env:")
        print("   GOOGLE_SHEETS_API_KEY=your-key-here")
    
    print("\n🔍 Google Sheets ID:", os.getenv('GOOGLE_SHEETS_ID', 'NOT SET'))
    print("\n💡 Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard server stopped.")
        server.server_close()

if __name__ == '__main__':
    main()
