<script setup>
import { ref, onMounted } from 'vue';
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';

// State
const vehiculos = ref([]);
const filters = ref({
  patente: '',
  marca: ''
});
const loading = ref(false);
const error = ref(null);

// Methods
const fetchVehiculos = async () => {
  loading.value = true;
  error.value = null;
  try {
    // Construct URL with query parameters
    let url = `${import.meta.env.VITE_API_URL}vehiculos/?`;
    
    const params = [];
    if (filters.value.patente) params.push(`patente=${encodeURIComponent(filters.value.patente)}`);
    if (filters.value.marca) params.push(`marca=${encodeURIComponent(filters.value.marca)}`);
    
    url += params.join('&');

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
        let errorMessage = 'Error en la solicitud';
        try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
        } catch (e) {
            errorMessage = response.statusText;
        }
        throw new Error(errorMessage);
    }

    const data = await response.json();
    vehiculos.value = data.data;

  } catch (err) {
    console.error('Error fetching vehiculos:', err);
    error.value = 'No se pudieron cargar los vehículos. ' + (err.message || '');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
    fetchVehiculos();
};

onMounted(() => {
  fetchVehiculos();
});
</script>

<template>
  <Header></Header>
  <div class="container-fluid mt-3" style="width: calc(100% - 30px); margin: 0 auto;">
    <div class="card shadow-sm mt-3">
        <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
          Documentación de Vehículos
        </div>
        <div class="card-body mt-3">
          
          <!-- Error Alert -->
          <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fa fa-exclamation-triangle me-2"></i> {{ error }}
            <button type="button" class="btn-close" @click="error = null" aria-label="Close"></button>
          </div>

          <!-- Search Form -->
          <div class="row mb-4">
            <div class="col-md-4">
              <label for="searchPatente" class="form-label negrita">Buscar por Patente</label>
              <input 
                type="text" 
                id="searchPatente" 
                class="form-control" 
                v-model="filters.patente"
                @keyup.enter="handleSearch"
                placeholder="Ej. ABCD12"
              >
            </div>
            <div class="col-md-4">
              <label for="searchMarca" class="form-label negrita">Buscar por Marca</label>
              <input 
                type="text" 
                id="searchMarca" 
                class="form-control" 
                v-model="filters.marca"
                @keyup.enter="handleSearch"
                placeholder="Ej. Toyota"
              >
            </div>
            <div class="col-md-4 d-flex align-items-end">
              <button class="btn btn-primary w-100" @click="handleSearch">
                <i class="fa fa-search me-2"></i> Buscar
              </button>
            </div>
          </div>

          <!-- Table -->
          <div class="table-responsive">
            <table class="table table-hover table-bordered align-middle text-center">
              <thead class="table-light">
                <tr>
                  <th>Patente</th>
                  <th>Marca</th>
                  <th>Modelo</th>
                  <th>Año</th>
                  <th>Kilómetros</th>
                  <th>Revisión Técnica</th>
                  <th>Permiso Circulación</th>
                  <th>Seguro Vigente</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="8" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Cargando...</span>
                    </div>
                  </td>
                </tr>
                <tr v-else-if="vehiculos.length === 0">
                    <td colspan="8" class="text-center py-4 text-muted">No se encontraron vehículos.</td>
                </tr>
                <tr v-for="vehiculo in vehiculos" :key="vehiculo.id">
                  <td class="fw-bold">{{ vehiculo.patente }}</td>
                  <td>{{ vehiculo.marca_descripcion }}</td> 
                  <td>{{ vehiculo.modelo }}</td>
                  <td>{{ vehiculo.agno }}</td>
                  <td>{{ vehiculo.kilometraje }}</td>
                  
                  <!-- Status Icons -->
                  <td>
                    <span v-if="vehiculo.revision_tecnica_al_dia === 1" class="badge bg-success rounded-pill"><i class="fa fa-check"></i> Al Día</span>
                    <span v-else class="badge bg-danger rounded-pill"><i class="fa fa-times"></i> Vencida</span>
                  </td>
                  <td>
                    <span v-if="vehiculo.permiso_circulacion === 1" class="badge bg-success rounded-pill"><i class="fa fa-check"></i> Vigente</span>
                    <span v-else class="badge bg-danger rounded-pill"><i class="fa fa-times"></i> Vencido</span>
                  </td>
                  <td>
                    <span v-if="vehiculo.seguro_vigente === 1" class="badge bg-success rounded-pill"><i class="fa fa-check"></i> Vigente</span>
                    <span v-else class="badge bg-danger rounded-pill"><i class="fa fa-times"></i> Vencido</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
        </div>
      </div>
  </div>
  <Footer></Footer>
</template>

<style scoped>
.negrita {
    font-weight: bold;
}
.table th {
    white-space: nowrap;
}
</style>
