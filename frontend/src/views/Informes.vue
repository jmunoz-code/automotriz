<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, watch, computed } from 'vue';
import moment from 'moment';
import 'moment/locale/es';

moment.locale('es');

export default {
  components: {
    Header,
    Footer,
  },
  setup() {
    const listaPresupuestos = ref([]);
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');

    const filtroNombre = ref('');
    const filtroRut = ref('');
    const filtroPatente = ref('');
    const filtroFechaInicio = ref('');
    const filtroFechaFin = ref('');

    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined) {
        return '';
      }
      return parseFloat(valor).toLocaleString('de-DE');
    };

    // INICIO: CAMBIO IMPLEMENTADO AQUÍ
    const formatearFecha = (fechaISO) => {
      if (!fechaISO) return '';
      const date = new Date(fechaISO);
      
      // Se usan los métodos getUTC... para asegurar que se muestre el día 
      // correcto sin importar la zona horaria del cliente.
      const day = String(date.getUTCDate()).padStart(2, '0');
      const month = String(date.getUTCMonth() + 1).padStart(2, '0'); // getUTCMonth es base 0, por eso se suma 1.
      const year = date.getUTCFullYear();
      
      return `${day}-${month}-${year}`;
    };
    // FIN: CAMBIO IMPLEMENTADO AQUÍ

    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;
      setTimeout(limpiarMensaje, 3000);
    };

    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    const cargarListaDePresupuestos = async () => {
      isLoading.value = true;
      listaPresupuestos.value = [];

      try {
        const params = new URLSearchParams();
        if (filtroNombre.value) params.append('nombre', filtroNombre.value);
        if (filtroRut.value) params.append('rut', filtroRut.value);
        if (filtroPatente.value) params.append('patente', filtroPatente.value);
        if (filtroFechaInicio.value) params.append('fecha_inicio', filtroFechaInicio.value);
        if (filtroFechaFin.value) params.append('fecha_fin', filtroFechaFin.value);

        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/buscar/?${params.toString()}`;

        const response = await fetch(apiUrl);

        if (response.ok) {
          const data = await response.json();
          listaPresupuestos.value = data.data;
          if (listaPresupuestos.value.length === 0) {
            mostrarMensaje('No se encontraron presupuestos que coincidan con los criterios de búsqueda.', 'info');
          } else {
            mostrarMensaje('Presupuestos actualizados.', 'success');
          }
        } else {
          const errorData = await response.json();
          mostrarMensaje('Error cargando los presupuestos. Por favor, intente de nuevo.', 'error');
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor. Verifique su conexión o intente más tarde.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    watch([filtroNombre, filtroRut, filtroPatente, filtroFechaInicio, filtroFechaFin], () => {
      if (filtroNombre.value || filtroRut.value || filtroPatente.value || filtroFechaInicio.value || filtroFechaFin.value) {
        cargarListaDePresupuestos();
      } else {
        listaPresupuestos.value = [];
        limpiarMensaje();
      }
    });

    onMounted(() => {
    });

    const presupuestosAgrupados = computed(() => {
      const agrupados = {};
      if (!listaPresupuestos.value || listaPresupuestos.value.length === 0) {
        return {};
      }

      // INICIO: Cambio para ordenar por FECHA DE CREACIÓN (ascendente)
      const presupuestosOrdenados = [...listaPresupuestos.value].sort((a, b) => {
        // Ordena por fecha_creacion (Fecha Contrato) de forma ascendente (más antiguo primero)
        return new Date(a.fecha_creacion) - new Date(b.fecha_creacion);
      });
      // FIN: Cambio para ordenar por FECHA DE CREACIÓN (ascendente)

      presupuestosOrdenados.forEach(p => {
        const fecha = moment(p.fecha_creacion);
        const anio = fecha.format('YYYY');
        const mesAnio = fecha.format('MMMM YYYY');
        const utilidad = p.utilidad;

        if (!agrupados[anio]) {
          agrupados[anio] = {
            total_anio: 0,
            meses: {},
          };
        }
        if (!agrupados[anio].meses[mesAnio]) {
          agrupados[anio].meses[mesAnio] = {
            total_mes: 0,
            presupuestos: [],
          };
        }
        agrupados[anio].meses[mesAnio].presupuestos.push(p);
        agrupados[anio].meses[mesAnio].total_mes += utilidad;
        agrupados[anio].total_anio += utilidad;
      });
      return agrupados;
    });

    const traducirMes = (mesAnio) => {
      const [mesIngles, anio] = mesAnio.split(' ');
      const meses = {
        'January': 'Enero',
        'February': 'Febrero',
        'March': 'Marzo',
        'April': 'Abril',
        'May': 'Mayo',
        'June': 'Junio',
        'July': 'Julio',
        'August': 'Agosto',
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre',
        'December': 'Diciembre',
      };
      return `${meses[mesIngles]} ${anio}`;
    };

    return {
      listaPresupuestos,
      isLoading,
      mensaje,
      tipoMensaje,
      filtroNombre,
      filtroRut,
      filtroPatente,
      filtroFechaInicio,
      filtroFechaFin,
      cargarListaDePresupuestos,
      formatearMilesConPunto,
      formatearFecha,
      mostrarMensaje,
      presupuestosAgrupados,
      traducirMes,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container-fluid mt-3">
    <div class="card shadow-sm">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
        Informe Negocios
      </div>
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-3">
            <label for="filtroNombre" class="form-label negrita">Nombre:</label>
            <input type="text" class="form-control form-control-sm" id="filtroNombre" v-model.lazy="filtroNombre"
              placeholder="Ej: Juan Perez" />
          </div>
          <div class="col-md-3">
            <label for="filtroRut" class="form-label negrita">RUT:</label>
            <input type="text" class="form-control form-control-sm" id="filtroRut" v-model.lazy="filtroRut"
              placeholder="Ej: 12.345.678-9" />
          </div>
          <div class="col-md-3">
            <label for="filtroPatente" class="form-label negrita">Patente:</label>
            <input type="text" class="form-control form-control-sm" id="filtroPatente" v-model.lazy="filtroPatente"
              placeholder="Ej: ABCD12" />
          </div>
          <div class="col-md-3">
            <label for="filtroFechaInicio" class="form-label negrita">Fecha Inicial:</label>
            <input type="date" class="form-control form-control-sm" id="filtroFechaInicio"
              v-model.lazy="filtroFechaInicio" />
          </div>
          <div class="col-md-3">
            <label for="filtroFechaFin" class="form-label negrita">Fecha Final:</label>
            <input type="date" class="form-control form-control-sm" id="filtroFechaFin" v-model.lazy="filtroFechaFin" />
          </div>
          <div class="col-md-3 d-flex align-items-end justify-content-between">
            <button class="btn btn-primary btn-sm me-2" @click="cargarListaDePresupuestos" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Buscando...' : 'Buscar Presupuestos' }}
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
                <th style="text-align: center">Fecha Contrato</th>
                <th style="text-align: center">Primer Vencimiento</th>
                <th style="text-align: center">Tipo Negocio</th>
                <th style="text-align: center">Rut Cliente</th>
                <th style="text-align: center">Nombre Cliente</th>
                <th style="text-align: center">Apellidos Cliente</th>
                <th style="text-align: center">Patente</th>
                <th style="text-align: right">Monto Compra</th>
                <th style="text-align: right">Monto Venta</th>
                <th style="text-align: right">Gastos</th>
                <th style="text-align: right">Utilidad</th>
              </tr>
            </thead>
            <tbody>
              <template v-if="Object.keys(presupuestosAgrupados).length > 0">
                <template v-for="(datosAnio, anio) in presupuestosAgrupados" :key="anio">
                  <tr class="table-dark">
                    <td></td>
                    <td colspan="9" style="font-weight: bold; font-size: large; text-align: justify;">Subtotal Año {{
                      anio }}</td>
                    <td class="text-right" style="font-weight: bold; font-size: large;">{{
                      formatearMilesConPunto(datosAnio.total_anio) }}
                    </td>
                  </tr>
                  <template v-for="(datosMes, mes) in datosAnio.meses" :key="mes">
                    <tr class="table-secondary">
                      <td></td>
                      <td colspan="9" class="text-start" style="font-weight: bold; font-size: medium;">{{
                        traducirMes(mes) }}
                      </td>
                      <td class="text-right" style="font-weight: bold; font-size: medium;">{{
                        formatearMilesConPunto(datosMes.total_mes) }}
                      </td>
                    </tr>
                    <tr v-for="presupuesto in datosMes.presupuestos" :key="presupuesto.id" style="cursor: default;">
                      <td style="text-align: center">{{ formatearFecha(presupuesto.fecha_creacion) }}</td>
                       <td style="text-align: center">{{ formatearFecha(presupuesto.fecha_inicio_pago) }}</td>
                      <td style="text-align: center"> {{ presupuesto.tipo_pago == 0 ? 'Contado' : 'Crédito' }}</td>
                      <td style="text-align: center">{{ presupuesto.rut_cliente }}</td>
                      <td style="text-align: left">{{ presupuesto.nombre_cliente }}</td>
                      <td style="text-align: left">{{ presupuesto.apellidos }}</td>
                      <td style="text-align: left">{{ presupuesto.patente_vehiculo }}</td>
                      <td style="text-align: right;"
                        :style="{ color:presupuesto.precio_compra <=0 ? 'red' : 'black' }">
                        {{ formatearMilesConPunto(presupuesto.precio_compra) }}
                      </td>

                      <td style="text-align: right">{{ formatearMilesConPunto(presupuesto.precio_venta) }}</td>
    

                      <td style="text-align: right">{{ formatearMilesConPunto(presupuesto.sumatoria_gastos) }}</td>
                      <td style="text-align: right;"
                        :style="{ color:presupuesto.precio_venta < presupuesto.utilidad ? 'red' : 'black', fontWeight: presupuesto.utilidad < 0 ? 'bold' : 'normal' }">
                        {{ formatearMilesConPunto(presupuesto.utilidad) }}
                      </td>
                    </tr>
                  </template>
                </template>
              </template>

              <tr v-else-if="isLoading">
                <td colspan="8" class="text-center">Cargando Presupuestos...</td>
              </tr>
              <tr v-else>
                <td colspan="8" class="text-center">No se encontraron presupuestos que coincidan con los criterios de
                  búsqueda.</td>
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

.custom-table {
  min-width: 1000px;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
}
</style>