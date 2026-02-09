<script setup>
import { ref, onMounted } from 'vue';
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const users = ref([]);
const selectedUser = ref(null); // Changed to object for v-select
const message = ref('');
const messageType = ref('');

const fetchUsers = async () => {
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}vendedores/`);
        if (response.ok) {
            const data = await response.json();
            // Assuming data.data is the array as per Vendedores.vue
            users.value = data.data || [];
        } else {
            console.error('Failed to fetch users');
        }
    } catch (e) {
        console.error(e);
    }
};

const grantPrivilege = async () => {
    if (!selectedUser.value) {
        message.value = 'Por favor seleccione un usuario';
        messageType.value = 'error';
        return;
    }

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}vendedores/temp-admin/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: selectedUser.value.id }) // Access ID from object
        });

        if (response.ok) {
            const data = await response.json();
            message.value = `Privilegio otorgado correctamente. ${data.message || ''}`;
            messageType.value = 'success';
            fetchUsers();
        } else {
            const error = await response.json();
            message.value = `Error: ${error.error || 'No se pudo otorgar el privilegio'}`;
            messageType.value = 'error';
        }
    } catch (e) {
        message.value = 'Error de conexión';
        messageType.value = 'error';
    }

    setTimeout(() => {
        message.value = '';
        messageType.value = '';
    }, 5000);
};

onMounted(() => {
    fetchUsers();
});
</script>

<template>
    <Header></Header>
    <div class="container mt-5 mb-5">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="card shadow-lg border-0 rounded-lg">
                    <div class="card-header bg-gradient-success text-white text-center py-4">
                        <h4 class="mb-0 fw-bold"><i class="fa fa-user-shield me-2"></i>Acceso Temporal</h4>
                    </div>
                    <div class="card-body p-5">
                        <p class="text-muted text-center mb-4">
                            Seleccione un usuario para otorgarle privilegios de administrador por <strong>2
                                minutos</strong>.
                        </p>

                        <div class="mb-4">
                            <label class="form-label fw-bold text-secondary">Seleccionar Usuario</label>
                            <v-select v-model="selectedUser" :options="users" label="usuario"
                                placeholder="Buscar usuario..." class="style-chooser">
                                <template #option="{ nombres, apellidos, usuario, nivel }">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span>{{ nombres }} {{ apellidos }} ({{ usuario }})</span>
                                        <span class="badge bg-secondary rounded-pill">{{ nivel }}</span>
                                    </div>
                                </template>
                                <template #selected-option="{ nombres, apellidos, usuario }">
                                    {{ nombres }} {{ apellidos }} ({{ usuario }})
                                </template>
                            </v-select>
                        </div>

                        <div class="d-grid gap-2">
                            <button class="btn btn-success btn-lg shadow-sm" @click="grantPrivilege"
                                :disabled="!selectedUser">
                                <i class="fa fa-check-circle me-2"></i>Otorgar Privilegio
                            </button>
                        </div>

                        <div v-if="message" class="mt-4 alert d-flex align-items-center"
                            :class="messageType === 'success' ? 'alert-success' : 'alert-danger'" role="alert">
                            <i class="me-2 fa"
                                :class="messageType === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'"></i>
                            <div>{{ message }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <Footer></Footer>
</template>

<style scoped>
.bg-gradient-success {
    background: linear-gradient(45deg, #28a745, #218838);
}

.style-chooser .vs__search::placeholder,
.style-chooser .vs__dropdown-toggle,
.style-chooser .vs__dropdown-menu {
    border-radius: 8px;
    padding: 4px;
}

.card {
    border-radius: 15px;
    /* overflow: hidden;  <-- ELIMINADO: Esto cortaba el dropdown */
    border: none;
    /* Aseguramos que no tenga borde estándar si usamos shadow */
}
</style>
