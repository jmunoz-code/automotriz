<script>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';

export default {
  props: {
    show: {
      type: Boolean,
      default: false
    },
    cuota: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close', 'abonoRegistrado', 'imprimirComprobante'], // <-- CAMBIO 1: Nuevo evento emitido
  setup(props, { emit }) {
    const cuotaSeleccionada = ref({});
    const montoAbono = ref(0);
    const interes = ref(3.5); // Nuevo campo para el interés
    const isSaving = ref(false);

    // Observa los cambios en la prop 'cuota' para actualizar los datos locales del modal
    watch(() => props.cuota, (newCuota) => {
      cuotaSeleccionada.value = { ...newCuota };
      montoAbono.value = newCuota.monto_cuota; // Puedes inicializar con el monto de la cuota o 0
    }, { immediate: true });

    const cerrarModal = () => {
      emit('close');
    };

    const guardarAbono = async () => {
      isSaving.value = true;
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}detallepago/`; // Ajusta esta URL a tu endpoint para detalle de pago
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            rut: cuotaSeleccionada.value.rut_cliente,
            patente: cuotaSeleccionada.value.patente,
            numero_cuota: cuotaSeleccionada.value.numero_cuota,
            monto_cuota: montoAbono.value, // Esto será el monto del abono
            interes: interes.value, // Envía el valor del interés
            // Puedes añadir otros campos si tu tabla de detalle de pago los requiere, como fecha_pago, etc.
          }),
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Abono registrado exitosamente:', data);
          emit('abonoRegistrado', 'Abono registrado exitosamente.', 'success');
          cerrarModal(); // Cerrar el modal después de guardar
        } else {
          const errorData = await response.json();
          console.error('Error al registrar abono:', errorData.message || response.statusText);
          emit('abonoRegistrado', errorData.message || 'Error al registrar el abono.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al registrar abono:', error);
        emit('abonoRegistrado', 'Error de conexión con el servidor al registrar abono.', 'error');
      } finally {
        isSaving.value = false;
      }
    };


    // Obtén la instancia del router
    const router = useRouter();

    // Dentro de setup(), antes de imprimirComprobante
    const obtenerNombreCliente = async (rut) => {
      try {
        // Construimos la URL usando el VITE_API_URL y la ruta 'clientes/<rut>/'
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/${rut}/`;
        const response = await fetch(apiUrl);

        if (response.ok) {
          const result = await response.json();
          const clienteData = result.data;

          if (clienteData && clienteData.nombres && clienteData.apellidos) {
            // Concatenamos el nombre y el apellido para enviarlo al comprobante
            return `${clienteData.nombres} ${clienteData.apellidos}`.trim();
          }
        }
        // Si no se encuentra o hay un error HTTP, devolvemos una cadena vacía
        return '';

      } catch (error) {
        console.error('Error al buscar cliente por RUT:', error);
        return ''; // Error de red o conexión
      }
    };

   // En ModalDetallePago.vue, dentro de setup()

    const imprimirComprobante = async () => { // <--- Convertida a ASYNC
      const rutCliente = cuotaSeleccionada.value.rut_cliente;

      // 1. Obtener el nombre completo del cliente
      const nombreCompleto = await obtenerNombreCliente(rutCliente);

      // Verificación (opcional):
      if (!nombreCompleto) {
        // Podrías usar un toast/notificación en lugar de alert
        alert('Error: No se pudo obtener el nombre del cliente. Verifique el RUT o la conexión.');
        return;
      }

      const datosParaComprobante = {
        rut: rutCliente,
        patente: cuotaSeleccionada.value.patente,
        numero_cuota: cuotaSeleccionada.value.numero_cuota,
        monto_pago: montoAbono.value,
        interes: interes.value,
        fecha: new Date().toISOString(),
        comprobanteNumero: cuotaSeleccionada.value.id,
        clienteNombre: nombreCompleto, // <--- ¡Dato Obtenido y Agregado!
      };

      router.push({
        name: 'Comprobante',
        query: datosParaComprobante
      });
    };
    return {
      cuotaSeleccionada,
      montoAbono,
      interes,
      isSaving,
      cerrarModal,
      guardarAbono,
      imprimirComprobante, // <-- CAMBIO 3: Retornar la nueva función
    };
  }
};
</script>

<template>
  <div class="modal fade" :class="{ 'show d-block': show }" tabindex="-1" role="dialog" @click.self="cerrarModal">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Registrar Abono/Pago de Cuota</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="cerrarModal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="guardarAbono">
            <div class="mb-3">
              <label for="rutCliente" class="form-label">RUT Cliente:</label>
              <input type="text" class="form-control" id="rutCliente" v-model="cuotaSeleccionada.rut_cliente" disabled>
            </div>
            <div class="mb-3">
              <label for="patente" class="form-label">Patente:</label>
              <input type="text" class="form-control" id="patente" v-model="cuotaSeleccionada.patente" disabled>
            </div>
            <div class="mb-3">
              <label for="numeroCuota" class="form-label">Número de Cuota:</label>
              <input type="text" class="form-control" id="numeroCuota" v-model="cuotaSeleccionada.numero_cuota"
                disabled>
            </div>
            <div class="mb-3">
              <label for="interes" class="form-label">Interés (%):</label>
              <input type="number" class="form-control" id="interes" v-model.number="interes" step="0.1" required>
            </div>
            <div class="mb-3">
              <label for="montoAbono" class="form-label">Monto Pago:</label>
              <input type="number" class="form-control" id="montoAbono" v-model.number="montoAbono" required>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="cerrarModal">Salir</button>
              <button type="submit" class="btn btn-primary" :disabled="isSaving">
                <span v-if="isSaving" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ isSaving ? 'Guardando...' : 'Grabar Abono/Pago' }}

              </button>
              <button type="button" class="btn btn-secondary" @click="imprimirComprobante">Imprimir</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>

<style scoped>
/* Estilos para el modal */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
  /* Fondo semitransparente */
}

.modal-dialog {
  max-width: 500px;
}

.modal-backdrop {
  z-index: 1040;
}

.modal.show.d-block {
  display: block;
}
</style>