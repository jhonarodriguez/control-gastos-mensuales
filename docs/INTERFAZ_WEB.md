# Guia de Interfaz Web

La interfaz web centraliza toda la configuracion financiera y la sincronizacion con Drive.

## Secciones

## Dashboard

- Sueldo mensual
- Ingresos extra del mes
- Ingreso total del mes
- Gastos fijos
- Deudas
- Ahorro disponible
- Compromisos fijos
- Presupuesto variables
- Retiro en efectivo (configurado)
- Recarga MOVII (configurada)
- Saldo real en banco

## Mi Sueldo

- Nombre de usuario
- Sueldo mensual
- Presupuesto mensual para variables

Tambien incluye bloque de **Ingresos Extra del Mes Actual**.

## Saldo Bancario

- Saldo inicio de mes (manual)
- Saldo real actual en banco (manual)
- Notas

Esto permite comparar proyeccion vs realidad.

## Gastos Fijos

CRUD de gastos recurrentes con:

- Concepto
- Valor
- Dia de cargo o frecuencia
- Categoria

## Deudas

CRUD de deudas mensuales:

- Concepto
- Valor
- Dia/frecuencia
- Detalle

## Retiros y MOVII

Seccion interactiva para marcar items de gastos/deudas que van a:

- Retiro en efectivo
- Recarga MOVII

Los totales se actualizan al instante y se guardan en configuracion.

## Generar Excel

- Mes actual
- Mes siguiente

## Google Drive

- Estado de configuracion
- Sincronizar ahora
- Backup

## Boton Sync del header

Es el flujo principal de sincronizacion:

1. Guarda configuracion actual
2. Actualiza o crea hoja mensual en Excel
3. Sube archivo a Google Drive

## Comportamiento del bot en Excel

Los gastos registrados por bot se agregan solo en `GASTOS VARIABLES DEL MES`.
La tabla `DETALLE DE GASTOS (BOT)` ya no se genera.
