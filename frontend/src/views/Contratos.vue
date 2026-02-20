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
      interes_mensual: 3.5,
      valor_cuota: null,
      tipo_pago_seleccionado: 'credito',
      habilitado_compra: null,
    });

    // States for the user interface
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]);
    const rutValido = ref(true);
    const vendedores = ref([]);

    // CORRECCIÓN CLAVE: Declarar 'calculo' como una ref para que sea reactiva
    const usuario = ref(localStorage.getItem('user_usuario'));
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

    const filtroContratos = ref(''); //
    const mostrarHistorico = ref(false); // Toggle para ver históricos

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
      // Asumimos formato YYYY-MM-DD que viene del backend
      const partes = fechaISO.toString().slice(0, 10).split('-');
      if (partes.length === 3) {
        const [year, month, day] = partes;
        return `${day}-${month}-${year}`;
      }
      return fechaISO;
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
          params: { rut: rutCliente, patente: contractPatente, idPrep: id }
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
    const registroAEliminarRut = ref(null);
    const registroAEliminarPatente = ref(null);
    const mostrarModalEliminar = ref(false);

    // Variables para el modal de deshabilitar
    const contratoADeshabilitar = ref(null);
    const mostrarModalDeshabilitar = ref(false);

    const abrirModalEliminar = (id, rut, patente) => {
      registroAEliminarId.value = id;
      registroAEliminarRut.value = rut;
      registroAEliminarPatente.value = patente;
      mostrarModalEliminar.value = true;
    };

    const cerrarModalEliminar = () => {
      registroAEliminarId.value = null;
      registroAEliminarRut.value = null;
      registroAEliminarPatente.value = null;
      mostrarModalEliminar.value = false;
    };

    const abrirModalDeshabilitar = (contrato) => {
      contratoADeshabilitar.value = contrato;
      mostrarModalDeshabilitar.value = true;
    };

    const cerrarModalDeshabilitar = () => {
      contratoADeshabilitar.value = null;
      mostrarModalDeshabilitar.value = false;
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

    const manejarCambioEstadoContrato = (contrato) => {
      // IMPORTANTE: En el backend, estado=0 es HABILITADO, estado=1 es DESHABILITADO
      // El checkbox muestra el estado "habilitado" visualmente
      // Si contrato.estado es false (deshabilitado visualmente), el valor en BD debe ser 1
      // Si contrato.estado es true (habilitado visualmente), el valor en BD debe ser 0

      // Si se está deshabilitando (cambiando de true/0 a false/1), mostrar modal de confirmación
      if (!contrato.estado) {
        // Revertir temporalmente el cambio en el checkbox
        contrato.estado = true;
        // Mostrar modal de confirmación
        abrirModalDeshabilitar(contrato);
      } else {
        // Si se está habilitando (cambiando de false/1 a true/0), proceder directamente
        actualizarEstadoContrato(contrato);
      }
    };

    const actualizarEstadoContrato = async (contrato) => {
      const contratoId = contrato.id;
      const nuevoHabilitado = contrato.estado;
      const nuevoEstadoDB = nuevoHabilitado ? 0 : 1;

      if (!contratoId) {
        mostrarMensaje('Error: No se encontró el ID del contrato para actualizar.', 'error');
        return;
      }

      isLoading.value = true;

      const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/estado/${contratoId}/`;

      try {
        const response = await fetch(apiUrl, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': 'Contratos',
          },
          body: JSON.stringify({ estado: nuevoEstadoDB }),
        });

        if (response.ok) {
          mostrarMensaje(`Presupuesto #${contratoId} actualizado a Habilitado: ${nuevoHabilitado ? 'SÍ' : 'NO'}.`, 'success');
        } else {
          contrato.estado = !nuevoHabilitado;
          const errorData = await response.json();
          console.error('ERROR al actualizar estado:', response.status, errorData);
          mostrarMensaje('Error al guardar el cambio en el servidor. Revirtiendo estado.', 'error');
        }
      } catch (error) {
        contrato.estado = !nuevoHabilitado;
        console.error('ERROR de conexión:', error);
        mostrarMensaje('Error de conexión con el servidor. No se pudo guardar.', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const deshabilitarContratoConfirmado = async () => {
      if (!contratoADeshabilitar.value) {
        cerrarModalDeshabilitar();
        return;
      }

      // Guardar el ID del contrato antes de actualizarlo
      const contratoId = contratoADeshabilitar.value.id;

      // Actualizar el estado del contrato a deshabilitado
      contratoADeshabilitar.value.estado = false;
      await actualizarEstadoContrato(contratoADeshabilitar.value);

      // IMPORTANTE: Eliminar el contrato de la lista visible inmediatamente
      // ya que los contratos descartados (estado=1) no deben aparecer en ningún listado
      datos.value = datos.value.filter(contrato => contrato.id !== contratoId);

      mostrarMensaje('Contrato descartado. No aparecerá en listados, cuotas ni informes.', 'success');
      cerrarModalDeshabilitar();
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
        console.error('Datos faltantes para generar cuotas:', { rut_cliente, patente, numero_cuota, monto_cuota, fecha_inicio_pago, monto_prestamo });
        mostrarMensaje('Faltan datos esenciales para generar las cuotas. Verifique RUT, Patente, Cantidad de Cuotas, Monto de Cuota y Fecha Inicial.', 'error');
        return;
      }

      // Construir la URL con query parameters (como espera el backend)
      const params = new URLSearchParams({
        rut_cliente: rut_cliente,
        patente: patente,
        numero_cuota: numero_cuota,
        monto_cuota: monto_cuota,
        fecha_vencimiento: fecha_inicio_pago,
        monto_prestamo: monto_prestamo,
        interes_mensual: interes_mensual || 0
      });

      const apiUrl = `${import.meta.env.VITE_API_URL}generarCuotas/?${params.toString()}`;
      console.log('Enviando datos al backend para generar cuotas:', apiUrl);

      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': 'Contratos',
          }
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || errorData.detail || JSON.stringify(errorData) || 'Error desconocido del servidor.');
        }

        const data = await response.json();
        console.log('Cuotas generadas con éxito:', data);
        mostrarMensaje('Cuotas generadas con éxito!', 'success');
      } catch (error) {
        console.error('Error al generar las cuotas:', error);
        mostrarMensaje(`Error al generar las cuotas: ${error.message}`, 'error');
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
        formData.value.habilitado_venta = null;
        formData.value.habilitado_compra = null;
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
          formData.value.habilitado_venta = vehiculoData.habilitado_venta;
          formData.value.habilitado_compra = vehiculoData.habilitado_compra;
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
          formData.value.habilitado_venta = null;
          formData.value.habilitado_compra = null;
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
          // Mapear los datos para convertir habilitado_venta de 0/1 a boolean
          listaVehiculos.value = data.data.map(vehiculo => ({
            ...vehiculo,
            habilitado_venta: vehiculo.habilitado_venta === 1
          }));
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
      formData.value.habilitado_venta = vehiculo.habilitado_venta;
      formData.value.habilitado_compra = vehiculo.habilitado_compra;
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
    const contratosFiltrados = computed(() => {
      let lista = datos.value;

      // 1. Filtrar por Estado (Histórico vs Activo)
      if (mostrarHistorico.value) {
        // Si está activado histórico, mostrar SOLO los estado = 1
        lista = lista.filter(contrato => Number(contrato.estado) === 1);
      } else {
        // Por defecto, mostrar SOLO los activos (estado != 1)
        lista = lista.filter(contrato => Number(contrato.estado) !== 1);
      }

      // 2. Filtrar por Texto de Búsqueda
      if (!filtroContratos.value) {
        return lista;
      }

      const filtro = filtroContratos.value.toLowerCase();
      return lista.filter(contrato =>
        (contrato.patente_vehiculo && contrato.patente_vehiculo.toLowerCase().includes(filtro)) ||
        (contrato.rut_cliente && contrato.rut_cliente.toLowerCase().includes(filtro)) ||
        (contrato.modelo_vehiculo && contrato.modelo_vehiculo.toLowerCase().includes(filtro)) ||
        (contrato.tipo_pago !== undefined && (contrato.tipo_pago === 0 ? 'contado' : 'crédito').toLowerCase().includes(filtro)) ||
        (String(contrato.precio_venta).includes(filtro)) ||
        (String(contrato.valor_pie).includes(filtro)) ||
        (String(contrato.numero_cuotas).includes(filtro)) ||
        (String(contrato.valor_cuota).includes(filtro))
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
      // El backend envía 'fecha_inicio_pago' o 'fecha_inicio' (dependiendo del serializador)
      const fechaPago = contrato.fecha_inicio_pago || contrato.fecha_inicio || contrato.fecha;

      if (fechaPago) {
        // No convertir a Date para evitar problemas de timezone
        // El backend ya envía las fechas en formato YYYY-MM-DD
        formData.value.fecha = fechaPago.toString().slice(0, 10);
      } else {
        formData.value.fecha = '';
      }

      // 🐛 CORRECCIÓN DEL ERROR 🐛
      // Realiza la misma verificación para la fecha de creación
      if (contrato.fecha_creacion) {
        // No convertir a Date para evitar problemas de timezone
        formData.value.fecha_creacion = contrato.fecha_creacion.toString().slice(0, 10);
      } else {
        formData.value.fecha_creacion = '';
      }

      console.log(contrato.fecha_creacion);
      console.log(contrato.fecha);

      formData.value.modelo = contrato.modelo_vehiculo;

      formData.value.precio_venta = contrato.precio_venta;
      formData.value.interes_mensual = contrato.interes_mensual;
      formData.value.valor_cuota = contrato.valor_cuota;
      // CORRECCIÓN: Usar rut_vendedor que viene del serializador
      formData.value.id_vendedor = contrato.rut_vendedor || contrato.id_vendedor || null;
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

      if (!formData.value.habilitado) {
        mostrarMensaje('El cliente no está habilitado para crear contratos.', 'error');
        return;
      }

      if (!formData.value.patente) {
        mostrarMensaje('Porfavor Ingrese Patente.', 'error');
        return;
      }

      if (!formData.value.habilitado_venta) {
        mostrarMensaje('El vehículo no está habilitado para crear contratos.', 'error');
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

        // Al usar rut como value en el dropdown, formData.value.id_vendedor YA ES EL RUT
        const rutVendedorParaEnviar = formData.value.id_vendedor || '';
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
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': 'Contratos',
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

        if (!formData.value.habilitado) {
          mostrarMensaje('El cliente no está habilitado para crear contratos.', 'error');
          return;
        }
        if (!formData.value.patente) {
          mostrarMensaje('Por favor, ingrese la patente del vehículo.', 'error');
          return;
        }

        if (!formData.value.habilitado_venta) {
          mostrarMensaje('El vehículo no está habilitado para crear contratos.', 'error');
          return;
        }

        // Validacion de duplicados eliminada a peticion del usuario (permitir multiples contratos mismo RUT/Patente)
        /*
        const contratoExistente = datos.value.find(
          contrato => contrato.rut_cliente === formData.value.rut &&
            contrato.patente_vehiculo === formData.value.patente
        );
  
        if (contratoExistente) {
          mostrarMensaje(`Ya existe un contrato para el RUT ${formData.value.rut} con la patente ${formData.value.patente}. No se pueden crear contratos duplicados.`, 'error');
          return;
        }
        */

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

        // Al usar rut como value en el dropdown, formData.value.id_vendedor YA ES EL RUT
        const rutVendedorParaEnviar = formData.value.id_vendedor || '';

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
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': 'Contratos',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          mostrarMensaje('¡Contrato Creado exitosamente!', 'success');

          // Deshabilitar el vehículo para venta después de crear el contrato
          try {
            const patenteVehiculo = formData.value.patente;
            const vehiculoApiUrl = `${import.meta.env.VITE_API_URL}vehiculos/${patenteVehiculo}/`;

            const vehiculoResponse = await fetch(vehiculoApiUrl, {
              method: 'PATCH',
              headers: {
                'Content-Type': 'application/json',
                'X-Usuario-Sesion': usuario.value || 'Anónimo',
                'X-Pagina-Origen': 'Contratos',
              },
              body: JSON.stringify({ habilitado_venta: 0 }),
            });

            if (vehiculoResponse.ok) {
              console.log(`Vehículo ${patenteVehiculo} deshabilitado para venta automáticamente.`);
            } else {
              console.error('Error al deshabilitar vehículo para venta:', await vehiculoResponse.json());
            }
          } catch (errorVehiculo) {
            console.error('Error de conexión al deshabilitar vehículo:', errorVehiculo);
          }

          // Generar cuotas automáticamente si es un contrato a crédito con cuotas
          console.log('--- REVISIÓN GENERACIÓN CUOTAS AUTO ---');
          console.log('Tipo Pago:', formData.value.tipo_pago_seleccionado);
          console.log('Num Cuotas:', formData.value.numero_cuotas);

          if (formData.value.tipo_pago_seleccionado === 'credito' && formData.value.numero_cuotas > 0) {
            console.log('>>> CONDICIONES OK. Intentando generar cuotas...');
            // Guardar los datos ANTES de limpiar el formulario
            const contratoParaCuotas = {
              rut_cliente: formData.value.rut,
              patente_vehiculo: formData.value.patente,
              numero_cuotas: formData.value.numero_cuotas,
              precio_venta: formData.value.precio_venta,
              valor_pie: formData.value.valor_pie,
              interes_mensual: formData.value.interes_mensual,
              valor_cuota: pasar_valor,
              fecha_inicio_pago: formData.value.fecha
            };

            console.log('Datos preparados:', contratoParaCuotas);

            try {
              await generarCuotas(contratoParaCuotas);
              console.log('>>> generarCuotas() finalizado.');
            } catch (errorGen) {
              console.error('>>> ERROR en generarCuotas():', errorGen);
              mostrarMensaje('Error generando cuotas: ' + errorGen.message, 'error');
            }

          } else {
            console.warn('>>> NO SE GENERAN CUOTAS. Condición no cumplida (Contado o 0 cuotas).');
          }

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
        isLoading.value = true;
        const rut = registroAEliminarRut.value;
        const patente = registroAEliminarPatente.value;

        // 1. Eliminar los pagos en detalle_pago
        if (rut && patente) {
          const apiUrlDetallepagos = `${import.meta.env.VITE_API_URL}detallepagocuotas/?rut=${rut}&patente=${patente}`;
          console.log('Eliminando pagos de detalle_pago:', apiUrlDetallepagos);
          try {
            const responsePagos = await fetch(apiUrlDetallepagos, {
              method: 'DELETE',
              headers: {
                'Content-Type': 'application/json',
                'X-Usuario-Sesion': usuario.value || 'Anónimo',
                'X-Pagina-Origen': 'Contratos',
              },
            });
            if (responsePagos.ok) {
              console.log('Pagos de detalle_pago eliminados exitosamente.');
            } else {
              console.warn('No se pudieron eliminar todos los pagos o no existían pagos.');
            }
          } catch (error) {
            console.error('Error eliminando pagos:', error);
          }

          // 2. Eliminar las cuotas en pago_cuotas
          const apiUrlCuotas = `${import.meta.env.VITE_API_URL}pagocuotas/?rut=${rut}&patente=${patente}`;
          console.log('Eliminando cuotas de pago_cuotas:', apiUrlCuotas);
          try {
            const responseCuotas = await fetch(apiUrlCuotas, {
              method: 'DELETE',
              headers: {
                'Content-Type': 'application/json',
                'X-Usuario-Sesion': usuario.value || 'Anónimo',
                'X-Pagina-Origen': 'Contratos',
              },
            });
            if (responseCuotas.ok) {
              console.log('Cuotas de pago_cuotas eliminadas exitosamente.');
            } else {
              console.warn('No se pudieron eliminar todas las cuotas o no existían cuotas.');
            }
          } catch (error) {
            console.error('Error eliminando cuotas:', error);
          }
        }

        // 3. Eliminar el contrato
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/${registroAEliminarId.value}/`;
        console.log('Eliminando contrato:', apiUrl);
        const response = await fetch(apiUrl, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-Usuario-Sesion': usuario.value || 'Anónimo',
            'X-Pagina-Origen': 'Contratos',
          },
        });

        if (response.ok) {
          mostrarMensaje('Contrato y sus datos asociados eliminados exitosamente!', 'success');
          cargarListaDeContratos();
        } else {
          const errorData = await response.json();
          mostrarMensaje(`Error eliminando contrato: ${errorData.message || response.statusText}`, 'error');
          console.error('Error eliminando contrato:', errorData);
        }
      } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
        console.error('Error de conexión:', error);
      } finally {
        isLoading.value = false;
        cerrarModalEliminar();
      }
    };

    const cargarListaDeContratos = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/`;
        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();

          console.log('Total contratos recibidos:', data.data.length);

          // Cargar TODOS los contratos sin filtrar por estado aquí
          // El filtrado se hace en contratosFiltrados
          datos.value = data.data.map(contrato => ({
            ...contrato,
            // Aseguramos que el estado se maneje consistentemente como 0 o 1
            // Si es 1, "1", o true, lo forzamos a 1 (Histórico/Descartado)
            // Cualquier otro valor (0, null, undefined, false) será 0 (Activo)
            estado: (contrato.estado == 1 || contrato.estado === '1' || contrato.estado === true) ? 1 : 0
          }));

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
        interes_mensual: 3.5,
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
      filtroContratos,
      mostrarHistorico,
      contratosFiltrados,
      actualizarEstadoContrato,
      manejarCambioEstadoContrato,
      mostrarModalDeshabilitar,
      abrirModalDeshabilitar,
      cerrarModalDeshabilitar,
      deshabilitarContratoConfirmado,
      contratoADeshabilitar,
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
              <div class="mb-3 row align-items-center">
                <label for="habilitado_venta" class="col-md-2 col-form-label negrita">Habilitado para Venta</label>
                <div class="col-md-4">
                  <span :class="formData.habilitado_venta ? 'badge bg-success' : 'badge bg-danger'">
                    {{ formData.habilitado_venta ? 'SÍ' : 'NO' }}
                  </span>
                </div>
              </div>

              <div v-if="mostrarListaVehiculos" class="mt-4">
                <h4 style="font-weight: bolder; font-size: medium; color: rgb(56, 149, 73);">Vehículos Disponibles
                </h4>
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
                      <th>Habilitado Venta</th>
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
                      <td>
                        <span :class="vehiculo.habilitado_venta ? 'badge bg-success' : 'badge bg-danger'">
                          {{ vehiculo.habilitado_venta ? 'Sí' : 'No' }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="vehiculosFiltrados.length === 0">
                      <td colspan="8" class="text-center">No se encontraron vehículos que coincidan con el filtro.
                      </td>
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
                    <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.rut">
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
                      maxlength="10" id="interes" name="interes" v-model="formData.interes_mensual" style="width: 200px"
                      :disabled="nivel !== 'ADMIN'" />
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
              <button type="button" class="btn btn-secondary btn-sm" @click="crearRegistro()"
                :disabled="!formData.habilitado_venta">Nuevo</button>
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
        <div class="mb-3 d-flex gap-2">
          <input type="text" class="form-control form-control-sm" v-model="filtroContratos"
            placeholder="Filtrar contratos por patente, RUT, cliente, tipo de pago, etc..." />

          <button type="button" class="btn btn-sm" :class="mostrarHistorico ? 'btn-warning' : 'btn-outline-secondary'"
            @click="mostrarHistorico = !mostrarHistorico">
            {{ mostrarHistorico ? 'Ocultar Histórico' : 'Ver Histórico' }}
          </button>
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
                <td style="text-align: center;">{{ formatearFecha(contrato.fecha_creacion) }}</td>
                <td style="text-align: center;">{{ formatearFecha(contrato.fecha_inicio_pago) }}</td>
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
                  <button type="button" class="btn btn-danger btn-sm"
                    @click.stop="abrirModalEliminar(contrato.id, contrato.rut_cliente, contrato.patente_vehiculo)"
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
                  <button type="button" class="btn btn-info btn-sm" @click.stop="generarCuotas(contrato)">
                    Cuotas
                  </button>
                </td>

                <td style="text-align: center;" @click.stop>
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" :id="'flexSwitchCheckChecked-' + contrato.id"
                      v-model="contrato.estado" @change="manejarCambioEstadoContrato(contrato)"
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
          <p>¿Estás seguro de que deseas eliminar este contrato?</p>
          <p><strong>Esta acción eliminará:</strong></p>
          <ul>
            <li>El contrato seleccionado</li>
            <li>Todas las cuotas asociadas en pago_cuotas</li>
            <li>Todos los pagos realizados en detalle_pagos</li>
          </ul>
          <p class="text-danger"><strong>Esta acción no se puede deshacer.</strong></p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cerrarModalEliminar">Cancelar</button>
          <button type="button" class="btn btn-danger" @click="eliminarRegistroConfirmado">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="mostrarModalEliminar" class="modal-backdrop fade show"></div>

  <!-- Modal de confirmación para deshabilitar contrato -->
  <div v-if="mostrarModalDeshabilitar" class="modal fade show" tabindex="-1" style="display: block;" aria-modal="true"
    role="dialog">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-warning">
          <h5 class="modal-title">Confirmar Deshabilitación de Contrato</h5>
          <button type="button" class="btn-close" @click="cerrarModalDeshabilitar" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p><strong>¿Estás seguro de que deseas deshabilitar este contrato?</strong></p>
          <p>Al deshabilitar este contrato:</p>
          <ul>
            <li>Desaparecerá de la lista de contratos activos</li>
            <li>Desaparecerá de pago de cuotas</li>
            <li>Desaparecerá de todos los informes</li>
          </ul>
          <p class="text-warning"><strong>Nota:</strong> Esta acción puede ser revertida volviendo a habilitar el
            contrato.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cerrarModalDeshabilitar">Cancelar</button>
          <button type="button" class="btn btn-warning" @click="deshabilitarContratoConfirmado">Deshabilitar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="mostrarModalDeshabilitar" class="modal-backdrop fade show"></div>

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

/* Agrandar checkbox "Descartar" en un 25% */
.form-check-input {
  width: 1.5625em;
  /* 1.25em * 1.25 = 1.5625em (25% más grande) */
  height: 1.5625em;
  margin-top: 0;
  cursor: pointer;
}

/* Ajustar el contenedor del switch para centrarlo mejor */
.form-check.form-switch {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 1.5625em;
}
</style>