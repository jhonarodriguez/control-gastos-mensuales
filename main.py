import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generador_excel import GeneradorExcelGastos
from automatizador import AutomatizadorGastos
from bot_whatsapp import BotWhatsApp
from google_drive import GoogleDriveManager
from google_drive_v2 import sincronizar_con_drive as sincronizar_excel_drive
from datetime import datetime

class SistemaControlGastos:
    
    def __init__(self):
        self.generador = None
        self.automatizador = None
        self.bot = None
        self.drive = None
    
    def inicializar(self):
        print('Inicializando sistema...')
        self.generador = GeneradorExcelGastos()
        self.automatizador = AutomatizadorGastos()
        self.bot = BotWhatsApp()
        self.drive = GoogleDriveManager()
        print('Sistema inicializado correctamente.\n')
    
    def crear_excel_inicial(self):
        print('Creando Excel inicial...')
        ruta = self.generador.crear_plantilla_inicial()
        print(f'Excel creado en: {ruta}')
        print('Ahora puedes abrirlo y personalizar los valores de tus gastos fijos.\n')
        return ruta
    
    def ejecutar_bot_consola(self):
        print('=== BOT DE CONTROL DE GASTOS - MODO CONSOLA ===\n')
        print('Escribe tus gastos de forma natural.')
        print('Ejemplos:')
        print('  - "Gasté 25000 en transporte"')
        print('  - "Compré café por 15000"')
        print('  - "Pagué 50000 de netflix"')
        print('\nEscribe "ayuda" para ver todos los comandos')
        print('Escribe "salir" para terminar\n')
        
        while True:
            try:
                mensaje = input('Tú: ').strip()
                
                if mensaje.lower() == 'salir':
                    print('¡Hasta luego! Guardando datos...')
                    break
                
                if not mensaje:
                    continue
                
                respuesta = self.bot.procesar_entrada(mensaje)
                print(f'\nBot: {respuesta}\n')
                
            except KeyboardInterrupt:
                print('\n\nInterrumpido por el usuario.')
                break
            except Exception as e:
                print(f'\nError: {e}\n')
    
    def configurar_google_drive(self):
        print('\n=== CONFIGURACIÓN DE GOOGLE DRIVE ===')
        print('Para configurar Google Drive, necesitas:')
        print('1. Ir a https://console.cloud.google.com/')
        print('2. Crear un nuevo proyecto')
        print('3. Habilitar la API de Google Drive')
        print('4. Crear credenciales OAuth 2.0')
        print('5. Descargar el archivo credentials.json')
        print('6. Guardarlo en la carpeta config/ del proyecto')
        print('\n¿Deseas iniciar la autenticación ahora? (s/n)')
        
        respuesta = input().lower()
        if respuesta == 's':
            if self.drive.autenticar():
                print('\nAutenticación exitosa!')
                print('Ahora puedes sincronizar tus archivos con Drive.')
                return True
        return False
    
    def abrir_interfaz_web(self):
        print('\n=== INTERFAZ WEB DE CONFIGURACIÓN ===')
        print('Iniciando servidor web...')
        print('Se abrirá automáticamente tu navegador.')
        print('La interfaz estará disponible en http://localhost:8080')
        print('\nPresiona Ctrl+C en esta ventana para cerrar el servidor.\n')
        
        try:
            import subprocess
            import sys
            
            # Iniciar el servidor web en un proceso separado
            if sys.platform.startswith('win'):
                subprocess.run([sys.executable, 'web_server.py'])
            else:
                subprocess.run([sys.executable, 'web_server.py'])
        except KeyboardInterrupt:
            print('\nServidor web detenido.')
        except Exception as e:
            print(f'\nError al iniciar el servidor web: {e}')
            print('Intenta ejecutar manualmente: python web_server.py')

    def crear_y_sincronizar_hoja(self, month_mode='siguiente'):
        """Crear/actualizar hoja mensual y sincronizar el archivo único en Drive."""
        print('\n=== CREAR Y SINCRONIZAR HOJA MENSUAL ===')
        print(f'Modo seleccionado: {month_mode}')
        resultado = sincronizar_excel_drive(
            config_path='config/configuracion.json',
            month_mode=month_mode,
        )
        if resultado.get('success'):
            hoja = resultado.get('hoja_objetivo', '(sin nombre)')
            accion = 'creada' if resultado.get('hoja_creada') else 'actualizada'
            print(f'\nHoja {accion}: {hoja}')
            if resultado.get('enlace'):
                print(f'Enlace Drive: {resultado["enlace"]}')
            return True

        print(f'\nError: {resultado.get("message", "No se pudo sincronizar con Drive")}')
        return False
    
    def mostrar_menu_principal(self):
        print('\n' + '='*60)
        print('  SISTEMA DE CONTROL DE GASTOS MENSUALES')
        print('  ' + datetime.now().strftime('%B %Y').upper())
        print('='*60 + '\n')
        
        print('MENÚ PRINCIPAL:\n')
        print('1. Crear Excel inicial')
        print('2. Abrir bot de gastos (modo consola)')
        print('3. Abrir interfaz web (configuración visual)')
        print('4. Crear/sincronizar hoja mensual (actual o siguiente)')
        print('5. Iniciar automatización programada')
        print('6. Configurar Google Drive')
        print('7. Sincronizar hoja del mes actual con Drive')
        print('8. Crear backup en Drive')
        print('9. Cambiar sueldo mensual')
        print('10. Actualizar gasto fijo')
        print('11. Ver archivos existentes')
        print('0. Salir\n')
    
    def ejecutar(self):
        self.inicializar()
        
        while True:
            try:
                self.mostrar_menu_principal()
                opcion = input('Selecciona una opción: ').strip()
                
                if opcion == '1':
                    self.crear_excel_inicial()
                
                elif opcion == '2':
                    self.ejecutar_bot_consola()
                
                elif opcion == '3':
                    self.abrir_interfaz_web()
                
                elif opcion == '4':
                    modo = input('Selecciona mes [1=actual, 2=siguiente] (default 2): ').strip()
                    month_mode = 'actual' if modo == '1' else 'siguiente'
                    self.crear_y_sincronizar_hoja(month_mode)
                
                elif opcion == '5':
                    print('Iniciando servicio de automatización...')
                    print('Presiona Ctrl+C para detener.')
                    self.automatizador.ejecutar_automatizacion_programada()
                
                elif opcion == '6':
                    self.configurar_google_drive()
                
                elif opcion == '7':
                    self.crear_y_sincronizar_hoja('actual')
                
                elif opcion == '8':
                    if self.drive.autenticar():
                        self.drive.crear_backup_mensual()
                
                elif opcion == '9':
                    try:
                        nuevo_sueldo = float(input('Ingresa el nuevo sueldo: '))
                        self.automatizador.cambiar_sueldo(nuevo_sueldo)
                    except ValueError:
                        print('Error: Ingresa un número válido.')
                
                elif opcion == '10':
                    print('\nGastos fijos disponibles:')
                    for concepto in self.automatizador.config['gastos_fijos'].keys():
                        print(f'  - {concepto}')
                    concepto = input('\nConcepto a modificar: ').strip()
                    try:
                        nuevo_valor = float(input('Nuevo valor: '))
                        self.automatizador.actualizar_gasto_fijo(concepto, nuevo_valor)
                    except ValueError:
                        print('Error: Ingresa un número válido.')
                
                elif opcion == '11':
                    archivos = self.automatizador.listar_archivos_meses()
                    if archivos:
                        print('\nArchivos existentes:')
                        for archivo in archivos:
                            print(f'  - {archivo}')
                    else:
                        print('\nNo hay archivos creados.')
                
                elif opcion == '0':
                    print('\n¡Hasta luego! Gracias por usar el sistema.')
                    break
                
                else:
                    print('\nOpción no válida. Intenta de nuevo.')
                
                input('\nPresiona Enter para continuar...')
                
            except KeyboardInterrupt:
                print('\n\nInterrumpido por el usuario.')
                break
            except Exception as e:
                print(f'\nError: {e}')
                input('\nPresiona Enter para continuar...')

def main():
    sistema = SistemaControlGastos()
    sistema.ejecutar()

if __name__ == '__main__':
    main()
