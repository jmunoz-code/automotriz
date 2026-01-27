<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref } from 'vue';

export default {
  name: 'Atributos',
  components: {
    Header,
    Footer,
  },
  setup() {
    const vendedores = ref([]);
    const selectedVendedor = ref(null);
    const mensaje = ref('');
    const tipoMensaje = ref(''); // 'success' or 'error'
    const isLoading = ref(false);

    const obtenerVendedores = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/`;
        const respuesta = await fetch(apiUrl);
        if (respuesta.ok) {
          const data = await respuesta.json();
          vendedores.value = data.data;
        } else {
            console.error('Error fetching vendors');
        }
      } catch (error) {
        console.error('Connection error', error);
      }
    };

    const hacerAdmin = async () => {
        if (!selectedVendedor.value) {
            mostrarMensaje("Seleccione un vendedor", "error");
            return;
        }
        
        isLoading.value = true;
        try {
             // La URL es /api/temp-admin/
             const apiUrl = `${import.meta.env.VITE_API_URL}temp-admin/`;
             
             const response = await fetch(apiUrl, {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({ id: selectedVendedor.value })
             });
             
             const data = await response.json();
             
             if (response.ok) {
                 mostrarMensaje(data.message || "Cambio exitoso", "success");
             } else {
                 mostrarMensaje(data.error || "Error desconocido", "error");
             }

        } catch (e) {
            mostrarMensaje("Error de conexión", "error");
        } finally {
            isLoading.value = false;
        }
    };

    const mostrarMensaje = (txt, type) => {
        mensaje.value = txt;
        tipoMensaje.value = type;
        setTimeout(() => { mensaje.value = ''; }, 3000);
    };

    onMounted(() => {
        obtenerVendedores();
    });

    return {
        vendedores, 
        selectedVendedor,
        hacerAdmin,
        mensaje,
        tipoMensaje,
        isLoading
    };
  }
};
</script>

<template>
  <Header></Header>
  <div class="page-container">
      <h3>Cambio de Atributos Temporales</h3>
      
      <div class="form-group">
          <label>Seleccionar Vendedor:</label>
          <select v-model="selectedVendedor" class="form-control">
              <option :value="null">Seleccione...</option>
              <option v-for="v in vendedores" :key="v.id" :value="v.id">
                  {{ v.nombres }} {{ v.apellidos }} ({{ v.nivel || 'N/A' }})
              </option>
          </select>
      </div>
      
      <div class="actions">
          <button @click="hacerAdmin" class="btn btn-primary" :disabled="isLoading || !selectedVendedor">
              {{ isLoading ? 'Procesando...' : 'Hacer ADMIN por 5 Minutos' }}
          </button>
      </div>
      
      <div v-if="mensaje" :class="['message', tipoMensaje]">
          {{ mensaje }}
      </div>
      
      <div style="margin-top:20px; font-size: 0.9em; color: #666;">
        <p>Esta acción otorgará privilegios de administrador al usuario seleccionado durante 5 minutos.</p>
        <p>Después de este tiempo, el sistema intentará revertir los permisos automáticamente.</p>
      </div>
  </div>
  <Footer></Footer>
</template>

<style scoped>
.page-container {
  padding: 20px;
  max-width: 600px;
  margin: 20px auto;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
h3 {
    text-align: center;
    color: #333;
}
.form-group {
    margin-bottom: 20px;
}
.form-control {
    width: 100%;
    padding: 10px;
    margin-top: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
}
.actions {
    text-align: center;
}
.btn {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    width: 100%;
}
.btn:disabled {
    background-color: #ccc;
}
.message {
    margin-top: 20px;
    padding: 10px;
    border-radius: 4px;
    text-align: center;
}
.success {
    background-color: #d4edda;
    color: #155724;
}
.error {
    background-color: #f8d7da;
    color: #721c24;
}
</style>
