<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref } from 'vue';

export default {
  name: 'CuotasImpagas',
  components: {
    Header,
    Footer,
  },
  setup() {
    // Referencias reactivas para los datos y el estado de la UI
    const listaCuotas = ref([]); // Lista original de la API
    const listaCuotasAgrupadas = ref([]); // Nueva lista para la tabla (Solo grupos con atraso)
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');

    // Nuevas referencias para el modal de detalles
    const mostrarModal = ref(false);
    const detallesCuotas = ref([]);
    const rutSeleccionado = ref('');
    const patenteSeleccionada = ref('');

    // --- Función: Actualizar Observación (Sin Cambios) ---
    const actualizarObservacion = async (cuotaId, nuevaObservacion) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/${cuotaId}/`;
        const response = await fetch(apiUrl, {
          method: 'PATCH', // Usamos PATCH para actualizar parcialmente el recurso
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ observacion: nuevaObservacion }),
        });

        if (response.ok) {
          mostrarMensaje('Observación actualizada exitosamente.', 'success');
        } else {
          const errorData = await response.json();
          console.error('Error al actualizar la observación:', errorData.message || response.statusText);
          mostrarMensaje('Error al actualizar la observación.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al actualizar observación:', error);
        mostrarMensaje('Error de conexión al actualizar la observación.', 'error');
      }
    };


    // --- Funciones auxiliares de formato (Sin Cambios) ---
    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined) {
        return '';
      }
      const num = parseFloat(valor);
      if (isNaN(num)) {
        return '';
      }
      return new Intl.NumberFormat('de-DE').format(num);
    };

    const formatearFecha = (fecha) => {
      if (!fecha) return 'N/A';
      const d = new Date(fecha);
      const dia = String(d.getDate()).padStart(2, '0');
      const mes = String(d.getMonth() + 1).padStart(2, '0');
      const anio = d.getFullYear();
      return `${dia}-${mes}-${anio}`;
    };

    // --- FUNCIÓN CLAVE: Agrupar Cuotas (CORREGIDA FINAL) ---
    const agruparCuotas = (cuotas) => {
      const grupos = new Map();

      cuotas.forEach(cuota => {
        const key = `${cuota.rut_cliente}-${cuota.patente}`;

        if (!grupos.has(key)) {
          grupos.set(key, {
            rut_cliente: cuota.rut_cliente,
            nombres: cuota.nombres,
            apellidos: cuota.apellidos,
            fono: cuota.fono,
            patente: cuota.patente,
            monto_total_impago: 0, // Sumará el MONTO NOMINAL de las cuotas atrasadas.
            observacion: cuota.observacion,
            cuotas_detalles: [], 
            id_primera_cuota: cuota.id,
            tiene_cuotas_atrasadas: false, 
          });
        }

        const grupo = grupos.get(key);
        
        // 1. Sumamos al monto total solo si la cuota está ATRASADA (dias_atraso > 0)
        if (cuota.dias_atraso > 0) {
            // ✅ AJUSTE FINAL: Usar cuota.monto_cuota para el monto total agrupado (como se solicitó).
            grupo.monto_total_impago += parseFloat(cuota.monto_cuota || 0); 
            grupo.tiene_cuotas_atrasadas = true; 
        }

        // 2. Agregamos el detalle.
        grupo.cuotas_detalles.push({
          id: cuota.id,
          numero_cuota: cuota.numero_cuota,
          fecha_vencimiento: cuota.fecha_vencimiento,
          dias_atraso: cuota.dias_atraso,
          // Mantiene cuota.monto_cuota para el detalle del modal (como se había corregido previamente).
          monto_cuota: cuota.monto_cuota, 
        });

        // Ordenamos los detalles por fecha de vencimiento
        grupo.cuotas_detalles.sort((a, b) => new Date(a.fecha_vencimiento) - new Date(b.fecha_vencimiento));
      });

      // Filtro final: Devolvemos solo los grupos que tienen al menos una cuota atrasada
      return Array.from(grupos.values()).filter(grupo => grupo.tiene_cuotas_atrasadas);
    };


    // --- Función para la API (Sin Cambios) ---
    const cargarCuotasImpagas = async () => {
      isLoading.value = true;
      limpiarMensaje();
      try {
        let apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/cuotas_impagas/`;

        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error('Error al cargar las cuotas impagas.');
        }

        const data = await response.json();
        listaCuotas.value = data; // Lista completa
        listaCuotasAgrupadas.value = agruparCuotas(data); // Lista agrupada y FILTRADA
        mostrarMensaje('Cuotas impagas cargadas con éxito.', 'success');
      } catch (error) {
        console.error('Error:', error);
        mostrarMensaje(error.message || 'Error de conexión con el servidor.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    // --- FUNCIÓN CLAVE: Manejar clic en la fila (Sin Cambios) ---
    const mostrarDetalles = (grupo) => {
      // Aplicamos el filtro para mostrar solo cuotas con días de atraso > 0
      const cuotasAtrasadas = grupo.cuotas_detalles.filter(detalle => detalle.dias_atraso > 0);

      detallesCuotas.value = cuotasAtrasadas;
      rutSeleccionado.value = grupo.rut_cliente;
      patenteSeleccionada.value = grupo.patente;
      mostrarModal.value = true;
    };

    const cerrarModal = () => {
      mostrarModal.value = false;
      detallesCuotas.value = [];
    };


    // --- Funciones para mensajes (Sin Cambios) ---
    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;

      setTimeout(() => {
        mensaje.value = '';
        tipoMensaje.value = '';
      }, 3000);
    };

    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    // Hook del ciclo de vida
    onMounted(() => {
      cargarCuotasImpagas();
    });

    return {
      listaCuotasAgrupadas,
      isLoading,
      mensaje,
      tipoMensaje,
      formatearMilesConPunto,
      formatearFecha,
      actualizarObservacion,
      // Para el modal
      mostrarModal,
      detallesCuotas,
      rutSeleccionado,
      patenteSeleccionada,
      mostrarDetalles,
      cerrarModal,
    };
  },
};
</script>

<template>
  <Header></Header>
  <div class="container-fluid page-container">
    <div class="card shadow">
      <div class="card-header" style="font-size: x-small; color: rgb(56, 149, 73); text-align: center;">
        <h3>Cuotas Impagas</h3>
        <p class="text-muted mb-0" style="font-size: small;">* Haz clic en una fila para ver el detalle de las cuotas atrasadas.</p>
      </div>
      <div class="card-body">
        <div v-if="isLoading" class="alert alert-info text-center">Cargando datos...</div>
        <div v-if="mensaje" :class="`alert alert-${tipoMensaje === 'error' ? 'danger' : 'success'}`">
          {{ mensaje }}
        </div>

        <div class="table-responsive">
          <table class="table table-striped table-hover custom-table">
            <thead>
              <tr>
                <th>RUT / Nombre Cliente</th>
                <th>Telefono</th>
                <th>Patente</th>
                <th>Monto Total Atrasado</th> <th>Observación</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="listaCuotasAgrupadas.length === 0">
                <td colspan="5" class="text-center">No se encontraron grupos con cuotas atrasadas.</td>
              </tr>
              <tr v-for="grupo in listaCuotasAgrupadas" :key="grupo.rut_cliente + grupo.patente"
                @click="mostrarDetalles(grupo)" class="clickable-row">

                <td>{{ grupo.rut_cliente }} {{ grupo.nombres }} {{ grupo.apellidos }}</td>
                <td>{{ grupo.fono }}</td>
                <td>{{ grupo.patente }}</td>
                
                <td class="text-end text-danger negrita">
                  $ {{ formatearMilesConPunto(grupo.monto_total_impago) }}
                </td>
               
                <td class="text-danger negrita" @click.stop>
                  <textarea class="form-control form-control-sm" v-model="grupo.observacion"
                    @blur="actualizarObservacion(grupo.id_primera_cuota, grupo.observacion)"
                    placeholder="Agregar observación" rows="1"></textarea>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div v-if="mostrarModal" class="modal-backdrop">
    <div class="modal-content-custom">
      <div class="modal-header-custom">
        <h5 class="modal-title">Detalle de Cuotas Atrasadas</h5>
        <button type="button" class="btn-close" @click="cerrarModal">X</button>
      </div>
      <div class="modal-body-custom">
        <p><strong>RUT:</strong> {{ rutSeleccionado }} | <strong>Patente:</strong> {{ patenteSeleccionada }}</p>
        
        <table class="table table-sm table-bordered">
          <thead>
            <tr>
              <th>N° Cuota</th>
              <th>Fecha Vencimiento</th>
              <th>Días Atraso</th>
              <th>Monto Cuota</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="detallesCuotas.length === 0">
              <td colspan="4" class="text-center">No hay cuotas con días de atraso en este grupo.</td>
            </tr>
            <tr v-for="detalle in detallesCuotas" :key="detalle.id">
              <td>{{ detalle.numero_cuota }}</td>
              <td>{{ formatearFecha(detalle.fecha_vencimiento) }}</td>
              <td class="text-danger negrita">{{ detalle.dias_atraso }}</td>
              <td class="text-end">$ {{ formatearMilesConPunto(detalle.monto_cuota) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="modal-footer-custom">
        <button type="button" class="btn btn-secondary" @click="cerrarModal">Cerrar</button>
      </div>
    </div>
  </div>

  <Footer></Footer>
</template>

<style scoped>
/* Estilos adicionales para la fila y el modal */
.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background-color: #f0f0f0;
}

/* Estilos del Modal (Popup) */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-content-custom {
  background: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}
.modal-header-custom .btn-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
}

.modal-footer-custom {
  border-top: 1px solid #eee;
  padding-top: 10px;
  margin-top: 15px;
  text-align: right;
}

.negrita {
  font-weight: bolder;
}

.custom-table {
  min-width: 800px;
}

.custom-table th,
.custom-table td {
  text-align: center;
}
</style>