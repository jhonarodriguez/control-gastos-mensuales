#!/usr/bin/env python3
"""
Script de actualización para el sistema de Control de Gastos
Actualiza las dependencias y verifica la configuración
"""

import subprocess
import sys
import os

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    print("="*60)
    print("INSTALANDO DEPENDENCIAS")
    print("="*60)
    
    dependencias = [
        'openpyxl>=3.1.2',
        'google-auth>=2.22.0',
        'google-auth-oauthlib>=1.0.0',
        'google-auth-httplib2>=0.1.1',
        'google-api-python-client>=2.97.0',
        'schedule>=1.2.0',
        'requests>=2.31.0',
        'psutil>=5.9.0'
    ]
    
    for dep in dependencias:
        print(f"\nInstalando {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} instalado correctamente")
        except Exception as e:
            print(f"✗ Error instalando {dep}: {e}")
    
    print("\n" + "="*60)
    print("INSTALACIÓN COMPLETADA")
    print("="*60)

def verificar_configuracion():
    """Verifica que la configuración esté correcta"""
    print("\n" + "="*60)
    print("VERIFICANDO CONFIGURACIÓN")
    print("="*60)
    
    config_path = 'config/configuracion.json'
    
    if not os.path.exists(config_path):
        print(f"✗ No se encontró {config_path}")
        return False
    
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verificar campos necesarios
        campos_requeridos = ['usuario', 'sueldo', 'gastos_fijos', 'categorias_gastos']
        
        for campo in campos_requeridos:
            if campo not in config:
                print(f"✗ Falta el campo: {campo}")
                return False
            print(f"✓ Campo {campo} encontrado")
        
        # Verificar saldo_bancario
        if 'saldo_bancario' not in config:
            print("⚠ Campo saldo_bancario no encontrado. Se creará con valores por defecto.")
        else:
            print(f"✓ Saldo bancario: ${config['saldo_bancario'].get('valor_actual', 0):,.2f}")
        
        print("\n✓ Configuración verificada correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error leyendo configuración: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("ACTUALIZACIÓN DE CONTROL DE GASTOS")
    print("="*60)
    print("\nEste script instalará las dependencias necesarias")
    print("y verificará la configuración del sistema.\n")
    
    input("Presiona Enter para continuar...")
    
    # Instalar dependencias
    instalar_dependencias()
    
    # Verificar configuración
    verificar_configuracion()
    
    print("\n" + "="*60)
    print("INSTRUCCIONES PARA USAR")
    print("="*60)
    print("\n1. Inicia la interfaz web:")
    print("   python web_server.py")
    print("\n2. Abre tu navegador en: http://localhost:8080")
    print("\n3. Configura tu saldo bancario en la sección correspondiente")
    print("\n4. Usa el botón de sync (🔄) en la parte superior derecha")
    print("   para sincronizar todo con Google Drive")
    print("\n5. Desde el chatbot, registra gastos y se sincronizarán")
    print("   automáticamente con Drive")
    print("\n" + "="*60)
    print("¡Listo para usar!")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
