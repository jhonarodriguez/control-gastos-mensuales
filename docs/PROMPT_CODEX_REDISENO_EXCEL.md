# Prompt para Codex (VS Code) - Rediseño del Excel mensual

Usa este prompt en Codex para seguir mejorando el layout del Excel con enfoque visual y escalable:

```text
Actúa como ingeniero senior Python + OpenPyXL.

Contexto:
- Repo: control-gastos-mensuales
- Archivo principal del layout: src/excel_mensual.py
- Actualmente se genera una hoja por mes con resumen, fijos, deudas y variables.
- Quiero mejorar legibilidad visual, jerarquía de información y escalabilidad sin romper compatibilidad.

Objetivo:
Refactorizar y mejorar el diseño del Excel para que sea fácil de entender en 10 segundos, manteniendo fórmulas y datos existentes.

Requisitos funcionales:
1) Mantener compatibilidad con hojas existentes y preservación de gastos variables.
2) No eliminar fórmulas clave del resumen.
3) Soportar crecimiento (más filas de gastos/deudas y más métricas).

Requisitos de UX visual:
1) Estructura por bloques claros:
   - Resumen ejecutivo (KPIs principales)
   - Detalle fijos
   - Detalle deudas
   - Variables del mes
   - Indicadores
2) Semáforo visual para:
   - Diferencia real vs proyectado
   - Estado presupuesto variables
3) Barras de datos para comparar totales de gastos.
4) Zebra striping (filas alternadas) en tablas para lectura rápida.
5) Encabezados consistentes y tipografía/colores homogéneos.
6) Congelar paneles y anchos de columna optimizados.

Requisitos técnicos:
1) Extraer helpers reutilizables para estilos (headers, celdas monetarias, tablas, condicionales).
2) Evitar duplicación de lógica de pintado.
3) Mantener nombres y constantes claras para filas/columnas.
4) Añadir comentarios breves donde la lógica no sea obvia.

Validación obligatoria:
1) Ejecutar py_compile de los módulos principales.
2) Generar un workbook de prueba con config/configuracion.example.json.
3) Verificar que las celdas de fórmulas clave sigan presentes.

Salida esperada:
1) Cambios en src/excel_mensual.py
2) (Opcional) Documento docs/ con guía de layout visual.
3) Resumen final con:
   - Qué se mejoró visualmente
   - Qué se refactorizó
   - Riesgos/pendientes
```

Tip: si quieres un rediseño aún más fuerte, pídele a Codex que cree una segunda hoja tipo `Dashboard` y deje la hoja mensual como fuente de datos.
