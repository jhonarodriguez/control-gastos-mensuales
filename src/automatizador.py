import json
import os
from datetime import datetime, timedelta
from generador_excel import GeneradorExcelGastos
import schedule
import time

class AutomatizadorGastos:
    
    def __init__(self, config_path='config/configuracion.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.generador = GeneradorExcelGastos(config_path)
        self.archivo_actual = None
    
    def obtener_nombre_mes_actual(self):
        return datetime.now().strftime('%Y-%m')
    
    def obtener_nombre_mes_siguiente(self):
        hoy = datetime.now()
        if hoy.month == 12:
            siguiente = hoy.replace(year=hoy.year + 1, month=1)
        else:
            siguiente = hoy.replace(month=hoy.month + 1)
        return siguiente.strftime('%Y-%m')
    
    def crear_nueva_hoja_mensual(self, nombre_mes=None):
        if nombre_mes is None:
            nombre_mes = self.obtener_nombre_mes_siguiente()
        
        print(f'Creando nueva hoja para el mes: {nombre_mes}')
        
        wb, _ = self.generador.crear_libro_nuevo(nombre_mes)
        
        ws_resumen = wb['Resumen']
        self._configurar_sueldo_inicial(ws_resumen)
        self._configurar_gastos_fijos(ws_resumen)
        
        ruta = self.generador.guardar_excel(wb, f'control_gastos_{nombre_mes}')
        self.archivo_actual = ruta
        
        print(f'Archivo creado: {ruta}')
        self._registrar_log(f'Hoja mensual creada: {nombre_mes}')
        
        return ruta
    
    def _configurar_sueldo_inicial(self, ws):
        ws['B5'] = self.config['sueldo']['valor_fijo']
    
    def _configurar_gastos_fijos(self, ws):
        fila = 10
        gastos_fijos = self.config['gastos_fijos']
        
        for concepto, datos in gastos_fijos.items():
            ws[f'B{fila}'] = datos['valor']
            fila += 1
    
    def _registrar_log(self, mensaje):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] {mensaje}\n'
        
        os.makedirs('logs', exist_ok=True)
        with open('logs/automatizacion.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def verificar_y_crear_mes(self):
        nombre_mes_siguiente = self.obtener_nombre_mes_siguiente()
        ruta_archivo = f'excel_templates/control_gastos_{nombre_mes_siguiente}.xlsx'
        
        if not os.path.exists(ruta_archivo):
            print(f'No existe archivo para {nombre_mes_siguiente}. Creando...')
            return self.crear_nueva_hoja_mensual(nombre_mes_siguiente)
        else:
            print(f'El archivo para {nombre_mes_siguiente} ya existe.')
            return ruta_archivo
    
    def ejecutar_automatizacion_programada(self):
        hora_creacion = self.config['automatizacion']['hora_creacion_hoja']
        
        print(f'Automatización configurada para ejecutarse a las {hora_creacion} del día 1 de cada mes')
        
        schedule.every().day.at(hora_creacion).do(self._ejecutar_si_es_primero)
        
        print('Servicio de automatización iniciado. Presiona Ctrl+C para detener.')
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print('\nServicio detenido.')
    
    def _ejecutar_si_es_primero(self):
        hoy = datetime.now()
        if hoy.day == 1:
            print(f'Es el primer día del mes. Ejecutando creación automática...')
            self.crear_nueva_hoja_mensual()
    
    def cambiar_sueldo(self, nuevo_sueldo):
        self.config['sueldo']['valor_fijo'] = nuevo_sueldo
        
        with open('config/configuracion.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f'Sueldo actualizado a: ${nuevo_sueldo:,.0f} COP')
        self._registrar_log(f'Sueldo modificado a: {nuevo_sueldo}')
    
    def actualizar_gasto_fijo(self, concepto, nuevo_valor):
        if concepto in self.config['gastos_fijos']:
            self.config['gastos_fijos'][concepto]['valor'] = nuevo_valor
            
            with open('config/configuracion.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f'Gasto fijo "{concepto}" actualizado a: ${nuevo_valor:,.0f} COP')
            self._registrar_log(f'Gasto fijo modificado - {concepto}: {nuevo_valor}')
        else:
            print(f'Error: El concepto "{concepto}" no existe en la configuración.')
    
    def listar_archivos_meses(self):
        carpeta = 'excel_templates'
        if not os.path.exists(carpeta):
            return []
        
        archivos = [f for f in os.listdir(carpeta) if f.startswith('control_gastos_') and f.endswith('.xlsx')]
        archivos.sort()
        return archivos
    
    def obtener_resumen_mes_actual(self):
        archivos = self.listar_archivos_meses()
        if not archivos:
            return None
        
        mes_actual = self.obtener_nombre_mes_actual()
        archivo_actual = f'control_gastos_{mes_actual}.xlsx'
        
        if archivo_actual in archivos:
            return os.path.join('excel_templates', archivo_actual)
        else:
            return os.path.join('excel_templates', archivos[-1])

def main():
    automatizador = AutomatizadorGastos()
    
    print('=== SISTEMA DE AUTOMATIZACIÓN DE GASTOS ===\n')
    print('1. Crear hoja del mes siguiente')
    print('2. Iniciar automatización programada')
    print('3. Cambiar sueldo fijo')
    print('4. Actualizar gasto fijo')
    print('5. Listar archivos existentes')
    print('6. Ver resumen del mes actual')
    print('0. Salir\n')
    
    opcion = input('Selecciona una opción: ')
    
    if opcion == '1':
        automatizador.crear_nueva_hoja_mensual()
    elif opcion == '2':
        automatizador.ejecutar_automatizacion_programada()
    elif opcion == '3':
        nuevo_sueldo = float(input('Ingresa el nuevo sueldo: '))
        automatizador.cambiar_sueldo(nuevo_sueldo)
    elif opcion == '4':
        print('\nGastos fijos disponibles:')
        for concepto in automatizador.config['gastos_fijos'].keys():
            print(f'  - {concepto}')
        concepto = input('\nIngresa el concepto a modificar: ')
        nuevo_valor = float(input('Ingresa el nuevo valor: '))
        automatizador.actualizar_gasto_fijo(concepto, nuevo_valor)
    elif opcion == '5':
        archivos = automatizador.listar_archivos_meses()
        if archivos:
            print('\nArchivos existentes:')
            for archivo in archivos:
                print(f'  - {archivo}')
        else:
            print('\nNo hay archivos creados.')
    elif opcion == '6':
        archivo = automatizador.obtener_resumen_mes_actual()
        if archivo:
            print(f'\nArchivo del mes actual: {archivo}')
        else:
            print('\nNo hay archivos disponibles.')
    elif opcion == '0':
        print('Saliendo...')
    else:
        print('Opción no válida.')

if __name__ == '__main__':
    main()
