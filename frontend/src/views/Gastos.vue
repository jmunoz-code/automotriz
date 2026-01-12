<template>
    <!-- Asumo que usas tu HeaderAdmin -->
    <Header></Header>
    <div class="container mt-3">
        <div class="card shadow-sm mt-3 mb-3">
            <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Gestión de Gastos Mensuales
            </div>
            <div class="card-body mt-3">

                <!-- Formulario para agregar/modificar -->
                <div class="card mb-4">
                    <div class="card-header">
                        <div class="card-title"
                            style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                            {{ esEdicion ? 'Modificando Gasto' : 'Ingresar Nuevo Gasto' }}
                        </div>
                    </div>
                    <div class="card-body">
                        <form @submit.prevent="guardarGasto">
                            <div class="row">
                                <div class="col-md-4">
                                    <label for="fecha-gasto" class="form-label negrita">Mes y Año</label>
                                    <input type="month" class="form-control form-control-sm" id="fecha-gasto"
                                        v-model="formData.fecha" required />
                                </div>
                                <div class="col-md-5">
                                    <label for="descripcion-gasto" class="form-label negrita">Descripción</label>
                                    <input type="text" class="form-control form-control-sm" id="descripcion-gasto"
                                        v-model="formData.descripcion" placeholder="Ej: Luz, Agua, Gastos Comunes"
                                        required />
                                </div>
                                <div class="col-md-3">
                                    <label for="valor-gasto" class="form-label negrita">Valor (CLP)</label>
                                    <input type="number" class="form-control form-control-sm" id="valor-gasto"
                                        v-model.number="formData.valor" step="1" min="0" required />
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12 d-flex justify-content-end">
                                    <button v-if="esEdicion" type="button" class="btn btn-sm btn-secondary me-2"
                                        @click="limpiarFormulario">
                                        Cancelar Edición
                                    </button>
                                    <button type="submit" class="btn btn-sm btn-success">
                                        {{ esEdicion ? 'Actualizar Gasto' : 'Grabar Gasto' }}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Mensaje de Alerta -->
                <div v-if="mensaje" class="mt-3 alert"
                    :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error' }">
                    {{ mensaje }}
                </div>

                <!-- Lista de Gastos Existentes -->
                <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                    Historial de Gastos
                </h3>
                <div v-if="cargando" class="text-center my-3">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Cargando...
                </div>
                <div class="table-responsive" v-if="!cargando">
                    <table class="table table-striped table-sm">
                        <thead>
                            <tr>
                                <th>Mes y Año</th>
                                <th>Descripción</th>
                                <th class="text-end">Valor</th>
                                <th class="text-center">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="gasto in listaGastos" :key="gasto.id">
                                <td>{{ formatFecha(gasto.fecha) }}</td>
                                <td>{{ gasto.descripcion }}</td>
                                <td class="text-end">{{ formatValor(gasto.valor) }}</td>
                                <td class="text-center">
                                    <button v-if="nivel === 'ADMIN'" @click="iniciarEdicion(gasto)"
                                        class="btn btn-warning btn-sm me-2">
                                        Modificar
                                    </button>
                                    &nbsp;
                                    <button v-if="nivel === 'ADMIN'" @click="eliminarGasto(gasto.id)"
                                        class="btn btn-danger btn-sm">
                                        Eliminar
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="listaGastos.length === 0">
                                <td colspan="4" class="text-center">No hay gastos registrados.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Header from '@/components/HeaderAdmin.vue';
import { ref, onMounted } from 'vue';

// --- Estado del Componente ---
const listaGastos = ref([]);
const esEdicion = ref(false);
const cargando = ref(true);
const mensaje = ref('');
const tipoMensaje = ref('');
const formData = ref({
    id: null,
    fecha: '',
    descripcion: '',
    valor: 0
});

const nivel = ref(localStorage.getItem('user_nivel'));

const API_URL = `${import.meta.env.VITE_API_URL}gastos/`;

// --- Funciones de Mensajes ---
const mostrarMensaje = (texto, tipo, duracion = 3000) => {
    mensaje.value = texto;
    tipoMensaje.value = tipo;
    setTimeout(() => {
        mensaje.value = '';
        tipoMensaje.value = '';
    }, duracion);
};

// --- >>> INICIO DE CORRECCIÓN (API Pública) <<< ---

// NO necesitamos getCookie()

/**
 * Cargar (READ) - Obtiene la lista de gastos
 */
async function cargarGastos() {
    cargando.value = true;
    try {
        const response = await fetch(API_URL, {
            method: 'GET'
            // NO necesitamos 'credentials'
        });

        if (!response.ok) {
            // El error "No autenticado" ya no debería ocurrir
            throw new Error('Error al cargar los gastos.');
        }

        listaGastos.value = await response.json();

    } catch (error) {
        mostrarMensaje(error.message, 'error');
    } finally {
        cargando.value = false;
    }
}

/**
 * Guardar (CREATE / UPDATE) - Guarda o actualiza un gasto
 */
async function guardarGasto() {
    // NO necesitamos 'csrfToken'

    const payload = {
        ...formData.value,
        fecha: `${formData.value.fecha}-01`
    };

    let url = API_URL;
    let method = 'POST';
    if (esEdicion.value) {
        url = `${API_URL}${formData.value.id}/`;
        method = 'PUT';
    }

    try {
        const response = await fetch(url, {
            method: method,
            // NO necesitamos 'credentials'
            headers: {
                'Content-Type': 'application/json'
                // NO necesitamos 'X-CSRFToken'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            let errorMsg = errorData.detail || 'Error al guardar el gasto.';
            // (El resto del manejo de errores está bien)
            if (errorData.fecha) errorMsg = `Fecha: ${errorData.fecha[0]}`;
            if (errorData.descripcion) errorMsg = `Descripción: ${errorData.descripcion[0]}`;
            if (errorData.valor) errorMsg = `Valor: ${errorData.valor[0]}`;
            throw new Error(errorMsg);
        }

        mostrarMensaje(
            esEdicion.value ? 'Gasto actualizado!' : 'Gasto creado!',
            'success'
        );

        limpiarFormulario();
        await cargarGastos(); // Recargar la lista

    } catch (error) {
        mostrarMensaje(error.message, 'error');
    }
}

/**
 * Eliminar (DELETE) - Borra un gasto
 */
async function eliminarGasto(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este gasto?')) {
        return;
    }

    // NO necesitamos 'csrfToken'

    try {
        const response = await fetch(`${API_URL}${id}/`, {
            method: 'DELETE'
            // NO necesitamos 'credentials'
            // NO necesitamos 'headers'
        });

        if (response.status === 204) {
            mostrarMensaje('Gasto eliminado exitosamente.', 'success');
            await cargarGastos();
        } else {
            throw new Error('Error al eliminar el gasto.');
        }

    } catch (error) {
        mostrarMensaje(error.message, 'error');
    }
}

// --- >>> FIN DE CORRECCIÓN <<< ---


/**
 * Limpia el formulario y cancela el modo edición.
 */
function limpiarFormulario() {
    formData.value = {
        id: null,
        fecha: '',
        descripcion: '',
        valor: 0
    };
    esEdicion.value = false;
}

/**
 * Prepara el formulario para modificar un gasto
 */
function iniciarEdicion(gasto) {
    const fechaParaInput = gasto.fecha.substring(0, 7); // 'YYYY-MM'
    formData.value = {
        id: gasto.id,
        fecha: fechaParaInput,
        descripcion: gasto.descripcion,
        valor: parseFloat(gasto.valor)
    };
    esEdicion.value = true;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}


// --- Funciones de Formato (Sin cambios) ---
function formatFecha(fechaISO) {
    if (!fechaISO) return '';
    const [year, month, day] = fechaISO.split('-').map(Number);
    const date = new Date(Date.UTC(year, month - 1, day));
    return date.toLocaleString('es-CL', {
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC'
    });
}

function formatValor(valor) {
    const num = parseFloat(valor);
    if (isNaN(num)) return '0';
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        maximumFractionDigits: 0
    }).format(num);
}

// --- Carga Inicial ---
onMounted(() => {
    cargarGastos();
});

</script>

<style scoped>
/* Estilos (Sin cambios) */
.negrita {
    font-weight: bold;
    font-size: small;
}

.table-sm th,
.table-sm td {
    font-size: 0.85rem;
    padding: 0.4rem;
    vertical-align: middle;
}

.form-label {
    font-weight: 500;
}

.btn-sm {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
}

.btn-warning,
.btn-danger {
    color: white;
}
</style>