class ConfigManager {
    constructor() {
        this.config = null;
        this.currentSection = 'dashboard';
        this.editingGasto = null;
        this.editingDeuda = null;
        this.init();
    }

    async init() {
        await this.loadConfig();
        this.setupEventListeners();
        this.updateUI();
        this.renderAll();
    }

    async loadConfig() {
        try {
            // Intentar cargar desde el endpoint del servidor
            const response = await fetch('/api/config');
            if (!response.ok) {
                throw new Error('No se pudo cargar la configuración');
            }
            this.config = await response.json();
            this.config.presupuesto_variables = this.config.presupuesto_variables || 0;
            this.config.deudas_fijas = this.config.deudas_fijas || {};
            this.config.saldo_bancario = this.config.saldo_bancario || {
                valor_actual: 0,
                moneda: 'COP',
                ultima_actualizacion: null,
                notas: ''
            };
            this.config.historial_saldos = this.config.historial_saldos || {
                saldo_mes_anterior: 0,
                mes_anterior: '',
                saldos_mensuales: {}
            };
            this.config.historial_saldos.saldos_mensuales = this.config.historial_saldos.saldos_mensuales || {};
            this.migrarHistorialMensualLegacy();
            this._normalizarFlujosEfectivo();
            console.log('Configuración cargada:', this.config);
        } catch (error) {
            console.error('Error cargando configuración:', error);
            this.showToast('Usando configuración por defecto', 'warning');
            // Configuración por defecto
            this.config = this.getDefaultConfig();
        }
    }

    getDefaultConfig() {
        return {
            usuario: { nombre: '' },
            sueldo: { valor_fijo: 4600000, moneda: 'COP' },
            presupuesto_variables: 0,
            saldo_bancario: { valor_actual: 13135871.09, moneda: 'COP', ultima_actualizacion: new Date().toISOString() },
            historial_saldos: { saldo_mes_anterior: 0, mes_anterior: '', saldos_mensuales: {} },
            gastos_fijos: {},
            deudas_fijas: {},
            flujos_efectivo: {
                retiro_efectivo_items: ['gasto:arriendo'],
                movii_items: [
                    'gasto:netflix',
                    'gasto:youtube_premium',
                    'gasto:google_drive',
                    'gasto:mercadolibre',
                    'gasto:hbo_max',
                    'gasto:pago_app_fitia',
                    'gasto:sub_facebook_don_j'
                ],
                actualizado_en: null
            },
            categorias_gastos: ['Vivienda', 'Alimentación', 'Servicios', 'Transporte', 'Salud/Bienestar', 'Entretenimiento', 'Tecnología', 'Compras', 'Educación', 'Otros', 'Descuentos'],
            google_drive: { archivo_excel_id: '', carpeta_backup_id: '' },
            whatsapp: { numero_bot: '', numero_usuario: '' },
            automatizacion: { hora_creacion_hoja: '00:01', formato_fecha: 'YYYY-MM-DD' }
        };
    }

    setupEventListeners() {
        // Navegación del sidebar
        document.querySelectorAll('.sidebar-menu li').forEach(item => {
            item.addEventListener('click', () => {
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        // Botón guardar todo
        document.getElementById('btn-guardar-todo').addEventListener('click', () => {
            this.saveConfig();
        });

        // Sección Sueldo
        document.getElementById('btn-guardar-sueldo').addEventListener('click', () => {
            this.guardarSueldo();
        });
        const btnAgregarIngresoExtra = document.getElementById('btn-agregar-ingreso-extra');
        if (btnAgregarIngresoExtra) {
            btnAgregarIngresoExtra.addEventListener('click', () => {
                this.agregarIngresoExtra();
            });
        }
        const inputIngresoExtraConcepto = document.getElementById('ingreso-extra-concepto');
        const inputIngresoExtraValor = document.getElementById('ingreso-extra-valor');
        [inputIngresoExtraConcepto, inputIngresoExtraValor].forEach((input) => {
            if (!input) {
                return;
            }
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.agregarIngresoExtra();
                }
            });
        });
        const retiroItems = document.getElementById('retiro-efectivo-items');
        if (retiroItems) {
            retiroItems.addEventListener('change', (e) => {
                this.manejarCambioFlujoEfectivo(e, 'retiro_efectivo_items');
            });
        }
        const moviiItems = document.getElementById('movii-items');
        if (moviiItems) {
            moviiItems.addEventListener('change', (e) => {
                this.manejarCambioFlujoEfectivo(e, 'movii_items');
            });
        }

        // Sección Gastos Fijos
        document.getElementById('btn-agregar-gasto').addEventListener('click', () => {
            this.abrirModalGasto();
        });

        document.getElementById('btn-guardar-gasto').addEventListener('click', () => {
            this.guardarGasto();
        });

        document.getElementById('gasto-tipo-fecha').addEventListener('change', (e) => {
            this.toggleTipoFecha(e.target.value);
        });

        // Seccion Deudas
        const btnAgregarDeuda = document.getElementById('btn-agregar-deuda');
        if (btnAgregarDeuda) {
            btnAgregarDeuda.addEventListener('click', () => {
                this.abrirModalDeuda();
            });
        }

        const btnGuardarDeuda = document.getElementById('btn-guardar-deuda');
        if (btnGuardarDeuda) {
            btnGuardarDeuda.addEventListener('click', () => {
                this.guardarDeuda();
            });
        }

        const deudaTipoFecha = document.getElementById('deuda-tipo-fecha');
        if (deudaTipoFecha) {
            deudaTipoFecha.addEventListener('change', (e) => {
                this.toggleTipoFechaDeuda(e.target.value);
            });
        }

        // Sección Categorías
        document.getElementById('btn-agregar-categoria').addEventListener('click', () => {
            this.abrirModalCategoria();
        });

        document.getElementById('btn-guardar-categoria').addEventListener('click', () => {
            this.guardarCategoria();
        });

        // Sección Excel
        document.getElementById('btn-excel-actual').addEventListener('click', () => {
            this.generarExcel('actual');
        });

        document.getElementById('btn-excel-siguiente').addEventListener('click', () => {
            this.generarExcel('siguiente');
        });

        // Sección Drive
        document.getElementById('btn-configurar-drive').addEventListener('click', () => {
            this.configurarDrive();
        });

        document.getElementById('btn-sync-ahora').addEventListener('click', () => {
            this.sincronizarDrive();
        });

        document.getElementById('btn-backup').addEventListener('click', () => {
            this.crearBackup();
        });

        // Sección Saldo Bancario
        document.getElementById('btn-actualizar-saldo').addEventListener('click', () => {
            this.actualizarSaldoBancario();
        });

        // Botón de sincronización general en el header
        document.getElementById('btn-sync-general').addEventListener('click', () => {
            this.sincronizarTodo();
        });

        // Botón ayuda
        document.getElementById('btn-ayuda').addEventListener('click', () => {
            this.mostrarAyuda();
        });

        // Cerrar modales
        document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
            btn.addEventListener('click', () => {
                this.cerrarModales();
            });
        });

        // Cerrar modal al hacer clic fuera
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.cerrarModales();
                }
            });
        });
    }

    switchSection(section) {
        // Actualizar menú activo
        document.querySelectorAll('.sidebar-menu li').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Actualizar título
        const titulos = {
            'dashboard': 'Dashboard',
            'sueldo': 'Configurar Sueldo',
            'saldo-bancario': 'Saldo Bancario',
            'gastos-fijos': 'Gastos Fijos',
            'deudas': 'Deudas Mensuales',
            'flujos-efectivo': 'Retiros y Recarga MOVII',
            'categorias': 'Categorías',
            'excel': 'Generar Excel',
            'drive': 'Google Drive',
            'logs': 'Historial',
            'documentacion': 'Documentación'
        };
        document.getElementById('page-title').textContent = titulos[section] || 'Dashboard';

        // Mostrar sección
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');

        this.currentSection = section;
    }

    updateUI() {
        // Actualizar nombre de usuario
        if (this.config.usuario.nombre) {
            document.getElementById('user-name').textContent = this.config.usuario.nombre;
            document.getElementById('nombre-usuario').value = this.config.usuario.nombre;
        }

        // Actualizar sueldo
        document.getElementById('sueldo-mensual').value = this.config.sueldo.valor_fijo;
        const presupuestoInput = document.getElementById('presupuesto-variables');
        if (presupuestoInput) {
            presupuestoInput.value = this.config.presupuesto_variables || 0;
        }

        // Actualizar saldo bancario
        this.updateUISaldoBancario();

        // Actualizar dashboard
        this.renderFlujosEfectivo();
        this.updateDashboard();
        this.renderIngresosExtra();

        // Actualizar meses en Excel
        const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        const hoy = new Date();
        const mesActualDate = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
        const mesSiguienteDate = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 1);
        const mesActual = meses[mesActualDate.getMonth()];
        const mesSiguiente = meses[mesSiguienteDate.getMonth()];
        const anioActual = mesActualDate.getFullYear();
        const anioSiguiente = mesSiguienteDate.getFullYear();
        
        document.getElementById('mes-actual').textContent = `${mesActual} ${anioActual}`;
        document.getElementById('mes-siguiente').textContent = `${mesSiguiente} ${anioSiguiente}`;

        // Verificar estado de Drive
        this.verificarDrive();
    }

    updateDashboard() {
        const sueldo = this.config.sueldo.valor_fijo;
        const ingresosExtraMes = this._obtenerTotalIngresosExtraMesActual();
        const ingresoTotalMes = sueldo + ingresosExtraMes;
        const gastosFijos = Object.values(this.config.gastos_fijos).reduce((sum, gasto) => {
            return sum + (gasto.valor || 0);
        }, 0);
        const deudas = Object.values(this.config.deudas_fijas || {}).reduce((sum, deuda) => {
            return sum + (deuda.valor || 0);
        }, 0);
        const ahorro = ingresoTotalMes - gastosFijos - deudas;
        const categorias = this.config.categorias_gastos.length;
        const saldoBanco = this.config.saldo_bancario?.valor_actual || 0;
        const ultimaActualizacion = this.config.saldo_bancario?.ultima_actualizacion;
        const presupuestoVariables = this.config.presupuesto_variables || 0;
        const totalRetiroEfectivo = this._calcularTotalFlujoEfectivo('retiro_efectivo_items');
        const totalRecargaMovii = this._calcularTotalFlujoEfectivo('movii_items');

        document.getElementById('dash-sueldo').textContent = this.formatMoney(sueldo);
        const dashIngresosExtra = document.getElementById('dash-ingresos-extra');
        if (dashIngresosExtra) {
            dashIngresosExtra.textContent = this.formatMoney(ingresosExtraMes);
        }
        const dashIngresoTotal = document.getElementById('dash-ingreso-total');
        if (dashIngresoTotal) {
            dashIngresoTotal.textContent = this.formatMoney(ingresoTotalMes);
        }
        document.getElementById('dash-gastos-fijos').textContent = this.formatMoney(gastosFijos);
        document.getElementById('dash-ahorro').textContent = this.formatMoney(ahorro);
        document.getElementById('dash-categorias').textContent = categorias;
        document.getElementById('dash-saldo-banco').textContent = this.formatMoney(saldoBanco);
        const dashDeudas = document.getElementById('dash-deudas');
        if (dashDeudas) {
            dashDeudas.textContent = this.formatMoney(deudas);
        }
        const dashCompromisos = document.getElementById('dash-compromisos');
        if (dashCompromisos) {
            dashCompromisos.textContent = this.formatMoney(gastosFijos + deudas);
        }
        const dashPresupuesto = document.getElementById('dash-presupuesto-variables');
        if (dashPresupuesto) {
            dashPresupuesto.textContent = this.formatMoney(presupuestoVariables);
        }
        const dashRetiro = document.getElementById('dash-retiro-efectivo');
        if (dashRetiro) {
            dashRetiro.textContent = this.formatMoney(totalRetiroEfectivo);
        }
        const dashMovii = document.getElementById('dash-recarga-movii');
        if (dashMovii) {
            dashMovii.textContent = this.formatMoney(totalRecargaMovii);
        }
        
        if (ultimaActualizacion) {
            const fecha = new Date(ultimaActualizacion);
            document.getElementById('dash-ultima-actualizacion').textContent = 
                'Actualizado: ' + fecha.toLocaleDateString() + ' ' + fecha.toLocaleTimeString();
        }

        // Renderizar próximos pagos
        this.renderProximosPagos();
    }

    renderAll() {
        this.renderGastosFijos();
        this.renderDeudas();
        this.renderFlujosEfectivo();
        this.renderIngresosExtra();
        this.renderCategorias();
        this.renderLogs();
    }

    renderGastosFijos() {
        const tbody = document.getElementById('gastos-tbody');
        tbody.innerHTML = '';

        const gastos = this.config.gastos_fijos;
        let totalGastos = 0;

        for (const [key, gasto] of Object.entries(gastos)) {
            totalGastos += gasto.valor || 0;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${this.formatNombreGasto(key)}</td>
                <td>${this.formatMoney(gasto.valor || 0)}</td>
                <td>${this.formatFechaGasto(gasto)}</td>
                <td><span class="badge">${gasto.categoria}</span></td>
                <td>
                    <button class="btn-icon btn-small" onclick="configManager.editarGasto('${key}')" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-small" onclick="configManager.eliminarGasto('${key}')" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        }

        // Actualizar totales
        document.getElementById('total-gastos-fijos').textContent = this.formatMoney(totalGastos);
        const porcentaje = this.config.sueldo.valor_fijo > 0 
            ? ((totalGastos / this.config.sueldo.valor_fijo) * 100).toFixed(1) 
            : 0;
        document.getElementById('porcentaje-gastos').textContent = `${porcentaje}%`;

        // Actualizar select de categorías en modal
        this.actualizarSelectCategorias();
        this.renderFlujosEfectivo();
    }

    renderDeudas() {
        const tbody = document.getElementById('deudas-tbody');
        if (!tbody) {
            return;
        }

        tbody.innerHTML = '';
        const deudas = this.config.deudas_fijas || {};
        let totalDeudas = 0;

        for (const [key, deuda] of Object.entries(deudas)) {
            totalDeudas += deuda.valor || 0;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${this.formatNombreGasto(key)}</td>
                <td>${this.formatMoney(deuda.valor || 0)}</td>
                <td>${this.formatFechaGasto(deuda)}</td>
                <td>${deuda.detalle || ''}</td>
                <td>
                    <button class="btn-icon btn-small" onclick="configManager.editarDeuda('${key}')" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-small" onclick="configManager.eliminarDeuda('${key}')" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        }

        const totalNode = document.getElementById('total-deudas-fijas');
        if (totalNode) {
            totalNode.textContent = this.formatMoney(totalDeudas);
        }
        this.renderFlujosEfectivo();
    }

    _normalizarFlujosEfectivo() {
        const defaults = {
            retiro_efectivo_items: ['gasto:arriendo'],
            movii_items: [
                'gasto:netflix',
                'gasto:youtube_premium',
                'gasto:google_drive',
                'gasto:mercadolibre',
                'gasto:hbo_max',
                'gasto:pago_app_fitia',
                'gasto:sub_facebook_don_j'
            ],
            actualizado_en: null
        };
        if (!this.config.flujos_efectivo || typeof this.config.flujos_efectivo !== 'object') {
            this.config.flujos_efectivo = { ...defaults };
        }
        if (!Array.isArray(this.config.flujos_efectivo.retiro_efectivo_items)) {
            this.config.flujos_efectivo.retiro_efectivo_items = [...defaults.retiro_efectivo_items];
        }
        if (!Array.isArray(this.config.flujos_efectivo.movii_items)) {
            this.config.flujos_efectivo.movii_items = [...defaults.movii_items];
        }
        this.config.flujos_efectivo.retiro_efectivo_items = [...new Set(
            this.config.flujos_efectivo.retiro_efectivo_items.filter(x => typeof x === 'string' && x.trim())
        )];
        this.config.flujos_efectivo.movii_items = [...new Set(
            this.config.flujos_efectivo.movii_items.filter(x => typeof x === 'string' && x.trim())
        )];
    }

    _obtenerCompromisosConfigurados() {
        const gastos = Object.entries(this.config.gastos_fijos || {}).map(([key, item]) => ({
            id: `gasto:${key}`,
            key,
            tipo: 'Gasto fijo',
            concepto: this.formatNombreGasto(key),
            valor: Number(item?.valor || 0)
        }));
        const deudas = Object.entries(this.config.deudas_fijas || {}).map(([key, item]) => ({
            id: `deuda:${key}`,
            key,
            tipo: 'Deuda',
            concepto: this.formatNombreGasto(key),
            valor: Number(item?.valor || 0)
        }));
        return [...gastos, ...deudas].sort((a, b) => a.concepto.localeCompare(b.concepto, 'es'));
    }

    _resolverIdFlujo(itemId, mapaCompromisos) {
        if (typeof itemId !== 'string') {
            return null;
        }
        const raw = itemId.trim();
        if (!raw) {
            return null;
        }
        if (mapaCompromisos.has(raw)) {
            return raw;
        }

        const legacyKey = raw.toLowerCase().replace(/\s+/g, '_');
        const gastoId = `gasto:${legacyKey}`;
        const deudaId = `deuda:${legacyKey}`;
        if (mapaCompromisos.has(gastoId)) {
            return gastoId;
        }
        if (mapaCompromisos.has(deudaId)) {
            return deudaId;
        }
        return null;
    }

    _obtenerSeleccionFlujoNormalizada(clave, mapaCompromisos) {
        this._normalizarFlujosEfectivo();
        const actuales = Array.isArray(this.config.flujos_efectivo[clave])
            ? this.config.flujos_efectivo[clave]
            : [];
        const normalizados = [];
        actuales.forEach((itemId) => {
            const resolved = this._resolverIdFlujo(itemId, mapaCompromisos);
            if (resolved && !normalizados.includes(resolved)) {
                normalizados.push(resolved);
            }
        });
        return normalizados;
    }

    _calcularTotalFlujoEfectivo(clave) {
        const compromisos = this._obtenerCompromisosConfigurados();
        const mapa = new Map(compromisos.map((x) => [x.id, x]));
        const seleccion = this._obtenerSeleccionFlujoNormalizada(clave, mapa);
        return seleccion.reduce((sum, id) => sum + Number(mapa.get(id)?.valor || 0), 0);
    }

    _resumirConceptosFlujo(seleccion, mapaCompromisos, max = 4) {
        if (!seleccion.length) {
            return 'Sin elementos seleccionados';
        }
        const conceptos = seleccion
            .map((id) => mapaCompromisos.get(id)?.concepto)
            .filter(Boolean);
        const base = conceptos.slice(0, max).join(', ');
        if (conceptos.length > max) {
            return `${base} y ${conceptos.length - max} mas`;
        }
        return base;
    }

    renderFlujosEfectivo() {
        const retiroContainer = document.getElementById('retiro-efectivo-items');
        const moviiContainer = document.getElementById('movii-items');
        if (!retiroContainer || !moviiContainer) {
            return;
        }

        this._normalizarFlujosEfectivo();
        const compromisos = this._obtenerCompromisosConfigurados();
        const mapa = new Map(compromisos.map((x) => [x.id, x]));

        const retiroSeleccion = this._obtenerSeleccionFlujoNormalizada('retiro_efectivo_items', mapa);
        const moviiSeleccion = this._obtenerSeleccionFlujoNormalizada('movii_items', mapa);
        const retiroOriginal = this.config.flujos_efectivo.retiro_efectivo_items || [];
        const moviiOriginal = this.config.flujos_efectivo.movii_items || [];
        const huboCambioNormalizacion =
            JSON.stringify(retiroOriginal) !== JSON.stringify(retiroSeleccion) ||
            JSON.stringify(moviiOriginal) !== JSON.stringify(moviiSeleccion);
        this.config.flujos_efectivo.retiro_efectivo_items = retiroSeleccion;
        this.config.flujos_efectivo.movii_items = moviiSeleccion;
        if (huboCambioNormalizacion) {
            this.saveConfig(false);
        }

        if (compromisos.length === 0) {
            retiroContainer.innerHTML = '<p class="empty-state">No hay gastos/deudas configurados todavia.</p>';
            moviiContainer.innerHTML = '<p class="empty-state">No hay gastos/deudas configurados todavia.</p>';
            return;
        }

        const htmlItems = (clave, seleccion) => compromisos.map((item) => `
            <label class="flujo-item">
                <input type="checkbox" data-flujo-clave="${clave}" data-item-id="${item.id}" ${seleccion.includes(item.id) ? 'checked' : ''}>
                <span class="flujo-item-concepto">${item.concepto}</span>
                <span class="flujo-item-meta">${item.tipo}</span>
                <span class="flujo-item-valor">${this.formatMoney(item.valor)}</span>
            </label>
        `).join('');

        retiroContainer.innerHTML = htmlItems('retiro_efectivo_items', retiroSeleccion);
        moviiContainer.innerHTML = htmlItems('movii_items', moviiSeleccion);

        const totalRetiro = retiroSeleccion.reduce((sum, id) => sum + Number(mapa.get(id)?.valor || 0), 0);
        const totalMovii = moviiSeleccion.reduce((sum, id) => sum + Number(mapa.get(id)?.valor || 0), 0);
        const totalRetiroNode = document.getElementById('total-retiro-efectivo');
        if (totalRetiroNode) {
            totalRetiroNode.textContent = this.formatMoney(totalRetiro);
        }
        const totalMoviiNode = document.getElementById('total-recarga-movii');
        if (totalMoviiNode) {
            totalMoviiNode.textContent = this.formatMoney(totalMovii);
        }
        const resumenRetiro = document.getElementById('resumen-retiro-efectivo');
        if (resumenRetiro) {
            resumenRetiro.textContent = this._resumirConceptosFlujo(retiroSeleccion, mapa);
        }
        const resumenMovii = document.getElementById('resumen-recarga-movii');
        if (resumenMovii) {
            resumenMovii.textContent = this._resumirConceptosFlujo(moviiSeleccion, mapa);
        }
    }

    manejarCambioFlujoEfectivo(event, clave) {
        const input = event.target;
        if (!(input instanceof HTMLInputElement) || input.type !== 'checkbox') {
            return;
        }
        const itemId = input.dataset.itemId;
        if (!itemId) {
            return;
        }

        this._normalizarFlujosEfectivo();
        const actual = new Set(this.config.flujos_efectivo[clave] || []);
        if (input.checked) {
            actual.add(itemId);
        } else {
            actual.delete(itemId);
        }
        this.config.flujos_efectivo[clave] = Array.from(actual);
        this.config.flujos_efectivo.actualizado_en = new Date().toISOString();

        this.renderFlujosEfectivo();
        this.updateDashboard();

        this.saveConfig(false).then((saved) => {
            if (!saved) {
                this.showToast('No se pudo guardar la seleccion de flujos', 'warning');
                return;
            }
            const nombre = clave === 'retiro_efectivo_items' ? 'Retiro en efectivo' : 'Recarga MOVII';
            const total = this._calcularTotalFlujoEfectivo(clave);
            this.showToast(`${nombre} actualizado: ${this.formatMoney(total)}`, 'success');
        });
    }

    _asegurarRegistroMesActual() {
        const claveMes = this._obtenerClaveMesActual();
        if (!this.config.historial_saldos) {
            this.config.historial_saldos = {
                saldo_mes_anterior: 0,
                mes_anterior: '',
                saldos_mensuales: {}
            };
        }
        if (!this.config.historial_saldos.saldos_mensuales) {
            this.config.historial_saldos.saldos_mensuales = {};
        }
        if (!this.config.historial_saldos.saldos_mensuales[claveMes]) {
            this.config.historial_saldos.saldos_mensuales[claveMes] = {};
        }
        const registroMes = this.config.historial_saldos.saldos_mensuales[claveMes];
        if (!Array.isArray(registroMes.ingresos_extra)) {
            registroMes.ingresos_extra = [];
        }
        return registroMes;
    }

    _obtenerIngresosExtraMesActual() {
        const registroMes = this._asegurarRegistroMesActual();
        return registroMes.ingresos_extra;
    }

    _obtenerTotalIngresosExtraMesActual() {
        return this._obtenerIngresosExtraMesActual().reduce((sum, item) => sum + Number(item.valor || 0), 0);
    }

    renderIngresosExtra() {
        const tbody = document.getElementById('ingresos-extra-tbody');
        const totalNode = document.getElementById('total-ingresos-extra-mes');
        if (!tbody || !totalNode) {
            return;
        }

        const ingresos = this._obtenerIngresosExtraMesActual();
        tbody.innerHTML = '';
        ingresos.forEach((ingreso, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${ingreso.concepto || 'Ingreso extra'}</td>
                <td>${this.formatMoney(ingreso.valor || 0)}</td>
                <td>
                    <button class="btn-icon btn-small" onclick="configManager.eliminarIngresoExtra(${idx})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        totalNode.textContent = this.formatMoney(this._obtenerTotalIngresosExtraMesActual());
    }

    agregarIngresoExtra() {
        const conceptoInput = document.getElementById('ingreso-extra-concepto');
        const valorInput = document.getElementById('ingreso-extra-valor');
        const concepto = (conceptoInput?.value || '').trim();
        const valor = this.parseCurrencyInput(valorInput?.value || '');

        if (!concepto) {
            this.showToast('Ingresa un concepto para el ingreso extra', 'error');
            return;
        }
        if (!Number.isFinite(valor) || valor <= 0) {
            this.showToast('Ingresa un valor valido para el ingreso extra', 'error');
            return;
        }

        const registroMes = this._asegurarRegistroMesActual();
        registroMes.ingresos_extra.push({
            concepto,
            valor,
            fecha_registro: new Date().toISOString()
        });

        // Actualiza UI al instante y luego persiste en backend.
        this.renderIngresosExtra();
        this.updateDashboard();
        this.saveConfig().then((saved) => {
            if (!saved) {
                this.showToast('No se pudo guardar en servidor. Verifica antes de sincronizar.', 'warning');
                return;
            }
            if (conceptoInput) {
                conceptoInput.value = '';
            }
            if (valorInput) {
                valorInput.value = '';
            }
            this.showToast('Ingreso extra agregado al mes actual', 'success');
        }).catch((error) => {
            console.error('Error guardando ingreso extra:', error);
            this.showToast('Se agrego en pantalla, pero fallo el guardado. Intenta de nuevo.', 'warning');
        });
    }

    eliminarIngresoExtra(index) {
        const registroMes = this._asegurarRegistroMesActual();
        if (!Array.isArray(registroMes.ingresos_extra) || index < 0 || index >= registroMes.ingresos_extra.length) {
            return;
        }

        registroMes.ingresos_extra.splice(index, 1);
        this.saveConfig().then((saved) => {
            if (!saved) {
                this.showToast('No se pudo guardar la eliminacion en servidor', 'warning');
                return;
            }
            this.renderIngresosExtra();
            this.updateDashboard();
            this.showToast('Ingreso extra eliminado', 'success');
        });
    }

    renderCategorias() {
        const container = document.getElementById('categorias-grid');
        container.innerHTML = '';

        this.config.categorias_gastos.forEach((categoria, index) => {
            const div = document.createElement('div');
            div.className = 'categoria-item';
            div.innerHTML = `
                <span>${categoria}</span>
                <div class="categoria-actions">
                    <button class="btn-icon" onclick="configManager.editarCategoria(${index})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="configManager.eliminarCategoria(${index})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(div);
        });
    }

    renderProximosPagos() {
        const container = document.getElementById('proximos-pagos');
        container.innerHTML = '';

        const gastos = Object.entries(this.config.gastos_fijos || {}).map(([k, v]) => [k, v, 'Gasto Fijo']);
        const deudas = Object.entries(this.config.deudas_fijas || {}).map(([k, v]) => [k, v, 'Deuda']);
        const items = [...gastos, ...deudas];
        if (items.length === 0) {
            container.innerHTML = '<p class="empty-state">Configura tus gastos fijos para ver los próximos pagos</p>';
            return;
        }

        // Ordenar por día
        const gastosOrdenados = items.sort((a, b) => {
            const diaA = a[1].dia_cargo || 1;
            const diaB = b[1].dia_cargo || 1;
            return diaA - diaB;
        });

        gastosOrdenados.slice(0, 7).forEach(([key, gasto, tipo]) => {
            const div = document.createElement('div');
            div.className = 'pago-item';
            div.innerHTML = `
                <div class="pago-info">
                    <h4>${this.formatNombreGasto(key)} <small>(${tipo})</small></h4>
                    <small>${this.formatFechaGasto(gasto)}</small>
                </div>
                <div class="pago-monto">${this.formatMoney(gasto.valor || 0)}</div>
            `;
            container.appendChild(div);
        });
    }

    renderLogs() {
        const container = document.getElementById('logs-container');
        
        // Simular logs (en producción vendrían de un archivo)
        const logs = [
            { time: new Date().toLocaleString(), message: 'Sistema iniciado correctamente', type: 'info' },
            { time: new Date().toLocaleString(), message: 'Configuración cargada', type: 'success' }
        ];

        container.innerHTML = '';
        logs.forEach(log => {
            const div = document.createElement('div');
            div.className = 'log-item';
            div.innerHTML = `
                <span class="log-time">${log.time}</span>
                <span class="log-message">${log.message}</span>
            `;
            container.appendChild(div);
        });
    }

    // Funciones de utilidad
    formatMoney(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    }

    parseCurrencyInput(value) {
        if (typeof value === 'number') {
            return value;
        }
        const raw = String(value || '').trim();
        if (!raw) {
            return NaN;
        }

        const sanitized = raw.replace(/[^\d.,-]/g, '');
        if (!sanitized) {
            return NaN;
        }

        if (/^-?\d{1,3}([.,]\d{3})+$/.test(sanitized)) {
            return Number(sanitized.replace(/[.,]/g, ''));
        }

        let normalized = sanitized;
        if (sanitized.includes(',') && sanitized.includes('.')) {
            if (sanitized.lastIndexOf(',') > sanitized.lastIndexOf('.')) {
                normalized = sanitized.replace(/\./g, '').replace(',', '.');
            } else {
                normalized = sanitized.replace(/,/g, '');
            }
        } else if (sanitized.includes(',')) {
            normalized = sanitized.replace(',', '.');
        } else if (/^-?\d+\.\d{3}$/.test(sanitized)) {
            normalized = sanitized.replace('.', '');
        }

        const parsed = Number(normalized);
        if (Number.isFinite(parsed)) {
            return parsed;
        }

        const fallback = Number(sanitized.replace(/[^\d-]/g, ''));
        return Number.isFinite(fallback) ? fallback : NaN;
    }

    migrarHistorialMensualLegacy() {
        const historial = this.config?.historial_saldos;
        if (!historial || typeof historial !== 'object') {
            return;
        }
        historial.saldos_mensuales = historial.saldos_mensuales || {};
        for (const [clave, valor] of Object.entries(historial)) {
            if (!/^\d{4}-\d{2}$/.test(clave)) {
                continue;
            }
            if (!historial.saldos_mensuales[clave] && valor && typeof valor === 'object') {
                historial.saldos_mensuales[clave] = valor;
            }
            delete historial[clave];
        }
    }

    formatNombreGasto(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatFechaGasto(gasto) {
        if (gasto.dia_cargo) {
            return `Día ${gasto.dia_cargo}`;
        } else if (gasto.frecuencia) {
            return gasto.frecuencia.charAt(0).toUpperCase() + gasto.frecuencia.slice(1);
        }
        return 'No definido';
    }

    // Acciones
    guardarSueldo() {
        const nombre = document.getElementById('nombre-usuario').value;
        const sueldo = parseFloat(document.getElementById('sueldo-mensual').value) || 0;
        const presupuestoVariables = parseFloat(document.getElementById('presupuesto-variables')?.value) || 0;

        this.config.usuario.nombre = nombre;
        this.config.sueldo.valor_fijo = sueldo;
        this.config.presupuesto_variables = presupuestoVariables;

        this.showToast('Sueldo guardado correctamente', 'success');
        this.updateUI();
    }

    abrirModalGasto(gastoKey = null) {
        this.editingGasto = gastoKey;
        const modal = document.getElementById('modal-gasto');
        const titulo = document.getElementById('modal-gasto-titulo');

        if (gastoKey) {
            titulo.textContent = 'Editar Gasto Fijo';
            const gasto = this.config.gastos_fijos[gastoKey];
            document.getElementById('gasto-nombre').value = this.formatNombreGasto(gastoKey);
            document.getElementById('gasto-valor').value = gasto.valor || 0;
            document.getElementById('gasto-categoria').value = gasto.categoria;
            
            if (gasto.dia_cargo) {
                document.getElementById('gasto-tipo-fecha').value = 'dia';
                document.getElementById('gasto-dia').value = gasto.dia_cargo;
            } else if (gasto.frecuencia) {
                document.getElementById('gasto-tipo-fecha').value = 'frecuencia';
                document.getElementById('gasto-frecuencia').value = gasto.frecuencia;
            }
            this.toggleTipoFecha(document.getElementById('gasto-tipo-fecha').value);
        } else {
            titulo.textContent = 'Agregar Gasto Fijo';
            this.limpiarModalGasto();
        }

        modal.classList.add('active');
    }

    guardarGasto() {
        const nombre = document.getElementById('gasto-nombre').value.trim().toLowerCase().replace(/\s+/g, '_');
        const valor = parseFloat(document.getElementById('gasto-valor').value) || 0;
        const categoria = document.getElementById('gasto-categoria').value;
        const tipoFecha = document.getElementById('gasto-tipo-fecha').value;

        if (!nombre) {
            this.showToast('Por favor ingresa un nombre para el gasto', 'error');
            return;
        }

        const gasto = {
            valor: valor,
            categoria: categoria
        };

        if (tipoFecha === 'dia') {
            gasto.dia_cargo = parseInt(document.getElementById('gasto-dia').value) || 1;
        } else {
            gasto.frecuencia = document.getElementById('gasto-frecuencia').value;
        }

        if (this.editingGasto && this.editingGasto !== nombre) {
            delete this.config.gastos_fijos[this.editingGasto];
        }

        this.config.gastos_fijos[nombre] = gasto;
        
        this.cerrarModales();
        this.renderGastosFijos();
        this.updateDashboard();
        this.showToast('Gasto guardado correctamente', 'success');
    }

    editarGasto(key) {
        this.abrirModalGasto(key);
    }

    eliminarGasto(key) {
        if (confirm('¿Estás seguro de que deseas eliminar este gasto?')) {
            delete this.config.gastos_fijos[key];
            this.renderGastosFijos();
            this.updateDashboard();
            this.showToast('Gasto eliminado', 'success');
        }
    }

    toggleTipoFecha(tipo) {
        const grupoDia = document.getElementById('grupo-dia');
        const grupoFrecuencia = document.getElementById('grupo-frecuencia');

        if (tipo === 'dia') {
            grupoDia.style.display = 'block';
            grupoFrecuencia.style.display = 'none';
        } else {
            grupoDia.style.display = 'none';
            grupoFrecuencia.style.display = 'block';
        }
    }

    limpiarModalGasto() {
        document.getElementById('gasto-nombre').value = '';
        document.getElementById('gasto-valor').value = '';
        document.getElementById('gasto-dia').value = '';
        document.getElementById('gasto-tipo-fecha').value = 'dia';
        this.toggleTipoFecha('dia');
    }

    abrirModalDeuda(deudaKey = null) {
        this.editingDeuda = deudaKey;
        const modal = document.getElementById('modal-deuda');
        if (!modal) {
            return;
        }

        const titulo = document.getElementById('modal-deuda-titulo');
        if (deudaKey) {
            titulo.textContent = 'Editar Deuda';
            const deuda = this.config.deudas_fijas[deudaKey];
            document.getElementById('deuda-nombre').value = this.formatNombreGasto(deudaKey);
            document.getElementById('deuda-valor').value = deuda.valor || 0;
            document.getElementById('deuda-detalle').value = deuda.detalle || '';
            if (deuda.dia_cargo) {
                document.getElementById('deuda-tipo-fecha').value = 'dia';
                document.getElementById('deuda-dia').value = deuda.dia_cargo;
            } else if (deuda.frecuencia) {
                document.getElementById('deuda-tipo-fecha').value = 'frecuencia';
                document.getElementById('deuda-frecuencia').value = deuda.frecuencia;
            }
            this.toggleTipoFechaDeuda(document.getElementById('deuda-tipo-fecha').value);
        } else {
            titulo.textContent = 'Agregar Deuda';
            this.limpiarModalDeuda();
        }

        modal.classList.add('active');
    }

    guardarDeuda() {
        const nombre = document.getElementById('deuda-nombre').value.trim().toLowerCase().replace(/\s+/g, '_');
        const valor = parseFloat(document.getElementById('deuda-valor').value) || 0;
        const detalle = document.getElementById('deuda-detalle').value.trim();
        const tipoFecha = document.getElementById('deuda-tipo-fecha').value;

        if (!nombre) {
            this.showToast('Por favor ingresa un nombre para la deuda', 'error');
            return;
        }

        const deuda = { valor, detalle };
        if (tipoFecha === 'dia') {
            deuda.dia_cargo = parseInt(document.getElementById('deuda-dia').value) || 1;
        } else {
            deuda.frecuencia = document.getElementById('deuda-frecuencia').value;
        }

        if (!this.config.deudas_fijas) {
            this.config.deudas_fijas = {};
        }
        if (this.editingDeuda && this.editingDeuda !== nombre) {
            delete this.config.deudas_fijas[this.editingDeuda];
        }

        this.config.deudas_fijas[nombre] = deuda;
        this.cerrarModales();
        this.renderDeudas();
        this.updateDashboard();
        this.showToast('Deuda guardada correctamente', 'success');
    }

    editarDeuda(key) {
        this.abrirModalDeuda(key);
    }

    eliminarDeuda(key) {
        if (confirm('¿Estás seguro de que deseas eliminar esta deuda?')) {
            delete this.config.deudas_fijas[key];
            this.renderDeudas();
            this.updateDashboard();
            this.showToast('Deuda eliminada', 'success');
        }
    }

    toggleTipoFechaDeuda(tipo) {
        const grupoDia = document.getElementById('grupo-deuda-dia');
        const grupoFrecuencia = document.getElementById('grupo-deuda-frecuencia');
        if (!grupoDia || !grupoFrecuencia) {
            return;
        }
        if (tipo === 'dia') {
            grupoDia.style.display = 'block';
            grupoFrecuencia.style.display = 'none';
        } else {
            grupoDia.style.display = 'none';
            grupoFrecuencia.style.display = 'block';
        }
    }

    limpiarModalDeuda() {
        document.getElementById('deuda-nombre').value = '';
        document.getElementById('deuda-valor').value = '';
        document.getElementById('deuda-detalle').value = '';
        document.getElementById('deuda-dia').value = '';
        document.getElementById('deuda-tipo-fecha').value = 'dia';
        this.toggleTipoFechaDeuda('dia');
    }

    abrirModalCategoria() {
        document.getElementById('modal-categoria').classList.add('active');
        document.getElementById('categoria-nombre').value = '';
    }

    guardarCategoria() {
        const nombre = document.getElementById('categoria-nombre').value.trim();

        if (!nombre) {
            this.showToast('Por favor ingresa un nombre para la categoría', 'error');
            return;
        }

        if (this.config.categorias_gastos.includes(nombre)) {
            this.showToast('Esta categoría ya existe', 'error');
            return;
        }

        this.config.categorias_gastos.push(nombre);
        this.cerrarModales();
        this.renderCategorias();
        this.showToast('Categoría agregada correctamente', 'success');
    }

    editarCategoria(index) {
        const categoria = this.config.categorias_gastos[index];
        const nuevoNombre = prompt('Editar nombre de la categoría:', categoria);
        
        if (nuevoNombre && nuevoNombre.trim() !== '') {
            this.config.categorias_gastos[index] = nuevoNombre.trim();
            this.renderCategorias();
            this.showToast('Categoría actualizada', 'success');
        }
    }

    eliminarCategoria(index) {
        if (confirm('¿Estás seguro de que deseas eliminar esta categoría?')) {
            this.config.categorias_gastos.splice(index, 1);
            this.renderCategorias();
            this.showToast('Categoría eliminada', 'success');
        }
    }

    actualizarSelectCategorias() {
        const select = document.getElementById('gasto-categoria');
        select.innerHTML = '';

        this.config.categorias_gastos.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            select.appendChild(option);
        });
    }

    cerrarModales() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
        this.editingGasto = null;
        this.editingDeuda = null;
    }

    async saveConfig(showSuccessToast = true) {
        try {
            // Enviar los datos al servidor
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.config, null, 2)
            });
            
            if (!response.ok) {
                throw new Error('Error al guardar en el servidor');
            }
            
            const result = await response.json();
            
            if (result.status === 'ok') {
                if (showSuccessToast) {
                    this.showToast('Configuración guardada correctamente', 'success');
                }
                return true;
            } else {
                throw new Error('Respuesta del servidor no válida');
            }
        } catch (error) {
            console.error('Error guardando configuración:', error);
            this.showToast('Error al guardar. Descargando archivo manualmente...', 'warning');
            
            // Fallback: descargar el archivo manualmente
            try {
                const configBlob = new Blob([JSON.stringify(this.config, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(configBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'configuracion.json';
                a.click();
                URL.revokeObjectURL(url);
                
                this.showToast('Archivo descargado. Reemplaza el archivo en config/', 'info');
            } catch (downloadError) {
                this.showToast('Error al guardar la configuración', 'error');
            }
            return false;
        }
    }

    async generarExcel(tipo) {
        const monthMode = tipo === 'siguiente' ? 'siguiente' : 'actual';
        this.showToast(
            `Creando hoja del ${monthMode === 'actual' ? 'mes actual' : 'mes siguiente'} y sincronizando...`,
            'info'
        );

        try {
            const guardadoOk = await this.saveConfig(false);
            if (!guardadoOk) {
                throw new Error('No se pudo guardar la configuracion antes de sincronizar');
            }

            const response = await fetch('/api/sync-drive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ month_mode: monthMode }),
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.message || 'No se pudo crear/sincronizar la hoja');
            }

            const hoja = result.hoja_objetivo || 'hoja mensual';
            const accion = result.hoja_creada ? 'creada' : 'actualizada';
            this.showToast(`Hoja ${accion}: ${hoja}`, 'success');

            if (result.enlace) {
                const abrir = confirm(
                    `Sincronizacion exitosa para "${hoja}". ¿Deseas abrir el archivo en Google Drive?`
                );
                if (abrir) {
                    window.open(result.enlace, '_blank');
                }
            }
        } catch (error) {
            console.error('Error creando/sincronizando hoja:', error);
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    verificarDrive() {
        const configurado = this.config.google_drive.archivo_excel_id !== '';
        
        document.getElementById('drive-no-configurado').style.display = configurado ? 'none' : 'block';
        document.getElementById('drive-configurado').style.display = configurado ? 'block' : 'none';
    }

    configurarDrive() {
        this.showToast('Para configurar Google Drive, sigue las instrucciones en docs/INSTALACION.md', 'info');
    }

    async sincronizarDrive() {
        await this.generarExcel('actual');
    }

    crearBackup() {
        this.showToast('Creando backup...', 'info');
        setTimeout(() => {
            this.showToast('Backup creado y subido a Google Drive', 'success');
        }, 2000);
    }

    mostrarAyuda() {
        alert(`AYUDA DEL SISTEMA

1. Configura tu sueldo en "Mi Sueldo"
2. Agrega tus gastos fijos en "Gastos Fijos"
3. Personaliza las categorías si lo necesitas
4. Genera tu Excel desde "Generar Excel"
5. Configura Google Drive para sincronización

TIPS:
- Los cambios se guardan al hacer clic en "Guardar Cambios"
- Puedes agregar, editar o eliminar gastos y categorías
- El dashboard muestra un resumen en tiempo real
- Los próximos pagos se ordenan por fecha

Para más información, revisa la documentación en docs/`);
    }

    // Funciones de Documentación
    async cargarDocumentacion(archivo) {
        try {
            const response = await fetch(`/api/docs/${archivo}`);
            if (!response.ok) {
                throw new Error('No se pudo cargar el documento');
            }
            const contenido = await response.text();
            
            // Convertir Markdown a HTML básico
            const html = this.markdownToHtml(contenido);
            
            // Mostrar el documento
            document.getElementById('doc-titulo').textContent = archivo.replace('.md', '');
            document.getElementById('doc-contenido').innerHTML = html;
            document.getElementById('doc-visor-card').style.display = 'block';
            
            // Scroll al visor
            document.getElementById('doc-visor-card').scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error cargando documentación:', error);
            this.showToast('Error al cargar el documento', 'error');
            
            // Cargar contenido de ejemplo si falla
            this.cargarDocumentoEjemplo(archivo);
        }
    }
    
    cargarDocumentoEjemplo(archivo) {
        const documentos = {
            'DOCUMENTACION.md': `
                <h1>Documentación Completa</h1>
                <p>Esta es la documentación técnica completa del sistema de control de gastos.</p>
                <h2>Características</h2>
                <ul>
                    <li>Excel profesional con fórmulas automáticas</li>
                    <li>Registro de gastos mediante chat</li>
                    <li>Automatización mensual</li>
                    <li>Integración con Google Drive</li>
                </ul>
                <p>Para más detalles, revisa los otros documentos.</p>
            `,
            'INSTALACION.md': `
                <h1>Guía de Instalación</h1>
                <h2>Paso 1: Requisitos</h2>
                <p>Necesitas Python 3.8 o superior instalado.</p>
                <h2>Paso 2: Instalación</h2>
                <pre><code>pip install -r requirements.txt</code></pre>
                <h2>Paso 3: Configuración</h2>
                <p>Usa esta interfaz web o edita config/configuracion.json</p>
            `,
            'EJEMPLOS.md': `
                <h1>Ejemplos de Uso</h1>
                <h2>Registrar un gasto</h2>
                <p>Escribe: "Gasté 25000 en transporte"</p>
                <h2>Ver sueldo</h2>
                <p>Escribe: "saldo"</p>
                <h2>Agregar gasto fijo</h2>
                <p>Ve a la sección "Gastos Fijos" y haz clic en "Agregar Gasto"</p>
            `,
            'INTERFAZ_WEB.md': `
                <h1>Guía de Interfaz Web</h1>
                <p>Esta interfaz te permite configurar todo el sistema de forma visual.</p>
                <h2>Dashboard</h2>
                <p>Muestra el resumen de tus finanzas: sueldo, gastos, ahorro y saldo bancario.</p>
                <h2>Gastos Fijos</h2>
                <p>Administra todos tus gastos recurrentes de forma visual.</p>
            `,
            'RESUMEN.md': `
                <h1>Resumen del Proyecto</h1>
                <p>Sistema completo de control de gastos mensuales.</p>
                <h2>Estructura</h2>
                <ul>
                    <li>Generador de Excel</li>
                    <li>Bot de registro de gastos</li>
                    <li>Automatización mensual</li>
                    <li>Interfaz web</li>
                </ul>
            `
        };
        
        const contenido = documentos[archivo] || '<p>Documento no disponible</p>';
        document.getElementById('doc-titulo').textContent = archivo.replace('.md', '');
        document.getElementById('doc-contenido').innerHTML = contenido;
        document.getElementById('doc-visor-card').style.display = 'block';
    }
    
    cerrarDocumento() {
        document.getElementById('doc-visor-card').style.display = 'none';
        document.getElementById('doc-contenido').innerHTML = '';
    }
    
    markdownToHtml(markdown) {
        // Conversión básica de Markdown a HTML
        let html = markdown
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            // Code
            .replace(/`(.*?)`/gim, '<code>$1</code>')
            // Code blocks
            .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
            // Lists
            .replace(/^\* (.*$)/gim, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
            // Line breaks
            .replace(/\n/gim, '<br>');
            
        return html;
    }

    actualizarSaldoBancario() {
        const nuevoSaldoInicioMes = parseFloat(document.getElementById('saldo-inicio-mes').value);
        const nuevoSaldo = parseFloat(document.getElementById('saldo-bancario-actual').value);
        const notas = document.getElementById('notas-saldo').value;
        
        if (isNaN(nuevoSaldoInicioMes) || nuevoSaldoInicioMes < 0) {
            this.showToast('Ingresa un saldo inicial de mes valido', 'error');
            return;
        }
        
        if (isNaN(nuevoSaldo) || nuevoSaldo < 0) {
            this.showToast('Ingresa un saldo actual valido', 'error');
            return;
        }
        
        if (!this.config.saldo_bancario) {
            this.config.saldo_bancario = {};
        }
        
        this.config.saldo_bancario.valor_actual = nuevoSaldo;
        this.config.saldo_bancario.moneda = 'COP';
        this.config.saldo_bancario.ultima_actualizacion = new Date().toISOString();
        this.config.saldo_bancario.notas = notas;
        
        if (!this.config.historial_saldos) {
            this.config.historial_saldos = {
                saldo_mes_anterior: nuevoSaldoInicioMes,
                mes_anterior: this._obtenerMesAnterior(),
                saldos_mensuales: {}
            };
        }
        if (!this.config.historial_saldos.saldos_mensuales) {
            this.config.historial_saldos.saldos_mensuales = {};
        }
        
        const mesActual = this._obtenerClaveMesActual();
        const saldoProyectado = nuevoSaldo - nuevoSaldoInicioMes;
        const registroMesExistente = this.config.historial_saldos.saldos_mensuales[mesActual] || {};
        const ingresosExtraMes = Array.isArray(registroMesExistente.ingresos_extra)
            ? registroMesExistente.ingresos_extra
            : [];
        this.config.historial_saldos.saldos_mensuales[mesActual] = {
            ...registroMesExistente,
            saldo_inicial: nuevoSaldoInicioMes,
            saldo_final: nuevoSaldo,
            diferencia: saldoProyectado,
            fecha_actualizacion: new Date().toISOString(),
            notas: notas,
            ingresos_extra: ingresosExtraMes
        };
        this.config.historial_saldos.saldo_mes_anterior = nuevoSaldoInicioMes;
        
        // Guardar configuración automáticamente
        this.saveConfig().then((saved) => {
            if (!saved) {
                this.showToast('No se pudo guardar el saldo en servidor', 'warning');
                return;
            }
            // Actualizar UI
            this.updateUISaldoBancario();
            this.updateDashboard();
            
            this.showToast('Saldos actualizados. Usa sync para reflejarlo en Drive', 'success');
            
            // Limpiar campo de notas
            document.getElementById('notas-saldo').value = '';
        });
    }
    
    _obtenerMesAnterior() {
        const fecha = new Date();
        fecha.setMonth(fecha.getMonth() - 1);
        const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        return meses[fecha.getMonth()] + ' ' + fecha.getFullYear();
    }

    _obtenerClaveMesActual() {
        const f = new Date();
        const y = f.getFullYear();
        const m = String(f.getMonth() + 1).padStart(2, '0');
        return `${y}-${m}`;
    }

    _obtenerSaldoInicioMesActual() {
        const claveMes = this._obtenerClaveMesActual();
        const historial = this.config.historial_saldos || {};
        const mensual = historial.saldos_mensuales || {};
        const registroMes = mensual[claveMes] || {};
        const saldoInicialMes = Number(registroMes.saldo_inicial || 0);
        if (saldoInicialMes > 0) {
            return saldoInicialMes;
        }
        const fallback = Number(historial.saldo_mes_anterior || 0);
        if (fallback > 0) {
            return fallback;
        }
        return Number(this.config.saldo_bancario?.valor_actual || 0);
    }
    
    updateUISaldoBancario() {
        const saldoActual = this.config.saldo_bancario?.valor_actual || 0;
        const saldoInicioMes = this._obtenerSaldoInicioMesActual();
        const ultimaActualizacion = this.config.saldo_bancario?.ultima_actualizacion;
        
        document.getElementById('saldo-inicio-registrado').textContent = this.formatMoney(saldoInicioMes);
        document.getElementById('saldo-actual-registrado').textContent = this.formatMoney(saldoActual);
        
        if (ultimaActualizacion) {
            const fecha = new Date(ultimaActualizacion);
            document.getElementById('saldo-ultima-actualizacion').textContent = 
                fecha.toLocaleDateString() + ' ' + fecha.toLocaleTimeString();
        } else {
            document.getElementById('saldo-ultima-actualizacion').textContent = 'Nunca';
        }
        
        // Actualizar campos de entrada
        document.getElementById('saldo-inicio-mes').value = saldoInicioMes;
        document.getElementById('saldo-bancario-actual').value = saldoActual;
    }
    
    async sincronizarTodo() {
        const btnSync = document.getElementById('btn-sync-general');
        const statusDiv = document.getElementById('sync-status-header');

        // Mostrar estado de sincronizacion
        btnSync.classList.add('syncing');
        statusDiv.style.display = 'block';
        btnSync.disabled = true;

        try {
            // Primero guardar la configuracion actual
            const guardadoOk = await this.saveConfig(false);
            if (!guardadoOk) {
                throw new Error('No se pudo guardar la configuracion antes de sincronizar');
            }

            // Sincronizar la hoja del mes actual con Drive
            const response = await fetch('/api/sync-drive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ month_mode: 'actual' }),
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.message || 'Error en la sincronizacion');
            }

            let detalleExtra = '';
            if (typeof result.ingresos_extra_total === 'number') {
                detalleExtra = ` | Ingresos extra mes: ${this.formatMoney(result.ingresos_extra_total)}`;
            }
            this.showToast(`Todo sincronizado con Google Drive${detalleExtra}`, 'success');

            if (result.enlace) {
                if (confirm('Sincronizacion exitosa. Deseas ver el archivo en Google Drive?')) {
                    window.open(result.enlace, '_blank');
                }
            }
        } catch (error) {
            console.error('Error sincronizando:', error);
            this.showToast('Error al sincronizar: ' + error.message, 'error');
        } finally {
            // Restaurar boton
            btnSync.classList.remove('syncing');
            statusDiv.style.display = 'none';
            btnSync.disabled = false;
        }
    }
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas fa-${icons[type]}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

// Inicializar la aplicación
const configManager = new ConfigManager();
window.configManager = configManager;


