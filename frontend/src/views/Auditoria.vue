<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed } from 'vue';

export default {
    name: 'Auditoria',
    components: {
        Header,
        Footer,
    },
    setup() {
        const registros = ref([]);
        const isLoading = ref(false);
        const mensaje = ref('');
        const tipoMensaje = ref('');
        const nivel = ref(localStorage.getItem('user_nivel'));

        // Filtros
        const filtros = ref({
            usuario: ''
        });

        // Paginación
        const paginaActual = ref(1);
        const registrosPorPagina = 20;

        const mostrarMensaje = (texto, tipo) => {
            mensaje.value = texto;
            tipoMensaje.value = tipo;
            setTimeout(() => {
                mensaje.value = '';
                tipoMensaje.value = '';
            }, 3000);
        };

        const cargarRegistros = async () => {
            if (nivel.value !== 'ADMIN') {
                mostrarMensaje('Acceso denegado. Solo administradores pueden ver esta página.', 'error');
                return;
            }

            isLoading.value = true;
            try {
                let url = `${import.meta.env.VITE_API_URL}auditoria/`;
                const params = new URLSearchParams();

                if (filtros.value.usuario) params.append('usuario', filtros.value.usuario);

                const response = await fetch(`${url}?${params.toString()}`);

                if (!response.ok) {
                    throw new Error('Error al cargar registros');
                }

                const data = await response.json();

                if (data.success) {
                    registros.value = data.data;
                } else {
                    throw new Error(data.message || 'Error desconocido');
                }

            } catch (error) {
                console.error('Error:', error);
                mostrarMensaje('Error al cargar registros de auditoría.', 'error');
            } finally {
                isLoading.value = false;
            }
        };

        const limpiarFiltros = () => {
            filtros.value = {
                usuario: ''
            };
            cargarRegistros();
        };

        // Computados para paginación
        const registrosPaginados = computed(() => {
            const inicio = (paginaActual.value - 1) * registrosPorPagina;
            const fin = inicio + registrosPorPagina;
            return registros.value.slice(inicio, fin);
        });

        const totalPaginas = computed(() => {
            return Math.ceil(registros.value.length / registrosPorPagina);
        });

        const cambiarPagina = (pagina) => {
            if (pagina >= 1 && pagina <= totalPaginas.value) {
                paginaActual.value = pagina;
            }
        };

        onMounted(() => {
            cargarRegistros();
        });

        return {
            registros,
            isLoading,
            mensaje,
            tipoMensaje,
            filtros,
            registrosPaginados,
            totalPaginas,
            paginaActual,
            cambiarPagina,
            cargarRegistros,
            limpiarFiltros
        };
    }
};
</script>

<template>
    <Header></Header>
    <div class="container-fluid mt-3 page-container">
        <div class="card shadow">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Auditoría del Sistema</h5>
                <button class="btn btn-sm btn-light" @click="cargarRegistros">
                    <i class="fas fa-sync-alt"></i> Actualizar
                </button>
            </div>

            <div class="card-body">
                <!-- Filtros -->
                <!-- Filtros -->
                <div class="row mb-4 bg-light p-3 rounded align-items-end">
                    <div class="col-md-4">
                        <label class="form-label">Usuario</label>
                        <input type="text" class="form-control form-control-sm" v-model="filtros.usuario"
                            placeholder="Filtrar por usuario" @keyup.enter="cargarRegistros">
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex gap-2">
                            <button class="btn btn-primary btn-sm w-100" @click="cargarRegistros">Buscar</button>
                            <button class="btn btn-secondary btn-sm w-100" @click="limpiarFiltros">Limpiar</button>
                        </div>
                    </div>
                </div>

                <!-- Alertas -->
                <div v-if="mensaje" :class="`alert alert-${tipoMensaje === 'error' ? 'danger' : 'success'}`">
                    {{ mensaje }}
                </div>

                <!-- Tabla -->
                <div class="table-responsive">
                    <table class="table table-striped table-hover table-bordered table-sm">
                        <thead class="table-dark">
                            <tr>
                                <th style="width: 50px;">ID</th>
                                <th style="width: 150px;">Fecha/Hora</th>
                                <th style="width: 120px;">Usuario</th>
                                <th style="width: 150px;">Página</th>
                                <th style="width: 100px;">Acción</th>
                                <th style="width: 120px;">Módulo/Tabla</th>
                                <th>Descripción</th>
                                <th>Valor Anterior</th>
                                <th>Valor Nuevo</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="isLoading">
                                <td colspan="9" class="text-center p-4">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Cargando...</span>
                                    </div>
                                </td>
                            </tr>
                            <tr v-if="!isLoading && registros.length === 0">
                                <td colspan="9" class="text-center p-4">No se encontraron registros de auditoría.</td>
                            </tr>
                            <tr v-for="log in registrosPaginados" :key="log.id">
                                <td class="text-center">{{ log.id }}</td>
                                <td>{{ log.fecha_hora_formateada }}</td>
                                <td class="fw-bold">{{ log.usuario }}</td>
                                <td>{{ log.pagina }}</td>
                                <td class="text-center">
                                    <span :class="{
                                        'badge bg-success': log.accion === 'CREAR',
                                        'badge bg-warning text-dark': log.accion === 'MODIFICAR',
                                        'badge bg-danger': log.accion === 'ELIMINAR'
                                    }">{{ log.accion }}</span>
                                </td>
                                <td>{{ log.modulo_tabla }}</td>
                                <td class="small">{{ log.descripcion }}</td>
                                <td class="small text-muted font-monospace">{{ log.valor_anterior || '-' }}</td>
                                <td class="small text-primary font-monospace">{{ log.valor_nuevo || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Paginación -->
                <nav v-if="totalPaginas > 1" aria-label="Navegación de páginas">
                    <ul class="pagination justify-content-center mt-3">
                        <li class="page-item" :class="{ disabled: paginaActual === 1 }">
                            <button class="page-link" @click="cambiarPagina(paginaActual - 1)">Anterior</button>
                        </li>
                        <li class="page-item disabled">
                            <span class="page-link">Página {{ paginaActual }} de {{ totalPaginas }}</span>
                        </li>
                        <li class="page-item" :class="{ disabled: paginaActual === totalPaginas }">
                            <button class="page-link" @click="cambiarPagina(paginaActual + 1)">Siguiente</button>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    </div>
    <Footer></Footer>
</template>

<style scoped>
.font-monospace {
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.85em;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.table td {
    vertical-align: middle;
}

.font-monospace:hover {
    white-space: normal;
    word-break: break-all;
    max-width: none;
    position: relative;
    z-index: 10;
    background-color: #fff;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}
</style>
