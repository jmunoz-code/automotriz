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
      // Tu método actual para formatear
      const formatter = new Intl.NumberFormat('de-DE');
      return formatter.format(valor);
    },
  },


  setup() {
    const formData = ref({
      patente: '',
      tipo_costo: '',
      descripcion: '',
      valor: '',
    });

    const nivel = ref(localStorage.getItem('user_nivel'));

    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]); // Aquí almacenarás la lista de costos

    const registroAEliminarId = ref(null);
    const mostrarModalEliminar = ref(false);

    const patenteABuscar = ref('');
    // Nuevo: para almacenar el total de gastos
    const totalGastosPatente = ref(0);

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
      if (!formData.value.tipo_costo.trim()) {
        mostrarMensaje('Por favor, ingrese Tipo Costo.', 'error');
        return;
      }
      if (!formData.value.descripcion.trim()) {
        mostrarMensaje('Por favor, ingrese Detalle.', 'error');
        return;
      }
      if (!formData.value.valor.trim()) {
        mostrarMensaje('Por favor, ingrese valor.', 'error');
        return;
      }

      crearRegistro();
    };

    const obtenerCostoPorPatente = async (patente) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}costos/${patente}/`;
        console.log(apiUrl);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error al consultar costo patente ${patente}: ${respuesta.status} - ${respuesta.statusText}`);
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
      formData.value.tipo_costo = '';
      formData.value.descripcion = '';
      formData.value.valor = '';
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarDatosPatente = async (patenteABuscar) => {
      console.log(patenteABuscar);
      try {
        const costoData = await obtenerCostoPorPatente(patenteABuscar);
        if (costoData) {
          formData.value.patente = costoData.patente;
          formData.value.tipo_costo = costoData.tipo_costo;
          formData.value.descripcion = costoData.descripcion;
          formData.value.valor = costoData.valor;
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
        const apiUrl = `${import.meta.env.VITE_API_URL}costos/`;
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
          mostrarMensaje('Costo creado exitosamente!', 'success');
          formData.value = { patente: '', tipo_costo: '', descripcion: '', valor: '' };
          cargarListaDeCostos(); // Recargar la lista después de crear
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear costo: ${errorData.message || response.statusText}`, 'error');
          console.error('Error al crear costo:', errorData);
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
        let apiUrl = `${import.meta.env.VITE_API_URL}costos/`;
        console.log("URL de carga de costos:", apiUrl);
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          datos.value = data.data;
          // Después de cargar todos los datos, restablecemos el total si no hay un filtro activo
          if (!patenteABuscar.value) {
            totalGastosPatente.value = 0;
          }
        } else {
          console.error('Error al cargar la lista de costos:', response.statusText);
          mostrarMensaje('Error al cargar la lista de costos.', 'error');
          datos.value = [];
        }
      } catch (error) {
        console.error('Error de conexión al cargar la lista de costos:', error);
        mostrarMensaje('Error de conexión al cargar la lista de costos.', 'error');
        datos.value = [];
      }
    };

    // Función para buscar costos por patente (modificada para calcular el total)
    const buscarCostos = async () => {
      try {
        let apiUrl = `${import.meta.env.VITE_API_URL}costos/filtro/${patenteABuscar.value}/`;
        console.log("URL de carga de costos:", apiUrl);
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          datos.value = data.data;
          // Calcular el total después de obtener los datos filtrados
          totalGastosPatente.value = calcularTotalGastos(datos.value);
        } else {
          console.error('Error al cargar la lista de costos:', response.statusText);
          mostrarMensaje('Error al cargar la lista de costos.', 'error');
          datos.value = [];
          totalGastosPatente.value = 0;
        }
      } catch (error) {
        console.error('Error de conexión al cargar la lista de costos:', error);
        mostrarMensaje('Error de conexión al cargar la lista de costos.', 'error');
        datos.value = [];
        totalGastosPatente.value = 0;
      }
    };

    // NUEVA FUNCIÓN: Calcula el total de gastos de una lista de costos
    const calcularTotalGastos = (listaDeCostos) => {
      // Usamos el método `reduce` para sumar el valor de todos los costos
      const total = listaDeCostos.reduce((acumulador, costo) => {
        // Aseguramos que el valor sea un número y lo sumamos
        return acumulador + parseFloat(costo.valor || 0);
      }, 0); // El valor inicial del acumulador es 0
      return total;
    };


    // Cargar la lista de costos al montar el componente
    cargarListaDeCostos();

    return {
      formData,
      handleSubmit,
      obtenerCostoPorPatente,
      cargarDatosPatente,
      cargarListaDeCostos,
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
      patenteABuscar,
      buscarCostos,
      totalGastosPatente, // Exportamos la nueva variable para que esté disponible en la plantilla
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
        Costos
      </div>
      <div class="card-body mt-3">

        <form @submit.prevent="handleSubmit">
          <div class="mb-3 row align-items-center">
            <label for="patente" class="col-md-2 col-form-label negrita">Patente</label>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm negrita" id="patente" v-model="formData.patente"
                required />
            </div>

          </div>
          <div class="mb-3">
            <label for="tipo_costo" class="form-label negrita">Nombre de Costo</label>
            <input type="text" class="form-control form-control-sm" id="tipo_costo" v-model="formData.tipo_costo"
              required />
          </div>

          <div class="mb-3 negrita">
            <div>
              <label for="descripcion" class="form-label negrita">Detalle Del Costo</label>
            </div>
            <textarea v-model="formData.descripcion" id="descripcion"
              style="width: 800px; box-sizing: border-box;"></textarea>
          </div>

          <div class="mb-3 negrita">
            <div>
              <label for="valor" class="form-label negrita">Valor $</label>
            </div>
            <input type="text" class="form-control form-control-sm" id="valor" v-model="formData.valor" required />
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

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista de Costos</h3>

        <div class="mb-3 row align-items-center">
          <label for="buscarPatente" class="col-md-2 col-form-label negrita">Patente:</label>
          <div class="col-md-3">
            <input type="text" class="form-control form-control-sm negrita" id="buscarPatente"
              v-model="patenteABuscar" />
          </div>
          <div class="col-md-auto ms-2">
            <button type="button" class="btn btn-sm btn-info" @click="buscarCostos">Filtrar x Patente</button>
          </div>

          <div class="col-md-auto ms-2">
            <button type="button" class="btn btn-sm btn-secondary" @click="cargarListaDeCostos('')">Mostrar Todos los
              Registros</button>
          </div>
        </div>

        <div v-if="patenteABuscar && totalGastosPatente > 0" class="alert alert-info mt-3 negrita">
          Total de gastos para la patente "{{ patenteABuscar }}": ${{ formatearMilesConPunto(totalGastosPatente) }}
        </div>

        <table class="table table-striped">
          <thead>
            <tr>

              <th>Patente</th>
              <th>Nombre de Costo</th>
              <th>Detalle de Costo</th>
              <th>Valor</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="costo in datos" :key="costo.id">

              <td>{{ costo.patente }}</td>
              <td>{{ costo.tipo_costo }}</td>
              <td>{{ costo.descripcion }}</td>
              <td class="negrita" style="text-align: right;">{{ formatearMilesConPunto(costo.valor) }}</td>
              <td>
                <button @click="abrirModalEliminar(costo.id)" class="btn btn-danger btn-sm"
                  :disabled="nivel !== 'ADMIN'">Eliminar</button>
              </td>
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