"""
RUN DASHBOARD - Servidor simple para el dashboard HTML
Permite que el navegador acceda al JSON
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Permitir CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Solo mostrar requests importantes
        if not self.path.endswith(('.ico', '.map')):
            print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"\n{'='*60}")
    print(f"  📊 JOB TRACKER DASHBOARD")
    print(f"{'='*60}\n")
    print(f"  Servidor iniciado en puerto {PORT}")
    print(f"  📁 Sirviendo desde: {project_root}\n")
    print(f"  🌐 Abre en tu navegador:")
    print(f"     http://localhost:{PORT}/dashboard.html\n")
    print(f"  ⚠️  Para detener: Ctrl+C\n")
    print(f"{'='*60}\n")
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print(f"  🛑 Servidor detenido")
            print(f"{'='*60}\n")

if __name__ == "__main__":
    main()