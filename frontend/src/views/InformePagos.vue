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
    const listaCuotas = ref([]);
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');

    const filtroRut = ref('');
    const filtroPatente = ref('');
    const filtroFechaInicio = ref('');
    const filtroFechaTermino = ref('');

    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined || isNaN(parseFloat(valor))) {
        return '';
      }
      const num = parseFloat(valor);
      const formatter = new Intl.NumberFormat('de-DE');
      return formatter.format(num);
    };

    const formatearFecha = (fechaISO) => {
      if (!fechaISO) return '';
      const date = new Date(fechaISO);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
    };

    const obtenerNombreDelMes = (claveMes) => {
      const [anio, mes] = claveMes.split('-');
      const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
      return meses[parseInt(mes) - 1];
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
        if (filtroRut.value) {
          params.append('rut_cliente', filtroRut.value);
        }
        if (filtroPatente.value) {
          params.append('patente', filtroPatente.value);
        }
        if (filtroFechaInicio.value) {
          params.append('fecha_inicio', filtroFechaInicio.value);
        }
        if (filtroFechaTermino.value) {
          params.append('fecha_termino', filtroFechaTermino.value);
        }
        if (params.toString()) {
          apiUrl += `?${params.toString()}`;
        }
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          listaCuotas.value = data.data;
          mostrarMensaje('Informe de pagos actualizado.', 'success');
        } else {
          console.error('Error cargando el informe de pagos:', response.statusText);
          mostrarMensaje('Error cargando el informe de pagos.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión cargando el informe de pagos:', error);
        mostrarMensaje('Error de conexión con el servidor.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const cuotasFiltradasYAgrupadas = computed(() => {
      if (!listaCuotas.value || listaCuotas.value.length === 0) {
        return {};
      }

      // 1. Filtrar las cuotas pagadas y por rango de fecha
      const inicio = filtroFechaInicio.value ? new Date(filtroFechaInicio.value + 'T00:00:00') : null;
      const termino = filtroFechaTermino.value ? new Date(filtroFechaTermino.value + 'T23:59:59') : null;

      const pagadasYFiltradasPorFecha = listaCuotas.value.filter(cuota => {
        // Filtrar cuotas de contratos descartados (estado = 1)
        if (cuota.estado === 1) {
          return false;
        }

        const cuotaPagada = parseFloat(cuota.abono_total) > 0;
        const fechaVencimiento = new Date(cuota.fecha_vencimiento);
        const enRango = (!inicio || fechaVencimiento >= inicio) && (!termino || fechaVencimiento <= termino);

        return cuotaPagada && enRango;
      });

      // 2. Agrupar por préstamo (RUT y Patente) y ordenar dentro de cada grupo por número de cuota
      const prestamosAgrupados = pagadasYFiltradasPorFecha.reduce((acc, cuota) => {
        const clavePrestamo = `${cuota.rut_cliente}-${cuota.patente}`;
        if (!acc[clavePrestamo]) {
          acc[clavePrestamo] = [];
        }
        acc[clavePrestamo].push(cuota);
        return acc;
      }, {});

      // 3. Procesar cada préstamo para calcular intereses y saldos
      const cuotasProcesadas = [];
      for (const clavePrestamo in prestamosAgrupados) {
        let capitalRestante = parseFloat(prestamosAgrupados[clavePrestamo][0].monto_a_financiar);

        prestamosAgrupados[clavePrestamo].sort((a, b) => a.numero_cuota - b.numero_cuota);

        prestamosAgrupados[clavePrestamo].forEach(cuota => {
          const interesCalculado = (capitalRestante * parseFloat(cuota.interes_mensual)) / 100;
          const pagoCapital = parseFloat(cuota.monto_cuota) - interesCalculado;
          const capitalAntesDelPago = capitalRestante;
          capitalRestante -= pagoCapital;

          const cuotaConCalculos = {
            ...cuota,
            interes_calculado: interesCalculado,
            pago_capital: pagoCapital,
            monto_a_financiar_calculado: capitalAntesDelPago,
            saldo: parseFloat(cuota.monto_cuota) - parseFloat(cuota.abono_total)
          };
          cuotasProcesadas.push(cuotaConCalculos);
        });
      }

      // 4. Agrupar las cuotas procesadas por año y mes para la visualización
      const grupos = {};
      cuotasProcesadas.forEach(cuota => {
        const fecha = new Date(cuota.fecha_vencimiento);
        const anio = fecha.getFullYear();
        const mes = fecha.getMonth() + 1;
        const claveMes = `${anio}-${String(mes).padStart(2, '0')}`;

        if (!grupos[anio]) {
          grupos[anio] = {
            totalAnual: 0,
            totalInteresAnual: 0,
            totalCapitalAnual: 0,
            totalMontoCuotaAnual: 0,
            totalAbonadoAnual: 0,
            meses: {}
          };
        }
        if (!grupos[anio].meses[claveMes]) {
          grupos[anio].meses[claveMes] = {
            totalMensual: 0,
            totalInteresMensual: 0,
            totalCapitalMensual: 0,
            totalAmortizacionCapitalMensual: 0,
            totalMontoCuotaMensual: 0,
            totalAbonadoMensual: 0,
            cuotas: []
          };
        }

        grupos[anio].meses[claveMes].cuotas.push(cuota);
        grupos[anio].meses[claveMes].totalMensual += parseFloat(cuota.abono_total) || 0;
        grupos[anio].meses[claveMes].totalInteresMensual += cuota.interes_calculado || 0;
        grupos[anio].meses[claveMes].totalCapitalMensual += cuota.monto_a_financiar_calculado || 0;
        grupos[anio].meses[claveMes].totalAmortizacionCapitalMensual += cuota.pago_capital || 0;
        grupos[anio].meses[claveMes].totalMontoCuotaMensual += parseFloat(cuota.monto_cuota) || 0;
        grupos[anio].meses[claveMes].totalAbonadoMensual += parseFloat(cuota.abono_total) || 0;

        grupos[anio].totalAnual += parseFloat(cuota.abono_total) || 0;
        grupos[anio].totalInteresAnual += cuota.interes_calculado || 0;
        grupos[anio].totalCapitalAnual += cuota.monto_a_financiar_calculado || 0;
        grupos[anio].totalMontoCuotaAnual += parseFloat(cuota.monto_cuota) || 0;
        grupos[anio].totalAbonadoAnual += parseFloat(cuota.abono_total) || 0;
      });

      return grupos;
    });

    const totalesGenerales = computed(() => {
      const totales = {
        totalInteres: 0,
        totalCapital: 0,
        totalMontoCuota: 0,
        totalAbonado: 0,
      };

      const grupos = cuotasFiltradasYAgrupadas.value;
      for (const anio in grupos) {
        totales.totalInteres += grupos[anio].totalInteresAnual;
        totales.totalCapital += grupos[anio].totalCapitalAnual;
        totales.totalMontoCuota += grupos[anio].totalMontoCuotaAnual;
        totales.totalAbonado += grupos[anio].totalAbonadoAnual;
      }
      return totales;
    });

    watch([filtroFechaInicio, filtroFechaTermino], () => {
      cargarListaDeCuotas();
    });

    onMounted(() => {
      //cargarListaDeCuotas();
    });

    return {
      isLoading,
      mensaje,
      tipoMensaje,
      filtroRut,
      filtroPatente,
      filtroFechaInicio,
      filtroFechaTermino,
      cargarListaDeCuotas,
      formatearMilesConPunto,
      formatearFecha,
      cuotasFiltradasYAgrupadas,
      obtenerNombreDelMes,
      totalesGenerales,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container-fluid mt-3">
    <div class="card shadow-sm">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
        Informe de Pagos
      </div>
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-3">
            <label for="filtroRut" class="form-label negrita">Filtrar por RUT Cliente:</label>
            <input type="text" class="form-control form-control-sm" id="filtroRut" v-model.lazy="filtroRut"
              placeholder="Ej: 12.345.678-9" />
          </div>
          <div class="col-md-3">
            <label for="filtroPatente" class="form-label negrita">Filtrar por Patente:</label>
            <input type="text" class="form-control form-control-sm" id="filtroPatente" v-model.lazy="filtroPatente"
              placeholder="Ej: ABCD12" />
          </div>
          <div class="col-md-3">
            <label for="filtroFechaInicio" class="form-label negrita">Fecha de Inicio:</label>
            <input type="date" class="form-control form-control-sm" id="filtroFechaInicio"
              v-model="filtroFechaInicio" />
          </div>
          <div class="col-md-3">
            <label for="filtroFechaTermino" class="form-label negrita">Fecha de Término:</label>
            <input type="date" class="form-control form-control-sm" id="filtroFechaTermino"
              v-model="filtroFechaTermino" />
          </div>
          <div class="col-md-12 d-flex justify-content-end mt-3">
            <button class="btn btn-primary btn-sm" @click="cargarListaDeCuotas" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Cargando...' : 'Generar Informe' }}
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

        <div v-if="isLoading" class="text-center">Cargando informe...</div>

        <div v-else-if="Object.keys(cuotasFiltradasYAgrupadas).length === 0" class="text-center">
          No se encontraron pagos para los criterios de búsqueda.
        </div>

        <div v-else class="mt-4">
          <div v-for="(anioData, anio) in cuotasFiltradasYAgrupadas" :key="anio" class="mb-5">
            <div class="row">
              <div class="col-12 d-flex justify-content-between align-items-center">
                <h3 class="mb-3">
                  <span class="badge bg-primary">Año: {{ anio }}</span>
                </h3>
              </div>
            </div>

            <div class="card shadow-sm mb-4">
              <div class="card-header bg-success text-white">
                <h5 class="mb-0">Totales Anuales</h5>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Total Interés:</p>
                    <h5>$ {{ formatearMilesConPunto(anioData.totalInteresAnual) }}</h5>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Total Capital:</p>
                    <h5>$ {{ formatearMilesConPunto(anioData.totalCapitalAnual) }}</h5>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Total Cuotas:</p>
                    <h5>$ {{ formatearMilesConPunto(anioData.totalMontoCuotaAnual) }}</h5>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Total Abonado:</p>
                    <h5>$ {{ formatearMilesConPunto(anioData.totalAbonadoAnual) }}</h5>
                  </div>
                </div>
              </div>
            </div>

            <div v-for="(mesData, claveMes) in anioData.meses" :key="claveMes" class="card shadow-sm mb-4">
              <div class="card-header bg-light">
                <div class="row">
                  <div class="col-6">
                    <h5 class="mb-0">
                      <span class="badge bg-secondary">Mes: {{ obtenerNombreDelMes(claveMes) }}</span>
                    </h5>
                  </div>
                </div>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-striped table-hover custom-table mb-0">
                    <thead>
                      <tr>
                        <th style="text-align: center">RUT Cliente</th>
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

                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="cuota in mesData.cuotas" :key="cuota.id">
                        <td style="text-align: center">{{ cuota.rut_cliente }}</td>
                        <td style="text-align: center">{{ cuota.patente }}</td>
                        <td style="text-align: center">{{ cuota.numero_cuota }}</td>
                        <td style="text-align: center">{{ formatearFecha(cuota.fecha_vencimiento) }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.monto_a_financiar_calculado) }}
                        </td>
                        <td style="text-align: center">{{ cuota.interes_mensual }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.interes_calculado) }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.pago_capital) }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.pago_capital +
                          cuota.interes_calculado) }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.monto_cuota) }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.abono_total) }}</td>
                        <td style="text-align: center">{{ formatearMilesConPunto(cuota.saldo) }}</td>
                        <td style="text-align: center">
                          <img v-if="parseFloat(cuota.abono_total) >= parseFloat(cuota.monto_cuota)"
                            src="../img/visto.png" alt="Abono Completo" width="20" height="20" />
                          <img v-else src="../img/x.png" alt="Abono Pendiente" width="20" height="20" />
                        </td>

                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colspan="4" class="text-end negrita">Subtotales Mensuales:</td>
                        <td class="negrita text-center">{{ formatearMilesConPunto(mesData.totalCapitalMensual) }}</td>
                        <td colspan="1"></td>
                        <td class="negrita text-center">{{ formatearMilesConPunto(mesData.totalInteresMensual) }}</td>
                        <td class="negrita text-center">{{
                          formatearMilesConPunto(mesData.totalAmortizacionCapitalMensual) }}</td>
                        <td class="negrita text-center">{{ formatearMilesConPunto(mesData.totalInteresMensual +
                          mesData.totalAmortizacionCapitalMensual) }}</td>
                        <td class="negrita text-center">{{ formatearMilesConPunto(mesData.totalMontoCuotaMensual) }}
                        </td>
                        <td class="negrita text-center">{{ formatearMilesConPunto(mesData.totalAbonadoMensual) }}</td>
                        <td colspan="2"></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <div class="row mt-5" v-if="Object.keys(cuotasFiltradasYAgrupadas).length > 0">
            <div class="col-12">
              <div class="card shadow-sm">
                <div class="card-header bg-success text-white">
                  <h4 class="mb-0">Totales Generales del Informe</h4>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-3">
                      <p class="mb-1 negrita">Total Interés:</p>
                      <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalInteres) }}</h5>
                    </div>
                    <div class="col-md-3">
                      <p class="mb-1 negrita">Total Capital:</p>
                      <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalCapital) }}</h5>
                    </div>
                    <div class="col-md-3">
                      <p class="mb-1 negrita">Total Cuotas:</p>
                      <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalMontoCuota) }}</h5>
                    </div>
                    <div class="col-md-3">
                      <p class="mb-1 negrita">Total Abonado:</p>
                      <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalAbonado) }}</h5>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

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
  width: 100%;
  table-layout: auto;
}

.custom-table td,
.custom-table th {
  white-space: nowrap;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
}

.badge {
  font-size: 1rem;
}
</style>