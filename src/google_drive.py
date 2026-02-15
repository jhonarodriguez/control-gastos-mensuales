import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import pickle
from datetime import datetime

class GoogleDriveManager:
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    
    def __init__(self, config_path='config/configuracion.json'):
        self.config_path = config_path
        self.creds = None
        self.service = None
        self.carpeta_excel = 'excel_templates'
        self.token_path = 'config/token.pickle'
        self.credentials_path = 'config/credentials.json'
        
        self._cargar_configuracion()
    
    def _cargar_configuracion(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.archivo_excel_id = self.config['google_drive'].get('archivo_excel_id', '')
        self.carpeta_backup_id = self.config['google_drive'].get('carpeta_backup_id', '')
    
    def _guardar_configuracion(self):
        self.config['google_drive']['archivo_excel_id'] = self.archivo_excel_id
        self.config['google_drive']['carpeta_backup_id'] = self.carpeta_backup_id
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def autenticar(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print('ERROR: No se encontró el archivo credentials.json')
                    print('Por favor descarga tus credenciales de Google Cloud Console')
                    print('y guárdalas en config/credentials.json')
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
        print('Autenticación exitosa con Google Drive')
        return True
    
    def crear_carpeta(self, nombre, parent_id=None):
        if not self.service:
            print('Error: No has iniciado sesión. Ejecuta autenticar() primero.')
            return None
        
        metadata = {
            'name': nombre,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            metadata['parents'] = [parent_id]
        
        try:
            carpeta = self.service.files().create(body=metadata, fields='id').execute()
            print(f'Carpeta creada: {nombre} (ID: {carpeta["id"]})')
            return carpeta['id']
        except Exception as e:
            print(f'Error al crear carpeta: {e}')
            return None
    
    def subir_archivo(self, ruta_local, nombre_drive=None, carpeta_id=None):
        if not self.service:
            print('Error: No has iniciado sesión.')
            return None
        
        if not os.path.exists(ruta_local):
            print(f'Error: El archivo {ruta_local} no existe.')
            return None
        
        if nombre_drive is None:
            nombre_drive = os.path.basename(ruta_local)
        
        file_metadata = {'name': nombre_drive}
        
        if carpeta_id:
            file_metadata['parents'] = [carpeta_id]
        
        media = MediaFileUpload(
            ruta_local,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f'Archivo subido exitosamente: {nombre_drive}')
            return file['id']
        except Exception as e:
            print(f'Error al subir archivo: {e}')
            return None
    
    def actualizar_archivo(self, file_id, ruta_local):
        if not self.service:
            print('Error: No has iniciado sesión.')
            return False
        
        if not os.path.exists(ruta_local):
            print(f'Error: El archivo {ruta_local} no existe.')
            return False
        
        media = MediaFileUpload(
            ruta_local,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )
        
        try:
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            print(f'Archivo actualizado exitosamente (ID: {file_id})')
            return True
        except Exception as e:
            print(f'Error al actualizar archivo: {e}')
            return False
    
    def descargar_archivo(self, file_id, ruta_destino):
        if not self.service:
            print('Error: No has iniciado sesión.')
            return False
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with open(ruta_destino, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f'Descargando... {int(status.progress() * 100)}%')
            
            print(f'Archivo descargado: {ruta_destino}')
            return True
        except Exception as e:
            print(f'Error al descargar archivo: {e}')
            return False
    
    def listar_archivos(self, carpeta_id=None, query=None):
        if not self.service:
            print('Error: No has iniciado sesión.')
            return []
        
        try:
            if query is None:
                query = "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            
            if carpeta_id:
                query += f" and '{carpeta_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields='files(id, name, modifiedTime, size)'
            ).execute()
            
            archivos = results.get('files', [])
            return archivos
        except Exception as e:
            print(f'Error al listar archivos: {e}')
            return []
    
    def sincronizar_archivo_mes(self, nombre_archivo=None):
        if nombre_archivo is None:
            nombre_archivo = 'ControlDeGastos.xlsx'
        
        ruta_local = os.path.join(self.carpeta_excel, nombre_archivo)
        
        if not os.path.exists(ruta_local):
            print(f'El archivo local {ruta_local} no existe.')
            return False
        
        if not self.archivo_excel_id:
            print('Subiendo archivo por primera vez...')
            file_id = self.subir_archivo(
                ruta_local,
                nombre_archivo,
                self.carpeta_backup_id
            )
            if file_id:
                self.archivo_excel_id = file_id
                self._guardar_configuracion()
                return True
        else:
            print('Actualizando archivo existente...')
            return self.actualizar_archivo(self.archivo_excel_id, ruta_local)
        
        return False
    
    def crear_backup_mensual(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_backup = f'backup_control_gastos_{timestamp}.zip'
        
        import zipfile
        ruta_backup = f'logs/{nombre_backup}'
        
        os.makedirs('logs', exist_ok=True)
        
        with zipfile.ZipFile(ruta_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.carpeta_excel):
                for file in files:
                    if file.endswith('.xlsx'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.carpeta_excel)
                        zipf.write(file_path, arcname)
        
        print(f'Backup creado: {ruta_backup}')
        
        if not self.carpeta_backup_id:
            print('Creando carpeta de backups en Drive...')
            self.carpeta_backup_id = self.crear_carpeta('Backups Control Gastos')
            if self.carpeta_backup_id:
                self._guardar_configuracion()
        
        if self.carpeta_backup_id:
            file_id = self.subir_archivo(
                ruta_backup,
                nombre_backup,
                self.carpeta_backup_id
            )
            if file_id:
                print(f'Backup subido a Drive exitosamente')
                return True
        
        return False
    
    def obtener_enlace_compartido(self, file_id):
        if not self.service:
            print('Error: No has iniciado sesión.')
            return None
        
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            enlace = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
            print(f'Enlace de acceso: {enlace}')
            return enlace
        except Exception as e:
            print(f'Error al crear enlace compartido: {e}')
            return None
    
    def verificar_conexion(self):
        if not self.service:
            print('No hay conexión activa con Google Drive.')
            return False
        
        try:
            about = self.service.about().get(fields='user').execute()
            usuario = about['user']['displayName']
            print(f'Conexión activa con Google Drive')
            print(f'Usuario: {usuario}')
            return True
        except Exception as e:
            print(f'Error al verificar conexión: {e}')
            return False

def main():
    drive = GoogleDriveManager()
    
    print('=== GOOGLE DRIVE MANAGER ===\n')
    print('1. Iniciar sesión en Google Drive')
    print('2. Sincronizar archivo del mes actual')
    print('3. Crear backup y subir a Drive')
    print('4. Listar archivos en Drive')
    print('5. Verificar conexión')
    print('0. Salir\n')
    
    opcion = input('Selecciona una opción: ')
    
    if opcion == '1':
        drive.autenticar()
    elif opcion == '2':
        if drive.autenticar():
            drive.sincronizar_archivo_mes()
    elif opcion == '3':
        if drive.autenticar():
            drive.crear_backup_mensual()
    elif opcion == '4':
        if drive.autenticar():
            archivos = drive.listar_archivos()
            if archivos:
                print('\nArchivos encontrados:')
                for archivo in archivos:
                    print(f"  - {archivo['name']} (Modificado: {archivo['modifiedTime']})")
            else:
                print('\nNo se encontraron archivos.')
    elif opcion == '5':
        drive.verificar_conexion()
    elif opcion == '0':
        print('Saliendo...')
    else:
        print('Opción no válida.')

if __name__ == '__main__':
    main()
