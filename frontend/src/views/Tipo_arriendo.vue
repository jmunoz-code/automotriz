<script>
import Header from '@/components/HeaderAdmin.vue'; // Asumo que usas el mismo header
import Footer from '@/components/Footer.vue';
import { ref, onMounted } from 'vue';

export default {
    components: {
        Header,
        // Footer, // Lo tenías comentado en el archivo que subiste
    },
    setup() {
        // --- Estado ---
        const listaTipos = ref([]);
        const nuevoTipoNombre = ref('');
        const nuevoTipoComision = ref(0.0); // <-- NUEVO ESTADO para la comisión
        const mensaje = ref('');
        const tipoMensaje = ref('');

        // Nivel del usuario
        const nivel = ref(localStorage.getItem('user_nivel'));

        // Define la URL de la nueva API (basado en tu config de Django)
        const API_URL_TIPOS = `${import.meta.env.VITE_API_URL}tipos-arriendo/`;

        // --- Funciones de Mensajes ---
        const mostrarMensaje = (texto, tipo) => {
            mensaje.value = texto;
            tipoMensaje.value = tipo;
            setTimeout(() => {
                mensaje.value = '';
                tipoMensaje.value = '';
            }, 3000);
        };

        // --- Cargar (Read) ---
        const cargarTiposArriendo = async () => {
            try {
                const response = await fetch(API_URL_TIPOS);
                if (!response.ok) {
                    throw new Error('Error al cargar los tipos de arriendo');
                }
                const data = await response.json();

                // El ViewSet de Django devuelve una lista de objetos directamente
                listaTipos.value = data;
            } catch (error) {
                mostrarMensaje(error.message || 'Error de conexión', 'error');
            }
        };

        // --- Crear (Create) ---
        const guardarNuevoTipo = async () => {
            if (!nuevoTipoNombre.value.trim()) {
                mostrarMensaje('El nombre no puede estar vacío.', 'error');
                return;
            }
            // <-- NUEVA VALIDACIÓN para la comisión -->
            if (nuevoTipoComision.value === null || nuevoTipoComision.value < 0 || nuevoTipoComision.value > 99.9) {
                mostrarMensaje('La comisión debe ser un número entre 0.0 y 99.9.', 'error');
                return;
            }

            try {
                // <-- NUEVO PAYLOAD (cuerpo de la petición) -->
                const payload = {
                    nombre: nuevoTipoNombre.value,
                    comision: nuevoTipoComision.value,
                };

                const response = await fetch(API_URL_TIPOS, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload), // <-- Se envía el payload con la comisión
                });

                if (response.status === 201) { // 201 Created
                    mostrarMensaje('Tipo de arriendo creado exitosamente!', 'success');
                    nuevoTipoNombre.value = ''; // Limpiar input
                    nuevoTipoComision.value = 0.0; // <-- LIMPIAR COMISIÓN
                    await cargarTiposArriendo(); // Recargar lista
                } else {
                    const errorData = await response.json();
                    // Manejo de error si el nombre ya existe (unique=True)
                    const errorMsg = errorData.nombre ? `Nombre: ${errorData.nombre[0]}` : 'Error al guardar';
                    mostrarMensaje(errorMsg, 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión con el servidor.', 'error');
            }
        };

        // --- Eliminar (Delete) ---
        const eliminarTipo = async (id) => {
            // Usamos un modal simple de confirmación del navegador
            if (!confirm(`¿Estás seguro de que deseas eliminar este tipo de arriendo (ID: ${id})?`)) {
                return;
            }

            try {
                const url = `${API_URL_TIPOS}${id}/`;
                const response = await fetch(url, { method: 'DELETE' });

                if (response.status === 204) { // 204 No Content (Éxito en DELETE)
                    mostrarMensaje('Tipo de arriendo eliminado exitosamente!', 'success');
                    await cargarTiposArriendo(); // Recargar lista
                } else {
                    mostrarMensaje('Error al eliminar el registro.', 'error');
                }
            } catch (error) {
                mostrarMensaje('Error de conexión con el servidor.', 'error');
            }
        };

        // --- Carga Inicial ---
        onMounted(() => {
            cargarTiposArriendo();
        });

        return {
            listaTipos,
            nuevoTipoNombre,
            nuevoTipoComision, // <-- EXPONER NUEVO ESTADO
            mensaje,
            tipoMensaje,
            guardarNuevoTipo,
            eliminarTipo,
            nivel,
        };
    },
};
</script>

<template>
    <Header></Header>

    <div class="container mt-3">
        <div class="card shadow-sm mt-3 mb-3">
            <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Gestión de Tipos de Arriendo
            </div>
            <div class="card-body mt-3">

                <!-- Formulario para agregar -->
                <div class="card mb-4">
                    <div class="card-header">
                        <div class="card-title"
                            style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                            Ingresar Nuevo Tipo de Arriendo
                        </div>
                    </div>
                    <div class="card-body">
                        <form @submit.prevent="guardarNuevoTipo">
                            <div class="row">
                                <!-- --- CAMBIO DE LAYOUT (col-md-8 a col-md-6) --- -->
                                <div class="col-md-6">
                                    <label for="nuevo_tipo" class="form-label negrita">Nombre del Tipo</label>
                                    <input type="text" class="form-control form-control-sm" id="nuevo_tipo"
                                        v-model="nuevoTipoNombre" required
                                        placeholder="Ej: Privado, Airbnb, Booking.com" />
                                </div>

                                <!-- --- NUEVO INPUT PARA COMISIÓN --- -->
                                <div class="col-md-3">
                                    <label for="nuevo_comision" class="form-label negrita">Comisión (%)</label>
                                    <input type="number" class="form-control form-control-sm" id="nuevo_comision"
                                        v-model.number="nuevoTipoComision" required step="0.1" min="0.0" max="99.9" />
                                </div>
                                <!-- --- FIN NUEVO INPUT --- -->

                                <!-- --- CAMBIO DE LAYOUT (col-md-4 a col-md-3) --- -->
                                <div class="col-md-3 d-flex align-items-end">
                                    <button type="submit" class="btn btn-sm btn-success w-100">
                                        Grabar Nuevo Tipo
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

                <!-- Lista de Tipos Existentes -->
                <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                    Tipos de Arriendo Existentes
                </h3>
                <div class="table-responsive">
                    <table class="table table-striped table-sm">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Comisión (%)</th> <!-- <-- NUEVA COLUMNA -->
                                <th class="text-end">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="tipo in listaTipos" :key="tipo.id">
                                <td>{{ tipo.id }}</td>
                                <td>{{ tipo.nombre }}</td>
                                <td>{{ tipo.comision }}%</td> <!-- <-- NUEVO DATO -->
                                <td class="text-end">
                                    <button @click="eliminarTipo(tipo.id)" class="btn btn-danger btn-sm"
                                        :disabled="nivel !== 'ADMIN'">
                                        Eliminar
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="listaTipos.length === 0">
                                <!-- --- CAMBIO COLSPAN (3 a 4) --- -->
                                <td colspan="4">No hay tipos de arriendo registrados.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
    </div>

</template>

<style scoped>
/* Estilos copiados de tu Ingreso_arriendo.vue para consistencia */
.negrita {
    font-weight: bold;
    font-size: small;
}

.table-sm th,
.table-sm td {
    font-size: 0.85rem;
    padding: 0.4rem;
}
</style>