<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';
import { ref, computed, onMounted } from 'vue';

export default {
    components: {
        Header,
        Footer,
    },
    setup() {
        // --- Estado del Formulario ---
        const formData = ref({
            id: null,
            fecha_inicio: '',
            fecha_fin: '',
            tipo_arriendo: '', // Se iniciará vacío
            valor_arriendo: 0,
            nombre_arrendatario: '',
            rut_arrendatario: '',
        });

        // --- Estado General ---
        const mensaje = ref('');
        const tipoMensaje = ref('');
        const datos = ref([]);
        const rutValido = ref(true);
        const registroAEliminarId = ref(null);
        const mostrarModalEliminar = ref(false);

        // --- URLs de API ---
        const API_URL_RESERVAS = `${import.meta.env.VITE_API_URL}reservas/`;
        // URL para cargar los tipos de arriendo
        const API_URL_TIPOS = `${import.meta.env.VITE_API_URL}tipos-arriendo/`; 

        // --- Estado para los tipos de arriendo ---
        const tiposArriendo = ref([]); // Aquí se guardarán los tipos desde la API

        // --- Propiedad Computada para Calcular Días ---
        const cantidadDias = computed(() => {
            const { fecha_inicio, fecha_fin } = formData.value;
            if (!fecha_inicio || !fecha_fin) return 0;

            try {
                // Usamos UTC para evitar problemas de zona horaria al calcular la diferencia
                const d1 = new Date(fecha_inicio);
                const d2 = new Date(fecha_fin);
                const d1_utc = Date.UTC(d1.getFullYear(), d1.getMonth(), d1.getDate());
                const d2_utc = Date.UTC(d2.getFullYear(), d2.getMonth(), d2.getDate());

                if (d2_utc < d1_utc) return 0;

                const ms_por_dia = 1000 * 60 * 60 * 24;
                const diff_ms = d2_utc - d1_utc;
                // Sumamos 1 para incluir el día de inicio
                const diff_dias = Math.round(diff_ms / ms_por_dia);
                return diff_dias + 1; 
            } catch (error) {
                console.error("Error al calcular fechas:", error);
                return 0;
            }
        });

        // --- Lógica de Validación ---
        const validarRut = (rut) => {
            if (!rut || typeof rut !== 'string') return false;
            const rutLimpio = rut.replace(/\./g, '').replace('-', '').toUpperCase();
            if (rutLimpio.length < 2) return false;
            const cuerpo = rutLimpio.slice(0, -1);
            const dv = rutLimpio.slice(-1);
            if (!/^[0-9]+$/.test(cuerpo)) return false;
            let suma = 0;
            let factor = 2;
            for (let i = cuerpo.length - 1; i >= 0; i--) {
                suma += parseInt(cuerpo[i]) * factor;
                factor = factor === 7 ? 2 : factor + 1;
            }
            const dvCalculado = 11 - (suma % 11);
            const dvEsperado = dvCalculado === 10 ? 'K' : dvCalculado === 11 ? '0' : String(dvCalculado);
            return dv === dvEsperado;
        };

        const handleRutInput = () => {
            rutValido.value = validarRut(formData.value.rut_arrendatario);
            if (!rutValido.value && formData.value.rut_arrendatario) {
                mostrarMensaje('El RUT del arrendatario no es válido.', 'error');
            } else if (rutValido.value && formData.value.rut_arrendatario) {
                limpiarMensaje();
            }
        };

        // --- Lógica CRUD ---

        // Función para cargar los TIPOS de arriendo desde la API
        const cargarTiposArriendo = async () => {
            try {
                const response = await fetch(API_URL_TIPOS); 
                if (response.ok) {
                    const data = await response.json();
                    // Asumimos que la API de tipos devuelve un array de objetos
                    // (como el que vimos en la foto: [{id: 8, nombre: 'otro privado', ...}])
                    tiposArriendo.value = data.data || data; 
                } else {
                    mostrarMensaje('Error al cargar los tipos de arriendo.', 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión al cargar tipos de arriendo.', 'error');
            }
        };

        // Función para cargar las RESERVAS
        const cargarListaDeReservas = async () => {
            try {
                const response = await fetch(API_URL_RESERVAS);
                if (response.ok) {
                    const data = await response.json();
                    // Usamos data.data porque tu ViewSet de Reservas lo devuelve así
                    datos.value = data.data; 
                } else {
                    mostrarMensaje('Error al cargar la lista de reservas.', 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión al cargar las reservas.', 'error');
            }
        };

        const cargarReservaParaEditar = (reserva) => {
            formData.value = {
                id: reserva.id,
                // Formateamos la fecha para el input type="date"
                fecha_inicio: reserva.fecha_inicio.split('T')[0],
                fecha_fin: reserva.fecha_fin.split('T')[0],
                // Usamos el ID (tipo_arriendo) para el v-model del select
                tipo_arriendo: reserva.tipo_arriendo, 
                valor_arriendo: reserva.valor_arriendo,
                nombre_arrendatario: reserva.nombre_arrendatario,
                rut_arrendatario: reserva.rut_arrendatario,
            };
            window.scrollTo({ top: 0, behavior: 'smooth' });
        };

        const guardarReserva = async () => {
            if (!validarRut(formData.value.rut_arrendatario)) {
                mostrarMensaje('Por favor, ingrese un RUT de arrendatario válido.', 'error');
                return;
            }
            // Validación para el select
            if (!formData.value.tipo_arriendo) {
                mostrarMensaje('Por favor, seleccione un tipo de arriendo.', 'error');
                return;
            }
            if (!formData.value.fecha_inicio || !formData.value.fecha_fin || !formData.value.nombre_arrendatario) {
                mostrarMensaje('Por favor, complete todos los campos obligatorios.', 'error');
                return;
            }
            if (cantidadDias.value <= 0) {
                mostrarMensaje('La fecha de fin debe ser igual o posterior a la fecha de inicio.', 'error');
                return;
            }

            if (formData.value.id) {
                await modificarReserva();
            } else {
                await crearReserva();
            }
        };

        const crearReserva = async () => {
            try {
                // El formData.value ya contiene el ID del tipo_arriendo
                const response = await fetch(API_URL_RESERVAS, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData.value),
                });
                if (response.ok) {
                    mostrarMensaje('Reserva creada exitosamente!', 'success');
                    limpiarFormulario();
                    await cargarListaDeReservas();
                } else {
                    const errorData = await response.json();
                    let errorMsg = errorData.message || response.statusText;
                    if (errorData.tipo_arriendo) {
                        errorMsg = `Tipo de Arriendo no válido: ${errorData.tipo_arriendo[0]}`;
                    }
                    mostrarMensaje(`Error al crear reserva: ${errorMsg}`, 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión con el servidor.', 'error');
            } finally {
                setTimeout(limpiarMensaje, 3000);
            }
        };

        const modificarReserva = async () => {
            try {
                const url = `${API_URL_RESERVAS}${formData.value.id}/`;
                const response = await fetch(url, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData.value),
                });
                if (response.ok) {
                    mostrarMensaje('Reserva modificada exitosamente!', 'success');
                    limpiarFormulario();
                    await cargarListaDeReservas();
                } else {
                    const errorData = await response.json();
                    mostrarMensaje(`Error al modificar reserva: ${errorData.message || response.statusText}`, 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión con el servidor.', 'error');
            } finally {
                setTimeout(limpiarMensaje, 3000);
            }
        };

        const eliminarReservaConfirmado = async () => {
            if (!registroAEliminarId.value) return;
            try {
                const url = `${API_URL_RESERVAS}${registroAEliminarId.value}/`;
                const response = await fetch(url, { method: 'DELETE' });
                if (response.ok) {
                    mostrarMensaje('Reserva eliminada exitosamente!', 'success');
                    limpiarFormulario();
                    await cargarListaDeReservas();
                } else {
                    const errorData = await response.json();
                    mostrarMensaje(`Error al eliminar reserva: ${errorData.message || response.statusText}`, 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión con el servidor.', 'error');
            } finally {
                cerrarModalEliminar();
                setTimeout(limpiarMensaje, 3000);
            }
        };

        // --- Funciones Auxiliares ---
        const limpiarFormulario = () => {
            formData.value = {
                id: null,
                fecha_inicio: '',
                fecha_fin: '',
                tipo_arriendo: '', // Limpiar a ''
                valor_arriendo: 0,
                nombre_arrendatario: '',
                rut_arrendatario: '',
            };
            rutValido.value = true;
            limpiarMensaje();
        };

        const formatCurrency = (value) => {
            return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(value);
        };

        const abrirModalEliminar = (id) => {
            registroAEliminarId.value = id;
            mostrarModalEliminar.value = true;
        };

        const cerrarModalEliminar = () => {
            registroAEliminarId.value = null;
            mostrarModalEliminar.value = false;
        };

        const mostrarMensaje = (texto, tipo) => {
            mensaje.value = texto;
            tipoMensaje.value = tipo;
        };

        const limpiarMensaje = () => {
            mensaje.value = '';
            tipoMensaje.value = '';
        };

        // --- Carga Inicial ---
        onMounted(() => {
            cargarListaDeReservas();
            cargarTiposArriendo(); // Cargar los tipos al iniciar
        });

        // --- Exponer todo ---
        return {
            formData,
            datos,
            mensaje,
            tipoMensaje,
            rutValido,
            mostrarModalEliminar,
            registroAEliminarId,
            cantidadDias,
            tiposArriendo, // Exponer la lista de tipos

            handleRutInput,
            guardarReserva,
            eliminarReservaConfirmado,
            limpiarFormulario,
            cargarReservaParaEditar,

            abrirModalEliminar,
            cerrarModalEliminar,
            formatCurrency,
        };
    },
};
</script>

<template>
    <Header></Header>

    <div class="container mt-3">
        <div class="card shadow-sm mt-3 mb-3">
            <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Gestión de Reservas
            </div>
            <div class="card-body mt-3">
                <br />
                <br />
                <form @submit.prevent="guardarReserva">
                    <div class="card">
                        <div class="card-header">
                            <div class="card-title"
                                style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                                {{ formData.id ? 'Modificando Reserva ID: ' + formData.id : 'Ingresar Nueva Reserva' }}
                            </div>
                        </div>
                        <div class="card-body left">

                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="rut_arrendatario" class="form-label negrita">RUT Arrendatario</label>
                                    <input type="text" class="form-control form-control-sm" id="rut_arrendatario"
                                        v-model="formData.rut_arrendatario" required @input="handleRutInput"
                                        :class="{ 'is-invalid': !rutValido && formData.rut_arrendatario }" />
                                    <div v-if="!rutValido && formData.rut_arrendatario" class="invalid-feedback">
                                        Por favor, ingrese un RUT válido.
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label for="nombre_arrendatario" class="form-label negrita">Nombre
                                        Arrendatario</label>
                                    <input type="text" class="form-control form-control-sm" id="nombre_arrendatario"
                                        v-model="formData.nombre_arrendatario" required />
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="fecha_inicio" class="form-label negrita">Fecha Inicio</label>
                                    <input type="date" class="form-control form-control-sm" id="fecha_inicio"
                                        v-model="formData.fecha_inicio" required />
                                </div>
                                <div class="col-md-6">
                                    <label for="fecha_fin" class="form-label negrita">Fecha Fin</label>
                                    <input type="date" class="form-control form-control-sm" id="fecha_fin"
                                        v-model="formData.fecha_fin" required />
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="cantidad_dias" class="form-label negrita">Cantidad de Días</label>
                                    <input type="number" class="form-control form-control-sm" id="cantidad_dias"
                                        :value="cantidadDias" readonly disabled style="background-color: #eee;" />
                                </div>
                            </div>


                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="tipo_arriendo" class="form-label negrita">Tipo de Arriendo</label>
                                    &nbsp;
                                    <select class="form-select" id="tipo_arriendo" v-model="formData.tipo_arriendo"
                                        required>
                                        <!-- Esta opción es importante para forzar al usuario a elegir -->
                                        <option value="" disabled>Seleccione un tipo...</option>
                                        
                                        <!-- 
                                          El v-model (formData.tipo_arriendo) guardará el 'tipo.id'
                                          porque :value="tipo.id" se lo indica.
                                        -->
                                        <option v-for="tipo in tiposArriendo" :key="tipo.id" 
                                                :value="tipo.id">
                                            {{ tipo.nombre }}
                                        </option>
                                    </select>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="valor_arriendo" class="form-label negrita">Valor Arriendo (CLP)</label>
                                    <input type="number" class="form-control form-control-sm" id="valor_arriendo"
                                        v-model.number="formData.valor_arriendo" required />
                                </div>
                            </div>

                            <br>
                            <br>
                            <div class="d-flex justify-content-center">
                                <div class="col-md-auto ms-2">
                                    <button type="submit" class="btn btn-sm btn-success">
                                        {{ formData.id ? 'Modificar' : 'Grabar' }}
                                    </button>
                                </div>
                                <div class="col-md-auto ms-2">
                                    <button type="button" class="btn btn-sm btn-secondary" @click="limpiarFormulario">
                                        Limpiar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>

                <div v-if="mensaje" class="mt-3 alert"
                    :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error' }">
                    {{ mensaje }}
                </div>

                <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                    Lista de Reservas
                </h3>
                <div class="table-responsive">
                    <table class="table table-striped table-sm">
                        <thead>
                            <tr>
                                <th>Fechas</th>
                                <th>Tipo</th> <!-- Esta es la columna del problema -->
                                <th>Valor</th>
                                <th>Arrendatario</th>
                                <th>RUT</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="reserva in datos" :key="reserva.id">
                                <td>{{ reserva.fecha_inicio }} al {{ reserva.fecha_fin }}</td>
                                <!-- 
                                  vvv ¡AQUÍ ESTÁ LA CORRECCIÓN! vvv
                                  Cambiamos 'reserva.tipo_arriendo' (que es el ID)
                                  por 'reserva.tipo_arriendo_nombre' (que es el texto)
                                -->
                                <td>{{ reserva.tipo_arriendo_nombre }}</td> 
                                <td>{{ formatCurrency(reserva.valor_arriendo) }}</td>
                                <td>{{ reserva.nombre_arrendatario }}</td>
                                <td>{{ reserva.rut_arrendatario }}</td>
                                <td class="me-3">
                                    <button @click="cargarReservaParaEditar(reserva)"
                                        class="btn btn-warning btn-sm me-3">Modificar</button>
                                    &nbsp;
                                    <button @click="abrirModalEliminar(reserva.id)"
                                        class="btn btn-danger btn-sm">Eliminar</button>

                                </td>
                            </tr>
                            <tr v-if="datos.length === 0">
                                <td colspan="6">No hay reservas registradas.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Eliminación -->
    <div v-if="mostrarModalEliminar" class="modal fade show d-block" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirmar Eliminación</h5>
                    <button type="button" class="btn-close" @click="cerrarModalEliminar"></button>
                </div>
                <div class="modal-body">
                    ¿Estás seguro de que deseas eliminar esta reserva (ID: {{ registroAEliminarId }})?
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="cerrarModalEliminar">Cancelar</button>
                    <button type="button" class="btn btn-danger" @click="eliminarReservaConfirmado">Eliminar</button>
                </div>
            </div>
        </div>
    </div>
    <Footer></Footer>
</template>


<style scoped>
/* Tus estilos están bien */
.negrita {
    font-weight: bold;
    font-size: small;
}

.left {
    padding-left: 10px;
    padding-right: 10px;
}

.modal.show {
    background-color: rgba(0, 0, 0, 0.5);
}

.table-sm th,
.table-sm td {
    font-size: 0.85rem;
    padding: 0.4rem;
}

</style>