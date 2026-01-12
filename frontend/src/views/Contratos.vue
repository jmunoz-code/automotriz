<script>

import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';

export default {
  components: {
    Header,
    Footer,
  },

  setup() {
    const router = useRouter();

    const formData = ref({
      // ... (todas tus propiedades existentes)
      nombres: null,
      apellidos: null,
      direccion: null,
      telefono: null,
      habilitado: null,
      id: null,
      rut: null,
      patente: null,
      valor_pie: null,
      numero_cuotas: 0,
      fecha: '',
      fecha_creacion: '',
      observacion: null,
      patenteaBuscar: null,
      tipo_automovil: null,
      marca: null,
      modelo: null,
      agno: null,
      numero_motor: null,
      numero_chasis: null,
      color: null,
      kilometraje: null,
      marca_descripcion: null,
      vehiculo_descripcion: null,
      precio_venta: null,
      id_vendedor: null,
      valor_venta_total: null,
      interes_mensual: null,
      valor_cuota: null,
      tipo_pago_seleccionado: 'credito',
    });

    // States for the user interface
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]);
    const rutValido = ref(true);
    const vendedores = ref([]);

    // CORRECCIÓN CLAVE: Declarar 'calculo' como una ref para que sea reactiva
    const calculo = ref(0); // Inicializa calculo con un valor reactivo, por ejemplo 0


    // NUEVAS VARIABLES PARA VEHÍCULOS
    const listaVehiculos = ref([]);
    const mostrarListaVehiculos = ref(false);
    const filtroPatente = ref('');

    // NUEVAS VARIABLES PARA CLIENTES
    const listaClientes = ref([]);
    const mostrarListaClientes = ref(false);
    const filtroRutCliente = ref('');
    const pasa_valor = ref(0);

    // NUEVA VARIABLE PARA FILTRAR CONTRATOS
    const filtroContratos = ref(''); //

    // Nivel del usuario desde localStorage
    const nivel = ref(localStorage.getItem('user_nivel'));

    // --- Funciones auxiliares para formatear y validar ---
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
      const date = new Date(fechaISO);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
    };

    const goToContrato = (contractPatente, id, pagina) => {
      const rutCliente = formData.value.rut;

      if (pagina == 0) {
        router.push({
          name: 'ContratoCompraVenta',
          params: { rut: rutCliente, idPrep: id, patente: contractPatente, pagina }
        });
      }

      if (pagina == 1) {
        router.push({
          name: 'ContratoCompraVenta',
          params: { rut: rutCliente, idPrep: id, patente: contractPatente, pagina }
        });
      }

      if (pagina == 2) {
        router.push({
          name: 'CartaResponsabilidad',
          params: { rut: rutCliente, patente: contractPatente }
        });
      }
    };

    const validarRut = (rut) => {
      if (!rut || typeof rut !== 'string') {
        return false;
      }
      const rutLimpio = rut.replace(/\./g, '').replace('-', '').toUpperCase();
      if (rutLimpio.length < 2) {
        return false;
      }
      const cuerpo = rutLimpio.slice(0, -1);
      const dv = rutLimpio.slice(-1);
      if (!/^[0-9]+$/.test(cuerpo)) {
        return false;
      }
      let suma = 0;
      let factor = 2;
      for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i]) * factor;
        factor = factor === 7 ? 2 : factor + 1;
      }
      const dvCalculado = 11 - (suma % 11);
      const dvEsperado = dvCalculado === 10 ? 'K' : dvCalculado === 11 ? '0' : String(dvCalculado);
      return dv === dvEsperado;
    };

    const handleRutInput = () => {
      console.log('Valor de formData.value.rut antes de limpiar:', formData.value.rut);
      const rutParaValidar = formData.value.rut ? formData.value.rut.trim().replace(/\./g, '').replace('-', '').toUpperCase() : '';
      console.log('Valor de RUT limpio para validar:', rutParaValidar);

      rutValido.value = validarRut(formData.value.rut);
      console.log('Resultado de validarRut:', rutValido.value);

      if (!rutValido.value && formData.value.rut) {
        mostrarMensaje('El RUT ingresado no es válido.', 'error');
      } else if (rutValido.value && formData.value.rut && mensaje.value === 'El RUT ingresado no es válido.') {
        limpiarMensaje();
      }
    };

    const registroAEliminarId = ref(null);
    const mostrarModalEliminar = ref(false);

    const abrirModalEliminar = (id) => {
      registroAEliminarId.value = id;
      mostrarModalEliminar.value = true;
    };

    const cerrarModalEliminar = () => {
      registroAEliminarId.value = null;
      mostrarModalEliminar.value = false;
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

    const formattedValorVentaTotal = computed({
      get() {
        if (formData.value.valor_venta_total === null || formData.value.valor_venta_total === undefined) {
          return '';
        }
        return formatearMilesConPunto(formData.value.valor_venta_total);
      },
      set(newValue) {
        const cleanValue = newValue.replace(/\./g, '').replace(/,/g, '.');
        const numValue = parseFloat(cleanValue);
        if (!isNaN(numValue)) {
          formData.value.valor_venta_total = numValue;
        } else {
          formData.value.valor_venta_total = null;
        }
      }
    });

    const formattedPie = computed({
      get() {
        if (formData.value.valor_pie === null || formData.value.valor_pie === undefined) {
          return '';
        }
        return formatearMilesConPunto(formData.value.valor_pie);
      },
      set(newValue) {
        const cleanValue = newValue.replace(/\./g, '').replace(/,/g, '.');
        const numValue = parseFloat(cleanValue);
        if (!isNaN(numValue)) {
          formData.value.valor_pie = numValue;
        } else {
          formData.value.valor_pie = null;
        }
      }
    });

    const formattedPrecioVenta = computed({
      get() {
        if (formData.value.precio_venta === null || formData.value.precio_venta === undefined) {
          return '';
        }
        return formatearMilesConPunto(formData.value.precio_venta);
      },
      set(newValue) {
        const cleanValue = newValue.replace(/\./g, '').replace(/,/g, '.');
        const numValue = parseFloat(cleanValue);
        if (!isNaN(numValue)) {
          formData.value.precio_venta = numValue;
        } else {
          formData.value.precio_venta = null;
        }
      }
    });

    // MODIFICAR ESTADO DE CONTRATO

    // MODIFICAR ESTADO DE CONTRATO

    const actualizarEstadoContrato = async (contrato) => {
      // Usamos el ID del contrato (presupuesto) para la URL

      const contratoId = contrato.id;


      const nuevoHabilitado = contrato.estado;


      // 💡 Paso 1: Mapear el booleano del Frontend al entero del Backend (1 o 0)
      // El backend espera el campo 'estado' como IntegerField.
      const nuevoEstadoDB = nuevoHabilitado ? 1 : 0;

      if (!contratoId) {
        mostrarMensaje('Error: No se encontró el ID del contrato para actualizar.', 'error');
        return;
      }

      isLoading.value = true;

      // ❌ CORRECCIÓN 1: La URL debe usar el ID y una barra diagonal al final.
      // Antes: presupuesto/estado${contrato}/ 
      // Ahora: presupuesto/estado/ID/
      const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/estado/${contratoId}/`;

      try {
        const response = await fetch(apiUrl, {
          method: 'PATCH', // Es correcto usar PATCH para actualización parcial
          headers: {
            'Content-Type': 'application/json',
          },
          // ❌ CORRECCIÓN 2: El nombre del campo en el body debe ser 'estado' 
          // y el valor debe ser el entero (1 o 0).
          body: JSON.stringify({
            estado: nuevoEstadoDB
          }),
        });

        if (response.ok) {
          // Usa el valor booleano para el mensaje
          mostrarMensaje(`Presupuesto #${contratoId} actualizado a Habilitado: ${nuevoHabilitado ? 'SÍ' : 'NO'}.`, 'success');
          // NO se revierte el estado aquí, ya que el cambio visual fue exitoso
        } else {
          // Si la API falla, revertimos el checkbox al estado anterior
          contrato.habilitado = !nuevoHabilitado;
          const errorData = await response.json();
          console.error('Error al actualizar estado:', response.status, errorData);
          mostrarMensaje('Error al guardar el cambio en el servidor. Revirtiendo estado.', 'error');
        }
      } catch (error) {
        // Si hay error de conexión, revertimos el checkbox
        contrato.habilitado = !nuevoHabilitado;
        console.error('Error de conexión:', error);
        mostrarMensaje('Error de conexión con el servidor. No se pudo guardar.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const obtenerCliente = async (rut) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/${rut}/`;
        console.log('Consulting client at:', apiUrl);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error consulting Client ${rut}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null;
          }
          throw new Error(`Error in query: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        return data.data;
      } catch (error) {
        console.error('Error consulting Client:', error);
        return null;
      }
    };

    const cargarDatosCliente = async (rutABuscar) => {
      if (!rutABuscar) {
        mostrarMensaje('Please enter a RUT to search for the client.', 'error');
        formData.value.nombres = null;
        formData.value.apellidos = null;
        formData.value.direccion = null;
        formData.value.telefono = null;
        formData.value.habilitado = null;
        formData.value.rut = null;
        return;
      }
      try {
        const clienteData = await obtenerCliente(rutABuscar);
        if (clienteData) {
          formData.value.nombres = clienteData.nombres;
          formData.value.apellidos = clienteData.apellidos;
          formData.value.direccion = clienteData.direccion;
          formData.value.telefono = clienteData.fono;
          formData.value.habilitado = clienteData.habilitado;
          formData.value.rut = clienteData.rut;
          console.warn('Client data loaded:', clienteData);
        } else {
          console.warn('No data found for client with RUT:', rutABuscar);
          formData.value.nombres = null;
          formData.value.apellidos = null;
          formData.value.direccion = null;
          formData.value.telefono = null;
          formData.value.habilitado = null;
          formData.value.rut = null;
          mostrarMensaje('Client not found.', 'info');
        }
      } catch (error) {
        console.error('Error loading client data:', error);
        mostrarMensaje('Error loading client data.', 'error');
      }
    };


    const generarCuotas = async (contrato) => {
      const rut_cliente = contrato.rut_cliente;
      const patente = contrato.patente_vehiculo;
      const numero_cuota = contrato.numero_cuotas;
      const monto_prestamo = contrato.precio_venta - contrato.valor_pie;
      const interes_mensual = contrato.interes_mensual;
      const monto_cuota = contrato.valor_cuota;
      const fecha_inicio_pago = contrato.fecha_inicio_pago;

      console.log('Interes contrato.interes_mensual:', interes_mensual);
      console.log('rut cliente:', rut_cliente);

      if (!rut_cliente || !patente || !numero_cuota || !monto_cuota || !fecha_inicio_pago) {
        alert('Faltan datos esenciales para generar las cuotas (RUT, Patente, Cantidad de Cuotas, Monto de Cuota o Fecha Inicial). O Es una venta al contado');
        console.error('Datos faltantes para generar cuotas:', { rut_cliente, patente, numero_cuota, monto_cuota, fecha_inicio_pago, monto_prestamo });
        return;
      }

      const payload = {
        rut_cliente: rut_cliente,
        patente: patente,
        numero_cuota: numero_cuota,
        monto_cuota: monto_cuota,
        fecha_vencimiento: fecha_inicio_pago,
        monto_prestamo: monto_prestamo,
        interes_mensual: interes_mensual
      };

      console.log('Enviando datos al backend para generar cuotas:', payload);
      console.log(`${import.meta.env.VITE_API_URL}pagocuotas/`);

      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}pagocuotas/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || errorData.detail || JSON.stringify(errorData) || 'Error desconocido del servidor.');
        }

        const data = await response.json();
        console.log('Cuotas generadas con éxito:', data);
        alert('Cuotas generadas con éxito.');
      } catch (error) {
        console.error('Error al generar las cuotas:', error);
        alert(`Error al generar las cuotas: ${error.message}`);
      }
    };


    const cargarListaDeClientes = async () => {
      isLoading.value = true;
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}clientes/`;
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          listaClientes.value = data.data;
        } else {
          console.error('Error cargando la lista de clientes:', response.statusText);
          mostrarMensaje('Error cargando la lista de clientes.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión cargando la lista de clientes:', error);
        mostrarMensaje('Error de conexión cargando la lista de clientes.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const seleccionarClienteDeLista = (cliente) => {
      formData.value.rut = cliente.rut;
      formData.value.nombres = cliente.nombres;
      formData.value.apellidos = cliente.apellidos;
      formData.value.direccion = cliente.direccion;
      formData.value.telefono = cliente.fono;
      formData.value.habilitado = cliente.habilitado;
      mostrarListaClientes.value = false;
      mostrarMensaje(`Datos del cliente ${cliente.rut} cargados.`, 'info');
    };

    const clientesFiltrados = computed(() => {
      if (!filtroRutCliente.value) {
        return listaClientes.value;
      }
      const filtro = filtroRutCliente.value.toLowerCase();
      return listaClientes.value.filter(cliente =>
        cliente.rut.toLowerCase().includes(filtro) ||
        (cliente.nombres && cliente.nombres.toLowerCase().includes(filtro)) ||
        (cliente.apellidos && cliente.apellidos.toLowerCase().includes(filtro)) ||
        (cliente.direccion && cliente.direccion.toLowerCase().includes(filtro)) ||
        (cliente.fono && cliente.fono.toLowerCase().includes(filtro))
      );
    });

    const obtenerVehiculo = async (patente) => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/${patente}/`;
        console.log('Consulting vehicle at:', apiUrl);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error consulting Vehicle ${patente}: ${respuesta.status} - ${respuesta.statusText}`);
          if (respuesta.status === 404) {
            return null;
          }
          throw new Error(`Error in Vehicle query: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        return data.data;
      } catch (error) {
        console.error('Error consulting Vehicle:', error);
        return null;
      }
    };

    const cargarDatosVehiculo = async (patenteABuscar) => {
      if (!patenteABuscar) {
        mostrarMensaje('Please enter a license plate to search for the vehicle.', 'error');
        formData.value.modelo = null;
        formData.value.agno = null;
        formData.value.color = null;
        formData.value.marca_descripcion = null;
        formData.value.vehiculo_descripcion = null;
        formData.value.patente = null;
        formData.value.precio_venta = null;
        return;
      }
      try {
        const vehiculoData = await obtenerVehiculo(patenteABuscar);
        if (vehiculoData) {
          formData.value.modelo = vehiculoData.modelo;
          formData.value.agno = vehiculoData.agno;
          formData.value.color = vehiculoData.color;
          formData.value.marca_descripcion = vehiculoData.marca_descripcion;
          formData.value.vehiculo_descripcion = vehiculoData.vehiculo_descripcion;
          formData.value.patente = vehiculoData.patente;
          formData.value.precio_venta = vehiculoData.precio_venta;
          console.warn('Vehicle data loaded:', vehiculoData);
        } else {
          console.warn('No data found for license plate:', patenteABuscar);
          formData.value.modelo = null;
          formData.value.agno = null;
          formData.value.color = null;
          formData.value.marca_descripcion = null;
          formData.value.vehiculo_descripcion = null;
          formData.value.patente = null;
          formData.value.precio_venta = null;
          mostrarMensaje('Vehiculo no encontrado.', 'info');
        }
      } catch (error) {
        console.error('Error loading vehicle data:', error);
        mostrarMensaje('Error loading vehicle data.', 'error');
      }
    };

    const cargarListaDeVehiculos = async () => {
      isLoading.value = true;
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/`;
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          listaVehiculos.value = data.data;
        } else {
          console.error('Error cargando la lista de vehículos:', response.statusText);
          mostrarMensaje('Error cargando la lista de vehículos.', 'error');
        }
      } catch (error) {
        console.error('Error de conexión cargando la lista de vehículos:', error);
        mostrarMensaje('Error de conexión cargando la lista de vehículos.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const seleccionarVehiculoDeLista = (vehiculo) => {
      formData.value.patenteaBuscar = vehiculo.patente;
      formData.value.patente = vehiculo.patente;
      formData.value.tipo_automovil = vehiculo.tipo_automovil;
      formData.value.marca = vehiculo.marca;
      formData.value.modelo = vehiculo.modelo;
      formData.value.agno = vehiculo.agno;
      formData.value.numero_motor = vehiculo.numero_motor;
      formData.value.numero_chasis = vehiculo.numero_chasis;
      formData.value.color = vehiculo.color;
      formData.value.kilometraje = vehiculo.kilometraje;
      formData.value.marca_descripcion = vehiculo.marca_descripcion;
      formData.value.vehiculo_descripcion = vehiculo.vehiculo_descripcion;
      formData.value.precio_venta = vehiculo.precio_venta;
      mostrarListaVehiculos.value = false;
      mostrarMensaje(`Datos del vehículo ${vehiculo.patente} cargados.`, 'info');
    };

    const vehiculosFiltrados = computed(() => {
      if (!filtroPatente.value) {
        return listaVehiculos.value;
      }
      const filtro = filtroPatente.value.toLowerCase();
      return listaVehiculos.value.filter(vehiculo =>
        vehiculo.patente.toLowerCase().includes(filtro) ||
        (vehiculo.tipo_automovil && vehiculo.tipo_automovil.toLowerCase().includes(filtro)) ||
        (vehiculo.marca_descripcion && vehiculo.marca_descripcion.toLowerCase().includes(filtro)) ||
        (vehiculo.modelo && vehiculo.modelo.toLowerCase().includes(filtro)) ||
        (vehiculo.color && vehiculo.color.toLowerCase().includes(filtro)) ||
        (String(vehiculo.agno).includes(filtro))
      );
    });

    // PROPIEDAD COMPUTADA PARA FILTRAR CONTRATOS
    const contratosFiltrados = computed(() => { //
      if (!filtroContratos.value) { //
        return datos.value; //
      }
      const filtro = filtroContratos.value.toLowerCase(); //
      return datos.value.filter(contrato => //
        (contrato.patente_vehiculo && contrato.patente_vehiculo.toLowerCase().includes(filtro)) || //
        (contrato.rut_cliente && contrato.rut_cliente.toLowerCase().includes(filtro)) || //
        (contrato.modelo_vehiculo && contrato.modelo_vehiculo.toLowerCase().includes(filtro)) || //
        (contrato.tipo_pago !== undefined && (contrato.tipo_pago === 0 ? 'contado' : 'crédito').toLowerCase().includes(filtro)) || //
        (String(contrato.precio_venta).includes(filtro)) || //
        (String(contrato.valor_pie).includes(filtro)) || //
        (String(contrato.numero_cuotas).includes(filtro)) || //
        (String(contrato.valor_cuota).includes(filtro)) //
      );
    });

    const cargarContratoEnFormulario = async (contrato) => {
      limpiarFormulario();
      formData.value.id = contrato.id;
      formData.value.rut = contrato.rut_cliente;
      formData.value.patente = contrato.patente_vehiculo;
      formData.value.valor_pie = contrato.valor_pie;
      formData.value.numero_cuotas = contrato.numero_cuotas;

      // 🐛 CORRECCIÓN DEL ERROR 🐛
      // Agrega una verificación para asegurarte de que la fecha existe
      if (contrato.fecha) {
        formData.value.fecha = new Date(contrato.fecha).toISOString().slice(0, 10);
      } else {
        // Si la fecha no existe, establece un valor por defecto o déjala vacía
        formData.value.fecha = '';
      }

      // 🐛 CORRECCIÓN DEL ERROR 🐛
      // Realiza la misma verificación para la fecha de creación
      if (contrato.fecha_creacion) {
        formData.value.fecha_creacion = new Date(contrato.fecha_creacion).toISOString().slice(0, 10);
      } else {
        formData.value.fecha_creacion = '';
      }

      console.log(contrato.fecha_creacion);
      console.log(contrato.fecha);

      formData.value.modelo = contrato.modelo_vehiculo;

      formData.value.precio_venta = contrato.precio_venta;
      formData.value.interes_mensual = contrato.interes_mensual;
      formData.value.valor_cuota = contrato.valor_cuota;
      formData.value.id_vendedor = contrato.id_vendedor || null;
      formData.value.rut = contrato.rut_cliente;
      formData.value.patenteaBuscar = contrato.patente_vehiculo;
      formData.value.modelo = contrato.modelo_vehiculo;

      formData.value.tipo_pago_seleccionado = contrato.tipo_pago === 0 ? 'contado' : 'credito';

      if (contrato.rut_cliente) {
        await cargarDatosCliente(contrato.rut_cliente);
      }
      if (contrato.patente_vehiculo) {
        await cargarDatosVehiculo(contrato.patente_vehiculo);
        formData.value.precio_venta = contrato.precio_venta;
      }

      mostrarMensaje('Datos del contrato cargados en el formulario.', 'info');
    };

    const calcularContrato = () => {
      const precioVenta = parseFloat(formData.value.precio_venta);
      const valor_pie = parseFloat(formData.value.valor_pie);
      const numeroCuotas = parseInt(formData.value.numero_cuotas);
      const interesMensual = parseFloat(formData.value.interes_mensual) / 100;

      if (isNaN(precioVenta) || isNaN(valor_pie) || isNaN(numeroCuotas) || isNaN(interesMensual)) {
        mostrarMensaje('Please enter valid numerical values for the calculation.', 'error');
        return;
      }

      if (numeroCuotas <= 0) {
        formData.value.valor_cuota = 0;
        // CORRECCIÓN CLAVE: Asignar el valor a la ref 'calculo'

        mostrarMensaje('Calculo desarrollado.', 'info');
        return;
      }

      const montoAFinanciar = precioVenta - valor_pie;
      let valorCuota;

      if (interesMensual === 0) {
        valorCuota = montoAFinanciar / numeroCuotas;
      } else {
        valorCuota = montoAFinanciar * (interesMensual * Math.pow(1 + interesMensual, numeroCuotas)) / (Math.pow(1 + interesMensual, numeroCuotas) - 1);
      }

      let valorCuotaEntero = parseInt(valorCuota);
      const ultimosTresDigitos = valorCuotaEntero % 1000;

      if (ultimosTresDigitos > 500) {
        valorCuota = Math.ceil(valorCuotaEntero / 1000) * 1000;
      } else {
        valorCuota = Math.floor(valorCuotaEntero / 1000) * 1000;
      }

      formData.value.valor_cuota = parseInt(valorCuota);
      // CORRECCIÓN CLAVE: Asignar el valor final calculado a la ref 'calculo'

      mostrarMensaje('Cálculo Desarrollado', 'Exitoso');
    };


    const handleSubmit = () => {
      if (!formData.value.id_vendedor) {
        mostrarMensaje('Por favor, seleccione un vendedor.', 'error');
        return;
      }

      if (!formData.value.rut) {
        mostrarMensaje('Porfavor Ingrese RUT.', 'error');
        return;
      }

      if (!formData.value.patente) {
        mostrarMensaje('Porfavor Ingrese Patente.', 'error');
        return;
      }

      if (formData.value.tipo_pago_seleccionado === 'credito') {
        if (formData.value.valor_pie === null || formData.value.valor_pie === '') {
          mostrarMensaje('Ingresar Pie.', 'error');
          return;
        }

        if (formData.value.numero_cuotas < 0 || formData.value.numero_cuotas > 60) {
          mostrarMensaje('Ingrese Número de cuotas válido (entre 0 y 32).', 'error');
          return;
        }

        if (formData.value.interes_mensual === null || formData.value.interes_mensual === '') {
          mostrarMensaje('Ingrese Interes.', 'error');
          return;
        }
      }

      if (!formData.value.fecha) {
        mostrarMensaje('Por Favor Ingrese Fecha', 'error');
        return;
      }

      if (!formData.value.fecha_creacion) {
        mostrarMensaje('Por Favor Ingrese Fecha Contrato', 'error');
        return;
      }

      guardarRegistro(formData.value.id);
    };

    const guardarRegistro = async (id) => {

      var pasar_valor = 0;

      if (calculo.value == 1) {

        pasar_valor = valor_cuota.value; // Usar formData.value.valor_cuota para el valor final del cálculo

      }
      else {

        pasar_valor = formData.value.valor_cuota;

      }

      if (formData.value.id === null) {
        mostrarMensaje('Para modificar, por favor seleccione un contrato de la lista primero.', 'error');
        return;
      }

      isLoading.value = true;
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/${id}/`;
        const method = 'PUT';

        let rutVendedorParaEnviar = '';
        if (formData.value.id_vendedor) {
          const vendedorSeleccionado = vendedores.value.find(
            (v) => v.id === formData.value.id_vendedor
          );

          if (vendedorSeleccionado) {
            rutVendedorParaEnviar = vendedorSeleccionado.rut;
          }
        }
        let payload = {};
        if (formData.value.tipo_pago_seleccionado === 'contado') {
          payload = {
            valor_pie: 0,
            numero_cuotas: 0,
            fecha_creacion: formData.value.fecha_creacion.toString().slice(0, 10),
            fecha_inicio_pago: formData.value.fecha.toString().slice(0, 10),
            interes_mensual: 0,
            valor_cuota: 0,
            rut_vendedor: rutVendedorParaEnviar,
            precio_venta: formData.value.precio_venta,
            tipo_pago: 0,
          };
        } else {

          // CORRECCIÓN CLAVE: Accede a calculo.value aquí
          payload = {
            valor_pie: formData.value.valor_pie,
            numero_cuotas: formData.value.numero_cuotas,
            fecha_creacion: formData.value.fecha_creacion,
            interes_mensual: formData.value.interes_mensual,
            // Aquí usas el valor de la ref 'calculo' que se actualizó en calcularContrato

            valor_cuota: pasar_valor,

            rut_vendedor: rutVendedorParaEnviar,
            fecha_inicio_pago: formData.value.fecha,
            precio_venta: formData.value.precio_venta,
            tipo_pago: 1,
          };
        }

        console.log("Datos a enviar (Payload):", JSON.stringify(payload));

        const response = await fetch(apiUrl, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          mostrarMensaje('¡Contrato actualizado exitosamente!', 'success');
          calculo.value = 0;
          cargarListaDeContratos();
          limpiarFormulario();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al actualizar Contrato: ${errorData.mensaje || response.statusText}`, 'error');
          console.error(`Error al actualizar Contrato:`, errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const crearRegistro = async (id) => {
      isLoading.value = true;

      var pasar_valor = 0;
      if (calculo.value == 1) {
        // alert("es uno");
        pasar_valor = formData.value.valor_cuota; // Usar formData.value.valor_cuota para el valor final del cálculo
      }
      else {
        // alert("cero");
        pasar_valor = formData.value.valor_cuota;
      }

      // alert("aqui vael valor");
      // alert(pasar_valor);
      //  pasar_valor = pasar_valor.replace(".", "");
      // pasar_valor = pasar_valor.replace(",", "");

      //   alert(pasar_valor);

      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/`;
        const method = 'POST';

        if (!formData.value.rut) {
          mostrarMensaje('Por favor, ingrese el RUT del cliente.', 'error');
          return;
        }
        if (!formData.value.patente) {
          mostrarMensaje('Por favor, ingrese la patente del vehículo.', 'error');
          return;
        }
        if (!formData.value.id_vendedor) {
          mostrarMensaje('Por favor, seleccione un vendedor.', 'error');
          return;
        }
        if (!formData.value.precio_venta) {
          mostrarMensaje('Por favor, ingrese el precio de venta.', 'error');
          return;
        }
        if (!formData.value.fecha) {
          mostrarMensaje('Por favor, ingrese la fecha.', 'error');
          return;
        }

        if (!formData.value.fecha_creacion) {
          mostrarMensaje('Por favor, ingrese la fecha de creación.', 'error');
          return;
        }

        let rutVendedorParaEnviar = '';
        if (formData.value.id_vendedor) {
          const vendedorSeleccionado = vendedores.value.find(
            (v) => v.id === formData.value.id_vendedor
          );

          if (vendedorSeleccionado) {
            rutVendedorParaEnviar = vendedorSeleccionado.rut;
          }
        }

        let payload = {};

        if (formData.value.tipo_pago_seleccionado === 'contado') {
          payload = {
            valor_pie: 0,
            numero_cuotas: 0,
            fecha_creacion: formData.value.fecha_creacion,
            interes_mensual: 0,
            valor_cuota: 0,
            rut_vendedor: rutVendedorParaEnviar,
            fecha_inicio_pago: formData.value.fecha,
            precio_venta: formData.value.precio_venta,
            rut_cliente: formData.value.rut,
            patente_vehiculo: formData.value.patente,
            nombre_cliente: formData.value.nombres,
            monto_a_financiar: formData.value.precio_venta,
            tipo_pago: 0,
          };
        } else {
          if (formData.value.valor_pie === null || formData.value.valor_pie === '') {
            mostrarMensaje('Para crédito, ingrese el pie.', 'error');
            return;
          }
          if (formData.value.numero_cuotas < 0 || formData.value.numero_cuotas > 60) {
            mostrarMensaje('Para crédito, ingrese un número de cuotas válido (entre 0 y 32).', 'error');
            return;
          }
          if (formData.value.interes_mensual === null || formData.value.interes_mensual === '') {
            mostrarMensaje('Para crédito, ingrese el interés mensual.', 'error');
            return;
          }

          payload = {
            valor_pie: formData.value.valor_pie,
            numero_cuotas: formData.value.numero_cuotas,

            interes_mensual: formData.value.interes_mensual,
            valor_cuota: pasar_valor,
            rut_vendedor: rutVendedorParaEnviar,
            fecha_inicio_pago: formData.value.fecha,
            fecha_creacion: formData.value.fecha_creacion,
            precio_venta: formData.value.precio_venta,
            rut_cliente: formData.value.rut,
            patente_vehiculo: formData.value.patente,
            nombre_cliente: formData.value.nombres,
            monto_a_financiar: formData.value.precio_venta - formData.value.valor_pie,
            tipo_pago: 1,
          };
        }

        console.log("Datos a enviar (Payload POST):", JSON.stringify(payload));

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          mostrarMensaje('¡Contrato Creado exitosamente!', 'success');
          cargarListaDeContratos();
          limpiarFormulario();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error al crear Contrato: ${errorData.mensaje || response.statusText}`, 'error');
          console.error(`Error al crear Contrato:`, errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const eliminarRegistroConfirmado = async () => {
      if (!registroAEliminarId.value) {
        console.error('No record ID specified for deletion.');
        mostrarMensaje('Error: Could not identify the contract to delete.', 'error');
        cerrarModalEliminar();
        return;
      }

      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/${registroAEliminarId.value}/`;
        console.log('Deletion URL:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          mostrarMensaje('Contract Deleted successfully!', 'success');
          cargarListaDeContratos();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error deleting Contract: ${errorData.message || response.statusText}`, 'error');
          console.error('Error deleting Contract:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Connection error with the server.', 'error');
        console.error('Connection error:', error);
      } finally {
        cerrarModalEliminar();
      }
    };

    const cargarListaDeContratos = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/`;
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();

          console.log(data);

          datos.value = data.data;

        } else {
          console.error('Error loading contract list:', response.statusText);
          mostrarMensaje('Error loading contract list.', 'error');
        }
      } catch (error) {
        console.error('Connection error loading contract list:', error);
        mostrarMensaje('Connection error loading contract list.', 'error');
      }
    };

    const obtenerVendedores = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vendedores/`;
        console.log('Consultando vendedores en:', apiUrl);
        const respuesta = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!respuesta.ok) {
          console.error(`Error consultando Vendedores: ${respuesta.status} - ${respuesta.statusText}`);
          throw new Error(`Error en la consulta: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        vendedores.value = data.data;
        console.log('Vendedores cargados:', vendedores.value);
      } catch (error) {
        console.error('Error consultando Vendedores:', error);
        mostrarMensaje('Error al cargar la lista de vendedores.', 'error');
      }
    };

    const limpiarFormulario = () => {
      formData.value = {
        nombres: null,
        apellidos: null,
        direccion: null,
        telefono: null,
        habilitado: null,
        rut: null,
        observacion: null,
        numero_cuotas: 0,
        id: null,
        patente: null,
        valor_pie: null,
        fecha: '',
        fecha_creacion: '',
        patenteaBuscar: null,
        tipo_automovil: null,
        marca: null,
        modelo: null,
        agno: null,
        numero_motor: null,
        numero_chasis: null,
        color: null,
        kilometraje: null,
        marca_descripcion: null,
        vehiculo_descripcion: null,
        precio_venta: null,
        id_vendedor: null,
        valor_venta_total: null,
        interes_mensual: null,
        valor_cuota: null,
        tipo_pago_seleccionado: 'credito',
        calculo: null
      };

      mostrarMensaje('Formulario limpiado.', 'info');
    };



    // NUEVA FUNCIÓN handleBlur (movida de methods a setup)
    const handleBlur = () => {

      return calculo.value = 1;

    };

    onMounted(() => {
      cargarListaDeContratos();
      obtenerVendedores();
      cargarListaDeVehiculos();
      cargarListaDeClientes();
    });

    return {
      formData,
      isLoading,
      handleSubmit,
      limpiarFormulario,
      guardarRegistro,
      obtenerCliente,
      mensaje,
      tipoMensaje,
      mostrarMensaje,
      limpiarMensaje,
      cargarDatosCliente,
      registroAEliminarId,
      mostrarModalEliminar,
      abrirModalEliminar,
      cerrarModalEliminar,
      eliminarRegistroConfirmado,
      cargarListaDeContratos,
      datos,
      cargarDatosVehiculo,
      cargarContratoEnFormulario,
      calcularContrato,
      crearRegistro,
      formattedValorVentaTotal,
      formattedPie,
      formattedPrecioVenta,
      rutValido,
      handleRutInput,
      obtenerVendedores,
      vendedores,
      goToContrato,
      formatearMilesConPunto,
      formatearFecha,
      listaVehiculos,
      mostrarListaVehiculos,
      cargarListaDeVehiculos,
      seleccionarVehiculoDeLista,
      filtroPatente,
      vehiculosFiltrados,
      listaClientes,
      mostrarListaClientes,
      cargarListaDeClientes,
      seleccionarClienteDeLista,
      filtroRutCliente,
      clientesFiltrados,
      generarCuotas,
      // CORRECCIÓN CLAVE: Retorna la ref 'calculo' para que esté disponible en el template y en otras funciones
      calculo,
      // Retorna también la función handleBlur si la quieres usar en el template
      handleBlur,
      filtroContratos, //
      contratosFiltrados, //
      actualizarEstadoContrato,
      nivel, // Added nivel to the return object
    };
  },
};
</script>


<template>
  <Header></Header>

  <div class="container-fluid mt-3">
    <div class="card shadow-sm mt-3 ">
      <div class="card-header" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Ingreso
        Contratos
      </div>
      <div class="card-body mt-3">
        <form @submit.prevent="handleSubmit">

          <div class="card">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Ingreso Contrato del Cliente</div>
            </div>
            <div class="card-body left">

              <div class="mb-3 row align-items-center">
                <label for="rut" class="col-md-1 col-form-label negrita">Rut</label>
                <div class="col-md-3">
                  <input type="text" class="form-control form-control-sm negrita" id="rut" v-model="formData.rut"
                    required @input="handleRutInput" :class="{ 'is-invalid': !rutValido && formData.rut }" />
                  <div v-if="!rutValido && formData.rut" class="invalid-feedback">
                    Por favor, ingrese un RUT válido.
                  </div>
                </div>
                <div class="col-md-auto ms-4">
                  <button type="button" class="btn btn-secondary btn-sm" @click="cargarDatosCliente(formData.rut)">
                    Buscar
                  </button>
                  <button type="button" class="btn btn-info btn-sm ms-2"
                    @click="mostrarListaClientes = !mostrarListaClientes">
                    {{ mostrarListaClientes ? 'Ocultar Lista' : 'Mostrar Lista de Clientes' }}
                  </button>
                </div>
              </div>

              <div class="mb-3 row align-items-center">
                <label for="nombres" class="col-md-2 col-form-label negrita">Nombres</label>
                <div class="col-md-4">
                  {{ formData.nombres }}
                </div>
                <label for="apellidos" class="col-md-2 col-form-label negrita">Apellidos</label>
                <div class="col-md-4">
                  {{ formData.apellidos }}
                </div>
              </div>
              <div class="mb-3 row align-items-center">
                <label for="direccion" class="col-md-2 col-form-label negrita">Direccion</label>
                <div class="col-md-4">
                  {{ formData.direccion }}
                </div>
                <label for="telefono" class="col-md-2 col-form-label negrita">Teléfono</label>
                <div class="col-md-4">
                  {{ formData.telefono }}
                </div>
              </div>
              <div class="mb-3 row align-items-center">
                <label for="habilitado" class="col-md-3 col-form-label negrita">Habilitado Compras :</label>

                <div class="col-md-9 negrita">
                  {{ formData.habilitado ? 'Sí' : 'No' }}
                </div>
              </div>

              <div v-if="mostrarListaClientes" class="mt-4">
                <h4 style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Clientes Disponibles</h4>
                <div class="mb-3">
                  <input type="text" class="form-control form-control-sm" v-model="filtroRutCliente"
                    placeholder="Filtrar por RUT, nombre, apellido, dirección o teléfono..." />
                </div>
                <table class="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>RUT</th>
                      <th>Nombres</th>
                      <th>Apellidos</th>
                      <th>Dirección</th>
                      <th>Teléfono</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="cliente in clientesFiltrados" :key="cliente.id"
                      @click="seleccionarClienteDeLista(cliente)" style="cursor: pointer;">
                      <td>{{ cliente.rut }}</td>
                      <td>{{ cliente.nombres }}</td>
                      <td>{{ cliente.apellidos }}</td>
                      <td>{{ cliente.fono }}</td>
                    </tr>
                    <tr v-if="clientesFiltrados.length === 0">
                      <td colspan="5" class="text-center">No se encontraron clientes que coincidan con el filtro.</td>
                    </tr>
                  </tbody>
                </table>
              </div>

            </div>
          </div>

          <div class="card mt-3">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Seleccion Vehículo</div>
            </div>
            <div class="card-body left">

              <div class="mb-3 row align-items-center">
                <label for="patenteaBuscar" class="col-md-2 col-form-label negrita">Patente</label>
                <div class="col-md-3">
                  <input type="text" class="form-control form-control-sm negrita" size="10" maxlength="10"
                    id="patenteaBuscar" name="patenteaBuscar" v-model="formData.patenteaBuscar" style="width: 200px" />
                </div>

                <div class="col-md-auto ms-4">
                  <button type="button" class="btn btn-secondary btn-sm"
                    @click="cargarDatosVehiculo(formData.patenteaBuscar)"> Buscar
                  </button>
                  <button type="button" class="btn btn-info btn-sm ms-2"
                    @click="mostrarListaVehiculos = !mostrarListaVehiculos">
                    {{ mostrarListaVehiculos ? 'Ocultar Lista' : 'Mostrar Lista de Vehículos' }}
                  </button>
                </div>
              </div>

              <div class="mb-3 row align-items-center">
                <label for="vehiculo" class="col-md-2 col-form-label negrita">Vehículo</label>
                <div class="col-md-4">
                  {{ formData.vehiculo_descripcion }}
                </div>
                <label for="marca" class="col-md-2 col-form-label negrita">Marca</label>
                <div class="col-md-4">
                  {{ formData.marca_descripcion }}
                </div>
              </div>
              <div class="mb-3 row align-items-center">
                <label for="agno" class="col-md-2 col-form-label negrita">Año</label>
                <div class="col-md-4">
                  {{ formData.agno }}
                </div>
                <label for="color" class="col-md-2 col-form-label negrita">Color</label>
                <div class="col-md-4">
                  {{ formData.color }}
                </div>
              </div>

              <div v-if="mostrarListaVehiculos" class="mt-4">
                <h4 style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Vehículos Disponibles</h4>
                <div class="mb-3">
                  <input type="text" class="form-control form-control-sm" v-model="filtroPatente"
                    placeholder="Filtrar por patente,  modelo" />
                </div>
                <table class="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>Patente</th>
                      <th>Tipo Vehículo</th>
                      <th>Marca</th>
                      <th>Modelo</th>
                      <th>Color</th>
                      <th>Año</th>
                      <th>Precio Venta</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="vehiculo in vehiculosFiltrados" :key="vehiculo.id"
                      @click="seleccionarVehiculoDeLista(vehiculo)" style="cursor: pointer;">
                      <td>{{ vehiculo.patente }}</td>
                      <td>{{ vehiculo.tipo_automovil }}</td>
                      <td>{{ vehiculo.marca_descripcion }}</td>
                      <td>{{ vehiculo.modelo }}</td>
                      <td>{{ vehiculo.color }}</td>
                      <td>{{ vehiculo.agno }}</td>
                      <td>{{ formatearMilesConPunto(vehiculo.precio_venta) }}</td>
                    </tr>
                    <tr v-if="vehiculosFiltrados.length === 0">
                      <td colspan="7" class="text-center">No se encontraron vehículos que coincidan con el filtro.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="card mt-3">
            <div class="card-header">
              <div class="card-title" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">
                Cálculo Contrato CompraVentas</div>
            </div>

            <div class="card-body left">
              <div class="mb-3 row align-items-center">
                <label class="col-md-2 col-form-label negrita">Tipo de Pago</label>
                <div class="col-md-4">
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="pagoContado" value="contado"
                      v-model="formData.tipo_pago_seleccionado">
                    <label class="form-check-label negrita" for="pagoContado">Contado</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="pagoCredito" value="credito"
                      v-model="formData.tipo_pago_seleccionado">
                    <label class="form-check-label negrita" for="pagoCredito">Crédito</label>
                  </div>
                </div>
              </div>

              <div class="mb-3 row">
                <label for="fecha_creacion" class="col-md-2 col-form-label negrita">Fecha Contrato</label>
                <div class="col-md-3">
                  <input type="date" class="form-control form-control-sm negrita" id="fecha_creacion"
                    name="fecha_creacion" v-model="formData.fecha_creacion" />
                </div>
              </div>




              <div class="mb-3 row align-items-center">
                <label for="vendedor" class="col-md-2 col-form-label negrita">Vendedor</label>
                <div class="col-md-4">
                  <select class="form-select form-select-sm negrita" id="vendedor" v-model="formData.id_vendedor">
                    <option :value="null" disabled>Seleccione un vendedor</option>
                    <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">
                      {{ vendedor.rut }} - {{ vendedor.nombres }} {{ vendedor.apellidos }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="mb-3 row align-items-center">
                <label for="venta" class="col-md-2 col-form-label negrita">Precio Venta $</label>
                <div class="col-md-3">
                  <input type="text" class="form-control form-control-sm negrita" size="10" maxlength="10"
                    id="precio_venta" name="precio_venta" v-model="formattedPrecioVenta" style="width: 200px" />
                </div>
              </div>

              <div v-if="formData.tipo_pago_seleccionado === 'credito'">
                <div class="mb-3 row align-items-center">
                  <label for="pie" class="col-md-2 col-form-label negrita">Pié $</label>
                  <div class="col-md-3">
                    <input type="text" class="form-control form-control-sm negrita" size="10" maxlength="10"
                      id="valor_pie" name="valor_pie" v-model="formattedPie" style="width: 200px" />
                  </div>
                </div>
                <div class="mb-3 row align-items-center">
                  <label for="numero_cuotas" class="col-md-2 col-form-label negrita">Número Cuotas</label>
                  <div class="col-md-3">
                    <input type="number" class="form-control form-control-sm negrita" size="10" maxlength="10"
                      id="numero_cuotas" name="numero_cuotas" v-model="formData.numero_cuotas" style="width: 200px" />
                  </div>

                  <label for="interes" class="col-md-2 col-form-label negrita">Interés %</label>
                  <div class="col-md-3">
                    <input type="number" step="0.1" class="form-control form-control-sm negrita" size="10"
                      maxlength="10" id="interes" name="interes" v-model="formData.interes_mensual"
                      style="width: 200px" />
                  </div>
                </div>
                <div class="mb-3 row align-items-center">
                  <label for="valor_cuota" class="col-md-2 col-form-label negrita">Valor Cuotas $</label>
                  <div class="col-md-3">
                    <input type="text" class="form-control form-control-sm negrita" size="10" maxlength="10"
                      id="valor_cuota" name="valor_cuota" :value="formatearMilesConPunto(formData.valor_cuota)"
                      style="width: 200px" @blur="handleBlur" />
                  </div>

                  <div class="col-md-auto ms-4">
                    <button type="button" class="btn btn-secondary btn-sm" @click="calcularContrato()">
                      Calcular
                    </button>
                  </div>
                </div>
              </div>
              <div class="mb-3 row">
                <label for="fecha" class="col-md-2 col-form-label negrita">Fecha de Pago</label>
                <div class="col-md-3">
                  <input type="date" class="form-control form-control-sm negrita" id="fecha" name="fecha"
                    v-model="formData.fecha" />
                </div>
              </div>
            </div>
          </div>
          <br>
          <div class="d-flex justify-content-center">
            <div class="col-md-auto ms-2">
              <button type="button" class="btn btn-secondary btn-sm" @click="limpiarFormulario()">Limpiar</button>
            </div>
            <div class="col-md-auto ms-2">
              <button type="button" class="btn btn-secondary btn-sm" @click="crearRegistro()">Nuevo</button>
            </div>
            <div class="col-md-auto ms-2">
              <button type="button" @click="handleSubmit" class="btn btn-secondary btn-sm"
                :disabled="isLoading || formData.id === null" @blur="handleBlur">
                {{ isLoading ? 'Modificando...' : 'Modificar' }}
              </button>
            </div>
            <br>
            <br>
          </div>

        </form>
        <div v-if="mensaje" class="mt-3 alert"
          :class="{ 'alert-success': tipoMensaje === 'success', 'alert-danger': tipoMensaje === 'error', 'alert-info': tipoMensaje === 'info' }">
          {{ mensaje }}
        </div>

        <h3 class="mt-4" style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Lista de Contratos
        </h3>
        <div class="mb-3">
          <input type="text" class="form-control form-control-sm" v-model="filtroContratos"
            placeholder="Filtrar contratos por patente, RUT, cliente, tipo de pago, etc..." />
        </div>
        <div class="table-responsive-xl">
          <table class="table table-striped custom-table">
            <thead>
              <tr style="text-align: center;">
                <th>Fecha Contrato</th>
                <th>Fecha Inicio Pago</th>
                <th>Patente</th>
                <th>Nombres</th>
                <th>Apellidos</th>
                <th>Precio Venta</th>
                <th>Tipo Pago</th>
                <th>Pie</th>
                <th>Modelo</th>
                <th>#cuotas</th>
                <th>Valor Cuota</th>
                <th>Acciones</th>
                <th>Contado</th>
                <th>Credito</th>
                <th>Carta</th>
                <th title="Generacion Cuotas">Cuotas</th>
                <th title="Contrato pagado se debe deshabilitar">Descartar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="contrato in contratosFiltrados" :key="contrato.id"
                @click="cargarContratoEnFormulario(contrato)" style="cursor: pointer;">
                <td style="text-align: center;">{{ contrato.fecha_creacion }}</td>
                <td style="text-align: center;">{{ contrato.fecha_inicio_pago }}</td>
                <td style="text-align: center;">{{ contrato.patente_vehiculo }}</td>
                <td style="text-align: left;">{{ contrato.nombre_cliente }}</td>
                <td style="text-align: left;">{{ contrato.apellidos }}</td>
                <td style="text-align: center;">{{ formatearMilesConPunto(contrato.precio_venta) }}</td>
                <td style="text-align: center;">{{ contrato.tipo_pago == 0 ? 'Contado' : 'Crédito' }}</td>
                <td style="text-align: center;">{{ formatearMilesConPunto(contrato.valor_pie) }}</td>
                <td style="text-align: center;">{{ contrato.modelo_vehiculo || 'N/A' }}</td>
                <td style="text-align: center;" title="Creacion Cuotas">{{ contrato.numero_cuotas }}</td>
                <td style="text-align: center;">{{ formatearMilesConPunto(contrato.valor_cuota) }}</td>
                <td>
                  <button type="button" class="btn btn-danger btn-sm" @click.stop="abrirModalEliminar(contrato.id)"
                    :disabled="nivel !== 'ADMIN'">
                    Eliminar
                  </button>
                </td>
                <td>
                  <button type="button" class="btn btn-info btn-sm"
                    @click.stop="goToContrato(contrato.patente_vehiculo, contrato.id, 0)">
                    Contado
                  </button>
                </td>
                <td>
                  <button type="button" class="btn btn-info btn-sm"
                    @click.stop="goToContrato(contrato.patente_vehiculo, contrato.id, 1)">
                    Crédito
                  </button>
                </td>
                <td>
                  <button type="button" class="btn btn-info btn-sm"
                    @click.stop="goToContrato(contrato.patente_vehiculo, contrato.id, 2)">
                    Carta
                  </button>
                </td>
                <td style="text-align: center;">
                  <button type="button" class="btn btn-info btn-sm" @click="generarCuotas(contrato)">
                    Cuotas
                  </button>
                </td>

                <td style="text-align: center;">
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" :id="'flexSwitchCheckChecked-' + contrato.id"
                      v-model="contrato.estado" @change="actualizarEstadoContrato(contrato)"
                      :disabled="nivel !== 'ADMIN'" />
                    <!-- Habilitado visualmente según el booleano -->
                  </div>
                </td>

              </tr>
              <tr v-if="contratosFiltrados.length === 0">
                <td colspan="17" class="text-center">No se encontraron contratos que coincidan con el filtro.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div v-if="mostrarModalEliminar" class="modal fade show" tabindex="-1" style="display: block;" aria-modal="true"
    role="dialog">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Confirmar Eliminación</h5>
          <button type="button" class="btn-close" @click="cerrarModalEliminar" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          ¿Estás seguro de que deseas eliminar este contrato? Esta acción no se puede deshacer.
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cerrarModalEliminar">Cancelar</button>
          <button type="button" class="btn btn-danger" @click="eliminarRegistroConfirmado">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="mostrarModalEliminar" class="modal-backdrop fade show"></div>
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
  min-width: 1200px;
}
</style>