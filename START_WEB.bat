@echo off
chcp 65001 >nul
echo ========================================
echo   CONTROL DE GASTOS - INTERFAZ WEB
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

echo Iniciando interfaz web...
echo Se abrira automaticamente tu navegador.
echo.
echo La interfaz estara disponible en: http://localhost:8080
echo.
echo Para detener el servidor, cierra esta ventana o presiona Ctrl+C
echo.

python web_server.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar el servidor web
    pause
)
