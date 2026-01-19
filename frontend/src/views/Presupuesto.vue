<script>
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import { onMounted, ref, computed, watch } from 'vue';

export default {
  name: 'Presupuesto',
  components: {
    Header,
    Footer,
  },
  methods: {
    // La sección methods puede quedar vacía o contener métodos que no usen refs de setup
    // Aquí no necesitamos los métodos de validación ni manejo de input del RUT,
    // ya que se manejarán completamente en setup con el watcher.
  },
  setup() {
    // Reactive object to store form data
    const formData = ref({
      rut: null, // Main RUT for client search and contract
      nombres: null,
      apellidos: null,
      direccion: null,
      telefono: null,
      habilitado: null,

      id: null,
      patente: null, // Patente del vehículo seleccionado para el contrato
      valor_pie: null,
      numero_cuotas: 0,
      fecha: '',
      observacion: null,
      vendedor: null, // NUEVO: ID del vendedor seleccionado

      patenteaBuscar: null, // Campo de input para buscar patente
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
      id_vendedor: null,

      precio_venta: null,
      interes_mensual: null,
      valor_cuota: null,
      paymentOption: 'contado', // NUEVO: Opción de pago (contado/credito)
    });

    // States for the user interface
    const isLoading = ref(false);
    const mensaje = ref('');
    const tipoMensaje = ref('');
    const datos = ref([]); // Lista de contratos
    const rutValido = ref(true);
    const mensajeRutInvalido = ref('');
    const listaVehiculos = ref([]); // Lista de vehículos para la tabla
    const vendedores = ref([]);

    // Nivel del usuario desde localStorage
    const nivel = ref(localStorage.getItem('user_nivel'));

    // Variables for the deletion modal
    const registroAEliminarId = ref(null);
    const mostrarModalEliminar = ref(false);

    // Propiedad computada para controlar la visibilidad de las secciones de cálculo/crédito
    const showCalculationSections = computed(() => formData.value.paymentOption === 'credito');

    // Propiedad computada para filtrar la lista de vehículos según la patente a buscar
    const filteredListaVehiculos = computed(() => {
      const searchTerm = formData.value.patenteaBuscar ? formData.value.patenteaBuscar.toLowerCase().trim() : '';
      if (!searchTerm) {
        return listaVehiculos.value; // Si no hay término de búsqueda, muestra todos
      }
      return listaVehiculos.value.filter(vehiculo =>
        vehiculo.patente.toLowerCase().includes(searchTerm)
      );
    });



    // --- NUEVA LÓGICA DE FECHA ---
    /**
     * Function to get the current date in dd/mm/yyyy format.
     * @returns {string} The formatted current date.
     */
    const getFormattedDate = () => {
      const today = new Date();
      const day = String(today.getDate()).padStart(2, '0');
      const month = String(today.getMonth() + 1).padStart(2, '0'); // January is 0!
      const year = today.getFullYear();
      return `${day}/${month}/${year}`;
    };
    // --- FIN DE LA NUEVA LÓGICA DE FECHA ---

    // --- DETECCIÓN DE DISPOSITIVO MÓVIL ---
    /**
     * Detecta si el usuario está accediendo desde un dispositivo móvil
     */
    const isMobile = ref(false);
    const detectMobile = () => {
      isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    };
    // --- FIN DETECCIÓN DE DISPOSITIVO MÓVIL ---

    /**
     * Formats numbers with a period for thousands.
     * @param {number} valor - The number to format.
     * @returns {string} The formatted number or an empty string if invalid.
     */
    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined || isNaN(valor)) {
        return '';
      }
      // Asegurarse de que sea un número antes de formatear
      return new Intl.NumberFormat('de-DE').format(parseFloat(valor));
    };

    /**
     * Validates a Chilean RUT using the Modulo 11 algorithm.
     * @param {string} rut - The RUT string to validate.
     * @returns {boolean} True if the RUT is valid, false otherwise.
     */
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

    /**
     * Handles the input event for the RUT field, performing validation.
     */
    const handleRutInput = () => {
      console.log('handleRutInput llamado.');
      console.log('Valor de formData.rut:', formData.value.rut);

      const rutParaValidar = formData.value.rut ? formData.value.rut.trim() : '';
      rutValido.value = validarRut(rutParaValidar);

      console.log('Valor de RUT limpio para validar:', rutParaValidar);
      console.log('Resultado de validarRut:', rutValido.value);

      if (!rutValido.value && rutParaValidar.length > 0) {
        mensajeRutInvalido.value = 'El RUT ingresado no es válido.';
        limpiarMensaje();
      } else {
        mensajeRutInvalido.value = '';
        if (mensaje.value === 'El RUT ingresado no es válido.' || mensaje.value === 'Por favor, complete el RUT y los Nombres del cliente antes de grabar el presupuesto.') {
          limpiarMensaje();
        }
      }
    };

    // WATCHER: Dispara handleRutInput cada vez que formData.rut cambia
    watch(() => formData.value.rut, (newValue, oldValue) => {
      handleRutInput();
    });

    // Watcher for paymentOption to update valor_pie and numero_cuotas accordingly
    watch(() => formData.value.paymentOption, (newOption) => {
      if (newOption === 'contado') {
        formData.value.valor_pie = formData.value.precio_venta; // Set valor_pie to total sales value
        formData.value.numero_cuotas = 0; // No installments for "contado"
      } else {
        // Reset or set default for "credito" if needed
        // Solo resetear si el precio de venta ya está establecido
        if (formData.value.precio_venta !== null) {
          formData.value.valor_pie = 0; // Default pie for credit
          formData.value.numero_cuotas = 1; // Default for credit
        }
      }
      calcularContrato(); // Recalculate when payment option changes
    });


    // Functions for the deletion modal
    const abrirModalEliminar = (id) => {
      registroAEliminarId.value = id;
      mostrarModalEliminar.value = true;
    };

    const cerrarModalEliminar = () => {
      registroAEliminarId.value = null;
      mostrarModalEliminar.value = false;
    };

    /**
     * Function to show temporary messages to the user.
     * @param {string} texto - The message text.
     * @param {string} tipo - The type of message ('success', 'error', 'info').
     */
    const mostrarMensaje = (texto, tipo) => {
      mensaje.value = texto;
      tipoMensaje.value = tipo;
      setTimeout(limpiarMensaje, 3000);
    };

    // Function to clear messages
    const limpiarMensaje = () => {
      mensaje.value = '';
      tipoMensaje.value = '';
    };

    // Computed Property for Precio Venta (bidirectional formatting)
    const formattedPrecioVenta = computed({
      get() {
        return formatearMilesConPunto(formData.value.precio_venta);
      },
      set(newValue) {
        const cleanValue = String(newValue).replace(/\./g, '').replace(/,/g, '.');
        const numValue = parseFloat(cleanValue);
        formData.value.precio_venta = isNaN(numValue) ? null : numValue;
      }
    });

    // Computed Property for Valor Pie (bidirectional formatting)
    const formattedPie = computed({
      get() {
        return formatearMilesConPunto(formData.value.valor_pie);
      },
      set(newValue) {
        const cleanValue = String(newValue).replace(/\./g, '').replace(/,/g, '.');
        const numValue = parseFloat(cleanValue);
        formData.value.valor_pie = isNaN(numValue) ? null : numValue;
      }
    });


    // --- Functions to get data from APIs ---

    /**
     * Function to get client data by RUT.
     * @param {string} rut - The client RUT to search.
     * @returns {Promise<Object|null>} Client data or null if not found/error.
     */
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

    /**
     * Function to load client data into the form.
     * @param {string} rutABuscar - The RUT to search for.
     */
    const cargarDatosCliente = async (rutABuscar) => {
      if (!rutABuscar) {
        mostrarMensaje('Please enter a RUT to search for the client.', 'error');
        limpiarCamposCliente();
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
          limpiarCamposCliente();
          mostrarMensaje('Client not found.', 'info');
        }
      } catch (error) {
        console.error('Error loading client data:', error);
        mostrarMensaje('Error loading client data.', 'error');
      }
    };

    /**
     * Clears client-related fields in formData.
     */
    const limpiarCamposCliente = () => {
      formData.value.nombres = null;
      formData.value.apellidos = null;
      formData.value.direccion = null;
      formData.value.telefono = null;
      formData.value.habilitado = null;
      formData.value.rut = null;
    };

    /**
     * Function to get vehicle data by license plate.
     * @param {string} patente - The license plate to search.
     * @returns {Promise<Object|null>} Vehicle data or null if not found/error.
     */
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

    /**
     * Function to load vehicle data into the form.
     * @param {string} patenteABuscar - The license plate to search for.
     */
    const cargarDatosVehiculo = async (patenteABuscar) => {
      if (!patenteABuscar) {
        mostrarMensaje('Please enter a license plate to search for the vehicle.', 'error');
        limpiarCamposVehiculo();
        return;
      }
      try {
        const vehiculoData = await obtenerVehiculo(patenteABuscar);
        if (vehiculoData) {
          formData.value.tipo_automovil = vehiculoData.tipo_automovil;
          formData.value.marca = vehiculoData.marca;
          formData.value.modelo = vehiculoData.modelo;
          formData.value.agno = vehiculoData.agno;
          formData.value.numero_motor = vehiculoData.numero_motor;
          formData.value.numero_chasis = vehiculoData.numero_chasis;
          formData.value.color = vehiculoData.color;
          formData.value.kilometraje = vehiculoData.kilometraje;
          formData.value.marca_descripcion = vehiculoData.marca_descripcion;
          formData.value.vehiculo_descripcion = vehiculoData.vehiculo_descripcion;

          // Solo actualiza el precio_venta si es un nuevo presupuesto (no estamos editando uno existente)
          // O si el precio de venta actual en el formulario está vacío/nulo.
          if (formData.value.id === null || formData.value.precio_venta === null || formData.value.precio_venta === 0) {
            formData.value.precio_venta = vehiculoData.precio_venta;
          }

          formData.value.patente = vehiculoData.patente; // Assign the vehicle license plate to the contract's 'patente' field

          console.warn('Vehicle data loaded:', vehiculoData);
          // Al cargar datos del vehículo, si se selecciona un vehículo,
          // establecemos la opción de pago por defecto a crédito y valor pie a 0.
          // Solo si no estamos cargando un contrato existente que ya tiene una opción de pago.
          if (formData.value.id === null) { // Solo si es un nuevo presupuesto
            formData.value.paymentOption = 'credito';
            formData.value.valor_pie = 0;
            formData.value.numero_cuotas = 1; // O el valor por defecto que desees para crédito
          }

        } else {
          console.warn('No data found for license plate:', patenteABuscar);
          limpiarCamposVehiculo();
          mostrarMensaje('Vehicle not found.', 'info');
          // Si no se encuentra el vehículo, resetea la opción de pago.
          formData.value.paymentOption = 'contado';
          formData.value.valor_pie = null;
          formData.value.numero_cuotas = 0;
        }
        calcularContrato(); // Recalcular después de cargar los datos del vehículo
      } catch (error) {
        console.error('Error loading vehicle data:', error);
        mostrarMensaje('Error loading vehicle data.', 'error');
      }
    };

    /**
     * Clears vehicle-related fields in formData.
     */
    const limpiarCamposVehiculo = () => {
      formData.value.tipo_automovil = null;
      formData.value.marca = null;
      formData.value.modelo = null;
      formData.value.agno = null;
      formData.value.numero_motor = null;
      formData.value.numero_chasis = null;
      formData.value.color = null;
      formData.value.kilometraje = null;
      formData.value.marca_descripcion = null;
      formData.value.vehiculo_descripcion = null;
      formData.value.patente = null;
      // También se debe limpiar el valor de la cuota y el pie al limpiar el vehículo
      formData.value.precio_venta = null;
      formData.value.interes_mensual = null;
      formData.value.valor_cuota = null;
      formData.value.valor_pie = null;
      formData.value.numero_cuotas = 0;
    };

    /**
     * Function to load the list of all available vehicles.
     * Assumes an API endpoint that returns a list of vehicles.
     */
    const cargarListaAutomoviles = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}vehiculos/`;
        console.log('Consulting all vehicles at:', apiUrl);
        const response = await fetch(apiUrl);

        if (!response.ok) {
          console.error(`Error loading vehicle list: ${response.status} - ${response.statusText}`);
          mostrarMensaje('Error loading vehicle list.', 'error');
          return;
        }

        const data = await response.json();
        listaVehiculos.value = data.data || [];
        console.log('Lista de vehículos cargada:', listaVehiculos.value);

      } catch (error) {
        console.error('Connection error loading vehicle list:', error);
        mostrarMensaje('Connection error loading vehicle list.', 'error');
        listaVehiculos.value = [];
      }
    };



    /**
     * Function to select an automobile from the list and load its data into the form.
     * @param {Object} automovil - The automobile object selected from the list.
     */
    const seleccionarAutomovil = async (automovil) => {
      if (automovil && automovil.patente) {
        formData.value.patenteaBuscar = automovil.patente; // Sincroniza el campo de búsqueda con la patente seleccionada
        await cargarDatosVehiculo(automovil.patente);
        mostrarMensaje(`Vehículo ${automovil.patente} seleccionado.`, 'info');
      } else {
        mostrarMensaje('Error al seleccionar el vehículo. Patente no encontrada.', 'error');
      }
    };

    /**
     * Maneja la búsqueda de vehículos por patente o muestra todos si el campo está vacío.
     */
    const handleSearchPatente = async () => {
      const patente = formData.value.patenteaBuscar ? formData.value.patenteaBuscar.trim() : '';

      if (patente) {
        // Si hay una patente en el campo de búsqueda, intenta cargar ese vehículo específico.
        const vehiculoData = await obtenerVehiculo(patente);
        if (vehiculoData) {
          // Si se encuentra, añade/actualiza en la lista de vehículos temporalmente para que la tabla lo muestre
          listaVehiculos.value = [vehiculoData]; // Mostrar solo el vehículo encontrado en la tabla
          cargarDatosVehiculo(patente); // Carga los datos en el formulario principal
          mostrarMensaje(`Vehículo ${patente} encontrado y seleccionado.`, 'success');
        } else {
          listaVehiculos.value = []; // Si no se encuentra, vacía la lista de la tabla
          limpiarCamposVehiculo(); // Limpia los campos del formulario principal
          mostrarMensaje('Vehículo con patente ' + patente + ' no encontrado.', 'info');
        }
      } else {
        // Si el campo de búsqueda está vacío, carga todos los vehículos.
        await cargarListaAutomoviles(); // Vuelve a cargar todos los vehículos
        limpiarCamposVehiculo(); // Limpia los campos del formulario principal del vehículo
        mostrarMensaje('Mostrando todos los vehículos registrados.', 'info');
      }
    };
    // --- Functions for the contract list and table actions ---

    /**
     * Function to load selected contract data from the table into the form.
     * @param {Object} contrato - The contract object to load.
     */

    /**
     * Function to calculate the installment value based on form data.
     */
    const calcularContrato = () => {
      let precioVenta = parseFloat(formData.value.precio_venta);
      let valor_pie = parseFloat(formData.value.valor_pie);
      let numeroCuotas = parseInt(formData.value.numero_cuotas);
      let interesMensual = parseFloat(formData.value.interes_mensual) / 100;

      // Reset values if invalid
      if (isNaN(precioVenta)) precioVenta = 0;
      if (isNaN(valor_pie)) valor_pie = 0;
      if (isNaN(numeroCuotas)) numeroCuotas = 0;
      if (isNaN(interesMensual)) interesMensual = 0;

      // Handle 'contado' payment option
      if (formData.value.paymentOption === 'contado') {
        formData.value.valor_pie = precioVenta; // Whole amount is the down payment
        formData.value.numero_cuotas = 0; // No installments
        formData.value.interes_mensual = 0; // No interest
        formData.value.valor_cuota = precioVenta; // Total price is the 'installment' (single payment)
        mostrarMensaje('Cálculo realizado (pago al contado).', 'info');
        return;
      }

      const montoAFinanciar = precioVenta - valor_pie;
      let valorCuota;

      if (montoAFinanciar <= 0) {
        formData.value.valor_cuota = 0;
        mostrarMensaje('Cálculo realizado (no se requiere financiación).', 'info');
        return;
      }

      if (numeroCuotas <= 0) { // For cases where "credito" is selected but 0 installments
        formData.value.valor_cuota = montoAFinanciar;
        mostrarMensaje('Cálculo realizado (pago único con crédito).', 'info');
        return;
      }

      if (interesMensual === 0) {
        valorCuota = montoAFinanciar / numeroCuotas;
      } else {
        const i = interesMensual;
        const n = numeroCuotas;
        const P = precioVenta - valor_pie;


        // Formula para la cuota de un préstamo (cuota fija)
        valorCuota = P * (i * Math.pow((1 + i), n)) / (Math.pow((1 + i), n) - 1);
      }


      // --- INICIO DE LA LÓGICA DE REDONDEO ---
      // Convertir a entero para trabajar con el redondeo
      let valorCuotaEntero = parseInt(valorCuota);

      // Obtener los tres últimos dígitos
      const ultimosTresDigitos = valorCuotaEntero % 1000;

      if (ultimosTresDigitos > 500) {
        // Redondear hacia arriba al próximo millar
        valorCuota = Math.ceil(valorCuotaEntero / 1000) * 1000;
      } else {
        // Redondear hacia abajo al millar más cercano (o mantener si ya0000000000000000000000000000000000000000000 es millar exacto o menor a 500)
        valorCuota = Math.floor(valorCuotaEntero / 1000) * 1000;
      }
      // --- FIN DE LA LÓGICA DE REDONDEO ---
      formData.value.valor_cuota = parseInt(valorCuota);

      mostrarMensaje('Cálculo del contrato realizado.', 'success');
    };

    // Watchers for calculation fields to trigger recalculation
    watch([
      () => formData.value.precio_venta,
      () => formData.value.valor_pie,
      () => formData.value.numero_cuotas,
      () => formData.value.interes_mensual,
      // Solo disparar recalculación si precio_venta no es null y paymentOption es crédito
      // El watcher de paymentOption ya maneja su propio cálculo.
    ], () => {
      // Solo recalcular si se ha seleccionado un vehículo (patente) y la opción de pago es 'credito'
      // El watcher de paymentOption ya se encarga de 'contado'.
      if (formData.value.patente && formData.value.paymentOption === 'credito') {
        calcularContrato();

        formData.value.valor_cuota = parseInt(valorCuota); // Asegurarse de que sea un entero final
        mostrarMensaje('Cálculo del contrato realizado.', 'success');
      }
    }, { deep: true });

    /**
     * Function to handle form submission (for saving/updating).
     */
    const handleSubmit = () => {

      // Basic validations before sending
      if (!formData.value.rut || !validarRut(formData.value.rut)) {
        mostrarMensaje('El RUT del cliente no es válido o está vacío.', 'error');
        console.log('Validación fallida: RUT inválido o vacío.');
        return;
      }

      if (!formData.value.patente) {
        mostrarMensaje('Please enter the vehicle\'s License Plate.', 'error');
        console.log('Validación fallida: Patente del vehículo vacía.');
        return;
      }

      if (!formData.value.id_vendedor) {
        mostrarMensaje('Por favor, seleccione un vendedor.', 'error');
        return;
      }

      // Validations specific to 'credito' option
      if (formData.value.paymentOption === 'credito') {
        if (formData.value.valor_pie === null || formData.value.valor_pie === '') {
          mostrarMensaje('Por favor, ingrese el valor del pie.', 'error');
          console.log('Validación fallida (Crédito): Valor de pie vacío.');
          return;
        }
        if (formData.value.numero_cuotas <= 0) {
          mostrarMensaje('Para pago a crédito, el número de cuotas debe ser mayor a 0.', 'error');
          console.log('Validación fallida (Crédito): Número de cuotas <= 0.');
          return;
        }
        if (formData.value.interes_mensual === null || formData.value.interes_mensual === '') {
          mostrarMensaje('Por favor, ingrese el interés mensual.', 'error');
          console.log('Validación fallida (Crédito): Interés mensual vacío.');
          return;
        }
      }

      if (formData.value.numero_cuotas < 0 || formData.value.numero_cuotas > 60) {
        mostrarMensaje('Please enter a number of installments between 0 and 60.', 'error');
        console.log('Validación fallida: Número de cuotas fuera de rango.');
        return;
      }

      if (formData.value.precio_venta === null || formData.value.precio_venta === '') {
        mostrarMensaje('Please enter the Sales Price.', 'error');
        console.log('Validación fallida: Valor de venta total vacío.');
        return;
      }
      console.log('Validaciones pasadas, llamando a guardarRegistro()');

      isLoading.value = true;
      guardarRegistro();
    };

    /**
     * Function to handle saving a contract record (create or update).
     */
    const guardarRegistro = async () => {
      isLoading.value = true;
      console.log('Intentando guardar registro...');
      try {
        const isUpdate = formData.value.id !== null;
        const apiUrl = isUpdate
          ? `${import.meta.env.VITE_API_URL}presupuesto/${formData.value.id}/`
          : `${import.meta.env.VITE_API_URL}presupuesto/`;
        const method = isUpdate ? 'PUT' : 'POST';

        let rutVendedorParaEnviar = '';
        if (formData.value.id_vendedor) {
          const vendedorSeleccionado = vendedores.value.find(
            (v) => v.id === formData.value.id_vendedor
          );

          if (vendedorSeleccionado) {
            rutVendedorParaEnviar = vendedorSeleccionado.rut;
          }
        }

        const payload = {
          rut_cliente: formData.value.rut,
          patente_vehiculo: formData.value.patente,
          nombre_cliente: formData.value.nombres, // Asumiendo que quieres guardar el nombre del cliente
          monto_a_financiar: formData.value.precio_venta - formData.value.valor_pie,
          tipo_pago: formData.value.paymentOption,
          valor_pie: formData.value.valor_pie,
          numero_cuotas: formData.value.numero_cuotas,
          interes_mensual: formData.value.interes_mensual,
          valor_cuota: formData.value.valor_cuota,
          precio_venta: formData.value.precio_venta, // Incluir el precio de venta total
          rut_vendedor: rutVendedorParaEnviar,
          // fecha_creacion se generará automáticamente en el backend si es un campo DateTimeField(auto_now=True)
        };

        console.log("PAYLOAD ENVIADO A /presupuesto/:", JSON.stringify(payload, null, 2));
        console.log("API URL:", apiUrl);
        console.log("Method:", method);

        const response = await fetch(apiUrl, {
          method: method,
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          console.log('Respuesta exitosa de la API.');
          mostrarMensaje(`Contrato ${isUpdate ? 'actualizado' : 'guardado'} con éxito!`, 'success');
          cargarListaDeContratos();
          limpiarFormulario();
          await cargarListaAutomoviles(); // Recargar la lista de automóviles después de guardar
        } else {
          const errorData = await response.json();
          console.error('Error al guardar registro:', errorData);
          mostrarMensaje(`Error ${isUpdate ? 'actualizando' : 'guardando'} contrato: ${errorData.mensaje || response.statusText}`, 'error');
        }
      } catch (error) {
        console.error('Excepción al guardar registro:', error);
        mostrarMensaje('Connection error with the server.', 'error');
      } finally {
        isLoading.value = false;
        console.log('Finalizado el intento de guardar registro.');
      }
    };


    /**
     * Function to delete a contract record (called from the confirmation modal).
     */
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
          await cargarListaAutomoviles(); // Recargar la lista de automóviles después de eliminar
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

    /**
     * Function to load the list of existing contracts and display them in the table.
     */
    const cargarListaDeContratos = async () => {
      try {
        const apiUrl = `${import.meta.env.VITE_API_URL}presupuesto/`;

        console.log(apiUrl);

        const response = await fetch(apiUrl);
        if (response.ok) {
          const data = await response.json();
          // Filtrar presupuestos descartados (estado = 1)
          datos.value = data.data.filter(contrato => contrato.estado !== 1);
        } else {
          console.error('Error loading contract list:', response.statusText);
          mostrarMensaje('Error loading contract list.', 'error');
        }
      } catch (error) {
        console.error('Connection error loading contract list:', error);
        mostrarMensaje('Connection error loading contract list.', 'error');
      }
    };

    /**
     * Auxiliary function to clear the form fields.
     */
    const limpiarFormulario = () => {
      formData.value = {
        rut: null,
        nombres: null,
        apellidos: null,
        direccion: null,
        telefono: null,
        habilitado: null,
        observacion: null,
        numero_cuotas: 0,
        id: null,
        patente: null,
        valor_pie: null,
        fecha: '',
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
        interes_mensual: null,
        valor_cuota: null,
        paymentOption: 'contado', // Reset payment option to default
        id_vendedor: null, // Almacenará el ID del vendedor
      };
      rutValido.value = true;
      mensajeRutInvalido.value = '';
      limpiarMensaje();
      const vendedores = ref([]);
      // No mostrar mensaje de "Form cleared" al inicio o al cargar un contrato,
      // solo cuando el usuario lo active explícitamente con un botón "Limpiar".
      // mostrarMensaje('Form cleared.', 'info');
    };


    // NUEVO: Función para obtener la lista de vendedores desde la API
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

    /**
     * Method to navigate to contract and liability letter routes.
     * @param {string} contractPatente - The license plate of the contract.
     * @param {number} pagina - 0 for ContratoCompraVenta, 1 for CartaResponsabilidad.
     */
    const goToContrato = (contractPatente, pagina) => {
      const rutCliente = formData.value.rut;
      console.warn("Navegación a otras rutas no implementada en este contexto de Canvas.");
      console.log(`Intentando ir a página ${pagina} con RUT: ${rutCliente}, Patente: ${contractPatente}`);
      // If you have Vue Router configured, uncomment this:
      /*
      import { useRouter } from 'vue-router';
      const router = useRouter();
      if (pagina === 0) {
        router.push({
          name: 'ContratoCompraVenta',
          params: { rut: rutCliente, patente: contractPatente }
        });
      }
      if (pagina === 1) {
        router.push({
          name: 'CartaResponsabilidad',
          params: { rut: rutCliente, patente: contractPatente }
        });
      }
      */
    };


    // Lifecycle hook: executes when the component has been mounted in the DOM
    onMounted(() => {
      console.log('Componente Presupuesto montado correctamente.');

      detectMobile(); // Detectar si es móvil
      cargarListaAutomoviles();
      obtenerVendedores();
      // NUEVO: Asignar la fecha actual al campo 'fecha' cuando se monta el componente
      formData.value.fecha = getFormattedDate();
    });

    // Return variables and functions that will be available in the template
    return {
      formData,
      isLoading,
      mensaje,
      tipoMensaje,
      datos,
      rutValido,
      mensajeRutInvalido,
      mostrarModalEliminar,
      listaVehiculos,
      isMobile, // Exponer la variable para detectar móvil

      showCalculationSections, // Exponer la propiedad computada
      filteredListaVehiculos, // Exponer la nueva propiedad computada

      // Functions (exposed from setup)
      formatearMilesConPunto,
      validarRut,
      handleRutInput,
      abrirModalEliminar,
      cerrarModalEliminar,
      mostrarMensaje,
      limpiarMensaje,
      obtenerCliente,
      cargarDatosCliente,
      obtenerVehiculo,
      cargarDatosVehiculo,
      calcularContrato,
      handleSubmit,
      guardarRegistro,
      eliminarRegistroConfirmado,
      cargarListaDeContratos,
      limpiarFormulario,
      formattedPrecioVenta, // Exponer la propiedad computada para el precio de venta
      formattedPie,
      goToContrato,
      seleccionarAutomovil,
      handleSearchPatente, // Exponer la nueva función de búsqueda
      obtenerVendedores,
      vendedores,
      nivel,

    };
  },
};
</script>

<template>
  <!-- Header solo visible en desktop -->
  <Header v-if="!isMobile"></Header>

  <!-- Logo siempre visible pero responsivo -->
  <div style="text-align: center; padding: 20px 10px;">
    <img src="/img/core-img/logo.png" alt="logo" class="logo-responsive" />
  </div>

  <div class="page-container">
    <br></br>
    <form @submit.prevent="handleSubmit">

      <h3>Cotización</h3>
      <br>
      <div style="text-align: right; font-weight: bold;">{{ formData.fecha }}</div>
      <br>
      <br>

      <div class="input-section">
        <label for="rut">RUT del Cliente:</label>
        <input type="text" id="rut" v-model="formData.rut" placeholder="Ej: 12345678-9" class="form-control">
      </div>

      <div class="input-section">
        <label for="nombresInput">Nombres del Cliente:</label>
        <input type="text" id="nombresInput" v-model="formData.nombres" placeholder="Ej: Juan Pérez"
          class="form-control">
      </div>

      <div class="input-section">
        <label for="vendedor">Vendedor</label>

        <select id="vendedor" v-model="formData.id_vendedor" class="form-control">
          <option :value="null" disabled>Seleccione un vendedor</option>
          <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">
            {{ vendedor.rut }} - {{ vendedor.nombres }} {{ vendedor.apellidos }}
          </option>
        </select>

      </div>

      <div class="input-section mt-4">
        <label for="patenteaBuscar">Buscar Patente:</label>
        <input type="text" id="patenteaBuscar" v-model="formData.patenteaBuscar" placeholder="Ej: ABCD12"
          class="form-control">
        <button type="button" @click="handleSearchPatente" class="btn btn-primary">Buscar Vehículo</button>
      </div>

      <div class="automoviles-list-section mt-4">
        <h4>Automóviles Disponibles</h4>
        <table class="table table-striped data-table">
          <thead>
            <tr>
              <th style="text-align: center;">Patente</th>
              <th style="text-align: center;">Marca</th>
              <th style="text-align: center;">Modelo</th>
              <th style="text-align: center;">Año</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredListaVehiculos.length === 0">
              <td colspan="4" class="text-center">No hay automóviles registrados que coincidan.</td>
            </tr>
            <tr v-for="automovil in filteredListaVehiculos" :key="automovil.patente"
              @click="seleccionarAutomovil(automovil)" class="cursor-pointer">
              <td>{{ automovil.patente }}</td>
              <td>{{ automovil.marca_descripcion || 'N/A' }}</td>
              <td>{{ automovil.modelo || 'N/A' }}</td>
              <td>{{ automovil.agno || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isLoading" class="loading-message">Cargando información...</div>
      <div v-if="mensaje" :class="tipoMensaje === 'error' ? 'error-message' : 'success-message'">{{ mensaje }}</div>


      <div v-if="formData.patente" class="vehicle-info-section">
        <h4>Información del Vehículo:</h4>
        <table class="data-table">
          <tr>
            <td class="label-col">Vehículo</td>
            <td class="data-col">{{ formData.vehiculo_descripcion || 'N/A' }}</td>
            <td class="label-col">Marca</td>
            <td class="data-col">{{ formData.marca_descripcion || 'N/A' }}</td>
          </tr>
          <tr>
            <td class="label-col">Modelo</td>
            <td class="data-col">{{ formData.modelo || 'N/A' }}</td>
            <td class="label-col">Año</td>
            <td class="data-col">{{ formData.agno || 'N/A' }}</td>
          </tr>

          <tr>
            <td class="label-col">Nº de motor</td>
            <td class="data-col">{{ formData.numero_motor || 'N/A' }}</td>
            <td class="label-col">Nº de chasis</td>
            <td class="data-col">{{ formData.numero_chasis || 'N/A' }}</td>
          </tr>

          <tr>
            <td class="label-col">Color</td>
            <td class="data-col">{{ formData.color || 'N/A' }}</td>
            <td class="label-col">Patente</td>
            <td class="data-col">{{ formData.patente || 'N/A' }}</td>
          </tr>
          <tr>
            <td class="label-col">Kilometraje</td>
            <td class="data-col">{{ formatearMilesConPunto(formData.kilometraje) || 'N/A' }}</td>
          </tr>
          <tr>
            <td class="label-col">Precio Venta ($):</td>
            <td class="data-col">
              <input style="font-weight: bold;" type="text" id="precioVenta" v-model="formattedPrecioVenta"
                class="form-control">
            </td>
          </tr>
        </table>

        <table class="data-table1 mt-4">
          <tr>
            <td class="label-col">
              Seleccione Opción de Pago:
            </td>
            <td class="data-col">

              <div class="radio-group">
                <input type="radio" value="contado" v-model="formData.paymentOption">
                &nbsp; Contado
                &nbsp;
                <input type="radio" value="credito" v-model="formData.paymentOption">
                &nbsp; Crédito
              </div>
            </td>
          </tr>
        </table>

        <table class="data-table1" v-if="showCalculationSections">
          <tr>
            <td class="label-col">Interés Mensual (%):</td>
            <td class="data-col">
              <input type="number" v-model.number="formData.interes_mensual" min="0" step="0.1" id="interes"
                class="form-control">
            </td>
          </tr>
        </table>

        <div class="calculation-section">
          <h4>Forma De Pago</h4>
          <div class="form-group">
            <label for="valorPie">Valor Pie ($):</label>
            <input type="text" id="valorPie" v-model="formattedPie" class="form-control" min="0"
              :disabled="formData.paymentOption === 'contado'">
          </div>
          <div class="form-group">
            <label for="numCuotas">Número de Cuotas:</label>
            <select id="numCuotas" v-model.number="formData.numero_cuotas" class="form-control"
              :disabled="formData.paymentOption === 'contado'">
              <option v-if="formData.paymentOption === 'contado'" :value="0">0</option>
              <template v-else>
                <option v-for="n in 60" :key="n" :value="n">{{ n }}</option>
              </template>
            </select>
          </div>

          <div class="results-section" v-if="formData.valor_cuota !== null">
            <p>Monto a Financiar: <strong>{{ formatearMilesConPunto(formData.precio_venta - formData.valor_pie)
                }}</strong></p>
            <p>Valor de Cada Cuota (con interés): <strong style="font-size: medium;">{{
              formatearMilesConPunto(formData.valor_cuota) }}</strong></p>


            <button type="button" @click="limpiarFormulario" class="btn btn-secondary mt-3 ms-2">Limpiar</button>
          </div>
          <div v-else>
            <p>Ingrese los valores para calcular las cuotas.</p>
          </div>
        </div>
      </div>
    </form>



    <div v-if="mostrarModalEliminar" class="modal-overlay">
      <div class="modal-content">
        <h4>Confirmar Eliminación</h4>
        <p>¿Está seguro de que desea eliminar el contrato ID: <strong>{{ registroAEliminarId }}</strong>?</p>
        <button @click="eliminarRegistroConfirmado" class="btn btn-danger me-2">Sí, Eliminar</button>
        <button @click="cerrarModalEliminar" class="btn btn-secondary">Cancelar</button>
      </div>
    </div>
  </div>
  <Footer></Footer>
</template>

<style scoped>
/* Tu CSS existente */
.negrita {
  font-weight: bold;
}

.page-container {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: black;
}

h2,
h3 {
  text-align: center;
  color: #333;
  margin-bottom: 25px;
}

h3 {
  color: #555;
  margin-top: 25px;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.input-section label {
  font-weight: bold;
  flex-shrink: 0;
}

.form-control {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1em;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.loading-message,
.error-message,
.success-message {
  text-align: center;
  font-size: 1.1em;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}

.loading-message {
  background-color: #e0f7fa;
  color: #007bff;
}

.error-message {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #d32f2f;
}

.success-message {
  background-color: #e6ffe6;
  color: #008000;
  border: 1px solid #008000;
}

.vehicle-info-section,
.calculation-section {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.data-table1 {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.data-table th,
.data-table td {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  vertical-align: top;
}

.data-table th {
  background-color: #f0f0f0;
  font-weight: bold;
  text-align: left;
}

.data-table .label-col {
  font-weight: bold;
  width: 30%;
  background-color: #f5f5f5;
}

.data-table .data-col {
  font-weight: normal;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.results-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #e6ffe6;
  border: 1px solid #4CAF50;
  border-radius: 5px;
  color: #333;
}

.results-section p {
  margin: 5px 0;
  font-size: 1.1em;
}

.results-section strong {
  color: #006400;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.modal-content h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.modal-content p {
  margin-bottom: 20px;
  color: #555;
}

.automoviles-list-section table tr.cursor-pointer {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.automoviles-list-section table tr.cursor-pointer:hover {
  background-color: #e0e0e0;
}

.oculta-por-defecto {
  display: none;
}


/* Print styles */
@media print {


  .footer,
  .data-table1,
  .message-success,
  .message-error,
  .loading-message,
  .error-message,
  .btn,
  .results-section button,
  .contract-list-section,
  .modal-overlay,
  .calculation-section,
  .payment-option-section,
  .automoviles-list-section {
    /* Oculta la nueva sección de automóviles al imprimir */
    display: none !important;
  }

  .oculta-por-defecto {
    display: none !important;
  }

  .page-container {
    width: 100%;
    max-width: 100%;
    margin: 0 auto;
    padding: 0;
    box-shadow: none;
    border: none;
  }

  h2,
  h3,
  h4 {
    text-align: center;
    color: black;
    margin-bottom: 5px;
    margin-top: 15px;
  }

  .vehicle-info-section {
    padding: 0;
    border: none;
    background-color: transparent;
  }

  .data-table {
    width: 90%;
    margin: 10px auto;
    border-collapse: collapse;
  }

  .data-table th,
  .data-table td {
    border: 1px solid #ccc !important;
    padding: 6px 10px;
    vertical-align: top;
    font-size: 0.9em;
  }

  .data-table .label-col {
    background-color: #f0f0f0 !important;
    font-weight: bold;
  }

  .data-table .data-col {
    font-weight: normal;
  }

  body {
    font-size: 10pt;
    color: black;
  }

  html,
  body {
    margin: 10;
    padding: 10;
  }

  .results-section {
    margin-top: 20px;
    padding: 15px;
    background-color: transparent;
    border: none;
    border-radius: 0;
    color: #333;
    text-align: center;
  }

  .results-section p {
    margin: 5px 0;
    font-size: 1.1em;
  }

  .results-section strong {
    color: #000;
  }
}

/* Responsive Styles */
@media (max-width: 768px) {
  .page-container {
    margin: 10px;
    padding: 10px;
  }

  /* Make logo responsive in template (overriding inline style if possible via class or just relying on max-width if added to inline) */
  /* Note: The logo has inline styles, so we might need to change the template or use !important if we can't touch template easily. 
     Better to update the template for the logo too. */

  .input-section {
    flex-direction: column;
    align-items: stretch;
  }

  .input-section label {
    margin-bottom: 5px;
  }

  .input-section .btn {
    width: 100%;
    margin-top: 10px;
  }

  /* Responsive Tables for Vehicle Info (Stacking key-value pairs) */
  .vehicle-info-section .data-table,
  .vehicle-info-section .data-table tbody,
  .vehicle-info-section .data-table tr,
  .vehicle-info-section .data-table td {
    display: block;
    width: 100%;
    box-sizing: border-box;
  }

  .vehicle-info-section .data-table tr {
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
  }

  /* Hide empty rows if any */
  .vehicle-info-section .data-table tr:empty {
    display: none;
  }

  .vehicle-info-section .data-table td {
    padding: 8px 10px;
    text-align: left;
    border: none;
    border-bottom: 1px solid #eee;
  }

  .vehicle-info-section .data-table td:last-child {
    border-bottom: none;
  }

  .vehicle-info-section .data-table .label-col {
    background-color: #f8f9fa;
    font-weight: bold;
    color: #333;
    width: 100%;
    /* Override the 30% width */
  }

  /* Payment Option Table */
  .data-table1,
  .data-table1 tbody,
  .data-table1 tr,
  .data-table1 td {
    display: block;
    width: 100%;
  }


  .data-table1 td {
    padding: 10px 0;
  }

  /* Automoviles List - Horizontal Scroll */
  .automoviles-list-section {
    overflow-x: auto;
  }

  .automoviles-list-section table {
    min-width: 600px;
    /* Ensure it doesn't get too squashed */
  }
}

/* Logo Responsive Styles */
.logo-responsive {
  width: 280px;
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

/* Ajustes adicionales para móvil */
@media (max-width: 480px) {
  .logo-responsive {
    width: 200px;
    max-width: 90%;
  }
}
</style>