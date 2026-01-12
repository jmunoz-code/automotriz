<script>
import Header from '@/components/HeaderAdmin.vue';
import Footer from '@/components/Footer.vue';
import { ref } from 'vue';

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
      patente: '',
      precio_compra: '',
      precio_venta: '',
      costo_asociado: '',
      interes: '',
    });

    const nivel = ref(localStorage.getItem('user_nivel'));

    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]); // Aquí almacenarás la lista de costos

    const registroAEliminarId = ref(null);
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
      if (!formData.value.patente) {
        mostrarMensaje('Por favor, ingrese Patente.', 'error');
        return;
      }
      if (!formData.value.precio_compra.trim()) {
        mostrarMensaje('Por favor, ingrese precio de compra.', 'error');
        return;
      }

      if (!formData.value.interes.trim()) {
        mostrarMensaje('Por favor, ingrese valor.', 'error');
        return;
      }

      if (!formData.value.margen.trim()) {
        mostrarMensaje('Por favor, ingrese valor.', 'error');
        return;
      }

      crearRegistro();
    };

    const obtenerValorizacionPorPatente = async (patente) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}costos/${patente}/`;
        console.log(apiUrl);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error al consultar   patente ${patente}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null;
          }
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        return data.data;
      } catch (error) {
        console.error('Error al consultar cliente por RUT:', error);
        return null;
      }
    };

    const limpiarFormulario = () => {
      formData.value.patente = '';
      formData.value.costo_asociado = '';
      formData.value.precio_compra = '';
      formData.value.precio_venta = '';
      formData.value.interes = '';
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarDatosPatente = async (patenteABuscar) => {
      console.log(patenteABuscar);
      try {
        const valorizacionData = await obtenerCostoPorPatente(patenteABuscar);
        if (costoData) {
          formData.value.patente = valorizacionData.patente;
          formData.value.costo_asociado = valorizacionData.costo_asociado;
          formData.value.precio_compra = valorizacionData.precio_compra;
          formData.value.precio_venta = valorizacionData.precio_venta;
          formData.value.interes = valorizacionData.interes;
        } else {
          console.warn('No se encontraron datos para la patente:', patenteABuscar);
          limpiarFormulario();
        }
      } catch (error) {
        console.error('Error al cargar datos para patente:', error);
      }
    };

    const crearRegistro = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}valorizacion/`;
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
          mostrarMensaje('Valorizacion creada exitosamente!', 'success');
          formData.value = { patente: '', costo_asociado: '', precio_compra: '', precio_venta: '', interes: '' };
          cargarListaDeCostos(); // Recargar la lista después de crear
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear Valorización: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al crear Valorización:', errorData);
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
        const apiUrl = `${import.meta.env.VITE_API_URL}costos/${registroAEliminarId.value}/`;
        console.log('URL de eliminación:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          mostrarMensaje('Costo Eliminado exitosamente!', 'success');
          cargarListaDeCostos(); // Recargar la lista después de eliminar
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al eliminar Costo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al eliminar Costo:', errorData);
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

    const cargarListaDeCostos = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}costos/`; // Endpoint para obtener la lista completa
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          datos.value = data.data; // Asume que tu API devuelve la lista en data.data
        } else {
          console.error('Error al cargar la lista de costos:', response.statusText);
          mostrarMensaje('Error al cargar la lista de costos.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al cargar la lista de costos:', error);
        mostrarMensaje('Error de conexión al cargar la lista de costos.', 'error');
      }
    };

    // Cargar la lista de costos al montar el componente
    cargarListaDeCostos();

    return {
      formData,
      handleSubmit,
      obtenerCostoPorPatente,
      cargarDatosPatente,
      crearRegistro,
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
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Valor Vehículo
      </div>
      <div class="card-body mt-3">

        <form @submit.prevent="handleSubmit">
          <div class="mb-3 row align-items-center">
            <label for="patente" class="col-md-2 col-form-label negrita">Patente</label>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm negrita" id="patente" v-model="formData.patente"
                required />
            </div>
            <div class="col-md-auto ms-4">
              <button type="button" class="btn btn-secondary btn-sm" @click="cargarDatosTipo_Pago(formData.id)">
                Buscar
              </button>
            </div>

          </div>

          <div class="mb-3">
            <label for="precio_compra" class="form-label negrita">Precio Compra</label>
            <input type="number" class="form-control form-control-sm" id="precio_compra"
              v-model="formData.precio_compra" required />
          </div>

          <div class="mb-3 negrita">
            <div>
              <label for="costo_asociado" class="form-label negrita">Gastos Asociados</label>
            </div>
            <input type="number" class="form-control form-control-sm" id="costo_asociado"
              v-model="formData.costo_asociado">
          </div>

          <div class="mb-3 negrita">
            <div>
              <label for="interes" class="form-label negrita">Interés Cuota</label>
            </div>
            <input type="number" class="form-control form-control-sm" id="interes" v-model="formData.interes">
          </div>

          <div class="mb-3 negrita">
            <div>
              <label for="precio_venta" class="form-label negrita">Precio de Venta</label>
            </div>
            <input type="number" class="form-control form-control-sm" id="precio_venta" v-model="formData.precio_venta">
          </div>

          <div class="d-flex justify-content-center">
            <div class="col-md-auto ms-2">
              <button type="submit" class="btn btn-sm btn-secondary">Crear</button>
            </div>

            <div class="col-md-auto ms-2">
              <button type="button" class="btn btn-sm btn-secondary" @click="limpiarFormulario">
                Limpiar
              </button>
            </div>
          </div>
        </form>

        <div v-if="mensaje" class="mt-3 alert"
          :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error' }">
          {{ mensaje }}
        </div>

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista Precios</h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patente</th>
              <th>Precio Compra</th>
              <th>Margen Venta</th>
              <th>Costos Asociados </th>
              <th>Interes Cuota</th>
              <th>Valor Total</th>
            </tr>

          </thead>
          <tbody>
            <tr v-for="costo in datos" :key="costo.id">
              <td>{{ costo.id }}</td>
              <td>{{ costo.patente }}</td>
              <td>{{ formatearMilesConPunto(costo.precio_compra) }}</td>
              <td>{{ formatearMilesConPunto(costo.costo_asociado) }}</td>
              <td>{{ formatearMilesConPunto(costo.precio_venta) }}</td>
              <td>{{ costo.interes }}</td>
              <td>{{ costo.valor_total }}</td>
              <td>
                <button v-if="nivel === 'ADMIN'" @click="abrirModalEliminar(costo.id)"
                  class="btn btn-danger btn-sm">Eliminar</button>
              </td>
            </tr>
            <tr v-if="datos.length === 0">
              <td colspan="6">No hay Valores registrados.</td>
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
            ¿Estás seguro de que deseas eliminar el costo con ID: {{ registroAEliminarId }}?
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