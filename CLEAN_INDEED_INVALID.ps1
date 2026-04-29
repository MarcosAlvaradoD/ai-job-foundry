# ============================================================================
# LIMPIEZA JOBS DE INDEED INVÁLIDOS
# ============================================================================

Write-Host ""
Write-Host "🧹 LIMPIEZA DE JOBS INDEED INVÁLIDOS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$project = "C:\Users\MSI\Desktop\ai-job-foundry"
Set-Location $project

Write-Host "📋 Descripción del problema:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Los 3 jobs actuales en la pestaña Indeed tienen URLs inválidas:" -ForegroundColor White
Write-Host "   https://mx.indeed.com/?from=profOnboarding&onboardingData=ey..." -ForegroundColor Red
Write-Host ""
Write-Host "   Estas son URLs de ONBOARDING, no de jobs reales." -ForegroundColor White
Write-Host "   Por eso el verifier marca todo como 'UNKNOWN'." -ForegroundColor White
Write-Host ""
Write-Host "   URLs VÁLIDAS de Indeed deberían ser:" -ForegroundColor Green
Write-Host "   https://to.indeed.com/XXXXXXX" -ForegroundColor Green
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "¿Eliminar los 3 jobs de prueba de Indeed? (s/n)"

if ($response -ne "s") {
    Write-Host ""
    Write-Host "❌ Cancelado por el usuario" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 0
}

Write-Host ""
Write-Host "🗑️  Ejecutando limpieza..." -ForegroundColor Cyan
Write-Host ""

# Script Python para limpiar
$pythonScript = @"
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent
load_dotenv(project_root / '.env')

from core.sheets.sheet_manager import SheetManager

def clean_indeed_test_jobs():
    """
    Elimina los 3 jobs de prueba de Indeed con URLs inválidas
    """
    manager = SheetManager()
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    print("📋 Obteniendo datos de Indeed...")
    
    # Get Indeed tab data
    result = manager.service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Indeed!A1:Z100'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("❌ No data found")
        return
    
    headers = values[0]
    rows = values[1:]
    
    # Find ApplyURL column
    if 'ApplyURL' not in headers:
        print("❌ ApplyURL column not found")
        return
    
    url_idx = headers.index('ApplyURL')
    
    # Find invalid URLs (onboarding URLs)
    invalid_rows = []
    for i, row in enumerate(rows, start=2):
        if len(row) > url_idx:
            url = row[url_idx]
            if 'profOnboarding' in url:
                invalid_rows.append(i)
    
    if not invalid_rows:
        print("✅ No invalid jobs found")
        return
    
    print(f"🔍 Found {len(invalid_rows)} invalid jobs:")
    for row_num in invalid_rows:
        print(f"   - Row {row_num}")
    
    # Get sheet ID
    sheet_metadata = manager.service.spreadsheets().get(
        spreadsheetId=sheet_id
    ).execute()
    
    indeed_sheet_id = None
    for sheet in sheet_metadata.get('sheets', []):
        if sheet['properties']['title'] == 'Indeed':
            indeed_sheet_id = sheet['properties']['sheetId']
            break
    
    if not indeed_sheet_id:
        print("❌ Indeed sheet ID not found")
        return
    
    # Delete rows (from bottom to top)
    invalid_rows.sort(reverse=True)
    
    requests = []
    for row_num in invalid_rows:
        requests.append({
            'deleteDimension': {
                'range': {
                    'sheetId': indeed_sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': row_num - 1,
                    'endIndex': row_num
                }
            }
        })
    
    # Execute batch delete
    manager.service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()
    
    print(f"✅ Deleted {len(invalid_rows)} invalid jobs from Indeed tab")

if __name__ == '__main__':
    clean_indeed_test_jobs()
"@

# Guardar script temporal
$pythonScript | Out-File -FilePath "temp_clean_indeed.py" -Encoding UTF8

# Ejecutar script
py temp_clean_indeed.py

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Los jobs reales de Indeed llegarán vía:" -ForegroundColor White
    Write-Host "   - Emails de alertas (bulletin processor)" -ForegroundColor White
    Write-Host "   - Indeed scraper (cuando esté implementado)" -ForegroundColor White
    Write-Host ""
    Write-Host "2. El verifier de Indeed funcionará correctamente" -ForegroundColor White
    Write-Host "   con URLs válidas formato:" -ForegroundColor White
    Write-Host "   https://to.indeed.com/XXXXXXX" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host "❌ ERROR EN LIMPIEZA" -ForegroundColor Red
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host ""
}

# Limpiar script temporal
Remove-Item "temp_clean_indeed.py" -Force -ErrorAction SilentlyContinue

Write-Host ""
pause
