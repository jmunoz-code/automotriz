<template>
    <Header></Header> 
    <div class="container mt-3">
        <div class="card shadow-sm mt-3 mb-3">
            <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Informe Mensual de Arriendos y Gastos
            </div>
            <div class="card-body mt-3">

                <div class="card mb-4">
                    <div class="card-body">
                        <form @submit.prevent="consultarInforme">
                            <div class="row align-items-end">
                                <div class="col-md-4">
                                    <label for="fecha-filtro" class="form-label negrita">Seleccionar Mes y Año</label>
                                    <input type="month" class="form-control" id="fecha-filtro"
                                        v-model="filtroFecha" required />
                                </div>
                                <div class="col-md-4">
                                    <button type="submit" class="btn btn-success w-100">
                                        <i class="bi bi-search"></i> Generar Informe
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <div v-if="mensaje" class="mt-3 alert"
                    :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error' }">
                    {{ mensaje }}
                </div>

                <div v-if="cargando" class="text-center my-3">
                    <span class="spinner-border spinner-border-sm text-success" role="status"></span>
                    <span class="ms-2">Procesando informe...</span>
                </div>

                <div class="table-responsive" v-if="!cargando && reporteData.length > 0">
                    <h5 class="mb-3 text-muted">Resultados del mes</h5>
                    <table class="table table-hover table-bordered table-sm">
                        <thead class="table-light">
                            <tr>
                                <th>Fecha Inicio</th>
                                <th>Fecha Fin</th>
                                <th>Arrendatario</th>
                                <th>Tipo</th>
                                <th class="text-end">Valor Arriendo</th>
                                <th class="text-center">Comisión</th>
                                <th class="text-end bg-success text-white">(Desc. Com)</th>
                                <th class="text-end text-danger">Gastos del Mes (Global)</th> 
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(item, index) in reporteData" :key="index">
                                <td>{{ formatFecha(item.fecha_inicio) }}</td>
                                <td>{{ formatFecha(item.fecha_fin) }}</td>
                                <td>{{ item.nombre_arrendatario }}</td>
                                <td>{{ item.tipo_arriendo__nombre }}</td>
                                <td class="text-end">{{ formatDinero(item.valor_arriendo) }}</td>
                                <td class="text-center">{{ item.tipo_arriendo__comision }}%</td>
                                <td class="text-end fw-bold text-success">{{ formatDinero(item.desc_com) }}</td>
                                <td class="text-end text-danger">{{ formatDinero(item.total_gastos_mes) }}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr class="table-secondary fw-bold">
                                <td colspan="6" class="text-end">UTILIDAD REAL (Total Ingresos - 1 vez Gasto):</td>
                                
                                <td class="text-end text-primary fs-5">
                                    {{ formatDinero(calcularUtilidadReal()) }}
                                </td>
                                
                                <td class="text-center text-muted">-</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <div v-if="!cargando && reporteData.length === 0 && busquedaRealizada" class="alert alert-warning mt-3 text-center">
                    No se encontraron movimientos para el mes seleccionado.
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import Header from '@/components/HeaderAdmin.vue';
import { ref } from 'vue';

const filtroFecha = ref('');
const reporteData = ref([]);
const cargando = ref(false);
const busquedaRealizada = ref(false);
const mensaje = ref('');
const tipoMensaje = ref('');

const API_URL = `${import.meta.env.VITE_API_URL}informes/reporte-mensual/`;

async function consultarInforme() {
    if (!filtroFecha.value) {
        mostrarMensaje("Por favor selecciona un mes y año", "error");
        return;
    }
    cargando.value = true;
    mensaje.value = '';
    busquedaRealizada.value = true;
    reporteData.value = [];

    try {
        const [anio, mes] = filtroFecha.value.split('-');
        const fechaFormateada = `01-${mes}-${anio}`;

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fecha: fechaFormateada })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al obtener el informe');
        }
        reporteData.value = await response.json();
    } catch (error) {
        console.error(error);
        mostrarMensaje(error.message, 'error');
    } finally {
        cargando.value = false;
    }
}

// --- AQUÍ ESTÁ LA MAGIA MATEMÁTICA ---
function calcularUtilidadReal() {
    // Si la lista está vacía, retornamos 0 para evitar errores
    if (reporteData.value.length === 0) return 0;

    // 1. Sumamos todos los montos de arriendo (ya con descuento de comisión)
    const totalIngresos = reporteData.value.reduce((suma, fila) => {
        return suma + parseFloat(fila.desc_com || 0);
    }, 0);

    // 2. Obtenemos el Gasto Mensual.
    // Como el backend repite este número en todas las filas, tomamos
    // simplemente el de la primera fila (índice 0) para no sumarlo muchas veces.
    const gastoMensual = parseFloat(reporteData.value[0].total_gastos_mes || 0);

    // 3. Retornamos la resta final
    return totalIngresos - gastoMensual;
}

function mostrarMensaje(texto, tipo) {
    mensaje.value = texto;
    tipoMensaje.value = tipo;
    setTimeout(() => mensaje.value = '', 5000);
}

function formatFecha(fechaISO) {
    if (!fechaISO) return '-';
    const [year, month, day] = fechaISO.split('-');
    return `${day}/${month}/${year}`;
}

function formatDinero(valor) {
    const num = parseFloat(valor);
    if (isNaN(num)) return '$0';
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        maximumFractionDigits: 0
    }).format(num);
}
</script>

<style scoped>
.negrita { font-weight: 700; color: #555; }
.card-header { background-color: #f8f9fa; border-bottom: 2px solid #28a745; }
</style>