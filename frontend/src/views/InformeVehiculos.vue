<template>
  <div class="informe-vehiculos-container">
    <h2>📊 Informe de Vehículos</h2>
    <p v-if="loading">Cargando datos del informe...</p>
    <p v-if="error" class="error-message">Error al cargar el informe: {{ error }}</p>

    <div v-if="!loading && !error && datosInforme">
      
      <div v-if="datosInforme.data && datosInforme.data.length === 0" class="no-data-message">
        <p>⚠️ **No se encontraron vehículos** que cumplan la condición **'Propiedad Automotriz = 1'**.</p>
        <p>El resumen financiero global muestra ceros porque no hay unidades para calcular.</p>
      </div>

      <section v-if="datosInforme.data && datosInforme.data.length > 0" class="detalle-table">
        <h3>Detalle por Unidad</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Año</th>
              <th>Marca</th>
              <th>Modelo</th>
              <th>Valor Compra</th>
              <th>Gastos</th>
              <th>Valor Venta</th>
              <th>Total Egresos</th>
              <th>Beneficio Bruto</th>
              <th>Margen (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(vehiculo, index) in datosInforme.data" :key="index">
              <td>{{ vehiculo.agno }}</td>
              <td>{{ vehiculo.marca }}</td>
              <td>{{ vehiculo.modelo }}</td>
              <td>{{ formatCurrency(vehiculo.valor_de_compra) }}</td>
              <td>{{ formatCurrency(vehiculo.gastos) }}</td>
              <td>{{ formatCurrency(vehiculo.valor_de_venta) }}</td>
              <td class="bg-light">{{ formatCurrency(vehiculo.total_egresos) }}</td>
              <td :class="getBeneficioClass(vehiculo.beneficio_bruto)">{{ formatCurrency(vehiculo.beneficio_bruto) }}</td>
              <td>{{ vehiculo.margen_beneficio.toFixed(2) }}%</td>
            </tr>
          </tbody>
        </table>
      </section>

      <hr>

      <section class="resumen-financiero">
        <h3>💰 Resumen Global de Totales</h3>
        <div class="resumen-grid">
          
          <div class="resumen-item primary">
            <h4>Valor de Compra Total</h4>
            <p>{{ formatCurrency(datosInforme.resumen_solicitado.total_valor_de_compra) }}</p>
          </div>
          <div class="resumen-item primary">
            <h4>Gastos Totales</h4>
            <p>{{ formatCurrency(datosInforme.resumen_solicitado.total_gastos) }}</p>
          </div>
          <div class="resumen-item primary">
            <h4>Valor de Venta Total</h4>
            <p>{{ formatCurrency(datosInforme.resumen_solicitado.total_valor_de_venta) }}</p>
          </div>
          
          <div class="resumen-item calculated">
            <h4>Total Egresos Global</h4>
            <p>{{ formatCurrency(datosInforme.resumen_solicitado.total_egresos_global) }}</p>
          </div>
          <div :class="['resumen-item calculated', getBeneficioClass(datosInforme.resumen_solicitado.beneficio_bruto_global, true)]">
            <h4>Beneficio Bruto Global</h4>
            <p>{{ formatCurrency(datosInforme.resumen_solicitado.beneficio_bruto_global) }}</p>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script>
export default {
  name: 'InformeVehiculos',
  data() {
    return {
      datosInforme: null,
      loading: true,
      error: null,
    };
  },
  mounted() {
    this.fetchInforme();
  },
  methods: {
    async fetchInforme() {
      this.loading = true;
      this.error = null;
      
      // Asegurarse de que el prefijo VITE_API_URL esté correctamente definido en .env
      const FETCH_URL = `${import.meta.env.VITE_API_URL}vehiculos/informe/propiedad-automotriz/`;

      console.log("API URL:", FETCH_URL);

      try {
        const response = await fetch(FETCH_URL, { 
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`Error ${response.status}: ${errorData.error || 'Respuesta no exitosa'}`);
        }

        this.datosInforme = await response.json();
        
      } catch (err) {
        console.error("Error al obtener el informe:", err);
        this.error = err.message || 'Error de red o de conexión con el servidor.';
      } finally {
        this.loading = false;
      }
    },
    
    // Función para formatear números a moneda (ej: $ 1.250.000)
    formatCurrency(value) {
      if (typeof value !== 'number') return `$ 0`;
      
      return new Intl.NumberFormat('es-CL', { 
        style: 'currency', 
        currency: 'CLP', 
        minimumFractionDigits: 0 
      }).format(value);
    },
    
    // Función para aplicar color verde/rojo según el beneficio
    getBeneficioClass(beneficio, isGlobal = false) {
      if (beneficio > 0) {
        return isGlobal ? 'positive-global' : 'positive';
      } else if (beneficio < 0) {
        return isGlobal ? 'negative-global' : 'negative';
      }
      return '';
    }
  }
};
</script>
<style scoped>
/* (El resto de los estilos se mantienen) */

/* --- Estilos Generales --- */
.informe-vehiculos-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

h2 {
  font-size: 1.8em;
  font-weight: 600;
  color: #34495e;
  border-bottom: 3px solid #3498db;
  padding-bottom: 10px;
  margin-top: 10px;
  margin-bottom: 30px;
}

h3 {
  font-size: 1.3em;
  color: #555;
  margin-top: 25px;
  margin-bottom: 15px;
}

/* ------------------------------------ */
/* --- TABLA DE DETALLE (AMORTIZACIÓN-LIKE) --- */
/* ------------------------------------ */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
  /* Eliminar bordes visibles en toda la tabla */
  border: none; 
}

.data-table th, .data-table td {
  padding: 12px 15px; /* Más padding para más espacio */
  text-align: right;
  border: none; /* Eliminar bordes de celdas */
  font-size: 0.95em;
}

/* Encabezado: Fondo sólido y texto centrado (similar a su imagen) */
.data-table thead tr {
  background-color: #f0f0f0; /* Fondo gris claro */
  color: #333;
  border-bottom: 1px solid #ddd;
}

.data-table th {
  font-weight: bold;
  text-align: center; /* Centrar el texto en los encabezados */
  border-bottom: 2px solid #ccc;
}

/* Filas del cuerpo: Sombreado alterno suave (como en la imagen) */
.data-table tbody tr {
  border-bottom: 1px solid #eee;
}

.data-table tbody tr:nth-child(even) {
  background-color: #f9f9f9; /* Sombreado más suave en filas pares */
}

/* Estilos de cálculo */
.bg-light {
    background-color: #e6f7ff; /* Fondo azul muy claro para egresos */
    font-weight: bold;
}

.positive {
  font-weight: bold;
  color: #27ae60; /* Verde */
}

.negative {
  font-weight: bold;
  color: #c0392b; /* Rojo */
}

/* Ajustar las columnas de texto (Año, Marca, Modelo) a la izquierda */
.data-table tbody tr td:nth-child(1), /* Año */
.data-table tbody tr td:nth-child(2), /* Marca */
.data-table tbody tr td:nth-child(3) { /* Modelo */
    text-align: left;
}

/* ------------------------------------ */
/* --- RESUMEN FINANCIERO --- */
/* ------------------------------------ */
.resumen-financiero {
  margin-top: 40px;
  padding: 25px;
  background-color: #ffffff; /* Fondo blanco para un contraste limpio */
  border: 1px solid #ddd;
  border-radius: 8px;
}

.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
}

.resumen-item {
  padding: 20px;
  border-radius: 6px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05); /* Sombra más sutil */
}

.resumen-item h4 {
  font-size: 0.9em;
  color: #777;
  text-transform: uppercase;
}

.resumen-item p {
  font-size: 1.6em;
  font-weight: 700;
  margin: 8px 0 0;
}

.primary {
    background-color: #f5f5f5; /* Gris muy claro para Totales Base */
    border-left: 5px solid #3498db;
}

.calculated {
    background-color: #e6f7ff; /* Azul muy claro para Totales Calculados */
    border-left: 5px solid #2980b9;
}

.positive-global {
  background-color: #d4edda; /* Verde claro para Beneficio Positivo */
  border-left-color: #27ae60 !important;
}

.negative-global {
  background-color: #f8d7da; /* Rojo claro para Beneficio Negativo */
  border-left-color: #c0392b !important;
}

.error-message {
    color: #c0392b;
    font-weight: bold;
}
</style>