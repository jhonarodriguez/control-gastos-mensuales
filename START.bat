@echo off
chcp 65001 >nul
echo ========================================
echo   CONTROL DE GASTOS MENSUALES
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8 o superior desde https://python.org
    pause
    exit /b 1
)

echo Python detectado:
python --version
echo.

REM Verificar si existen las dependencias
if not exist "src\__pycache__" (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo Dependencias instaladas correctamente.
    echo.
)

:menu
echo ========================================
echo   SELECCIONA UNA OPCION:
echo ========================================
echo.
echo 1. Interfaz Web (Recomendada) - Facil y visual
echo 2. Menu de Consola - Tradicional
echo.
echo ========================================
set /p opcion="Selecciona 1 o 2: "

if "%opcion%"=="1" goto web
if "%opcion%"=="2" goto consola
goto menu

:web
echo.
echo Iniciando Interfaz Web...
echo Se abrira automaticamente tu navegador
echo.
python web_server.py
if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar la interfaz web
    pause
)
goto fin

:consola
echo.
echo Iniciando Menu de Consola...
echo.
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: El programa termino con errores
    echo Revisa los mensajes de error arriba
    pause
)

:fin
