# Ejemplos de Uso

## Bot: registrar un gasto

Entrada:

```text
almuerzo 18000
```

Resultado esperado:
- Registra un gasto en `GASTOS VARIABLES DEL MES`
- Categoria detectada automaticamente

## Bot: registrar varios gastos en un mensaje

Entrada:

```text
uber 12000 y cafe 9000 y mercado 35000
```

Resultado esperado:
- Se registran 3 gastos en la tabla de variables
- Devuelve resumen con total y lista corta

## Bot: formato con separadores

Entrada:

```text
mercado 85.000; farmacia 23,000; gasolina 40k
```

Resultado esperado:
- Montos normalizados correctamente
- Todos quedan en variables

## Bot: comandos

```text
ayuda
saldo
resumen
gastos
sueldo 5000000
gasto netflix 30000
```

## Web: ingresos extra del mes

1. Ir a `Mi Sueldo` > `Ingresos Extra del Mes Actual`
2. Agregar concepto y valor
3. Se actualiza dashboard y se guarda por mes

## Web: retiro en efectivo y MOVII

1. Ir a `Retiros y MOVII`
2. Marcar items que aplican en cada flujo
3. Ver total instantaneo
4. Sincronizar para reflejarlo en Excel

## Web: saldos bancarios

1. Definir `Saldo inicio de mes`
2. Definir `Saldo real en banco`
3. Sincronizar

En Excel se calcula diferencia entre proyectado y real.

## Sincronizacion completa

1. Cambios en web
2. Boton `Sync` del header
3. Excel en Drive actualizado con hoja del mes
