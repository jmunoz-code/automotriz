<script>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router'; // Importar useRoute para acceder a los parámetros de la URL
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';

export default {
  components: {
    Header,
    Footer,
  },
  setup() {
    
    const route = useRoute();
    
    const formatearMilesConPunto = (valor) => {
      if (valor === null || valor === undefined || isNaN(valor)) {
        return '';
      }
      return new Intl.NumberFormat('de-DE').format(parseFloat(valor));
    };

    return {
      formatearMilesConPunto,
    };
  },
  data() {
    return {
      fechaContrato: 'Cargando...',

      nombreEmpresaVendedor: 'Nicolás Automotriz SPA',
      rutEmpresaVendedor: '76.692.119-1',
      cedulaEmpresaVendedor: '76.692.119-1',
      calleEmpresaVendedor: 'Patricio Lynch Nº 1.000',

      nombreComprador: 'Cargando...',
      apellidoComprador: 'Cargando...',
      rutComprador: 'Cargando...',
      direccionComprador: 'Cargando...',
      telefonoComprador: 'Cargando...',
      emailComprador: 'Cargando...',

      vehiculoTipo: 'Cargando...',
      vehiculoMarca: 'Cargando...',
      vehiculoModelo: 'Cargando...',
      vehiculoAgno: 'Cargando...',
      vehiculoNumeroMotor: 'Cargando...',
      vehiculoNumeroChasis: 'Cargando...',
      vehiculoColor: 'Cargando...',
      vehiculoPatente: 'Cargando...',
      vehiculoKilometraje: 'Cargando...',

      piePago: 'Cargando...',
      numCuotas: 'Cargando...',
      valorCuota: 'Cargando...',
      fechaInicioCuotas: 'Cargando...',
      fechaFinCuotas: 'Cargando...',
      contratoObservacion: 'Cargando...',
      contratoFecha: 'Cargando...',
      precioVentaTotalContrato: 'Cargando...', // Agregado para el valor_venta_total del contrato

      isLoading: true,
      error: null
    };
  },

  props: {
    // Estas props son recibidas del router cuando navegas a esta ruta
    rut: {
      type: String,
      required: true
    },
    patente: {
      type: String,
      required: true
    },
    idPrep: { // Esta es la prop que contendrá el ID del presupuesto
      type: Number, // Puede ser Number o String si viene de la URL
      required: true
    },
    pagina: { // Esta es la prop que contendrá el ID del presupuesto
      type: Number, // Puede ser Number o String si viene de la URL
      required: true
    },

    contract: { // Se mantiene, aunque el fetch principal usa los params
      type: Object,
      required: false,
      default: () => ({})
    },
  },

  async mounted() {
    // DEBUGGING: Imprime las props recibidas para verificar sus valores.
    console.log('DEBUG: Prop "rut" recibida:', this.rut);
    console.log('DEBUG: Prop "patente" recibida:', this.patente);
    console.log('DEBUG: Prop "idPrep" recibida (ID del Presupuesto):', this.idPrep); // Verifica que idPrep llegue aquí y tenga el valor correcto
    console.log('DEBUG: Prop "pagina:', this.pagina); // Verifica que idPrep llegue aquí y tenga el valor correcto

    this.rutComprador = this.rut;
    this.vehiculoPatente = this.patente;
    // alert(this.idPrep); // Puedes comentar o quitar esta alerta una vez que confirmes que funciona.
    // this.idPrep = this.idPrep; // ¡ELIMINAR ESTA LÍNEA! Es redundante y una mala práctica.

    this.isLoading = true;
    this.error = null;

    try {
      // Se hacen las 3 llamadas a la API en paralelo
      const [clienteApiResponse, vehiculoApiResponse, contratoApiResponse] = await Promise.all([
        this.fetchClienteData(this.rut),
        this.fetchVehiculoData(this.patente),
        // CORRECCIÓN CLAVE AQUÍ: Pasa SOLO los 3 argumentos que fetchContratoData espera.
        // `this.idPrep` es el ID del presupuesto que necesitas para la búsqueda del contrato.
        this.fetchContratoData(this.idPrep)
      ]);

      this.populateClienteData(clienteApiResponse);
      this.populateVehiculoData(vehiculoApiResponse);
      this.populateContratoData(contratoApiResponse);

      // La fecha del contrato principal debería ser la fecha actual del día en que se genera.
      const today = new Date();
      const options = { day: '2-digit', month: 'long', year: 'numeric' };
      this.fechaContrato = today.toLocaleDateString('es-ES', options).toUpperCase();

    } catch (err) {
      console.error("Error al cargar los datos del contrato:", err);
      this.error = "Error al cargar los datos. Por favor, inténtelo de nuevo más tarde.";

      // Poner todos los campos en "No disponible" en caso de error
      this.nombreComprador = 'No disponible';
      this.apellidoComprador = 'No disponible';
      this.rutComprador = 'No disponible';
      this.direccionComprador = 'No disponible';
      this.telefonoComprador = 'No disponible';
      this.emailComprador = 'No disponible';

      this.vehiculoTipo = 'No disponible';
      this.vehiculoMarca = 'No disponible';
      this.vehiculoModelo = 'No disponible';
      this.vehiculoAgno = 'No disponible';
      this.vehiculoNumeroMotor = 'No disponible';
      this.vehiculoNumeroChasis = 'No disponible';
      this.vehiculoColor = 'No disponible';
      this.vehiculoPatente = 'No disponible';
      this.vehiculoKilometraje = 'No disponible';

      this.piePago = 'No disponible';
      this.numCuotas = 'No disponible';
      this.valorCuota = 'No disponible';
      this.fechaInicioCuotas = 'No disponible';
      this.fechaFinCuotas = 'No disponible';
      this.contratoObservacion = 'No disponible';
      this.contratoFecha = 'No disponible';
      this.precioVentaTotalContrato = 'No disponible';
      this.pagina = '';

    } finally {
      this.isLoading = false;
    }
  },
  methods: {

    async fetchClienteData(rut) {

      const url = `${import.meta.env.VITE_API_URL}clientes/${rut}/`;

      console.log('DEBUG: fetchClienteData - URL de API para cliente:', url);

      try {
        const response = await fetch(url);
        console.log("DEBUG: fetchClienteData - Response object:", response);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        return data;
      } catch (error) {
        console.error("ERROR: Error al obtener datos del cliente:", error);
        throw error;
      }
    },

    async fetchVehiculoData(patente) {
      const url = `${import.meta.env.VITE_API_URL}vehiculos/${patente}/`;

      console.log('DEBUG: fetchVehiculoData - URL de API para vehículo:', url);

      try {
        const response = await fetch(url);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        return data;
      } catch (error) {
        console.error("ERROR: Error al obtener datos del vehículo:", error);
        throw error;
      }
    },

    // La firma de esta función está correcta (rut, idPrep, patente)
    async fetchContratoData(idPrep) { // Asegúrate de que solo se pasa idPrep aquí desde mounted()
      const url = `${import.meta.env.VITE_API_URL}presupuesto/${idPrep}/`; // URL para llamar a Clase2
      console.log('DEBUG: fetchContratoData - URL de API para presupuesto (CORREGIDA para Clase2):', url);

      try {
        const response = await fetch(url);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        // La API de Clase2 devuelve { "data": {...} } donde {...} es el objeto del presupuesto.
        // Solo necesitamos data.data aquí.
        return data.data; // <--- CORRECCIÓN IMPORTANTE AQUÍ
      } catch (error) {
        console.error("ERROR: Error al obtener Contrato del Cliente:", error);
        throw error;
      }
    },

    populateClienteData(apiResponse) {
      const clienteData = apiResponse.data;

      if (clienteData) {
        this.nombreComprador = clienteData.nombres || 'N/A';
        this.apellidoComprador = clienteData.apellidos || 'N/A';
        this.rutComprador = clienteData.rut || 'N/A';
        this.direccionComprador = clienteData.direccion || 'N/A';
        this.telefonoComprador = clienteData.fono || 'N/A';
        this.emailComprador = clienteData.correo || 'N/A';
      } else {
        console.warn("Datos de cliente no válidos o vacíos en la respuesta de la API:", apiResponse);
      }
    },

    populateVehiculoData(apiResponse) {
      const vehiculoData = apiResponse.data;

      if (vehiculoData) {
        this.vehiculoMarca = vehiculoData.marca_descripcion || 'N/A';
        this.vehiculoTipo = vehiculoData.vehiculo_descripcion || 'N/A';
        this.vehiculoModelo = vehiculoData.modelo || 'N/A';
        this.vehiculoAgno = vehiculoData.agno || 'N/A';
        this.vehiculoNumeroMotor = vehiculoData.numero_motor || 'N/A';
        this.vehiculoNumeroChasis = vehiculoData.numero_chasis || 'N/A';
        this.vehiculoColor = vehiculoData.color || 'N/A';
        this.vehiculoPatente = vehiculoData.patente || 'N/A';
        this.vehiculoKilometraje = vehiculoData.kilometraje || 'N/A';
      } else {
        console.warn("Datos de vehículo no válidos o vacíos en la respuesta de la API:", apiResponse);
      }
    },

    populateContratoData(apiResponseData) { // Renombrado a apiResponseData para mayor claridad
      // ANTES: const contratoData = apiResponse.data && apiResponse.data.length > 0 ? apiResponse.data[0] : null;
      // AHORA: apiResponseData ya es el objeto directo que necesitamos.
      const contratoData = apiResponseData; // <--- CORRECCIÓN IMPORTANTE AQUÍ

      console.log("DEBUG: Datos de contrato recibidos de la API para populateContratoData (después de corrección):", contratoData);

      if (contratoData) {
        this.piePago = contratoData.valor_pie || 'N/A';
        this.numCuotas = contratoData.numero_cuotas || '0';
        this.valorCuota = contratoData.valor_cuota || '0';
        this.contratoObservacion = contratoData.observacion || 'N/A';
        this.precioVentaTotalContrato = contratoData.valor_venta_total || 'N/A';

        // Formatear fechaInicioCuotas al formato deseado
        if (contratoData.fecha_inicio_pago) {
          // const dateInicio = (contratoData.fecha_inicio_pago);
          // const options = { day: '2-digit', month: 'long', year: 'numeric' };
          //  this.fechaInicioCuotas = contratoData.fecha_inicio_pago;
          this.contratoFecha = contratoData.fecha_inicio_pago;

          const partes = contratoData.fecha_inicio_pago.split('-');

          // Verificar si la división fue exitosa y tiene 3 partes
          if (partes.length === 3) {
            // Reordenar las partes y unirlas con el guion
            // partes[2] es '06', partes[1] es '10', partes[0] es '2023'
            this.fechaInicioCuotas = `${partes[2]}-${partes[1]}-${partes[0]}`;
          }

        } else {
          this.fechaInicioCuotas = 'N/A';
          this.contratoFecha = 'N/A';
        }

        // Calcular fechaFinCuotas usando la fecha original de la API para el cálculo
        if (contratoData.fecha_inicio_pago && !isNaN(parseInt(this.numCuotas))) {
          this.fechaFinCuotas = this.calcularFechaFinCuotas(contratoData.fecha_inicio_pago, parseInt(this.numCuotas));
        } else {
          this.fechaFinCuotas = 'No disponible';
        }

      } else {
        console.warn("Datos de contrato no válidos o vacíos después de intentar procesarlos:", apiResponseData);
        this.fechaFinCuotas = 'No disponible';
      }
    },

    /**
     * Calcula la fecha del último mes de pago.
     * @param {string} fechaInicio - La fecha de inicio en formato 'YYYY-MM-DD'.
     * @param {number} numMeses - El número de meses a añadir (cuotas).
     * @returns {string} La fecha del último mes de pago en formato legible (ej. "28 DE SEPTIEMBRE DE 2025").
     */
    calcularFechaFinCuotas(fechaInicio, numMeses) {
      // Si numMeses es 0 o menos, la fecha de fin es la misma que la de inicio (o N/A si no hay cuotas)
      if (numMeses <= 0) {
        const date = new Date(fechaInicio);
        const options = { day: '2-digit', month: 'long', year: 'numeric' };
        return date.toLocaleDateString('es-ES', options).toUpperCase();
      }

      const fecha = new Date(fechaInicio);
      if (isNaN(fecha.getTime())) {
        console.error("ERROR: Fecha de inicio inválida para el cálculo:", fechaInicio);
        return 'Fecha inválida';
      }

      // Sumamos los meses. Restamos 1 al número de cuotas porque la primera cuota ya está incluida en la fecha de inicio.
      // Por ejemplo, si son 4 cuotas, la primera es en el mes 0, y las otras 3 se suman.
      fecha.setMonth(fecha.getMonth() + (numMeses - 1));

      const options = { day: '2-digit', month: 'long', year: 'numeric' };
      return fecha.toLocaleDateString('es-ES', options).toUpperCase();
    },
  },
};
</script>

<template>

  <div class="contrato-container">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading && !error" class="loading-message">
      Cargando contrato...
    </div>

    <div v-if="!isLoading && !error">
      <div class="contrato-header">
        <img src="/img/core-img/logo.png" alt="Nicolás Automotriz Logo" class="logo">
        <div class="header-title">Contrato Compraventa de vehículo usado</div>
      </div>

      <div>
        <span>En Río Bueno, </span>
        <span class="data-field date">{{ fechaContrato }}</span>
      </div>
      <br>

      <div class="contrato-section">
        <p>
          <strong class="section-title">PRIMERO.</strong> Entre {{ nombreEmpresaVendedor }}, cédula nacional de
          identidad Nº {{ rutEmpresaVendedor }}, domiciliado en calle {{ calleEmpresaVendedor }} de la ciudad de Río
          Bueno, , en adelante, como "vendedor" y como comprador (a):
        </p>
        <br>
        <table class="first-section-table">
          <tr>
            <td class="label-col">Nombre:</td>
            <td class="data-col"><span class="data-field">{{ nombreComprador}} {{apellidoComprador}}</span>
            
           
            </td>
          </tr>
          <tr>
            <td class="label-col">Rut:</td>
            <td class="data-col"><span class="data-field">{{ rutComprador }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Dirección:</td>
            <td class="data-col"><span class="data-field">{{ direccionComprador }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Teléfono:</td>
            <td class="data-col"><span class="data-field">{{ telefonoComprador }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Email:</td>
            <td class="data-col"><span class="data-field">{{ emailComprador }}</span></td>
          </tr>
        </table>
      </div>

      <div class="contrato-section">
        <strong class="section-title">SEGUNDO.</strong> El vendedor vende y transfiere, al comprador, quien compra y
        adquiere para sí, el siguiente vehículo usado:
        <table class="vehicle-details-table">
          <tr>
            <td class="label-col">Vehículo:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoTipo }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Marca:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoMarca }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Modelo:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoModelo }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Año:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoAgno }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Nº de motor:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoNumeroMotor }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Nº de chasis:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoNumeroChasis }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Color:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoColor }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Patente:</td>
            <td class="data-col"><span class="data-field">{{ vehiculoPatente }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Kilometraje:</td>
            <td class="data-col"><span class="data-field">{{ formatearMilesConPunto(vehiculoKilometraje) }}</span></td>
          </tr>
        </table>
      </div>

      <div v-if="pagina == 1" class="contrato-section">
        <strong class="section-title">TERCERO.</strong> El comprador pagara de la siguiente forma:
        <table class="payment-details-table">
          <tr>
            <td class="label-col">Pie :</td>
            <td class="data-col"><span class="data-field">{{ formatearMilesConPunto(piePago) }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Nº de cuotas :</td>
            <td class="data-col"><span class="data-field">{{ numCuotas }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Valor cuota :</td>
            <td class="data-col"><span class="data-field">{{ formatearMilesConPunto(valorCuota) }}</span></td>
          </tr>
          <tr>
            <td class="label-col">A partir de :</td>
            <td class="data-col"><span class="data-field">{{ fechaInicioCuotas }}</span></td>
          </tr>
          <tr>
            <td class="label-col">Hasta :</td>
            <td class="data-col"><span class="data-field">{{ fechaFinCuotas.substring(5, 25) }}</span></td>
          </tr>
        </table>

        <div class="contrato-section">
          <strong class="section-title">CUARTO.</strong> La transferencia será otorgada y cancelada por el comprador al
          final del crédito.
        </div>
      </div>

      <div v-else>
        <div class="contrato-section">
          <strong class="section-title">TERCERO.</strong> El comprador pagará al Contado
        </div>

        <div class="contrato-section">
          <strong class="section-title">CUARTO.</strong> La transferencia será otorgada y cancelada por el comprador.
        </div>
      </div>

      <div class="contrato-section">
        <strong class="section-title">QUINTO.</strong> El comprador toma pleno conocimiento y acepta en su totalidad la
        cláusula sexta, que en el desistimiento del presente contrato, facultará a la parte vendedora a cobrar una
        indemnización de un 15% del valor de venta del vehículo, como así mismo Nicolás Automotriz SPA cobrara un
        arrendamiento diario de los días ocupados por el comprador del vehículo, valor de mercado, al momento del
        desistimiento.
      </div>

      <div class="contrato-section">
        <strong class="section-title">SEXTO.</strong> Los gastos de transferencia serán de cargo del comprador.
      </div>

      <div class="contrato-section">
        <strong class="section-title">SÉPTIMO.</strong> El comprador acepta el vehículo en el estado en que se
        encuentra, será obligación de la parte Comprador revisar y probarlo, ya que si no lo hiciera será exclusivamente
        responsabilidad del Comprador. Cualquier defecto que se encuentre o problema no tendrá derecho a reclamo alguno.
        No se otorga garantía por la venta de vehículos usados. Una vez que estos abandonen la sala de exposición y
        ventas.
      </div>

      <div class="contrato-section">
        <strong class="section-title">OCTAVO.</strong> El comprador faculta expresamente en este acto a la Sociedad
        vendedora Nicolás Automotriz Spa para disponer total o parcialmente de los documentos de pago de dinero o
        instrumento de crédito otorgado por él, pudiendo cubrir el saldo insoluto, intereses, gastos de cobranza, gastos
        notariales u otros gastos relacionados con la obtención y/o
      </div>

      <div class="contrato-section">
        <strong class="section-title">NOVENO.</strong> Declara el comprador haber recibido materialmente el vehículo
        objeto de este contrato, a su entera satisfacción, por lo que expresa no tener cargo alguno ni objeción que
        formular, declarando el comprador que renuncia expresamente a las acciones de saneamiento por evicción y por
        vicios redhibitorios, establecidos en los párrafos 7 y 8 del Título XXIII del Libro IV del Código Civil.
      </div>

      <div class="contrato-section">
        <strong class="section-title">DÉCIMO.</strong> Firman ambas partes en conformidad el presente contrato de
        Compraventa sin tener reclamo alguno que formular ni ahora ni a posterior.
      </div>

      <table class="signature-table">
        <tbody>
          <tr>
            <td class="signature-cell">
              <div class="signature-line"></div>
              <p>FIRMA VENDEDOR</p>
              <p>RUT .............................................</p>
            </td>
            <td class="signature-cell">
              <div class="signature-line"></div>
              <p>FIRMA COMPRADOR</p>
              <p>RUT .............................................</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <Footer></Footer>
</template>

<style scoped>
/* Contenedor principal para simular la página */
.contrato-container {
  font-family: Arial, sans-serif;
  max-width: 800px;
  /* Ancho que se asemeja al documento de la imagen */
  margin: 10px auto;
  padding: 10px;
  /* Padding interno */
  background-color: white;
  line-height: 1.0;
  /* Espaciado de línea para legibilidad */
  font-size: 0.9em;
  /* Tamaño de fuente general */
  color: black;
  /* Asegura que el contenedor base sea negro */
  border: none;
  /* No hay borde en el contenedor principal en la imagen */
  box-shadow: none;
  /* No hay sombra en el contenedor principal en la imagen */
}

/* Mensajes de carga y error */
.loading-message,
.error-message {
  text-align: center;
  font-size: 1.2em;
  color: black;
  /* Asegura que estos mensajes sean negros */
  margin-top: 50px;
}

.error-message {
  color: red;
}

/* Encabezado del contrato (logo y título) */
.contrato-header {
  text-align: left;
  margin-bottom: 20px;
}

.contrato-header .logo {
  max-width: 180px;
  /* Ajusta el tamaño del logo según la imagen */
  height: auto;
  margin-bottom: 10px;
}

.contrato-header .header-title {
  font-size: 1.2em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
}

/* Línea de fecha y lugar */
.header-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 5px;
  border-bottom: 1px solid black;
  /* Línea debajo de la fecha */
}

.header-line span:last-child {
  border-bottom: 1px solid black;
  /* Línea debajo solo de la fecha */
  padding-bottom: 2px;
  display: inline-block;
  min-width: 120px;
  /* Ancho mínimo para la línea de la fecha */
  text-align: right;
}

/* Secciones del contrato */
.contrato-section {
  margin-bottom: 15px;
  text-align: justify;
  color: black;
  /* **IMPORTANTE:** Asegura que el texto dentro de cada sección sea negro */
}

.contrato-section p {
  margin-bottom: 10px;
  color: black;
  /* **IMPORTANTE:** Asegura el color negro para los párrafos específicos */
}

.section-title {
  font-weight: bold;
  color: black;
  /* **IMPORTANTE:** Asegura que estos títulos también sean negros */
}

/* Estilos de las tablas */
.first-section-table,
.vehicle-details-table,
.payment-details-table {
  width: 100%;
  border-collapse: collapse;
  /* Bordes colapsados para una apariencia limpia */
  margin-top: 10px;
  margin-bottom: 20px;
  background-color: #f2f2f2;
  /* Este es tu color celeste/gris claro */
  color: black;
  /* Asegura que el texto dentro de las tablas sea negro */
}

.first-section-table td,
.vehicle-details-table td,
.payment-details-table td {
  border: 1px solid #000;
  /* Bordes visibles como en la imagen */
  padding: 6px 10px;
  /* Padding dentro de las celdas */
  vertical-align: top;
  color: black;
  /* Asegura que el texto dentro de las celdas sea negro */
}

.first-section-table .label-col,
.vehicle-details-table .label-col,
.payment-details-table .label-col {
  font-weight: bold;
  width: 25%;
  /* Ajusta el ancho de la columna de etiquetas */
  background-color: #f2f2f2;
  /* Color de fondo para las etiquetas */
  color: black;
  /* Asegura que las etiquetas de columna sean negras */
}

.data-field {
  border-bottom: 0px solid #000;
  /* Línea debajo de los datos */
  padding-bottom: 2px;
  /*display: inline-block; */
  min-width: 80%;
  /* Asegura que la línea sea visible */
  flex-grow: 1;
  /* Permite que ocupe el espacio disponible */
  color: black;
  /* Asegura que los campos de datos sean negros */
}

/* Sección de firmas */
.signature-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 50px;
  color: black;
  /* Asegura que el texto de la tabla de firmas sea negro */
}

.signature-table td {
  border: 0px solid #000;
  /* Bordes para las celdas de firma */
  padding: 15px 10px;
  text-align: center;
  vertical-align: bottom;
  /* Alinea el texto a la parte inferior de la celda */
  height: 80px;
  /* Proporciona espacio para la firma */
  color: black;
  /* Asegura que el texto dentro de las celdas de firma sea negro */
}

.signature-line {
  border-bottom: 1px solid #000;
  width: 80%;
  /* Ancho de la línea de firma */
  margin: 0 auto 10px auto;
  /* Centra la línea y da espacio debajo */
  display: block;
}

.signature-cell p {
  margin: 0;
  /* Elimina márgenes extra en los párrafos de la firma */
  font-size: 0.9em;
  color: black;
  /* Asegura que los párrafos en las celdas de firma sean negros */
}
</style>