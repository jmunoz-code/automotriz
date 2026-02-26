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

            // Nivel del usuario
            const nivel = ref(localStorage.getItem('user_nivel'));

            const filtroRutCuota = ref('');
            const filtroPatenteCuota = ref('');
            const mostrarHistorico = ref(false);

            const showModal = ref(false);
            const showModal1 = ref(false);

            const clienteSeleccionado = ref(null); // Estado para manejar la vista detallada
            const cuotaParaEditar = ref({});
            // const mostrarSoloMora = ref(true); // Ya no se usa explícitamente con switch, es implícito en la vista principal


            const cuotasSeleccionadas = ref([]);

            const eliminarSeleccionadas = async () => {
              if (cuotasSeleccionadas.value.length === 0) {
                mostrarMensaje('No hay cuotas seleccionadas.', 'warning');
                return;
              }

              if (!confirm(`¿Está seguro de que desea eliminar las ${cuotasSeleccionadas.value.length} cuotas seleccionadas? Esta acción no se puede deshacer.`)) {
                return;
              }

              isLoading.value = true;
              let nExitos = 0;
              let nErrores = 0;

              const ids = [...cuotasSeleccionadas.value];

              const promises = ids.map(async (id) => {
                try {
                  const apiUrl = `${import.meta.env.VITE_API_URL}pagocuotas/eliminar_por_id/${id}/`;
                  const response = await fetch(apiUrl, {
                    method: 'DELETE',
                  });
                  if (response.ok) return true;
                  return false;
                } catch (e) {
                  return false;
                }
              });

              const results = await Promise.all(promises);
              nExitos = results.filter((r) => r).length;
              nErrores = results.filter((r) => !r).length;

              isLoading.value = false;
              cuotasSeleccionadas.value = []; // Limpiar selección
              cargarListaDeCuotas(); // Recargar lista

              if (nErrores === 0) {
                mostrarMensaje(`Se eliminaron ${nExitos} cuotas exitosamente.`, 'success');
              } else {
                mostrarMensaje(`Se eliminaron ${nExitos} cuotas. Hubo error en ${nErrores}.`, 'warning');
              }
            };

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
              // Asumimos formato YYYY-MM-DD que viene del backend
              const partes = fechaISO.toString().slice(0, 10).split('-');
              if (partes.length === 3) {
                const [year, month, day] = partes;
                return `${day}-${month}-${year}`;
              }
              return fechaISO;
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

                // Agregar parámetro histórico según el checkbox
                params.append('historico', mostrarHistorico.value ? 'true' : 'false');

                if (filtroRutCuota.value) {
                  params.append('rut_cliente', filtroRutCuota.value);
                }
                if (filtroPatenteCuota.value) {
                  params.append('patente', filtroPatenteCuota.value);
                }

                apiUrl += `?${params.toString()}`;

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
              if (nivel.value !== 'ADMIN') {
                mostrarMensaje('Acción no permitida. Solo administradores pueden modificar el monto.', 'error');
                return;
              }
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
                mostrarMensaje('Error al actualizar la cuota.', 'error');
              }
            };

            const actualizarInteresMora = async (cuotaId, nuevoMonto) => {

              // Asegurar que el valor sea un número entero
              let montoEntero = Math.round(parseFloat(nuevoMonto));

              // Si no es un número válido (ej. vacío), enviar null o 0 según corresponda. 
              // Asumiremos 0 si es inválido para mantener consistencia numérica, o null si el backend lo prefiere.
              if (isNaN(montoEntero)) {
                montoEntero = 0;
              }

              try {
                const url = `${import.meta.env.VITE_API_URL}pagocuotas/modificar_cuota/${cuotaId}/`;

                const response = await fetch(url, {
                  method: 'PATCH',
                  headers: {
                    'Content-Type': 'application/json'
                  },
                  body: JSON.stringify({
                    interes_mora: montoEntero
                  })
                });

                if (!response.ok) {
                  throw new Error(`Error al actualizar interés mora: ${response.statusText}`);
                }

                mostrarMensaje('Interés por mora actualizado exitosamente.', 'success');
                // cargarListaDeCuotas(); // Opcional, si quieres refrescar

              } catch (error) {
                console.error('Error:', error);
                mostrarMensaje('Error al actualizar el interés por mora.', 'error');
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

              // Ya no filtramos por estado aquí, el backend se encarga según el parámetro 'historico'
              const cuotasFiltradas = listaCuotas.value;

              let capitalRestante = 0;
              let lastRut = null;
              let lastPatente = null;

              // Se usa .map() para crear un nuevo array con los cálculos
              return cuotasFiltradas.map((cuota, index) => {
                const nuevaCuota = { ...cuota };

                // Condición para reiniciar el cálculo: si el RUT o la patente cambian.
                if (index === 0 || nuevaCuota.rut_cliente !== lastRut || nuevaCuota.patente !== lastPatente) {
                  capitalRestante = parseFloat(nuevaCuota.monto_a_financiar);
                }

                // Calcula el interés de la cuota actual en base al capital restante.
                const interesMensual = parseFloat(nuevaCuota.interes_mensual) || 0;
                const interesCalculado = capitalRestante > 0 ? (capitalRestante * interesMensual) / 100 : 0;
                nuevaCuota.interes_calculado = interesCalculado;

                // Determinar el monto efectivo para el cálculo (si se abonó más que la cuota, se usa el abono)
                const montoCuota = parseFloat(nuevaCuota.monto_cuota) || 0;
                const abonoTotal = parseFloat(nuevaCuota.abono_total) || 0;
                const pagoEfectivo = Math.max(montoCuota, abonoTotal);

                // Calcula el pago de capital de la cuota actual.
                const pagoCapital = pagoEfectivo - interesCalculado;
                nuevaCuota.pago_capital = pagoCapital;

                // Asigna el capital restante actual a la propiedad de la cuota.
                nuevaCuota.monto_a_financiar_calculado = Math.abs(capitalRestante);

                // Actualiza el capital restante para la siguiente iteración.
                capitalRestante -= pagoCapital;

                // Almacena los valores de la fila actual para la próxima comparación.
                lastRut = nuevaCuota.rut_cliente;
                lastPatente = nuevaCuota.patente;

                // Cálculo de días de atraso
                const fechaVenc = new Date(nuevaCuota.fecha_vencimiento);
                const hoy = new Date();
                const diffTime = hoy - fechaVenc;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                nuevaCuota.dias_atraso = diffDays > 0 ? diffDays : 0;

                return nuevaCuota;
              });
            });

            // --- LÓGICA DE AGRUPACIÓN PARA LA VISTA PRINCIPAL ---
            // Muestra clientes con cuotas pendientes (pagadas parcialmente o no pagadas)
            const clientesEnMora = computed(() => {
              const grupos = new Map();
              const cuotas = cuotasConCalculoDeCapital.value;


              cuotas.forEach((cuota) => {
                const key = `${cuota.rut_cliente}-${cuota.patente}`;

                if (!grupos.has(key)) {
                  grupos.set(key, {
                    rut_cliente: cuota.rut_cliente,
                    nombres: cuota.nombres,
                    apellidos: cuota.apellidos,
                    patente: cuota.patente,
                    tiene_deuda: false,
                    // Guardamos referencia para mostrar datos básicos
                  });
                }

                const grupo = grupos.get(key);

                // Verificación de cuotas pendientes (con saldo > 0 y mora >= 1 día)
                const monto = parseFloat(cuota.monto_cuota) || 0;
                const abono = parseFloat(cuota.abono_total) || 0;
                const saldo = monto - abono;
                const dias_atraso = parseInt(cuota.dias_atraso) || 0;

                // Solo si el saldo > 0 y tiene al menos 1 día de mora
                if (saldo > 0 && dias_atraso >= 1) {
                  grupo.tiene_deuda = true;
                }
              });


              // Retornar grupos
              const resultados = Array.from(grupos.values());

              // Si hay filtros activos (RUT o Patente) o modo Histórico, mostramos TODOS los resultados encontrados
              // independientemente de si tienen deuda o no. Así el usuario puede "buscar" un cliente al día.
              if (mostrarHistorico.value || filtroRutCuota.value || filtroPatenteCuota.value) {
                return resultados;
              }
              // En la vista general (sin filtros), solo mostramos los que tienen deuda pendiente
              return resultados.filter(g => g.tiene_deuda);

            });

            // --- CUOTAS DEL CLIENTE SELECCIONADO (DETALLE) ---
            const cuotasDeClienteSeleccionado = computed(() => {
              if (!clienteSeleccionado.value) return [];
              return cuotasConCalculoDeCapital.value.filter(c =>
                c.rut_cliente === clienteSeleccionado.value.rut_cliente &&
                c.patente === clienteSeleccionado.value.patente
              );
            });

            const verDetalleCliente = (cliente) => {
              clienteSeleccionado.value = cliente;
            };

            const volverALista = () => {
              clienteSeleccionado.value = null;
              cuotasSeleccionadas.value = []; // Limpiar selección al volver
            };

            const cambiarEstadoPresupuesto = async () => {
              if (!clienteSeleccionado.value) return;

              try {
                const nuevoEstado = mostrarHistorico.value ? 1 : 0;
                const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/${clienteSeleccionado.value.rut_cliente}/${clienteSeleccionado.value.patente}/`;

                const response = await fetch(apiUrl, {
                  method: 'PATCH',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({ estado: nuevoEstado }),
                });

                if (response.ok) {
                  const mensaje = nuevoEstado === 1
                    ? 'Contrato movido al histórico exitosamente.'
                    : 'Contrato reactivado exitosamente.';
                  mostrarMensaje(mensaje, 'success');

                  // Recargar las cuotas para reflejar el cambio
                  await cargarListaDeCuotas();

                  // Volver a la lista principal
                  volverALista();
                } else {
                  const errorData = await response.json();
                  console.error('Error al actualizar el estado del presupuesto:', errorData);
                  mostrarMensaje('Error al actualizar el estado del presupuesto.', 'error');
                  // Revertir el checkbox si falla
                  mostrarHistorico.value = !mostrarHistorico.value;
                }
              } catch (error) {
                console.error('Error de conexión al actualizar estado:', error);
                mostrarMensaje('Error de conexión al actualizar el estado.', 'error');
                // Revertir el checkbox si falla
                mostrarHistorico.value = !mostrarHistorico.value;
              }
            };

            watch([filtroRutCuota, filtroPatenteCuota, mostrarHistorico], () => {
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
              cuotasConCalculoDeCapital,
              grabarEdicionCuota,
              actualizarInteresMora,
              nivel,
              clientesEnMora,
              clienteSeleccionado,
              cuotasDeClienteSeleccionado,
              verDetalleCliente,
              volverALista,
              mostrarHistorico,
              cambiarEstadoPresupuesto,
              cuotasSeleccionadas,
              eliminarSeleccionadas,
              calcularPagoCapital: (cuota) => {
                const monto = parseFloat(cuota.monto_cuota) || 0;
                const abono = parseFloat(cuota.abono_total) || 0;
                const interes = parseFloat(cuota.interes_calculado) || 0;
                // Usa el pago efectivo (el mayor entre monto y abono)
                const pagoEfectivo = Math.max(monto, abono);
                return pagoEfectivo - interes;
              },
              calcularTotalPago: (cuota) => {
                const capital = parseFloat(cuota.monto_a_financiar_calculado) || 0;
                const interes = parseFloat(cuota.interes_calculado) || 0;
                return capital + interes;
              },
              calcularSaldo: (cuota) => {
                const monto = parseFloat(cuota.monto_cuota) || 0;
                const abono = parseFloat(cuota.abono_total) || 0;
                // Si abonó igual o más que la cuota, el saldo es 0
                // Si abonó menos, el saldo es la diferencia
                return abono >= monto ? 0 : monto - abono;
              },
              totalCapital: computed(() => {
                // El capital total debe ser el de la última cuota (capital restante)
                const cuotas = cuotasDeClienteSeleccionado.value;
                if (cuotas.length === 0) return 0;
                const ultimaCuota = cuotas[cuotas.length - 1];
                // Calcular el capital restante: capital actual - amortización de esta cuota
                const capitalActual = parseFloat(ultimaCuota.monto_a_financiar_calculado) || 0;
                const monto = parseFloat(ultimaCuota.monto_cuota) || 0;
                const abono = parseFloat(ultimaCuota.abono_total) || 0;
                const interes = parseFloat(ultimaCuota.interes_calculado) || 0;
                const pagoEfectivo = Math.max(monto, abono);
                const amortizacion = pagoEfectivo - interes;
                return capitalActual - amortizacion;
              }),
              totalInteres: computed(() => {
                // El interés total debe ser el interés calculado sobre el capital restante
                const cuotas = cuotasDeClienteSeleccionado.value;
                if (cuotas.length === 0) return 0;
                const ultimaCuota = cuotas[cuotas.length - 1];

                // Calcular el capital restante
                const capitalActual = parseFloat(ultimaCuota.monto_a_financiar_calculado) || 0;
                const monto = parseFloat(ultimaCuota.monto_cuota) || 0;
                const abono = parseFloat(ultimaCuota.abono_total) || 0;
                const interes = parseFloat(ultimaCuota.interes_calculado) || 0;
                const pagoEfectivo = Math.max(monto, abono);
                const amortizacion = pagoEfectivo - interes;
                const capitalRestante = capitalActual - amortizacion;

                // Calcular el interés sobre el capital restante
                const tasaInteres = parseFloat(ultimaCuota.interes_mensual) || 0;
                return capitalRestante > 0 ? (capitalRestante * tasaInteres) / 100 : 0;
              }),
              totalAmortizacion: computed(() => {
                return cuotasDeClienteSeleccionado.value.reduce((sum, cuota) => {
                  const monto = parseFloat(cuota.monto_cuota) || 0;
                  const abono = parseFloat(cuota.abono_total) || 0;
                  const interes = parseFloat(cuota.interes_calculado) || 0;
                  const pagoEfectivo = Math.max(monto, abono);
                  return sum + (pagoEfectivo - interes);
                }, 0);
              }),
              totalCapitalInteres: computed(() => {
                // Debe ser la suma del total de capital + total de interés
                const cuotas = cuotasDeClienteSeleccionado.value;
                if (cuotas.length === 0) return 0;

                // Calcular capital restante
                const ultimaCuota = cuotas[cuotas.length - 1];
                const capitalActual = parseFloat(ultimaCuota.monto_a_financiar_calculado) || 0;
                const monto = parseFloat(ultimaCuota.monto_cuota) || 0;
                const abono = parseFloat(ultimaCuota.abono_total) || 0;
                const interes = parseFloat(ultimaCuota.interes_calculado) || 0;
                const pagoEfectivo = Math.max(monto, abono);
                const amortizacion = pagoEfectivo - interes;
                const capitalRestante = capitalActual - amortizacion;

                // Calcular interés sobre capital restante
                const tasaInteres = parseFloat(ultimaCuota.interes_mensual) || 0;
                const interesCalculado = capitalRestante > 0 ? (capitalRestante * tasaInteres) / 100 : 0;

                return capitalRestante + interesCalculado;
              }),
              totalMontoCuota: computed(() => {
                return cuotasDeClienteSeleccionado.value.reduce((sum, cuota) => {
                  return sum + (parseFloat(cuota.monto_cuota) || 0);
                }, 0);
              }),
              totalInteresMora: computed(() => {
                return cuotasDeClienteSeleccionado.value.reduce((sum, cuota) => {
                  return sum + (parseFloat(cuota.interes_mora) || 0);
                }, 0);
              }),
              totalAbonado: computed(() => {
                return cuotasDeClienteSeleccionado.value.reduce((sum, cuota) => {
                  return sum + (parseFloat(cuota.abono_total) || 0);
                }, 0);
              }),
              totalSaldo: computed(() => {
                return cuotasDeClienteSeleccionado.value.reduce((sum, cuota) => {
                  const monto = parseFloat(cuota.monto_cuota) || 0;
                  const abono = parseFloat(cuota.abono_total) || 0;
                  const saldo = abono >= monto ? 0 : monto - abono;
                  return sum + saldo;
                }, 0);
              })
            };
          }
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
        <div class="row mb-4" v-if="!clienteSeleccionado">
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
            <div class="form-check d-flex align-items-center me-3 checkbox-historico">
              <input type="checkbox" class="form-check-input checkbox-large" id="checkHistorico"
                v-model="mostrarHistorico">
              <label class="form-check-label negrita ms-2" for="checkHistorico">
                Histórico
              </label>
            </div>
            <button class="btn btn-primary btn-sm me-2" @click="cargarListaDeCuotas" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Cargando...' : 'Buscar Cuotas' }}
            </button>


          </div>
        </div>

        <div v-if="!clienteSeleccionado" class="table-responsive">
          <h5 class="mb-3 text-secondary">Clientes con Cuotas Pendientes</h5>
          <table class="table table-striped table-hover custom-table">
            <thead>
              <tr>
                <th style="text-align: center">RUT</th>
                <th style="text-align: center">Nombre</th>
                <th style="text-align: center">Apellido</th>
                <th style="text-align: center">Patente</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="clientesEnMora.length === 0 && !isLoading">
                <td colspan="4" class="text-center">No se encontraron clientes con cuotas pendientes.</td>
              </tr>
              <tr v-else-if="isLoading">
                <td colspan="4" class="text-center">Cargando...</td>
              </tr>
              <tr v-for="grupo in clientesEnMora" :key="grupo.rut_cliente + grupo.patente"
                @click="verDetalleCliente(grupo)" style="cursor: pointer;">
                <td style="text-align: center">{{ grupo.rut_cliente }}</td>
                <td style="text-align: center">{{ grupo.nombres }}</td>
                <td style="text-align: center">{{ grupo.apellidos }}</td>
                <td style="text-align: center">{{ grupo.patente }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- VISTA NIVEL 2: DETALLE DE CUOTAS DEL CLIENTE SELECCIONADO -->
        <div v-else>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="d-flex align-items-center">
              <h5 class="text-secondary mb-0 me-3">
                Detalle de Cuotas: {{ clienteSeleccionado.nombres }} {{ clienteSeleccionado.apellidos }} ({{
                  clienteSeleccionado.rut_cliente }} - {{
                  clienteSeleccionado.patente }})
              </h5>
              <!-- Solo mostrar checkbox si se está viendo el histórico -->
              <div v-if="mostrarHistorico" class="form-check d-flex align-items-center checkbox-historico-detalle">
                <input type="checkbox" class="form-check-input checkbox-large" id="checkHistoricoDetalle"
                  v-model="mostrarHistorico" @change="cambiarEstadoPresupuesto" :disabled="nivel !== 'ADMIN'">
                <label class="form-check-label negrita ms-2" for="checkHistoricoDetalle">
                  Histórico
                </label>
              </div>
            </div>
            <button class="btn btn-danger btn-sm me-2" @click="eliminarSeleccionadas"
              :disabled="isLoading || cuotasSeleccionadas.length === 0">
              Eliminar Seleccionadas ({{ cuotasSeleccionadas.length }})
            </button>
            <button class="btn btn-secondary btn-sm" @click="volverALista">
              <i class="fas fa-arrow-left"></i> Volver a la Lista
            </button>
          </div>

          <div class="table-wrapper">
            <table class="table table-striped table-hover custom-table">
              <thead class="sticky-header">
                <tr>
                  <th style="text-align: center" v-if="!mostrarHistorico">Sel.</th>
                  <th style="text-align: center"># Cuota</th>
                  <th style="text-align: center">Fecha Vencimiento</th>
                  <th style="text-align: center">Capital</th>
                  <th style="text-align: center">Tasa</th>
                  <th style="text-align: center">Interes</th>
                  <th style="text-align: center">Amortizacion Capital</th>
                  <th style="text-align: center">Capital + Interés</th>
                  <th style="text-align: center">Monto Cuota</th>
                  <th style="text-align: center">Interés Mora</th>
                  <th style="text-align: center">Monto Abonado</th>
                  <th style="text-align: center">Saldo</th>
                  <th style="text-align: center">Estado</th>
                  <th style="text-align: center">Observación</th>
                  <th v-if="!mostrarHistorico">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="cuota in cuotasDeClienteSeleccionado" :key="cuota.id" style="cursor: pointer;">
                  <td style="text-align: center; vertical-align: middle;" v-if="!mostrarHistorico">
                    <div class="d-flex justify-content-center align-items-center"
                      style="height: 100%; min-height: 40px;">
                      <input type="checkbox" :value="cuota.id" v-model="cuotasSeleccionadas"
                        class="form-check-input checkbox-large" style="margin: 0 !important;" @click.stop />
                    </div>
                  </td>
                  <td style="text-align: center">{{ cuota.numero_cuota }}</td>
                  <td style="text-align: center">{{ formatearFecha(cuota.fecha_vencimiento) }}</td>
                  <td style="text-align: center">{{ formatearMilesConPunto(cuota.monto_a_financiar_calculado, 2) }}</td>
                  <td style="text-align: center">{{ cuota.interes_mensual }}</td>
                  <td style="text-align: center">{{ formatearMilesConPunto(cuota.interes_calculado, 2) }}</td>
                  <td style="text-align: center">{{ formatearMilesConPunto(calcularPagoCapital(cuota), 2) }}</td>
                  <td style="text-align: center">{{ formatearMilesConPunto(calcularTotalPago(cuota),
                    2) }}</td>

                  <td style="text-align: center">
                    <input type="number" v-model="cuota.monto_cuota"
                      @blur="grabarEdicionCuota(cuota.id, cuota.monto_cuota)" class="form-control form-control-sm"
                      style="width: 120px; text-align: center;" :disabled="nivel !== 'ADMIN'" />

                  </td>
                  <td style="text-align: center">
                    <input type="number" v-model="cuota.interes_mora"
                      @blur="actualizarInteresMora(cuota.id, cuota.interes_mora)" class="form-control form-control-sm"
                      style="width: 120px; text-align: center; margin: 0 auto;" />
                  </td>
                  <td style="text-align: center">{{ formatearMilesConPunto(cuota.abono_total) }} </td>
                  <td style="text-align: center">{{ formatearMilesConPunto(calcularSaldo(cuota)) }}
                  </td>
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
                  <td v-if="!mostrarHistorico" style="min-width: 310px;">
                    <button class="btn btn-info btn-sm me-1" @click.stop="abrirModalGrabar(cuota)">
                      Abonar
                    </button>
                    &nbsp;
                    <button class="btn btn-secondary btn-sm me-1" @click.stop="abrirModalEdicion(cuota)">
                      Abonos
                    </button>
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr style="background-color: #f8f9fa; font-weight: bold; border-top: 2px solid #dee2e6;">
                  <td v-if="!mostrarHistorico"></td>
                  <td style="text-align: center">TOTAL</td>
                  <td></td>
                  <td style="text-align: center">{{ formatearMilesConPunto(totalCapital, 2) }}</td>
                  <td></td>
                  <td style="text-align: center">{{ formatearMilesConPunto(totalInteres, 2) }}</td>
                  <td style="text-align: center">{{ formatearMilesConPunto(totalAmortizacion, 2) }}</td>
                  <td style="text-align: center">{{ formatearMilesConPunto(totalCapitalInteres, 2) }}</td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td v-if="!mostrarHistorico"></td>
                </tr>
              </tfoot>
            </table>
          </div>
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

/* Contenedor para la tabla con encabezado fijo */
.table-wrapper {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: auto;
  position: relative;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

/* Encabezado sticky */
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8f9fa;
}

.sticky-header th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.1);
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

/* Estilos para el checkbox histórico */
.checkbox-historico {
  margin-bottom: 0 !important;
  padding-bottom: 0.375rem;
  /* Alineación con inputs */
}

.checkbox-large {
  width: 1.25rem !important;
  /* 25% más grande que el tamaño estándar (1rem) */
  height: 1.25rem !important;
  cursor: pointer;
  margin-top: 0 !important;
}

.checkbox-large:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}
</style>