<script>
export default {
    name: 'ContratoCompraVenta',
    props: {
        rut: {
            type: String,
            required: true
        },
        patente: {
            type: String,
            required: true
        },
        idPrep: {
            type: [Number, String], // Puede venir como String desde la URL
            required: true
        },
        contract: {
            type: Object,
            required: false,
            default: () => ({})
        },
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

            piePago: 'Cargando...', // No visible en la "Carta de Responsabilidad" pero se mantiene por si es necesario para el "Contrato de Compraventa"
            numCuotas: 'Cargando...', // No visible en la "Carta de Responsabilidad"
            valorCuota: 'Cargando...', // No visible en la "Carta de Responsabilidad"
            fechaInicioCuotas: 'Cargando...', // No visible en la "Carta de Responsabilidad"
            fechaFinCuotas: 'Cargando...', // No visible en la "Carta de Responsabilidad"
            contratoObservacion: 'Cargando...', // No visible en la "Carta de Responsabilidad"
            contratoFecha: 'Cargando...', // No visible en la "Carta de Responsabilidad"

            isLoading: true,
            error: null
        };
    },
    async mounted() {
        console.log('DEBUG: RUT recibido en ContratoCompraventa:', this.rut);
        console.log('DEBUG: Patente recibida en ContratoCompraventa:', this.patente);
        console.log('DEBUG: ID Presupuesto recibido:', this.idPrep);

        this.rutComprador = this.rut;
        this.vehiculoPatente = this.patente;

        this.isLoading = true;
        this.error = null;

        try {
            // Fetching client, vehicle, and contract data
            const [clienteApiResponse, vehiculoApiResponse, contratoApiResponse] = await Promise.all([
                this.fetchClienteData(this.rut),
                this.fetchVehiculoData(this.patente),
                this.fetchContratoData(this.idPrep)
            ]);

            this.populateClienteData(clienteApiResponse);
            this.populateVehiculoData(vehiculoApiResponse);

            // La fecha de la carta debe ser la fecha de creación del presupuesto
            if (contratoApiResponse && contratoApiResponse.fecha_creacion) {
                // Parsear manualmente para evitar problemas de zona horaria
                const fechaStr = contratoApiResponse.fecha_creacion;
                const [year, month, day] = fechaStr.split('-').map(Number);
                const fechaCreacion = new Date(year, month - 1, day); // month - 1 porque los meses van de 0-11
                const options = { day: '2-digit', month: 'long', year: 'numeric' };
                this.fechaContrato = fechaCreacion.toLocaleDateString('es-ES', options).toUpperCase();
            } else {
                // Fallback a fecha actual si no hay fecha_creacion
                const today = new Date();
                const options = { day: '2-digit', month: 'long', year: 'numeric' };
                this.fechaContrato = today.toLocaleDateString('es-ES', options).toUpperCase();
            }


        } catch (err) {
            console.error("Error al cargar los datos de la Carta de Responsabilidad:", err);
            this.error = "Error al cargar los datos. Por favor, inténtelo de nuevo más tarde.";

            // Reset data to "No disponible" on error
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

        } finally {
            this.isLoading = false;
        }
    },
    methods: {
        formatearMilesConPunto(valor) {
            const formatter = new Intl.NumberFormat('de-DE'); // 'de-DE' for dot separator
            return formatter.format(valor);
        },


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

        async fetchContratoData(idPrep) {
            const url = `${import.meta.env.VITE_API_URL}presupuesto/${idPrep}/`;
            console.log('DEBUG: fetchContratoData - URL de API para presupuesto:', url);

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                }
                const data = await response.json();
                return data.data;
            } catch (error) {
                console.error("ERROR: Error al obtener Contrato del Cliente:", error);
                throw error;
            }
        },


        populateClienteData(apiResponse) {
            const clienteData = apiResponse.data;

            if (clienteData) {
                this.nombreComprador = clienteData.nombres || 'N/A';
                this.apellidoComprador = clienteData.apellidos || ''; // Apellido se concatena con el nombre
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
        // The following methods are not strictly needed for "Carta de Responsabilidad"
        // based on the provided images, but are kept if this component has dual purpose.
        populateContratoData(apiResponse) {
            // This method would populate contract-specific data if applicable
            // Not used for "Carta de Responsabilidad" as per images.
        },
        calcularFechaFinCuotas(fechaInicio, numMeses) {
            // Not used for "Carta de Responsabilidad" as per images.
            return '';
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
        <br>
        <div v-if="!isLoading && !error">
            <div class="contrato-header">
                <img src="/img/core-img/logo.png" alt="Nicolás Automotriz Logo" class="logo">
                <div class="header-title">CARTA DE RESPONSABILIDAD</div>
            </div>
            <br>
            <br>
            <div>
                <span>En Río Bueno, </span>
                <span class="data-field date">{{ fechaContrato }}</span>
            </div>
            <br>

            <div class="contrato-section">
                <p>
                    Por el presente instrumento me responsabilizo de cualquier siniestro, accidente, daño e
                    indemnización de perjuicio que pudiera producirse a terceros, en su persona física o en sus bienes,
                    con motivo de uso del vehículo, individualizado mas adelante, yo como
                </p>
                <br>
                <table class="client-info-table">
                    <tr>
                        <td class="label-col">Nombre</td>
                        <td class="data-col">{{ nombreComprador }} {{ apellidoComprador }}</td>
                    </tr>
                    <tr>
                        <td class="label-col">Rut</td>
                        <td class="data-col">{{ rutComprador }}</td>
                    </tr>
                    <tr>
                        <td class="label-col">Dirección</td>
                        <td class="data-col">{{ direccionComprador }}</td>
                    </tr>
                    <tr>
                        <td class="label-col">Teléfono</td>
                        <td class="data-col">{{ telefonoComprador }}</td>
                    </tr>
                    <tr>
                        <td class="label-col">Email</td>
                        <td class="data-col">{{ emailComprador }}</td>
                    </tr>
                </table>
            </div>
            <br>
            <div class="contrato-section">
                <p>
                    Adquiero igual responsabilidad por las sanciones, penas o multas por infracciones de tránsito o de
                    los reglamentos municipales, debiendo comparecer al efecto al Señor(a). Ante cualquier autoridad
                    para responder por la responsabilidad en este acto en el que se da por recibido a su entera
                    satisfacción del vehículo que se entrega, sin que le asista el derecho a efectuar un reclamo
                    posterior sobre el mismo.
                </p>
                <p>
                    En igual forma me responsabilizo del pago total de los impuestos tanto fiscales como municipales y
                    gravámenes que afectan las transferencias de dicho vehículo en los plazos que la ley señala.
                </p>
            </div>
            <br>

            <div class="contrato-section">
                <p>El vehículo es el siguiente:</p>
                <br>
                <table class="vehicle-details-table">
                    <tr>
                        <td class="label-col">Vehículo</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoTipo }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Marca</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoMarca }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Modelo</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoModelo }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Año</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoAgno }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Nº de motor</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoNumeroMotor }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Nº de chasis</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoNumeroChasis }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Color</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoColor }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Patente</td>
                        <td class="data-col"><span class="data-field">{{ vehiculoPatente }}</span></td>
                    </tr>
                    <tr>
                        <td class="label-col">Kilometraje</td>
                        <td class="data-col"><span class="data-field">{{ formatearMilesConPunto(vehiculoKilometraje)
                                }}</span></td>
                    </tr>
                </table>
            </div>
            <br>

            <div class="contrato-section">
                <p>Para conformidad firman,</p>
            </div>
            <br>
            <br>

            <table class="signature-table">
                <tbody>
                    <tr>
                        <td class="signature-cell">
                            <div class="signature-line"></div>
                            <p>Rut: 76.692.119-1</p>
                        </td>
                        <td class="signature-cell">
                            <div class="signature-line"></div>
                            <p>Rut: .............................................</p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>


<style scoped>
/* Contenedor principal para simular la página */
.contrato-container {
    font-family: Arial, sans-serif;
    max-width: 800px;
    /* Ajusta el ancho para que se asemeje a la imagen */
    margin: 10px auto;
    padding: 10px;
    background-color: white;
    line-height: 1.0;
    font-size: 0.9em;
    color: black;
    border: none;
    box-shadow: none;
}

/* Mensajes de carga y error */
.loading-message,
.error-message {
    text-align: center;
    font-size: 1.2em;
    color: black;
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

/* Estilos de la fecha y lugar */
.data-field.date {
    font-weight: bold;
    /* La fecha en la imagen está en negrita */
}

/* Secciones del contrato */
.contrato-section {
    margin-bottom: 15px;
    text-align: justify;
    color: black;
}

.contrato-section p {
    margin-bottom: 10px;
    color: black;
}

.section-title {
    font-weight: bold;
    color: black;
}

/* Estilos de las tablas */
.client-info-table,
.vehicle-details-table,
.payment-details-table {
    /* Se mantiene por si se usa en otro contexto, pero no visible en la imagen */
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    margin-bottom: 20px;
    color: black;
}

.client-info-table td,
.vehicle-details-table td,
.payment-details-table td {
    border: 1px solid #000;
    /* Bordes visibles como en la imagen */
    padding: 6px 10px;
    /* Padding dentro de las celdas */
    vertical-align: top;
    color: black;
}

/* Estilos específicos para la tabla de información del cliente */
.client-info-table .label-col {
    font-weight: normal;
    /* Etiquetas sin negrita, como en la imagen */
    width: 25%;
    /* Ancho de la columna de etiquetas */
    background-color: #f2f2f2;
    /* Color de fondo para las etiquetas, similar al de la imagen */
    color: black;
}

.client-info-table .data-col {
    font-weight: bold;
    /* Datos en negrita, como en la imagen */
    color: black;
}

/* Estilos para las otras tablas (vehículo) */
.vehicle-details-table .label-col {
    font-weight: normal;
    /* Etiquetas de vehículo sin negrita, como en la imagen */
    width: 25%;
    background-color: #f2f2f2;
    color: black;
}

.vehicle-details-table .data-col {
    font-weight: bold;
    /* Datos del vehículo en negrita, como en la imagen */
    color: black;
}

/* Para los campos de texto normales (fuera de tablas), como la fecha */
.data-field {
    color: black;
}

/* Sección de firmas */
.signature-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 50px;
    color: black;
}

.signature-table td {
    border: 0px solid #000;
    /* Sin bordes visibles para las celdas de firma */
    padding: 15px 10px;
    text-align: center;
    vertical-align: bottom;
    height: 80px;
    color: black;
}

.signature-line {
    border-bottom: 1px solid #000;
    width: 80%;
    /* Ancho de la línea de firma */
    margin: 0 auto 10px auto;
    display: block;
}

.signature-cell p {
    margin: 0;
    font-size: 0.9em;
    color: black;
}
</style>