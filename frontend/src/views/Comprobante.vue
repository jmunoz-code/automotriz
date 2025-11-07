<script>
import { computed } from 'vue';
import { useRoute } from 'vue-router'; // <-- Importamos useRoute

export default {
  name: 'ReciboNicolasAutomotriz',
  // NOTA: Usamos useRoute para leer datos directamente de la URL.
  setup() {
    const route = useRoute(); // <-- Accedemos a la ruta actual, que contiene el query

    // Leemos los valores directamente de route.query (son reactivos)
    // Usamos || '' o || 0 para manejar casos donde el parámetro no esté en la URL
    const rut = computed(() => route.query.rut || '');
    const patente = computed(() => route.query.patente || '');
    const monto_pago = computed(() => Number(route.query.monto_pago) || 0);
    const numero_cuota = computed(() => route.query.numero_cuota || null);
    const fecha = computed(() => route.query.fecha || new Date().toISOString());

    // Valores estáticos o con valor por defecto que no se envían desde ModalDetallePago.vue
    const comprobanteNumero = computed(() => route.query.comprobanteNumero || '0');
    const clienteNombre = computed(() => route.query.clienteNombre || '');

    // Formatear el monto a CLP (ejemplo)
    const montoFormateado = computed(() => {
      const monto = monto_pago.value;
      return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        minimumFractionDigits: 0
      }).format(monto);
    });

    // Calcular el detalle del comprobante
    const detalleItems = computed(() => {
      if (!numero_cuota.value || monto_pago.value <= 0) return [];

      return [
        {
          descripcion: `Abono de Cuota N° ${numero_cuota.value} del vehículo Patente ${patente.value}.`,
          valor: montoFormateado.value
        }
      ];
    });

    // Extracción de la fecha
    const fechaObjeto = computed(() => new Date(fecha.value));

    const fechaDia = computed(() => {
      const d = fechaObjeto.value.getDate();
      return isNaN(d) ? '' : d.toString().padStart(2, '0');
    });
    const fechaMes = computed(() => {
      const m = fechaObjeto.value.getMonth() + 1;
      return isNaN(m) ? '' : m.toString().padStart(2, '0');
    });
    const fechaAnio = computed(() => {
      const y = fechaObjeto.value.getFullYear();
      return isNaN(y) ? '' : y.toString().substring(2);
    });

    // Retornar todas las variables calculadas y leídas para el template
    return {
      montoFormateado,
      detalleItems,
      fechaDia,
      fechaMes,
      fechaAnio,
      rut,
      patente,
      clienteNombre,
      comprobanteNumero,
    };
  }
}
</script>

<template>
  <div class="recibo-container">
    <div class="header">
      <div class="company-details">
        <div class="logo-section">
          <span class="logo-n"> <img src="/img/core-img/logo_comprobante.png" alt="logo"
              style="width:260px; height:80px" /></span>
        </div>
        <div class="nicolas-automotriz">NICOLAS AUTOMOTRIZ</div>
        <div class="info-empresa">
          <div>Giro: COMPRA VENTA DE VEHICULOS - CONSIGNACIONES - CORRETAJES</div>
          <div>R.U.T.: <strong>76.692.119-1</strong></div>
          <div>Patricio Lynch N° 1.000 - Río Bueno</div>
          <div>Fono: <strong>642341011</strong> - Cel. Empresa: <strong>+56 9 68455049</strong></div>
        </div>
      </div>

      <div class="recibo-numero">
        <div class="recibo-titulo">RECIBO DINERO</div>
        <div class="numero-box">
          <span style="font-size: 14px; font-weight: bold;">N°</span>
          <span style="font-size: 16px;">{{ comprobanteNumero }}</span>
        </div>

        <div class="date-grid">
          <div>DÍA</div>
          <div>MES</div>
          <div>AÑO</div>
          <div style="border-top: 1px solid #000;">{{ fechaDia }}</div>
          <div style="border-top: 1px solid #000;">{{ fechaMes }}</div>
          <div style="border-top: 1px solid #000;">{{ fechaAnio }}</div>

        </div>
      </div>
    </div>

    <div class="data-field">Nombre: {{ clienteNombre }}</div>

    <div class="data-row">
      <div class="data-field-rut">RUT: <strong>{{ rut }}</strong></div>
      <div class="data-field-patente">Vehículo: <strong>{{ patente }}</strong></div>
    </div>

    <div class="payment-row">
      <div class="payment-field">Efectivo:</div>
      <div class="payment-field"><input type="checkbox" name="efec" id=""></div>
      <div class="payment-field">Cheque:</div>
      <div class="payment-field"><input type="checkbox" name="efec" id=""></div>
      <div class="payment-field">Transferencia:</div>
      <div class="payment-field"><input type="checkbox" name="efec" id=""></div>
    </div>
    <table class="detalle-table">
      <thead>
        <tr>
          <th class="detalle-col">DETALLE</th>
          <th class="valor-col">VALOR</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in detalleItems" :key="index">
          <td class="detalle-col">{{ item.descripcion }}</td>
          <td class="valor-col">{{ item.valor }}</td>
        </tr>
      </tbody>
    </table>

    <div class="footer-section">
      <div class="total-box">
        <strong>TOTAL $</strong>
        <div class="total-value-box">{{ montoFormateado }}</div>
      </div>
    </div>
  </div>

  <br />
  <br />
  <br />
  .....................................................................................................................
  <br />
  <br />
  <br />

  <div class="recibo-container">
    <div class="header">
      <div class="company-details">
        <div class="logo-section">
          <span class="logo-n"> <img src="/img/core-img/logo_comprobante.png" alt="logo"
              style="width:260px; height:80px" /></span>
        </div>
        <div class="nicolas-automotriz">NICOLAS AUTOMOTRIZ</div>
        <div class="info-empresa">
          <div>Giro: COMPRA VENTA DE VEHICULOS - CONSIGNACIONES - CORRETAJES</div>
          <div>R.U.T.: <strong>76.692.119-1</strong></div>
          <div>Patricio Lynch N° 1.000 - Río Bueno</div>
          <div>Fono: <strong>642341011</strong> - Cel. Empresa: <strong>+56 9 68455049</strong></div>
        </div>
      </div>

      <div class="recibo-numero">
        <div class="recibo-titulo">RECIBO DINERO</div>
        <div class="numero-box">
          <span style="font-size: 14px; font-weight: bold;">N°</span>
          <span style="font-size: 16px;">{{ comprobanteNumero }}</span>
        </div>

        <div class="date-grid">
          <div>DÍA</div>
          <div>MES</div>
          <div>AÑO</div>
          <div style="border-top: 1px solid #000;">{{ fechaDia }}</div>
          <div style="border-top: 1px solid #000;">{{ fechaMes }}</div>
          <div style="border-top: 1px solid #000;">{{ fechaAnio }}</div>
        </div>
      </div>
    </div>

    <div class="data-field">Nombre: {{ clienteNombre }}</div>

    <div class="data-row">
      <div class="data-field-rut">RUT: <strong>{{ rut }}</strong></div>
      <div class="data-field-patente">Vehículo: <strong>{{ patente }}</strong></div>
    </div>

    <div class="payment-row">
      <div class="payment-field">Efectivo:</div>
      <div class="payment-field"><input type="checkbox" name="efec" id=""></div>
      <div class="payment-field">Cheque:</div>
      <div class="payment-field"><input type="checkbox" name="efec" id=""></div>
      <div class="payment-field">Transferencia:</div>
      <div class="payment-field"><input type="checkbox" name="efec" id=""></div>
    </div>
    <table class="detalle-table">
      <thead>
        <tr>
          <th class="detalle-col">DETALLE</th>
          <th class="valor-col">VALOR</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in detalleItems" :key="index">
          <td class="detalle-col">{{ item.descripcion }}</td>
          <td class="valor-col">{{ item.valor }}</td>
        </tr>
      </tbody>
    </table>

    <div class="footer-section">
      <div class="total-box">
        <strong>TOTAL $</strong>
        <div class="total-value-box">{{ montoFormateado }}</div>
      </div>
    </div>
  </div>
</template>


<style scoped>
/* Estilos generales (scoped para que solo afecten a este componente) */
.recibo-container {
  width: 750px;
  padding: 20px;
  border: 1px solid #ccc;
  background-color: #f8fcf8;
  font-family: Arial, sans-serif;
  font-size: 10px;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.company-details {
  width: 70%;
}

.logo-section {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.logo-n {
  font-size: 24px;
  font-weight: bold;
  color: #000;
  margin-right: 10px;
}

.nicolas-automotriz {
  font-size: 16px;
  font-weight: bold;
  border-bottom: 2px solid #000;
  margin-bottom: 5px;
  padding-bottom: 2px;
}

.info-empresa {
  font-size: 9px;
  line-height: 1.3;
}

.recibo-numero {
  width: 50%;
  text-align: center;
  border: 2px solid #000;
  padding: 5px;
}

.recibo-titulo {
  font-size: 12px;
  font-weight: bold;
  line-height: 1;
}

.numero-box {
  margin: 5px 0;
  border: 1px solid #000;
  padding: 2px;
}

.date-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: 1px solid #000;
  margin-top: 5px;
}

.date-grid>div {
  border-right: 1px solid #000;
  text-align: center;
  padding: 1px 0;
}

.date-grid>div:last-child {
  border-right: none;
}


/* --- SECCIÓN DE CLIENTE, RUT Y PAGO (CORRECCIÓN VISUAL) --- */

/* Aseguramos que el primer campo (Nombre) tenga borde superior e inferior de 1px */
.data-field {
  border: 1px solid #000;
  padding: 4px 10px;
  width: 100%;
  /* Ocupa todo el ancho */
  border-top: 1px solid #000;
  /* Aseguramos borde superior */
  margin-bottom: -1px;
  /* Para que se pegue al siguiente row */
}

/* Fila de RUT y Patente */
.data-row {
  display: flex;
  border: 1px solid #000;
  border-top: 1px solid #000;
  /* Aseguramos el borde superior */
  margin-bottom: -1px;
  /* Para que se pegue al siguiente row */
}

.data-field-rut {
  padding: 4px 10px;
  width: 50%;
  border-right: 1px solid #000;
}

.data-field-patente {
  padding: 4px 10px;
  width: 50%;
}

/* Fila de tipo de pago */
.payment-row {
  display: flex;
  border: 1px solid #000;
  padding: 0;
  border-top: 1px solid #000;
  /* Aseguramos el borde superior */
  margin-bottom: 5px;
  /* Separación de la tabla de detalle */
}

.payment-field {
  padding: 4px 10px;
  width: 33.33%;
  border-right: 1px solid #000;
}

.payment-field:last-child {
  border-right: none;
}

/* --- FIN SECCIÓN DE CLIENTE, RUT Y PAGO --- */


.detalle-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 5px;
}

.detalle-table thead th,
.detalle-table tbody td {
  border: 1px solid #000;
  padding: 5px 10px;
  text-align: left;
}

.detalle-col {
  width: 100%;
  font-size: 12px;

}

.valor-col {
  width: 25%;
  text-align: right !important;
}

.footer-section {
  display: flex;
  justify-content: flex-end;
  /* Alineamos a la derecha */
  border: 1px solid #000;
  border-top: none;
  margin-top: -1px;
  /* Para pegarlo a la tabla */
}

.total-box {
  width: 50%;
  /* Ocupa la mitad del ancho del comprobante para cuadrar con VALOR */
  display: flex;
  align-items: center;
  /* Eliminamos border-left porque el borde ya lo da el footer-section */
  padding: 5px;
  font-size: 14px;
}

.total-value-box {
  flex-grow: 1;
  border: 1px solid #000;
  text-align: right;
  padding: 2px 5px;
  margin-left: 5px;
}
</style>