<template>
  <div class="modal fade" :class="{ 'show': show }" style="display: block;" tabindex="-1" v-if="show"
    @click.self="closeModal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Detalle Abonos Cuotas Cliente</h5>
          <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div v-if="cuota && cuota.id">
            <p style="font-size: medium;"><strong>RUT Cliente:</strong> {{ cuota.rut_cliente }}</p>
            <p style="font-size: medium;"><strong>Patente:</strong> {{ cuota.patente }}</p>
            <p style="font-size: medium;"><strong>Número de Cuota:</strong> {{ cuota.numero_cuota }}</p>
            <hr>
            <h6 class="mb-3">Abonos Registrados para esta Cuota:</h6>
            <div v-if="isLoading" class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando abonos...</span>
              </div>
              <p>Cargando abonos...</p>
            </div>
            <div v-else-if="abonos.length > 0">
              <ul class="list-group">
                <li v-for="abono in abonos" :key="abono.id"
                  class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>ID Abono:</strong> {{ abono.id }} <br>
                    <strong>Fecha Abono:</strong> {{ formatearFechaHora(abono.fecha_abono) }} <br>
                    <strong>Monto:</strong> $ {{ formatearMilesConPunto(abono.monto_total) }}
                  </div>
                  <div class="botones-accion d-flex">
                    <button type="button" class="btn btn-primary btn-sm me-2" @click="imprimirModal(abono.id)"
                      title="Imprimir Comprobante">
                      <i class="bi bi-printer"></i> Imprimir
                    </button>
                    <button type="button" class="btn btn-danger btn-sm" @click="confirmDeleteAbono(abono.id)"
                      title="Eliminar Abono">
                      <i class="bi bi-trash"></i> Borrar
                    </button>
                  </div>
                </li>
              </ul>
              <!-- Fila de TOTAL -->
              <div class="mt-3 p-3 bg-light border rounded">
                <strong style="font-size: 1.1em;">TOTAL ABONADO: $ {{ formatearMilesConPunto(totalAbonos) }}</strong>
              </div>
            </div>
            <div v-else class="alert alert-info" role="alert">
              No se han encontrado abonos registrados para esta cuota.
            </div>
          </div>
          <div v-else class="alert alert-warning" role="alert">
            No se ha seleccionado ninguna cuota para mostrar detalles.
          </div>
        </div>
        <div class="modal-footer">

          <button type="button" class="btn btn-secondary" @click="closeModal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade" :class="{ 'show': show }" v-if="show"></div>
</template>

<script>
import { ref, watch, toRefs, computed } from 'vue';
import { useRouter } from 'vue-router'; // 👈 IMPORTACIÓN CLAVE
export default {
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    cuota: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ['close', 'abonoDeleted'], // Agregamos 'abonoDeleted' para notificar al padre
  setup(props, { emit }) {
    const { show, cuota } = toRefs(props);
    const router = useRouter(); // 👈 INICIALIZACIÓN CLAVE
    const abonos = ref([]);
    const isLoading = ref(false);

    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined) {
        return '0';
      }
      const num = parseFloat(valor);
      if (isNaN(num)) {
        return '0';
      }

      const formatter = new Intl.NumberFormat('de-DE');
      return formatter.format(num);
    };

    const formatearFechaHora = (fechaISO) => {
      if (!fechaISO) return '';
      // Intentar una conversión más robusta, asumiendo que el formato ISO es válido
      const date = new Date(fechaISO);
      // Si la fecha es inválida, se muestra la cadena vacía
      if (isNaN(date.getTime())) return fechaISO;

      const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
      return date.toLocaleDateString('es-ES', options);
    };

    // --- NUEVA FUNCIÓN PARA NAVEGAR A COMPROBANTE ---
    const imprimirModal = (abonoId) => {
      if (abonoId) {
        router.push({
          name: 'comprobante', // 👈 Nombre de la ruta configurada en el router/index.js
          params: {
            id: abonoId       // 👈 Pasa el ID del abono
          }
        });
        // NOTA: El modal no se cierra aquí, ya que el usuario podría querer volver.
        // La navegación simplemente oculta este modal al cambiar de ruta.
      } else {
        alert('ID de abono no válido para imprimir.');
      }
    };
    // ------------------------------------------------

    const fetchAbonos = async () => {
      isLoading.value = true;
      try {
        // NOTA: Ajusté la URL de fetch según el código proporcionado
        const url = `${import.meta.env.VITE_API_URL}detallepago/${cuota.value.rut_cliente}/${cuota.value.patente}/${cuota.value.numero_cuota}/`;
        console.log("DEBUG: Fetching abonos from:", url);

        const response = await fetch(url);

        if (response.ok) {
          const data = await response.json();
          // Asumo que 'data' contiene los abonos directamente, o en data.data
          abonos.value = data.data.map(abono => ({
            ...abono,
            // Asegura que el monto total esté presente para la vista
            monto_total: parseFloat(abono.monto_total || abono.monto_cuota || 0)
          })) || [];
          console.log("DEBUG: Abonos fetched:", abonos.value);
        } else {
          const errorData = await response.json().catch(() => ({ message: 'Error desconocido al obtener abonos.' }));
          console.error('Error al cargar abonos:', response.status, errorData.message);
          abonos.value = [];
        }
      } catch (error) {
        console.error('Error de conexión al cargar abonos:', error);
        abonos.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    const confirmDeleteAbono = async (abonoId) => {
      if (confirm('¿Estás seguro de que deseas eliminar este abono? Esta acción no se puede deshacer.')) {
        await deleteAbono(abonoId);
      }
    };

    const deleteAbono = async (abonoId) => {
      isLoading.value = true;
      try {
        let url = `${import.meta.env.VITE_API_URL}detallepago/${abonoId}/`;

        console.log("DEBUG: Deleting abono from:", url);

        const response = await fetch(url, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          console.log(`Abono con ID ${abonoId} eliminado exitosamente.`);
          await fetchAbonos();
          emit('abonoDeleted');
        } else {
          const errorData = await response.json().catch(() => ({ message: 'Error desconocido al eliminar abono.' }));
          console.error('Error al eliminar abono:', response.status, errorData.message);
          alert(`Error al eliminar abono: ${errorData.message || response.statusText}`);
        }
      } catch (error) {
        console.error('Error de conexión al eliminar abono:', error);
        alert('Error de conexión al eliminar abono.');
      } finally {
        isLoading.value = false;
      }
    };

    watch(show, (newVal) => {
      if (newVal) {
        fetchAbonos();
      } else {
        abonos.value = [];
      }
    }, { immediate: true });

    const closeModal = () => {
      emit('close');
    };

    // Computed property para calcular el total de todos los abonos
    const totalAbonos = computed(() => {
      return abonos.value.reduce((sum, abono) => {
        return sum + (parseFloat(abono.monto_total) || 0);
      }, 0);
    });

    return {
      show,
      cuota,
      abonos,
      isLoading,
      formatearMilesConPunto,
      formatearFechaHora,
      closeModal,
      confirmDeleteAbono,
      imprimirModal, // 👈 FUNCIÓN DISPONIBLE EN EL TEMPLATE
      totalAbonos,
    };
  },
};
</script>

<style scoped>
/* Estilos básicos para el modal de Bootstrap */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
}

.modal.show {
  display: block;
  z-index: 1050;
  overflow-x: hidden;
  overflow-y: auto;
}

.modal-dialog {
  margin: 1.75rem auto;
}

.list-group-item {
  border-left: 5px solid #007bff;
  margin-bottom: 8px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, .05);
}

.list-group-item:last-child {
  margin-bottom: 0;
}

/* Nuevo estilo para hacer las filas clicables más obvias */
.abono-item-clickable {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.abono-item-clickable:hover {
  background-color: #f8f9fa;
}

/* Estilo para espaciar los botones */
.botones-accion button {
  margin-left: 5px;
}
</style>