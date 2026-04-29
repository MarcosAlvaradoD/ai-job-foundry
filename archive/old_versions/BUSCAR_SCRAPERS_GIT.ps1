################################################################################
# BUSCAR SCRAPERS EN GIT HISTORY
# Busca archivos eliminados de scrapers en el historial de Git
################################################################################

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host "🔍 BUSCANDO SCRAPERS EN GIT HISTORY" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en un repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "❌ No estás en un repositorio Git" -ForegroundColor Red
    Write-Host "   Navega a: C:\Users\MSI\Desktop\ai-job-foundry" -ForegroundColor Yellow
    exit 1
}

Write-Host "📂 Repositorio: " -NoNewline
Write-Host (Get-Location) -ForegroundColor Green
Write-Host ""

################################################################################
# 1. BUSCAR ARCHIVOS CON NOMBRE "scraper"
################################################################################

Write-Host "🔎 Buscando archivos con 'scraper' en el nombre..." -ForegroundColor Cyan
Write-Host ""

$scraperFiles = git log --all --full-history --pretty=format: --name-only -- "*scraper*.py" | Sort-Object -Unique

if ($scraperFiles) {
    Write-Host "✅ Encontrados:" -ForegroundColor Green
    foreach ($file in $scraperFiles) {
        if ($file) {
            Write-Host "   📄 $file" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "❌ No se encontraron archivos con 'scraper' en el nombre" -ForegroundColor Red
}

Write-Host ""

################################################################################
# 2. BUSCAR COMMITS QUE MODIFICARON O ELIMINARON SCRAPERS
################################################################################

Write-Host "📝 Buscando commits que mencionan 'scraper'..." -ForegroundColor Cyan
Write-Host ""

$commits = git log --all --grep="scraper" --oneline

if ($commits) {
    Write-Host "✅ Commits encontrados:" -ForegroundColor Green
    Write-Host $commits -ForegroundColor Yellow
} else {
    Write-Host "⚠️  No se encontraron commits con 'scraper' en el mensaje" -ForegroundColor Yellow
}

Write-Host ""

################################################################################
# 3. BUSCAR ARCHIVOS ELIMINADOS EN COMMITS RECIENTES
################################################################################

Write-Host "🗑️  Buscando archivos eliminados en últimos 50 commits..." -ForegroundColor Cyan
Write-Host ""

$deletedFiles = git log --diff-filter=D --summary --pretty=format: -50 | Select-String "delete mode" | Select-String ".py"

if ($deletedFiles) {
    Write-Host "✅ Archivos Python eliminados recientemente:" -ForegroundColor Green
    foreach ($line in $deletedFiles) {
        Write-Host "   $line" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  No se encontraron archivos Python eliminados recientemente" -ForegroundColor Yellow
}

Write-Host ""

################################################################################
# 4. LISTAR TODOS LOS ARCHIVOS PYTHON EN EL HISTORIAL
################################################################################

Write-Host "📚 Listando TODOS los archivos Python que alguna vez existieron..." -ForegroundColor Cyan
Write-Host ""

$allPythonFiles = git log --all --pretty=format: --name-only -- "*.py" | Sort-Object -Unique

$scraperRelated = $allPythonFiles | Where-Object { $_ -like "*scraper*" -or $_ -like "*linkedin*" -or $_ -like "*indeed*" }

if ($scraperRelated) {
    Write-Host "✅ Archivos relacionados con scrapers encontrados:" -ForegroundColor Green
    foreach ($file in $scraperRelated) {
        if ($file) {
            # Verificar si el archivo existe actualmente
            if (Test-Path $file) {
                Write-Host "   ✅ $file (EXISTE)" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $file (ELIMINADO)" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "❌ No se encontraron archivos relacionados" -ForegroundColor Red
}

Write-Host ""

################################################################################
# 5. BUSCAR EN COMMITS ESPECÍFICOS
################################################################################

Write-Host "🎯 Buscando en commits que modificaron core/ingestion/..." -ForegroundColor Cyan
Write-Host ""

$ingestionCommits = git log --all --oneline -- "core/ingestion/*.py"

if ($ingestionCommits) {
    Write-Host "✅ Commits en core/ingestion/:" -ForegroundColor Green
    Write-Host $ingestionCommits -ForegroundColor Yellow
} else {
    Write-Host "⚠️  No se encontraron commits en core/ingestion/" -ForegroundColor Yellow
}

Write-Host ""

################################################################################
# 6. GENERAR REPORTE DE ARCHIVOS ELIMINADOS
################################################################################

Write-Host "📊 Generando reporte detallado..." -ForegroundColor Cyan
Write-Host ""

$reportFile = "SCRAPERS_GIT_SEARCH_REPORT.txt"

$report = @"
================================================================================
REPORTE DE BÚSQUEDA DE SCRAPERS EN GIT
================================================================================
Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Repositorio: $(Get-Location)
================================================================================

1. ARCHIVOS CON 'SCRAPER' EN EL NOMBRE:
----------------------------------------
$($scraperFiles -join "`n")

2. COMMITS QUE MENCIONAN 'SCRAPER':
------------------------------------
$commits

3. ARCHIVOS PYTHON ELIMINADOS (últimos 50 commits):
-----------------------------------------------------
$($deletedFiles -join "`n")

4. ARCHIVOS RELACIONADOS CON SCRAPERS:
---------------------------------------
$($scraperRelated | ForEach-Object {
    if (Test-Path $_) {
        "✅ $_ (EXISTE)"
    } else {
        "❌ $_ (ELIMINADO)"
    }
} | Out-String)

5. COMMITS EN core/ingestion/:
-------------------------------
$ingestionCommits

================================================================================

📋 ACCIONES RECOMENDADAS:

1. Si encontraste archivos eliminados:
   git show COMMIT_HASH:ruta/al/archivo.py > archivo_recuperado.py

2. Ver contenido de un archivo eliminado:
   git show COMMIT_HASH:core/ingestion/linkedin_scraper_V2.py

3. Recuperar archivo completo:
   git checkout COMMIT_HASH -- core/ingestion/linkedin_scraper_V2.py

4. Ver historial de un archivo específico:
   git log --all --full-history -- core/ingestion/linkedin_scraper_V2.py

================================================================================
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "✅ Reporte guardado en: " -NoNewline -ForegroundColor Green
Write-Host $reportFile -ForegroundColor Yellow
Write-Host ""

################################################################################
# 7. COMANDOS ÚTILES PARA RECUPERAR
################################################################################

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host "💡 COMANDOS ÚTILES PARA RECUPERAR ARCHIVOS" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Para VER el contenido de un archivo eliminado:" -ForegroundColor Cyan
Write-Host "   git show COMMIT_HASH:ruta/al/archivo.py" -ForegroundColor White
Write-Host ""

Write-Host "💾 Para RECUPERAR un archivo eliminado:" -ForegroundColor Cyan
Write-Host "   git checkout COMMIT_HASH -- ruta/al/archivo.py" -ForegroundColor White
Write-Host ""

Write-Host "🔍 Para ver CUÁNDO se eliminó un archivo:" -ForegroundColor Cyan
Write-Host "   git log --all --full-history -- ruta/al/archivo.py" -ForegroundColor White
Write-Host ""

Write-Host "📊 Para ver DIFERENCIAS antes de eliminar:" -ForegroundColor Cyan
Write-Host "   git show COMMIT_HASH -- ruta/al/archivo.py" -ForegroundColor White
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host "✅ BÚSQUEDA COMPLETA" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*78) -ForegroundColor Cyan
Write-Host ""
