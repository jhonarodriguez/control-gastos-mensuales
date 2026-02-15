#!/bin/bash

echo "========================================"
echo "   CONTROL DE GASTOS - INTERFAZ WEB"
echo "========================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python no está instalado"
        echo "Por favor instala Python 3.8 o superior"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Iniciando interfaz web..."
echo "Se abrira automaticamente tu navegador."
echo ""
echo "La interfaz estara disponible en: http://localhost:8080"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

$PYTHON_CMD web_server.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: No se pudo iniciar el servidor web"
    read -p "Presiona Enter para continuar..."
fi
