<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed } from 'vue';

export default {
    components: {
        Header,
        Footer,
    },

    setup() {
        const listaCuotas = ref([]);
        const isLoading = ref(false);
        const mensaje = ref('');
        const tipoMensaje = ref('');

        // MODIFICACIÓN: Nuevas variables para capturar la respuesta de la API
        const totalPrecioVenta = ref(0);
        const totalCostos = ref(0);
        const totalNeto = ref(0);
        const totalImpagoReal = ref(0); // Nuevo: Sumatoria de solo cuotas atrasadas

        const cargarTotalVentaSinPresupuesto = async () => {
            try {
                const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/total-sin-presupuesto/`;
                const response = await fetch(apiUrl);

                if (response.ok) {
                    const data = await response.json();

                    // MODIFICACIÓN: Capturamos los 3 valores (neto, venta, costos)
                    totalPrecioVenta.value = data.total_precio_venta || 0;
                    totalCostos.value = data.total_costos || 0;
                    totalNeto.value = data.total_neto || 0;
                } else {
                    const errorText = await response.text();
                    console.error(`Error ${response.status} cargando total de venta sin presupuesto:`, errorText);
                    totalPrecioVenta.value = 0;
                    totalCostos.value = 0;
                    totalNeto.value = 0;
                }
            } catch (error) {
                console.error('Error de conexión cargando total de venta sin presupuesto:', error);
                totalPrecioVenta.value = 0;
                totalCostos.value = 0;
                totalNeto.value = 0;
            }
        };

        const cargarTotalImpagoReal = async () => {
            try {
                // Usamos el endpoint de cuotas impagas para obtener la suma exacta de lo vencido
                // Esto asegura consistencia con la vista de CuotasImpagas.vue
                const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/cuotas_impagas/`;
                const response = await fetch(apiUrl);

                if (response.ok) {
                    const data = await response.json();
                    // Sumamos 'monto_cuota' de todas las cuotas que vienen en este endpoint (que ya son las atrasadas)
                    // Ojo: En CuotasImpagas logic se sumaba si dias_atraso > 0.
                    // El endpoint devuelve una lista plana de cuotas con dias_atraso calculados.
                    // Filtramos por si acaso el endpoint trajera algo no vencido (aunque su nombre lo indica),
                    // y sumamos.

                    let suma = 0;
                    data.forEach(cuota => {
                        if (cuota.dias_atraso > 10 && parseInt(cuota.estado) === 0) {
                            suma += parseFloat(cuota.monto_cuota || 0);
                        }
                    });
                    totalImpagoReal.value = suma;
                }
            } catch (error) {
                console.error('Error cargando total impago real:', error);
            }
        };

        const porcentajeImpagoGeneral = computed(() => {
            // El 'Saldo Total Pendiente (General)' es 'totalesGeneralesPendientes.value.totalSaldo'
            const totalPendiente = totalesGeneralesPendientes.value?.totalSaldo || 0;
            if (totalPendiente === 0) return 0;
            return ((totalImpagoReal.value / totalPendiente) * 100).toFixed(2);
        });

        const formatearMilesConPunto = (valor) => {
            if (valor === null || valor === undefined || isNaN(parseFloat(valor))) {
                return '';
            }
            const num = Math.round(parseFloat(valor));
            const formatter = new Intl.NumberFormat('de-DE');
            return formatter.format(num);
        };

        const mostrarMensaje = (texto, tipo) => {
            mensaje.value = texto;
            tipoMensaje.value = tipo;
            setTimeout(limpiarMensaje, 3000);
        };

        const limpiarMensaje = () => {
            mensaje.value = '';
            tipoMensaje.value = '';
        };

        const cargarListaDeCuotas = async () => {
            isLoading.value = true;
            listaCuotas.value = [];
            try {
                let apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/`;
                const response = await fetch(apiUrl);

                if (response.ok) {
                    const data = await response.json();
                    listaCuotas.value = data.data;
                    mostrarMensaje('Total de pagos actualizado para todos los clientes.', 'success');
                } else {
                    console.error('Error cargando el informe de pagos:', response.statusText);
                    mostrarMensaje('Error cargando el informe de pagos.', 'error');
                }
            } catch (error) {
                console.error('Error de conexión cargando el informe de pagos:', error);
                mostrarMensaje('Error de conexión con el servidor.', 'error');
            } finally {
                isLoading.value = false;
            }
        };

        // ... (código existente)

        const listaCuotasProcesada = computed(() => {
            if (!listaCuotas.value || listaCuotas.value.length === 0) {
                return [];
            }

            // APLICAR FILTRO 1: Presupuesto (Solo estado 0 - Activo)
            const cuotasFiltradas = listaCuotas.value.filter(cuota => {
                // Asumimos que el campo 'estado' (del presupuesto) está disponible en el objeto cuota
                const estadoPresupuesto = cuota.estado;
                return parseInt(estadoPresupuesto) === 0; // Solo estado activo
            });

            if (cuotasFiltradas.length === 0) {
                return [];
            }

            // El resto de la lógica de amortización ahora opera sobre las cuotasFiltradas
            const prestamosAgrupados = cuotasFiltradas.reduce((acc, cuota) => {
                const clavePrestamo = `${cuota.rut_cliente}-${cuota.patente}`;
                if (!acc[clavePrestamo]) {
                    acc[clavePrestamo] = [];
                }
                acc[clavePrestamo].push(cuota);
                return acc;
            }, {});

            const cuotasProcesadas = [];
            for (const clavePrestamo in prestamosAgrupados) {
                const cuotasDelPrestamo = prestamosAgrupados[clavePrestamo];
                cuotasDelPrestamo.sort((a, b) => a.numero_cuota - b.numero_cuota);

                let capitalRestante = parseFloat(cuotasDelPrestamo[0].monto_a_financiar || 0);

                cuotasDelPrestamo.forEach(cuota => {
                    if (capitalRestante < 0) capitalRestante = 0;

                    const interesCalculado = (capitalRestante * parseFloat(cuota.interes_mensual || 0)) / 100;
                    let pagoCapital = parseFloat(cuota.monto_cuota || 0) - interesCalculado;

                    if (pagoCapital > capitalRestante) {
                        pagoCapital = capitalRestante;
                    }

                    const capitalAntesDelPago = capitalRestante;
                    capitalRestante -= pagoCapital;

                    const cuotaConCalculos = {
                        ...cuota,
                        interes_calculado: interesCalculado,
                        pago_capital: pagoCapital,
                        monto_a_financiar_calculado: capitalAntesDelPago,
                        saldo: parseFloat(cuota.monto_cuota || 0) - parseFloat(cuota.abono_total || 0)
                    };
                    cuotasProcesadas.push(cuotaConCalculos);
                });
            }

            return cuotasProcesadas;
        });
        // ... (código existente)
        // Propiedad Computada: Solo se suman las cuotas que tienen abono (Pagos Realizados)
        const totalesGenerales = computed(() => {
            const totales = {
                totalInteres: 0,
                totalCapitalAmortizado: 0,
                totalAbonado: 0,
                totalSaldo: 0, // Saldo general
            };

            const lista = listaCuotasProcesada.value;

            lista.forEach(cuota => {
                const abonoReal = parseFloat(cuota.abono_total) || 0;

                totales.totalAbonado += abonoReal;
                totales.totalSaldo += cuota.saldo || 0;

                if (abonoReal > 0) {
                    totales.totalInteres += cuota.interes_calculado || 0;
                    totales.totalCapitalAmortizado += cuota.pago_capital || 0;
                }
            });
            return totales;
        });

        // Propiedad Computada: Solo se suman las cuotas SIN abono (Cuotas NO Abonadas, Abono = 0)
        const totalesGeneralesPendientes = computed(() => {
            const totales = {
                totalInteres: 0,
                totalCapitalAmortizado: 0,
                totalCuota: 0,
                totalSaldo: 0, // Saldo general
            };

            const lista = listaCuotasProcesada.value;

            lista.forEach(cuota => {
                const abonoReal = parseFloat(cuota.abono_total) || 0;

                if (abonoReal === 0) {
                    totales.totalInteres += cuota.interes_calculado || 0;
                    totales.totalCapitalAmortizado += cuota.pago_capital || 0;
                    totales.totalCuota += (cuota.interes_calculado || 0) + (cuota.pago_capital || 0);
                }
                totales.totalSaldo += cuota.saldo || 0;
            });

            return totales;
        });


        // Carga automática al montar el componente
        onMounted(() => {
            cargarListaDeCuotas();
            cargarTotalVentaSinPresupuesto();
            cargarTotalImpagoReal();
        });

        return {
            isLoading,
            mensaje,
            tipoMensaje,
            cargarListaDeCuotas,
            formatearMilesConPunto,
            listaCuotasProcesada,
            totalesGenerales,
            totalesGeneralesPendientes,

            // MODIFICACIÓN: Exponer las nuevas variables
            totalPrecioVenta,
            totalCostos,
            totalNeto,
            porcentajeImpagoGeneral,
        };
    },
};
</script>

<template>
    <Header></Header>

    <div class="container-fluid mt-3">
        <div class="card shadow-sm">
            <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Informe Deuda Clientes
            </div>
            <div class="card-body">

                <div v-if="mensaje" class="alert" :class="{
                    'alert-success': tipoMensaje === 'success',
                    'alert-danger': tipoMensaje === 'error',
                    'alert-info': tipoMensaje === 'info',
                }" role="alert">
                    {{ mensaje }}
                </div>

                <div v-if="isLoading" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2">Cargando informe totalizado de todos los clientes...</p>
                </div>

                <div v-else-if="listaCuotasProcesada.length === 0" class="text-center">
                    No se encontraron cuotas registradas.
                </div>

                <div v-else class="mt-4">

                    <div class="row mb-5">
                        <div class="col-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-success text-white">
                                    <h4 class="mb-0">Resumen Total (Solo Pagos Realizados)</h4>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Utilidad Total **Abonada**:</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalInteres) }}</h5>
                                        </div>
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Total Capital **Amortizado**:</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalCapitalAmortizado) }}
                                            </h5>
                                        </div>
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Suma Total **Abonada** (Real):</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalAbonado) }}</h5>
                                        </div>
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Saldo Total **Pendiente** (Cuotas):</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalSaldo) }}</h5>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>


                    <div class="row mb-5">
                        <div class="col-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-danger text-white">
                                    <h4 class="mb-0">Resumen Total (Cuotas NO Abonadas)</h4>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Utilidad Total**Pendiente**:</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalInteres) }}
                                            </h5>
                                        </div>
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Capital Teórico **Pendiente**:</p>
                                            <h5>$ {{
                                                formatearMilesConPunto(totalesGeneralesPendientes.totalCapitalAmortizado)
                                                }}</h5>
                                        </div>
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Monto Total Cuota **Teórica Pendiente**:</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalCuota) }}
                                            </h5>
                                        </div>
                                        <div class="col-md-3">
                                            <p class="mb-1 negrita">Saldo Total **Pendiente** (General):</p>
                                            <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalSaldo) }}
                                                <br>
                                                <span style="font-size: 1.0em; color: red; font-weight: bold;">
                                                    ({{ porcentajeImpagoGeneral }}% del Total Pendiente)
                                                </span>
                                            </h5>
                                        </div>
                                    </div>

                                    <div class="row mt-4 pt-3 border-top">
                                        <div class="col-md-6 text-info">
                                            <p class="mb-1 negrita">Valorizacion Vehiculos (Venta)</p>
                                            <h5>$ {{ formatearMilesConPunto(totalPrecioVenta) }}</h5>
                                        </div>
                                        <div class="col-md-6 text-success">
                                            <p class="mb-1 negrita">Valor (Venta - Costos)</p>
                                            <h5>$ {{ formatearMilesConPunto(totalNeto) }}</h5>
                                        </div>
                                    </div>
                                    <p class="mt-3 text-muted">

                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>


                </div>
            </div>
        </div>
    </div>
    <Footer></Footer>
</template>

<style scoped>
/* Estilos limpios para evitar el error de sintaxis que reportas */
.negrita {
    font-weight: bolder;
}

.spinner-border {
    width: 2rem;
    height: 2rem;
}
</style>