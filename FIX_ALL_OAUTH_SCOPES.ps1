#!/usr/bin/env pwsh
# ================================================================
# AI JOB FOUNDRY - FIX ALL OAUTH SCOPES
# ================================================================
# Remueve scopes innecesarios (gmail.send, calendar) de todos
# los archivos Python que los tienen definidos
# ================================================================

Write-Host "`n============================================================"
Write-Host "  🔧 FIXING OAUTH SCOPES IN ALL FILES"
Write-Host "============================================================`n"

$CORRECT_SCOPES = @"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]
"@

# Lista de archivos a corregir (excepto send_test_email.py que SÍ necesita gmail.send)
$FILES_TO_FIX = @(
    "core\ingestion\ingest_email_to_sheet_v2.py",
    "core\jobs_pipeline\enrich_sheet_with_llm.py",
    "core\jobs_pipeline\ingest_email_to_sheet_v2.py",
    "scripts\fix_oauth_scope_error.py",
    "scripts\oauth\fix_oauth_scopes.py",
    "scripts\oauth\fix_oauth_complete.py",
    "scripts\oauth\verify_oauth.py",
    "scripts\oauth\test_oauth.py"
)

$totalFiles = $FILES_TO_FIX.Count
$fixedCount = 0
$errorCount = 0

foreach ($file in $FILES_TO_FIX) {
    $filePath = Join-Path $PSScriptRoot $file
    
    if (Test-Path $filePath) {
        Write-Host "📝 Processing: $file" -ForegroundColor Cyan
        
        try {
            # Leer contenido
            $content = Get-Content $filePath -Raw -Encoding UTF8
            
            # Reemplazar SCOPES incorrectos
            $pattern = 'SCOPES\s*=\s*\[[^\]]*gmail\.send[^\]]*\]'
            
            if ($content -match $pattern) {
                # Preservar indentación
                $match = [regex]::Match($content, $pattern)
                $originalIndent = ""
                $lines = $content.Substring(0, $match.Index).Split("`n")
                if ($lines.Count -gt 0) {
                    $lastLine = $lines[-1]
                    $originalIndent = $lastLine -replace '\S.*', ''
                }
                
                # Aplicar indentación correcta
                $indentedScopes = $CORRECT_SCOPES -split "`n" | ForEach-Object {
                    if ($_ -match '^\s*SCOPES') {
                        $originalIndent + $_
                    } elseif ($_ -match '^\s*]') {
                        $originalIndent + ']'
                    } elseif ($_ -match '^\s*\[') {
                        '['
                    } else {
                        $originalIndent + '    ' + $_.TrimStart()
                    }
                }
                $indentedScopesText = $indentedScopes -join "`n"
                
                $content = $content -replace $pattern, $indentedScopesText
                
                # Guardar cambios
                $content | Set-Content $filePath -Encoding UTF8 -NoNewline
                
                Write-Host "   ✅ Fixed successfully" -ForegroundColor Green
                $fixedCount++
            } else {
                Write-Host "   ⏭️  No changes needed (correct scopes)" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "   ❌ Error: $_" -ForegroundColor Red
            $errorCount++
        }
    } else {
        Write-Host "   ⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================================"
Write-Host "📊 SUMMARY:" -ForegroundColor Cyan
Write-Host "   Total files checked: $totalFiles"
Write-Host "   ✅ Fixed: $fixedCount" -ForegroundColor Green
Write-Host "   ❌ Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) {'Red'} else {'Green'})
Write-Host "============================================================`n"

if ($errorCount -eq 0) {
    Write-Host "✅ All OAuth scopes fixed successfully!" -ForegroundColor Green
    Write-Host "`n📋 NEXT STEP: Delete old token and re-authenticate"
    Write-Host "   Run: py scripts\oauth\reauthenticate_gmail_v2.py`n"
} else {
    Write-Host "⚠️  Some files had errors. Please review manually." -ForegroundColor Yellow
}
