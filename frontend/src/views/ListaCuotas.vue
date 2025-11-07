<script>
// Lógica del componente (sin cambios)
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import ModalDetallePago from '@/components/ModalDetallePago.vue';
import AbonoDetalleModal from '@/components/AbonoDetalleModal.vue';
import { onMounted, ref, computed, watch } from 'vue';

export default {
  components: {
    Header,
    Footer,
    AbonoDetalleModal,
    ModalDetallePago,
  },
  setup() {
    const listaCuotas = ref([]);
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');

    const filtroRutCuota = ref('');
    const filtroPatenteCuota = ref('');

    const showModal = ref(false);
    const showModal1 = ref(false);
    const cuotaParaEditar = ref({});

    const formatearMilesConPunto = (valor) => {
    if (valor === null || valor === undefined) {
      return '';
    }
    
    // 1. Convertir a número.
    const num = parseFloat(valor); 
    
    if (isNaN(num)) {
      return '';
    }
    
    // 2. Aplicar el redondeo al entero más cercano aquí:
    const numRedondeado = Math.round(num); // <-- ¡Aquí se redondea!
    
    // 3. Aplicar el formato.
    const formatter = new Intl.NumberFormat('de-DE');
    return formatter.format(numRedondeado); // Usamos el número redondeado
};
    const formatearFecha = (fechaISO) => {
      if (!fechaISO) return '';
      const date = new Date(fechaISO);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
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
      isLoading.value = true;
      listaCuotas.value = [];
      try {
        let apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/`;
        const params = new URLSearchParams();
        if (filtroRutCuota.value) {
          params.append('rut_cliente', filtroRutCuota.value);
        }
        if (filtroPatenteCuota.value) {
          params.append('patente', filtroPatenteCuota.value);
        }
        if (params.toString()) {
          apiUrl += `?${params.toString()}`;
        }
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          listaCuotas.value = data.data;
          mostrarMensaje('Lista de cuotas actualizada.', 'success');
        } else {
          console.error('Error cargando la lista de cuotas:', response.statusText);
          mostrarMensaje('Error cargando la lista de cuotas.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión cargando la lista de cuotas:', error);
        mostrarMensaje('Error de conexión con el servidor.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const eliminarCuotas = async () => {
      if (!filtroRutCuota.value || !filtroPatenteCuota.value) {
        mostrarMensaje('Por favor, ingrese un RUT de cliente y una Patente para eliminar.', 'error');
        return;
      }
      if (!confirm(`¿Está seguro de que desea eliminar todas las cuotas para el RUT: ${filtroRutCuota.value} y Patente: ${filtroPatenteCuota.value}? Esta acción no se puede deshacer.`)) {
        return;
      }
      isLoading.value = true;
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/eliminar_por_rut_patente/`;
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            rut_cliente: filtroRutCuota.value,
            patente: filtroPatenteCuota.value,
          }),
        });
        if (response.ok) {
          const data = await response.json();
          mostrarMensaje(data.message || 'Cuotas eliminadas exitosamente.', 'success');
          cargarListaDeCuotas();
        } else {
          const errorData = await response.json();
          console.error('Error eliminando cuotas:', errorData.message || response.statusText);
          mostrarMensaje(errorData.message || 'Error al eliminar cuotas.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al eliminar cuotas:', error);
        mostrarMensaje('Error de conexión con el servidor al intentar eliminar.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const eliminarUnaCuota = async (cuotaId) => {
      const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/eliminar_por_id/${cuotaId}/`;
      console.log('URL:', apiUrl);
      if (!confirm('¿Está seguro de que desea eliminar esta cuota? Esta acción no se puede deshacer.')) {
        return;
      }
      isLoading.value = true;
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/eliminar_por_id/${cuotaId}/`;
        console.log('URL:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
        });
        if (response.ok) {
          mostrarMensaje('Cuota eliminada exitosamente.', 'success');
         cargarListaDeCuotas();
        } else {
          const errorData = await response.json();
          console.error('Error eliminando la cuota:', errorData.message || response.statusText);
          mostrarMensaje(errorData.message || 'Error al eliminar la cuota.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión al eliminar cuota:', error);
        mostrarMensaje('Error de conexión con el servidor al intentar eliminar la cuota.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const abrirModalEdicion = (cuota) => {
      cuotaParaEditar.value = { ...cuota };
      showModal.value = true;
    };

    const cerrarModalEdicion = () => {
      showModal.value = false;
      cargarListaDeCuotas();
    };

    const abrirModalGrabar = (cuota) => {
      cuotaParaEditar.value = { ...cuota };
      showModal1.value = true;
    };

    const cerrarModalGrabar = () => {
      showModal1.value = false;
    };

    const handleAbonoRegistrado = (mensajeTexto, tipo) => {
      mostrarMensaje(mensajeTexto, tipo);
      cargarListaDeCuotas();
    };

    // Ejemplo de la función que podría disparar la actualización
    const grabarEdicionCuota = async (cuotaId, nuevoMonto) => {
      console.log('Modifica:');
      
      try {
        const url = `${import.meta.env.VITE_API_URL}pagocuotas/modificar_cuota/${cuotaId}/`;
        
        const response = await fetch(url, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            monto_cuota: nuevoMonto
          })
        });

        if (!response.ok) {
          throw new Error(`Error al actualizar la cuota: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Cuota actualizada exitosamente:', data);

        // Opcional: Recargar los datos de la lista para mostrar el cambio
        cargarListaDeCuotas();
         

      } catch (error) {
        console.error('Error:', error);
        // Manejar el error, por ejemplo, mostrar un mensaje al usuario
      }
    };

    const actualizarObservacion = async (cuotaId, nuevaObservacion) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/${cuotaId}/`;
        const response = await fetch(apiUrl, {
          method: 'PATCH',
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

    // --- PROPIEDAD COMPUTADA CON LA LÓGICA DE REINICIO CORREGIDA ---
    const cuotasConCalculoDeCapital = computed(() => {
      if (!listaCuotas.value || listaCuotas.value.length === 0) {
        return [];
      }

      let capitalRestante = 0;
      let lastRut = null;
      let lastPatente = null;

      // Se usa .map() para crear un nuevo array con los cálculos
      return listaCuotas.value.map((cuota, index) => {
        const nuevaCuota = { ...cuota };

        // Condición para reiniciar el cálculo: si el RUT o la patente cambian.
        if (index === 0 || nuevaCuota.rut_cliente !== lastRut || nuevaCuota.patente !== lastPatente) {
          capitalRestante = parseFloat(nuevaCuota.monto_a_financiar);
        }

        // Calcula el interés de la cuota actual en base al capital restante.
        const interesCalculado = (capitalRestante * nuevaCuota.interes_mensual) / 100;
        nuevaCuota.interes_calculado = interesCalculado;

        // Calcula el pago de capital de la cuota actual.
        const pagoCapital = nuevaCuota.monto_cuota - interesCalculado;
        nuevaCuota.pago_capital = pagoCapital;

        // Asigna el capital restante actual a la propiedad de la cuota.
        nuevaCuota.monto_a_financiar_calculado = capitalRestante;

        // Actualiza el capital restante para la siguiente iteración.
        capitalRestante -= pagoCapital;

        // Almacena los valores de la fila actual para la próxima comparación.
        lastRut = nuevaCuota.rut_cliente;
        lastPatente = nuevaCuota.patente;

        return nuevaCuota;
      });
    });

    watch([filtroRutCuota, filtroPatenteCuota], () => {
      cargarListaDeCuotas();
    });

    onMounted(() => {
      // cargarListaDeCuotas();
    });

    return {
      listaCuotas,
      isLoading,
      mensaje,
      tipoMensaje,
      filtroRutCuota,
      filtroPatenteCuota,
      cargarListaDeCuotas,
      eliminarCuotas,
      formatearMilesConPunto,
      formatearFecha,
      mostrarMensaje,
      showModal,
      showModal1,
      cuotaParaEditar,
      abrirModalEdicion,
      cerrarModalEdicion,
      abrirModalGrabar,
      cerrarModalGrabar,
      handleAbonoRegistrado,
      actualizarObservacion,
      eliminarUnaCuota,
      cuotasConCalculoDeCapital,
      grabarEdicionCuota,
    };
  },
};
</script>


<template>
  <Header></Header>

  <div class="container-fluid mt-3">
    <div class="card shadow-sm">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
        Listado y Búsqueda de Cuotas
      </div>
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-4">
            <label for="filtroRutCuota" class="form-label negrita">Filtrar/Eliminar por RUT Cliente:</label>
            <input type="text" class="form-control form-control-sm" id="filtroRutCuota" v-model.lazy="filtroRutCuota"
              placeholder="Ej: 12.345.678-9" />
          </div>
          <div class="col-md-4">
            <label for="filtroPatenteCuota" class="form-label negrita">Filtrar/Eliminar por Patente:</label>
            <input type="text" class="form-control form-control-sm" id="filtroPatenteCuota"
              v-model.lazy="filtroPatenteCuota" placeholder="Ej: ABCD12" />
          </div>
          <div class="col-md-4 d-flex align-items-end justify-content-between">
            <button class="btn btn-primary btn-sm me-2" @click="cargarListaDeCuotas" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Cargando...' : 'Buscar Cuotas' }}
            </button>
            <button class="btn btn-danger btn-sm" @click="eliminarCuotas"
              :disabled="isLoading || !filtroRutCuota || !filtroPatenteCuota">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Eliminando...' : 'Eliminar Cuotas' }}
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
                <th style="text-align: center">RUT</th>
                <th style="text-align: center">Nombre</th>
                <th style="text-align: center">Apellido</th>
                <th style="text-align: center">Patente</th>
                <th style="text-align: center"># Cuota</th>
                <th style="text-align: center">Fecha Vencimiento</th>
                <th style="text-align: center">Capital</th>
                <th style="text-align: center">Tasa</th>
                <th style="text-align: center">Interes</th>
                <th style="text-align: center">Amortizacion Capital</th>
                <th style="text-align: center">Capital + Interés</th>
                <th style="text-align: center">Monto Cuota</th>
                <th style="text-align: center">Monto Abonado</th>
                <th style="text-align: center">Saldo</th>
                <th style="text-align: center">Estado</th>
                <th style="text-align: center">Observación</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="cuotasConCalculoDeCapital.length === 0 && !isLoading">
                <td colspan="12" class="text-center">No se encontraron cuotas que coincidan con los criterios de
                  búsqueda.</td>
              </tr>
              <tr v-else-if="isLoading">
                <td colspan="12" class="text-center">Cargando cuotas...</td>
              </tr>
              <tr v-for="cuota in cuotasConCalculoDeCapital" :key="cuota.id" style="cursor: pointer;">
                <td style="text-align: center">{{ cuota.rut_cliente }}</td>
                <td style="text-align: left;width: 120px;">{{ cuota.nombres.trim() }}</td>
                <td style="text-align: left;width: 180px;">{{ cuota.apellidos.trim() }}</td>
                <td style="text-align: center">{{ cuota.patente }}</td>
                <td style="text-align: center">{{ cuota.numero_cuota }}</td>
                <td style="text-align: center">{{ formatearFecha(cuota.fecha_vencimiento) }}</td>
                <td style="text-align: center">{{ formatearMilesConPunto(cuota.monto_a_financiar_calculado,2) }}</td>
                <td style="text-align: center">{{ cuota.interes_mensual }}</td>
                <td style="text-align: center">{{ formatearMilesConPunto(cuota.interes_calculado,2) }}</td>
                <td style="text-align: center">{{ formatearMilesConPunto(cuota.pago_capital,2) }}</td>
               <td style="text-align: center">{{ formatearMilesConPunto(cuota.pago_capital + cuota.interes_calculado, 2) }}</td>
                
                <td style="text-align: center">


                  <input type="number" v-model="cuota.monto_cuota"
                    @blur="grabarEdicionCuota(cuota.id, cuota.monto_cuota)" class="form-control form-control-sm" style="width: 120px; text-align: center;" />


                </td>
                <td style="text-align: center">{{ formatearMilesConPunto(cuota.abono_total) }} </td>
                <td style="text-align: center">{{ formatearMilesConPunto(cuota.monto_cuota - cuota.abono_total) }}</td>
                <td style="text-align: center">

                  <img v-if="parseFloat(cuota.abono_total) >= parseFloat(cuota.monto_cuota)" src="../img/visto.png"
                    alt="Abono Completo" width="20" height="20" />
                  <img v-else src="../img/x.png" alt="Abono Pendiente" width="20" height="20" />

                </td>
                <td>
                  <textarea class="form-control form-control-sm" v-model="cuota.observacion"
                    @blur="actualizarObservacion(cuota.id, cuota.observacion)" placeholder="Agregar observación"
                    rows="1">
                  </textarea>
                </td>
                <td style="width: 310px;">
                  <button class="btn btn-info btn-sm me-4" style="margin-right: 3px;"
                    @click.stop="abrirModalGrabar(cuota)">
                    Abonar
                  </button>
                  <button class="btn btn-secondary btn-sm" @click.stop="abrirModalEdicion(cuota)"
                    style="margin-right: 3px;">
                    Abonos
                  </button>
                  <button class="btn btn-danger btn-sm" @click.stop="eliminarUnaCuota(cuota.id)">
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

  <AbonoDetalleModal :show="showModal" :cuota="cuotaParaEditar" @close="cerrarModalEdicion"
    @abonoRegistrado="handleAbonoRegistrado"></AbonoDetalleModal>

  <ModalDetallePago :show="showModal1" :cuota="cuotaParaEditar" @close="cerrarModalGrabar"
    @abonoRegistrado="handleAbonoRegistrado">
  </ModalDetallePago>

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
  width: 100%;
  /* Asegura que la tabla ocupe todo el ancho disponible */
  table-layout: auto;
  /* Permite que el ancho de las celdas se ajuste al contenido */
}

/* Optimiza la columna de Observación para texto largo */
.custom-table td:nth-child(14) {
  max-width: 150px;
  /* Establece un ancho máximo para la columna de Observación */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  /* Evita que el texto salte de línea */
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
}

tr {
  cursor: pointer;
}
</style>