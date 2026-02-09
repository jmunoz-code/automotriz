<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed } from 'vue';

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

    // Nivel del usuario
    const nivel = ref(localStorage.getItem('user_nivel'));

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
        // Convertimos explicitamente dias_atraso a número para evitar errores con strings
        const diasAtraso = parseInt(cuota.dias_atraso || 0);
        if (diasAtraso > 10) {
          // ✅ AJUSTE FINAL: Usar cuota.monto_cuota para el monto total agrupado (como se solicitó).
          grupo.monto_total_impago += parseFloat(cuota.monto_cuota || 0);
          grupo.tiene_cuotas_atrasadas = true;
        }

        // 2. Agregamos el detalle.
        grupo.cuotas_detalles.push({
          id: cuota.id,
          numero_cuota: cuota.numero_cuota,
          fecha_vencimiento: cuota.fecha_vencimiento,
          dias_atraso: diasAtraso,
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
      const cuotasAtrasadas = grupo.cuotas_detalles.filter(detalle => detalle.dias_atraso > 10);

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

    // --- Computed para el Total General ---
    const totalGeneralImpago = computed(() => {
      // Sumamos el 'monto_total_impago' de todos los grupos en la lista
      return listaCuotasAgrupadas.value.reduce((acc, grupo) => acc + (grupo.monto_total_impago || 0), 0);
    });

    // --- NUEVO: Lógica para obtener el Porcentaje respecto al Saldo Total Pendiente ---
    const totalDeudaGeneral = ref(0);

    const cargarTotalDeudaGeneral = async () => {
      try {
        // Usamos el mismo endpoint que en resumen.vue para obtener todas las cuotas
        const response = await fetch(`${import.meta.env.VITE_API_URL}pagocuotas/`);
        if (response.ok) {
          const data = await response.json();
          const todasLasCuotas = data.data || [];

          // Calculamos el saldo total pendiente (monto_cuota - abono_total)
          // Filtrando presupuestos (estado !== 1) tal como en resumen.vue
          // Aseguramos conversión de tipos para evitar errores
          const saldoTotal = todasLasCuotas
            .filter(cuota => parseInt(cuota.estado) !== 1)
            .reduce((acc, cuota) => {
              const saldo = (parseFloat(cuota.monto_cuota) || 0) - (parseFloat(cuota.abono_total) || 0);
              return acc + saldo;
            }, 0);

          totalDeudaGeneral.value = saldoTotal;
          console.log('Total Deuda General cargada:', totalDeudaGeneral.value);
        }
      } catch (error) {
        console.error('Error al cargar total deuda general:', error);
      }
    };

    const porcentajeImpago = computed(() => {
      if (!totalDeudaGeneral.value || totalDeudaGeneral.value === 0) return 0;
      return ((totalGeneralImpago.value / totalDeudaGeneral.value) * 100).toFixed(2);
    });

    const imprimirReporte = () => {
      window.print();
    };

    onMounted(() => {
      cargarCuotasImpagas();
      cargarTotalDeudaGeneral();
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
      totalGeneralImpago,
      totalDeudaGeneral,
      porcentajeImpago,
      imprimirReporte,
      nivel,
    };
  },
};
</script>

<template>
  <div class="no-print">
    <Header></Header>
  </div>
  <div class="container-fluid page-container">
    <div class="card shadow">
      <div class="card-header d-flex justify-content-between align-items-center"
        style="font-size: x-small; color: rgb(56, 149, 73);">
        <div style="flex-grow: 1; text-align: center;">
          <h3 class="mb-1">Cuotas Impagas</h3>
          <p class="text-muted mb-0 no-print" style="font-size: small;">* Haz clic en una fila para ver el detalle de
            las cuotas atrasadas.</p>
        </div>
        <button class="btn btn-outline-dark btn-sm no-print ms-3" @click="imprimirReporte" title="Imprimir Informe">
          <i class="fa-solid fa-print fa-lg"></i> Imprimir
        </button>
      </div>
      <div class="card-body">
        <div v-if="isLoading" class="alert alert-info text-center no-print">Cargando datos...</div>
        <div v-if="mensaje" :class="`alert alert-${tipoMensaje === 'error' ? 'danger' : 'success'} no-print`">
          {{ mensaje }}
        </div>

        <div class="table-responsive">
          <table class="table table-striped table-hover custom-table">
            <thead>
              <tr>
                <th>RUT / Nombre Cliente</th>
                <th>Telefono</th>
                <th>Patente</th>
                <th>Monto Total Atrasado</th>
                <th class="col-observacion">Observación</th>
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

                <td class="text-danger negrita col-observacion" @click.stop>
                  <textarea class="form-control form-control-sm" v-model="grupo.observacion"
                    @blur="actualizarObservacion(grupo.id_primera_cuota, grupo.observacion)"
                    placeholder="Agregar observación" rows="1" :disabled="nivel !== 'ADMIN'"></textarea>
                </td>
              </tr>
            </tbody>
            <tfoot class="no-print-tfoot">
              <tr>
                <td colspan="3" class="text-end negrita" style="font-size: 1.1em;">TOTAL GENERAL IMPAGO:</td>
                <td class="text-end text-danger negrita" style="font-size: 1.1em; border-top: 2px solid #555;">
                  $ {{ formatearMilesConPunto(totalGeneralImpago) }}
                  <br>
                  <span style="font-size: 1.2em; color: red; font-weight: bold;">
                    ({{ porcentajeImpago }}% del Total Pendiente)
                  </span>
                </td>
                <td class="col-observacion"></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Total Section exclusively for Print -->
        <div class="print-only-total mt-4">
          <div class="d-flex justify-content-end align-items-center">
            <div class="text-end me-3 negrita" style="font-size: 1.1em;">TOTAL GENERAL IMPAGO:</div>
            <div class="text-end text-danger negrita"
              style="font-size: 1.1em; border-top: 2px solid #000; min-width: 150px;">
              $ {{ formatearMilesConPunto(totalGeneralImpago) }}
              <br>
              <span style="font-size: 1.2em; color: red; font-weight: bold;">
                ({{ porcentajeImpago }}% del Total Pendiente)
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>

  <div v-if="mostrarModal" class="modal-backdrop no-print">
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

  <div class="no-print">
    <Footer></Footer>
  </div>
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

/* ESTILOS DE IMPRESIÓN */
.print-only-total {
  display: none;
}

@media print {

  .no-print,
  .no-print-tfoot,
  .col-observacion {
    display: none !important;
  }

  .print-only-total {
    display: block !important;
  }

  .card,
  .card-body,
  .container-fluid {
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
  }

  .table-responsive {
    overflow: visible !important;
  }

  /* Asegurar que el total al final no se corte */
  .print-only-total {
    page-break-inside: avoid;
  }
}
</style>