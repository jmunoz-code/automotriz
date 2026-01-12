<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref } from 'vue';

export default {
  components: {
    Header,
    Footer,
  },
  data() {
    return {
      numero: 1234567.89,
    };
  },
  methods: {
    formatearMilesConPunto(valor) {
      const formatter = new Intl.NumberFormat('de-DE'); // Usa el locale alemán
      return formatter.format(valor);
    },
  },


  setup() {
    const formData = ref({
      id: '',
      tipo_vehiculo: '',
      descripcion: '',
    });

    const nivel = ref(localStorage.getItem('user_nivel'));

    const mostrarModalEliminar = ref(false);

    const abrirModalEliminar = (id) => {
      registroAEliminarId.value = id;
      mostrarModalEliminar.value = true;
    };

    const cerrarModalEliminar = () => {
      registroAEliminarId.value = null;
      mostrarModalEliminar.value = false;
    };

    const handleSubmit = () => {


      if (!formData.value.descripcion.trim()) {
        mostrarMensaje('Por favor, ingrese Descripcion.', 'error');
        return;
      }

      console.log(formData.value);
      crearRegistro();

      cargarListaDeTipo();
    };

    const obtenerTipo = async (tipo) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}tipoVehiculo/${tipo}/`;
        console.log(apiUrl);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error al consultar tipo Vehiculo ${tipo}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null;
          }
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        return data.data;
      } catch (error) {
        console.error('Error al consultar tipo Vehiculo:', error);
        return null;
      }
    };

    const limpiarFormulario = () => {

      formData.value.id = '';
      formData.value.tipo_vehiculo = '';
      formData.value.descripcion = '';

      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarDatosTipo = async (idABuscar) => {

      try {
        const tipoData = await obtenerTipo(idABuscar);
        if (tipoData) {

          formData.value.id = tipoData.id;
          formData.value.tipo_vehiculo = tipoData.tipo_vehiculo;
          formData.value.descripcion = tipoData.descripcion;

        } else {
          console.warn('No se encontraron datos para Id Tipo Vehiculo  :', idABuscar);
          limpiarFormulario();
        }
      } catch (error) {
        console.error('Error al cargar datos para Id Tipo Vehiculo:', error);
      }
    };

    const crearRegistro = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}tipoVehiculo/`;
        console.log(apiUrl);
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData.value),
        });

        if (response.ok) {
          const data = await response.json();
          mostrarMensaje('Tipo Vehiculo creado exitosamente!', 'success');
          formData.value = { id: '', detalle: '' };
          cargarListaDeTipo(); // Recargar la lista después de crear
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear tipo Vehiculo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al crear tipo Vehiculo:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };


    const modificarRegistro = async (tipo) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}tipoVehiculo/${tipo}/`;
        console.log(apiUrl);
        const response = await fetch(apiUrl, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData.value),
        });

        if (response.ok) {
          const data = await response.json();
          mostrarMensaje('Tipo Vehiculo modificado exitosamente!', 'success');
          formData.value = { id: '', tipo_vehiculo: '', descripcion: '' };
          cargarListaDeTipo(); // Recargar la lista después de modificar
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al modificar Tipo Vehiculo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al modificar Tipo Vehiculo:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const eliminarRegistroConfirmado = async () => {
      if (!registroAEliminarId.value) {
        console.error('No se ha especificado el ID del registro a eliminar.');
        return;
      }

      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}tipoVehiculo/${registroAEliminarId.value}/`;
        console.log('URL de eliminación:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          mostrarMensaje('Tipo Vehiculo Eliminado exitosamente!', 'success');
          cargarListaDeTipo(); // Recargar la lista después de eliminar
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al eliminar Tipo Vehiculo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al eliminar Tipo Vehiculo:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        cerrarModalEliminar();
        setTimeout(limpiarMensaje, 3000);
      }
    };

    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;
    };

    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarListaDeTipo = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}tipoVehiculo/`; // Endpoint para obtener la lista completa
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          datos.value = data.data; // Asume que tu API devuelve la lista en data.data
        } else {
          console.error('Error al cargar la lista de Tipos de Vehiculo:', response.statusText);
          mostrarMensaje('Error al cargar la lista de Tipos de Vehiculo.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al cargar la Tipos de Vehiculo:', error);
        mostrarMensaje('Error de conexión al cargar laTipos de Vehiculo.', 'error');
      }
    };

    // Cargar la lista de costos al montar el componente
    cargarListaDeTipo();

    return {
      formData,
      handleSubmit,
      obtenerTipo,
      cargarDatosTipo,
      cargarListaDeTipo,
      crearRegistro,
      modificarRegistro,
      mensaje,
      tipoMensaje,
      datos,
      limpiarFormulario,
      registroAEliminarId,
      mostrarModalEliminar,
      abrirModalEliminar,
      cerrarModalEliminar,
      eliminarRegistroConfirmado,
      nivel,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container mt-3">
    <div class="card shadow-sm mt-3 mb-3">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Mantención
        Vehículos
      </div>
      <div class="card-body mt-3">

        <form @submit.prevent="handleSubmit">

          <div class="mb-3 row align-items-center">
            <label for="id" class="col-md-2 col-form-label negrita">Tipo Vehiculos</label>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm negrita" id="id" v-model="formData.id" />
            </div>
            <div class="col-md-auto ms-4">
              <button type="button" class="btn btn-secondary btn-sm" @click="cargarDatosTipo(formData.id)">
                Buscar
              </button>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);"> Gestión
                de Tipos de Vehículos</div>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label for="tipo_vehiculo" class="form-label negrita">Código Tipo Vehiculo</label>
                <input type="text" :size="5" class="form-control form-control-sm" id="tipo_vehiculo"
                  v-model="formData.tipo_vehiculo" required />
              </div>


              <div class="mb-3">
                <label for="descripcion" class="form-label negrita">Descripción</label>
                <input type="text" class="form-control form-control-sm" id="descripcion" v-model="formData.descripcion"
                  required />
              </div>
              <div class="d-flex justify-content-center">
                <div class="col-md-auto ms-2">
                  <button type="submit" class="btn btn-sm btn-secondary">Crear</button>
                </div>
                <div class="col-md-auto ms-2" v-if="nivel === 'ADMIN'">
                  <button type="button" class="btn btn-sm btn-secondary" @click="modificarRegistro(formData.id)">
                    Modificar
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

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista Tipo Vehículos
        </h3>
        <table class="table table-striped">
          <thead>
            <tr>

              <th>ID Vehículo</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tipo_vehiculo in datos" :key="tipo_vehiculo.id">

              <td>{{ tipo_vehiculo.tipo_vehiculo }}</td>
              <td>{{ tipo_vehiculo.descripcion }}</td>

              <td>
                <button v-if="nivel === 'ADMIN'" @click="abrirModalEliminar(tipo_vehiculo.id)"
                  class="btn btn-danger btn-sm">Eliminar</button>
              </td>
            </tr>
            <tr v-if="datos.length === 0">
              <td colspan="6">No hay tipos de Vehículos registrado.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="mostrarModalEliminar" class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirmar Eliminación</h5>
            <button type="button" class="btn-close" @click="cerrarModalEliminar" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ¿Estás seguro de que deseas eliminar el Tipo Combustible con ID: {{ registroAEliminarId }}?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="cerrarModalEliminar">Cancelar</button>
            <button type="button" class="btn btn-danger btn-sm" @click="eliminarRegistroConfirmado">Eliminar</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="mostrarModalEliminar" class="modal-backdrop fade show"></div>
  </div>
  <Footer></Footer>
</template>

<style scoped>
/* Puedes agregar estilos personalizados aquí si lo deseas */
.negrita {
  font-weight: bold;
  font-size: small;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-dialog {
  background-color: white;
  border-radius: 5px;
  padding: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: bold;
}

.modal-body {
  margin-bottom: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.modal-footer button {
  margin-left: 10px;
}
</style>