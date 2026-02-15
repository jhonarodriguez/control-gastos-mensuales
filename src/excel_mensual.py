import json
import os
import tempfile
import time
from datetime import datetime

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


class GeneradorExcelMensual:
    """
    Generador de Excel mensual:
    - 1 hoja por mes (formato "Mes Anio")
    - vista con 3 cajas: resumen, fijos y variables
    - registro del bot solo en variables del mes
    """

    MESES = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    FILA_FIJOS_DATA_INICIO = 4
    FILA_FIJOS_DATA_FIN = 23
    FILA_FIJOS_TOTAL = 24

    FILA_VARIABLES_DATA_INICIO = 4
    FILA_VARIABLES_DATA_FIN = 28
    FILA_VARIABLES_TOTAL = 29

    DEFAULT_RETIRO_EFECTIVO_ITEMS = ["gasto:arriendo"]
    DEFAULT_MOVII_ITEMS = [
        "gasto:netflix",
        "gasto:youtube_premium",
        "gasto:google_drive",
        "gasto:mercadolibre",
        "gasto:hbo_max",
        "gasto:pago_app_fitia",
        "gasto:sub_facebook_don_j",
    ]

    ORDEN_GASTOS_FIJOS = [
        "arriendo",
        "mercado_primera_quincena",
        "mercado_segunda_quincena",
        "servicio_gas",
        "descuento_quincenal",
        "gimnasio",
        "netflix",
        "movistar",
        "youtube_premium",
        "google_drive",
        "gamepass",
        "mercadolibre",
        "hbo_max",
        "pago_app_fitia",
        "sub_facebook_don_j",
    ]

    PLANTILLA_VARIABLES = [
        "arreglo cuerda guitarra",
        "envio abono viaje los del sur",
        "monedas madre",
        "visita padre hospital",
        "cable control",
        "abuela almuerzo sabado visita padre hospital",
        "visita padre sabado",
        "almuerzo san valentin",
        "juego parabox nintendo switch",
        "audifonos regalo lina",
        "juego cuphead",
        "compra gasto general",
        "envio padre",
        "mercado fruta primera semana",
        "compra gasto general",
        "prueba bot flutter",
    ]

    def __init__(self, config_path="config/configuracion.json"):
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.colores = {
            "titulo": "1F4E78",
            "resumen": "1F4E78",
            "fijos_header": "1F4E78",
            "variables_header": "1F4E78",
            "subheader": "1F4E78",
            "total": "FFFFFF",
            "ingreso": "FFFFFF",
            "saldo": "FFFFFF",
            "alerta": "FFFFFF",
            "notas": "FFFFFF",
            "blanco": "FFFFFF",
        }

        self.borde = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

    def _nombre_hoja_mes(self, mes_nombre, anio):
        return f"{mes_nombre} {anio}"

    def _colorear(self, ws, ref, color, bold=False, font_color="000000", align="left"):
        cell = ws[ref]
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        cell.font = Font(bold=bold, color=font_color)
        cell.alignment = Alignment(horizontal=align, vertical="center")
        cell.border = self.borde

    def _normalizar_numero(self, valor):
        if isinstance(valor, (int, float)):
            return float(valor)
        try:
            if valor is None or valor == "":
                return 0.0
            txt = str(valor).replace("$", "").replace(",", "").strip()
            return float(txt)
        except Exception:
            return 0.0

    def _obtener_registro_mes(self, historial, llave_mes):
        if not isinstance(historial, dict):
            return {}

        saldos_mensuales = historial.get("saldos_mensuales", {})
        if isinstance(saldos_mensuales, dict):
            registro = saldos_mensuales.get(llave_mes, {})
            if isinstance(registro, dict):
                return registro

        legacy = historial.get(llave_mes, {})
        return legacy if isinstance(legacy, dict) else {}

    def _obtener_saldo_inicio_mes(self, mes_nombre, anio):
        saldo_real = self._normalizar_numero(self.config.get("saldo_bancario", {}).get("valor_actual", 0))
        historial = self.config.get("historial_saldos", {})

        try:
            mes_idx = self.MESES.index(mes_nombre) + 1
        except ValueError:
            mes_idx = datetime.now().month

        llave_actual = f"{anio:04d}-{mes_idx:02d}"
        registro_actual = self._obtener_registro_mes(historial, llave_actual)
        saldo_inicio_actual = self._normalizar_numero(registro_actual.get("saldo_inicial", 0))
        if saldo_inicio_actual > 0:
            return saldo_inicio_actual

        if mes_idx == 1:
            anio_prev = anio - 1
            mes_prev = 12
        else:
            anio_prev = anio
            mes_prev = mes_idx - 1

        llave_prev = f"{anio_prev:04d}-{mes_prev:02d}"
        registro_prev = self._obtener_registro_mes(historial, llave_prev)
        saldo_prev = self._normalizar_numero(registro_prev.get("saldo_final", 0))
        if saldo_prev > 0:
            return saldo_prev

        saldo_mes_anterior = self._normalizar_numero(historial.get("saldo_mes_anterior", 0))
        if saldo_mes_anterior > 0:
            return saldo_mes_anterior

        return saldo_real

    def _obtener_ingresos_extra_mes(self, mes_nombre, anio):
        historial = self.config.get("historial_saldos", {})

        try:
            mes_idx = self.MESES.index(mes_nombre) + 1
        except ValueError:
            mes_idx = datetime.now().month

        llave_actual = f"{anio:04d}-{mes_idx:02d}"
        registro_mes = self._obtener_registro_mes(historial, llave_actual)
        ingresos_raw = registro_mes.get("ingresos_extra", [])
        if not isinstance(ingresos_raw, list):
            return [], 0.0

        ingresos = []
        total = 0.0
        for item in ingresos_raw:
            if not isinstance(item, dict):
                continue
            concepto = str(item.get("concepto", "Ingreso extra")).strip() or "Ingreso extra"
            valor = self._normalizar_numero(item.get("valor", 0))
            fecha_registro = str(item.get("fecha_registro", "") or "")
            if valor <= 0:
                continue
            ingresos.append({"concepto": concepto, "valor": valor, "fecha_registro": fecha_registro})
            total += valor

        return ingresos, total

    def _obtener_compromisos_por_id(self):
        compromisos = {}

        for key, datos in (self.config.get("gastos_fijos") or {}).items():
            item_id = f"gasto:{key}"
            compromisos[item_id] = {
                "id": item_id,
                "key": key,
                "concepto": str(key).replace("_", " ").title(),
                "valor": self._normalizar_numero((datos or {}).get("valor", 0)),
            }

        for key, datos in (self.config.get("deudas_fijas") or {}).items():
            item_id = f"deuda:{key}"
            compromisos[item_id] = {
                "id": item_id,
                "key": key,
                "concepto": str(key).replace("_", " ").title(),
                "valor": self._normalizar_numero((datos or {}).get("valor", 0)),
            }

        return compromisos

    def _normalizar_item_flujo(self, raw_item, compromisos):
        if not isinstance(raw_item, str):
            return None

        item = raw_item.strip()
        if not item:
            return None
        if item in compromisos:
            return item

        # Compatibilidad con formato legacy por clave sin prefijo.
        legacy_key = item.lower().replace(" ", "_")
        gasto_id = f"gasto:{legacy_key}"
        deuda_id = f"deuda:{legacy_key}"
        if gasto_id in compromisos:
            return gasto_id
        if deuda_id in compromisos:
            return deuda_id
        return None

    def _obtener_total_flujo(self, clave_items, defaults):
        compromisos = self._obtener_compromisos_por_id()
        flujos = self.config.get("flujos_efectivo", {}) or {}
        seleccion_raw = flujos.get(clave_items, defaults)
        if not isinstance(seleccion_raw, list):
            seleccion_raw = defaults

        total = 0.0
        vistos = set()
        for raw_item in seleccion_raw:
            item_id = self._normalizar_item_flujo(raw_item, compromisos)
            if not item_id or item_id in vistos:
                continue
            vistos.add(item_id)
            total += self._normalizar_numero((compromisos.get(item_id) or {}).get("valor", 0))

        return total

    def _normalizar_detalle_variable(self, categoria, fecha):
        categoria_txt = "" if categoria is None else str(categoria).strip()
        fecha_txt = "" if fecha is None else str(fecha).strip()

        if not categoria_txt and "|" in fecha_txt:
            partes = [x.strip() for x in fecha_txt.split("|", 1)]
            categoria_txt = partes[0] if partes else ""
            fecha_txt = partes[1] if len(partes) > 1 else ""

        return categoria_txt, fecha_txt

    def _extraer_registros_existentes(self, ws):
        variables = []

        def _agregar_variable(monto, concepto, categoria, fecha):
            concepto_txt = "" if concepto is None else str(concepto).strip()
            if not concepto_txt:
                return

            monto_num = self._normalizar_numero(monto)
            if monto_num <= 0:
                return

            categoria_txt, fecha_txt = self._normalizar_detalle_variable(categoria, fecha)
            variables.append((monto_num, concepto_txt, categoria_txt, fecha_txt))

        # Layout nuevo: H:K
        for fila in range(self.FILA_VARIABLES_DATA_INICIO, self.FILA_VARIABLES_DATA_FIN + 1):
            _agregar_variable(
                ws[f"H{fila}"].value,
                ws[f"I{fila}"].value,
                ws[f"J{fila}"].value,
                ws[f"K{fila}"].value,
            )

        # Layout anterior: K:M
        if not variables:
            for fila in range(self.FILA_VARIABLES_DATA_INICIO, self.FILA_VARIABLES_DATA_FIN + 1):
                _agregar_variable(
                    ws[f"K{fila}"].value,
                    ws[f"L{fila}"].value,
                    "",
                    ws[f"M{fila}"].value,
                )

        # Layout legacy: tabla DETALLE DE GASTOS en A:F
        if not variables:
            fila_titulo = None
            for fila in range(1, ws.max_row + 1):
                valor = ws[f"A{fila}"].value
                if valor and "DETALLE DE GASTOS" in str(valor).upper():
                    fila_titulo = fila
                    break

            if fila_titulo:
                fila = fila_titulo + 2
                while fila <= ws.max_row:
                    fecha = ws[f"A{fila}"].value
                    concepto = ws[f"B{fila}"].value
                    categoria = ws[f"C{fila}"].value
                    monto = ws[f"D{fila}"].value
                    metodo = ws[f"E{fila}"].value
                    notas = ws[f"F{fila}"].value

                    if not any([fecha, concepto, categoria, monto, metodo, notas]):
                        break

                    if fecha and "EJEMPLO" in str(fecha).upper():
                        fila += 1
                        continue

                    _agregar_variable(monto, concepto, categoria, fecha)
                    fila += 1

        return variables

    def _limpiar_hoja(self, ws):
        if ws.merged_cells.ranges:
            for rng in list(ws.merged_cells.ranges):
                try:
                    ws.unmerge_cells(str(rng))
                except Exception:
                    pass
        ws.delete_rows(1, ws.max_row + 1)

    def _escribir_fijos(self, ws):
        gastos_fijos = self.config.get("gastos_fijos", {}) or {}
        ordenados = []
        usados = set()

        for key in self.ORDEN_GASTOS_FIJOS:
            if key in gastos_fijos:
                ordenados.append((key, gastos_fijos.get(key) or {}))
                usados.add(key)

        for key, datos in gastos_fijos.items():
            if key in usados:
                continue
            ordenados.append((key, datos or {}))

        fila = self.FILA_FIJOS_DATA_INICIO
        for nombre, datos in ordenados:
            if fila > self.FILA_FIJOS_DATA_FIN:
                break

            monto = self._normalizar_numero(datos.get("valor", 0))
            categoria = datos.get("categoria", "Sin categoria")
            fecha = ""
            if "dia_cargo" in datos:
                fecha = f"Dia {datos.get('dia_cargo')}"
            elif "frecuencia" in datos:
                fecha = str(datos.get("frecuencia", "")).title()

            ws[f"D{fila}"] = monto
            ws[f"E{fila}"] = nombre.replace("_", " ").title()
            ws[f"F{fila}"] = f"{categoria} | {fecha}".strip(" |")
            ws[f"D{fila}"].number_format = "$#,##0"

            self._colorear(ws, f"D{fila}", self.colores["blanco"])
            self._colorear(ws, f"E{fila}", self.colores["blanco"])
            self._colorear(ws, f"F{fila}", self.colores["blanco"])
            fila += 1

        for fila in range(fila, self.FILA_FIJOS_DATA_FIN + 1):
            self._colorear(ws, f"D{fila}", self.colores["blanco"])
            self._colorear(ws, f"E{fila}", self.colores["blanco"])
            self._colorear(ws, f"F{fila}", self.colores["blanco"])

    def _aplicar_banding(self, ws, columnas, fila_inicio, fila_fin, color_par, color_impar):
        for fila in range(fila_inicio, fila_fin + 1):
            color = color_par if fila % 2 == 0 else color_impar
            for col in columnas:
                self._colorear(ws, f"{col}{fila}", color)

    def _construir_layout_base(self, ws, mes_nombre, anio):
        sueldo = self._normalizar_numero(self.config.get("sueldo", {}).get("valor_fijo", 0))
        saldo_real = self._normalizar_numero(self.config.get("saldo_bancario", {}).get("valor_actual", 0))
        saldo_inicio = self._obtener_saldo_inicio_mes(mes_nombre, anio)
        _ingresos_extra_detalle, ingresos_extra_total = self._obtener_ingresos_extra_mes(mes_nombre, anio)
        retiro_total = self._obtener_total_flujo(
            "retiro_efectivo_items",
            self.DEFAULT_RETIRO_EFECTIVO_ITEMS,
        )
        movii_total = self._obtener_total_flujo(
            "movii_items",
            self.DEFAULT_MOVII_ITEMS,
        )

        ws["A1"] = f"CONTROL DE GASTOS - {mes_nombre.upper()} {anio}"
        ws.merge_cells("A1:K1")
        self._colorear(ws, "A1", self.colores["titulo"], bold=True, font_color="FFFFFF", align="center")
        ws.row_dimensions[1].height = 32

        ws.merge_cells("A2:B2")
        ws["A2"] = "RESUMEN EJECUTIVO"
        self._colorear(ws, "A2", self.colores["resumen"], bold=True, font_color="FFFFFF", align="center")

        ws.merge_cells("D2:F2")
        ws["D2"] = "GASTOS FIJOS CONFIGURADOS"
        self._colorear(ws, "D2", self.colores["fijos_header"], bold=True, font_color="FFFFFF", align="center")

        ws.merge_cells("H2:K2")
        ws["H2"] = "GASTOS VARIABLES DEL MES"
        self._colorear(ws, "H2", self.colores["variables_header"], bold=True, font_color="FFFFFF", align="center")

        for ref, txt in [("D3", "Monto"), ("E3", "Concepto"), ("F3", "Categoria / Fecha")]:
            ws[ref] = txt
            self._colorear(ws, ref, self.colores["subheader"], bold=True, font_color="FFFFFF", align="center")

        for ref, txt in [("H3", "Monto"), ("I3", "Concepto"), ("J3", "Categoria"), ("K3", "Fecha")]:
            ws[ref] = txt
            self._colorear(ws, ref, self.colores["subheader"], bold=True, font_color="FFFFFF", align="center")

        resumen_labels = [
            (3, "Ingresos Totales", sueldo + ingresos_extra_total, self.colores["blanco"]),
            (4, "Total Gastos Fijos", f"=D{self.FILA_FIJOS_TOTAL}", self.colores["blanco"]),
            (5, "Total Gastos Variables", f"=H{self.FILA_VARIABLES_TOTAL}", self.colores["blanco"]),
            (6, "Saldo Inicio Mes", saldo_inicio, self.colores["blanco"]),
            (7, "Saldo Proyectado", "=B6+B3-B4-B5", self.colores["blanco"]),
            (8, "Saldo Real Banco", saldo_real, self.colores["blanco"]),
            (9, "Diferencia", "=B8-B7", self.colores["blanco"]),
            (10, "Retiro en efectivo", retiro_total, self.colores["blanco"]),
            (11, "Recarga MOVII", movii_total, self.colores["blanco"]),
        ]

        for fila, label, value, color in resumen_labels:
            ws[f"A{fila}"] = label
            ws[f"B{fila}"] = value
            self._colorear(ws, f"A{fila}", color, bold=True)
            self._colorear(ws, f"B{fila}", color, bold=True)
            ws[f"B{fila}"].number_format = "$#,##0"

        ws[f"D{self.FILA_FIJOS_TOTAL}"] = f"=SUM(D{self.FILA_FIJOS_DATA_INICIO}:D{self.FILA_FIJOS_DATA_FIN})"
        ws[f"E{self.FILA_FIJOS_TOTAL}"] = "TOTAL GASTOS FIJOS"
        ws[f"D{self.FILA_FIJOS_TOTAL}"].number_format = "$#,##0"
        for ref in [f"D{self.FILA_FIJOS_TOTAL}", f"E{self.FILA_FIJOS_TOTAL}", f"F{self.FILA_FIJOS_TOTAL}"]:
            self._colorear(ws, ref, self.colores["total"], bold=True)

        ws[f"H{self.FILA_VARIABLES_TOTAL}"] = (
            f"=SUM(H{self.FILA_VARIABLES_DATA_INICIO}:H{self.FILA_VARIABLES_DATA_FIN})"
        )
        ws[f"I{self.FILA_VARIABLES_TOTAL}"] = "TOTAL GASTOS VARIABLES"
        ws[f"H{self.FILA_VARIABLES_TOTAL}"].number_format = "$#,##0"
        for ref in [f"H{self.FILA_VARIABLES_TOTAL}", f"I{self.FILA_VARIABLES_TOTAL}",
                    f"J{self.FILA_VARIABLES_TOTAL}", f"K{self.FILA_VARIABLES_TOTAL}"]:
            self._colorear(ws, ref, self.colores["total"], bold=True)

        ws.column_dimensions["A"].width = 32
        ws.column_dimensions["B"].width = 18
        ws.column_dimensions["C"].width = 4
        ws.column_dimensions["D"].width = 14
        ws.column_dimensions["E"].width = 30
        ws.column_dimensions["F"].width = 24
        ws.column_dimensions["G"].width = 4
        ws.column_dimensions["H"].width = 14
        ws.column_dimensions["I"].width = 32
        ws.column_dimensions["J"].width = 18
        ws.column_dimensions["K"].width = 14

        ws.freeze_panes = "A4"

    def _insertar_registros_preservados(self, ws, variables):
        # Plantilla base de variables (sin montos fijos).
        for offset, fila in enumerate(range(self.FILA_VARIABLES_DATA_INICIO, self.FILA_VARIABLES_DATA_FIN + 1)):
            concepto_plantilla = self.PLANTILLA_VARIABLES[offset] if offset < len(self.PLANTILLA_VARIABLES) else ""
            ws[f"H{fila}"] = ""
            ws[f"I{fila}"] = concepto_plantilla
            ws[f"J{fila}"] = ""
            ws[f"K{fila}"] = ""
            self._colorear(ws, f"H{fila}", self.colores["blanco"])
            self._colorear(ws, f"I{fila}", self.colores["blanco"])
            self._colorear(ws, f"J{fila}", self.colores["blanco"])
            self._colorear(ws, f"K{fila}", self.colores["blanco"])

        fila_var = self.FILA_VARIABLES_DATA_INICIO
        for monto, concepto, categoria, fecha in variables:
            if fila_var > self.FILA_VARIABLES_DATA_FIN:
                break

            ws[f"H{fila_var}"] = self._normalizar_numero(monto)
            ws[f"I{fila_var}"] = concepto
            ws[f"J{fila_var}"] = categoria
            ws[f"K{fila_var}"] = fecha
            ws[f"H{fila_var}"].number_format = "$#,##0"
            self._colorear(ws, f"H{fila_var}", self.colores["blanco"])
            self._colorear(ws, f"I{fila_var}", self.colores["blanco"])
            self._colorear(ws, f"J{fila_var}", self.colores["blanco"])
            self._colorear(ws, f"K{fila_var}", self.colores["blanco"])
            fila_var += 1

    def crear_o_actualizar_hoja_mes(self, wb, mes_nombre, anio):
        """
        Crea o actualiza (sin perder gastos) la hoja mensual.
        """
        hoja_objetivo = self._nombre_hoja_mes(mes_nombre, anio)
        hoja_legacy = mes_nombre

        variables = []

        if hoja_objetivo in wb.sheetnames:
            ws = wb[hoja_objetivo]
            variables = self._extraer_registros_existentes(ws)
            self._limpiar_hoja(ws)
        elif hoja_legacy in wb.sheetnames:
            ws = wb[hoja_legacy]
            variables = self._extraer_registros_existentes(ws)
            ws.title = hoja_objetivo
            self._limpiar_hoja(ws)
        else:
            ws = wb.create_sheet(hoja_objetivo)

        self._construir_layout_base(ws, mes_nombre, anio)
        self._escribir_fijos(ws)
        self._insertar_registros_preservados(ws, variables)
        return ws

    def _buscar_siguiente_fila_libre(self, ws, col, fila_inicio, fila_fin):
        for fila in range(fila_inicio, fila_fin + 1):
            valor = ws[f"{col}{fila}"].value
            if valor in (None, ""):
                return fila
            if isinstance(valor, str) and "EJEMPLO" in valor.upper():
                return fila
        return None

    def agregar_gasto_a_hoja(self, ws, datos_gasto):
        """
        Inserta un gasto solo en la tabla de variables del mes (H:K).
        """
        fila_var = self._buscar_siguiente_fila_libre(
            ws, "H", self.FILA_VARIABLES_DATA_INICIO, self.FILA_VARIABLES_DATA_FIN
        )
        if fila_var:
            categoria = datos_gasto.get("categoria", "Otros")
            fecha = datos_gasto.get("fecha", "")

            ws[f"H{fila_var}"] = self._normalizar_numero(datos_gasto.get("monto", 0))
            ws[f"I{fila_var}"] = datos_gasto.get("concepto", "Gasto general")
            ws[f"J{fila_var}"] = "" if categoria is None else str(categoria)
            ws[f"K{fila_var}"] = "" if fecha is None else str(fecha)
            ws[f"H{fila_var}"].number_format = "$#,##0"
            self._colorear(ws, f"H{fila_var}", self.colores["blanco"])
            self._colorear(ws, f"I{fila_var}", self.colores["blanco"])
            self._colorear(ws, f"J{fila_var}", self.colores["blanco"])
            self._colorear(ws, f"K{fila_var}", self.colores["blanco"])

    def crear_excel_nuevo(self):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        ahora = datetime.now()
        mes_actual = self.MESES[ahora.month - 1]
        anio_actual = ahora.year

        self.crear_o_actualizar_hoja_mes(wb, mes_actual, anio_actual)
        return wb

    def guardar_excel_temporal(self, wb, nombre="ControlDeGastos.xlsx"):
        temp_dir = os.path.join(tempfile.gettempdir(), "control_gastos")
        os.makedirs(temp_dir, exist_ok=True)
        ruta = os.path.join(temp_dir, nombre)

        try:
            wb.save(ruta)
        except PermissionError:
            ruta_alt = os.path.join(temp_dir, f"ControlDeGastos_{int(time.time())}.xlsx")
            wb.save(ruta_alt)
            return ruta_alt

        return ruta


if __name__ == "__main__":
    generador = GeneradorExcelMensual()
    wb = generador.crear_excel_nuevo()
    ruta = generador.guardar_excel_temporal(wb)
    print(f"Excel creado: {ruta}")
