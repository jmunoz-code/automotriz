<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed } from 'vue';

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

    // --- SECCIÓN DE BÚSQUEDA MODIFICADA ---
    const terminoBusqueda = ref(''); // NUEVO: Un único campo para buscar
    const resultadosBusqueda = ref([]); // NUEVO: Almacena las sugerencias de la API
    const debounceTimer = ref(null); // NUEVO: Para controlar el tiempo de espera al teclear
    const creditoSeleccionado = ref(null); // NUEVO: Para saber si ya se eligió un crédito y mostrar el informe
    const isLoadingSearch = ref(false); // NUEVO: Indicador de carga solo para la lista de sugerencias

    // --- FUNCIONES DE FORMATO (sin cambios) ---
    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined || isNaN(parseFloat(valor))) return '';
      const num = Math.round(parseFloat(valor));
      return new Intl.NumberFormat('de-DE').format(num);
    };

    const formatearFecha = (fechaISO) => {
      if (!fechaISO) return '';
      const date = new Date(fechaISO + 'T00:00:00');
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
    };

    // --- GESTIÓN DE MENSAJES (sin cambios) ---
    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;
      setTimeout(limpiarMensaje, 3000);
    };

    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    // --- LÓGICA DE CARGA DE DATOS (MODIFICADA) ---

    // NUEVO: Función para buscar coincidencias mientras el usuario escribe
    const buscarCoincidencias = () => {
      clearTimeout(debounceTimer.value);

      // Ocultar resultados si el campo está vacío
      if (terminoBusqueda.value.length === 0) {
        resultadosBusqueda.value = [];
        return;
      }

      // La búsqueda solo se activa con al menos 3 caracteres, para coincidir con la lógica del backend
      if (terminoBusqueda.value.length < 3) {
        // Podrías poner un mensaje tipo "Mínimo 3 caracteres" aquí si quieres
        resultadosBusqueda.value = [];
        return;
      }

      isLoadingSearch.value = true;
      debounceTimer.value = setTimeout(async () => {
        try {
          // Llama al NUEVO ENDPOINT LIGERO creado en Django
          const apiUrl = `${import.meta.env.VITE_API_URL}creditos/buscar/?q=${terminoBusqueda.value}`;
          const response = await fetch(apiUrl);

          if (response.ok) {
            const data = await response.json();
            // Asegúrate de que tu backend devuelve la data en 'data.data'
            resultadosBusqueda.value = data.data;
          } else {
            console.error('Error buscando coincidencias', response.statusText);
            resultadosBusqueda.value = [];
          }
        } catch (error) {
          console.error('Error de conexión en búsqueda:', error);
          resultadosBusqueda.value = [];
        } finally {
          isLoadingSearch.value = false;
        }
      }, 300); // Espera 300ms después de la última pulsación (Debounce)
    };

    const seleccionarCreditoYGenerarInforme = async (credito) => {
      creditoSeleccionado.value = credito;
      // Rellena el input con la descripción completa usando el campo 'nombres_completos'
      // que es el nombre del cliente en el backend.
      terminoBusqueda.value = `${credito.nombres_completos} - Patente: ${credito.patente}`;
      resultadosBusqueda.value = [];

      // Llama a la función de carga original con los datos específicos
      await cargarListaDeCuotas(credito.rut_cliente, credito.patente);
    };

    // NUEVO: Función para reiniciar la vista y permitir una nueva búsqueda
    const reiniciarBusqueda = () => {
      listaCuotas.value = [];
      creditoSeleccionado.value = null;
      terminoBusqueda.value = '';
      limpiarMensaje();
    };


    // MODIFICADO: Ahora acepta parámetros para buscar el informe detallado
    const cargarListaDeCuotas = async (rut, patente) => {
      isLoading.value = true;
      listaCuotas.value = [];
      try {
        // Llama al ENDPOINT PESADO original, pero con filtros específicos
        let apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/`;
        const params = new URLSearchParams();

        // Usa los parámetros recibidos del crédito seleccionado
        if (rut) params.append('rut_cliente', rut);
        if (patente) params.append('patente', patente);

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

    // --- PROPIEDADES COMPUTADAS (sin cambios en la lógica interna) ---
    const listaCuotasProcesada = computed(() => {
      // ... (Tu lógica de procesamiento de cuotas permanece igual) ...
      if (!listaCuotas.value || listaCuotas.value.length === 0) {
        return [];
      }

      // Filtrar cuotas de contratos descartados (estado = 1)
      const cuotasSinFiltrar = listaCuotas.value.filter(cuota => cuota.estado !== 1);

      const prestamosAgrupados = cuotasSinFiltrar.reduce((acc, cuota) => {
        const clavePrestamo = `${cuota.rut_cliente}-${cuota.patente}`;
        if (!acc[clavePrestamo]) {
          acc[clavePrestamo] = [];
        }
        acc[clavePrestamo].push(cuota);
        return acc;
      }, {});

      const cuotasProcesadas = [];
      for (const clavePrestamo in prestamosAgrupados) {
        const cuotasDelPrestamo = prestamosAgrupados[clavePrestamo];
        cuotasDelPrestamo.sort((a, b) => a.numero_cuota - b.numero_cuota);

        let capitalRestante = parseFloat(cuotasDelPrestamo[0].monto_a_financiar || 0);

        cuotasDelPrestamo.forEach(cuota => {
          if (capitalRestante < 0) capitalRestante = 0;

          const interesCalculado = (capitalRestante * parseFloat(cuota.interes_mensual || 0)) / 100;
          let pagoCapital = parseFloat(cuota.monto_cuota || 0) - interesCalculado;

          if (pagoCapital > capitalRestante) {
            pagoCapital = capitalRestante;
          }

          const capitalAntesDelPago = capitalRestante;
          capitalRestante -= pagoCapital;

          const cuotaConCalculos = {
            ...cuota,
            interes_calculado: interesCalculado,
            pago_capital: pagoCapital,
            monto_a_financiar_calculado: capitalAntesDelPago,
            saldo: parseFloat(cuota.monto_cuota || 0) - parseFloat(cuota.abono_total || 0)
          };
          cuotasProcesadas.push(cuotaConCalculos);
        });
      }

      cuotasProcesadas.sort((a, b) => {
        const fechaA = new Date(a.fecha_vencimiento + 'T00:00:00');
        const fechaB = new Date(b.fecha_vencimiento + 'T00:00:00');
        if (fechaA.getTime() !== fechaB.getTime()) {
          return fechaA.getTime() - fechaB.getTime();
        }
        return a.numero_cuota - b.numero_cuota;
      });

      return cuotasProcesadas;
    });

    const infoResumenPrestamo = computed(() => {
      // ... (Tu lógica de resumen permanece igual) ...
      if (listaCuotasProcesada.value && listaCuotasProcesada.value.length > 0) {
        const primeraCuota = listaCuotasProcesada.value[0];
        return {
          rut_cliente: primeraCuota.rut_cliente,
          nombres: primeraCuota.nombres,
          apellidos: primeraCuota.apellidos,
          patente: primeraCuota.patente,
          numero_cuotas: primeraCuota.numero_cuotas,
          precio_venta: primeraCuota.precio_venta,
          interes_mensual: primeraCuota.interes_mensual,
          precio_venta: primeraCuota.precio_venta || 0,
          monto_a_financiar: primeraCuota.monto_a_financiar || 0,
          valor_pie: primeraCuota.valor_pie || 0,
          fecha_creacion: primeraCuota.fecha_creacion || 0,
        };
      }
      return null;
    });


    const totalesGenerales = computed(() => {
      // ... (Tu lógica de totales abonados permanece igual) ...
      const totales = {
        totalInteres: 0,
        totalCapitalAmortizado: 0,
        totalMontoCuota: 0,
        totalAbonado: 0,
        totalSaldo: 0,
      };

      const lista = listaCuotasProcesada.value;

      lista.forEach(cuota => {
        const abonoReal = parseFloat(cuota.abono_total) || 0;
        totales.totalAbonado += abonoReal;
        totales.totalSaldo += (cuota.abono_total > cuota.pago_capital +
          cuota.interes_calculado ? (cuota.abono_total -
            cuota.pago_capital +
            cuota.interes_calculado) : 0) || 0;

        if (abonoReal > 0) {
          totales.totalInteres += cuota.interes_calculado || 0;
          totales.totalCapitalAmortizado += cuota.pago_capital || 0;
          totales.totalMontoCuota += parseFloat(cuota.monto_cuota) || 0;
        }
      });

      return totales;
    });

    const totalesGeneralesPendientes = computed(() => {
      // ... (Tu lógica de totales pendientes permanece igual) ...
      const totales = {
        totalInteres: 0,
        totalCapitalAmortizado: 0,
        totalMontoCuota: 0,
        totalCuota: 0,
        totalSaldo: 0,
      };

      const lista = listaCuotasProcesada.value;

      lista.forEach(cuota => {
        const abonoReal = parseFloat(cuota.abono_total) || 0;

        if (abonoReal === 0) {
          totales.totalInteres += cuota.interes_calculado || 0;
          totales.totalCapitalAmortizado += cuota.pago_capital || 0;
          totales.totalMontoCuota += parseFloat(cuota.monto_cuota) || 0;
          totales.totalCuota += (cuota.interes_calculado || 0) + (cuota.pago_capital || 0);
        }
        totales.totalSaldo += cuota.saldo || 0;
      });

      return totales;
    });


    onMounted(() => {
      // Dejar vacío
    });

    return {
      isLoading,
      mensaje,
      tipoMensaje,
      // --- Exportar nuevas propiedades y funciones ---
      terminoBusqueda,
      resultadosBusqueda,
      isLoadingSearch,
      creditoSeleccionado,
      buscarCoincidencias,
      seleccionarCreditoYGenerarInforme,
      reiniciarBusqueda,
      // --- Exportar el resto ---
      formatearMilesConPunto,
      formatearFecha,
      listaCuotasProcesada,
      totalesGenerales,
      totalesGeneralesPendientes,
      infoResumenPrestamo,
    };
  },
};
</script>

<template>
  <Header></Header>

  <div class="container-fluid mt-3">
    <div class="card shadow-sm">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
        Informe de Pagos Simplificado
      </div>
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-12">
            <label for="buscador" class="form-label negrita">Buscar Cliente o Crédito:</label>
            <div class="input-group">
              <input type="text" class="form-control" id="buscador" v-model="terminoBusqueda"
                @input="buscarCoincidencias" @focus="creditoSeleccionado ? reiniciarBusqueda() : null"
                placeholder="Buscar por RUT, Patente o Nombres (mínimo 3 caracteres)..." autocomplete="off"
                :disabled="creditoSeleccionado" />
              <button v-if="creditoSeleccionado" class="btn btn-outline-secondary" @click="reiniciarBusqueda">
                Nueva Búsqueda
              </button>
            </div>

            <div class="position-relative">
              <div v-if="!isLoadingSearch && resultadosBusqueda.length > 0 && terminoBusqueda.length >= 3"
                class="list-group position-absolute w-100 shadow-sm" style="z-index: 1000;">
                <button type="button" class="list-group-item list-group-item-action"
                  v-for="credito in resultadosBusqueda" :key="credito.rut_cliente + credito.patente"
                  @click="seleccionarCreditoYGenerarInforme(credito)">
                  <span class="negrita">{{ credito.nombres_completos }} - {{ credito.apellidos_cliente }}</span> <br>
                  <small>RUT: {{ credito.rut_cliente }} - Patente: {{ credito.patente }} </small>

                </button>
              </div>
              <div v-if="isLoadingSearch" class="list-group position-absolute w-100 shadow-sm" style="z-index: 1000;">
                <span class="list-group-item">Buscando coincidencias...</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="creditoSeleccionado">

          <div v-if="isLoading" class="text-center">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Cargando informe...</span>
            </div>

          </div>

          <div v-else>

            <div v-if="infoResumenPrestamo" class="card shadow-sm my-4">
              <div class="card-header bg-secondary text-white">
                <h5 class="mb-0">Información Cliente/Crédito</h5>
              </div>
              <div class="card-body" style="font-size: medium;">
                <div class="row">
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Nombres:</p><span>{{ infoResumenPrestamo.nombres }} {{
                      infoResumenPrestamo.apellidos }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">RUT:</p><span>{{ infoResumenPrestamo.rut_cliente }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Patente:</p><span>{{ infoResumenPrestamo.patente }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Fecha Crédito:</p><span>{{
                      formatearFecha(infoResumenPrestamo.fecha_creacion) }}</span>
                  </div>
                </div>
                <hr>
                <div class="row mt-2">
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Tasa Interes:</p><span> {{ infoResumenPrestamo.interes_mensual }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Precio de Venta:</p><span>$ {{
                      formatearMilesConPunto(infoResumenPrestamo.precio_venta) }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Pie:</p><span>$ {{ formatearMilesConPunto(infoResumenPrestamo.valor_pie)
                    }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Capital Otorgado:</p><span>$ {{
                      formatearMilesConPunto(infoResumenPrestamo.monto_a_financiar) }}</span>
                  </div>
                  <div class="col-md-3">
                    <p class="mb-1 negrita">Total Cuotas:</p><span>{{
                      formatearMilesConPunto(infoResumenPrestamo.numero_cuotas) }} </span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="mensaje" class="alert"
              :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error', 'alert-info': tipoMensaje === 'info' }"
              role="alert">
              {{ mensaje }}
            </div>

            <div v-if="listaCuotasProcesada.length === 0 && !isLoading" class="text-center">
              No se encontraron cuotas para el crédito seleccionado.
            </div>

            <div v-else class="mt-4">
              <div class="card shadow-sm mb-4">
                <div class="card-header bg-light">
                  <h5 class="mb-0">Listado de Cuotas (Amortización Completa)</h5>
                </div>
                <div class="card-body p-0">
                  <div class="table-responsive">
                    <table class="table table-striped table-hover custom-table mb-0">
                      <thead>
                        <tr>

                          <th style="text-align: center"># Cuota</th>
                          <th style="text-align: center">Fecha Vencimiento</th>
                          <th style="text-align: center">Capital Adeudado</th>

                          <th style="text-align: center">Interés Calculado</th>
                          <th style="text-align: center">Amortización Capital</th>
                          <th style="text-align: center">Monto Cuota</th>

                          <th style="text-align: center">Monto Abonado</th>
                          <th style="text-align: center">Interés Cob.</th>
                          <th style="text-align: center">Estado</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="cuota in listaCuotasProcesada" :key="cuota.id">

                          <td style="text-align: center">{{ cuota.numero_cuota }}</td>
                          <td style="text-align: center">{{ formatearFecha(cuota.fecha_vencimiento) }}</td>
                          <td style="text-align: center">{{ formatearMilesConPunto(cuota.monto_a_financiar_calculado) }}
                          </td>

                          <td style="text-align: center">{{ formatearMilesConPunto(cuota.interes_calculado) }}</td>
                          <td style="text-align: center">{{ formatearMilesConPunto(cuota.pago_capital) }}</td>
                          <td style="text-align: center">{{ formatearMilesConPunto(cuota.pago_capital +
                            cuota.interes_calculado) }}</td>

                          <td style="text-align: center">{{ formatearMilesConPunto(cuota.abono_total) }}</td>

                          <td style="text-align: center">
                            {{ formatearMilesConPunto(cuota.abono_total > cuota.pago_capital +
                              cuota.interes_calculado ? (cuota.abono_total -
                                cuota.pago_capital +
                                cuota.interes_calculado) : 0) }}
                          </td>

                          <td style="text-align: center">
                            <img v-if="parseFloat(cuota.abono_total || 0) >= parseFloat(cuota.monto_cuota || 0)"
                              src="../img/visto.png" alt="Abono Completo" width="20" height="20" />
                            <img v-else-if="parseFloat(cuota.abono_total || 0) > 0" />
                            <img v-else src="../img/x.png" alt="Pendiente" width="20" height="20" />
                          </td>
                        </tr>
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colspan="3" class="text-end negrita">Total General **Abonado** del Informe:</td>

                          <td class="negrita text-center">{{ formatearMilesConPunto(totalesGenerales.totalInteres) }}
                          </td>
                          <td class="negrita text-center">{{
                            formatearMilesConPunto(totalesGenerales.totalCapitalAmortizado) }}</td>
                          <td class="negrita text-center">{{
                            formatearMilesConPunto(totalesGenerales.totalCapitalAmortizado +
                              totalesGenerales.totalInteres) }}</td>
                          <td class="negrita text-center">{{ formatearMilesConPunto(totalesGenerales.totalAbonado) }}
                          </td>
                          <td class="negrita text-center">{{ formatearMilesConPunto(totalesGenerales.totalSaldo) }}</td>

                          <td colspan="1"></td>

                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mt-5">
              <div class="col-12">
                <div class="card shadow-sm">
                  <div class="card-header bg-success text-white">
                    <h4 class="mb-0">Resumen Total del Informe (Solo Pagos Realizados)</h4>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Utilidad Total **Abonada**:</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalInteres) }}</h5>
                      </div>
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Total Capital **Amortizado**:</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalCapitalAmortizado) }}</h5>
                      </div>
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Suma Total **Abonada** (Real):</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalAbonado) }}</h5>
                      </div>
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Saldo Total **Pendiente** (Cuotas):</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGenerales.totalSaldo) }}</h5>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mt-5">
              <div class="col-12">
                <div class="card shadow-sm">
                  <div class="card-header bg-danger text-white">
                    <h4 class="mb-0">Resumen Total del Informe (Cuotas NO Abonadas)</h4>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Interés Teórico **Pendiente**:</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalInteres) }}</h5>
                      </div>
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Capital Teórico **Pendiente**:</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalCapitalAmortizado) }}</h5>
                      </div>
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Monto Total Cuota **Pendiente**:</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalCuota) }}</h5>
                      </div>
                      <div class="col-md-3">
                        <p class="mb-1 negrita">Saldo Total **Pendiente** (General):</p>
                        <h5>$ {{ formatearMilesConPunto(totalesGeneralesPendientes.totalSaldo) }}</h5>
                      </div>
                    </div>
                    <p class="mt-3 text-muted">
                      *Este resumen considera la suma de Interés y Capital teórico solo para las cuotas donde el abono
                      total es **cero**.
                      El Saldo Total Pendiente (General) incluye todos los saldos, incluso abonos parciales.
                    </p>
                  </div>
                </div>
              </div>
            </div>


          </div>
        </div>

        <div v-if="!creditoSeleccionado && !terminoBusqueda" class="text-center text-muted mt-5">
          <p>Utilice el campo de búsqueda para encontrar un crédito y generar el informe.</p>
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

/* Estilos adicionales para la lista de sugerencias */
.list-group.position-absolute {
  border-top: none;
  border-radius: 0 0 .25rem .25rem;
  max-height: 300px;
  overflow-y: auto;
}

.list-group-item-action {
  cursor: pointer;
}

.list-group-item-action:hover {
  background-color: #f8f9fa;
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