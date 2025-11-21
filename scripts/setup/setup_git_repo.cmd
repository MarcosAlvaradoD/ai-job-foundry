@echo off
REM ============================================
REM Setup Git Repository - AI Job Foundry
REM ============================================

echo.
echo ====================================
echo   CONFIGURACION DE REPOSITORIO GIT
echo ====================================
echo.

REM Ir al escritorio
cd %USERPROFILE%\Desktop

REM Crear carpeta JobTracker si no existe
if not exist "JobTracker" (
    echo [+] Creando carpeta JobTracker...
    mkdir JobTracker
)

REM Entrar a JobTracker
cd JobTracker

REM Verificar si ya es un repo
if exist ".git" (
    echo [!] Ya existe un repositorio Git aqui
    echo [?] Quieres reiniciar? (se perderan cambios no guardados)
    pause
    rmdir /s /q .git
)

REM Inicializar Git
echo [+] Inicializando repositorio Git...
git init

REM Crear .gitignore ANTES de agregar archivos
echo [+] Creando .gitignore...
(
echo # Python
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.egg-info/
echo.
echo # Datos sensibles
echo credentials.json
echo token.json
echo *.token
echo *.key
echo .env
echo config/credentials/
echo.
echo # Datos locales
echo data/job_applications.json
echo data/interview_logs/
echo logs/
echo *.log
echo.
echo # Node
echo node_modules/
echo.
echo # Sistema
echo .DS_Store
echo Thumbs.db
echo desktop.ini
) > .gitignore

REM Crear README.md
echo [+] Creando README.md...
(
echo # AI Job Foundry
echo.
echo Sistema automatizado e inteligente para gestion de busqueda de empleo.
echo.
echo ## Autor
echo Marcos Alvarado ^(c^) 2025
echo.
echo ## Licencia
echo Este proyecto esta protegido bajo licencia MIT.
echo Si usas este codigo con fines comerciales, se requiere atribucion y compensacion.
echo.
echo ## Estructura
echo - `job_tracker.py` - Monitor de comunicaciones
echo - `interview_copilot.py` - Asistente de entrevistas
echo - `project_auditor.py` - Auditor de estructura
) > README.md

REM Crear LICENSE
echo [+] Creando LICENSE...
(
echo MIT License with Commercial Clause
echo.
echo Copyright ^(c^) 2025 Marcos Alvarado
echo.
echo Permission is hereby granted, free of charge, to any person obtaining a copy
echo of this software for PERSONAL USE. For COMMERCIAL USE, explicit permission
echo and compensation are required.
echo.
echo Contact: [tu email]
) > LICENSE

REM Configurar Git (si no esta configurado)
echo [+] Configurando Git...
git config user.name "Marcos Alvarado" 2>nul
git config user.email "markalvati@gmail.com" 2>nul

REM Agregar archivos
echo [+] Agregando archivos al staging...
git add .

REM Primer commit
echo [+] Creando primer commit...
git commit -m "Initial commit - AI Job Foundry v1.0"

echo.
echo ====================================
echo   REPOSITORIO CREADO EXITOSAMENTE
echo ====================================
echo.
echo Siguiente paso:
echo 1. Ve a github.com/MarcosAlvaradoD
echo 2. Crea un nuevo repositorio llamado "ai-job-foundry"
echo 3. NO inicialices con README ^(ya lo tenemos^)
echo 4. Copia el comando que GitHub te da y ejecutalo aqui
echo.
echo Ejemplo:
echo git remote add origin https://github.com/MarcosAlvaradoD/ai-job-foundry.git
echo git branch -M main
echo git push -u origin main
echo.

pause