# Documentacion Tecnica

## Objetivo

Sistema para control mensual de gastos con:

- Configuracion web
- Registro de gastos por bot
- Excel mensual estructurado
- Sincronizacion con Google Drive

## Componentes principales

- `web_server.py`
  - Sirve frontend (`web/`)
  - API `/api/config` para leer/guardar configuracion
  - API `/api/sync-drive` para sincronizacion completa

- `web/app.js`
  - Render y persistencia de configuracion
  - Dashboard
  - CRUD de gastos/deudas/categorias
  - Ingresos extra por mes
  - Flujos de efectivo (retiro/MOVII)

- `src/excel_mensual.py`
  - Crea o actualiza hoja mensual
  - Mantiene variables ya registradas
  - Calcula resumen, saldos y control
  - Incluye totales de retiro en efectivo y MOVII
  - No genera `DETALLE DE GASTOS (BOT)`

- `src/bot_whatsapp.py`
  - Parseo de lenguaje natural
  - Registro multiple por mensaje
  - Inserta gastos en `GASTOS VARIABLES DEL MES`
  - Sincroniza archivo con Drive

- `src/google_drive_v2.py`
  - Autenticacion OAuth
  - Descargar/subir archivo unico de Drive

## Modelo de configuracion (`config/configuracion.json`)

Claves relevantes:

- `sueldo.valor_fijo`
- `gastos_fijos`
- `deudas_fijas`
- `presupuesto_variables`
- `saldo_bancario.valor_actual`
- `historial_saldos.saldos_mensuales[YYYY-MM]`
  - `saldo_inicial`
  - `saldo_final`
  - `diferencia`
  - `ingresos_extra[]`
- `flujos_efectivo`
  - `retiro_efectivo_items[]`
  - `movii_items[]`

## Flujo de sincronizacion

1. Frontend guarda config en `/api/config`
2. `/api/sync-drive`:
   - carga config
   - descarga Excel actual desde Drive (si existe)
   - actualiza/crea hoja del mes
   - sube archivo actualizado
3. Devuelve estado y enlace de Drive

## Layout mensual (resumen)

La hoja mensual contiene:

- Resumen del mes
- Fijos configurados
- Deudas mensuales
- Gastos variables del mes
- Ingresos extra del mes (detalle)
- Indicadores de control

Los gastos del bot van solo al bloque de variables (`K:M`).

## Seguridad

No subir a GitHub:

- `config/configuracion.json`
- `config/credentials.json`
- `config/token.pickle`

Usar `config/configuracion.example.json` como plantilla compartible.
