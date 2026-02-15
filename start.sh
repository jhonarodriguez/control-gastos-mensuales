#!/bin/bash

echo "========================================"
echo "   CONTROL DE GASTOS MENSUALES"
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

echo "Python detectado:"
$PYTHON_CMD --version
echo ""

# Verificar si existen las dependencias
if [ ! -d "src/__pycache__" ]; then
    echo "Instalando dependencias..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
    echo "Dependencias instaladas correctamente."
    echo ""
fi

echo "========================================"
echo "   SELECCIONA UNA OPCION:"
echo "========================================"
echo ""
echo "1. Interfaz Web (Recomendada) - Facil y visual"
echo "2. Menu de Consola - Tradicional"
echo ""
echo "========================================"
read -p "Selecciona 1 o 2: " opcion

case $opcion in
    1)
        echo ""
        echo "Iniciando Interfaz Web..."
        echo "Se abrira automaticamente tu navegador"
        echo ""
        $PYTHON_CMD web_server.py
        if [ $? -ne 0 ]; then
            echo ""
            echo "ERROR: No se pudo iniciar la interfaz web"
            read -p "Presiona Enter para continuar..."
        fi
        ;;
    2)
        echo ""
        echo "Iniciando Menu de Consola..."
        echo ""
        $PYTHON_CMD main.py
        if [ $? -ne 0 ]; then
            echo ""
            echo "ERROR: El programa termino con errores"
            echo "Revisa los mensajes de error arriba"
            read -p "Presiona Enter para continuar..."
        fi
        ;;
    *)
        echo "Opcion no valida"
        ;;
esac
