# Control de Gastos Mensuales

Sistema para controlar gastos mensuales en Excel con sincronizacion a Google Drive y registro por bot.

## Estado actual

- Excel unico en Drive: `ControlDeGastos.xlsx`
- Una hoja por mes: `Febrero 2026`, `Marzo 2026`, etc.
- Registro de gastos por bot con lenguaje natural
- Registro multiple en un solo mensaje
- Dashboard web para configurar todo sin editar JSON manual
- Sincronizacion general desde el boton del header

## Cambios importantes ya aplicados

- Ingresos extra por mes desde la web
- Saldo inicio de mes separado de saldo real en banco
- Flujos configurables:
  - Retiro en efectivo
  - Recarga MOVII
- Los gastos del bot se guardan solo en `GASTOS VARIABLES DEL MES`
- Se elimino la tabla `DETALLE DE GASTOS (BOT)` del layout mensual

## Flujo recomendado

1. Inicia la web:

```bash
python web_server.py
```

2. Configura en la web:
- Sueldo
- Gastos fijos
- Deudas
- Saldo inicio / saldo real
- Ingresos extra del mes
- Retiros y MOVII

3. Sincroniza con el boton `Sync` del header.

4. Registra gastos desde el bot durante el mes.

## Comandos del bot

- `ayuda`
- `saldo`
- `resumen`
- `gastos`
- `sueldo 5000000`
- `gasto netflix 30000`

Ejemplos de registro:

- `almuerzo 18000`
- `uber 12000 y cafe 9000`
- `mercado 85000; farmacia 23000; gasolina 40000`

## Estructura principal

- `src/excel_mensual.py`: layout y formulas del Excel mensual
- `src/bot_whatsapp.py`: parser de mensajes y escritura de gastos
- `src/google_drive_v2.py`: sync con Drive
- `web/`: interfaz web de configuracion
- `web_server.py`: API local para web + sync

## Seguridad para GitHub

Este repo debe ignorar:

- `config/configuracion.json`
- `config/credentials.json`
- `config/token.pickle`
- logs, temporales y archivos de salida

Se incluye `config/configuracion.example.json` como plantilla segura.

## Documentacion

- `docs/INSTALACION.md`
- `docs/INTERFAZ_WEB.md`
- `docs/EJEMPLOS.md`
- `docs/DOCUMENTACION.md`
- `docs/RESUMEN.md`
