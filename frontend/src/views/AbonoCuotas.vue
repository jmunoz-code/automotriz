<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed, watch } from 'vue';

export default {
  components: {
    Header,
    Footer,
  },
  setup() {
    const listaCuotas = ref([]); // Contendrá los registros de detallePagoCuotas
    const isLoading = ref(false);

    const nivel = ref(localStorage.getItem('user_nivel'));

    const mensaje = ref('');
    const tipoMensaje = ref('');

    const filtroRutCuota = ref('');
    const filtroPatenteCuota = ref('');

    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined) {
        return '';
      }
      const num = parseFloat(valor);
      if (isNaN(num)) {
        return '';
      }
      const formatter = new Intl.NumberFormat('de-DE');
      return formatter.format(num);
    };

    const formatearFecha = (fechaISO) => {
      if (!fechaISO) return '';
      // Para fecha_abono que es DateTimeField
      const date = new Date(fechaISO);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${day}-${month}-${year} ${hours}:${minutes}`;
    };

    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;
      setTimeout(limpiarMensaje, 3000);
    };

    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarListaDeCuotas = async () => {
      // Validar que ambos campos estén llenos antes de hacer la llamada a la API
      if (!filtroRutCuota.value || !filtroPatenteCuota.value) {
        mostrarMensaje('Debe ingresar tanto el RUT de Cliente como la Patente para buscar las cuotas.', 'error');
        listaCuotas.value = []; // Limpia la lista si no hay filtros completos
        return; // Detiene la ejecución si los campos están vacíos
      }

      isLoading.value = true; // Activa el estado de carga
      listaCuotas.value = []; // Limpiar la lista actual antes de cargar nuevos datos

      try {
        // Construir la URL utilizando los valores de los filtros directamente en la ruta.
        // Esto asume que tu endpoint de Django espera la URL en el formato:
        // VITE_API_URL/detallepago/{rut}/{patente}/
        const apiUrl = `${import.meta.env.VITE_API_URL}detallepago/${filtroRutCuota.value}/${filtroPatenteCuota.value}/`;

        console.log('DEBUG: Cargando cuotas desde:', apiUrl);

        // Realizar la petición Fetch a la API
        const response = await fetch(apiUrl);

        if (response.ok) {
          // Si la respuesta es exitosa (código 2xx)
          const data = await response.json();
          // Asumiendo que tu backend devuelve los datos de las cuotas dentro de una clave 'data'
          listaCuotas.value = data.data;
          console.log('DEBUG: Cuotas cargadas exitosamente:', listaCuotas.value);

          // Mostrar mensaje de éxito o de no encontrado si la lista está vacía
          if (listaCuotas.value.length === 0) {
            mostrarMensaje('No se encontraron cuotas para los criterios de búsqueda.', 'info');
          } else {
            mostrarMensaje('Cuotas actualizadas.', 'success');
          }
        } else {
          // Si la respuesta no es exitosa (códigos de error como 404, 500, etc.)
          const errorData = await response.json(); // Intentar parsear el cuerpo del error para obtener mensajes del backend
          console.error('Error cargando las cuotas:', response.status, response.statusText, errorData);

          // Si es un error 404 y el backend envió un mensaje específico
          if (response.status === 404 && errorData && errorData.message) {
            mostrarMensaje(errorData.message, 'info'); // Mostrar el mensaje de "No se encontraron detalles de pago" de tu Django
          } else {
            mostrarMensaje('Error cargando las cuotas. Por favor, intente de nuevo.', 'error');
          }
        }
      } catch (error) {
        // Capturar errores de red o cualquier otra excepción durante la petición
        console.error('Error de conexión cargando las cuotas:', error);
        mostrarMensaje('Error de conexión con el servidor. Verifique su conexión o intente más tarde.', 'error');
      } finally {
        isLoading.value = false; // Desactiva el estado de carga al finalizar, independientemente del resultado
      }
    };

    // --- NUEVAS FUNCIONES PARA ELIMINAR ABONO ---

    const confirmarEliminarAbono = (idAbono) => {
      if (confirm('¿Estás seguro de que quieres eliminar este abono? Esta acción es irreversible.')) {
        eliminarAbono(idAbono);
      }
    };

    const eliminarAbono = async (idAbono) => {
      isLoading.value = true;
      try {
        // Asumiendo que tu endpoint de eliminación es:
        // VITE_API_URL/detallepago/{id_abono}/
        const apiUrl = `${import.meta.env.VITE_API_URL}detallepago/${idAbono}/`;

        console.log('DEBUG: Eliminando abono desde:', apiUrl);

        const response = await fetch(apiUrl, {
          method: 'DELETE', // Especificamos el método DELETE
        });

        if (response.ok) {
          // Si la eliminación fue exitosa (ej. 204 No Content)
          mostrarMensaje('Abono eliminado exitosamente.', 'success');
          // Recargar la lista de cuotas para reflejar el cambio
          await cargarListaDeCuotas();
        } else {
          // Manejar errores en la eliminación
          const errorData = await response.json(); // Intentar obtener el mensaje de error del backend
          console.error('Error eliminando el abono:', response.status, response.statusText, errorData);
          mostrarMensaje(`Error al eliminar abono: ${errorData.detail || errorData.message || response.statusText}`, 'error');
        }
      } catch (error) {
        console.error('Error de conexión al eliminar el abono:', error);
        mostrarMensaje('Error de conexión con el servidor al intentar eliminar.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    // --- FIN NUEVAS FUNCIONES ---

    const cuotasFiltradas = computed(() => {
      return listaCuotas.value;
    });

    // Observador para recargar la lista cuando cambian los filtros
    watch([filtroRutCuota, filtroPatenteCuota], () => {
      // Si ambos están llenos, busca; de lo contrario, limpia la lista
      if (filtroRutCuota.value && filtroPatenteCuota.value) {
        cargarListaDeCuotas();
      } else {
        listaCuotas.value = [];
        limpiarMensaje();
      }
    });

    onMounted(() => {
      // La carga inicial se disparará con el watch si los campos se rellenan
    });

    return {
      listaCuotas,
      isLoading,
      mensaje,
      tipoMensaje,
      filtroRutCuota,
      filtroPatenteCuota,
      cuotasFiltradas,
      cargarListaDeCuotas,
      formatearMilesConPunto,
      formatearFecha,
      mostrarMensaje,
      confirmarEliminarAbono, // Exponer la nueva función
      nivel,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container-fluid mt-3">
    <div class="card shadow-sm">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
        Historial de Abonos Registrados
      </div>
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-4">
            <label for="filtroRutCuota" class="form-label negrita">RUT Cliente (Requerido):</label>
            <input type="text" class="form-control form-control-sm" id="filtroRutCuota" v-model.lazy="filtroRutCuota"
              placeholder="Ej: 12.345.678-9" />
          </div>
          <div class="col-md-4">
            <label for="filtroPatenteCuota" class="form-label negrita">Patente (Requerido):</label>
            <input type="text" class="form-control form-control-sm" id="filtroPatenteCuota"
              v-model.lazy="filtroPatenteCuota" placeholder="Ej: ABCD12" />
          </div>
          <div class="col-md-4 d-flex align-items-end justify-content-between">
            <button class="btn btn-primary btn-sm me-2" @click="cargarListaDeCuotas"
              :disabled="isLoading || !filtroRutCuota || !filtroPatenteCuota">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Buscando...' : 'Buscar Abonos' }}
            </button>
          </div>
        </div>

        <div v-if="mensaje" class="alert" :class="{
          'alert-success': tipoMensaje === 'success',
          'alert-danger': tipoMensaje === 'error',
          'alert-info': tipoMensaje === 'info',
        }" role="alert">
          {{ mensaje }}
        </div>

        <div class="table-responsive">
          <table class="table table-striped table-hover custom-table">
            <thead>
              <tr>
                <th style="text-align: center">RUT Cliente</th>
                <th style="text-align: center">Patente</th>
                <th style="text-align: center"># Cuota</th>
                <th style="text-align: center">Monto Abono</th>
                <th style="text-align: center">Fecha Abono</th>
                <th style="text-align: center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="cuotasFiltradas.length === 0 && !isLoading">
                <td colspan="6" class="text-center">No se encontraron abonos que coincidan con los criterios de
                  búsqueda.</td>
              </tr>
              <tr v-else-if="isLoading">
                <td colspan="6" class="text-center">Cargando abonos...</td>
              </tr>
              <tr v-for="abono in cuotasFiltradas" :key="abono.id" style="cursor: default;">
                <td style="text-align: center">{{ abono.rut }}</td>
                <td style="text-align: center">{{ abono.patente }}</td>
                <td style="text-align: center">{{ abono.numero_cuota }}</td>
                <td style="text-align: center">{{ formatearMilesConPunto(abono.monto_cuota) }}</td>
                <td style="text-align: center">{{ formatearFecha(abono.fecha_abono) }}</td>
                <td style="text-align: center">
                  <button v-if="nivel === 'ADMIN'" class="btn btn-danger btn-sm"
                    @click="confirmarEliminarAbono(abono.id)">
                    Eliminar
                  </button>
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
  font-weight: bolder;
}

.left {
  text-align: left;
}

.custom-table {
  min-width: 1000px;
  /* Ajusta este valor si tus columnas son más anchas */
}

/* Estilo para el spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
}

/* Cursor por defecto para filas que no son clicables */
tr {
  cursor: default;
}
</style>