# Resumen del Proyecto

## Que hace hoy

- Control mensual de gastos en Excel
- Configuracion completa desde interfaz web
- Registro por bot con mensajes naturales
- Sincronizacion de archivo unico en Google Drive

## Funciones clave

- Hoja por mes (sin crear archivos separados por cada mes)
- Ingresos extra por mes
- Saldo inicio de mes y saldo real en banco
- Diferencia automatico entre proyeccion y saldo real
- Retiro en efectivo configurable
- Recarga MOVII configurable
- Bot con soporte para varios gastos en un solo mensaje

## Estado del Excel mensual

- Tabla `GASTOS VARIABLES DEL MES` para gasto diario
- Sin tabla `DETALLE DE GASTOS (BOT)`
- Resumen con formulas y totales
- Indicadores de control

## Seguridad para repositorio

- Configuracion real y credenciales ignoradas por `.gitignore`
- Plantilla publica: `config/configuracion.example.json`

## Archivos importantes

- `web_server.py`
- `web/index.html`
- `web/app.js`
- `src/excel_mensual.py`
- `src/bot_whatsapp.py`
- `src/google_drive_v2.py`
