#!/usr/bin/env python3
"""
Servidor web para la interfaz de configuraciÃ³n del Control de Gastos
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import json
import threading
from pathlib import Path

PORT = 8080
WEB_DIR = Path(__file__).parent / "web"
CONFIG_FILE = Path(__file__).parent / "config" / "configuracion.json"
BOT_INSTANCE = None
BOT_LOCK = threading.Lock()


def get_bot_instance():
    """Inicializar (lazy) una unica instancia del bot."""
    global BOT_INSTANCE
    if BOT_INSTANCE is not None:
        return BOT_INSTANCE

    try:
        from src.bot_whatsapp import BotWhatsApp
    except ModuleNotFoundError:
        from bot_whatsapp import BotWhatsApp

    BOT_INSTANCE = BotWhatsApp()
    return BOT_INSTANCE

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para servir archivos y manejar API"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    
    def do_GET(self):
        """Manejar peticiones GET"""
        path = self.path.split('?', 1)[0]

        if path == '/api/config':
            self.serve_config()
        elif path.startswith('/api/docs/'):
            self.serve_docs()
        elif path == '/api/bot/health':
            self.bot_health()
        elif path == '/':
            self.path = '/index.html'
            return super().do_GET()
        else:
            return super().do_GET()
    
    def do_POST(self):
        """Manejar peticiones POST"""
        path = self.path.split('?', 1)[0]

        if path == '/api/config':
            self.save_config()
        elif path == '/api/sync-drive':
            self.sync_drive()
        elif path == '/api/bot/message':
            self.bot_message()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        """Responder preflight CORS para clientes web/móviles (Flutter, navegadores)."""
        self.send_response(204)
        self.end_headers()
    
    def serve_config(self):
        """Servir el archivo de configuraciÃ³n"""
        try:
            # Si el archivo no existe, crear uno por defecto
            if not CONFIG_FILE.exists():
                print(f"Archivo de configuraciÃ³n no encontrado en {CONFIG_FILE}")
                print("Creando configuraciÃ³n por defecto...")
                
                # Crear directorio config si no existe
                CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
                
                # ConfiguraciÃ³n por defecto
                default_config = {
                    "usuario": {"nombre": ""},
                    "sueldo": {"valor_fijo": 4600000, "moneda": "COP"},
                    "presupuesto_variables": 0,
                    "saldo_bancario": {
                        "valor_actual": 0,
                        "moneda": "COP",
                        "ultima_actualizacion": None,
                        "notas": ""
                    },
                    "historial_saldos": {
                        "saldo_mes_anterior": 0,
                        "mes_anterior": "",
                        "saldos_mensuales": {}
                    },
                    "gastos_fijos": {
                        "arriendo": {"valor": 0, "dia_cargo": 1, "categoria": "Vivienda"},
                        "mercado_primera_quincena": {"valor": 0, "dia_cargo": 15, "categoria": "AlimentaciÃ³n"},
                        "mercado_segunda_quincena": {"valor": 0, "dia_cargo": 30, "categoria": "AlimentaciÃ³n"},
                        "servicio_gas": {"valor": 0, "dia_cargo": 10, "categoria": "Servicios"},
                        "descuento_quincenal": {"valor": 5000, "frecuencia": "quincenal", "categoria": "Descuentos"},
                        "gimnasio": {"valor": 0, "dia_cargo": 1, "categoria": "Salud/Bienestar"},
                        "netflix": {"valor": 0, "dia_cargo": 5, "categoria": "Entretenimiento"},
                        "movistar": {"valor": 0, "dia_cargo": 10, "categoria": "Servicios"},
                        "youtube_premium": {"valor": 0, "dia_cargo": 5, "categoria": "Entretenimiento"},
                        "google_drive": {"valor": 0, "dia_cargo": 1, "categoria": "TecnologÃ­a"},
                        "gamepass": {"valor": 0, "dia_cargo": 15, "categoria": "Entretenimiento"},
                        "mercadolibre": {"valor": 0, "dia_cargo": 1, "categoria": "Compras"}
                    },
                    "deudas_fijas": {},
                    "flujos_efectivo": {
                        "retiro_efectivo_items": ["gasto:arriendo"],
                        "movii_items": [
                            "gasto:netflix",
                            "gasto:youtube_premium",
                            "gasto:google_drive",
                            "gasto:mercadolibre",
                            "gasto:hbo_max",
                            "gasto:pago_app_fitia",
                            "gasto:sub_facebook_don_j"
                        ],
                        "actualizado_en": None
                    },
                    "categorias_gastos": ["Vivienda", "AlimentaciÃ³n", "Servicios", "Transporte", "Salud/Bienestar", "Entretenimiento", "TecnologÃ­a", "Compras", "EducaciÃ³n", "Otros", "Descuentos"],
                    "google_drive": {"archivo_excel_id": "", "carpeta_backup_id": ""},
                    "whatsapp": {"numero_bot": "", "numero_usuario": ""},
                    "automatizacion": {"hora_creacion_hoja": "00:01", "formato_fecha": "YYYY-MM-DD"}
                }
                
                # Guardar configuraciÃ³n por defecto
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                config = default_config
                print(f"ConfiguraciÃ³n por defecto creada en: {CONFIG_FILE}")
            else:
                # Cargar configuraciÃ³n existente
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Compatibilidad: agregar claves nuevas si no existen
            if 'presupuesto_variables' not in config:
                config['presupuesto_variables'] = 0
            if 'deudas_fijas' not in config or not isinstance(config.get('deudas_fijas'), dict):
                config['deudas_fijas'] = {}
            if 'saldo_bancario' not in config or not isinstance(config.get('saldo_bancario'), dict):
                config['saldo_bancario'] = {
                    'valor_actual': 0,
                    'moneda': 'COP',
                    'ultima_actualizacion': None,
                    'notas': ''
                }
            if 'historial_saldos' not in config or not isinstance(config.get('historial_saldos'), dict):
                config['historial_saldos'] = {
                    'saldo_mes_anterior': 0,
                    'mes_anterior': '',
                    'saldos_mensuales': {}
                }
            if 'saldos_mensuales' not in config['historial_saldos'] or not isinstance(config['historial_saldos'].get('saldos_mensuales'), dict):
                config['historial_saldos']['saldos_mensuales'] = {}
            if 'flujos_efectivo' not in config or not isinstance(config.get('flujos_efectivo'), dict):
                config['flujos_efectivo'] = {
                    'retiro_efectivo_items': ['gasto:arriendo'],
                    'movii_items': [
                        'gasto:netflix',
                        'gasto:youtube_premium',
                        'gasto:google_drive',
                        'gasto:mercadolibre',
                        'gasto:hbo_max',
                        'gasto:pago_app_fitia',
                        'gasto:sub_facebook_don_j'
                    ],
                    'actualizado_en': None
                }
            if 'retiro_efectivo_items' not in config['flujos_efectivo'] or not isinstance(config['flujos_efectivo'].get('retiro_efectivo_items'), list):
                config['flujos_efectivo']['retiro_efectivo_items'] = ['gasto:arriendo']
            if 'movii_items' not in config['flujos_efectivo'] or not isinstance(config['flujos_efectivo'].get('movii_items'), list):
                config['flujos_efectivo']['movii_items'] = [
                    'gasto:netflix',
                    'gasto:youtube_premium',
                    'gasto:google_drive',
                    'gasto:mercadolibre',
                    'gasto:hbo_max',
                    'gasto:pago_app_fitia',
                    'gasto:sub_facebook_don_j'
                ]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            
        except Exception as e:
            print(f"Error sirviendo configuraciÃ³n: {e}")
            self.send_error(500, str(e))
    
    def save_config(self):
        """Guardar el archivo de configuraciÃ³n"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config = json.loads(post_data.decode('utf-8'))
            
            # Crear directorio config si no existe
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar configuraciÃ³n
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"ConfiguraciÃ³n guardada exitosamente en: {CONFIG_FILE}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'ConfiguraciÃ³n guardada'}).encode())
        except Exception as e:
            print(f"Error guardando configuraciÃ³n: {e}")
            self.send_error(500, str(e))
    
    def serve_docs(self):
        """Servir archivos de documentaciÃ³n Markdown"""
        try:
            # Extraer el nombre del archivo de la URL
            archivo = self.path.replace('/api/docs/', '')
            docs_dir = Path(__file__).parent / "docs"
            archivo_path = docs_dir / archivo
            
            # Verificar que el archivo existe y estÃ¡ en el directorio docs
            if not archivo_path.exists() or not str(archivo_path).startswith(str(docs_dir)):
                self.send_error(404, "Documento no encontrado")
                return
            
            # Leer el archivo
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(contenido.encode('utf-8'))
            
        except Exception as e:
            print(f"Error sirviendo documentaciÃ³n: {e}")
            self.send_error(500, str(e))

    def bot_health(self):
        """Verificar estado del bot para clientes moviles/web."""
        try:
            get_bot_instance()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'status': 'ok',
                'message': 'Bot disponible'
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'status': 'error',
                'message': f'Bot no disponible: {e}'
            }, ensure_ascii=False).encode('utf-8'))

    def bot_message(self):
        """Procesar un mensaje del bot y ejecutar la logica existente."""
        try:
            content_length = int(self.headers.get('Content-Length', '0'))
            if content_length <= 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Body vacio. Envia JSON con el campo "mensaje".'
                }, ensure_ascii=False).encode('utf-8'))
                return

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            if not isinstance(payload, dict):
                raise ValueError('El body JSON debe ser un objeto.')

            mensaje = str(payload.get('mensaje', '')).strip()
            numero_remitente = payload.get('numero_remitente')

            if not mensaje:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'El campo "mensaje" es obligatorio.'
                }, ensure_ascii=False).encode('utf-8'))
                return

            bot = get_bot_instance()
            with BOT_LOCK:
                respuesta = bot.procesar_entrada(mensaje, numero_remitente=numero_remitente)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'mensaje': mensaje,
                'respuesta': respuesta
            }, ensure_ascii=False).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'JSON invalido en el body.'
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            print(f"Error procesando mensaje del bot: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'Error del bot: {e}'
            }, ensure_ascii=False).encode('utf-8'))
    
    def end_headers(self):
        """Agregar headers para CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()


    def sync_drive(self):
        """Sincronizar Excel con Google Drive"""
        try:
            import sys
            import os
            
            # Agregar src al path
            src_path = os.path.join(os.path.dirname(__file__), 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            # Importar mÃ³dulos necesarios
            from excel_mensual import GeneradorExcelMensual
            from google_drive_v2 import GoogleDriveManager
            import openpyxl
            
            print("Iniciando sincronizaciÃ³n con Drive...")
            
            # Inicializar managers
            generador = GeneradorExcelMensual(str(CONFIG_FILE))
            drive = GoogleDriveManager(str(CONFIG_FILE))
            
            # Autenticar con Drive
            if not drive.autenticar():
                raise Exception("No se pudo autenticar con Google Drive")
            
            # Crear/obtener carpeta
            carpeta_id = drive.crear_o_obtener_carpeta()
            if not carpeta_id:
                raise Exception("No se pudo crear/obtener la carpeta en Drive")
            
            # Determinar mes actual
            from datetime import datetime
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            mes_actual = meses[datetime.now().month - 1]
            anio_actual = datetime.now().year
            hoja_actual = f'{mes_actual} {anio_actual}'
            clave_mes_actual = f'{anio_actual:04d}-{datetime.now().month:02d}'

            # Calcular ingresos extra del mes para confirmacion al usuario.
            historial = generador.config.get('historial_saldos', {})
            registro_mes = {}
            if isinstance(historial, dict):
                saldos_mensuales = historial.get('saldos_mensuales', {})
                if isinstance(saldos_mensuales, dict):
                    registro_mes = saldos_mensuales.get(clave_mes_actual, {}) or {}
                if not registro_mes and isinstance(historial.get(clave_mes_actual), dict):
                    registro_mes = historial.get(clave_mes_actual, {})
            ingresos_extra_raw = registro_mes.get('ingresos_extra', []) if isinstance(registro_mes, dict) else []
            ingresos_extra_total = 0.0
            ingresos_extra_count = 0
            if isinstance(ingresos_extra_raw, list):
                for item in ingresos_extra_raw:
                    if not isinstance(item, dict):
                        continue
                    try:
                        valor = float(item.get('valor', 0) or 0)
                    except Exception:
                        valor = 0.0
                    if valor > 0:
                        ingresos_extra_total += valor
                        ingresos_extra_count += 1
            
            # Verificar si existe archivo en Drive
            ruta_temp = None
            if drive.archivo_excel_id and drive.verificar_excel_drive():
                print(f'Archivo existente encontrado. Descargando...')
                ruta_temp = drive.descargar_excel_drive()
                
                if ruta_temp:
                    try:
                        # Abrir workbook existente
                        wb = openpyxl.load_workbook(ruta_temp)
                        
                        # Crear/actualizar hoja del mes sin borrar registros previos
                        generador.crear_o_actualizar_hoja_mes(wb, mes_actual, anio_actual)
                        print(f'Hoja de {hoja_actual} actualizada')
                        
                        # Guardar temporalmente
                        ruta_nueva = generador.guardar_excel_temporal(wb)
                        
                    except Exception as e:
                        print(f'Error actualizando archivo: {e}')
                        import traceback
                        traceback.print_exc()
                        ruta_temp = None
            
            if not ruta_temp:
                # Crear nuevo Excel
                print('Creando nuevo archivo Excel...')
                wb = generador.crear_excel_nuevo()
                ruta_nueva = generador.guardar_excel_temporal(wb)
            
            # Subir a Drive
            print('Subiendo archivo a Google Drive...')
            file_id = drive.subir_excel_drive(ruta_nueva, actualizar=(drive.archivo_excel_id != ''))
            
            if not file_id:
                raise Exception("No se pudo subir el archivo a Drive")
            
            # Obtener enlace compartido
            enlace = drive.obtener_enlace_compartido()
            
            print("SincronizaciÃ³n completada exitosamente!")
            
            # Responder Ã©xito
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'SincronizaciÃ³n completada',
                'enlace': enlace,
                'hoja_actual': hoja_actual,
                'ingresos_extra_total': ingresos_extra_total,
                'ingresos_extra_count': ingresos_extra_count
            }).encode())
                
        except Exception as e:
            print(f"Error en sincronizaciÃ³n: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': str(e)
            }).encode())


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor HTTP concurrente para evitar bloqueo global por request."""
    allow_reuse_address = True
    daemon_threads = True


def start_server(port=PORT, open_browser=False):
    """Iniciar el servidor web"""
    
    # Verificar que existe el directorio web
    if not WEB_DIR.exists():
        print(f"Error: No se encuentra el directorio {WEB_DIR}")
        print("AsegÃºrate de estar en el directorio correcto del proyecto.")
        return False
    
    # Intentar usar el puerto especificado, si estÃ¡ ocupado buscar otro
    while True:
        try:
            with ThreadingTCPServer(("", port), CustomHandler) as httpd:
                url = f"http://localhost:{port}"
                print(f"\n{'='*60}")
                print(f"  SERVIDOR WEB INICIADO")
                print(f"{'='*60}")
                print(f"\n  Interfaz disponible en: {url}")
                print(f"\n  Presiona Ctrl+C para detener el servidor")
                print(f"{'='*60}\n")
                
                if open_browser:
                    webbrowser.open(url)
                
                httpd.serve_forever()
                break
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Puerto {port} ocupado, intentando con {port + 1}...")
                port += 1
            else:
                raise

def main():
    """FunciÃ³n principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Servidor web para Control de Gastos')
    parser.add_argument('--port', '-p', type=int, default=PORT, help=f'Puerto (default: {PORT})')
    parser.add_argument('--no-browser', action='store_true', help='No abrir navegador automÃ¡ticamente')
    
    args = parser.parse_args()
    
    try:
        start_server(port=args.port, open_browser=not args.no_browser)
    except KeyboardInterrupt:
        print("\n\nServidor detenido.")
        sys.exit(0)

if __name__ == '__main__':
    main()


